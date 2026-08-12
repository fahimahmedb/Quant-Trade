"""Backtest — Tilt Amihud illiquidité, univers POINT-IN-TIME réel du
NDX-100 (spécification pré-enregistrée dans
PREREG_volume_candidates_pit_universe.md, committée avant ce script,
avant tout fetch de volume PIT et tout calcul).

Réutilise STRICTEMENT (Règle 7) la logique de signal du #261
(`nonml_amihud_illiquidity_tilt_backtest.py` : ILLIQ_WINDOW,
REBAL_EVERY, TERCILE, COST_BPS, `lag_one_day` inchangés) -- seul le
filtre d'univers change, à chaque date de rebalancement, aux titres
RÉELLEMENT membres du NDX-100 ce jour-là
(`ndx100_membership.tickers_as_of_date`, déjà vendorée au #163), au lieu
de la liste des membres de 2026 appliquée rétroactivement. Ancrage
2015-01-01 comme au #163.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_amihud_illiquidity_tilt_backtest import (  # noqa: E402
    lag_one_day, ILLIQ_WINDOW, REBAL_EVERY, COST_BPS, TERCILE,
)
from ndx100_membership import tickers_as_of_date  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
VOLUME_PIT_DIR = ROOT / "data" / "pead" / "volume_pit"
REBAL_ANCHOR = "2015-01-01"


def load_series(dir_path, key):
    series = {}
    for path in sorted(dir_path.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        s = pd.Series(payload[key], index=ts, dtype=float).dropna()
        s = s[~s.index.duplicated(keep="first")].sort_index()
        series[path.stem] = s
    return series


def main():
    close_series = load_series(PRICES_PIT_DIR, "close")
    vol_series = load_series(VOLUME_PIT_DIR, "volume")
    tickers = sorted(set(close_series.keys()) & set(vol_series.keys()))
    excluded = sorted(set(close_series.keys()) - set(vol_series.keys()))

    ref_idx = None
    for t in tickers:
        ref_idx = close_series[t].index if ref_idx is None else ref_idx.union(close_series[t].index)
    ref_idx = ref_idx.sort_values()

    P = pd.DataFrame({t: close_series[t].reindex(ref_idx) for t in tickers})
    V = pd.DataFrame({t: vol_series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    R = np.log(P / P.shift(1))
    # R_simple : rendements SIMPLES, reserves au P&L (le rendement d'un panier
    # pondere est somme(w_i * r_simple_i)). R reste en LOG car il sert a construire
    # le SIGNAL, dont la definition pre-enregistree ne doit pas changer.
    # Voir results/nonml_portfolio_log_aggregation_audit.md.
    R_simple = (P / P.shift(1) - 1.0)
    R.iloc[0, :] = 0.0
    R_safe = np.nan_to_num(R_simple.values, nan=0.0)

    dollar_volume = P.values * V.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily = np.abs(R.values) / dollar_volume
    illiq_daily[~np.isfinite(illiq_daily)] = np.nan
    illiq_avg = pd.DataFrame(illiq_daily).rolling(ILLIQ_WINDOW).mean().values

    weights_illiq = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))

    first_rebal = max(ILLIQ_WINDOW, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
    membership_log = []
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        illiq = illiq_avg[t]
        elig_all = np.where(np.isfinite(illiq) & (illiq > 0))[0]
        members = tickers_as_of_date(P.index[t])
        eligible = np.array([j for j in elig_all if tickers[j] in members], dtype=int)
        membership_log.append((P.index[t], len(members), len(eligible)))

        n_top = max(1, int(round(len(eligible) * TERCILE)))
        n_top = min(n_top, len(eligible))
        if n_top > 0:
            top_idx = eligible[np.argsort(-illiq[eligible])[:n_top]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top
            weights_illiq[t:end] = w
        if len(eligible) > 0:
            weights_bh[t:end, eligible] = 1.0 / len(eligible)

    weights_illiq = lag_one_day(weights_illiq)
    weights_bh = lag_one_day(weights_bh)

    start = first_rebal
    pnl_illiq = (weights_illiq[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_illiq = np.abs(np.diff(weights_illiq[start:], axis=0, prepend=weights_illiq[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_illiq = pnl_illiq - turn_illiq * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)

    me_illiq, me_bh = trading_metrics(np.log1p(pnl_illiq)), trading_metrics(np.log1p(pnl_bh))
    ret_illiq = np.cumprod(1.0 + pnl_illiq)[-1] - 1.0
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    sharpe_ok = me_illiq["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_illiq > ret_bh
    verdict = sharpe_ok and ret_ok

    avg_coverage = np.mean([n_e / max(1, n_m) for _, n_m, n_e in membership_log])

    lines = [
        "# Résultat — Tilt Amihud illiquidité, univers POINT-IN-TIME réel (cycle #264)",
        "",
        f"Univers PIT : {n_tickers} tickers avec prix ET volume PIT disponibles "
        f"({len(excluded)} exclus faute de volume : {', '.join(excluded) if excluded else 'aucun'}). "
        f"Couverture moyenne de l'univers investissable (éligibles/membres réels) : {100*avg_coverage:.1f}%. "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}). "
        "Référence = Buy&Hold équipondéré (univers PIT réel à chaque date, pas la liste 2026). "
        "Construction causale dès le départ (`lag_one_day`).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers PIT) | {me_bh['sharpe_ann']:+.2f} | "
        f"{100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Tilt illiquidité (univers PIT)** | **{me_illiq['sharpe_ann']:+.2f}** | "
        f"**{100*ret_illiq:+.1f}%** | {me_illiq['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_amihud_illiquidity_tilt_pit_universe_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

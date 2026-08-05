"""Backtest — Momentum 12-1 + double-tri turnover, univers POINT-IN-TIME
réel du NDX-100 (spécification pré-enregistrée dans
PREREG_volume_candidates_pit_universe.md, committée avant ce script,
avant tout fetch de volume PIT et tout calcul).

Réutilise STRICTEMENT (Règle 7) la logique de signal du #258
(`nonml_momentum_turnover_doublesort_backtest.py` : LOOKBACK, SKIP,
TURNOVER_WINDOW, REBAL_EVERY, TERCILE, COST_BPS, `lag_one_day`
inchangés) -- seul le filtre d'univers change, à chaque date de
rebalancement, aux titres RÉELLEMENT membres du NDX-100 ce jour-là
(`ndx100_membership.tickers_as_of_date`, déjà vendorée au #163),
au lieu de la liste des membres de 2026 appliquée rétroactivement.
Ancrage 2015-01-01 comme au #163 (première date couverte par la
composition), pour bénéficier du même allongement d'échantillon.
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
from nonml_momentum_turnover_doublesort_backtest import (  # noqa: E402
    lag_one_day, LOOKBACK, SKIP, TURNOVER_WINDOW, REBAL_EVERY, COST_BPS, TERCILE,
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
    close = P.values
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    momentum = np.full((T, n_tickers), np.nan)
    for i in range(LOOKBACK, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - LOOKBACK]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum[i, valid] = m[valid]

    dollar_volume = P.values * V.values
    turnover_avg = pd.DataFrame(dollar_volume).rolling(TURNOVER_WINDOW).mean().values

    weights_double = np.zeros((T, n_tickers))
    weights_mom = np.zeros((T, n_tickers))

    first_rebal = max(LOOKBACK, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
    membership_log = []
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        m = momentum[t]
        tv = turnover_avg[t]
        elig_all = np.where(np.isfinite(m) & np.isfinite(tv) & (tv > 0))[0]
        members = tickers_as_of_date(P.index[t])
        eligible = np.array([j for j in elig_all if tickers[j] in members], dtype=int)
        membership_log.append((P.index[t], len(members), len(eligible)))

        # TERCILE sur le nombre de titres REELEMENT eligibles a cette date
        # (univers PIT variable dans le temps, pas un compte fixe de 99/214)
        n_top_mom = max(1, int(round(len(eligible) * TERCILE)))
        n_top_mom = min(n_top_mom, len(eligible))
        if n_top_mom > 0:
            top_mom_idx = eligible[np.argsort(-m[eligible])[:n_top_mom]]
            w = np.zeros(n_tickers)
            w[top_mom_idx] = 1.0 / n_top_mom
            weights_mom[t:end] = w

            n_top_double = max(1, int(round(len(top_mom_idx) * TERCILE)))
            n_top_double = min(n_top_double, len(top_mom_idx))
            if n_top_double > 0:
                low_turnover_idx = top_mom_idx[np.argsort(tv[top_mom_idx])[:n_top_double]]
                w2 = np.zeros(n_tickers)
                w2[low_turnover_idx] = 1.0 / n_top_double
                weights_double[t:end] = w2

    weights_double = lag_one_day(weights_double)
    weights_mom = lag_one_day(weights_mom)

    start = first_rebal
    pnl_double = (weights_double[start:] * R_safe[start:]).sum(axis=1)
    pnl_mom = (weights_mom[start:] * R_safe[start:]).sum(axis=1)
    turn_double = np.abs(np.diff(weights_double[start:], axis=0, prepend=weights_double[start:start+1])).sum(axis=1) / 2.0
    turn_mom = np.abs(np.diff(weights_mom[start:], axis=0, prepend=weights_mom[start:start+1])).sum(axis=1) / 2.0
    pnl_double = pnl_double - turn_double * (COST_BPS / 1e4)
    pnl_mom = pnl_mom - turn_mom * (COST_BPS / 1e4)

    me_double, me_mom = trading_metrics(pnl_double), trading_metrics(pnl_mom)
    ret_double = np.cumprod(1.0 + pnl_double)[-1] - 1.0
    ret_mom = np.cumprod(1.0 + pnl_mom)[-1] - 1.0
    sharpe_ok = me_double["sharpe_ann"] > me_mom["sharpe_ann"]
    ret_ok = ret_double > ret_mom
    verdict = sharpe_ok and ret_ok

    avg_coverage = np.mean([n_e / max(1, n_m) for _, n_m, n_e in membership_log])

    lines = [
        "# Résultat — Momentum 12-1 + double-tri turnover, univers POINT-IN-TIME réel (cycle #264)",
        "",
        f"Univers PIT : {n_tickers} tickers avec prix ET volume PIT disponibles "
        f"({len(excluded)} exclus faute de volume : {', '.join(excluded) if excluded else 'aucun'}). "
        f"Couverture moyenne de l'univers investissable (éligibles/membres réels) : {100*avg_coverage:.1f}%. "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}). "
        "Référence = momentum 12-1 seul (même construction, univers PIT). Construction causale "
        "dès le départ (`lag_one_day`).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Momentum 12-1 seul (référence, univers PIT) | {me_mom['sharpe_ann']:+.2f} | "
        f"{100*ret_mom:+.1f}% | {me_mom['max_drawdown_pct']:.1f}% |",
        f"| **Momentum 12-1 + double-tri turnover faible (univers PIT)** | **{me_double['sharpe_ann']:+.2f}** | "
        f"**{100*ret_double:+.1f}%** | {me_double['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe double tri > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement double tri > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_turnover_doublesort_pit_universe_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

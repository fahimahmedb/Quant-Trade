"""Backtest — Tilt Amihud illiquidité (spécification pré-enregistrée dans
PREREG_amihud_illiquidity_tilt.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Règle de succès renforcée (Sharpe ET rendement
absolu), référence = Buy&Hold équipondéré (même convention que #4/#73/
#78/#82).

Construction CAUSALE dès le départ (`lag_one_day` appliqué à la
construction, pas une correction a posteriori) -- leçon directe du
balayage d'intégrité #252-260
(`results/nonml_same_bar_execution_audit.md`).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

PRICES_DIR = ROOT / "data" / "pead" / "prices"
VOLUME_DIR = ROOT / "data" / "pead" / "volume"
ILLIQ_WINDOW = 126
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0


def load_all_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > ILLIQ_WINDOW + REBAL_EVERY:
            series[path.stem] = close
    return series


def load_all_volume():
    series = {}
    for path in sorted(VOLUME_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        vol = pd.Series(payload["volume"], index=ts, dtype=float).dropna()
        vol = vol[~vol.index.duplicated(keep="first")].sort_index()
        series[path.stem] = vol
    return series


def lag_one_day(W):
    """Convention d'exécution CAUSALE : le poids décidé à la clôture de t-1 est
    celui détenu pendant la séance t. Appliquée dès la construction ici (pas
    une correction a posteriori) -- voir `results/nonml_same_bar_execution_audit.md`."""
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def main():
    close_series = load_all_prices()
    vol_series = load_all_volume()
    tickers = sorted(set(close_series.keys()) & set(vol_series.keys()))
    excluded = sorted(set(close_series.keys()) - set(vol_series.keys()))

    ref_idx = None
    for t in tickers:
        ref_idx = close_series[t].index if ref_idx is None else ref_idx.union(close_series[t].index)
    ref_idx = ref_idx.sort_values()

    P = pd.DataFrame({t: close_series[t].reindex(ref_idx) for t in tickers})
    V = pd.DataFrame({t: vol_series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    exists = np.isfinite(P.values)
    R = np.log(P / P.shift(1))
    R.iloc[0, :] = 0.0
    # R_simple : rendements SIMPLES, reserves au P&L (le rendement d'un panier
    # pondere est somme(w_i * r_simple_i)). R reste en LOG car il sert a construire
    # le SIGNAL, dont la definition pre-enregistree ne doit pas changer.
    # Voir results/nonml_portfolio_log_aggregation_audit.md.
    R_simple = (P / P.shift(1) - 1.0)
    R_simple.iloc[0, :] = 0.0
    R_safe = np.nan_to_num(R_simple.values, nan=0.0)

    dollar_volume = P.values * V.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily = np.abs(R.values) / dollar_volume
    illiq_daily[~np.isfinite(illiq_daily)] = np.nan
    illiq_avg = pd.DataFrame(illiq_daily).rolling(ILLIQ_WINDOW).mean().values

    weights_illiq = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    n_top = max(1, int(round(n_tickers * TERCILE)))

    rebal_dates = list(range(ILLIQ_WINDOW, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        illiq = illiq_avg[t]
        eligible = np.where(np.isfinite(illiq) & (illiq > 0))[0]
        n_top_t = min(n_top, len(eligible))
        if n_top_t > 0:
            # tercile LE PLUS illiquide (ILLIQ le plus eleve)
            top_idx = eligible[np.argsort(-illiq[eligible])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_illiq[t:end] = w

        listed = exists[t]
        n_listed = listed.sum()
        if n_listed > 0:
            weights_bh[t:end] = listed.astype(float) / n_listed

    weights_illiq = lag_one_day(weights_illiq)
    weights_bh = lag_one_day(weights_bh)

    start = ILLIQ_WINDOW
    pnl_illiq = (weights_illiq[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)

    turn_illiq = np.abs(np.diff(weights_illiq[start:], axis=0, prepend=weights_illiq[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    # P&L BRUT conserve avant deduction des couts + turnover : la batterie
    # Regle 9 (schema portefeuille) doit pouvoir recalculer le P&L a 3x et 5x.
    # Pour un panier le turnover vaut somme(|dw_i|)/2, non derivable d'une
    # exposition scalaire -- il doit donc etre sauvegarde explicitement.
    pnl_gross_ov_, pnl_gross_bh_ = pnl_illiq.copy(), pnl_bh.copy()
    pnl_illiq = pnl_illiq - turn_illiq * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)
    np.savez(ROOT / "results" / "nonml_amihud_illiquidity_tilt_pnl.npz",
             pnl_gross_ov=pnl_gross_ov_, pnl_gross_bh=pnl_gross_bh_,
             turn_ov=turn_illiq, turn_bh=turn_bh,
             dates=P.index.values[start:], cost_bps=COST_BPS)

    me_illiq = trading_metrics(np.log1p(pnl_illiq))
    me_bh = trading_metrics(np.log1p(pnl_bh))
    equity_illiq = np.cumprod(1.0 + pnl_illiq)
    equity_bh = np.cumprod(1.0 + pnl_bh)
    ret_illiq_total = equity_illiq[-1] - 1.0
    ret_bh_total = equity_bh[-1] - 1.0

    sharpe_ok = me_illiq["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_illiq_total > ret_bh_total
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Tilt Amihud illiquidité (pré-enregistré, exécuté une fois, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100 avec prix ET volume disponibles "
        f"({len(excluded)} exclus faute de volume : {', '.join(excluded) if excluded else 'aucun'}), "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}), "
        f"rebalancement tous les {REBAL_EVERY}j, tercile LE PLUS ILLIQUIDE "
        f"(ILLIQ = |rendement|/volume-dollars, moyenne glissante {ILLIQ_WINDOW}j). "
        "Construction causale dès le départ (`lag_one_day` appliqué à la construction).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh_total:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Tilt illiquidité (tercile le plus illiquide)** | **{me_illiq['sharpe_ann']:+.2f}** | "
        f"**{100*ret_illiq_total:+.1f}%** | {me_illiq['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_amihud_illiquidity_tilt_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

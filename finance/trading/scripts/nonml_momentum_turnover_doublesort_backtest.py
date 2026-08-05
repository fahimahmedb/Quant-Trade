"""Backtest — Momentum 12-1 (#73) + double-tri par turnover/volume-dollars
(spécification pré-enregistrée dans PREREG_momentum_turnover_doublesort.md,
committée avant ce script et avant tout fetch de volume). n_trials=1,
aucune dépendance ML. Règle de succès renforcée -- référence = momentum
12-1 seul (#73), pas Buy&Hold.

Construction CAUSALE dès le départ (`lag_one_day` appliqué à la
construction, pas une correction après coup) -- leçon directement tirée
du balayage d'intégrité #252-257 (`results/nonml_same_bar_execution_audit.md`).
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
LOOKBACK = 252
SKIP = 21
TURNOVER_WINDOW = 126
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
        if len(close) > LOOKBACK + REBAL_EVERY:
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
    close = P.values
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    # signal momentum 12-1 (identique au #73/#79)
    momentum = np.full((T, n_tickers), np.nan)
    for i in range(LOOKBACK, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - LOOKBACK]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum[i, valid] = m[valid]

    # turnover proxy : volume en dollars moyen glissant (nouvelle donnée, jamais utilisée)
    dollar_volume = P.values * V.values
    turnover_avg = pd.DataFrame(dollar_volume).rolling(TURNOVER_WINDOW).mean().values

    weights_double = np.zeros((T, n_tickers))
    weights_momentum_only = np.zeros((T, n_tickers))
    n_top_mom_full = max(1, int(round(n_tickers * TERCILE)))

    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T

        m = momentum[t]
        tv = turnover_avg[t]
        eligible = np.where(np.isfinite(m) & np.isfinite(tv) & (tv > 0))[0]

        # reference : momentum 12-1 seul (#73), sur le meme univers eligible
        n_top_mom = min(n_top_mom_full, len(eligible))
        if n_top_mom > 0:
            top_mom_idx = eligible[np.argsort(-m[eligible])[:n_top_mom]]
            w = np.zeros(n_tickers)
            w[top_mom_idx] = 1.0 / n_top_mom
            weights_momentum_only[t:end] = w

            # double tri : parmi le tercile momentum, tercile turnover LE PLUS FAIBLE
            n_top_double = max(1, int(round(len(top_mom_idx) * TERCILE)))
            n_top_double = min(n_top_double, len(top_mom_idx))
            if n_top_double > 0:
                low_turnover_idx = top_mom_idx[np.argsort(tv[top_mom_idx])[:n_top_double]]
                w2 = np.zeros(n_tickers)
                w2[low_turnover_idx] = 1.0 / n_top_double
                weights_double[t:end] = w2

    # convention causale : decision a la cloture de t-1, detenue pendant la seance t
    weights_double = lag_one_day(weights_double)
    weights_momentum_only = lag_one_day(weights_momentum_only)

    start = LOOKBACK
    pnl_double = (weights_double[start:] * R_safe[start:]).sum(axis=1)
    pnl_mom = (weights_momentum_only[start:] * R_safe[start:]).sum(axis=1)

    turn_double = np.abs(np.diff(weights_double[start:], axis=0, prepend=weights_double[start:start+1])).sum(axis=1) / 2.0
    turn_mom = np.abs(np.diff(weights_momentum_only[start:], axis=0, prepend=weights_momentum_only[start:start+1])).sum(axis=1) / 2.0
    pnl_double = pnl_double - turn_double * (COST_BPS / 1e4)
    pnl_mom = pnl_mom - turn_mom * (COST_BPS / 1e4)

    me_double = trading_metrics(pnl_double)
    me_mom = trading_metrics(pnl_mom)

    equity_double = np.cumprod(1.0 + pnl_double)
    equity_mom = np.cumprod(1.0 + pnl_mom)
    ret_double_total = equity_double[-1] - 1.0
    ret_mom_total = equity_mom[-1] - 1.0

    sharpe_ok = me_double["sharpe_ann"] > me_mom["sharpe_ann"]
    ret_ok = ret_double_total > ret_mom_total
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Momentum 12-1 + double-tri turnover/volume-dollars (pré-enregistré, combinaison #73 + nouvelle donnée volume)",
        "",
        f"Univers : {n_tickers} tickers NDX-100 avec prix ET volume disponibles "
        f"({len(excluded)} exclus faute de volume : {', '.join(excluded) if excluded else 'aucun'}), "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}), "
        f"rebalancement tous les {REBAL_EVERY}j. Référence = momentum 12-1 seul (cycle #73), PAS Buy&Hold. "
        f"Double tri : tercile momentum 12-1 (SKIP={SKIP}j, LOOKBACK={LOOKBACK}j), puis tercile à turnover "
        f"(volume en dollars moyen {TURNOVER_WINDOW}j) LE PLUS FAIBLE parmi ce sous-ensemble. "
        "Construction causale dès le départ (`lag_one_day` appliqué à la construction).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Momentum 12-1 seul (référence, cycle #73, univers restreint) | {me_mom['sharpe_ann']:+.2f} | "
        f"{100*ret_mom_total:+.1f}% | {me_mom['max_drawdown_pct']:.1f}% |",
        f"| **Momentum 12-1 + double-tri turnover faible** | **{me_double['sharpe_ann']:+.2f}** | "
        f"**{100*ret_double_total:+.1f}%** | {me_double['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe double tri > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement double tri > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_turnover_doublesort_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

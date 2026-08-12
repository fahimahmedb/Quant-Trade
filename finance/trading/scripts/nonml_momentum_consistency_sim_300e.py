"""Simulation — 300 EUR dans le portefeuille "momentum de constance"
(NDX-100), ~3 derniers mois de données disponibles. Spécification
pré-enregistrée (N_BLOCKS=12, BLOCK_LEN=21, REBAL_EVERY=21, tercile
sup.), aucun paramètre retouché après les résultats de
backtest/robustesse.
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
BLOCK_LEN = 21
N_BLOCKS = 12
LOOKBACK = BLOCK_LEN * N_BLOCKS
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAPITAL0 = 300.0
WINDOW_DAYS = 63


def load_prices():
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


def consistency_at(close: np.ndarray, t: int) -> np.ndarray:
    n_tickers = close.shape[1]
    pos_count = np.zeros(n_tickers)
    valid_count = np.zeros(n_tickers)
    for b in range(N_BLOCKS):
        end_idx = t - b * BLOCK_LEN
        start_idx = end_idx - BLOCK_LEN
        c_end, c_start = close[end_idx], close[start_idx]
        valid = np.isfinite(c_end) & np.isfinite(c_start)
        valid_count += valid
        with np.errstate(all="ignore"):
            block_ret = np.where(valid, c_end / c_start - 1.0, np.nan)
        pos_count += np.where(valid & (block_ret > 0), 1.0, 0.0)
    full = valid_count == N_BLOCKS
    return np.where(full, pos_count / N_BLOCKS, np.nan)


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.nan_to_num((P / P.shift(1) - 1.0).values, nan=0.0)
    R[0, :] = 0.0

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_cons = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        cons = consistency_at(close, t)
        elig = np.where(np.isfinite(cons))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-cons[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_cons[t:end] = w
        listed = exists[t]
        if listed.sum() > 0:
            weights_bh[t:end] = listed.astype(float) / listed.sum()

    pnl_c_full = (weights_cons * R).sum(axis=1)
    pnl_b_full = (weights_bh * R).sum(axis=1)
    turn_c = np.abs(np.diff(weights_cons, axis=0, prepend=weights_cons[:1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_bh, axis=0, prepend=weights_bh[:1])).sum(axis=1) / 2.0
    pnl_c_full = pnl_c_full - turn_c * (COST_BPS / 1e4)
    pnl_b_full = pnl_b_full - turn_b * (COST_BPS / 1e4)

    pnl_c = pnl_c_full[-WINDOW_DAYS:]
    pnl_b = pnl_b_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]

    equity_c = CAPITAL0 * np.cumprod(1.0 + pnl_c)
    equity_b = CAPITAL0 * np.cumprod(1.0 + pnl_b)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_c, me_b = trading_metrics(np.log1p(pnl_c)), trading_metrics(np.log1p(pnl_b))

    lines = [
        "# Simulation — 300 EUR, portefeuille Momentum de constance (NDX-100, ~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_c)} séances). "
        "Spécification pré-enregistrée (N_BLOCKS=12, BLOCK_LEN=21, REBAL_EVERY=21j, tercile sup.), "
        "aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {equity_b[-1]:.2f} EUR | "
        f"{100*(equity_b[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_b):.1f}% | {me_b['sharpe_ann']:+.2f} |",
        f"| **Momentum de constance** | **{equity_c[-1]:.2f} EUR** | "
        f"**{100*(equity_c[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_c):.1f}% | {me_c['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre de 3 mois illustrative uniquement (~3 rebalancements "
        "mensuels observés) — le verdict statistique réel reste celui du backtest complet "
        "(2022-2026, PASS Sharpe+rendement) et de la robustesse (4/5 variantes voisines de "
        "paramètres restent OUI/OUI, N_BLOCKS=14 seul échoue)."
    ]

    out = ROOT / "results" / "nonml_momentum_consistency_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Simulation — 300 EUR dans le portefeuille "leaders 52w-high" (NDX-100),
~3 derniers mois de données disponibles. Spécification pré-enregistrée
(LOOKBACK=252, REBAL_EVERY=21, tercile sup.), aucun paramètre retouché
après les résultats de backtest/robustesse.
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
LOOKBACK = 252
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAPITAL0 = 300.0
WINDOW_DAYS = 63  # ~3 mois de seances


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

    rolling_max = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(LOOKBACK, T):
        window = close[i - LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
    ratio = np.where(has_full, close / rolling_max, np.nan)

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_leaders = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        r = ratio[t]
        elig = np.where(np.isfinite(r))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-r[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_leaders[t:end] = w
        listed = exists[t]
        if listed.sum() > 0:
            weights_bh[t:end] = listed.astype(float) / listed.sum()

    pnl_l_full = (weights_leaders * R).sum(axis=1)
    pnl_b_full = (weights_bh * R).sum(axis=1)
    turn_l = np.abs(np.diff(weights_leaders, axis=0, prepend=weights_leaders[:1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_bh, axis=0, prepend=weights_bh[:1])).sum(axis=1) / 2.0
    pnl_l_full = pnl_l_full - turn_l * (COST_BPS / 1e4)
    pnl_b_full = pnl_b_full - turn_b * (COST_BPS / 1e4)

    pnl_l = pnl_l_full[-WINDOW_DAYS:]
    pnl_b = pnl_b_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]

    equity_l = CAPITAL0 * np.cumprod(1.0 + pnl_l)
    equity_b = CAPITAL0 * np.cumprod(1.0 + pnl_b)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_l, me_b = trading_metrics(np.log1p(pnl_l)), trading_metrics(np.log1p(pnl_b))

    lines = [
        "# Simulation — 300 EUR, portefeuille Leaders 52w-high (NDX-100, ~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_l)} séances). "
        "Spécification pré-enregistrée (LOOKBACK=252, REBAL_EVERY=21j, tercile sup.), "
        "aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {equity_b[-1]:.2f} EUR | "
        f"{100*(equity_b[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_b):.1f}% | {me_b['sharpe_ann']:+.2f} |",
        f"| **Leaders 52w-high** | **{equity_l[-1]:.2f} EUR** | "
        f"**{100*(equity_l[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_l):.1f}% | {me_l['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre de 3 mois illustrative uniquement (~3 rebalancements "
        "mensuels observés) — le verdict statistique réel reste celui du backtest complet "
        "(2022-2026, PASS Sharpe+rendement) et de la robustesse (plateau confirmé sur 5/5 "
        "variantes voisines de paramètres)."
    ]

    out = ROOT / "results" / "nonml_momentum_52w_high_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

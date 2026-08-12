"""Simulation — 300 EUR dans le portefeuille "winners" (momentum court
terme, NDX-100), ~3 derniers mois. Spécification pré-enregistrée
(signal 5j, rebal 5j), aucun paramètre retouché après les résultats
précédents.
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
SIGNAL_WINDOW = 5
REBAL_EVERY = 5
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
        if len(close) > SIGNAL_WINDOW + REBAL_EVERY + 10:
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

    signal = np.full((T, n_tickers), np.nan)
    for i in range(SIGNAL_WINDOW, T):
        with np.errstate(all="ignore", invalid="ignore"):
            signal[i] = close[i] / close[i - SIGNAL_WINDOW] - 1.0
        signal[i, ~(exists[i] & exists[i - SIGNAL_WINDOW])] = np.nan

    n_top = max(1, int(round(n_tickers * TERCILE)))
    start = SIGNAL_WINDOW
    weights_w = np.zeros((T, n_tickers))
    weights_b = np.zeros((T, n_tickers))
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        s = signal[t]
        elig = np.where(np.isfinite(s))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-s[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_w[t:end] = w
        listed = exists[t]
        if listed.sum() > 0:
            weights_b[t:end] = listed.astype(float) / listed.sum()

    pnl_w_full = (weights_w * R).sum(axis=1)
    pnl_b_full = (weights_b * R).sum(axis=1)
    turn_w = np.abs(np.diff(weights_w, axis=0, prepend=weights_w[:1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_b, axis=0, prepend=weights_b[:1])).sum(axis=1) / 2.0
    pnl_w_full = pnl_w_full - turn_w * (COST_BPS / 1e4)
    pnl_b_full = pnl_b_full - turn_b * (COST_BPS / 1e4)

    pnl_w = pnl_w_full[-WINDOW_DAYS:]
    pnl_b = pnl_b_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]

    equity_w = CAPITAL0 * np.cumprod(1.0 + pnl_w)
    equity_b = CAPITAL0 * np.cumprod(1.0 + pnl_b)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_w, me_b = trading_metrics(np.log1p(pnl_w)), trading_metrics(np.log1p(pnl_b))

    lines = [
        "# Simulation — 300 EUR, portefeuille Winners momentum court terme (NDX-100, ~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_w)} séances).",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {equity_b[-1]:.2f} EUR | "
        f"{100*(equity_b[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_b):.1f}% | {me_b['sharpe_ann']:+.2f} |",
        f"| **Winners momentum** | **{equity_w[-1]:.2f} EUR** | "
        f"**{100*(equity_w[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_w):.1f}% | {me_w['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative. Le verdict "
        "statistique réel reste celui du backtest complet (2021-2026, PASS extrême) — "
        "mais rappel important de l'audit : ce résultat reflète un marché haussier très "
        "concentré (IA/semi-conducteurs) sur la période étudiée, pas nécessairement un "
        "edge généralisable à d'autres régimes de marché. Un Sharpe de cet ordre de "
        "grandeur doit toujours éveiller la prudence, pas la confiance aveugle."
    ]

    out = ROOT / "results" / "nonml_short_term_momentum_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

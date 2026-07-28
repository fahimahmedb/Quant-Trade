"""Robustesse — Momentum court terme (winners). Grille de plausibilité
(PAS un retuning) autour de SIGNAL_WINDOW=5j / REBAL_EVERY=5j.
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
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
GRID = [(3, 5), (5, 5), (10, 5), (5, 3), (5, 10)]  # (signal_window, rebal_every)


def load_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > 20:
            series[path.stem] = close
    return series


def run_one(P, signal_window, rebal_every):
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0

    signal = np.full((T, n_tickers), np.nan)
    for i in range(signal_window, T):
        with np.errstate(all="ignore", invalid="ignore"):
            signal[i] = close[i] / close[i - signal_window] - 1.0
        signal[i, ~(exists[i] & exists[i - signal_window])] = np.nan

    n_top = max(1, int(round(n_tickers * TERCILE)))
    start = signal_window
    weights_w = np.zeros((T, n_tickers))
    weights_b = np.zeros((T, n_tickers))
    rebal_dates = list(range(start, T, rebal_every))
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

    pnl_w = (weights_w[start:] * R[start:]).sum(axis=1)
    pnl_b = (weights_b[start:] * R[start:]).sum(axis=1)
    turn_w = np.abs(np.diff(weights_w[start:], axis=0, prepend=weights_w[start:start+1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_b[start:], axis=0, prepend=weights_b[start:start+1])).sum(axis=1) / 2.0
    pnl_w = pnl_w - turn_w * (COST_BPS / 1e4)
    pnl_b = pnl_b - turn_b * (COST_BPS / 1e4)
    me_w, me_b = trading_metrics(pnl_w), trading_metrics(pnl_b)
    ret_w = np.cumprod(1.0 + pnl_w)[-1] - 1.0
    ret_b = np.cumprod(1.0 + pnl_b)[-1] - 1.0
    return (me_w["sharpe_ann"] > me_b["sharpe_ann"]), (ret_w > ret_b), me_w["sharpe_ann"], ret_w


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    lines = [
        "# Robustesse — Momentum court terme, winners (grille de plausibilité, PAS un retuning)",
        "",
        "Spécification pré-enregistrée : signal 5j / rebal 5j.",
        "",
        "| Signal (j) | Rebal (j) | Sharpe>BH | Rendement>BH | Sharpe | Rendement total |",
        "|---|---|---|---|---|---|",
    ]
    for sw, rb in GRID:
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, sw, rb)
        marker = " ← spécification pré-enregistrée" if (sw, rb) == (5, 5) else ""
        lines.append(f"| {sw} | {rb} | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")

    out = ROOT / "results" / "nonml_short_term_momentum_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

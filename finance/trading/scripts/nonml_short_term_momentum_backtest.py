"""Backtest — Momentum court terme, 1 semaine (spécification pré-enregistrée
dans PREREG_short_term_momentum.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Soumis à la règle de succès renforcée. Réutilise la
construction d'univers dynamique du cycle #4/#5 -- seul le sens du tri
change (tercile SUPÉRIEUR au lieu d'inférieur).
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


def build_universe():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    return P


def main():
    P = build_universe()
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    signal = np.full((T, n_tickers), np.nan)
    for i in range(SIGNAL_WINDOW, T):
        with np.errstate(all="ignore", invalid="ignore"):
            signal[i] = close[i] / close[i - SIGNAL_WINDOW] - 1.0
        signal[i, ~(exists[i] & exists[i - SIGNAL_WINDOW])] = np.nan

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_winners = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    start = SIGNAL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        s = signal[t]
        elig = np.where(np.isfinite(s))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-s[elig])[:n_top_t]]  # les PLUS HAUTS rendements (winners)
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_winners[t:end] = w
        listed = exists[t]
        if listed.sum() > 0:
            weights_bh[t:end] = listed.astype(float) / listed.sum()

    pnl_w = (weights_winners[start:] * R_safe[start:]).sum(axis=1)
    pnl_b = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_w = np.abs(np.diff(weights_winners[start:], axis=0, prepend=weights_winners[start:start+1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_w = pnl_w - turn_w * (COST_BPS / 1e4)
    pnl_b = pnl_b - turn_b * (COST_BPS / 1e4)

    me_w, me_b = trading_metrics(pnl_w), trading_metrics(pnl_b)
    equity_w = np.cumprod(1.0 + pnl_w)
    equity_b = np.cumprod(1.0 + pnl_b)
    ret_w, ret_b = equity_w[-1] - 1.0, equity_b[-1] - 1.0

    sharpe_ok = me_w["sharpe_ann"] > me_b["sharpe_ann"]
    ret_ok = ret_w > ret_b
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Momentum court terme, 1 semaine, winners (pré-enregistré, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), signal = rendement 5j, "
        f"rebalancement hebdomadaire, tercile SUPÉRIEUR ({n_top} titres).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_b['sharpe_ann']:+.2f} | {100*ret_b:+.1f}% | "
        f"{me_b['max_drawdown_pct']:.1f}% |",
        f"| **Winners (tercile sup., momentum)** | **{me_w['sharpe_ann']:+.2f}** | "
        f"**{100*ret_w:+.1f}%** | {me_w['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe winners > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total winners > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
        "",
        "**Comparaison directe avec le cycle #5** (même signal, même univers, tercile "
        "opposé) : à mettre en regard de `results/nonml_short_term_reversal_result.md` "
        "(losers : Sharpe -1.02, rendement -83.6%).",
    ]

    out = ROOT / "results" / "nonml_short_term_momentum_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

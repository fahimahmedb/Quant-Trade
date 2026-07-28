"""Backtest — Reversal court terme (1 semaine, niveau titre), spécification
pré-enregistrée dans PREREG_short_term_reversal.md, committée avant ce
script. n_trials=1, aucune dépendance ML. Soumis à la règle de succès
renforcée (Sharpe ET rendement absolu). Réutilise la construction
d'univers dynamique (calendrier union) validée/corrigée au cycle #4.
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
SIGNAL_WINDOW = 5    # 1 semaine
REBAL_EVERY = 5       # hebdomadaire
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

    n_bottom = max(1, int(round(n_tickers * TERCILE)))
    weights_losers = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    start = SIGNAL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        s = signal[t]
        elig = np.where(np.isfinite(s))[0]
        n_bot_t = min(n_bottom, len(elig))
        if n_bot_t > 0:
            bottom_idx = elig[np.argsort(s[elig])[:n_bot_t]]  # les PLUS BAS rendements
            w = np.zeros(n_tickers)
            w[bottom_idx] = 1.0 / n_bot_t
            weights_losers[t:end] = w
        listed = exists[t]
        if listed.sum() > 0:
            weights_bh[t:end] = listed.astype(float) / listed.sum()

    pnl_l = (weights_losers[start:] * R_safe[start:]).sum(axis=1)
    pnl_b = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_l = np.abs(np.diff(weights_losers[start:], axis=0, prepend=weights_losers[start:start+1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_l = pnl_l - turn_l * (COST_BPS / 1e4)
    pnl_b = pnl_b - turn_b * (COST_BPS / 1e4)

    me_l, me_b = trading_metrics(pnl_l), trading_metrics(pnl_b)
    equity_l = np.cumprod(1.0 + pnl_l)
    equity_b = np.cumprod(1.0 + pnl_b)
    ret_l, ret_b = equity_l[-1] - 1.0, equity_b[-1] - 1.0

    sharpe_ok = me_l["sharpe_ann"] > me_b["sharpe_ann"]
    ret_ok = ret_l > ret_b
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Reversal court terme, 1 semaine (pré-enregistré, exécuté une fois, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), signal = rendement 5j, "
        f"rebalancement hebdomadaire, tercile inférieur ({n_bottom} titres).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_b['sharpe_ann']:+.2f} | {100*ret_b:+.1f}% | "
        f"{me_b['max_drawdown_pct']:.1f}% |",
        f"| **Losers (tercile inf., reversal)** | **{me_l['sharpe_ann']:+.2f}** | "
        f"**{100*ret_l:+.1f}%** | {me_l['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe losers > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total losers > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
        "",
        "**Lecture honnête** : rebalancement hebdomadaire = turnover bien plus élevé "
        "(~52/an) que le momentum 52-semaines (~12/an) — coût de transaction "
        "proportionnellement plus lourd, à garder en tête pour interpréter un éventuel FAIL.",
    ]

    out = ROOT / "results" / "nonml_short_term_reversal_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

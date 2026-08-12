"""Backtest — Tilt sur l'asymétrie (skewness) des rendements individuels
(spécification pré-enregistrée dans PREREG_skewness_tilt.md, committée
avant ce script). n_trials=1, aucune dépendance ML. Règle de succès
renforcée (Sharpe ET rendement absolu).
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
SKEW_WINDOW = 60
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
        if len(close) > SKEW_WINDOW + REBAL_EVERY:
            series[path.stem] = close
    return series


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())

    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()

    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T = len(P)
    tickers = list(P.columns)
    n_tickers = len(tickers)
    print(f"Univers exploitable : {n_tickers} tickers, {T} séances (calendrier UNION, "
          f"chaque titre pondéré seulement depuis sa 1ère cotation) "
          f"({P.index[0].date()} → {P.index[-1].date()})")

    R = np.log(P / P.shift(1))
    R.iloc[0, :] = 0.0
    # R_simple : rendements SIMPLES, reserves au P&L (le rendement d'un panier
    # pondere est somme(w_i * r_simple_i)). R reste en LOG car il sert a construire
    # le SIGNAL, dont la definition pre-enregistree ne doit pas changer.
    # Voir results/nonml_portfolio_log_aggregation_audit.md.
    R_simple = (P / P.shift(1) - 1.0)
    R_simple.iloc[0, :] = 0.0
    close = P.values
    exists = np.isfinite(close)

    skew60 = R.rolling(SKEW_WINDOW).skew().values

    weights_lowskew = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))

    n_top = max(1, int(round(n_tickers * TERCILE)))
    rebal_dates = list(range(SKEW_WINDOW, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T

        s = skew60[t]
        valid = np.isfinite(s)
        eligible_idx = np.where(valid)[0]
        n_top_t = min(n_top, len(eligible_idx))
        if n_top_t > 0:
            # tercile a l'asymetrie la PLUS FAIBLE
            top_idx = eligible_idx[np.argsort(s[eligible_idx])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_lowskew[t:end] = w

        listed = exists[t]
        n_listed = listed.sum()
        if n_listed > 0:
            weights_bh[t:end] = listed.astype(float) / n_listed

    start = SKEW_WINDOW
    R_safe = np.nan_to_num(R_simple.values, nan=0.0)
    pnl_lowskew = (weights_lowskew[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)

    turn_lowskew = np.abs(np.diff(weights_lowskew[start:], axis=0, prepend=weights_lowskew[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_lowskew = pnl_lowskew - turn_lowskew * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)

    me_lowskew = trading_metrics(np.log1p(pnl_lowskew))
    me_bh = trading_metrics(np.log1p(pnl_bh))

    equity_lowskew = np.cumprod(1.0 + pnl_lowskew)
    equity_bh = np.cumprod(1.0 + pnl_bh)
    ret_lowskew_total = equity_lowskew[-1] - 1.0
    ret_bh_total = equity_bh[-1] - 1.0

    sharpe_ok = me_lowskew["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_lowskew_total > ret_bh_total
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Tilt sur l'asymétrie (skewness) individuelle (pré-enregistré, exécuté une fois, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), rebalancement tous les "
        f"{REBAL_EVERY}j, tercile à l'asymétrie la PLUS FAIBLE (fenêtre {SKEW_WINDOW}j).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh_total:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Asymétrie faible (tercile)** | **{me_lowskew['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lowskew_total:+.1f}%** | {me_lowskew['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_skewness_tilt_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Robustesse — Momentum 12-1 mois.

Grille de plausibilité (PAS un retuning) autour de la spécification
pré-enregistrée (LOOKBACK=252, REBAL_EVERY=21) : ±20% sur chaque
paramètre indépendamment. SKIP=21 (l'exclusion du dernier mois, cœur de
la construction Jegadeesh & Titman) n'est PAS perturbé. Le verdict PASS
officiel reste celui de la spécification pré-enregistrée
(`results/nonml_momentum_12_1_result.md`).
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
SKIP = 21

LOOKBACK_GRID = [200, 252, 300]
REBAL_GRID = [15, 21, 27]


def load_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > 300 + 27:
            series[path.stem] = close
    return series


def run_one(P: pd.DataFrame, lookback: int, rebal_every: int):
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    # Rendements SIMPLES : le rendement d'un panier pondere est somme(w_i*r_simple_i).
    # Voir results/nonml_portfolio_log_aggregation_audit.md.
    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    momentum = np.full((T, n_tickers), np.nan)
    for i in range(lookback, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - lookback]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum[i, valid] = m[valid]

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_mom = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    rebal_dates = list(range(lookback, T, rebal_every))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        m = momentum[t]
        elig = np.where(np.isfinite(m))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-m[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_mom[t:end] = w
        listed = exists[t]
        if listed.sum() > 0:
            weights_bh[t:end] = listed.astype(float) / listed.sum()

    start = lookback
    pnl_m = (weights_mom[start:] * R_safe[start:]).sum(axis=1)
    pnl_b = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_m = np.abs(np.diff(weights_mom[start:], axis=0, prepend=weights_mom[start:start+1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_m = pnl_m - turn_m * (COST_BPS / 1e4)
    pnl_b = pnl_b - turn_b * (COST_BPS / 1e4)

    me_m, me_b = trading_metrics(np.log1p(pnl_m)), trading_metrics(np.log1p(pnl_b))
    ret_m = np.cumprod(1.0 + pnl_m)[-1] - 1.0
    ret_b = np.cumprod(1.0 + pnl_b)[-1] - 1.0
    return me_m["sharpe_ann"] > me_b["sharpe_ann"], ret_m > ret_b, me_m["sharpe_ann"], ret_m


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    lines = [
        "# Robustesse — Momentum 12-1 mois (grille de plausibilité, PAS un retuning)",
        "",
        "Spécification pré-enregistrée : LOOKBACK=252, REBAL_EVERY=21, SKIP=21 (fixe, non "
        "perturbé — cœur de la construction Jegadeesh & Titman). Le verdict PASS officiel reste "
        "celui de cette spécification (`results/nonml_momentum_12_1_result.md`) — ceci est "
        "diagnostique uniquement.",
        "",
        "| LOOKBACK | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe momentum | Rendement total momentum |",
        "|---|---|---|---|---|---|",
    ]
    for lb in LOOKBACK_GRID:
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, lb, 21)
        marker = " ← LOOKBACK pré-enregistré" if lb == 252 else ""
        lines.append(f"| {lb} | 21 | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")
    for rb in REBAL_GRID:
        if rb == 21:
            continue
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, 252, rb)
        lines.append(f"| 252 | {rb} | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}% |")

    lines.append("")
    lines.append(
        "**Lecture** : si la majorité des variantes voisines restent OUI/OUI, l'effet est "
        "un plateau plausible autour de la spécification 252j/21j, pas un pic isolé."
    )

    out = ROOT / "results" / "nonml_momentum_12_1_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

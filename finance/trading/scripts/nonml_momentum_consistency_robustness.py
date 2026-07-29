"""Robustesse — Momentum de constance.

Grille de plausibilité (PAS un retuning) autour de la spécification
pré-enregistrée (N_BLOCKS=12, REBAL_EVERY=21) : variation du nombre de
blocs et de la fréquence de rebalancement. BLOCK_LEN=21 (définition du
"mois de bourse") n'est PAS perturbé, cœur de la construction. Le
verdict PASS officiel reste celui de la spécification pré-enregistrée
(`results/nonml_momentum_consistency_result.md`).
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
COST_BPS = 5.0
TERCILE = 1.0 / 3.0

N_BLOCKS_GRID = [10, 12, 14]
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
        if len(close) > 14 * BLOCK_LEN + 27:
            series[path.stem] = close
    return series


def consistency_at(close: np.ndarray, t: int, n_blocks: int) -> np.ndarray:
    n_tickers = close.shape[1]
    pos_count = np.zeros(n_tickers)
    valid_count = np.zeros(n_tickers)
    for b in range(n_blocks):
        end_idx = t - b * BLOCK_LEN
        start_idx = end_idx - BLOCK_LEN
        c_end, c_start = close[end_idx], close[start_idx]
        valid = np.isfinite(c_end) & np.isfinite(c_start)
        valid_count += valid
        with np.errstate(all="ignore"):
            block_ret = np.where(valid, c_end / c_start - 1.0, np.nan)
        pos_count += np.where(valid & (block_ret > 0), 1.0, 0.0)
    full = valid_count == n_blocks
    return np.where(full, pos_count / n_blocks, np.nan)


def run_one(P: pd.DataFrame, n_blocks: int, rebal_every: int):
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0
    lookback = n_blocks * BLOCK_LEN

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_cons = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    rebal_dates = list(range(lookback, T, rebal_every))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        cons = consistency_at(close, t, n_blocks)
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

    start = lookback
    pnl_c = (weights_cons[start:] * R[start:]).sum(axis=1)
    pnl_b = (weights_bh[start:] * R[start:]).sum(axis=1)
    turn_c = np.abs(np.diff(weights_cons[start:], axis=0, prepend=weights_cons[start:start+1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_c = pnl_c - turn_c * (COST_BPS / 1e4)
    pnl_b = pnl_b - turn_b * (COST_BPS / 1e4)

    me_c, me_b = trading_metrics(pnl_c), trading_metrics(pnl_b)
    ret_c = np.cumprod(1.0 + pnl_c)[-1] - 1.0
    ret_b = np.cumprod(1.0 + pnl_b)[-1] - 1.0
    return me_c["sharpe_ann"] > me_b["sharpe_ann"], ret_c > ret_b, me_c["sharpe_ann"], ret_c


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    lines = [
        "# Robustesse — Momentum de constance (grille de plausibilité, PAS un retuning)",
        "",
        "Spécification pré-enregistrée : N_BLOCKS=12, REBAL_EVERY=21 (BLOCK_LEN=21 fixe, cœur "
        "de la construction). Le verdict PASS officiel reste celui de cette spécification "
        "(`results/nonml_momentum_consistency_result.md`) — ceci est diagnostique uniquement.",
        "",
        "| N_BLOCKS | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe constance | Rendement total constance |",
        "|---|---|---|---|---|---|",
    ]
    for nb in N_BLOCKS_GRID:
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, nb, 21)
        marker = " ← N_BLOCKS pré-enregistré" if nb == 12 else ""
        lines.append(f"| {nb} | 21 | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")
    for rb in REBAL_GRID:
        if rb == 21:
            continue
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, 12, rb)
        lines.append(f"| 12 | {rb} | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}% |")

    lines.append("")
    lines.append(
        "**Lecture** : si la majorité des variantes voisines restent OUI/OUI, l'effet est "
        "un plateau plausible autour de la spécification N_BLOCKS=12/REBAL_EVERY=21j, pas un "
        "pic isolé."
    )

    out = ROOT / "results" / "nonml_momentum_consistency_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

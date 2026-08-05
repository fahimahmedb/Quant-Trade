"""Robustesse — Momentum de constance, univers point-in-time (cycle #266).

Grille de plausibilité (PAS un retuning) : réutilise STRICTEMENT (Règle
7) la grille déjà publiée au #82 original (N_BLOCKS {10,12,14},
REBAL_EVERY {15,21,27}, BLOCK_LEN=21j fixe). Le verdict PASS officiel
reste celui de la spécification pré-enregistrée
(`results/nonml_momentum_consistency_pit_universe_result.md`).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402
from nonml_momentum_consistency_backtest import lag_one_day, BLOCK_LEN, TERCILE, COST_BPS  # noqa: E402
from nonml_momentum_consistency_pit_universe_backtest import load_prices, REBAL_ANCHOR  # noqa: E402

N_BLOCKS_GRID = [10, 12, 14]
REBAL_GRID = [15, 21, 27]


def consistency_at_n(close, t, n_blocks):
    n_tickers = close.shape[1]
    block_positive_count = np.zeros(n_tickers)
    block_valid_count = np.zeros(n_tickers)
    for b in range(n_blocks):
        end_idx = t - b * BLOCK_LEN
        start_idx = end_idx - BLOCK_LEN
        c_end = close[end_idx]
        c_start = close[start_idx]
        valid = np.isfinite(c_end) & np.isfinite(c_start)
        block_valid_count += valid
        with np.errstate(all="ignore"):
            block_ret = np.where(valid, c_end / c_start - 1.0, np.nan)
        block_positive_count += np.where(valid & (block_ret > 0), 1.0, 0.0)
    full_history = block_valid_count == n_blocks
    return np.where(full_history, block_positive_count / n_blocks, np.nan)


def run_one(P: pd.DataFrame, n_blocks: int, rebal_every: int):
    T, n_tickers = P.shape
    close = P.values
    tickers = list(P.columns)
    lookback = BLOCK_LEN * n_blocks
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    weights_cons = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    first_rebal = max(lookback, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, rebal_every))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        cons = consistency_at_n(close, t, n_blocks)
        elig_all = np.where(np.isfinite(cons))[0]
        members = tickers_as_of_date(P.index[t])
        eligible = np.array([j for j in elig_all if tickers[j] in members], dtype=int)
        n_top = max(1, int(round(len(eligible) * TERCILE)))
        n_top = min(n_top, len(eligible))
        if n_top > 0:
            top_idx = eligible[np.argsort(-cons[eligible])[:n_top]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top
            weights_cons[t:end] = w
        if len(eligible) > 0:
            weights_bh[t:end, eligible] = 1.0 / len(eligible)

    weights_cons = lag_one_day(weights_cons)
    weights_bh = lag_one_day(weights_bh)
    start = first_rebal
    pnl_cons = (weights_cons[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_cons = np.abs(np.diff(weights_cons[start:], axis=0, prepend=weights_cons[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_cons = pnl_cons - turn_cons * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)
    me_cons, me_bh = trading_metrics(pnl_cons), trading_metrics(pnl_bh)
    ret_cons = np.cumprod(1.0 + pnl_cons)[-1] - 1.0
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    return me_cons["sharpe_ann"] > me_bh["sharpe_ann"], ret_cons > ret_bh, me_cons["sharpe_ann"], ret_cons


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    lines = [
        "# Robustesse — Momentum de constance, univers point-in-time (grille de plausibilité, PAS un retuning)",
        "",
        "Grille réutilisée telle quelle du #82 original : N_BLOCKS {10,12,14}, "
        "REBAL_EVERY {15,21,27}j, BLOCK_LEN=21j fixe. Le verdict PASS officiel reste celui "
        "de la spécification pré-enregistrée "
        "(`results/nonml_momentum_consistency_pit_universe_result.md`).",
        "",
        "| N_BLOCKS | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe constance | Rendement total |",
        "|---|---|---|---|---|---|",
    ]
    results = []
    for nb in N_BLOCKS_GRID:
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, nb, 21)
        results.append((sharpe_ok, ret_ok))
        marker = " ← pré-enregistré" if nb == 12 else ""
        lines.append(f"| {nb} | 21 | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")
    for rb in REBAL_GRID:
        if rb == 21:
            continue
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, 12, rb)
        results.append((sharpe_ok, ret_ok))
        lines.append(f"| 12 | {rb} | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}% |")

    n_pass = sum(1 for s, r in results if s and r)
    lines.append("")
    lines.append(f"**{n_pass}/{len(results)} variantes OUI/OUI.** Lecture : si la majorité des "
                 "variantes voisines restent OUI/OUI, l'effet est un plateau plausible, pas un pic isolé.")

    out = ROOT / "results" / "nonml_momentum_consistency_pit_universe_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

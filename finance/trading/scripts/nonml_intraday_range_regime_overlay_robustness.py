"""Robustesse — Overlay de régime par le range intra-séance.

Grille de plausibilité (PAS un retuning) autour du CAP pré-enregistré
(2.0x) : CAP in {1.5, 2.0, 2.5, 3.0}. Le verdict PASS officiel reste
celui de CAP=2.0 (`results/nonml_intraday_range_regime_overlay_result.md`).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_intraday_range_regime_overlay_backtest import (  # noqa: E402
    calm_range_regime_mask, COST_BPS, WARMUP, MARKETS,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]


def run_one(df, cap):
    high, low, close = df["high"].values, df["low"].values, df["close"].values
    bh_full = np.log(close[1:] / close[:-1])
    T = len(bh_full)
    mask_full = calm_range_regime_mask(high, low, close)
    mask = mask_full[1:]
    idx = np.arange(WARMUP, T)

    pos = np.where(mask, cap, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov_full = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh_full = bh_full.copy()
    pnl_bh_full[0] -= COST_BPS / 1e4

    pnl_ov, pnl_bh = pnl_ov_full[idx], pnl_bh_full[idx]
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    lines = [
        "# Robustesse — Overlay de régime par le range intra-séance (grille de plausibilité, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x. Le verdict PASS officiel reste celui de cette valeur "
        "(`results/nonml_intraday_range_regime_overlay_result.md`) — ceci est diagnostique uniquement.",
        "",
        "| CAP | Nb marchés PASS (Sharpe ET rendement) /5 |",
        "|---|---|",
    ]
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if path.exists():
            df = load_ohlc(str(path))
            quality_report(df)
            dfs[name] = df

    for cap in CAP_GRID:
        n_pass = sum(run_one(df, cap) for df in dfs.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(dfs)}{marker} |")

    lines.append("")
    lines.append(
        "**Lecture** : si les CAP voisins restent proches de 5/5, l'effet est un plateau "
        "plausible autour de 2.0x, pas un pic isolé sur ce niveau de levier précis."
    )

    out = ROOT / "results" / "nonml_intraday_range_regime_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

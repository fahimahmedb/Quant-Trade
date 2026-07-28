"""Robustesse — Overlay proximité plus haut 52-semaines (indice). Grille
CAP (autour de 2.0x préenregistré) ET grille de seuil (autour de 95%
préenregistré) -- PAS un retuning, annoncé dans le pré-enregistrement.
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
from nonml_index_52w_high_overlay_backtest import near_high_mask, COST_BPS, LOOKBACK, MARKETS  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
THRESHOLD_GRID = [0.90, 0.93, 0.95, 0.97]


def run_one(close: np.ndarray, cap: float, threshold: float) -> bool:
    near_high = near_high_mask(close, threshold)
    start = LOOKBACK
    close_t = close[start:]
    r = np.log(close_t[1:] / close_t[:-1])
    mask = near_high[start:-1]
    pos = np.where(mask, cap, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    closes = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if path.exists():
            df = load_ohlc(str(path))
            quality_report(df)
            closes[name] = df["close"].values

    lines = [
        "# Robustesse — Overlay proximité plus haut 52-semaines indice (grilles CAP et seuil, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x, seuil pré-enregistré = 95%.",
        "",
        "## Grille CAP (seuil fixé à 95%)",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        n_pass = sum(run_one(c, cap, 0.95) for c in closes.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(closes)}{marker} |")

    lines.append("")
    lines.append("## Grille seuil de proximité (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Seuil | Nb marchés PASS /5 |")
    lines.append("|---|---|")
    for thr in THRESHOLD_GRID:
        n_pass = sum(run_one(c, 2.0, thr) for c in closes.values())
        marker = " ← seuil pré-enregistré" if thr == 0.95 else ""
        lines.append(f"| {100*thr:.0f}% | {n_pass}/{len(closes)}{marker} |")

    out = ROOT / "results" / "nonml_index_52w_high_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

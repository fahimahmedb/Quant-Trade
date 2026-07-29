"""Robustesse — Overlay vol-targeting gaté par vote majoritaire. Grilles
CAP, fenêtre de vol, ET seuil de vote (2/3/4 sur 5 -- fait partie de la
définition du mécanisme d'agrégation pré-enregistrée, PAS un retuning
après résultat : la grille {2,3,4} était déjà prévue dans le PREREG
avant tout calcul).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_ensemble_vote_vol_targeting_overlay_backtest import (  # noqa: E402
    build_votes, COST_BPS, TARGET_VOL_ANNUAL, ANNUALIZATION,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]
VOTE_GRID = [2, 3, 4]


def position_for(r, gate_aligned, cap, vol_window):
    gate_r = gate_aligned[:-1]
    vol_ann = pd.Series(r).rolling(vol_window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt = TARGET_VOL_ANNUAL / vol_lagged
    vt = np.clip(vt, 1.0, cap)
    vt = np.nan_to_num(vt, nan=1.0)
    return np.where(gate_r, vt, 1.0)


def run_one(r, gate_aligned, start, cap, vol_window):
    pos_full = position_for(r, gate_aligned, cap, vol_window)
    r_t = r[start:]
    pos = pos_full[start:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    dates_idx = pd.to_datetime(df["date"])
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])

    votes, first_valid = build_votes(dates_idx)

    lines = [
        "# Robustesse — Overlay vote majoritaire (grilles CAP, fenêtre de vol, ET seuil de vote)",
        "",
        "CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j, seuil de vote pré-enregistré = 3/5.",
        "",
        "## Grille CAP (fenêtre 20j, seuil de vote 3/5)",
        "",
        "| CAP | PASS (Sharpe ET rendement > BH) |",
        "|---|---|",
    ]
    gate32 = votes >= 3
    for cap in CAP_GRID:
        start = max(first_valid, 20)
        ok = run_one(r, gate32, start, cap, 20)
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {'OUI' if ok else 'non'}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (CAP 2.0x, seuil de vote 3/5)")
    lines.append("")
    lines.append("| Fenêtre | PASS (Sharpe ET rendement > BH) |")
    lines.append("|---|---|")
    for window in WINDOW_GRID:
        start = max(first_valid, window)
        ok = run_one(r, gate32, start, 2.0, window)
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {'OUI' if ok else 'non'}{marker} |")

    lines.append("")
    lines.append("## Grille seuil de vote (CAP 2.0x, fenêtre 20j)")
    lines.append("")
    lines.append("| Seuil (sur 5) | %j actif | PASS (Sharpe ET rendement > BH) |")
    lines.append("|---|---|---|")
    for vt in VOTE_GRID:
        gate_v = votes >= vt
        start = max(first_valid, 20)
        ok = run_one(r, gate_v, start, 2.0, 20)
        pct_active = 100 * gate_v[start:].mean()
        marker = " ← seuil pré-enregistré" if vt == 3 else ""
        lines.append(f"| {vt}/5 | {pct_active:.1f}% | {'OUI' if ok else 'non'}{marker} |")

    out = ROOT / "results" / "nonml_ensemble_vote_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

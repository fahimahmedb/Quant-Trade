"""Robustesse — Overlay vol-targeting gaté par Santa Claus Rally. Grille
CAP ET grille de fenêtre de vol (PAS un retuning de la fenêtre
calendaire DEC_TAIL/JAN_HEAD), autour des valeurs pré-enregistrées
(CAP=2.0x, fenêtre=20j).
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
from nonml_santa_vol_targeting_overlay_backtest import santa_claus_mask, COST_BPS, TARGET_VOL_ANNUAL, ANNUALIZATION, MARKETS  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]


def position_for(close: np.ndarray, dates, cap: float, vol_window: int) -> np.ndarray:
    r = np.log(close[1:] / close[:-1])
    gate = santa_claus_mask(dates)[1:]
    vol_ann = pd.Series(r).rolling(vol_window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt = TARGET_VOL_ANNUAL / vol_lagged
    vt = np.clip(vt, 1.0, cap)
    vt = np.nan_to_num(vt, nan=1.0)
    return np.where(gate, vt, 1.0)


def run_one(close: np.ndarray, dates, cap: float, vol_window: int) -> bool:
    r = np.log(close[1:] / close[:-1])
    pos_full = position_for(close, dates, cap, vol_window)
    start = vol_window
    r_t = r[start:]
    pos = pos_full[start:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if path.exists():
            df = load_ohlc(str(path))
            quality_report(df)
            dfs[name] = df

    lines = [
        "# Robustesse — Overlay vol-targeting gaté par Santa Claus Rally (grilles CAP et fenêtre, PAS un retuning de la fenêtre calendaire)",
        "",
        "CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j.",
        "",
        "## Grille CAP (fenêtre fixée à 20j)",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        n_pass = sum(run_one(df["close"].values, df["date"], cap, 20) for df in dfs.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(dfs)}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | Nb marchés PASS /5 |")
    lines.append("|---|---|")
    for window in WINDOW_GRID:
        n_pass = sum(run_one(df["close"].values, df["date"], 2.0, window) for df in dfs.values())
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {n_pass}/{len(dfs)}{marker} |")

    out = ROOT / "results" / "nonml_santa_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

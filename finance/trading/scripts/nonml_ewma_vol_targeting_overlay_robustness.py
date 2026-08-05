"""Robustesse — Overlay vol-targeting estimateur EWMA. Grille CAP ET
grille de fenêtre d'amorçage (PAS un retuning de λ, réutilisé tel quel
de ewma_path, Règle 7), autour des valeurs pré-enregistrées (CAP=2.0x,
fenêtre d'amorçage=20j).
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
from nonml_ewma_vol_targeting_overlay_backtest import COST_BPS, LAM, TARGET_VOL_ANNUAL, ANNUALIZATION, MARKETS  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
SEED_WINDOW_GRID = [15, 20, 25, 30]


def position_for(r: np.ndarray, cap: float, seed_window: int) -> np.ndarray:
    n = len(r)
    s2 = np.full(n, np.nan)
    s2[seed_window - 1] = r[:seed_window].var(ddof=1)
    for t in range(seed_window, n):
        s2[t] = LAM * s2[t - 1] + (1 - LAM) * r[t - 1] ** 2
    vol_ann = np.sqrt(np.clip(s2, 0.0, None)) * ANNUALIZATION
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL / vol_ann
    pos = np.clip(pos, 0.0, cap)
    return np.nan_to_num(pos, nan=1.0)


def run_one(r: np.ndarray, cap: float, seed_window: int) -> bool:
    pos_full = position_for(r, cap, seed_window)
    start = seed_window
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
    data = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if path.exists():
            df = load_ohlc(str(path))
            quality_report(df)
            close = df["close"].values
            r = np.log(close[1:] / close[:-1])
            data[name] = r

    lines = [
        "# Robustesse — Overlay vol-targeting EWMA (grilles CAP et fenêtre d'amorçage, PAS un retuning de λ)",
        "",
        f"CAP pré-enregistré = 2.0x, fenêtre d'amorçage pré-enregistrée = 20j. λ={LAM} (paramètre "
        "réutilisé de ewma_path, Étape C) reste fixe.",
        "",
        "## Grille CAP (fenêtre d'amorçage fixée à 20j)",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        n_pass = sum(run_one(r, cap, 20) for r in data.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(data)}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre d'amorçage (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | Nb marchés PASS /5 |")
    lines.append("|---|---|")
    for window in SEED_WINDOW_GRID:
        n_pass = sum(run_one(r, 2.0, window) for r in data.values())
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {n_pass}/{len(data)}{marker} |")

    out = ROOT / "results" / "nonml_ewma_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

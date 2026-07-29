"""Robustesse — Vol-targeting défensif, critère Calmar. Grille
TARGET_VOL_ANNUAL ET grille de fenêtre de vol, autour des valeurs
pré-enregistrées (prévu dans le PREREG avant tout calcul).
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
from nonml_defensive_calmar_vol_targeting_overlay_backtest import CAP, COST_BPS, MARKETS, ANNUALIZATION  # noqa: E402

TARGET_VOL_GRID = [0.15, 0.20, 0.25, 0.30]
WINDOW_GRID = [15, 20, 25, 30]


def position_for(r, target_vol, vol_window):
    vol_ann = pd.Series(r).rolling(vol_window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = target_vol / vol_lagged
    pos = np.clip(pos, 0.0, CAP)
    return np.nan_to_num(pos, nan=1.0)


def run_grid(target_vol, vol_window):
    n_success = 0
    for name, fname in MARKETS.items():
        df = load_ohlc(str(REPO_ROOT / "data" / fname))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        pos_full = position_for(r, target_vol, vol_window)
        start = vol_window
        r_t, pos = r[start:], pos_full[start:]
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
        pnl_bh = r_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4
        me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
        calmar_bh = me_bh["calmar"] if np.isfinite(me_bh["calmar"]) else -np.inf
        calmar_ov = me_ov["calmar"] if np.isfinite(me_ov["calmar"]) else -np.inf
        n_success += int(calmar_ov > calmar_bh)
    return n_success


def main():
    lines = [
        "# Robustesse — Vol-targeting défensif, critère Calmar (grilles TARGET_VOL_ANNUAL et fenêtre de vol)",
        "",
        "TARGET_VOL_ANNUAL pré-enregistré = 20%, fenêtre pré-enregistrée = 20j.",
        "",
        "## Grille TARGET_VOL_ANNUAL (fenêtre fixée à 20j)",
        "",
        "| Cible vol | Marchés Calmar>BH | PASS (≥4/5) |",
        "|---|---|---|",
    ]
    for tv in TARGET_VOL_GRID:
        n = run_grid(tv, 20)
        marker = " ← cible pré-enregistrée" if tv == 0.20 else ""
        lines.append(f"| {tv:.0%} | {n}/5 | {'OUI' if n >= 4 else 'non'}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (cible 20%)")
    lines.append("")
    lines.append("| Fenêtre | Marchés Calmar>BH | PASS (≥4/5) |")
    lines.append("|---|---|---|")
    for window in WINDOW_GRID:
        n = run_grid(0.20, window)
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {n}/5 | {'OUI' if n >= 4 else 'non'}{marker} |")

    out = ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

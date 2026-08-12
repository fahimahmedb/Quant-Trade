"""Robustesse — Overlay vol-targeting gaté par la prévision GJR-t
walk-forward (cycle #234).

Grille CAP et grille de fenêtre de vol réalisée (le dénominateur du
mécanisme #46, PAS un retuning) autour des valeurs pré-enregistrées
(CAP=2.0x, VOL_WINDOW=20j). T0, REFIT_EVERY et MEDIAN_WINDOW (paramètres
du modèle GJR-t et de la porte elle-même) restent fixes, comme pour
toutes les portes précédentes de cette famille (#47/#54/#57/#78/#80/
#216-#223/#234) — la prévision GJR-t et la porte ne dépendent ni de CAP
ni de VOL_WINDOW, donc `walk_forward_vol_forecast` n'est calculé qu'une
seule fois (même principe que `..._volatility_managed_portfolio_gjr_
robustness.py`, #165).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import walk_forward_vol_forecast  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_gjr_forecast_gate_vol_targeting_overlay_backtest import (  # noqa: E402
    MARKET_FILE, T0, REFIT_EVERY, MEDIAN_WINDOW, VOL_WINDOW,
    TARGET_VOL_ANNUAL, CAP, COST_BPS, ANNUALIZATION,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]


def evaluate(gate: np.ndarray, r_frac: np.ndarray, cap: float, window: int, start: int):
    vol_ann_frac = pd.Series(r_frac).rolling(window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann_frac, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, cap)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    pos_full = np.where(gate, vt_exposure, 1.0)

    r_t = r_frac[start:]
    pos = pos_full[start:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
    ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    r_pct = log_returns_pct(df).values
    r_frac = r_pct / 100.0

    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    vol_fcst_pct = fc["vol_fcst"]
    valid = vol_fcst_pct[T0:]
    med = pd.Series(valid).rolling(MEDIAN_WINDOW).median().values
    gate_valid = np.nan_to_num(valid <= med, nan=0.0).astype(bool)
    gate = np.zeros(len(r_pct), dtype=bool)
    gate[T0:] = gate_valid

    start = T0 + MEDIAN_WINDOW

    lines = [
        "# Robustesse — Overlay vol-targeting gaté par la prévision GJR-t walk-forward "
        "(grilles CAP et fenêtre de vol réalisée, PAS un retuning de T0/REFIT_EVERY/MEDIAN_WINDOW)",
        "",
        "CAP pré-enregistré = 2.0x, fenêtre de vol réalisée pré-enregistrée = 20j. T0=750, "
        "REFIT_EVERY=21j et MEDIAN_WINDOW=252 (paramètres du modèle GJR-t et de la porte "
        "elle-même) restent fixes — la prévision et la porte sont calculées une seule fois, "
        "la grille ne fait que re-mapper la même série en positions. Marché unique NDX "
        "(périmètre du #234).",
        "",
        "## Grille CAP (fenêtre de vol réalisée fixée à 20j)",
        "",
        "| CAP | PASS |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        ok = evaluate(gate, r_frac, cap, VOL_WINDOW, start)
        marker = " ← CAP pré-enregistré" if cap == CAP else ""
        lines.append(f"| {cap}x | {'OUI' if ok else 'non'}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol réalisée (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | PASS |")
    lines.append("|---|---|")
    for window in WINDOW_GRID:
        ok = evaluate(gate, r_frac, CAP, window, start)
        marker = " ← fenêtre pré-enregistrée" if window == VOL_WINDOW else ""
        lines.append(f"| {window}j | {'OUI' if ok else 'non'}{marker} |")

    out = ROOT / "results" / "nonml_gjr_forecast_gate_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

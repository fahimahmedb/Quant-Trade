"""Robustesse — Overlay vol-targeting gaté par le ν glissant (MLE
Student-t). Grille CAP ET grille de fenêtre de vol (PAS un retuning de
NU_WINDOW, REFIT_EVERY ni de MEDIAN_WINDOW, les paramètres du signal de
porte lui-même), autour des valeurs pré-enregistrées (CAP=2.0x,
fenêtre=20j). La porte (ν et sa médiane) ne dépend ni de CAP ni de la
fenêtre de vol, donc n'est calculée qu'une seule fois par marché (coût du
MLE, même principe que les robustesses GJR-t/HAR-P).
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

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_student_t_tail_vol_targeting_overlay_backtest import (  # noqa: E402
    calm_nu_mask, COST_BPS, TARGET_VOL_ANNUAL, ANNUALIZATION,
    NU_WINDOW, MEDIAN_WINDOW, MARKETS,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]


def position_for(r: np.ndarray, gate: np.ndarray, cap: float, window: int) -> np.ndarray:
    vol_ann = pd.Series(r).rolling(window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL / vol_lagged
    pos = np.clip(pos, 1.0, cap)
    pos = np.where(gate, pos, 1.0)
    return np.nan_to_num(pos, nan=1.0)


def run_one(r: np.ndarray, gate: np.ndarray, cap: float, window: int) -> bool:
    start = NU_WINDOW + MEDIAN_WINDOW
    pos_full = position_for(r, gate, cap, window)
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
    data = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        if len(r) <= NU_WINDOW + MEDIAN_WINDOW:
            continue
        gate = calm_nu_mask(r)
        data[name] = (r, gate)

    lines = [
        "# Robustesse — Overlay vol-targeting gaté par le ν glissant (MLE Student-t) "
        "(grilles CAP et fenêtre de vol, PAS un retuning de NU_WINDOW/REFIT_EVERY/MEDIAN_WINDOW)",
        "",
        "CAP pré-enregistré = 2.0x, fenêtre de vol pré-enregistrée = 20j. NU_WINDOW=252, "
        "REFIT_EVERY=21j et MEDIAN_WINDOW=252 (paramètres du signal de porte lui-même) "
        "restent fixes, comme pour toutes les portes précédentes de cette famille "
        "(#47/#54/#57/#78/#80/#216-#223/#234). La porte n'est calculée qu'une seule fois "
        f"par marché ({len(data)} marchés).",
        "",
        "## Grille CAP (fenêtre fixée à 20j)",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        n_pass = sum(run_one(r, gate, cap, 20) for r, gate in data.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(data)}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | Nb marchés PASS /5 |")
    lines.append("|---|---|")
    for window in WINDOW_GRID:
        n_pass = sum(run_one(r, gate, 2.0, window) for r, gate in data.values())
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {n_pass}/{len(data)}{marker} |")

    out = ROOT / "results" / "nonml_student_t_tail_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

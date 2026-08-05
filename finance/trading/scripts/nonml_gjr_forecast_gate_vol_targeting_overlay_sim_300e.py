"""Simulation — 300 EUR dans l'overlay vol-targeting gaté par la prévision
GJR-t walk-forward, sur les ~3 derniers mois du NDX (fenêtre illustrative
usuelle du backlog, 63 séances).

Aucun paramètre retouché : positions recalculées avec exactement le même
pipeline que `nonml_gjr_forecast_gate_vol_targeting_overlay_backtest.py`
(pas d'artefact npz pour ce cycle — non déclaré au PREREG, réservé à un
futur cycle Règle 9 dédié si celui-ci est repris dans la file d'attente).
Cette fenêtre est **illustrative** : 63 séances ne tranchent rien
statistiquement, le verdict reste celui du backtest complet (9270 séances).
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

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def mdd_pct(equity):
    running_max = np.maximum.accumulate(equity)
    return float((equity / running_max - 1.0).min() * 100)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    ser = log_returns_pct(df)
    r_pct = ser.values
    dates = ser.index
    r_frac = r_pct / 100.0

    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    vol_fcst_pct = fc["vol_fcst"]
    valid = vol_fcst_pct[T0:]
    med = pd.Series(valid).rolling(MEDIAN_WINDOW).median().values
    gate_valid = np.nan_to_num(valid <= med, nan=0.0).astype(bool)
    gate = np.zeros(len(r_pct), dtype=bool)
    gate[T0:] = gate_valid

    vol_ann_frac = pd.Series(r_frac).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann_frac, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    pos_full = np.where(gate, vt_exposure, 1.0)

    pos = pos_full[-WINDOW_DAYS:]
    r = r_frac[-WINDOW_DAYS:]
    dates_w = pd.to_datetime(dates[-WINDOW_DAYS:])

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    eq_ov = CAPITAL0 * np.cumprod(1.0 + pnl_ov)
    eq_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)
    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, overlay vol-targeting gaté par la prévision GJR-t "
        "(~3 derniers mois, NDX)",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({len(r)} séances). "
        f"Position = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j, 1.0, {CAP}x) "
        f"si porte GJR-t active, sinon 1.0x. Coûts {COST_BPS:.0f} bps.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay vol-targeting gaté GJR-t** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        f"Exposition moyenne sur la fenêtre : {pos.mean():.2f}x "
        f"(min {pos.min():.2f}x, max {pos.max():.2f}x).",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (9270 séances, "
        "PASS de niveau 1, marge très marginale). Règle 9 non exécutée à ce stade (à faire "
        "si ce cycle est repris dans la file d'attente des PASS frais).",
    ]

    out = ROOT / "results" / "nonml_gjr_forecast_gate_vol_targeting_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

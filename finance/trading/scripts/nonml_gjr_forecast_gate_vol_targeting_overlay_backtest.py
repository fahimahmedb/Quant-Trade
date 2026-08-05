"""Backtest — Overlay vol-targeting gaté par la prévision GJR-t
walk-forward (spécification pré-enregistrée dans
PREREG_gjr_forecast_gate_vol_targeting_overlay.md, committée avant ce
script). Réutilise overlay.py::walk_forward_vol_forecast (Étape C,
déjà validé au SPA, déjà réutilisé au #165) comme PORTE du mécanisme
#46 standard (vol réalisée close-to-close inchangée comme dénominateur)
— distinct du #165/#166 qui remplaçaient l'estimateur lui-même.
NDX uniquement. n_trials=1, aucune dépendance ML. Règle de succès
renforcée.
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

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import walk_forward_vol_forecast  # noqa: E402
from prediction import trading_metrics  # noqa: E402

MARKET_FILE = "nasdaq100_daily.txt"
T0 = 750
REFIT_EVERY = 21
MEDIAN_WINDOW = 252
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
CAP = 2.0
COST_BPS = 5.0
ANNUALIZATION = np.sqrt(252)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    ser = log_returns_pct(df)
    r_pct = ser.values  # % , r_pct[k] = 100*log(close[k+1]/close[k])
    dates = ser.index
    r_frac = r_pct / 100.0

    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    vol_fcst_pct = fc["vol_fcst"]  # NaN avant T0, deja causale (walk-forward)

    # porte : vol_fcst <= sa mediane glissante 252j, calculee uniquement sur
    # la partie valide (>= T0) pour eviter toute contamination par les NaN
    # d'amorcage.
    valid = vol_fcst_pct[T0:]
    med = pd.Series(valid).rolling(MEDIAN_WINDOW).median().values
    gate_valid = valid <= med
    gate_valid = np.nan_to_num(gate_valid, nan=0.0).astype(bool)
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

    start = T0 + MEDIAN_WINDOW
    r_t = r_frac[start:]
    pos = pos_full[start:]
    dates_oos = dates[start:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    np.savez(ROOT / "results" / "nonml_gjr_forecast_gate_vol_targeting_overlay_pnl.npz",
             pos=pos, r_asset=r_t, dates=dates_oos.values, cost_bps=COST_BPS)

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = bool(sharpe_ok and ret_ok)
    gate_active = pos > 1.0

    lines = [
        "# Résultat — Overlay vol-targeting gaté par la prévision GJR-t walk-forward "
        "(pré-enregistré, règle renforcée, NDX uniquement)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si vol_prévue_GJR-t(t) ≤ sa médiane glissante {MEDIAN_WINDOW}j, sinon 1.0x. "
        f"T0={T0}, REFIT_EVERY={REFIT_EVERY}j (walk-forward Étape C réutilisé tel quel). "
        f"{len(r_t)} séances testables.",
        "",
        f"%j porte active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté prévision GJR-t** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'} (marché unique NDX).**",
    ]

    out = ROOT / "results" / "nonml_gjr_forecast_gate_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

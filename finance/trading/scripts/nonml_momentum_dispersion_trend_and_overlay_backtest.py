"""Backtest — Double porte AND : dispersion du momentum (#100) ET
tendance 52w-high (#47) (spécification pré-enregistrée dans
PREREG_momentum_dispersion_trend_and_overlay.md, committée avant ce
script). n_trials=1, aucune dépendance ML. Règle de succès renforcée.
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
from nonml_momentum_dispersion_vol_targeting_overlay_backtest import (  # noqa: E402
    compute_momentum_dispersion_series, MEDIAN_WINDOW,
)
from nonml_trend_vol_targeting_overlay_backtest import near_high_mask, INDEX_LOOKBACK  # noqa: E402

COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (longueur T-1). gate_aligned = porte
    combinee alignee sur close (longueur T, booleenne). Renvoie la
    position pour chaque rendement de r."""
    gate_r = gate_aligned[:-1]  # meme convention causale que #47/#57/#78/#81/#94/#96/#97/#98/#99/#100

    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    pos = np.where(gate_r, vt_exposure, 1.0)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    trend_gate = near_high_mask(close)

    dispersion = compute_momentum_dispersion_series()
    median_disp = dispersion.rolling(MEDIAN_WINDOW).median()
    disp_gate_series = (dispersion >= median_disp)
    disp_gate_aligned_raw = disp_gate_series.reindex(dates_idx.values, method="ffill")
    disp_gate_aligned = disp_gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    gate_combined = trend_gate & disp_gate_aligned

    pos_full = combined_position(bh_full, gate_combined)

    valid_mask = disp_gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, INDEX_LOOKBACK, VOL_WINDOW)

    bh_t = bh_full[start:]
    pos = pos_full[start:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok

    gate_active = (pos > 1.0)
    gate_combined_t = gate_combined[start:-1]
    trend_only = (trend_gate & ~disp_gate_aligned)[start:-1]
    disp_only = (~trend_gate & disp_gate_aligned)[start:-1]

    lines = [
        "# Résultat — Double porte AND dispersion momentum + tendance 52w-high (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si proximité 52w-high(t) ET dispersion momentum(t) ≥ médiane 252j SIMULTANÉMENT, sinon 1.0x. "
        f"{len(bh_t)} séances testables.",
        "",
        f"%j porte combinée (AND) active : {100*gate_combined_t.mean():.1f}% "
        f"(vs tendance seule {100*(trend_only.mean()+gate_combined_t.mean()):.1f}%, "
        f"dispersion seule {100*(disp_only.mean()+gate_combined_t.mean()):.1f}%)",
        f"%j porte combinée avec position résultante >1x : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté AND dispersion∩tendance** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_dispersion_trend_and_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

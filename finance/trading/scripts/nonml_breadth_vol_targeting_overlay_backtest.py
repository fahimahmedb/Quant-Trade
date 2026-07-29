"""Backtest — Overlay vol-targeting gaté par la confirmation multi-marché
(breadth NDX+Russell2000, spécification pré-enregistrée dans
PREREG_breadth_vol_targeting_overlay.md, committée avant ce script).
Combine les cycles #52 (porte) et #46/#47 (mécanisme vol-targeting).
n_trials=1, aucune dépendance ML. Règle de succès renforcée.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CAP = 2.0
INDEX_LOOKBACK = 252
INDEX_THRESHOLD = 0.95
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def near_high_series(df) -> pd.Series:
    close = df["close"].values
    rolling_max = pd.Series(close).rolling(INDEX_LOOKBACK).max().values
    near_high = close >= INDEX_THRESHOLD * rolling_max
    dates = pd.to_datetime(df["date"]).values
    return pd.Series(near_high, index=dates)


def breadth_gate(df_primary, df_confirm) -> np.ndarray:
    """Porte = signal A (primaire) ET signal B (confirmation, aligné par
    date avec ffill), longueur T (alignee sur df_primary["close"])."""
    signal_a = near_high_series(df_primary)
    signal_b = near_high_series(df_confirm)
    dates_primary = pd.to_datetime(df_primary["date"])
    b_aligned = signal_b.reindex(dates_primary.values, method="ffill").fillna(False).values.astype(bool)
    a_aligned = signal_a.values.astype(bool)
    return a_aligned & b_aligned


def combined_position(close: np.ndarray, r: np.ndarray, gate: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (meme longueur que close[1:]).
    gate = porte breadth alignee sur close (longueur T). Renvoie la
    position pour chaque rendement de r : clip(vol_cible/vol_realisee(t-1),
    1.0, CAP) si porte active, 1.0 sinon."""
    # meme convention causale que #47 : gate[i] connu a la cloture du
    # jour i (jour de decision) s'applique a r[i]=log(close[i+1]/close[i])
    # -> gate[:-1], PAS gate[1:] (fuite d'un jour).
    gate_r = gate[:-1]

    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    return np.where(gate_r, vt_exposure, 1.0)


def main():
    df_primary = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_primary)
    df_confirm = load_ohlc(str(REPO_ROOT / "data" / "russell2000_daily.txt"))
    quality_report(df_confirm)

    close = df_primary["close"].values
    bh_full = np.log(close[1:] / close[:-1])
    gate = breadth_gate(df_primary, df_confirm)

    pos_full = combined_position(close, bh_full, gate)
    start = INDEX_LOOKBACK
    bh_t = bh_full[start:]
    pos = pos_full[start:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Overlay vol-targeting gaté par la confirmation multi-marché NDX+Russell2000 (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"quand NDX ET Russell 2000 sont SIMULTANÉMENT ≥{100*INDEX_THRESHOLD:.0f}% de leur plus haut "
        f"{INDEX_LOOKBACK}j, sinon 1.0x. {len(bh_t)} séances testables.",
        "",
        f"%j porte breadth active : {100*gate[start:-1].mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté breadth** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_breadth_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

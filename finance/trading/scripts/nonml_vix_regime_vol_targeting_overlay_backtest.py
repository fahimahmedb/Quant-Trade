"""Backtest — Overlay vol-targeting gaté par le régime VIX (signal
GENUINEMENT externe, pas auto-référentiel comme réalisé/GARCH/EWMA
déjà testés) (spécification pré-enregistrée dans
PREREG_vix_regime_vol_targeting_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée niveau 1 --
SI PASS, ce résultat n'est PAS final, voir Règle 9
(`scripts/nonml_pass_validation_battery.py`).
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

MEDIAN_WINDOW = 252
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def load_vix() -> pd.Series:
    df = pd.read_csv(REPO_ROOT / "data" / "vixcls_daily.csv")
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["VIXCLS"] = pd.to_numeric(df["VIXCLS"], errors="coerce")  # "." (jours fériés) -> NaN
    s = pd.Series(df["VIXCLS"].values, index=df["observation_date"]).dropna()
    return s[~s.index.duplicated(keep="first")].sort_index()


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    gate_r = gate_aligned[:-1]
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    pos = np.where(gate_r, vt_exposure, 1.0)
    return np.nan_to_num(pos, nan=1.0)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    vix = load_vix()
    vix_lagged = vix.shift(1)  # VIX(t-1), causal explicite
    median_vix = vix_lagged.rolling(MEDIAN_WINDOW).median()
    gate_series = (vix_lagged >= median_vix)
    gate_series_filled = gate_series.fillna(False)

    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series_filled.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    pos_full = combined_position(bh_full, gate_aligned)

    valid_mask = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, VOL_WINDOW)

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
    lines = [
        "# Résultat — Overlay vol-targeting gaté par le régime VIX, signal externe (pré-enregistré, règle renforcée niveau 1)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si VIX(t-1) ≥ sa médiane glissante {MEDIAN_WINDOW}j, sinon 1.0x. {len(bh_t)} séances "
        f"testables (historique VIX 1990+, plus court que NDX complet).",
        "",
        f"%j porte régime VIX active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté régime VIX** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS (niveau 1)' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py vix_regime_vol_targeting_overlay` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_vix_regime_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    # Sauvegarde INCONDITIONNELLE du P&L (cycle #426, lot 4) : la condition
    # `if verdict:` privait le diagnostic du #415 de ce candidat, qui porte un
    # FAIL. Convention du #416. Aucune ligne de calcul n'est modifiee.
    dates_used = dates_idx.values[1:][start:]
    np.savez(
        ROOT / "results" / "nonml_vix_regime_vol_targeting_overlay_pnl.npz",
        pos=pos, r_asset=bh_t, dates=dates_used, cost_bps=COST_BPS,
    )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Backtest — Overlay vol-targeting gaté par vote majoritaire (≥3/5)
entre 5 gates DÉJÀ VALIDÉES niveau 1 dans ce backlog (#78, #89, #100,
#104, #112) (spécification pré-enregistrée dans
PREREG_ensemble_vote_vol_targeting_overlay.md, committée avant ce
script). n_trials=1 pour CETTE construction d'ensemble. Règle de succès
renforcée niveau 1 -- SI PASS, ce résultat n'est PAS final, voir Règle 9
(`scripts/nonml_pass_validation_battery.py`).

Réimporte SANS modification les fonctions compute_*_series() des 5
scripts déjà committés (aucune réimplémentation divergente).
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

COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)
VOTE_THRESHOLD = 3  # sur 5


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


def build_votes(dates_idx):
    """Renvoie (vote_count[T], first_valid_overall) -- reimporte les 5
    gates deja validees SANS les modifier."""
    votes = np.zeros(len(dates_idx), dtype=int)
    first_valids = []

    # 1. #78 dispersion cross-sectionnelle
    from nonml_dispersion_vol_targeting_overlay_backtest import (
        compute_dispersion_series, MEDIAN_WINDOW as MW1,
    )
    s = compute_dispersion_series()
    med = s.rolling(MW1).median()
    gate_series = (s >= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    votes += gate_aligned.astype(int)
    valid = gate_raw.notna().values
    first_valids.append(int(np.argmax(valid)) if valid.any() else len(valid))

    # 2. #89 weakness breadth (continue -> seuillee a >0, comportement identique a l'original)
    from nonml_weakness_breadth_vol_targeting_overlay_backtest import (
        compute_weakness_breadth_series, INDEX_LOOKBACK as IL2,
    )
    b = compute_weakness_breadth_series()
    b_raw = b.reindex(dates_idx.values, method="ffill").values
    gate_aligned = np.nan_to_num(b_raw, nan=0.0) > 0.0
    votes += gate_aligned.astype(int)
    first_valids.append(int(np.argmax(~np.isnan(b_raw))) if np.isfinite(b_raw).any() else len(b_raw))
    first_valids[-1] = max(first_valids[-1], IL2)

    # 3. #100 dispersion du momentum
    from nonml_momentum_dispersion_vol_targeting_overlay_backtest import (
        compute_momentum_dispersion_series, MEDIAN_WINDOW as MW3,
    )
    s = compute_momentum_dispersion_series()
    med = s.rolling(MW3).median()
    gate_series = (s >= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    votes += gate_aligned.astype(int)
    valid = gate_raw.notna().values
    first_valids.append(int(np.argmax(valid)) if valid.any() else len(valid))

    # 4. #104 position continue dans le range 252j
    from nonml_range_position_vol_targeting_overlay_backtest import (
        compute_range_position_series, MEDIAN_WINDOW as MW4,
    )
    s = compute_range_position_series()
    med = s.rolling(MW4).median()
    gate_series = (s >= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    votes += gate_aligned.astype(int)
    valid = gate_raw.notna().values
    first_valids.append(int(np.argmax(valid)) if valid.any() else len(valid))

    # 5. #112 spread decile de momentum
    from nonml_momentum_decile_spread_vol_targeting_overlay_backtest import (
        compute_decile_spread_series, MEDIAN_WINDOW as MW5,
    )
    s = compute_decile_spread_series()
    med = s.rolling(MW5).median()
    gate_series = (s >= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    votes += gate_aligned.astype(int)
    valid = gate_raw.notna().values
    first_valids.append(int(np.argmax(valid)) if valid.any() else len(valid))

    return votes, max(first_valids)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    votes, first_valid = build_votes(dates_idx)
    gate_aligned = votes >= VOTE_THRESHOLD

    pos_full = combined_position(bh_full, gate_aligned)
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
    vote_active_pct = 100 * (votes[start:] >= VOTE_THRESHOLD).mean()
    lines = [
        "# Résultat — Overlay vol-targeting gaté par vote majoritaire (≥3/5 gates déjà validées) (pré-enregistré, règle renforcée niveau 1)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si ≥{VOTE_THRESHOLD}/5 des gates #78/#89/#100/#104/#112 sont actives simultanément, "
        f"sinon 1.0x. {len(bh_t)} séances testables (intersection des 5 fenêtres individuelles).",
        "",
        f"%j porte ensemble active : {vote_active_pct:.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vote majoritaire (≥3/5)** | **{me_ov['sharpe_ann']:+.2f}** | "
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
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9), ET biais de sélection "
                     "assumé (les 5 membres sont choisis PARCE QU'ils étaient déjà PASS niveau 1). Doit "
                     "encore passer `nonml_pass_validation_battery.py "
                     "ensemble_vote_vol_targeting_overlay` (n_trials=taille du backlog, pas remis à 5).**")

    out = ROOT / "results" / "nonml_ensemble_vote_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        dates_used = dates_idx.values[1:][start:]
        np.savez(
            ROOT / "results" / "nonml_ensemble_vote_vol_targeting_overlay_pnl.npz",
            pos=pos, r_asset=bh_t, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

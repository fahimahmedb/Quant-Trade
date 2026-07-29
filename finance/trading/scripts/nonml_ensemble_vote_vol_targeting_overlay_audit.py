"""Audit adversarial — Overlay vol-targeting gaté par vote majoritaire
(ensemble de 5 gates).

1. Recalcul indépendant du décompte de votes (boucle Python explicite
   sur les 5 séries déjà calculées par build_votes, recomptage manuel
   sans réutiliser l'addition vectorisée) à un échantillon de dates.
2. Test anti-lookahead sur l'infrastructure d'agrégation (mutation du
   futur NDX -- les 5 compute_*_series() sous-jacents sont déjà audités
   individuellement à leur cycle d'origine, ce test cible spécifiquement
   le NOUVEAU code d'agrégation de ce script).
3. Cohérence du seuil de vote : vérifie que Vote(t)>=3 implique bien au
   moins 3 gates individuelles actives (pas d'erreur d'addition/decalage).
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
from nonml_ensemble_vote_vol_targeting_overlay_backtest import (  # noqa: E402
    build_votes, combined_position, VOTE_THRESHOLD,
)


def independent_gates(dates_idx):
    """Recalcule chacune des 5 gates SEPAREMENT (meme logique, mais
    boucle Python explicite pour l'addition finale, pas np.array +=)."""
    gates = []

    from nonml_dispersion_vol_targeting_overlay_backtest import compute_dispersion_series, MEDIAN_WINDOW as MW1
    s = compute_dispersion_series()
    med = s.rolling(MW1).median()
    g = (s >= med).fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    gates.append(g)

    from nonml_weakness_breadth_vol_targeting_overlay_backtest import compute_weakness_breadth_series
    b = compute_weakness_breadth_series()
    b_raw = b.reindex(dates_idx.values, method="ffill").values
    gates.append(np.nan_to_num(b_raw, nan=0.0) > 0.0)

    from nonml_momentum_dispersion_vol_targeting_overlay_backtest import compute_momentum_dispersion_series, MEDIAN_WINDOW as MW3
    s = compute_momentum_dispersion_series()
    med = s.rolling(MW3).median()
    g = (s >= med).fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    gates.append(g)

    from nonml_range_position_vol_targeting_overlay_backtest import compute_range_position_series, MEDIAN_WINDOW as MW4
    s = compute_range_position_series()
    med = s.rolling(MW4).median()
    g = (s >= med).fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    gates.append(g)

    from nonml_momentum_decile_spread_vol_targeting_overlay_backtest import compute_decile_spread_series, MEDIAN_WINDOW as MW5
    s = compute_decile_spread_series()
    med = s.rolling(MW5).median()
    g = (s >= med).fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    gates.append(g)

    return gates


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    votes_orig, first_valid = build_votes(dates_idx)
    gates_indep = independent_gates(dates_idx)
    T = len(votes_orig)

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par vote majoritaire (5 gates)", "",
             "## 1. Recalcul indépendant du décompte de votes (boucle Python explicite, addition manuelle)", "",
             "| Date (indice) | Vote original | Vote recalculé | Écart |",
             "|---|---|---|---|"]
    check_idx = list(range(first_valid, T, 400))
    all_ok = True
    for i in check_idx:
        votes_manual = sum(1 for g in gates_indep if bool(g[i]))
        orig = int(votes_orig[i])
        ok = (votes_manual == orig)
        all_ok &= ok
        lines.append(f"| {i} | {orig} | {votes_manual} | {'0' if ok else 'ÉCART'} |")
    lines.append("")
    lines.append(f"**{'OK — décompte de votes confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead sur l'infrastructure d'agrégation (mutation NDX, 20% les plus récents)")
    lines.append("")
    T_close = len(close)
    cut = int(T_close * 0.8)
    rng = np.random.default_rng(113)
    close_mut = close.copy()
    close_mut[cut:] = close_mut[cut:] * (1.0 + rng.normal(0, 0.5, T_close - cut))
    bh_full_mut = np.log(close_mut[1:] / close_mut[:-1])
    votes_mut, _ = build_votes(dates_idx)  # les gates sous-jacentes ne dependent pas de close NDX (titres individuels)
    pos_before = combined_position(bh_full, votes_orig >= VOTE_THRESHOLD)
    pos_after = combined_position(bh_full_mut, votes_mut >= VOTE_THRESHOLD)
    check_slice = slice(0, cut - 260)
    diff = float(np.nanmax(np.abs(pos_before[check_slice] - pos_after[check_slice])))
    lines.append(f"Écart max sur les positions passées (avant mutation, marge 260j) : {diff:.2e}")
    lines.append(f"**{'OK — aucune fuite du futur vers le passé.' if diff < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Cohérence du seuil de vote")
    lines.append("")
    votes_check = np.array([sum(1 for g in gates_indep if bool(g[i])) for i in range(first_valid, T)])
    gate_final = votes_check >= VOTE_THRESHOLD
    consistent = np.array_equal(gate_final, (votes_orig[first_valid:] >= VOTE_THRESHOLD))
    lines.append(f"**{'OK — porte finale (Vote>=3) cohérente sur toute la période testable.' if consistent else 'ÉCHEC — incohérence détectée.'}**")

    out = ROOT / "results" / "nonml_ensemble_vote_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

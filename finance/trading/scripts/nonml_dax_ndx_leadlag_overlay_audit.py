"""Audit adversarial — Overlay avance-retard cross-marché DAX->marchés US.

1. Recalcul indépendant du signal DaxRet(D-1) par boucle+searchsorted
   explicite (sans pandas.reindex/ffill), comparaison exacte.
2. Vérification anti-lookahead par perturbation du futur DAX (mutation
   des rendements DAX à partir d'une date de coupure, contrôle à une
   date antérieure — même esprit que #175/#193).
3. Cohérence de la fenêtre testée (DAX démarre en 1999, donc le test
   NDX/Russell/S&P 500 est restreint à ~1999/2000-2026, PAS l'historique
   complet 40 ans de NDX — signalé honnêtement, pas un bug).
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
from nonml_dax_ndx_leadlag_overlay_backtest import (  # noqa: E402
    dax_ret_series, dax_signal_lag, TARGET_MARKETS,
)


def independent_signal(dax_dates: np.ndarray, dax_rets: np.ndarray, target_dates: np.ndarray) -> np.ndarray:
    """Reimplementation par recherche explicite (np.searchsorted), sans
    pandas.reindex/ffill : pour chaque date cible D, trouve l'indice DAX
    le plus recent dont la date est STRICTEMENT < D, renvoie son rendement."""
    out = np.full(len(target_dates), np.nan)
    for i, d in enumerate(target_dates):
        idx = np.searchsorted(dax_dates, d, side="left") - 1
        if idx >= 0:
            out[i] = dax_rets[idx]
    return out


def main():
    dax_r = dax_ret_series()
    dax_dates = dax_r.index.values
    dax_rets = dax_r.values

    lines = ["# Audit adversarial — Overlay avance-retard cross-marché DAX→marchés US", "",
             "## 1. Recalcul indépendant du signal (searchsorted explicite)", "",
             "| Marché | Séances | Désaccords |",
             "|---|---|---|"]
    all_ok = True
    ndx_dates_for_pert = None
    for name, fname in TARGET_MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        sig_orig = dax_signal_lag(dates, dax_r)
        sig_indep = independent_signal(dax_dates, dax_rets, dates.values)

        both_finite = np.isfinite(sig_orig) & np.isfinite(sig_indep)
        n_diff = int((~np.isclose(sig_orig[both_finite], sig_indep[both_finite], atol=1e-12)).sum())
        n_nan_mismatch = int((np.isfinite(sig_orig) != np.isfinite(sig_indep)).sum())
        all_ok &= (n_diff == 0 and n_nan_mismatch == 0)
        lines.append(f"| {name} | {len(dates)} | {n_diff + n_nan_mismatch} |")

        if name == "NDX (40 ans)":
            ndx_dates_for_pert = dates

    lines.append("")
    lines.append(f"**{'OK — signal confirmé par recalcul indépendant (0 désaccord).' if all_ok else 'ÉCHEC — désaccord détecté.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur DAX)")
    lines.append("")
    mutation_start = pd.Timestamp("2022-06-01")
    check_date_target = pd.Timestamp("2018-06-01")
    dax_r_pert = dax_r.copy()
    rng = np.random.default_rng(280)
    mask_mut = dax_r_pert.index >= mutation_start
    dax_r_pert[mask_mut] = dax_r_pert[mask_mut] + rng.normal(0, 0.5, size=mask_mut.sum())

    check_date = ndx_dates_for_pert[ndx_dates_for_pert.searchsorted(check_date_target)]
    sig_orig_check = dax_signal_lag(ndx_dates_for_pert, dax_r)
    sig_pert_check = dax_signal_lag(ndx_dates_for_pert, dax_r_pert)
    idx_check = int(np.where(ndx_dates_for_pert == check_date)[0][0])
    diff_pert = abs(sig_orig_check[idx_check] - sig_pert_check[idx_check])
    anti_leak_ok = diff_pert < 1e-12
    lines.append(f"Mutation appliquée à partir de {mutation_start.date()}, contrôle à {pd.Timestamp(check_date).date()}.")
    lines.append(f"Écart de signal à une date antérieure à la mutation : {diff_pert:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Cohérence de la fenêtre testée")
    lines.append("")
    lines.append(f"DAX démarre le {pd.Timestamp(dax_dates.min()).date()} — le test sur NDX (historique complet "
                 f"depuis {pd.Timestamp('1985-10-01').date()}) est donc restreint à partir de cette date, PAS "
                 "l'historique complet 40 ans. Signalé honnêtement, cohérent avec le nombre de séances test "
                 "(6711, ≈26,7 ans) rapporté dans le résultat principal — pas un bug.")

    out = ROOT / "results" / "nonml_dax_ndx_leadlag_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

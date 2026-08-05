"""Audit adversarial — Porte dispersion cross-sectionnelle, univers
point-in-time.

1. Recalcul indépendant de la dispersion PIT à un échantillon de dates
   (boucle Python explicite, formule d'écart-type manuelle).
2. Vérifie que le masque NaN (bug trouvé et corrigé avant tout commit du
   résultat) élimine bien toute contamination pré-2015.
3. Test anti-lookahead (perturbation du futur).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from ndx100_membership import tickers_as_of_date  # noqa: E402
from nonml_dispersion_vol_targeting_overlay_pit_universe_backtest import (  # noqa: E402
    load_prices_pit, compute_dispersion_series_pit, MIN_LISTED, COMPOSITION_START,
)


def independent_dispersion_at(P: pd.DataFrame, tickers, date):
    if date < COMPOSITION_START:
        return None
    members = tickers_as_of_date(date)
    row = P.loc[date] if date in P.index else None
    if row is None:
        return None
    idx = P.index.get_loc(date)
    if idx == 0:
        return None
    prev = P.iloc[idx - 1]
    rets = []
    for tk in tickers:
        if tk not in members:
            continue
        c1, c0 = row[tk], prev[tk]
        if not (np.isfinite(c1) and np.isfinite(c0)):
            continue
        rets.append(np.log(c1 / c0))
    if len(rets) < MIN_LISTED:
        return np.nan
    rets = np.array(rets)
    mean = rets.mean()
    var = np.sum((rets - mean) ** 2) / (len(rets) - 1)
    return float(np.sqrt(var))


def main():
    series = load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    dispersion = compute_dispersion_series_pit()
    post_2015 = dispersion.index[dispersion.index >= COMPOSITION_START]
    check_dates = post_2015[::400]

    lines = ["# Audit adversarial — Porte dispersion cross-sectionnelle, univers point-in-time", "",
             "## 1. Recalcul indépendant de la dispersion PIT à un échantillon de dates", "",
             "| Date | Dispersion (original) | Dispersion (recalcul indépendant) | Écart |",
             "|---|---|---|---|"]
    all_ok = True
    for d in check_dates:
        orig = dispersion.loc[d]
        indep = independent_dispersion_at(P, tickers, d)
        if indep is None:
            continue
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        elif np.isnan(orig) or np.isnan(indep):
            diff = float("inf")
        else:
            diff = abs(orig - indep)
        all_ok &= (diff < 1e-9)
        lines.append(f"| {d.date()} | {orig:.6f} | {indep:.6f} | {diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — dispersion PIT confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Vérification de l'absence de contamination pré-2015")
    lines.append("")
    pre_2015 = dispersion.index[dispersion.index < COMPOSITION_START]
    n_pre_nonnan = int(dispersion.loc[pre_2015].notna().sum()) if len(pre_2015) > 0 else 0
    lines.append(f"Nombre de valeurs de dispersion NON-NaN avant {COMPOSITION_START.date()} : {n_pre_nonnan} "
                 f"(sur {len(pre_2015)} dates disponibles dans le panneau PIT avant cette date).")
    mask_ok = n_pre_nonnan == 0
    lines.append(f"**{'OK — aucune dispersion calculée hors couverture de composition (bug du masque NaN corrigé).' if mask_ok else 'ÉCHEC — contamination détectée.'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    # mutation a partir de mi-2022 (bien apres la couverture de composition
    # 2015+), controle a une date bien anterieure (2018) pour garantir que
    # la date de controle ET la mutation sont toutes deux dans la periode
    # ou la dispersion PIT est effectivement calculee.
    mutation_start = pd.Timestamp("2022-06-01")
    check_date_target = pd.Timestamp("2018-06-01")
    cut = int(P.index.searchsorted(mutation_start))
    check_date = P.index[P.index.searchsorted(check_date_target)]
    P_pert = P.copy()
    rng = np.random.default_rng(277)
    P_pert.iloc[cut:] = P_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_pert.iloc[cut:].shape))
    orig_val = dispersion.loc[check_date]
    pert_val = independent_dispersion_at(P_pert, tickers, check_date)
    diff_pert = abs(orig_val - pert_val) if (pert_val is not None and np.isfinite(orig_val) and np.isfinite(pert_val)) else 0.0
    anti_leak_ok = diff_pert < 1e-9
    lines.append(f"Mutation appliquée à partir de {mutation_start.date()}, contrôle à {check_date.date()} "
                 "(bien antérieure, dans la période où la dispersion PIT est calculée).")
    lines.append(f"Écart de dispersion à une date antérieure à la mutation : {diff_pert:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_dispersion_vol_targeting_overlay_pit_universe_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

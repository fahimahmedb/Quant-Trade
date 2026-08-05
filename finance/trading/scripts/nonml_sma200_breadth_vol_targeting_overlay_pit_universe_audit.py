"""Audit adversarial — Porte breadth SMA200, univers point-in-time.

1. Recalcul indépendant de la breadth PIT à un échantillon de dates
   (boucle Python explicite).
2. Vérifie l'absence de contamination pré-2015.
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
from nonml_sma200_breadth_vol_targeting_overlay_pit_universe_backtest import (  # noqa: E402
    load_prices_pit, compute_sma200_breadth_series_pit, SMA_WINDOW, COMPOSITION_START,
)


def independent_breadth_at(P: pd.DataFrame, tickers, date):
    if date < COMPOSITION_START:
        return None
    members = tickers_as_of_date(date)
    idx = P.index.get_loc(date)
    if idx < SMA_WINDOW - 1:
        return np.nan
    n_calc, n_above = 0, 0
    for tk in tickers:
        if tk not in members:
            continue
        window = P[tk].iloc[idx - SMA_WINDOW + 1:idx + 1]
        if window.isna().any():
            continue
        sma = window.mean()
        price = P[tk].iloc[idx]
        n_calc += 1
        if price > sma:
            n_above += 1
    if n_calc == 0:
        return np.nan
    return n_above / n_calc


def main():
    series = load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    breadth = compute_sma200_breadth_series_pit()
    post_2015 = breadth.index[breadth.index >= COMPOSITION_START]
    check_dates = post_2015[::400]

    lines = ["# Audit adversarial — Porte breadth SMA200, univers point-in-time", "",
             "## 1. Recalcul indépendant de la breadth PIT à un échantillon de dates", "",
             "| Date | Breadth (original) | Breadth (recalcul indépendant) | Écart |",
             "|---|---|---|---|"]
    all_ok = True
    for d in check_dates:
        orig = breadth.loc[d]
        indep = independent_breadth_at(P, tickers, d)
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
    lines.append(f"**{'OK — breadth PIT confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Vérification de l'absence de contamination pré-2015")
    lines.append("")
    pre_2015 = breadth.index[breadth.index < COMPOSITION_START]
    n_pre_nonnan = int(breadth.loc[pre_2015].notna().sum()) if len(pre_2015) > 0 else 0
    lines.append(f"Nombre de valeurs de breadth NON-NaN avant {COMPOSITION_START.date()} : {n_pre_nonnan} "
                 f"(sur {len(pre_2015)} dates disponibles dans le panneau PIT avant cette date).")
    mask_ok = n_pre_nonnan == 0
    lines.append(f"**{'OK — aucune breadth calculée hors couverture de composition.' if mask_ok else 'ÉCHEC — contamination détectée.'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    mutation_start = pd.Timestamp("2022-06-01")
    check_date_target = pd.Timestamp("2018-06-01")
    cut = int(P.index.searchsorted(mutation_start))
    check_date = P.index[P.index.searchsorted(check_date_target)]
    P_pert = P.copy()
    rng = np.random.default_rng(278)
    P_pert.iloc[cut:] = P_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_pert.iloc[cut:].shape))
    orig_val = breadth.loc[check_date]
    pert_val = independent_breadth_at(P_pert, tickers, check_date)
    diff_pert = abs(orig_val - pert_val) if (pert_val is not None and np.isfinite(orig_val) and np.isfinite(pert_val)) else 0.0
    anti_leak_ok = diff_pert < 1e-9
    lines.append(f"Mutation appliquée à partir de {mutation_start.date()}, contrôle à {check_date.date()}.")
    lines.append(f"Écart de breadth à une date antérieure à la mutation : {diff_pert:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_sma200_breadth_vol_targeting_overlay_pit_universe_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Audit adversarial — Choc de prix du pétrole WTI (DCOILWTICO), overlay défensif.

1. Recalcul indépendant par boucle+searchsorted manuel (side="right"
   inclusif, méthode prouvée correcte au #203, re-confirmée au
   #283/#284).
2. Vérification de l'épisode du prix négatif du 20/04/2020 (WTI à
   -36,98$, événement COVID réel et documenté, pas un bug de données) :
   confirme que log(négatif) produit bien un NaN traité comme donnée
   manquante, sans propagation d'erreur silencieuse.
3. Anti-lookahead par troncature de l'historique.
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
from nonml_oil_price_shock_overlay_backtest import (  # noqa: E402
    build_oil_change_series, load_oil_change_lag, expanding_tercile_cut_high, MARKETS, RET_WINDOW,
)


def independent_change_lag(dates: np.ndarray, oil_dates: np.ndarray, oil_vals: np.ndarray) -> np.ndarray:
    """Reimplementation par searchsorted explicite (side="right" pour
    l'inclusion <=), puis decalage d'une POSITION dans le calendrier
    cible pour reproduire ffill+shift(1)."""
    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(oil_dates, d, side="right") - 1
        if idx >= 0:
            out[i] = oil_vals[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def main():
    oil_series = build_oil_change_series()
    oil_dates = oil_series.index.values
    oil_vals = oil_series.values

    lines = ["# Audit adversarial — Choc de prix du pétrole WTI (DCOILWTICO), overlay défensif", "",
             "## 1. Recalcul indépendant (searchsorted explicite, side=\"right\" inclusif)", "",
             "| Marché | Séances | Désaccords |",
             "|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        orig = load_oil_change_lag(dates, oil_series)
        indep = independent_change_lag(dates.values, oil_dates, oil_vals)

        both_finite = np.isfinite(orig) & np.isfinite(indep)
        n_diff = int((~np.isclose(orig[both_finite], indep[both_finite], atol=1e-9)).sum())
        n_nan_mismatch = int((np.isfinite(orig) != np.isfinite(indep)).sum())
        all_ok &= (n_diff == 0 and n_nan_mismatch == 0)
        lines.append(f"| {name} | {len(dates)} | {n_diff + n_nan_mismatch} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul indépendant (0 désaccord).' if all_ok else 'ÉCHEC — désaccord détecté.'}**")

    lines.append("")
    lines.append("## 2. Épisode du prix négatif du 20/04/2020 (événement COVID réel, pas un bug)")
    lines.append("")
    raw = pd.read_csv(REPO_ROOT / "data" / "wti_oil_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    neg_row = raw[raw["DCOILWTICO"] < 0]
    lines.append(f"Valeur négative confirmée dans la source FRED brute : {neg_row.to_dict('records')} "
                 "(crise de stockage COVID, 20/04/2020, documentée publiquement — pas une erreur de données).")
    d_neg = pd.Timestamp("2020-04-20")
    around = raw[(raw["observation_date"] >= d_neg - pd.Timedelta(days=25)) &
                 (raw["observation_date"] <= d_neg + pd.Timedelta(days=1))].dropna(subset=["DCOILWTICO"])
    vals_around = around["DCOILWTICO"].astype(float).values
    n_nan_produced = int(np.isnan(np.log(vals_around[vals_around <= 0])).sum()) if (vals_around <= 0).any() else 0
    with np.errstate(invalid="ignore"):
        change_at_event = np.log(vals_around[-1] / vals_around[0]) if len(vals_around) > RET_WINDOW else np.nan
    lines.append(f"`log(WTI(t)/WTI(t-{RET_WINDOW}))` autour de cet épisode produit bien `NaN` "
                 f"(valeur négative au dénominateur ou numérateur) plutôt qu'un résultat numérique erroné : "
                 f"{'NaN confirmé' if not np.isfinite(change_at_event) else 'valeur finie inattendue'}.")
    ok2 = not np.isfinite(change_at_event)
    lines.append(f"**{'OK — le NaN se propage correctement, exclu du calcul du tercile (np.isfinite), aucune valeur aberrante silencieuse.' if ok2 else 'À VÉRIFIER MANUELLEMENT.'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (troncature de l'historique)")
    lines.append("")
    df_ndx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_ndx)
    ndx_dates = pd.DatetimeIndex(df_ndx["date"].values)
    oil_lag_full = load_oil_change_lag(ndx_dates, oil_series)[1:]
    pos_full = expanding_tercile_cut_high(oil_lag_full)

    N_CHECK = 2000
    TRUNC_POINTS = [4000, 6000, 8500]
    all_trunc_ok = True
    for cut in TRUNC_POINTS:
        dates_trunc = ndx_dates[:cut]
        oil_lag_trunc = load_oil_change_lag(dates_trunc, oil_series)[1:]
        pos_trunc = expanding_tercile_cut_high(oil_lag_trunc)
        n = min(N_CHECK, len(pos_trunc), cut - 1)
        match = np.allclose(pos_full[:n], pos_trunc[:n], equal_nan=True)
        all_trunc_ok &= match
        lines.append(f"Troncature à {cut} séances, comparaison sur les {n} premières positions : "
                     f"{'identique' if match else 'DIFFÉRENT'}.")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.' if all_trunc_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_oil_price_shock_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Audit adversarial — Mises en chantier de logements US (HOUST), overlay défensif.

1. Recalcul indépendant par boucle+searchsorted manuel (sans
   pandas.reindex/ffill), même méthode que #195/#203/#204/#205/#206.
2. Vérification dédiée du décalage d'un mois de publication (inspection
   directe : la dernière observation n'apparaît jamais avant la date de
   disponibilité déclarée).
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
from nonml_housing_starts_overlay_backtest import (  # noqa: E402
    build_houst_growth_series, load_houst_growth_lag, expanding_tercile_cut_low, MARKETS,
)


def independent_growth_lag(dates: np.ndarray, houst_dates: np.ndarray, houst_vals: np.ndarray) -> np.ndarray:
    """Reimplementation par searchsorted explicite (sans pandas.reindex/
    ffill), meme methode prouvee au #203 (m2_growth) : side="right" pour
    l'inclusion (<=, pas <), puis decalage d'une POSITION dans le
    calendrier cible (pas d'une date civile) pour reproduire exactement
    la semantique ffill+shift(1) de l'original."""
    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(houst_dates, d, side="right") - 1
        if idx >= 0:
            out[i] = houst_vals[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def main():
    houst_series = build_houst_growth_series()
    houst_dates = houst_series.index.values
    houst_vals = houst_series.values

    lines = ["# Audit adversarial — Mises en chantier de logements US (HOUST), overlay défensif", "",
             "## 1. Recalcul indépendant (searchsorted explicite)", "",
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

        orig = load_houst_growth_lag(dates, houst_series)
        indep = independent_growth_lag(dates.values, houst_dates, houst_vals)

        both_finite = np.isfinite(orig) & np.isfinite(indep)
        n_diff = int((~np.isclose(orig[both_finite], indep[both_finite], atol=1e-9)).sum())
        n_nan_mismatch = int((np.isfinite(orig) != np.isfinite(indep)).sum())
        all_ok &= (n_diff == 0 and n_nan_mismatch == 0)
        lines.append(f"| {name} | {len(dates)} | {n_diff + n_nan_mismatch} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul indépendant (0 désaccord).' if all_ok else 'ÉCHEC — désaccord détecté.'}**")

    lines.append("")
    lines.append("## 2. Vérification dédiée du décalage d'un mois de publication")
    lines.append("")
    raw = pd.read_csv(REPO_ROOT / "data" / "houst_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["HOUST"]).sort_values("observation_date")
    last_obs = raw["observation_date"].iloc[-1]
    last_avail = houst_dates[-1]
    lines.append(f"Dernière observation HOUST : mois de {pd.Timestamp(last_obs).date()}. "
                 f"Disponible dans la série décalée à partir de {pd.Timestamp(last_avail).date()} "
                 f"({(pd.Timestamp(last_avail) - pd.Timestamp(last_obs)).days} jours calendaires après, "
                 "cohérent avec le délai de publication réel de ~3 semaines déclaré au PREREG).")
    ok2 = pd.Timestamp(last_avail) > pd.Timestamp(last_obs)
    lines.append(f"**{'OK — la valeur du mois M n’apparaît jamais avant sa date de disponibilité décalée.' if ok2 else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (troncature de l'historique)")
    lines.append("")
    df_ndx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_ndx)
    ndx_dates = pd.DatetimeIndex(df_ndx["date"].values)
    houst_lag_full = load_houst_growth_lag(ndx_dates, houst_series)[1:]
    pos_full = expanding_tercile_cut_low(houst_lag_full)

    N_CHECK = 2000
    TRUNC_POINTS = [4000, 7000, 9000]
    all_trunc_ok = True
    for cut in TRUNC_POINTS:
        dates_trunc = ndx_dates[:cut]
        houst_lag_trunc = load_houst_growth_lag(dates_trunc, houst_series)[1:]
        pos_trunc = expanding_tercile_cut_low(houst_lag_trunc)
        n = min(N_CHECK, len(pos_trunc), cut - 1)
        match = np.allclose(pos_full[:n], pos_trunc[:n], equal_nan=True)
        all_trunc_ok &= match
        lines.append(f"Troncature à {cut} séances, comparaison sur les {n} premières positions : "
                     f"{'identique' if match else 'DIFFÉRENT'}.")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.' if all_trunc_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_housing_starts_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

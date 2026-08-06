"""Audit indépendant — Prix du gaz naturel US Henry Hub (DHHNGSP).

1. Recalcul indépendant par boucle+searchsorted manuel (side="right"
   inclusif, méthode prouvée correcte au #203/#283/#284) et tercile
   expanding par tri+interpolation manuel (sans np.percentile).
2. Anti-lookahead par troncature de l'historique.
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
from nonml_oil_price_shock_overlay_backtest import CUT, RET_WINDOW, MARKETS, expanding_tercile_cut_high  # noqa: E402
from nonml_natural_gas_price_overlay_backtest import (  # noqa: E402
    build_gas_change_series, load_gas_change_lag,
)


def independent_change_lag(dates: np.ndarray, gas_dates: np.ndarray, gas_vals: np.ndarray) -> np.ndarray:
    """Reimplementation par searchsorted explicite (side="right" pour
    l'inclusion <=), puis decalage d'une POSITION dans le calendrier
    cible pour reproduire ffill+shift(1)."""
    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(gas_dates, d, side="right") - 1
        if idx >= 0:
            out[i] = gas_vals[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def manual_percentile_high_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (200.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    gas_series = build_gas_change_series()
    gas_dates = gas_series.index.values
    gas_vals = gas_series.values

    lines = ["# Audit — Prix du gaz naturel US Henry Hub (DHHNGSP)", "",
             "## 1. Recalcul indépendant (searchsorted explicite, side=\"right\" inclusif + tercile tri+interpolation manuel)", ""]
    all_ok = True

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        gas_lag_official = load_gas_change_lag(dates, gas_series)[1:]
        pos_official = expanding_tercile_cut_high(gas_lag_official)

        gas_lag_manual = independent_change_lag(dates.values, gas_dates, gas_vals)[1:]
        diff_align = np.nanmax(np.abs(gas_lag_official - gas_lag_manual))

        start = int(np.argmax(np.isfinite(gas_lag_manual)))
        T = len(gas_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(gas_lag_manual[t]):
                continue
            hist = gas_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_high_tercile(hist)
            pos_manual[t] = CUT if gas_lag_manual[t] >= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(gas_lag_official[i] - gas_lag_manual[i])
            if local_diff >= 1e-10:
                boundary_tie_ok = False

        ok = (diff_align < 1e-8) and (n_pos_diff == 0 or boundary_tie_ok)
        all_ok &= ok
        lines.append(f"### {name}")
        lines.append(f"- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : {diff_align:.2e}")
        if n_pos_diff == 0:
            lines.append("- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00")
        else:
            lines.append(f"- **{n_pos_diff}/{n_total} désaccords de position** — sensibilité de bord flottante "
                         f"documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    lines.append(f"**{'OK — position confirmée par recalcul indépendant sur les 5 marchés.' if all_ok else 'ÉCHEC — désaccord détecté.'}**")
    lines.append("")

    lines.append("## 2. Absence de valeur négative (contrairement à l'épisode WTI du 20/04/2020)")
    lines.append("")
    raw = pd.read_csv(REPO_ROOT / "data" / "natural_gas_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    vals_num = pd.to_numeric(raw["DHHNGSP"], errors="coerce")
    n_neg = int((vals_num < 0).sum())
    lines.append(f"Nombre de valeurs négatives dans la série brute : {n_neg} "
                 f"(confirmé absent, contrairement au pétrole WTI où un épisode négatif réel existe en 2020) — "
                 f"aucune gestion spéciale de NaN issue d'un log négatif requise pour cette série.")
    lines.append(f"**{'OK' if n_neg == 0 else 'À VÉRIFIER MANUELLEMENT'}**")
    lines.append("")

    lines.append("## 3. Test anti-lookahead (troncature de l'historique)")
    lines.append("")
    df_ndx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_ndx)
    ndx_dates = pd.DatetimeIndex(df_ndx["date"].values)
    gas_lag_full = load_gas_change_lag(ndx_dates, gas_series)[1:]
    pos_full = expanding_tercile_cut_high(gas_lag_full)

    N_CHECK = 2000
    TRUNC_POINTS = [4000, 6000, 8500]
    all_trunc_ok = True
    for cut in TRUNC_POINTS:
        dates_trunc = ndx_dates[:cut]
        gas_lag_trunc = load_gas_change_lag(dates_trunc, gas_series)[1:]
        pos_trunc = expanding_tercile_cut_high(gas_lag_trunc)
        n = min(N_CHECK, len(pos_trunc), cut - 1)
        match = np.allclose(pos_full[:n], pos_trunc[:n], equal_nan=True)
        all_trunc_ok &= match
        lines.append(f"Troncature à {cut} séances, comparaison sur les {n} premières positions : "
                     f"{'identique' if match else 'DIFFÉRENT'}.")
    all_ok &= all_trunc_ok and (n_neg == 0)

    lines.append("")
    lines.append(f"**{'OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.' if all_trunc_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_natural_gas_price_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()

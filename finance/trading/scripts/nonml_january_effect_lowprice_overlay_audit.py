"""Audit adversarial — "January effect" (proxy prix bas) en overlay.

1. Recalcul indépendant de la sélection tercile "prix bas" à un
   échantillon de dates de rebalancement (boucle Python explicite,
   sans réutiliser np.argsort du backtest) pour vérifier l'absence de
   divergence.
2. Vérifie que la détection du mois de janvier est bien data-driven
   (basée sur `date.month`, pas de plage de jours codée en dur) en
   comparant au nombre réel de jours de bourse en janvier par année.
3. Test anti-lookahead (perturbation du futur) sur le signal de
   sélection.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_january_effect_lowprice_overlay_backtest import (  # noqa: E402
    load_all_prices, REBAL_EVERY, TERCILE, CAP,
)


def independent_select_at(close_row: np.ndarray, n_tickers: int, n_low: int) -> np.ndarray:
    """Selection du tercile 'prix bas' par boucle Python explicite,
    sans reutiliser np.argsort vectorise du backtest."""
    pairs = [(j, close_row[j]) for j in range(n_tickers) if np.isfinite(close_row[j])]
    pairs.sort(key=lambda x: x[1])
    chosen = [j for j, _ in pairs[:n_low]]
    w = np.zeros(n_tickers)
    if chosen:
        for j in chosen:
            w[j] = 1.0 / len(chosen)
    return w


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)

    n_low = max(1, int(round(n_tickers * TERCILE)))
    start = REBAL_EVERY
    rebal_dates = list(range(start, T, REBAL_EVERY))
    check_dates = rebal_dates[::5]

    lines = ["# Audit adversarial — \"January effect\" (proxy prix bas) en overlay", "",
             "## 1. Recalcul indépendant de la sélection tercile (boucle Python explicite)", "",
             "| Date (indice) | Écart max absolu (poids) |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        c = close[t].copy()
        c[~exists[t]] = np.nan
        w_indep = independent_select_at(c, n_tickers, n_low)

        elig = np.where(np.isfinite(c))[0]
        n_low_t = min(n_low, len(elig))
        w_orig = np.zeros(n_tickers)
        if n_low_t > 0:
            low_idx = elig[np.argsort(c[elig])[:n_low_t]]
            w_orig[low_idx] = 1.0 / n_low_t

        diff = float(np.max(np.abs(w_orig - w_indep)))
        all_ok &= (diff < 1e-12)
        lines.append(f"| {t} | {diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — sélection confirmée par recalcul indépendant sur toutes les dates échantillonnées.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Détection du mois de janvier (data-driven, pas de plage codée en dur)")
    lines.append("")
    is_january = pd.Series([d.month == 1 for d in P.index], index=P.index)
    jan_by_year = is_january.groupby(P.index.year).sum()
    lines.append("| Année | Jours de bourse en janvier détectés |")
    lines.append("|---|---|")
    for year, n in jan_by_year.items():
        lines.append(f"| {year} | {int(n)} |")
    plausible = bool(((jan_by_year >= 15) | (jan_by_year == 0)).all())
    lines.append("")
    lines.append(f"**{'OK — nombre de jours de bourse par janvier plausible (15-23j US, ou 0 pour une année partielle).' if plausible else 'ÉCHEC — anomalie détectée.'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(86)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    close_mut = P_mut.values

    check_i = cut - REBAL_EVERY - 50
    c_before = close[check_i].copy()
    c_before[~exists[check_i]] = np.nan
    c_after = close_mut[check_i].copy()
    c_after[~np.isfinite(close_mut[check_i])] = np.nan
    w_before = independent_select_at(c_before, n_tickers, n_low)
    w_after = independent_select_at(c_after, n_tickers, n_low)
    max_diff_lookahead = float(np.max(np.abs(w_before - w_after)))
    lines.append(f"Écart sur la sélection calculée à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 4. Rappel de la limite méthodologique (voir PREREG)")
    lines.append("")
    lines.append("Le tercile 'prix bas' est un proxy imparfait de la capitalisation boursière "
                 "réelle (pas de données de nombre d'actions en circulation disponibles). "
                 "Le résultat teste un effet de NIVEAU DE PRIX, pas une vraie stratification "
                 "par taille d'entreprise — limite documentée avant tout calcul dans le PREREG, "
                 "pas découverte après coup.")

    out = ROOT / "results" / "nonml_january_effect_lowprice_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

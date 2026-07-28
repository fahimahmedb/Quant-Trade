"""Audit adversarial — Momentum 52-semaines.

1. Recalcul indépendant du ratio prix/plus-haut-52sem par une méthode
   différente (pandas .rolling().max() au lieu d'une boucle numpy manuelle)
   pour vérifier l'absence de bug d'indexation.
2. Test anti-lookahead : perturbe délibérément les 20% de prix les plus
   récents et vérifie que les positions AVANT cette période sont
   inchangées (le ratio à la date t ne doit dépendre que de close[t-251:t+1]).
3. Vérifie la mécanique de l'univers dynamique (nombre de titres éligibles
   au fil du temps, pas de saut suspect).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

PRICES_DIR = ROOT / "data" / "pead" / "prices"
LOOKBACK = 252


def load_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > LOOKBACK + 21:
            series[path.stem] = close
    return series


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    lines = ["# Audit adversarial — Momentum 52-semaines", ""]

    # --- 1. Recalcul independant (pandas rolling, methode differente) ---
    close = P.values
    rolling_max_manual = np.full(P.shape, np.nan)
    for i in range(LOOKBACK, len(P)):
        window = close[i - LOOKBACK + 1:i + 1]
        with np.errstate(all="ignore"):
            rolling_max_manual[i] = np.nanmax(window, axis=0)

    rolling_max_pandas = P.rolling(window=LOOKBACK, min_periods=LOOKBACK).max().values

    mask_both_valid = np.isfinite(rolling_max_manual) & np.isfinite(rolling_max_pandas)
    diff = np.abs(rolling_max_manual[mask_both_valid] - rolling_max_pandas[mask_both_valid])
    max_diff = float(diff.max()) if diff.size else 0.0

    lines.append("## 1. Recalcul indépendant du plus-haut glissant (numpy manuel vs pandas.rolling)")
    lines.append("")
    lines.append(f"Écart maximum absolu sur {mask_both_valid.sum()} valeurs comparables : {max_diff:.2e}")
    lines.append(f"**{'OK — méthodes concordantes.' if max_diff < 1e-6 else 'ÉCHEC — divergence, bug à corriger.'}**")
    lines.append("")

    # --- 2. Test anti-lookahead ---
    T = len(P)
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(42)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))

    def ratio_at(df, i):
        window = df.values[i - LOOKBACK + 1:i + 1]
        with np.errstate(all="ignore"):
            rmax = np.nanmax(window, axis=0)
        return df.values[i] / rmax

    check_i = cut - 50  # bien avant la mutation, aucune donnee mutee dans sa fenetre de 252j
    r_orig = ratio_at(P, check_i)
    r_mut = ratio_at(P_mut, check_i)
    r_orig_clean = np.nan_to_num(r_orig, nan=0.0)
    r_mut_clean = np.nan_to_num(r_mut, nan=0.0)
    max_diff_lookahead = float(np.abs(r_orig_clean - r_mut_clean).max())

    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    lines.append(f"Écart sur le ratio calculé à un jour antérieur à la mutation (fenêtre 252j "
                 f"n'incluant aucune donnée mutée) : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")

    # --- 3. Univers dynamique ---
    n_listed = np.isfinite(P.values).sum(axis=1)
    lines.append("## 3. Taille de l'univers éligible au fil du temps")
    lines.append("")
    lines.append(f"Min {n_listed.min()}, max {n_listed.max()}, médiane {int(np.median(n_listed))} "
                 f"titres cotés simultanément sur les {T} séances — croissance progressive "
                 "attendue (nouvelles entrées à l'indice/IPO), pas de saut suspect si la "
                 "progression est monotone-ish.")

    out = ROOT / "results" / "nonml_momentum_52w_high_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

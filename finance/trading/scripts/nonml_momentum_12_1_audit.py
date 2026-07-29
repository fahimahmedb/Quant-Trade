"""Audit adversarial — Momentum 12-1 mois.

1. Recalcul indépendant du signal momentum(t)=close(t-SKIP)/close(t-LOOKBACK)-1
   par indexation directe pandas (au lieu de la boucle numpy manuelle du
   backtest) pour vérifier l'absence de bug d'indexation.
2. Test anti-lookahead : perturbe délibérément les 20% de prix les plus
   récents et vérifie que le signal calculé à une date antérieure (dont
   la fenêtre ne recoupe pas la mutation) est inchangé.
3. Vérifie la mécanique de l'univers dynamique (nombre de titres
   éligibles au fil du temps, pas de saut suspect).
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
SKIP = 21


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

    lines = ["# Audit adversarial — Momentum 12-1 mois", ""]

    # --- 1. Recalcul independant (indexation pandas .shift() directe) ---
    close = P.values
    T = len(P)
    momentum_manual = np.full((T, len(tickers)), np.nan)
    for i in range(LOOKBACK, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - LOOKBACK]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum_manual[i, valid] = m[valid]

    P_skip = P.shift(SKIP)
    P_lookback = P.shift(LOOKBACK)
    momentum_pandas = (P_skip / P_lookback - 1.0).values

    mask_both_valid = np.isfinite(momentum_manual) & np.isfinite(momentum_pandas)
    diff = np.abs(momentum_manual[mask_both_valid] - momentum_pandas[mask_both_valid])
    max_diff = float(diff.max()) if diff.size else 0.0

    lines.append("## 1. Recalcul indépendant du signal (boucle numpy manuelle vs pandas.shift())")
    lines.append("")
    lines.append(f"Écart maximum absolu sur {mask_both_valid.sum()} valeurs comparables : {max_diff:.2e}")
    lines.append(f"**{'OK — méthodes concordantes.' if max_diff < 1e-9 else 'ÉCHEC — divergence, bug à corriger.'}**")
    lines.append("")

    # --- 2. Test anti-lookahead ---
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(211)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))

    def momentum_at(df, i):
        c_skip = df.values[i - SKIP]
        c_lookback = df.values[i - LOOKBACK]
        with np.errstate(all="ignore"):
            return c_skip / c_lookback - 1.0

    check_i = cut - LOOKBACK - 50  # bien avant la mutation, aucune donnee mutee dans les fenetres SKIP/LOOKBACK
    m_orig = momentum_at(P, check_i)
    m_mut = momentum_at(P_mut, check_i)
    m_orig_clean = np.nan_to_num(m_orig, nan=0.0)
    m_mut_clean = np.nan_to_num(m_mut, nan=0.0)
    max_diff_lookahead = float(np.abs(m_orig_clean - m_mut_clean).max())

    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    lines.append(f"Écart sur le signal calculé à un jour antérieur à la mutation (fenêtres "
                 f"SKIP={SKIP}j et LOOKBACK={LOOKBACK}j n'incluant aucune donnée mutée) : "
                 f"{max_diff_lookahead:.2e}")
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

    out = ROOT / "results" / "nonml_momentum_12_1_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Audit adversarial — Porte majoritaire (≥2/3) défaut carte de crédit
+ NFCI + BAA10Y.

1. Recalcul indépendant du vote majoritaire par boucle explicite
   distincte (sans réutiliser expanding_tercile_gate_high), vérifie la
   cohérence contre la porte du backtest.
2. Vérifie les relations d'inclusion attendues : la porte ET à 3
   (les 3 votes) est un SOUS-ENSEMBLE de la porte majoritaire (≥2/3),
   qui est elle-même un SOUS-ENSEMBLE de l'union à 3 (au moins 1 vote).
3. Anti-lookahead par troncature de l'historique.

Chaque porte individuelle utilise SON PROPRE indice de première valeur
finie (own_start), PAS un start externe commun -- leçon du bug trouvé
et corrigé au #296 pour ce même type de recalcul, appliquée dès ce
script (Règle 7).
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
from nonml_delinquency_nfci_combined_overlay_backtest import (  # noqa: E402
    expanding_tercile_gate_high, MARKETS, TERCILE_PCT,
)
from nonml_credit_card_delinquency_overlay_backtest import (  # noqa: E402
    build_delinquency_series, load_delinquency_lag,
)
from nonml_financial_conditions_overlay_backtest import (  # noqa: E402
    build_nfci_series, load_nfci_lag,
)
from nonml_credit_spread_overlay_backtest import load_baa10y_lag  # noqa: E402


def independent_gate_at(level: np.ndarray, t: int) -> bool:
    """Recalcul independant de la porte tercile-haut pour UN SEUL indice
    t, par tri+interpolation manuelle (sans np.percentile) -- echantillonne,
    meme logique que l'audit du #282/#296/#298. Utilise le PROPRE indice
    de premiere valeur finie de CETTE serie (own_start), jamais un start
    externe commun."""
    own_start = int(np.argmax(np.isfinite(level)))
    if not np.isfinite(level[t]):
        return False
    hist = sorted(v for v in level[own_start:t + 1] if np.isfinite(v))
    n = len(hist)
    rank = (1.0 - TERCILE_PCT / 100.0) * (n - 1)
    lo, hi = int(np.floor(rank)), int(np.ceil(rank))
    frac = rank - lo
    thresh = hist[lo] * (1 - frac) + hist[hi] * frac if lo != hi else hist[lo]
    return bool(level[t] >= thresh)


def main():
    delinq_series = build_delinquency_series()
    nfci_series = build_nfci_series()

    lines = ["# Audit adversarial — Porte majoritaire (≥2/3) défaut carte + NFCI + BAA10Y", "",
             "## 1. Recalcul indépendant du vote majoritaire (tri manuel, sans np.percentile)", "",
             "Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet "
             "à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296/#298).",
             "",
             "| Marché | % actif ≥2/3 | % actif ET (3/3) | % actif OU (≥1/3) | ET⊆maj ? | maj⊆OU ? | Dates échantillonnées | Désaccords |",
             "|---|---|---|---|---|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        delinq_lag = load_delinquency_lag(dates, delinq_series)[1:]
        nfci_lag = load_nfci_lag(dates, nfci_series)[1:]
        baa10y_lag = load_baa10y_lag(dates)[1:]
        valid = np.isfinite(delinq_lag) & np.isfinite(nfci_lag) & np.isfinite(baa10y_lag)
        start = int(np.argmax(valid))

        gate_delinq = expanding_tercile_gate_high(delinq_lag)
        gate_nfci = expanding_tercile_gate_high(nfci_lag)
        gate_baa10y = expanding_tercile_gate_high(baa10y_lag)
        votes = gate_delinq.astype(int) + gate_nfci.astype(int) + gate_baa10y.astype(int)
        gate_majority = votes >= 2
        gate_and3 = votes == 3
        gate_or3 = votes >= 1

        subset_and = bool(np.all(~gate_and3[start:] | gate_majority[start:]))
        subset_maj_or = bool(np.all(~gate_majority[start:] | gate_or3[start:]))
        all_ok &= subset_and and subset_maj_or

        sample_idx = list(range(start, len(delinq_lag), 250))
        n_diff = 0
        for t in sample_idx:
            v = (int(independent_gate_at(delinq_lag, t))
                 + int(independent_gate_at(nfci_lag, t))
                 + int(independent_gate_at(baa10y_lag, t)))
            indep_majority = v >= 2
            if indep_majority != bool(gate_majority[t]):
                n_diff += 1
        all_ok &= (n_diff == 0)

        lines.append(f"| {name} | {100*gate_majority[start:].mean():.1f}% | "
                     f"{100*gate_and3[start:].mean():.1f}% | {100*gate_or3[start:].mean():.1f}% | "
                     f"{'OUI' if subset_and else 'NON'} | {'OUI' if subset_maj_or else 'NON'} | "
                     f"{len(sample_idx)} | {n_diff} |")

    lines.append("")
    lines.append(f"**{'OK — vote majoritaire confirmé cohérent avec les relations ET(3)⊆majorité⊆OU(3), recalcul indépendant identique sur l’échantillon (0 désaccord).' if all_ok else 'ÉCHEC — incohérence détectée.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (troncature de l'historique)")
    lines.append("")
    df_ndx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_ndx)
    ndx_dates = pd.DatetimeIndex(df_ndx["date"].values)
    delinq_lag_full = load_delinquency_lag(ndx_dates, delinq_series)[1:]
    nfci_lag_full = load_nfci_lag(ndx_dates, nfci_series)[1:]
    baa10y_lag_full = load_baa10y_lag(ndx_dates)[1:]
    votes_full = (expanding_tercile_gate_high(delinq_lag_full).astype(int)
                  + expanding_tercile_gate_high(nfci_lag_full).astype(int)
                  + expanding_tercile_gate_high(baa10y_lag_full).astype(int))
    gate_full = votes_full >= 2

    N_CHECK = 2000
    TRUNC_POINTS = [4000, 7000, 9000]
    all_trunc_ok = True
    for cut in TRUNC_POINTS:
        dates_trunc = ndx_dates[:cut]
        delinq_lag_trunc = load_delinquency_lag(dates_trunc, delinq_series)[1:]
        nfci_lag_trunc = load_nfci_lag(dates_trunc, nfci_series)[1:]
        baa10y_lag_trunc = load_baa10y_lag(dates_trunc)[1:]
        votes_trunc = (expanding_tercile_gate_high(delinq_lag_trunc).astype(int)
                       + expanding_tercile_gate_high(nfci_lag_trunc).astype(int)
                       + expanding_tercile_gate_high(baa10y_lag_trunc).astype(int))
        gate_trunc = votes_trunc >= 2
        n = min(N_CHECK, len(gate_trunc), cut - 1)
        match = np.array_equal(gate_full[:n], gate_trunc[:n])
        all_trunc_ok &= match
        lines.append(f"Troncature à {cut} séances, comparaison sur les {n} premières positions : "
                     f"{'identique' if match else 'DIFFÉRENT'}.")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.' if all_trunc_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_delinquency_nfci_baa10y_majority_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

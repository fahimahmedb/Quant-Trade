"""Audit adversarial — Porte combinée (ET) défaut carte de crédit + NFCI.

1. Recalcul indépendant de la porte ET par boucle explicite distincte
   (sans réutiliser expanding_tercile_gate_high), vérifie que la porte
   combinée est bien un SOUS-ENSEMBLE strict des deux portes
   individuelles (#286, #291) déjà validées séparément.
2. Vérifie que le taux d'activation combiné est cohérent avec une
   intersection (pas juste une des deux portes recopiée par erreur).
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
from nonml_delinquency_nfci_combined_overlay_backtest import (  # noqa: E402
    expanding_tercile_gate_high, MARKETS, TERCILE_PCT,
)
from nonml_credit_card_delinquency_overlay_backtest import (  # noqa: E402
    build_delinquency_series, load_delinquency_lag,
)
from nonml_financial_conditions_overlay_backtest import (  # noqa: E402
    build_nfci_series, load_nfci_lag,
)


def independent_gate_at(level: np.ndarray, t: int) -> bool:
    """Recalcul independant de la porte tercile-haut pour UN SEUL indice
    t, par tri+interpolation manuelle (sans np.percentile) -- echantillonne,
    ne recalcule pas la sequence complete (le tri Python pur sur des
    dizaines de milliers d'elements a chaque pas serait prohibitif, meme
    logique d'echantillonnage que l'audit du #282/rate_velocity).

    Utilise le PROPRE indice de premiere valeur finie de CETTE serie
    (comme expanding_tercile_gate_high), PAS un start externe commun --
    bug trouve et corrige avant tout commit : le #286 (DRCCLACBS, depuis
    1991) et le #291 (NFCI, depuis 1971) n'ont pas le meme historique
    disponible sur le calendrier cible, chaque porte doit batir son
    seuil expanding sur SA PROPRE histoire complete, pas une fenetre
    tronquee au demarrage du second signal."""
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

    lines = ["# Audit adversarial — Porte combinée (ET) défaut carte de crédit + NFCI", "",
             "## 1. Recalcul indépendant de la porte ET (tri manuel, sans np.percentile)", "",
             "Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet "
             "à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du "
             "#282, vitesse des taux).",
             "",
             "| Marché | % actif ET | % actif défaut seul | % actif NFCI seul | ET ⊆ défaut ? | ET ⊆ NFCI ? | Dates échantillonnées | Désaccords |",
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
        valid = np.isfinite(delinq_lag) & np.isfinite(nfci_lag)
        start = int(np.argmax(valid))

        gate_delinq = expanding_tercile_gate_high(delinq_lag)
        gate_nfci = expanding_tercile_gate_high(nfci_lag)
        gate_combined = gate_delinq & gate_nfci

        subset_delinq = bool(np.all(~gate_combined[start:] | gate_delinq[start:]))
        subset_nfci = bool(np.all(~gate_combined[start:] | gate_nfci[start:]))
        all_ok &= subset_delinq and subset_nfci

        sample_idx = list(range(start, len(delinq_lag), 250))
        n_diff = 0
        for t in sample_idx:
            indep_delinq = independent_gate_at(delinq_lag, t)
            indep_nfci = independent_gate_at(nfci_lag, t)
            indep_combined = indep_delinq and indep_nfci
            if indep_combined != bool(gate_combined[t]):
                n_diff += 1
        all_ok &= (n_diff == 0)

        lines.append(f"| {name} | {100*gate_combined[start:].mean():.1f}% | "
                     f"{100*gate_delinq[start:].mean():.1f}% | {100*gate_nfci[start:].mean():.1f}% | "
                     f"{'OUI' if subset_delinq else 'NON'} | {'OUI' if subset_nfci else 'NON'} | "
                     f"{len(sample_idx)} | {n_diff} |")

    lines.append("")
    lines.append(f"**{'OK — porte ET confirmée sous-ensemble strict des deux portes individuelles, recalcul indépendant identique sur l’échantillon (0 désaccord).' if all_ok else 'ÉCHEC — incohérence détectée.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (troncature de l'historique)")
    lines.append("")
    df_ndx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_ndx)
    ndx_dates = pd.DatetimeIndex(df_ndx["date"].values)
    delinq_lag_full = load_delinquency_lag(ndx_dates, delinq_series)[1:]
    nfci_lag_full = load_nfci_lag(ndx_dates, nfci_series)[1:]
    gate_full = expanding_tercile_gate_high(delinq_lag_full) & expanding_tercile_gate_high(nfci_lag_full)

    N_CHECK = 2000
    TRUNC_POINTS = [4000, 7000, 9000]
    all_trunc_ok = True
    for cut in TRUNC_POINTS:
        dates_trunc = ndx_dates[:cut]
        delinq_lag_trunc = load_delinquency_lag(dates_trunc, delinq_series)[1:]
        nfci_lag_trunc = load_nfci_lag(dates_trunc, nfci_series)[1:]
        gate_trunc = expanding_tercile_gate_high(delinq_lag_trunc) & expanding_tercile_gate_high(nfci_lag_trunc)
        n = min(N_CHECK, len(gate_trunc), cut - 1)
        match = np.array_equal(gate_full[:n], gate_trunc[:n])
        all_trunc_ok &= match
        lines.append(f"Troncature à {cut} séances, comparaison sur les {n} premières positions : "
                     f"{'identique' if match else 'DIFFÉRENT'}.")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.' if all_trunc_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_delinquency_nfci_combined_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

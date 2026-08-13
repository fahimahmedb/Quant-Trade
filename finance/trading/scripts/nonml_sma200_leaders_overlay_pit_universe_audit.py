"""Audit — Leaders + overlay SMA200, univers point-in-time.

Le backtest a établi ce que le PREREG annonçait comme possible : sur la fenêtre
2015-2026, le signal SMA200 et l'union SMA200 ∪ 52w-high **ne diffèrent jamais**.
Ce cycle est donc une identité arithmétique du #401.

L'audit qui a du sens ici n'est pas de rejouer les contrôles génériques déjà
passés au #401 — c'est de **prouver l'identité**, puis de la justifier. Quatre
contrôles :

1. **Identité bit-à-bit des P&L** avec `nonml_leaders_trend_union_overlay_pit_universe_pnl.npz`.
   Si les deux séries coïncident exactement, tous les contrôles passés au #401
   (simulation en nombre de parts, anti-lookahead sur les prix) portent
   littéralement sur les mêmes nombres et se transfèrent — ce n'est pas un
   raccourci, c'est la même série.
2. **Inclusion des signaux mesurée directement sur l'indice**, sur toute
   l'histoire disponible et pas seulement sur la fenêtre testée : combien de
   séances le 52w-high est-il actif sans la SMA200 ?
3. **Causalité du décalage des poids** (recalculée ici, pas héritée).
4. **Appartenance point-in-time à la date de décision** (recalculée ici).

Usage : python3 scripts/nonml_sma200_leaders_overlay_pit_universe_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import nonml_sma200_leaders_overlay_pit_universe_backtest as bt  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

OUT = ROOT / "results" / "nonml_sma200_leaders_overlay_pit_universe_audit.md"
REF_NPZ = ROOT / "results" / "nonml_leaders_trend_union_overlay_pit_universe_pnl.npz"
OWN_NPZ = ROOT / "results" / "nonml_sma200_leaders_overlay_pit_universe_pnl.npz"


def main():
    L = ["# Audit — Leaders + overlay SMA200, univers point-in-time", ""]
    L.append("Le backtest a confirmé ce que le PREREG annonçait comme possible : sur")
    L.append("2015-2026 le signal SMA200 et l'union SMA200 ∪ 52w-high ne diffèrent jamais.")
    L.append("Ce cycle est une **identité arithmétique** du #401. L'audit le prouve plutôt")
    L.append("que de rejouer des contrôles déjà passés sur les mêmes nombres.")
    L.append("")

    # --- 1. identite bit-a-bit avec le #401 ---
    own = np.load(OWN_NPZ, allow_pickle=True)
    ref = np.load(REF_NPZ, allow_pickle=True)
    fields = ["pnl_gross_ov", "pnl_gross_bh", "turn_ov", "turn_bh"]
    exact = {}
    for f in fields:
        a, b = own[f], ref[f]
        exact[f] = bool(a.shape == b.shape and np.array_equal(a, b))
    dates_same = bool(np.array_equal(own["dates"], ref["dates"]))
    cost_same = bool(float(own["cost_bps"]) == float(ref["cost_bps"]))
    ok1 = all(exact.values()) and dates_same and cost_same

    L.append("## 1. Identité bit-à-bit du P&L avec le #401")
    L.append("")
    L.append("Comparaison des deux `.npz` sauvegardés, série par série, par égalité")
    L.append("**exacte** (`np.array_equal`, pas une tolérance numérique).")
    L.append("")
    L.append("| Série | Longueur | Identique au #401 |")
    L.append("|---|---|---|")
    for f in fields:
        L.append(f"| `{f}` | {len(own[f])} | **{'OUI' if exact[f] else 'NON'}** |")
    L.append(f"| `dates` | {len(own['dates'])} | **{'OUI' if dates_same else 'NON'}** |")
    L.append(f"| `cost_bps` | — | **{'OUI' if cost_same else 'NON'}** |")
    L.append("")
    if ok1:
        L.append("**IDENTITÉ CONFIRMÉE — les deux candidats produisent exactement la même série.**")
        L.append("")
        L.append("Conséquence : les contrôles du #401 (simulation en nombre de parts,")
        L.append("anti-lookahead par perturbation des prix, appartenance PIT) portent sur ces")
        L.append("nombres-ci. Les transférer n'est pas un raccourci — c'est la même série. La")
        L.append("réserve du #401 (écart de niveau 6,34 % au contrôle en parts) se transfère")
        L.append("elle aussi, à l'identique, et n'est donc pas passée sous silence ici.")
    else:
        L.append("**DIVERGENCE — les deux candidats ne produisent pas la même série.**")
        L.append("")
        L.append("Le résultat serait alors une observation propre et non un doublon, contrairement")
        L.append("à ce que la mesure de signal du backtest indique. À investiguer avant de conclure.")
    L.append("")

    # --- 2. inclusion des signaux sur TOUTE l'histoire de l'indice ---
    sma_sig, union_sig = bt.index_signals()
    near_only = int(((~sma_sig.values) & union_sig.values).sum())
    n_defined = int(len(sma_sig))
    sma_on = int(sma_sig.values.sum())

    L.append("## 2. Inclusion des signaux, mesurée sur toute l'histoire de l'indice")
    L.append("")
    L.append("Le backtest mesure la divergence sur la seule fenêtre testable (2900 séances).")
    L.append("Ce contrôle élargit la mesure à **tout** l'historique NDX-100 disponible, pour")
    L.append("vérifier que l'inclusion n'est pas un accident de fenêtre.")
    L.append("")
    L.append(f"- séances d'indice examinées : **{n_defined}**")
    L.append(f"- séances où l'indice est au-dessus de sa SMA200 : **{sma_on}**")
    L.append(f"- séances où le 52w-high est actif **sans** la SMA200 : **{near_only}**")
    L.append("")
    if near_only == 0:
        L.append("**INCLUSION STRICTE SUR TOUTE L'HISTOIRE** — « à ≥ 95 % du plus haut 252 j »")
        L.append("implique toujours « au-dessus de la SMA200 » sur ces données. L'union des deux")
        L.append("est donc identiquement égale à SMA200 seul : les candidats #33 et #41 ne sont")
        L.append("pas deux stratégies mais une seule, écrite deux fois.")
    else:
        L.append(f"**INCLUSION NON STRICTE** — {near_only} séances où le 52w-high est actif seul.")
        L.append("L'union diffère alors de SMA200 sur ces séances ; si la fenêtre testable ne")
        L.append("les contient pas, la coïncidence observée est propre à la fenêtre.")
    L.append("")

    # --- 3 & 4. controles recalcules ici, non herites ---
    P, tickers, W, investable, _cov = bt.build_weights()
    W_lag = bt.lag_one_day(W)
    ok3 = bool(np.array_equal(W_lag[1:], W[:-1])) and bool((W_lag[0] == 0).all())

    L.append("## 3. Causalité du décalage des poids")
    L.append("")
    L.append("Recalculé ici, pas hérité du #401.")
    L.append("")
    L.append(f"- décalage d'exactement un jour vérifié : **{'OUI' if ok3 else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME' if ok3 else 'ANOMALIE'}**")
    L.append("")

    rebal_dates = list(range(bt.LOOKBACK, len(P), bt.REBAL_EVERY))
    viol = checked = 0
    for t in rebal_dates:
        if P.index[t] < bt.COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[t])
        if not members:
            continue
        checked += 1
        for j in np.where(W[t] > 0)[0]:
            if tickers[j] not in members:
                viol += 1

    L.append("## 4. Appartenance point-in-time à la date de décision")
    L.append("")
    L.append("Recalculé ici, pas hérité du #401.")
    L.append("")
    L.append(f"- dates de rebalancement vérifiées : **{checked}**")
    L.append(f"- sélections d'un non-membre à la décision : **{viol}**")
    L.append("")
    L.append(f"**{'CONFORME — aucun titre sélectionné avant son entrée dans l indice.' if viol == 0 else 'FUITE DÉTECTÉE'}**")
    L.append("")

    verdict = ok1 and (near_only == 0) and ok3 and (viol == 0)
    L.append("## Verdict de l'audit")
    L.append("")
    if verdict:
        L.append("**CONFORME — et le cycle est établi comme un doublon exact du #401.**")
        L.append("")
        L.append("Le verdict FAIL est correct, mais il ne constitue **pas** une observation")
        L.append("indépendante : conformément à la règle de comptage fixée au PREREG avant tout")
        L.append("calcul, ce cycle n'est pas ajouté au décompte des candidats testés de l'axe.")
        L.append("")
        L.append("Ce que ce cycle apporte réellement, et qui n'est pas rien : la confirmation")
        L.append("que deux entrées du backlog comptées séparément depuis le #33 et le #41")
        L.append("désignent la même stratégie. Le nombre d'essais indépendants du backlog est")
        L.append("donc surestimé d'au moins une unité — ce qui compte pour les corrections de")
        L.append("multiplicité (DSR, SPA), et va dans le sens **défavorable** aux candidats.")
    else:
        L.append("**NON CONFORME — au moins un contrôle échoue.**")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

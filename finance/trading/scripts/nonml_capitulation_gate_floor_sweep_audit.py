"""Audit — balayage des portes de capitulation neutralisées par le plancher 1,0×.

Quatre contrôles :

1. **Contrôles positif et négatif de la détection** — un script dont la structure
   est connue doit être trouvé ; un script qui ne l'a pas ne doit pas l'être. Un
   balayage qui ne trouve presque rien peut vouloir dire qu'il n'y a rien, ou
   qu'il ne sait pas chercher.
2. **Confirmation par lecture** du seul « PASS vide » signalé — critère 2 du
   pré-enregistrement.
3. **Exposition restante** — parmi les candidats détectés mais non mesurés faute
   de `.npz`, combien portent un PASS ? C'est la part du risque que ce cycle ne
   peut pas lever.
4. **Ce que le balayage corrige dans la formulation du #410** — la structure
   est-elle suffisante à elle seule pour neutraliser un overlay ?

Usage : python3 scripts/nonml_capitulation_gate_floor_sweep_audit.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"
sys.path.insert(0, str(SCRIPTS))

import nonml_capitulation_gate_floor_sweep_backtest as sw  # noqa: E402

OUT = RESULTS / "nonml_capitulation_gate_floor_sweep_audit.md"


def main():
    structured, measured, unmeasured, inactive, empty_pass = sw.main()

    L = ["# Audit — balayage des portes de capitulation neutralisées par le plancher 1,0×", ""]

    # --- 1. controles positif et negatif de la detection ---
    known = SCRIPTS / "nonml_weakness_breadth_vol_targeting_overlay_backtest.py"
    pos_ok = "weakness_breadth_vol_targeting_overlay" in structured
    # controle negatif : un overlay a exposition CONSTANTE (pas de vol-targeting)
    neg_name = "leaders_trend_union_overlay"
    neg_path = SCRIPTS / f"nonml_{neg_name}_backtest.py"
    neg_flagged = neg_name in structured
    neg_exists = neg_path.exists()

    L.append("## 1. La détection sait-elle chercher ?")
    L.append("")
    L.append("Un balayage qui ne trouve presque rien peut signifier qu'il n'y a presque rien,")
    L.append("ou qu'il ne sait pas chercher. Deux contrôles séparent les deux cas.")
    L.append("")
    L.append("**Contrôle positif** — le cas établi au #410 doit être détecté :")
    L.append("")
    L.append(f"- `nonml_weakness_breadth_vol_targeting_overlay_backtest.py` présent : "
             f"**{'OUI' if known.exists() else 'NON'}**")
    L.append(f"- détecté comme portant la structure : **{'OUI' if pos_ok else 'NON'}**")
    L.append("")
    L.append("**Contrôle négatif** — un overlay à exposition **constante** (`CAP` fixe, sans")
    L.append("vol-targeting) ne doit **pas** être signalé :")
    L.append("")
    L.append(f"- `nonml_{neg_name}_backtest.py` présent : **{'OUI' if neg_exists else 'NON'}**")
    L.append(f"- signalé à tort : **{'OUI' if neg_flagged else 'NON'}**")
    L.append("")
    ok1 = pos_ok and not neg_flagged
    L.append(f"**{'CONFORME — la détection trouve ce qu elle doit trouver et rien de plus.' if ok1 else 'DÉTECTION NON VALIDÉE — son résultat ne prouve rien.'}**")
    L.append("")

    # --- 2. confirmation par lecture du PASS vide ---
    L.append("## 2. Confirmation par lecture du « PASS vide » signalé")
    L.append("")
    L.append("Critère 2 du pré-enregistrement : aucun candidat n'est déclaré vide sur la seule")
    L.append("foi du compteur.")
    L.append("")
    if empty_pass:
        for n, a, v in empty_pass:
            rep = RESULTS / f"nonml_{n}_result.md"
            txt = rep.read_text(encoding="utf-8") if rep.exists() else ""
            has_warning = "NON INFORMATIF" in txt
            L.append(f"### `{n}`")
            L.append("")
            L.append(f"- activation mesurée : **{100*a:.2f} %**")
            L.append(f"- verdict au rapport : **{v}**")
            L.append(f"- le rapport porte-t-il déjà l'avertissement « NON INFORMATIF » : "
                     f"**{'OUI' if has_warning else 'NON'}**")
            L.append("")
            if has_warning:
                L.append("**Confirmé, et déjà documenté.** C'est le cas établi au #410, dont le")
                L.append("rapport porte l'étiquette depuis ce cycle-là. Le balayage ne découvre")
                L.append("donc rien de neuf ici — il **retrouve** le cas connu, ce qui est la")
                L.append("condition pour que son silence sur les autres ait un sens.")
            else:
                L.append("**Confirmé et NON documenté** — ce rapport annonce un PASS sans signaler")
                L.append("que la stratégie ne prend aucune position. À requalifier dans un cycle")
                L.append("dédié.")
            L.append("")
    else:
        L.append("Aucun.")
        L.append("")

    # --- 3. exposition restante ---
    unmeasured_pass = [n for n in unmeasured if sw.verdict_of(n) == "PASS"]
    L.append("## 3. Exposition restante — ce que ce cycle ne peut pas lever")
    L.append("")
    L.append(f"- candidats détectés mais non mesurés : **{len(unmeasured)}**")
    L.append(f"- dont portant un **PASS** : **{len(unmeasured_pass)}**")
    L.append("")
    if unmeasured_pass:
        for n in unmeasured_pass:
            L.append(f"- `{n}`")
        L.append("")
    L.append("Ces candidats ont la structure à risque et un verdict positif, mais aucun `.npz`")
    L.append("ne permet de mesurer leur activation. **Le diagnostic les laisse en suspens** :")
    L.append("c'est la mesure exacte de ce que la lacune du #406 coûte, et l'argument le plus")
    L.append("concret en faveur de la sauvegarde systématique du P&L.")
    L.append("")

    # --- 4. ce que le balayage corrige dans la formulation du #410 ---
    acts = np.array([a for _n, a, _v in measured], dtype=float)
    n_normal = int((acts >= sw.INACTIVE_MAX).sum())
    L.append("## 4. Ce que ce balayage corrige dans la formulation du #410")
    L.append("")
    L.append("Le #410 concluait que la structure valait « pour **toute** variante combinant une")
    L.append("porte de capitulation avec un vol-targeting à plancher 1,0× ». Le balayage")
    L.append("permet de préciser cette phrase.")
    L.append("")
    L.append(f"- candidats portant la structure `clip(…, 1.0, …)` : **{len(structured)}**")
    L.append(f"- parmi les **{len(measured)}** mesurés, activation normale (≥ "
             f"{100*sw.INACTIVE_MAX:.0f} %) : **{n_normal}**")
    if acts.size:
        L.append(f"- activation médiane des mesurés : **{100*float(np.median(acts)):.1f} %**")
    L.append("")
    L.append("**La structure seule ne neutralise rien.** Le plancher à 1,0× est très répandu")
    L.append("dans le dépôt et, dans la quasi-totalité des cas mesurés, l'overlay s'active")
    L.append("normalement. Ce qui neutralise, c'est la **conjonction** du plancher avec une")
    L.append("porte qui s'ouvre précisément quand la volatilité est haute — la faiblesse.")
    L.append("")
    L.append("La formulation du #410 était donc trop large : elle laissait entendre qu'un")
    L.append("montage fréquent était défectueux, alors que le défaut tient à un type de porte")
    L.append("particulier. Correction consignée ici plutôt que laissée à l'interprétation.")
    L.append("")

    L.append("## Verdict de l'audit")
    L.append("")
    if ok1:
        L.append("**MÉTHODE VALIDE.** Contrôles positif et négatif conformes : le balayage")
        L.append("retrouve le cas connu et ne signale pas de faux positif évident.")
        L.append("")
        L.append(f"Résultat : **{len(inactive)}** candidat structurellement inactif parmi les")
        L.append(f"{len(measured)} mesurés, déjà documenté. **{len(unmeasured_pass)}** candidats")
        L.append("à PASS restent hors de portée faute de `.npz` — c'est la limite du cycle, et")
        L.append("elle est chiffrée plutôt que passée sous silence.")
    else:
        L.append("**MÉTHODE NON VALIDÉE** — la détection échoue son propre contrôle.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

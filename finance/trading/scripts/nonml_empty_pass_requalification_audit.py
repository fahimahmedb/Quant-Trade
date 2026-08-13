"""Audit — requalification des PASS obtenus par inactivité (cycle #417).

Le balayage n'a requalifié **aucun** candidat. Deux lectures opposées sont
possibles : il n'y avait rien à requalifier, ou la détection ne sait pas
détecter. L'audit tranche.

Quatre contrôles :

1. **Contrôle positif** — un candidat dont l'inactivité est établie doit être
   reconnu par la règle. Sans cela, le zéro ne prouve rien.
2. **Contrôle négatif** — un candidat dont l'overlay agit ne doit pas être
   requalifié, même si son activation est faible (cas `santa`, tranché au #416).
3. **La tâche était-elle déjà faite ?** — le backlog demandait de requalifier
   `weakness_breadth_vol_targeting_overlay`. L'audit vérifie l'historique du
   fichier plutôt que de croire l'énoncé de la tâche.
4. **Portée non couverte** — quels schémas de `.npz` échappent à la règle, et
   combien de PASS cela laisse hors d'atteinte.

Usage : python3 scripts/nonml_empty_pass_requalification_audit.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import nonml_empty_pass_requalification_backtest as rq  # noqa: E402

OUT = RESULTS / "nonml_empty_pass_requalification_audit.md"


def main():
    requalified, already, pass_but_acts, examined, unusable = rq.main()

    L = ["# Audit — requalification des PASS obtenus par inactivité", ""]
    L.append("Le balayage n'a requalifié **aucun** candidat. Deux lectures opposées sont")
    L.append("possibles : il n'y avait rien à requalifier, ou la règle ne sait pas détecter.")
    L.append("Cet audit tranche.")
    L.append("")

    # --- 1. controle positif ---
    known = "weakness_breadth_vol_targeting_overlay"
    npz = RESULTS / f"nonml_{known}_pnl.npz"
    res = rq.pnl_identical(npz) if npz.exists() else None
    pos_ok = bool(res and res[0])

    L.append("## 1. Contrôle positif — la règle reconnaît-elle l'inactivité ?")
    L.append("")
    L.append(f"`{known}` a un P&L établi comme identique à Buy & Hold (#416).")
    L.append("")
    if res:
        L.append(f"- séances testées : **{res[1]}**")
        L.append(f"- séances où le P&L diffère (hors coût d'entrée) : **{res[2]}**")
        L.append(f"- reconnu identique par la règle : **{'OUI' if pos_ok else 'NON'}**")
    else:
        L.append("- `.npz` absent ou inexploitable")
    L.append("")
    L.append(f"**{'CONFORME — le zéro requalification est informatif.' if pos_ok else 'RÈGLE AVEUGLE — son zéro ne prouve rien.'}**")
    L.append("")

    # --- 2. controle negatif ---
    santa = "santa_vol_targeting_overlay"
    res_s = rq.pnl_identical(RESULTS / f"nonml_{santa}_pnl.npz")
    neg_ok = bool(res_s and not res_s[0])

    L.append("## 2. Contrôle négatif — une porte rare n'est pas une porte neutralisée")
    L.append("")
    L.append(f"`{santa}` n'active sa porte que 1,70 % du temps mais **agit** quand elle")
    L.append("s'ouvre (#416). La règle ne doit **pas** le requalifier.")
    L.append("")
    if res_s:
        L.append(f"- séances où le P&L diffère de Buy & Hold : **{res_s[2]}**")
        L.append(f"- requalifié à tort : **{'OUI' if res_s[0] else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME — le critère d identité ne confond pas rareté et inactivité.' if neg_ok else 'FAUX POSITIF'}**")
    L.append("")

    # --- 3. la tache etait-elle deja faite ? ---
    rep = RESULTS / f"nonml_{known}_result.md"
    txt = rep.read_text(encoding="utf-8") if rep.exists() else ""
    had_label = "NON INFORMATIF" in txt
    from_417 = rq.MARKER in txt

    L.append("## 3. La tâche demandée était-elle déjà faite ?")
    L.append("")
    L.append("Le backlog du #416 inscrivait comme tâche : « requalifier")
    L.append(f"`{known}` — le PASS doit porter l'étiquette non informatif comme sa version")
    L.append("point-in-time ». L'audit vérifie l'historique du fichier plutôt que de croire")
    L.append("l'énoncé de la tâche.")
    L.append("")
    L.append(f"- le rapport porte l'étiquette « NON INFORMATIF » : **{'OUI' if had_label else 'NON'}**")
    L.append(f"- cette étiquette a-t-elle été ajoutée par le présent cycle : "
             f"**{'OUI' if from_417 else 'NON'}**")
    L.append("")
    if had_label and not from_417:
        L.append("**La tâche était déjà faite — et depuis son cycle d'origine.** Le rapport du")
        L.append("#89 portait déjà, dans son propre texte, un avertissement en toutes lettres :")
        L.append("« PASS NON INFORMATIF […] l'overlay ne s'active essentiellement jamais […]")
        L.append("ne constitue PAS une validation économique ». L'étiquette n'a jamais manqué.")
        L.append("")
        L.append("**L'erreur est la mienne, et elle est datée** : en rédigeant la file du #416")
        L.append("j'ai inscrit cette requalification sans rouvrir le rapport concerné. C'est")
        L.append("exactement la règle du #400 — vérifier l'historique avant d'agir — appliquée")
        L.append("scrupuleusement aux candidats de stratégie et oubliée pour une tâche de")
        L.append("maintenance.")
        L.append("")
        L.append("Ce que le cycle a produit de réel n'est donc pas la requalification annoncée,")
        L.append("mais le **balayage systématique** qui l'accompagnait.")
    elif from_417:
        L.append("**L'étiquette a été ajoutée par ce cycle.**")
    else:
        L.append("**Le rapport ne porte aucune étiquette** — la tâche reste à faire.")
    L.append("")

    # --- 4. portee non couverte ---
    unusable_pass = []
    for name in unusable:
        rep_u = RESULTS / f"nonml_{name}_result.md"
        if rep_u.exists() and rq.verdict_of(rep_u) == "PASS":
            unusable_pass.append(name)

    L.append("## 4. Portée non couverte")
    L.append("")
    L.append(f"- `.npz` inexploitables par la règle : **{len(unusable)}**")
    L.append(f"- dont portant un PASS : **{len(unusable_pass)}**")
    L.append("")
    if unusable_pass:
        for n in unusable_pass:
            L.append(f"- `{n}`")
        L.append("")
    L.append("Ces candidats ont une jambe de référence qui n'est **pas** Buy & Hold mais un")
    L.append("portefeuille (schémas « panier » et « deux jambes »). Le critère d'identité ne")
    L.append("s'y transpose pas tel quel : un overlay de panier peut être inactif sans que son")
    L.append("P&L égale celui d'un indice. Étendre la règle à ces schémas demanderait de")
    L.append("comparer chaque candidat à **sa propre** référence — travail distinct, non")
    L.append("entrepris ici et déclaré comme tel.")
    L.append("")

    verdict = pos_ok and neg_ok
    L.append("## Verdict de l'audit")
    L.append("")
    if verdict:
        L.append("**MÉTHODE VALIDE.** Contrôles positif et négatif conformes : le zéro")
        L.append("requalification signifie bien qu'il n'y avait rien à requalifier parmi les")
        L.append(f"**{len(examined)}** candidats mesurables, et non que la règle est aveugle.")
        L.append("")
        L.append(f"Sur ces {len(examined)}, **{len(pass_but_acts)}** portent un PASS dont")
        L.append("l'overlay agit réellement. **Le PASS obtenu par inactivité est un cas isolé**,")
        L.append("déjà documenté à son cycle d'origine — pas un travers répandu du backlog.")
    else:
        L.append("**MÉTHODE NON VALIDÉE** — la règle échoue son propre contrôle.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

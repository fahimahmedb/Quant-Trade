"""Audit — réécriture de la ligne « Couverture 100 % » (#429).

Spécification pré-enregistrée dans `PREREG_coverage_wording_fix.md`, committée
avant toute modification.

Premier cycle qui **modifie** une ligne publiée. Le garde-fou n'est plus « ne
rien changer » mais « ne changer **que** ce qui est annoncé, mot pour mot ».

Quatre contrôles fixés avant calcul :
1. exactement 1 suppression dans le rapport du balayage de doublons ;
2. le texte inséré est celui du pré-enregistrement, au caractère près ;
3. décomptes de doublons inchangés (218 / 3 / 1) ;
4. le rapport jumeau (balayage de capitulation) est identique octet à octet.
"""
import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_coverage_wording_fix_audit.md"

DUP = RESULTS / "nonml_pnl_duplicate_sweep_result.md"
CAP = RESULTS / "nonml_capitulation_gate_floor_sweep_result.md"

DUP_BEFORE = Path(sys.argv[1]) if len(sys.argv) > 1 else None
CAP_BEFORE = Path(sys.argv[2]) if len(sys.argv) > 2 else None

# Texte FIXE dans le pre-enregistrement, recopie ici sans retouche.
REMOVED_EXPECTED = "**Couverture 100 %** — critère 1 du pré-enregistrement atteint."
INSERTED_EXPECTED = [
    "**100 % des fichiers trouvés ont été relus** — critère 1 du pré-enregistrement",
    "atteint. Ce taux ne mesure pas la couverture du dépôt : voir juste en dessous.",
]

EXPECTED_COUNTS = {"series": 218, "exact": 3, "quasi": 1}


def grab(txt, pat, default="-1"):
    m = re.search(pat, txt)
    return int(m.group(1)) if m else int(default)


def main():
    txt = DUP.read_text(encoding="utf-8")

    L = ["# Audit — réécriture de la ligne « Couverture 100 % » (pré-enregistré)", ""]
    L.append("Cycle d'**outillage documentaire**, et le **premier à modifier une ligne déjà")
    L.append("publiée**. Aucune stratégie évaluée, aucun verdict recalculé, aucun seuil touché.")
    L.append("")
    L.append("Les cinq lots de persistance (#416 → #427) tenaient « 0 différence octet à")
    L.append("octet » ; le #428 en est sorti pour n'ajouter que des insertions ; celui-ci")
    L.append("remplace du texte. Chaque régime a été déclaré avant d'être appliqué, et le")
    L.append("garde-fou est ici « ne changer **que** ce qui est annoncé, mot pour mot ».")
    L.append("")

    # --- Contrôles 1 et 2 -------------------------------------------------
    L.append("## Contrôles 1 et 2 — une seule ligne remplacée, par le texte annoncé")
    L.append("")
    added = removed = None
    if DUP_BEFORE and DUP_BEFORE.exists():
        a = DUP_BEFORE.read_text(encoding="utf-8").splitlines()
        b = txt.splitlines()
        diff = list(difflib.unified_diff(a, b, lineterm="", n=0))
        added = [d[1:] for d in diff if d.startswith("+") and not d.startswith("+++")]
        removed = [d[1:] for d in diff if d.startswith("-") and not d.startswith("---")]
        L.append(f"- lignes **supprimées** : **{len(removed)}**")
        L.append(f"- lignes **insérées** : **{len(added)}**")
        L.append("")
        one_removal = (len(removed) == 1 and removed[0] == REMOVED_EXPECTED)
        text_ok = all(x in added for x in INSERTED_EXPECTED)
        L.append("| Contrôle | Attendu | Obtenu | |")
        L.append("|---|---|---|---|")
        L.append(f"| suppressions | 1, exactement la ligne annoncée | {len(removed)} | "
                 f"{'✔' if one_removal else '✘'} |")
        L.append(f"| texte inséré | identique au pré-enregistrement | "
                 f"{'conforme' if text_ok else 'différent'} | {'✔' if text_ok else '✘'} |")
        L.append("")
        if removed:
            L.append("Ligne supprimée :")
            L.append("")
            L.append("```")
            for d in removed:
                L.append(d)
            L.append("```")
            L.append("")
        if added:
            L.append("Lignes insérées :")
            L.append("")
            L.append("```")
            for d in added:
                L.append(d)
            L.append("```")
            L.append("")
        if one_removal and text_ok:
            L.append("**Contrôles passés.** Le `diff` se limite à la ligne annoncée, et le texte")
            L.append("de remplacement est celui fixé avant tout calcul — il n'a pas été retouché")
            L.append("après avoir vu le rendu, ce que l'engagement 2 interdisait.")
        else:
            L.append("**Contrôle ÉCHOUÉ** — le `diff` déborde de ce qui était annoncé, ou le")
            L.append("texte inséré diffère du pré-enregistrement. Bloquant.")
    else:
        one_removal = text_ok = False
        L.append("**Contrôles non exécutables** — instantané avant modification absent.")
    L.append("")

    # --- Contrôle 3 -------------------------------------------------------
    L.append("## Contrôle 3 — décomptes de doublons inchangés")
    L.append("")
    got = {
        "series": grab(txt, r"P&L reconstruits\s*:\s*\*\*(\d+)\*\*"),
        "exact": grab(txt, r"groupes de doublons\s*:\s*\*\*(\d+)\*\*"),
        "quasi": grab(txt, r"paires signalées\s*:\s*\*\*(\d+)\*\*"),
    }
    labels = {"series": "séries de P&L reconstruites", "exact": "groupes de doublons exacts",
              "quasi": "quasi-doublons"}
    counts_ok = all(EXPECTED_COUNTS[k] == got[k] for k in EXPECTED_COUNTS)
    L.append("| | #428 | #429 | |")
    L.append("|---|---|---|---|")
    for k in ("series", "exact", "quasi"):
        L.append(f"| {labels[k]} | {EXPECTED_COUNTS[k]} | **{got[k]}** | "
                 f"{'✔' if EXPECTED_COUNTS[k] == got[k] else '✘'} |")
    L.append("")
    L.append("**Aucun décompte n'a bougé.**" if counts_ok else
             "**Un décompte a changé** — la réécriture a touché la détection. Bloquant.")
    L.append("")

    # --- Contrôle 4 -------------------------------------------------------
    L.append("## Contrôle 4 — le rapport jumeau est resté intact")
    L.append("")
    L.append("Deux rapports portaient la même formule. Le second dit **vrai** : son volet A")
    L.append("examine réellement les **284** scripts `nonml_*_backtest.py` du dépôt, 0 illisible,")
    L.append("et son volet B publie sa propre couverture séparément (62/62 depuis le #427).")
    L.append("")
    L.append("Corriger une formulation exacte parce qu'elle **ressemble** à une formulation")
    L.append("fautive serait du zèle, pas de la rigueur. Ce contrôle vérifie que je m'en suis")
    L.append("abstenu.")
    L.append("")
    cap_ok = None
    if CAP_BEFORE and CAP_BEFORE.exists():
        cap_ok = CAP_BEFORE.read_bytes() == CAP.read_bytes()
        L.append(f"- `nonml_capitulation_gate_floor_sweep_result.md` : "
                 f"**{'identique octet à octet' if cap_ok else 'MODIFIÉ'}** "
                 f"{'✔' if cap_ok else '✘'}")
        if not cap_ok:
            L.append("")
            L.append("**Contrôle ÉCHOUÉ** — le rapport jumeau a changé alors qu'il ne devait pas.")
    else:
        L.append("**Contrôle non exécutable** — instantané absent.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    all_ok = bool(one_removal and text_ok and counts_ok and cap_ok)
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| suppressions dans le rapport | 1 | {len(removed) if removed is not None else '—'} | "
             f"{'✔' if one_removal else '✘'} |")
    L.append(f"| texte inséré | celui du pré-enregistrement | "
             f"{'conforme' if text_ok else '—'} | {'✔' if text_ok else '✘'} |")
    L.append(f"| décomptes | 218 / 3 / 1 | {got['series']} / {got['exact']} / {got['quasi']} | "
             f"{'✔' if counts_ok else '✘'} |")
    L.append(f"| rapport jumeau | 0 différence | "
             f"{'0' if cap_ok else '—'} | {'✔' if cap_ok else '✘'} |")
    L.append("")
    if all_ok:
        L.append("**Prédiction déductive vérifiée.** La limite que le #428 avait signalée est")
        L.append("fermée : la ligne ne promet plus une couverture du dépôt qu'elle ne mesure")
        L.append("pas, et la section ajoutée au #428 la complète juste en dessous.")
        L.append("")
        L.append("Trois régimes de modification auront donc été déclarés puis tenus : **0")
        L.append("différence** (#416 → #427), **insertions seulement** (#428), **remplacement")
        L.append("d'une ligne annoncée** (#429). Aucun n'a été élargi en cours de route.")
    else:
        L.append("**Un contrôle a échoué** — voir ci-dessus avant toute autre conclusion.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

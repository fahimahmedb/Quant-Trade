"""Les trois ecarts silencieux du #444 : mesurer avant de decider (#455).

Specification pre-enregistree dans `PREREG_silent_skip_decision.md`, committee
AVANT toute mesure.

Cycle de **decision**. Le #444 etait explicite : ces trois consommateurs n'ont
pas de DEFAUT, leur resultat reste juste — c'est une lacune de couverture. La
question n'est donc pas « corriger » mais **« est-ce trompeur ? »**.
"""
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"

OUT = RESULTS / "nonml_silent_skip_decision_result.md"

# Les trois classes C du #444, avec la ligne citee par son rapport.
CIBLES = [
    ("nonml_empty_pass_requalification_backtest.py",
     "nonml_empty_pass_requalification_result.md",
     '`if "pos" not in d.files or "r_asset" not in d.files: continue`', False),
    ("nonml_pnl_persistence_lot5_audit.py",
     "nonml_pnl_persistence_lot5_audit.md",
     '`if "pos" not in p.files: continue`', False),
    ("nonml_npz_report_consistency_backtest.py",
     "nonml_npz_report_consistency_result.md",
     "compte ces fichiers sous l'étiquette **fausse** « schéma panier »", True),
]

# Une revendication de couverture : le rapport affirme voir TOUT.
REVENDIC = [
    re.compile(r"\bde \*\*tous\*\* les\b", re.I),
    re.compile(r"\btous les `?\*?\*?results?/?\*?_?pnl", re.I),
    re.compile(r"100\s*%\s*des fichiers", re.I),
    re.compile(r"\bexhaustif\b", re.I),
]


def n_skip_troisieme_schema():
    """Combien de `.npz` portent le troisieme schema (donc ecartes) ?"""
    n, noms = 0, []
    for p in sorted(RESULTS.glob("*_pnl.npz")):
        try:
            f = set(np.load(p, allow_pickle=True).files)
        except Exception:  # noqa: BLE001
            continue
        if "pos" not in f and not {"pnl_gross_ov", "turn_ov"} <= f:
            n += 1
            noms.append(p.name)
    return n, noms


def main():
    n_skip, noms = n_skip_troisieme_schema()

    lignes = []
    for script, rapport, ligne, historique in CIBLES:
        p = RESULTS / rapport
        t = p.read_text(encoding="utf-8") if p.exists() else ""
        hits = [rx.pattern for rx in REVENDIC if rx.search(t)]
        # La ligne exacte qui revendique, citee — ou son absence constatee.
        cite = None
        for ln in t.splitlines():
            if any(rx.search(ln) for rx in REVENDIC):
                cite = ln.strip()
                break
        if historique:
            decision = "ne rien changer (compte rendu d'un cycle passé)"
        elif n_skip > 0 and hits:
            decision = "**rendre l'écart visible**"
        else:
            decision = "ne rien changer"
        lignes.append((script, rapport, ligne, historique, bool(hits), cite, decision))

    a_modifier = [r for r in lignes if r[6].startswith("**")]

    L = ["# Les trois écarts silencieux du #444 : mesurer avant de décider "
         "(pré-enregistré)", ""]
    L.append("**Cycle de décision.** Il pouvait se conclure par « on ne touche à rien » ;")
    L.append("la règle était fixée **avant** toute mesure.")
    L.append("")

    L.append("## Ce que le #444 disait, et qu'il faut rappeler")
    L.append("")
    L.append("Ces trois consommateurs **n'ont pas de défaut** : leur résultat reste juste.")
    L.append("Ils écartent le troisième schéma `.npz` sans le signaler — une **lacune de")
    L.append("couverture**. Un silence n'induit en erreur que si le rapport **affirme** une")
    L.append("couverture que ce silence contredit.")
    L.append("")

    L.append("## Combien de fichiers sont écartés ?")
    L.append("")
    L.append(f"`.npz` du **troisième schéma** (ni `pos`, ni clés de panier) : **{n_skip}**")
    L.append("")
    for x in noms:
        L.append(f"- `{x}`")
    L.append("")

    L.append("## Chaque rapport revendique-t-il une couverture ?")
    L.append("")
    L.append("| Script | Ligne qui écarte | Revendique | Ligne citée | Décision |")
    L.append("|---|---|---|---|---|")
    for s, rap, ligne, hist, rev, cite, dec in lignes:
        c = f"`{cite[:60]}`" if cite else "— aucune —"
        L.append(f"| `{s}` | {ligne} | {'**oui**' if rev else 'non'} | {c} | {dec} |")
    L.append("")

    L.append("## La décision")
    L.append("")
    L.append("Règle fixée avant mesure : *rendre l'écart visible si et seulement si*")
    L.append("`n_skip > 0` **et** *le rapport revendique une couverture que ce silence")
    L.append("contredit*.")
    L.append("")
    if not a_modifier:
        L.append("### **Décision : on ne touche à rien.**")
        L.append("")
        L.append("Aucun des trois rapports ne revendique une couverture exhaustive des")
        L.append("fichiers. Leur silence ne trompe donc personne : ils parlent de")
        L.append("**candidats**, pas de l'inventaire des `.npz` du dépôt.")
        L.append("")
        L.append("**C'est la conclusion d'un cycle, pas son échec.** Un cycle qui mesure et")
        L.append("conclut qu'il n'y a rien à faire vaut mieux qu'un cycle qui modifie pour")
        L.append("justifier son existence — et la dette inscrite depuis le #444 se ferme")
        L.append("ici, par une mesure plutôt que par un abandon.")
        L.append("")
        L.append("**Prédiction vérifiée** : je l'annonçais, en n'excluant pas l'inverse.")
    else:
        L.append(f"### **Décision : rendre l'écart visible dans {len(a_modifier)} script(s).**")
        L.append("")
        for s, *_ in a_modifier:
            L.append(f"- `{s}`")
        L.append("")

    L.append("")
    L.append("## La provision déclarée d'avance, et son application")
    L.append("")
    L.append("`nonml_npz_report_consistency_backtest.py` produit le **compte rendu du")
    L.append("#442**. Le pré-enregistrement prévoyait de **ne pas y toucher**, quelle que")
    L.append("soit la mesure : le régénérer ferait re-raconter ce cycle avec un état du")
    L.append("dépôt qu'il n'a pas connu.")
    L.append("")
    L.append("**Appliqué.** Le #449 avait rencontré ce cas de figure **sans l'avoir prévu**")
    L.append("et avait dû publier une entorse ; ici la provision était écrite avant, et il")
    L.append("n'y a pas d'entorse à signaler. C'est le seul progrès de méthode de ce cycle,")
    L.append("et il est mince.")
    L.append("")

    L.append("## Ce que ce cycle ne permet pas de conclure")
    L.append("")
    L.append("- Il ne dit **pas** que ces scripts couvrent tout le dépôt : ils n'en couvrent")
    L.append(f"  pas les **{n_skip}** fichiers du troisième schéma. Il dit que **leur")
    L.append("  rapport ne prétend pas le contraire**.")
    L.append("- Il ne **recalcule** aucun verdict et ne régénère aucun rapport.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date")
    L.append("> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,")
    L.append("> et ce n'est pas une péremption de résultat (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

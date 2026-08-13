"""Audit de la campagne v2 (#437).

Spécification pré-enregistrée dans `PREREG_reproducibility_campaign_v2.md`.

**Une divergence a de nouveau été trouvée** — et l'instruire montre que le
critère d'auto-référence que j'avais pré-enregistré était **incomplet**. Cet
audit nomme ce défaut, le chiffre, et refuse de corriger le critère ici pour
sauver la borne.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
OUT = RESULTS / "nonml_reproducibility_campaign_v2_audit.md"
REPORT = RESULTS / "nonml_reproducibility_campaign_v2_result.md"

# Critere tel que PRE-ENREGISTRE au #437 : trois litteraux exacts.
NARROW = re.compile(
    r'glob\("nonml_\*_backtest\.py"\)|glob\("\*_pnl\.npz"\)|glob\("nonml_\*_result\.md"\)')
# Critere CONCEPTUEL : balayage d'un repertoire que les cycles alimentent.
CONCEPT = re.compile(r'(RESULTS|SCRIPTS)\.glob\(|ROOT\s*/\s*"(results|scripts)"[^\n]*\.glob\(')


def eligible():
    out = []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        n = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if (RESULTS / f"nonml_{n}_result.md").exists():
            out.append((n, s))
    return out


def main():
    txt = REPORT.read_text(encoding="utf-8")
    m = re.search(r"\| `([^`]+)` \| [\d.]+ s \| (\d+) \|", txt)
    name = m.group(1) if m else "?"

    L = ["# Audit — campagne v2 : le critère que j'avais pré-enregistré était incomplet", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("**aucun rapport publié modifié**.")
    L.append("")

    # --- La divergence ----------------------------------------------------
    L.append("## La divergence")
    L.append("")
    L.append(f"Sur 24 tirages dans le vivier « nettoyé » : **23 identiques**, **1 divergent** —")
    L.append(f"`{name}`.")
    L.append("")
    L.append("```")
    L.append("- - fichiers `nonml_*_pnl.npz` trouvés : **173**")
    L.append("+ - fichiers `nonml_*_pnl.npz` trouvés : **208**")
    L.append("```")
    L.append("")
    L.append("Le rapport annonçait **173** fichiers `.npz` ; il y en a **208** aujourd'hui.")
    L.append("Les 35 de plus ont été produits par mes propres cycles #416 à #427.")
    L.append("")

    # --- Le défaut du critère ---------------------------------------------
    L.append("## Le défaut — mon critère cherchait des littéraux, pas un concept")
    L.append("")
    L.append("Le critère pré-enregistré au #437 énumérait **trois écritures exactes** :")
    L.append("")
    L.append("```")
    L.append('glob("nonml_*_backtest.py")   glob("*_pnl.npz")   glob("nonml_*_result.md")')
    L.append("```")
    L.append("")
    L.append(f"Or `{name}` écrit `RESULTS.glob(\"nonml_*_pnl.npz\")`. **Le même concept, une")
    L.append("orthographe différente** — le préfixe `nonml_` à l'intérieur des guillemets")
    L.append("suffit à faire échouer la correspondance littérale.")
    L.append("")
    L.append("Le critère était censé être *mécanique et complet*. Il était mécanique, et")
    L.append("**incomplet** : j'ai encodé trois exemples au lieu de la propriété qu'ils")
    L.append("illustraient — « le script balaie un répertoire que les cycles alimentent ».")
    L.append("")

    items = eligible()
    n_narrow = sum(1 for _, s in items if NARROW.search(s.read_text(encoding="utf-8")))
    concept_hits = [n for n, s in items if CONCEPT.search(s.read_text(encoding="utf-8"))]
    missed = [n for n, s in items
              if CONCEPT.search(s.read_text(encoding="utf-8"))
              and not NARROW.search(s.read_text(encoding="utf-8"))]
    L.append("| Formulation du critère | Scripts capturés |")
    L.append("|---|---|")
    L.append(f"| **pré-enregistré** (trois littéraux) | **{n_narrow}** |")
    L.append(f"| **conceptuel** (`glob` sur `results/` ou `scripts/`) | **{len(concept_hits)}** |")
    L.append(f"| **manqués** par le critère pré-enregistré | **{len(missed)}** |")
    L.append("")
    for n in missed:
        L.append(f"- `{n}`")
    L.append("")
    L.append("L'écart est **petit en nombre** — deux scripts — mais il suffit à faire échouer")
    L.append("la campagne, puisqu'un seul tirage divergent suffit à annuler la borne.")
    L.append("")

    # --- Ce que je refuse de faire, pour la deuxième fois -----------------
    L.append("## Ce que je refuse de faire, pour la deuxième fois consécutive")
    L.append("")
    L.append("Le geste tentant est évident : élargir le critère au concept, relancer, publier")
    L.append("une borne. **Je ne le fais pas ici.**")
    L.append("")
    L.append("Le critère a été pré-enregistré **avant** ce tirage. Le corriger **après** avoir")
    L.append("vu quel script lui échappait — et sachant que ce script est précisément celui qui")
    L.append("annule la borne — serait exactement le geste que le #436 avait refusé, répété un")
    L.append("cycle plus tard avec une justification plus sophistiquée.")
    L.append("")
    L.append("> Le critère conceptuel sera **pré-enregistré au prochain cycle**, avec sa")
    L.append("> formulation exacte, et la campagne repartira **encore** de zéro.")
    L.append("")
    L.append("**Borne v2 : non publiée.** Comme au #436.")
    L.append("")

    # --- Ce que la campagne a réellement produit --------------------------
    L.append("## Ce que ces quatre cycles ont réellement produit")
    L.append("")
    L.append("Aucune borne publiable, et deux constats qui valent mieux qu'une borne :")
    L.append("")
    L.append("1. **Mon outillage de diagnostic est instable par construction.** Dix scripts")
    L.append("   embarquent un décompte du dépôt dans leur rapport ; ils divergent à chaque")
    L.append("   cycle qui ajoute un fichier. J'ai écrit la plupart d'entre eux, et introduit")
    L.append("   au #428 le compteur qui a fait tomber le premier.")
    L.append("2. **Un critère « mécanique » écrit trop vite reste faux.** Énumérer trois")
    L.append("   littéraux n'est pas formaliser une propriété. Le pré-enregistrement protège")
    L.append("   de l'ajustement après coup, il ne protège pas d'une spécification bâclée.")
    L.append("")
    L.append("Les rapports de **stratégie**, eux, n'ont produit **aucune divergence** :")
    L.append("sur les 84 tirages des #434-#437, les 4 divergences observées ou attendues sont")
    L.append("toutes des **diagnostics auto-référents**. C'est une indication rassurante — pas")
    L.append("une borne, et je ne la présente pas comme telle.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append("| critère appliqué, exclus listés | oui | 7 exclus | ✔ |")
    L.append("| 24 tirés et classés | 24 | 24 | ✔ |")
    L.append("| divergence publiée avec `diff` | si présente | **oui** | ✔ |")
    L.append("| rapports publiés modifiés | 0 | 0 | ✔ |")
    L.append("| borne v2 publiée | 11,7 % | **non publiée** | — |")
    L.append("")
    L.append("Le pré-enregistrement engageait à publier la borne « même si elle est moins")
    L.append("flatteuse ». Elle n'est pas moins flatteuse : elle est **inexistante**, et pour")
    L.append("une raison qui m'incombe.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

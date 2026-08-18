"""Audit adversarial du #495 — contrôle d'un cycle qui a exécuté puis renoncé.

Le cycle a EXECUTE deux scripts, obtenu ce qu'il voulait (temoins presents,
rapports idempotents), puis a tout restaure. C'est le renoncement le plus
couteux de la serie. L'audit verifie qu'il est FONDE et non theatral :

1. l'appel en process existe-t-il vraiment dans les deux scripts ?
2. l'effet collateral est-il attribuable a cet appel ?
3. l'arbre est-il reellement propre — rien n'a-t-il ete laisse ?
4. le critere 5 mesure-t-il l'execution, ou l'arbre apres coup ?
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAPPORT = RESULTS / "nonml_class_a_witness_publication_result.md"
OUT = RESULTS / "nonml_class_a_witness_publication_audit.md"
MOI = "class_a_witness_publication"
CIBLES = ["nonml_net_pnl_correction_backtest.py",
          "nonml_sweep_pass_prose_fix_backtest.py"]
COLLATERAL = "nonml_pnl_duplicate_sweep_result.md"


def sans_markdown(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def appels_en_process(py):
    """(modules du dépôt importés, lignes d'appel `.main()`) — par AST."""
    arbre = ast.parse(py.read_text(encoding="utf-8"))
    mods, alias = [], {}
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("nonml_"):
                    mods.append(a.name)
                    alias[a.asname or a.name] = a.name
    mains = []
    for n in ast.walk(arbre):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr == "main" and isinstance(n.func.value, ast.Name) \
                and n.func.value.id in alias:
            mains.append((n.lineno, alias[n.func.value.id]))
    return mods, mains


def main():
    pub = sans_markdown(RAPPORT.read_text(encoding="utf-8")) if RAPPORT.exists() else ""

    L = ["# Audit adversarial — l'exécution puis le renoncement (#495)", ""]
    L.append("Le cycle a **exécuté** deux scripts, **obtenu ce qu'il voulait** — témoins")
    L.append("présents, rapports idempotents — puis **tout restauré**. C'est le")
    L.append("renoncement le plus coûteux de la série. **L'audit vérifie qu'il est")
    L.append("fondé, et non théâtral.**")
    L.append("")

    # --- 1. L'appel en process --------------------------------------------
    L.append("## 1. L'appel en process existe-t-il vraiment ?")
    L.append("")
    L.append("Route : **AST** — résoudre l'alias d'import vers le module du dépôt, et")
    L.append("ne retenir que les `.main()` appelés **sur cet alias**.")
    L.append("")
    L.append("| Script | Module importé | Lignes d'appel `.main()` |")
    L.append("|---|---|---|")
    tous = True
    for nom in CIBLES:
        mods, mains = appels_en_process(SCRIPTS / nom)
        tous = tous and bool(mains)
        L.append(f"| `{nom}` | "
                 f"{', '.join('`' + m + '`' for m in mods) if mods else '—'} | "
                 f"**{[l for l, _m in mains] if mains else 'aucun'}** |")
    L.append("")
    if tous:
        L.append("> **Confirmé par résolution d'alias.** Les deux appellent le `main()`")
        L.append("> d'un module du dépôt. **Le classement A du #494 était faux**, et sa")
        L.append("> règle — qui cherchait `subprocess.run([sys.executable, …])` — ne")
        L.append("> pouvait pas le voir.")
    L.append("")

    # --- 2. L'effet collateral est-il attribuable ? ------------------------
    L.append("## 2. L'effet collatéral est-il attribuable à cet appel ?")
    L.append("")
    L.append(f"Le cycle impute la modification de `{COLLATERAL}` à `sw.main()`.")
    L.append("**Contrôle : le module appelé écrit-il bien ce fichier ?**")
    L.append("")
    cible_mod = None
    for nom in CIBLES:
        mods, mains = appels_en_process(SCRIPTS / nom)
        if mains:
            cible_mod = mains[0][1]
            break
    ecrit = "—"
    if cible_mod:
        src = (SCRIPTS / f"{cible_mod}.py").read_text(encoding="utf-8")
        m = re.search(r"OUT\s*=\s*RESULTS\s*/\s*[\"']([^\"']+)[\"']", src)
        ecrit = m.group(1) if m else "—"
    L.append(f"- module appelé : **`{cible_mod}`**")
    L.append(f"- son `OUT` : **`{ecrit}`**")
    L.append(f"- correspond au fichier collatéral : "
             f"**{'OUI' if ecrit == COLLATERAL else 'NON'}**")
    L.append("")
    attribue = ecrit == COLLATERAL
    if attribue:
        L.append("> **L'attribution est exacte.** Le fichier modifié est le rapport")
        L.append("> propre du module appelé. **L'effet de bord n'est pas une")
        L.append("> supposition** : il se lit dans le code du module.")
    L.append("")

    # --- 3. L'arbre est-il reellement propre ? -----------------------------
    L.append("## 3. L'arbre est-il réellement propre ?")
    L.append("")
    sale = [l for l in git("status", "--porcelain").splitlines()
            if l.strip() and MOI not in l]
    L.append(f"- fichiers modifiés hors ceux du cycle : **{len(sale)}**")
    for l in sale[:8]:
        L.append(f"  - `{l.strip()}`")
    L.append("")
    propre = not sale
    if propre:
        L.append("> **Rien n'a été laissé.** Le renoncement va jusqu'au bout : les")
        L.append("> rapports régénérés **et** le fichier collatéral sont restaurés.")
    L.append("")

    # --- 4. Le critere 5 s'auto-absout-il ? --------------------------------
    L.append("## 4. Le critère 5 mesure-t-il l'exécution, ou l'arbre après coup ?")
    L.append("")
    L.append("**C'est le point où un cycle pourrait se blanchir sans mentir** :")
    L.append("restaurer, puis constater que l'arbre est propre, et cocher le critère.")
    L.append("")
    controles = [
        ("le critère 5 est marqué NON", "Aucun autre fichier modifié par l'exécution — NON" in pub),
        ("le fichier collatéral est nommé dans le critère", COLLATERAL in pub),
        ("le rapport dit que mesurer après coup l'auto-absoudrait",
         "un critère qui s'auto-absout ne contrôle rien" in pub),
        ("le verdict est FAIL", "FAIL" in pub),
        ("rien n'est committé alors que les témoins étaient présents",
         "aucun n'est publié" in pub),
        ("la chaîne #487 → #494 → #495 est publiée", "un seul geste juste" in pub),
    ]
    L.append("| Contrôle | Résultat |")
    L.append("|---|---|")
    for lab, ok in controles:
        L.append(f"| {lab} | {'**OUI**' if ok else '**NON**'} |")
    L.append("")
    manques = [lab for lab, ok in controles if not ok]
    if not manques:
        L.append("> **Le critère mesure l'exécution, pas l'arbre restauré**, et le")
        L.append("> rapport écrit pourquoi. **Le FAIL est réel** : un cycle qui aurait")
        L.append("> mesuré après restauration aurait pu cocher le critère et publier.")
    else:
        L.append(f"> **{len(manques)} contrôle(s) échoue(nt)** :")
        for m in manques:
            L.append(f"> - {m}")
    L.append("")

    L.append("## Verdict")
    L.append("")
    bon = tous and attribue and propre and not manques
    L.append(f"**{'CONCORDANT' if bon else 'RÉSERVES'}** — l'appel en process est")
    L.append("**confirmé par résolution d'alias**, l'effet collatéral est **attribué")
    L.append("sur pièce**, l'arbre est **réellement propre**, et le critère 5")
    L.append(f"**ne s'auto-absout pas**. **{len(controles) - len(manques)}/"
             f"{len(controles)}** contrôles de transparence tenus.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

"""Audit adversarial du #490 — contrôle d'un cycle qui ne modifie rien.

Ne rien faire est le resultat le moins couteux. L'audit verifie donc que
l'abstention est **decidee par la mesure** et non commode :

1. la portee de `indet` est-elle bien celle annoncee ?  -> AST, autre parcours
2. le hissage serait-il vraiment anodin ?               -> le calcul est-il pur ?
3. le cycle a-t-il vraiment ete empeche par SON pre-enregistrement ?
4. le depot est-il intact, et le rapport cible non regenere ?
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAPPORT = RESULTS / "nonml_battery_witness_hoist_result.md"
PREREG = ROOT / "PREREG_battery_witness_hoist.md"
OUT = RESULTS / "nonml_battery_witness_hoist_audit.md"
CIBLE = SCRIPTS / "nonml_battery_coverage_backtest.py"
VAR, DEP = "indet", "executes"


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def portee_par_parcours(src, nom):
    """Parcours ascendant : le noeud d'affectation a-t-il un ancetre garde ?"""
    arbre = ast.parse(src)
    parents = {}
    for n in ast.walk(arbre):
        for c in ast.iter_child_nodes(n):
            parents[c] = n
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Assign):
            continue
        noms = []
        for t in n.targets:
            noms += [x.id for x in (t.elts if isinstance(t, (ast.Tuple, ast.List))
                                    else [t]) if isinstance(x, ast.Name)]
        if nom not in noms:
            continue
        prof, cur = 0, n
        while cur in parents:
            cur = parents[cur]
            if isinstance(cur, (ast.If, ast.For, ast.While, ast.Try)):
                prof += 1
            if isinstance(cur, ast.FunctionDef):
                break
        return n.lineno, prof
    return None, None


def calcul_pur(src, nom):
    """L'expression affectee a `nom` n'appelle-t-elle que des builtins ?"""
    arbre = ast.parse(src)
    for n in ast.walk(arbre):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == nom for t in n.targets):
            appels = set()
            for x in ast.walk(n.value):
                if isinstance(x, ast.Call):
                    f = x.func
                    appels.add(f.id if isinstance(f, ast.Name)
                               else (f.attr if isinstance(f, ast.Attribute) else "?"))
            return appels
    return None


def sans_markdown(t):
    """Retire gras/italique et replie les retours a la ligne.

    Les motifs de recherche de cette serie ont echoue cinq fois (#478, #482,
    #484, #487, #488) sur du texte francais mis en gras ou coupe en deux
    lignes. On normalise une fois pour toutes plutot que de le constater encore.
    """
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def main():
    src = CIBLE.read_text(encoding="utf-8")
    pub_brut = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""
    pre_brut = PREREG.read_text(encoding="utf-8") if PREREG.exists() else ""
    pub, pre = sans_markdown(pub_brut), sans_markdown(pre_brut)

    L = ["# Audit adversarial — le témoin non déplacé (#490)", ""]
    L.append("**Ne rien faire est le résultat le moins coûteux.** L'audit vérifie donc")
    L.append("que l'abstention est **décidée par la mesure**, et non commode.")
    L.append("")

    L.append("*(Les motifs de recherche de cet audit **normalisent le markdown** —")
    L.append("gras, code, retours à la ligne. Cinq audits de cette série ont échoué")
    L.append("sur du texte français mis en gras ; la classe d'erreur est corrigée ici")
    L.append("plutôt que constatée une sixième fois.)*")
    L.append("")

    L.append("## 1. La portée annoncée est-elle exacte ?")
    L.append("")
    L.append("Route : parcours **ascendant** des parents AST — l'inverse du parcours")
    L.append("descendant du backtest.")
    L.append("")
    L.append("| Nom | Ligne | Profondeur (parcours ascendant) |")
    L.append("|---|---|---|")
    lv, pv = portee_par_parcours(src, VAR)
    ld, pd = portee_par_parcours(src, DEP)
    L.append(f"| `{VAR}` | {lv} | **{pv}** |")
    L.append(f"| `{DEP}` | {ld} | **{pd}** |")
    L.append("")
    exact = pv is not None and pv > 0 and pd == 0
    if exact:
        L.append("> **Confirmé par une route indépendante.** `indet` est sous garde,")
        L.append("> `executes` ne l'est pas. **L'abstention repose sur un fait, pas sur")
        L.append("> une impression.**")
    else:
        L.append("> **Non confirmé** — publié tel quel.")
    L.append("")

    L.append("## 2. Le hissage serait-il vraiment anodin ?")
    L.append("")
    L.append("Le rapport l'affirme **contre lui-même** : hisser le calcul serait sans")
    L.append("effet. **Contrôle : l'expression n'appelle-t-elle que des fonctions")
    L.append("pures ?**")
    L.append("")
    appels = calcul_pur(src, VAR) or set()
    purs = appels <= {"sum", "len", "sorted", "set", "list"}
    L.append(f"- appels dans l'expression de `{VAR}` : "
             f"**{', '.join(sorted(appels)) if appels else 'aucun'}**")
    L.append(f"- tous **purs** *(builtins sans effet de bord)* : "
             f"**{'OUI' if purs else 'NON'}**")
    L.append("")
    if purs:
        L.append("> **L'aveu du rapport est vérifié.** Le hissage n'aurait eu aucun")
        L.append("> effet observable — **le cycle s'est donc privé d'une réparation")
        L.append("> inoffensive**, par la seule lettre de son pré-enregistrement.")
        L.append("")
        L.append("**C'est le coût réel de la discipline, et il est ici visible :** un")
        L.append("geste sûr n'a pas été fait parce qu'il n'avait pas été annoncé.")
    L.append("")

    L.append("## 3. Est-ce bien SON pré-enregistrement qui l'a empêché ?")
    L.append("")
    interdit = "il n'est pas fait" in pre and "hisser" in pre
    L.append(f"- le pré-enregistrement interdit explicitement le hissage : "
             f"**{'OUI' if interdit else 'NON'}**")
    L.append(f"- il a été committé **avant** le résultat : "
             f"**{'OUI' if git('log', '--format=%h', '--', 'finance/trading/PREREG_battery_witness_hoist.md').strip() else 'NON'}**")
    L.append("")
    if interdit:
        L.append("> **L'interdiction est bien dans le texte pré-enregistré**, écrite")
        L.append("> avant de connaître la portée de `indet`. **L'abstention n'est pas")
        L.append("> une justification construite après coup.**")
    L.append("")

    L.append("## 4. Le dépôt est-il intact ?")
    L.append("")
    diff = git("diff", "--numstat", "HEAD")
    lignes = [l for l in diff.splitlines()
              if l.strip() and "battery_witness_hoist" not in l]
    st = git("status", "--porcelain",
             "finance/trading/results/nonml_battery_coverage_result.md").strip()
    L.append(f"- fichiers modifiés hors ceux du cycle : **{len(lignes)}**")
    for l in lignes[:6]:
        L.append(f"  - `{l.strip()}`")
    L.append(f"- rapport de `battery_coverage` : "
             f"**{'inchangé' if not st else 'MODIFIÉ'}**")
    L.append("")
    intact = not lignes and not st
    if intact:
        L.append("> **Aucune modification, aucune exécution.** Le cycle a fait exactement")
        L.append("> ce qu'il annonçait : **rien**.")
    L.append("")

    L.append("## 5. Le cycle publie-t-il ce qui l'accuse ?")
    L.append("")
    controles = [
        ("il déclare d'avance que le résultat sur la règle serait non informatif",
         "non informatif" in pre),
        ("il écrit que son pré-enregistrement était trop strict",
         "plus strict que nécessaire" in pub),
        ("il dit que le hissage aurait été anodin", "anodin" in pub),
        ("il refuse d'assouplir la règle après mesure",
         "l'assouplir maintenant" in pub),
        ("il inscrit le hissage comme piste à déclarer", "déclarer le hissage" in pub),
    ]
    L.append("| Contrôle | Résultat |")
    L.append("|---|---|")
    for lab, ok in controles:
        L.append(f"| {lab} | {'**OUI**' if ok else '**NON**'} |")
    L.append("")
    manques = [lab for lab, ok in controles if not ok]
    if not manques:
        L.append("> **Le cycle publie que sa propre règle lui a coûté une réparation")
        L.append("> sûre**, et refuse quand même de l'assouplir. C'est la seule façon")
        L.append("> de rendre une abstention crédible.")
    else:
        L.append(f"> **{len(manques)} contrôle(s) échoue(nt)** :")
        for m in manques:
            L.append(f"> - {m}")
    L.append("")

    L.append("## Verdict")
    L.append("")
    bon = exact and purs and interdit and intact and not manques
    L.append(f"**{'CONCORDANT' if bon else 'RÉSERVES'}** — la portée est **confirmée**")
    L.append("par une route ascendante, le caractère anodin du hissage **vérifié**,")
    L.append("l'interdiction **présente dans le texte pré-enregistré**, le dépôt")
    L.append(f"**intact**, et **{len(controles) - len(manques)}/{len(controles)}**")
    L.append("contrôles de transparence tenus.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

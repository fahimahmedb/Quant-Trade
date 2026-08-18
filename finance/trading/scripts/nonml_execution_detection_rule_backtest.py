"""Une regle de classe qui voit l'execution en process (#496).

Specification pre-enregistree dans `PREREG_execution_detection_rule.md`,
committee AVANT toute mesure -- les trois conditions comprises.

Le #494 classait << execute un tiers >> sur `subprocess.run([sys.executable`.
Le #495 a montre que cette regle est AVEUGLE a l'execution en process
(`import nonml_x as sw; sw.main()`). Ce cycle mesure l'ampleur de cet angle
mort, SANS RIEN EXECUTER : lecture d'AST uniquement.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_execution_detection_rule_result.md"
SRC_494 = RESULTS / "nonml_unpublished_witnesses_paths_result.md"
MOI = "execution_detection_rule"

# La regle du #494, verbatim -- telle qu'elle est ecrite dans son backtest.
REGLE_494 = r"subprocess\.run\(\[sys\.executable"

# Les trois conditions de la regle corrigee, citees depuis le pre-enregistrement.
COND = {
    1: "`subprocess.run([sys.executable, …])` — la forme du #494",
    2: "importe un module `nonml_*` du dépôt **et** appelle `.main()` sur "
       "l'alias de cet import — la forme découverte au #495",
    3: "appelle `runpy.run_path`, `exec(open(…).read())` ou `importlib` sur "
       "un chemin de `scripts/`",
}


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def nom_attr(node):
    """Chaine pointee d'un Attribute/Name, ou None."""
    bouts = []
    cur = node
    while isinstance(cur, ast.Attribute):
        bouts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        bouts.append(cur.id)
        return ".".join(reversed(bouts))
    return None


def condition_1(arbre):
    """subprocess.run([sys.executable, ...]).

    Renvoie (declenchee, cibles). La condition pre-enregistree ne demande PAS
    que la cible soit nommable : elle l'est rarement (variable de chemin).
    """
    vue, cibles = False, []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        if nom_attr(n.func) not in ("subprocess.run", "subprocess.check_call",
                                    "subprocess.check_output"):
            continue
        if not n.args or not isinstance(n.args[0], (ast.List, ast.Tuple)):
            continue
        elts = n.args[0].elts
        if not elts or nom_attr(elts[0]) != "sys.executable":
            continue
        vue = True
        for e in elts[1:]:
            for sous in ast.walk(e):
                if isinstance(sous, ast.Constant) and isinstance(sous.value, str):
                    if sous.value.endswith(".py"):
                        cibles.append(sous.value)
    return vue, cibles


def alias_nonml(arbre, existants):
    """{alias -> module} pour tout `import nonml_*` du depot."""
    m = {}
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("nonml_") and a.name in existants:
                    m[a.asname or a.name] = a.name
    return m


def condition_2(arbre, existants):
    """Import d'un module nonml_* du depot + appel `.main()` sur son alias."""
    al = alias_nonml(arbre, existants)
    if not al:
        return []
    cibles = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Attribute):
            continue
        if n.func.attr != "main":
            continue
        base = nom_attr(n.func.value)
        if base in al:
            cibles.append(al[base] + ".py")
    return cibles


def condition_3(arbre, src):
    """runpy.run_path / exec(open(...).read()) / importlib sur un chemin scripts/."""
    cibles = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        nom = nom_attr(n.func)
        exotique = False
        if nom and (nom.startswith("runpy.") or nom.startswith("importlib")):
            exotique = True
        if isinstance(n.func, ast.Name) and n.func.id == "exec":
            if any(isinstance(s, ast.Call) and isinstance(s.func, ast.Name)
                   and s.func.id == "open" for s in ast.walk(n)):
                exotique = True
        if not exotique:
            continue
        seg = ast.get_source_segment(src, n) or ""
        if ".py" in seg or "scripts" in seg or "SCRIPTS" in seg:
            cibles.append(nom or "exec(open(…).read())")
    return cibles


def forme_hors_regle(arbre, existants):
    """`from nonml_x import main` + `main()` -- NON couverte par la regle declaree."""
    directs = {}
    for n in ast.walk(arbre):
        if isinstance(n, ast.ImportFrom) and n.module \
                and n.module.startswith("nonml_") and n.module in existants:
            for a in n.names:
                if a.name == "main":
                    directs[a.asname or a.name] = n.module
    if not directs:
        return []
    vus = []
    for n in ast.walk(arbre):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                and n.func.id in directs:
            vus.append(directs[n.func.id] + ".py")
    return vus


def analyse(py, existants):
    src = py.read_text(encoding="utf-8")
    arbre = ast.parse(src)
    v1, c1 = condition_1(arbre)
    c2 = condition_2(arbre, existants)
    c3 = condition_3(arbre, src)
    hors = forme_hors_regle(arbre, existants)
    r494 = len(re.findall(REGLE_494, src))
    return {"py": py.name, "c1": c1, "c2": c2, "c3": c3, "hors": hors,
            "r494": r494,
            "declenchees": [i for i, v in ((1, v1), (2, c2), (3, c3)) if v]}


def temoins_du_494():
    """Les 4 temoins, LUS dans le rapport du #494 -- pas une liste ecrite ici."""
    txt = SRC_494.read_text(encoding="utf-8")
    bloc = txt.split("## Les quatre mesures", 1)[-1].split("\n## ", 1)[0]
    noms, classes = [], {}
    for l in bloc.splitlines():
        m = re.match(r"\|\s*`([a-z0-9_]+\.py)`\s*\|", l)
        if m:
            noms.append(m.group(1))
            cl = re.findall(r"\*\*([ABC])\*\*\s*\|\s*$", l.rstrip())
            classes[m.group(1)] = cl[0] if cl else "?"
    return noms, classes


def main():
    avant = set(git("status", "--porcelain").splitlines())

    fichiers = [p for p in sorted(SCRIPTS.glob("nonml_*.py")) if MOI not in p.name]
    existants = {p.stem for p in SCRIPTS.glob("nonml_*.py")}
    profils = {}
    for py in fichiers:
        try:
            profils[py.name] = analyse(py, existants)
        except (SyntaxError, UnicodeDecodeError):
            continue

    noms_t, cl_494 = temoins_du_494()
    execute = [p for p in profils.values() if p["declenchees"]]
    aveugle = [p for p in profils.values() if p["r494"] == 0 and (p["c2"] or p["c3"])]
    hors_regle = [p for p in profils.values() if p["hors"] and not p["declenchees"]]

    par_cond = {i: [p for p in profils.values() if p["declenchees"] and i in p["declenchees"]]
                for i in (1, 2, 3)}

    cibles = {}
    for p in profils.values():
        for c in p["c1"] + p["c2"] + p["c3"]:
            cibles[c] = cibles.get(c, 0) + 1

    L = []
    A = L.append
    A("# Une règle de classe qui **voit l'exécution en process** (pré-enregistré)")
    A("")
    A("Le **#494** classait « exécute un tiers » sur la seule forme")
    A(f"`{REGLE_494}`. Le **#495** a montré qu'un script peut exécuter un tiers")
    A("**en process**, sans sous-processus — et que la règle ne le voit pas.")
    A("")
    A("## La règle corrigée, citée verbatim")
    A("")
    A("> Un script **exécute un tiers du dépôt** si l'une au moins de ces")
    A("> conditions est vraie, établie par **AST** :")
    for i in (1, 2, 3):
        A(f"> {i}. {COND[i]} ;")
    A("")
    A(f"- scripts `nonml_*.py` analysés : **{len(profils)}**")
    A(f"- scripts que la règle corrigée classe « exécute un tiers » : **{len(execute)}**")
    A("")
    A("| Condition | Scripts déclenchés |")
    A("|---|---|")
    for i in (1, 2, 3):
        A(f"| **{i}** | **{len(par_cond[i])}** |")
    A("")
    A("## Les quatre témoins du #494, reclassés")
    A("")
    A("Les noms sont **lus dans le rapport du #494**, pas réécrits ici.")
    A("")
    A("| Témoin | Classe #494 | Conditions déclenchées | Verdict règle corrigée |")
    A("|---|---|---|---|")
    n_exec_t = 0
    for n in noms_t:
        p = profils.get(n)
        if p is None:
            A(f"| `{n}` | **{cl_494.get(n,'?')}** | — | **script absent** |")
            continue
        d = ", ".join(str(i) for i in p["declenchees"]) or "aucune"
        v = "**exécute un tiers**" if p["declenchees"] else "**n'exécute rien**"
        if p["declenchees"]:
            n_exec_t += 1
        A(f"| `{n}` | **{cl_494.get(n,'?')}** | {d} | {v} |")
    A("")
    A(f"- témoins classés « exécute un tiers » par la règle corrigée : "
      f"**{n_exec_t}** sur **{len(noms_t)}**")
    A("")
    if n_exec_t == len(noms_t):
        A("> La conclusion du #495 — « les 4 sont de classe C » — **tient sur les")
        A("> quatre**, alors qu'il n'en avait lu que deux.")
    else:
        A(f"> **Le #495 a extrapolé.** Il concluait que les 4 témoins étaient de")
        A(f"> classe C après en avoir lu **2** ; la mesure en trouve **{n_exec_t}**")
        A(f"> qui exécutent un tiers. Sa conclusion était une **généralisation**,")
        A("> pas une mesure.")
    A("")
    A("## L'ampleur de l'angle mort du #494")
    A("")
    A("Scripts que la règle du #494 classait **« sans exécution »** et qui")
    A("**exécutent pourtant un tiers** :")
    A("")
    A(f"- scripts dans l'angle mort : **{len(aveugle)}**")
    A("")
    if aveugle:
        A("| Script | Condition | Cibles exécutées |")
        A("|---|---|---|")
        for p in sorted(aveugle, key=lambda x: x["py"]):
            d = ", ".join(str(i) for i in p["declenchees"])
            cs = ", ".join(f"`{c}`" for c in sorted(set(p["c2"] + p["c3"]))) or "—"
            A(f"| `{p['py']}` | {d} | {cs} |")
        A("")
    A("## Les cibles des exécutions")
    A("")
    A(f"- modules distincts exécutés par un tiers : **{len(cibles)}**")
    A("")
    A("Une cible n'est **pas toujours nommable statiquement** : quand le chemin")
    A("est construit dans une variable (`str(BATTERIE)`, `SCRIPTS / script`),")
    A("l'AST ne voit qu'un **fragment** — les entrées qui ne commencent pas par")
    A("`nonml_` en sont. Elles sont publiées **telles quelles**, non filtrées :")
    A("filtrer après lecture serait choisir ses chiffres.")
    A("")
    if cibles:
        A("| Cible | Nombre d'appels |")
        A("|---|---|")
        for c, k in sorted(cibles.items(), key=lambda x: (-x[1], x[0])):
            A(f"| `{c}` | **{k}** |")
        A("")
    A("## Une forme que ma propre règle corrigée ne voit pas")
    A("")
    A("`from nonml_x import main` puis `main()` exécute un tiers **sans**")
    A("attribut sur un alias — la condition 2 exige `.main()` **sur l'alias**.")
    A("La forme est comptée ici **hors règle**, sans reclassement : la règle a")
    A("été figée avant mesure et **ne sera pas élargie après coup**.")
    A("")
    A(f"- scripts employant cette forme, non déjà classés : **{len(hors_regle)}**")
    A("")
    if hors_regle:
        for p in sorted(hors_regle, key=lambda x: x["py"]):
            A(f"- `{p['py']}` → {', '.join('`'+c+'`' for c in sorted(set(p['hors'])))}")
        A("")
    A("## Deux bugs de mon propre détecteur, corrigés avant tout résultat")
    A("")
    A("Ils sont publiés parce qu'ils auraient **fabriqué une conclusion fausse**.")
    A("")
    A("1. **La condition 1 confondait « déclenchée » et « cible nommable ».**")
    A("   Elle ne se déclenchait que si un littéral `\"….py\"` figurait dans")
    A("   l'appel. Or `battery_coverage` et `six_reports_regeneration` passent")
    A("   une **variable** de chemin. Le premier jet les classait donc")
    A("   « n'exécute rien » — **2 témoins sur 4** — et j'aurais publié que le")
    A("   **#495 avait extrapolé**. Après correction : **4 sur 4**, et c'est le")
    A("   contraire qui est vrai.")
    A("2. **Le critère 5 se mesurait par regex sur ma propre source.** Ma source")
    A("   **cite** la règle du #494 en clair ; le motif s'y trouvait donc, et le")
    A("   critère tombait à **NON** pour un script qui n'exécute rien. C'est la")
    A("   distinction **porteur / citeur** du #473, retombée sur moi. Mesuré par")
    A("   **AST** — des appels, pas des chaînes — il vaut **0**.")
    A("")
    A("> Les deux fois, le détecteur était faux **dans le sens qui m'accusait**.")
    A("> Cela ne les rend pas anodins : un détecteur faux reste faux, et rien ne")
    A("> garantissait le signe.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = n_exec_t == len(noms_t)
    p2 = len(aveugle) >= 5
    p3 = len(par_cond[3]) == 0
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| les 4 témoins exécutent un tiers | 4 | {n_exec_t} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| ≥ 5 scripts dans l'angle mort du #494 | ≥ 5 | {len(aveugle)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| la condition 3 ne trouve rien | 0 | {len(par_cond[3])} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    A("## Aucune exécution")
    A("")
    mien = Path(__file__).read_text(encoding="utf-8")
    mien_regex = len(re.findall(REGLE_494, mien))
    v1m, c1m = condition_1(ast.parse(mien))
    mien_ast = len(condition_2(ast.parse(mien), existants)) + (1 if v1m else 0)
    A(f"- occurrences du motif du #494 dans ma source, **par regex** : "
      f"**{mien_regex}** — je **cite** la règle, je ne l'exerce pas ;")
    A(f"- **appels** d'exécution dans ma source, **par AST** : **{mien_ast}**.")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    ok5 = mien_ast == 0 and len(nouv) == 0
    A("## Critères de succès")
    A("")
    c = [("Règle corrigée citée verbatim, trois conditions publiées séparément "
          "avec leur compte", True),
         (f"Les **{len(noms_t)}** témoins reclassés, chacun avec sa condition",
          len(noms_t) == 4 and all(n in profils for n in noms_t)),
         ("Ampleur de l'angle mort du #494 mesurée sur tout le dépôt", True),
         (f"Cibles des exécutions nommées (**{len(cibles)}**)", len(cibles) > 0),
         ("Aucun script exécuté, arbre vérifié propre", ok5)]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé**, pas sur un rendement.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : cycle de vérification,")
    A("aucune position, aucun paramètre numérique de stratégie.")
    A("")
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    A("> de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(execute)} scripts exécutent un tiers, "
          f"angle mort #494 = {len(aveugle)}")


if __name__ == "__main__":
    main()

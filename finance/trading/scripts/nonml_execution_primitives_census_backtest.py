"""Recensement des primitives d'execution (#497).

Specification pre-enregistree dans `PREREG_execution_primitives_census.md`,
committee AVANT toute mesure -- univers des 12 primitives compris.

La regle << ce script execute un tiers >> a ete rapiecee trois fois (#494,
#495, #496). Ce cycle fige l'univers des primitives et les compte TOUTES,
zeros compris, SANS RIEN EXECUTER.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_execution_primitives_census_result.md"
RAP_496 = RESULTS / "nonml_execution_detection_rule_result.md"
AUD_496 = RESULTS / "nonml_execution_detection_rule_audit.md"
RAP_494 = RESULTS / "nonml_unpublished_witnesses_paths_result.md"
MOI = "execution_primitives_census"

PRINCIPE = (
    "Une règle qui prétend dire « ce script exécute un tiers » doit nommer "
    "**toute primitive qui exécute effectivement**. Le critère est **factuel, "
    "pas historique** : une forme entre parce qu'elle lance du code tiers, "
    "**jamais** parce qu'un cycle antérieur l'a rencontrée."
)
VARIANTE = (
    "la règle nomme les formes déjà observées en usage — un critère "
    "**historique**, qui aurait laissé `Popen` dehors."
)
LIBELLES = {
    "P1": "`subprocess.run([sys.executable, …])`",
    "P2": "`subprocess.Popen([sys.executable, …])`",
    "P3": "`subprocess.call` / `check_call` / `check_output` sur `sys.executable`",
    "P4": "`os.system(…)`",
    "P5": "`os.popen(…)`",
    "P6": "`os.execv*` / `os.spawn*`",
    "P7": "`runpy.run_path` / `runpy.run_module`",
    "P8": "`exec(open(…).read())` ou `eval` sur un fichier",
    "P9": "`importlib` (`spec_from_file_location`, `import_module`) sur `scripts/`",
    "P10": "`import nonml_* as a` + `a.main()` — l'exécution en process du #495",
    "P11": "`from nonml_* import main` + `main()`",
    "P12": "`multiprocessing.Process(target=…)`",
}
RAPIECAGES = [
    ("#494", "`subprocess.run([sys.executable, …])` — la règle d'origine"),
    ("#495", "découvre l'exécution **en process** (`import nonml_x ; x.main()`)"),
    ("#496", "ajoute la condition 2 ; son audit découvre `subprocess.Popen`"),
]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def pointe(node):
    bouts = []
    cur = node
    while isinstance(cur, ast.Attribute):
        bouts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        bouts.append(cur.id)
        return ".".join(reversed(bouts))
    return None


def liste_sys_executable(n):
    """L'appel passe-t-il [sys.executable, ...] en premier argument ?"""
    if not n.args or not isinstance(n.args[0], (ast.List, ast.Tuple)):
        return False
    e = n.args[0].elts
    return bool(e) and pointe(e[0]) == "sys.executable"


def constantes_py(n):
    out = []
    for s in ast.walk(n):
        if isinstance(s, ast.Constant) and isinstance(s.value, str) \
                and s.value.endswith(".py"):
            out.append(s.value)
    return out


def alias_imports(arbre, existants):
    """{alias -> module} pour `import nonml_x [as a]`, et noms de `from ... import main`."""
    par_alias, directs = {}, {}
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("nonml_") and a.name in existants:
                    par_alias[a.asname or a.name] = a.name
        elif isinstance(n, ast.ImportFrom):
            if n.module and n.module.startswith("nonml_") and n.module in existants:
                for a in n.names:
                    if a.name == "main":
                        directs[a.asname or a.name] = n.module
    return par_alias, directs


def primitives(src, arbre, existants):
    """Les 12 primitives, par AST. Renvoie {clef: [cibles]}."""
    t = {k: [] for k in LIBELLES}
    par_alias, directs = alias_imports(arbre, existants)
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        nom = pointe(n.func)
        seg = ast.get_source_segment(src, n) or ""
        cibles = constantes_py(n)

        if nom == "subprocess.run" and liste_sys_executable(n):
            t["P1"] += cibles or ["(chemin en variable)"]
        elif nom == "subprocess.Popen" and liste_sys_executable(n):
            t["P2"] += cibles or ["(chemin en variable)"]
        elif nom in ("subprocess.call", "subprocess.check_call",
                     "subprocess.check_output") and liste_sys_executable(n):
            t["P3"] += cibles or ["(chemin en variable)"]
        elif nom == "os.system":
            t["P4"] += cibles or ["(commande en variable)"]
        elif nom == "os.popen":
            t["P5"] += cibles or ["(commande en variable)"]
        elif nom and (re.match(r"^os\.execv", nom) or re.match(r"^os\.spawn", nom)):
            t["P6"] += cibles or ["(chemin en variable)"]
        elif nom in ("runpy.run_path", "runpy.run_module"):
            t["P7"] += cibles or ["(chemin en variable)"]
        elif isinstance(n.func, ast.Name) and n.func.id in ("exec", "eval"):
            if any(isinstance(s, ast.Call) and isinstance(s.func, ast.Name)
                   and s.func.id == "open" for s in ast.walk(n)):
                t["P8"] += cibles or ["(fichier en variable)"]
        elif nom and nom.startswith("importlib"):
            if ".py" in seg or "scripts" in seg or "SCRIPTS" in seg:
                t["P9"].append(nom)
        elif nom == "multiprocessing.Process" or (
                nom and nom.endswith(".Process")
                and nom.split(".")[0] == "multiprocessing"):
            if any(k.arg == "target" for k in n.keywords):
                t["P12"] += ["(cible en variable)"]

        if isinstance(n.func, ast.Attribute) and n.func.attr == "main":
            base = pointe(n.func.value)
            if base in par_alias:
                t["P10"].append(par_alias[base] + ".py")
        if isinstance(n.func, ast.Name) and n.func.id in directs:
            t["P11"].append(directs[n.func.id] + ".py")
    return {k: v for k, v in t.items() if v}


def noms_tableau(txt, titre):
    bloc = txt.split(titre, 1)[-1].split("\n## ", 1)[0]
    return [m.group(1) for l in bloc.splitlines()
            if (m := re.match(r"\|\s*`([a-z0-9_]+\.py)`\s*\|", l))]


def compte_dans(chemin, motif_re):
    """Un chiffre LU dans un rapport deja publie -- jamais retape ici.

    `motif_re` porte son propre groupe de capture : le nombre precede parfois
    la phrase (<< 2 script(s) appellent ... >>), et un lecteur qui cherche
    toujours APRES ramene un chiffre etranger -- l'erreur du premier jet.
    """
    plat = re.sub(r"\s+", " ", chemin.read_text(encoding="utf-8")
                  .replace("*", "").replace("`", ""))
    m = re.search(motif_re, plat)
    return int(m.group(1)) if m else None


def compte_496(motif):
    """Un chiffre du rapport du #496, LU -- pas retapé ici."""
    plat = re.sub(r"\s+", " ", RAP_496.read_text(encoding="utf-8")
                  .replace("*", "").replace("`", ""))
    m = re.search(re.escape(motif) + r"[^0-9]{0,40}(\d+)", plat)
    return int(m.group(1)) if m else None


def main():
    avant = set(git("status", "--porcelain").splitlines())

    fichiers = [p for p in sorted(SCRIPTS.glob("nonml_*.py")) if MOI not in p.name]
    existants = {p.stem for p in SCRIPTS.glob("nonml_*.py")}

    profils, par_prim = {}, {k: [] for k in LIBELLES}
    for py in fichiers:
        try:
            src = py.read_text(encoding="utf-8")
            arbre = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        t = primitives(src, arbre, existants)
        profils[py.name] = t
        for k in t:
            par_prim[k].append(py.name)

    executants = sorted(n for n, t in profils.items() if t)
    # La regle du #494 : P1 seule.
    r494 = {n for n, t in profils.items() if "P1" in t}
    aveugle = sorted(n for n in executants if n not in r494)
    cibles = {}
    for t in profils.values():
        for k, v in t.items():
            for c in v:
                cibles[c] = cibles.get(c, 0) + 1

    temoins = noms_tableau(RAP_494.read_text(encoding="utf-8"),
                           "## Les quatre mesures")
    t_exec = [n for n in temoins if profils.get(n)]

    e496 = compte_496("que la règle corrigée classe « exécute un tiers » :")
    a496 = compte_496("scripts dans l'angle mort :")
    c496 = compte_496("modules distincts exécutés par un tiers :")

    hors = [k for k in ("P3", "P4", "P5", "P6", "P7", "P8", "P11", "P12")
            if par_prim[k]]
    # Reconciliation : la regle du #496 = P1 (cond.1) + P9 (cond.3) + P10 (cond.2).
    set496 = {n for n, t in profils.items() if {"P1", "P9", "P10"} & set(t)}
    delta = sorted(n for n in executants if n not in set496)

    L = []
    A = L.append
    A("# Recenser les primitives d'exécution, au lieu de les rattraper une par une")
    A("")
    A("## Le principe d'inclusion, cité verbatim")
    A("")
    A(f"> {PRINCIPE}")
    A("")
    A(f"Il **aurait pu exclure** `Popen` : la variante rejetée était — {VARIANTE}")
    A("Le principe retenu étant **factuel**, `Popen` entre.")
    A("")
    A("## Les rapiéçages de cette règle")
    A("")
    A(f"- amendements successifs : **{len(RAPIECAGES)}**")
    A("")
    for c, quoi in RAPIECAGES:
        A(f"- **{c}** — {quoi} ;")
    A("")
    A("> Chaque cycle rattrapait la forme que le précédent avait manquée.")
    A("> **Ce recensement compte les 12 d'un coup, zéros compris.**")
    A("")
    A("## Les 12 primitives, comptées séparément")
    A("")
    A(f"- scripts `nonml_*.py` analysés : **{len(profils)}**")
    A("")
    A("| # | Primitive | Scripts | Appels |")
    A("|---|---|---|---|")
    for k in LIBELLES:
        na = sum(len(profils[n][k]) for n in par_prim[k])
        A(f"| {k} | {LIBELLES[k]} | **{len(par_prim[k])}** | **{na}** |")
    A("")
    nuls = [k for k in LIBELLES if not par_prim[k]]
    A(f"- primitives **jamais employées** : **{len(nuls)}** "
      f"({', '.join(nuls) if nuls else '—'})")
    A("")
    A("## Le recompte, et son écart avec le #496")
    A("")
    A("Les chiffres du #496 sont **lus dans son rapport**, pas retapés ici.")
    A("")
    A("| Grandeur | #496 | #497 | Écart |")
    A("|---|---|---|---|")
    for nom, a, b in (("scripts exécutants", e496, len(executants)),
                      ("angle mort du #494", a496, len(aveugle)),
                      ("cibles distinctes", c496, len(cibles))):
        d = (b - a) if a is not None else None
        A(f"| {nom} | **{a}** | **{b}** | **{d:+d}** |" if d is not None
          else f"| {nom} | **—** | **{b}** | **—** |")
    A(f"| témoins « exécute un tiers » | **{len(temoins)}** | "
      f"**{len(t_exec)}** | **{len(t_exec) - len(temoins):+d}** |")
    A("")
    A("## Les quatre témoins sous la règle amendée")
    A("")
    A("| Témoin | Primitives déclenchées |")
    A("|---|---|")
    for n in temoins:
        t = profils.get(n, {})
        A(f"| `{n}` | {', '.join(sorted(t)) if t else '**aucune**'} |")
    A("")
    A("## Les cibles")
    A("")
    A(f"- cibles distinctes : **{len(cibles)}**")
    A("")
    A("| Cible | Appels |")
    A("|---|---|")
    for c, k in sorted(cibles.items(), key=lambda x: (-x[1], x[0])):
        A(f"| `{c}` | **{k}** |")
    A("")
    A("Une cible n'est **pas toujours nommable statiquement** : les entrées")
    A("`(… en variable)` sont des appels dont l'AST ne voit pas la destination.")
    A("Elles sont publiées **telles quelles** — les retirer flatterait le compte.")
    A("")
    A("## Mes prédictions, confrontées")
    A("")
    p1 = len(executants) == 32
    p2 = bool(hors)
    p3 = len(t_exec) == len(temoins)
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| le recompte donne 32 exécutants | 32 | {len(executants)} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| ≥ 1 primitive hors P1/P2/P9/P10 employée | ≥ 1 | {len(hors)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| les 4 témoins restent classés | {len(temoins)} | {len(t_exec)} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    A("### Les deux premières sont réfutées **ensemble**" if not p1 and not p2
      else "### Ce que l'alternative a donné")
    A("")
    if not p1 and not p2:
        A("Le pré-enregistrement affirmait que les prédictions 1 et 2 étaient")
        A("**mutuellement exclusives par construction** : l'une devait tomber,")
        A("pas les deux. **Elles tombent toutes les deux.**")
        A("")
        A("> **Ma construction était fausse.** Elle supposait que le seul écart")
        A("> possible au « 30 + 2 » venait d'une primitive inconnue. Il venait")
        A("> d'ailleurs : **le « + 2 » lui-même était faux.**")
    else:
        A("Les prédictions 1 et 2 étaient annoncées mutuellement exclusives ;")
        A("la mesure les départage dans le sens prévu.")
    A("")
    if p2:
        A(f"Primitives trouvées hors du quatuor connu : "
          f"**{', '.join(hors)}** — l'univers figé **n'était pas superflu**.")
    else:
        A("**Aucune** primitive hors P1/P2/P9/P10 n'est employée : les huit")
        A("autres valent **zéro**. Le recensement n'a rien découvert — et c'est")
        A("**exactement ce qu'un recensement doit pouvoir donner** : sans lui,")
        A("l'absence n'était pas établie, seulement supposée.")
    A("")
    A("## D'où vient l'écart — réconciliation nom par nom")
    A("")
    A("La règle du #496 se reconstruit ici comme **P1 ∪ P9 ∪ P10** (ses")
    A("conditions 1, 3 et 2). Tout script exécutant hors de cet ensemble est")
    A("**nouveau**, et il est nommé :")
    A("")
    A(f"- exécutants sous la règle du #496 reconstruite : **{len(set496)}**")
    A(f"- exécutants supplémentaires sous la règle amendée : **{len(delta)}**")
    A("")
    for n in delta:
        A(f"- `{n}` → {', '.join(sorted(profils[n]))}")
    A("")
    reste = len(executants) - len(set496) - len(delta)
    A(f"- résidu inexpliqué : **{reste}**")
    A("")
    popen_496 = compte_dans(
        AUD_496, r"(\d+) script\(s\) appellent subprocess\.Popen")
    if popen_496 is not None and popen_496 != len(delta):
        A(f"> **L'audit du #496 avait compté {popen_496} script(s) `Popen` ; il")
        A(f"> y en a {len(delta)}.** Ce compte venait de sa route **regex**, et")
        A("> une route textuelle se trompe **une fois de plus** là où l'AST voit")
        A("> juste. **Ma prédiction 1 reposait sur ce chiffre emprunté sans le")
        A("> refaire** — c'est ce qui l'a fait tomber, pas une primitive exotique.")
        A("")
    elif popen_496 is None:
        A("> Le compte de `Popen` du #496 n'a **pas pu être relu** dans son")
        A("> audit ; l'écart n'est donc pas attribué à un chiffre précis.")
        A("")
    A("## Aucune exécution")
    A("")
    mien = Path(__file__).read_text(encoding="utf-8")
    t_mien = primitives(mien, ast.parse(mien), existants)
    A(f"- primitives d'exécution **d'un tiers du dépôt** dans ma source : "
      f"**{len([k for k, v in t_mien.items() if k != 'P1'])}**")
    A("  *(mes propres appels `subprocess` ne visent que `git`, jamais "
      "`sys.executable`)*")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    ok5 = not [k for k in t_mien if k != "P1"] and not nouv
    A("## Critères de succès")
    A("")
    c = [("Principe d'inclusion cité verbatim, avec la variante qui aurait "
          "exclu `Popen`", True),
         (f"Les **{len(LIBELLES)}** primitives comptées séparément, "
          f"**{len(nuls)}** zéros publiés", len(LIBELLES) == 12),
         ("Recompte publié avec son écart vs le #496 sur les quatre grandeurs",
          None not in (e496, a496, c496)),
         (f"Rapiéçages nommés et comptés (**{len(RAPIECAGES)}**)", True),
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
    print(f"{verdict} — {len(executants)} exécutants, {len(nuls)} primitives nulles, "
          f"hors quatuor : {hors or '—'}")


if __name__ == "__main__":
    main()

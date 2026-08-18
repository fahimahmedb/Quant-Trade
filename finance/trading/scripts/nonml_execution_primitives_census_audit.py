"""Audit independant du #497 -- recalcul par une AUTRE route.

Le backtest apparie des noeuds AST (Attribute, Name, arguments). Cet audit
recompte en DEPARSANT chaque noeud Call (`ast.unparse`) puis en appariant du
texte NORMALISE. La route partage l'analyse syntaxique -- deliberement : le
#496 a montre qu'une route purement textuelle confond porteur et citeur, et
qu'elle rate les appels coupes en plusieurs lignes. Ce qu'elle ne partage pas,
c'est la LOGIQUE d'appariement, qui est justement ce qui a faux au #496.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_execution_primitives_census_result.md"
BT = SCRIPTS / "nonml_execution_primitives_census_backtest.py"
RAP_496 = RESULTS / "nonml_execution_detection_rule_result.md"
RAP_494 = RESULTS / "nonml_unpublished_witnesses_paths_result.md"
OUT = RESULTS / "nonml_execution_primitives_census_audit.md"
MOI = "execution_primitives_census"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")

# Motifs sur le code DEPARSE d'un noeud Call -- une logique differente.
MOTIFS = {
    "P1": r"^subprocess\.run\(\[sys\.executable",
    "P2": r"^subprocess\.Popen\(\[sys\.executable",
    "P3": r"^subprocess\.(?:call|check_call|check_output)\(\[sys\.executable",
    "P4": r"^os\.system\(",
    "P5": r"^os\.popen\(",
    "P6": r"^os\.(?:execv|spawn)\w*\(",
    "P7": r"^runpy\.run_(?:path|module)\(",
    "P8": r"^(?:exec|eval)\(.*\bopen\(",
    "P9": r"^importlib\b",
}


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def plat(txt):
    return re.sub(r"\s+", " ", txt.replace("*", "").replace("`", ""))


def route_unparse(src, arbre, existants):
    """Les primitives, appariees sur le code DEPARSE de chaque Call."""
    vus = set()
    alias, directs = {}, {}
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("nonml_") and a.name in existants:
                    alias[a.asname or a.name] = a.name
        elif isinstance(n, ast.ImportFrom) and n.module \
                and n.module.startswith("nonml_") and n.module in existants:
            for a in n.names:
                if a.name == "main":
                    directs[a.asname or a.name] = n.module
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        try:
            code = ast.unparse(n)
        except Exception:
            continue
        for k, m in MOTIFS.items():
            if re.match(m, code):
                if k == "P9" and not re.search(r"\.py|scripts|SCRIPTS", code):
                    continue
                vus.add(k)
        m10 = re.match(r"^([A-Za-z_][\w.]*)\.main\(", code)
        if m10 and m10.group(1) in alias:
            vus.add("P10")
        m11 = re.match(r"^([A-Za-z_]\w*)\(", code)
        if m11 and m11.group(1) in directs:
            vus.add("P11")
        if re.match(r"^multiprocessing\.Process\(", code) and "target=" in code:
            vus.add("P12")
    return vus


def lit_table(txt):
    """{clef -> (scripts, appels)} depuis le tableau des 12 primitives."""
    bloc = txt.split("## Les 12 primitives", 1)[-1].split("\n## ", 1)[0]
    out = {}
    for l in bloc.splitlines():
        m = re.match(r"\|\s*(P\d+)\s*\|.*?\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|", l)
        if m:
            out[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    return out


def noms_tableau(txt, titre):
    bloc = txt.split(titre, 1)[-1].split("\n## ", 1)[0]
    return [m.group(1) for l in bloc.splitlines()
            if (m := re.match(r"\|\s*`([a-z0-9_]+\.py)`\s*\|", l))]


def main():
    rap = RAP.read_text(encoding="utf-8")
    src_bt = BT.read_text(encoding="utf-8")
    existants = {p.stem for p in SCRIPTS.glob("nonml_*.py")}
    fichiers = [p for p in sorted(SCRIPTS.glob("nonml_*.py")) if MOI not in p.name]

    compte = {k: 0 for k in list(MOTIFS) + ["P10", "P11", "P12"]}
    execs = set()
    for py in fichiers:
        try:
            s = py.read_text(encoding="utf-8")
            a = ast.parse(s)
        except (SyntaxError, UnicodeDecodeError):
            continue
        v = route_unparse(s, a, existants)
        for k in v:
            compte[k] += 1
        if v:
            execs.add(py.name)

    publie = lit_table(rap)
    ecarts = [(k, publie.get(k, (None, None))[0], compte.get(k, 0))
              for k in sorted(compte, key=lambda x: int(x[1:]))
              if publie.get(k, (None, None))[0] != compte.get(k, 0)]

    # --- Le total et la reconciliation tiennent-ils ? ----------------------
    p = plat(rap)
    def n(motif):
        m = re.search(motif, p)
        return int(m.group(1)) if m else None
    n_exec = n(r"scripts exécutants \| (?:\d+) \| (\d+)")
    n_496 = n(r"règle du #496 reconstruite : (\d+)")
    n_sup = n(r"supplémentaires sous la règle amendée : (\d+)")
    n_res = n(r"résidu inexpliqué : (\d+)")
    somme_ok = None not in (n_exec, n_496, n_sup, n_res) \
        and n_496 + n_sup + n_res == n_exec

    # --- Les chiffres empruntes au #496 sont-ils les bons ? ---------------
    p496 = plat(RAP_496.read_text(encoding="utf-8"))
    emprunts = {
        "scripts exécutants": (
            n(r"scripts exécutants \| (\d+)"),
            n and int(re.search(r"classe « exécute un tiers » : (\d+)", p496).group(1))),
        "angle mort": (
            n(r"angle mort du #494 \| (\d+)"),
            int(re.search(r"scripts dans l'angle mort : (\d+)", p496).group(1))),
        "cibles": (
            n(r"cibles distinctes \| (\d+)"),
            int(re.search(r"modules distincts exécutés par un tiers : (\d+)", p496).group(1))),
    }
    emprunts_ok = all(a == b for a, b in emprunts.values())

    # --- Temoins ----------------------------------------------------------
    t497 = noms_tableau(rap, "## Les quatre témoins sous la règle amendée")
    t494 = noms_tableau(RAP_494.read_text(encoding="utf-8"), "## Les quatre mesures")
    temoins_ok = sorted(t497) == sorted(t494)

    # --- Le backtest est-il inerte ? --------------------------------------
    a_bt = ast.parse(src_bt)
    # AUCUNE primitive n'est retiree ici : un `discard` de complaisance
    # masquerait justement ce que ce controle doit voir.
    v_bt = route_unparse(src_bt, a_bt, existants)
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]
    inerte = not v_bt and not sales

    # --- Chiffres en dur ---------------------------------------------------
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]

    L = []
    A = L.append
    A("# Audit indépendant — recensement des primitives d'exécution (#497)")
    A("")
    A("Le backtest apparie des **nœuds** AST. Cet audit **déparse** chaque")
    A("`Call` (`ast.unparse`) et apparie du **texte normalisé** — les deux")
    A("routes partagent l'analyse syntaxique, **pas la logique d'appariement**,")
    A("qui est précisément ce qui avait faux au #496.")
    A("")
    A("## Les 12 primitives, recomptées")
    A("")
    A("| # | Rapport | Route déparsée | Accord |")
    A("|---|---|---|---|")
    for k in sorted(compte, key=lambda x: int(x[1:])):
        a = publie.get(k, (None, None))[0]
        b = compte[k]
        A(f"| {k} | **{a}** | **{b}** | {'**oui**' if a == b else '**NON**'} |")
    A("")
    A(f"- primitives en désaccord : **{len(ecarts)}**")
    if ecarts:
        A("")
        for k, a, b in ecarts:
            A(f"  - **{k}** : rapport **{a}**, route déparsée **{b}**")
    A("")
    A("## La réconciliation tient-elle l'addition ?")
    A("")
    A(f"- exécutants publiés : **{n_exec}**")
    A(f"- sous la règle du #496 reconstruite : **{n_496}**")
    A(f"- supplémentaires : **{n_sup}** ; résidu : **{n_res}**")
    A(f"- l'addition ferme : **{'OUI' if somme_ok else 'NON'}**")
    A("")
    A("## Les chiffres empruntés au #496 sont-ils les siens ?")
    A("")
    A("Le backtest a **lu** trois chiffres dans le rapport du #496. Un lecteur")
    A("qui cherche le nombre **après** la phrase alors qu'il la **précède**")
    A("ramène un chiffre étranger — c'est arrivé dans ce cycle même. Ils sont")
    A("donc relus ici par une autre expression :")
    A("")
    A("| Grandeur | Colonne #496 du rapport | Relu dans le #496 | Accord |")
    A("|---|---|---|---|")
    for nom, (a, b) in emprunts.items():
        A(f"| {nom} | **{a}** | **{b}** | {'**oui**' if a == b else '**NON**'} |")
    A("")
    A("## Les témoins")
    A("")
    A(f"- noms listés par le #497 : **{len(t497)}** ; par le #494 : **{len(t494)}**")
    A(f"- listes identiques : **{'OUI' if temoins_ok else 'NON'}**")
    A("")
    A("## Le backtest exécute-t-il quelque chose ?")
    A("")
    A(f"- primitives d'exécution d'un tiers dans sa source : **{len(v_bt)}**")
    A(f"- fichiers de l'arbre git modifiés hors ce cycle : **{len(sales)}**")
    A("")
    if inerte:
        A("> **Rien n'a été exécuté.** Ses appels `subprocess` visent `git` et")
        A("> **ne passent pas par `sys.executable`** : aucune primitive ne se")
        A("> déclenche, sans qu'aucune ait été retirée à la main.")
    else:
        A("> **Le script n'est pas inerte** — le détail ci-dessus le montre.")
    A("")
    A("## Les chiffres du rapport sont-ils calculés ?")
    A("")
    A(f"- nombres en gras : **{len(GRAS.findall(rap))}** ; "
      f"dont **tapés en dur** : **{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("les deux routes donnent les mêmes 12 comptes", not ecarts),
            ("la réconciliation ferme l'addition sans résidu", bool(somme_ok)),
            ("les chiffres empruntés au #496 sont bien les siens", emprunts_ok),
            ("les témoins du #497 sont exactement ceux du #494", temoins_ok),
            ("le backtest n'exécute aucun tiers et ne salit pas l'arbre", inerte),
            ("aucun chiffre du rapport n'est tapé en dur", not en_dur)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : aucune série de prix.")
    A("Son équivalent ici est **l'inertie**, vérifiée ci-dessus.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — {len(ecarts)} désaccord(s)")


if __name__ == "__main__":
    main()

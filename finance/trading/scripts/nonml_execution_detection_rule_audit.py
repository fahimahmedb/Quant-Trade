"""Audit independant du #496 -- recalcul par une AUTRE route.

Le backtest classe par AST. Cet audit reconstruit les memes comptes par
EXPRESSIONS REGULIERES, une route qui ne partage aucune ligne avec la
premiere, puis confronte les deux. Un desaccord est publie, pas lisse.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_execution_detection_rule_result.md"
BT = SCRIPTS / "nonml_execution_detection_rule_backtest.py"
SRC_494 = RESULTS / "nonml_unpublished_witnesses_paths_result.md"
OUT = RESULTS / "nonml_execution_detection_rule_audit.md"
MOI = "execution_detection_rule"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")
R_IMPORT = re.compile(
    r"^[ \t]*import[ \t]+(nonml_\w+)(?:[ \t]+as[ \t]+(\w+))?[ \t]*(?:#.*)?$", re.M)
R_SUBPROC = re.compile(r"subprocess\.\w+\(\s*\[\s*sys\.executable")
R_POPEN = re.compile(r"subprocess\.Popen\(\s*\[\s*sys\.executable")
R_AUTRES = re.compile(r"subprocess\.check_(?:call|output)\(\s*\[\s*sys\.executable")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def lit(p):
    return p.read_text(encoding="utf-8")


def sans_markdown(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def sans_commentaires(src):
    return re.sub(r"#[^\n]*", "", src)


def sans_chaines(src):
    """Retire les litteraux de chaine -- separe le PORTEUR du CITEUR."""
    for t in ('"""', "'''"):
        src = re.sub(re.escape(t) + r"(?:.|\n)*?" + re.escape(t), t + t, src)
    src = re.sub(r'"(?:[^"\\\n]|\\.)*"', '\"\"', src)
    src = re.sub(r"'(?:[^'\\\n]|\\.)*'", "''", src)
    return src


def route_regex(src, existants):
    """c1 et c2 reconstruits sans AST."""
    c1 = bool(R_SUBPROC.search(src))
    c2 = []
    for mod, alias in R_IMPORT.findall(src):
        if mod not in existants:
            continue
        nom = alias or mod
        if re.search(r"\b" + re.escape(nom) + r"\.main\s*\(", src):
            c2.append(mod + ".py")
    return c1, c2


def compte_gras(txt, motif):
    """Le nombre en gras qui suit une phrase reperee -- lecture du rapport."""
    plat = sans_markdown(txt)
    m = re.search(re.escape(sans_markdown(motif)) + r"[^0-9]{0,40}(\d+)", plat)
    return int(m.group(1)) if m else None


def main():
    rap = lit(RAP)
    src_bt = lit(BT)
    existants = {p.stem for p in SCRIPTS.glob("nonml_*.py")}
    fichiers = [p for p in sorted(SCRIPTS.glob("nonml_*.py")) if MOI not in p.name]

    # --- Route independante -------------------------------------------------
    r_exec, r_c1, r_c2, r_cibles = [], [], [], {}
    r_citeur, r_popen, r_autres = [], [], []
    for py in fichiers:
        try:
            s = lit(py)
        except UnicodeDecodeError:
            continue
        c1, c2 = route_regex(s, existants)
        if c1:
            r_c1.append(py.name)
        if c2:
            r_c2.append(py.name)
            for c in c2:
                r_cibles[c] = r_cibles.get(c, 0) + 1
        if c1 or c2:
            r_exec.append(py.name)
        net = sans_chaines(sans_commentaires(s))
        if c1 and not R_SUBPROC.search(net):
            r_citeur.append(py.name)
        if R_POPEN.search(net):
            r_popen.append(py.name)
        if R_AUTRES.search(net):
            r_autres.append(py.name)
    r_aveugle = [n for n in r_c2 if n not in r_c1]

    # --- Ce que le rapport publie ------------------------------------------
    p_analyses = compte_gras(rap, "scripts nonml_*.py analysés :")
    p_exec = compte_gras(rap, "que la règle corrigée classe « exécute un tiers » :")
    p_aveugle = compte_gras(rap, "scripts dans l'angle mort :")
    p_cibles = compte_gras(rap, "modules distincts exécutés par un tiers :")

    # --- Temoins : les noms du rapport #496 sont-ils ceux du #494 ? ---------
    def noms(txt, titre):
        bloc = txt.split(titre, 1)[-1].split("\n## ", 1)[0]
        return [m.group(1) for l in bloc.splitlines()
                if (m := re.match(r"\|\s*`([a-z0-9_]+\.py)`\s*\|", l))]
    n496 = noms(rap, "## Les quatre témoins du #494, reclassés")
    n494 = noms(lit(SRC_494), "## Les quatre mesures")
    memes = sorted(n496) == sorted(n494)

    # --- Le backtest n'execute rien : verifie ici, independamment -----------
    arbre = ast.parse(src_bt)
    appels = 0
    for n in ast.walk(arbre):
        if isinstance(n, ast.Call):
            f = n.func
            base = None
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                base = f"{f.value.id}.{f.attr}"
            if base and base.startswith("subprocess."):
                if n.args and isinstance(n.args[0], (ast.List, ast.Tuple)):
                    e = n.args[0].elts
                    if e and isinstance(e[0], ast.Attribute) and e[0].attr == "executable":
                        appels += 1
    imports_bt = [m for m, _ in R_IMPORT.findall(src_bt) if m in existants]

    # --- Chiffres en gras : interpoles ou tapes a la main ? ----------------
    en_dur = []
    for m in GRAS.finditer(rap):
        v = m.group(1).replace(" ", "").replace(" ", "")
        if re.search(r"[\"']\s*\*\*" + re.escape(v) + r"\s*\*\*", src_bt):
            en_dur.append(v)

    # --- Arbre git ----------------------------------------------------------
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — règle de détection de l'exécution (#496)")
    A("")
    A("Le backtest classe par **AST**. Cet audit reconstruit les mêmes comptes")
    A("par **expressions régulières** — une route qui ne partage aucune ligne")
    A("avec la première.")
    A("")
    A("## Recalcul par la route indépendante")
    A("")
    A("| Grandeur | Rapport | Route regex | Accord |")
    A("|---|---|---|---|")
    lignes = [("scripts analysés", p_analyses, len(fichiers)),
              ("scripts « exécute un tiers »", p_exec, len(r_exec)),
              ("angle mort du #494", p_aveugle, len(r_aveugle)),
              ("cibles distinctes", p_cibles, len(r_cibles))]
    for nom, a, b in lignes:
        ok = a == b
        A(f"| {nom} | **{a}** | **{b}** | {'**oui**' if ok else '**NON**'} |")
    A("")
    ecarts = [(n, a, b) for n, a, b in lignes if a != b]
    if ecarts:
        A("> **Désaccord entre les deux routes.** Il est publié tel quel :")
        for n, a, b in ecarts:
            A(f"> - *{n}* : AST **{a}**, regex **{b}** — écart **{abs((a or 0)-(b or 0))}**.")
        A("")
        A("**La cause est mesurée, pas invoquée.**")
        A("")
        A(f"- **{len(r_citeur)}** script(s) où le motif ne vit que dans un")
        A("  **littéral de chaîne** : la regex y voit un porteur, l'AST un")
        A("  **citeur** — c'est la distinction du #473, et l'AST a raison ;")
        A(f"- **{len(r_popen)}** script(s) appellent `subprocess.Popen([sys.executable, …])`,")
        A("  une forme que la **condition 1 ne nomme pas** : elle dit « la forme")
        A("  du #494 », et le #494 cherchait `subprocess.run`.")
        A("  **C'est un troisième angle mort — celui de ma règle corrigée** ;")
        A("- pour les **cibles**, la route regex ne collecte que celles de la")
        A("  condition 2 ; elle ignore par construction les littéraux passés à")
        A("  `subprocess` et la condition 3.")
        A("")
        A("L'implémentation du backtest accepte aussi `check_call`/`check_output`,")
        A("que le texte pré-enregistré ne nomme pas — **dépassement mesuré** :")
        A(f"scripts concernés dans le dépôt : **{len(r_autres)}**.")
        A("")
        A("> **Rien n'est reclassé ici.** La règle a été figée avant mesure ;")
        A("> `Popen` est enregistré comme angle mort, pas absorbé après coup.")
    else:
        A("> Les deux routes **concordent** sur les quatre grandeurs.")
    A("")
    A("## Les témoins sont-ils bien ceux du #494 ?")
    A("")
    A(f"- noms listés par le #496 : **{len(n496)}**")
    A(f"- noms listés par le #494 : **{len(n494)}**")
    A(f"- listes identiques : **{'OUI' if memes else 'NON'}**")
    A("")
    if not memes:
        A(f"> Écart : `{sorted(set(n496) ^ set(n494))}`")
        A("")
    A("## Le backtest exécute-t-il quelque chose ?")
    A("")
    A(f"- appels `subprocess` sur `sys.executable` dans son AST : **{appels}**")
    A(f"- modules `nonml_*` du dépôt qu'il importe : **{len(imports_bt)}**")
    A(f"- fichiers de l'arbre git modifiés hors ce cycle : **{len(sales)}**")
    A("")
    ok_exec = appels == 0 and not imports_bt and not sales
    if ok_exec:
        A("> **Rien n'a été exécuté.** Le script lit des sources et écrit son")
        A("> seul rapport ; l'arbre ne porte aucune trace d'un tiers.")
    else:
        A("> **Le script n'est pas inerte** — le détail ci-dessus le montre.")
    A("")
    A("## Les chiffres du rapport sont-ils calculés ?")
    A("")
    A(f"- nombres en gras dans le rapport : **{len(GRAS.findall(rap))}**")
    A(f"- dont **tapés en dur** dans le backtest : **{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    causes = set(r_citeur) | set(r_popen)
    gap = abs((p_exec or 0) - len(r_exec))
    borne = gap <= len(causes)
    A("")
    A("## L'écart est-il **entièrement** attribué ?")
    A("")
    A(f"- écart sur « exécute un tiers » : **{gap}**")
    A(f"- scripts porteurs d'une cause nommée (citeur ou `Popen`) : **{len(causes)}**")
    A(f"- l'écart tient dans les causes nommées : **{'OUI' if borne else 'NON'}**")
    A("")
    A("> Ce test **borne**, il n'**identifie** pas : il vérifie qu'il reste assez")
    A("> de causes nommées pour couvrir l'écart, non que ce sont les bonnes.")
    A("> Une réconciliation nom par nom exigerait la liste AST, que cet audit")
    A("> s'interdit d'utiliser pour rester indépendant. **Limite assumée.**")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("tout écart entre routes tient dans des causes nommées", borne),
            ("les témoins du #496 sont exactement ceux du #494", memes),
            ("le backtest n'exécute aucun tiers et ne salit pas l'arbre", ok_exec),
            ("aucun chiffre du rapport n'est tapé en dur", not en_dur)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}**")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : ce cycle ne lit aucune")
    A("série de prix. Son équivalent ici est **l'inertie** — vérifiée ci-dessus.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(v)


if __name__ == "__main__":
    main()

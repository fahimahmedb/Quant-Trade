"""Audit adversarial du #476 — recalcul independant.

Route differente : l'arbre syntaxique (AST) au lieu de l'expression reguliere
sur le texte. L'AST distingue nativement une chaine simple (`ast.Constant`)
d'une f-string (`ast.JoinedStr`) -- la distinction que le backtest doit
reconstituer par regex. Population et mediane recomptees separement.

Un chiffre qui ne se retrouve pas est signale, jamais aligne.
"""
import ast
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

RAPPORT = RESULTS / "nonml_hardcoded_figures_sweep_result.md"
OUT = RESULTS / "nonml_hardcoded_figures_sweep_audit.md"
MOI = "hardcoded_figures_sweep"
GRAS = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
SUFFIXES = [("_result.md", "_backtest.py"), ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]


def producteur(nom_md):
    for a, b in SUFFIXES:
        if nom_md.endswith(a):
            return SCRIPTS / f"{nom_md[:-len(a)]}{b}"
    return None


def litteraux_ast(chemin):
    """Chaines SIMPLES portant un chiffre en gras, passees a append/write/print.

    `ast.Constant` exclut d'office les f-strings (`ast.JoinedStr`) et les
    concatenations dynamiques (`ast.BinOp`) : la distinction que le backtest
    doit reconstruire par regex est ici structurelle.
    """
    try:
        arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    except SyntaxError:
        return None
    out = set()
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        nom = f.attr if isinstance(f, ast.Attribute) else \
            (f.id if isinstance(f, ast.Name) else "")
        if nom not in ("append", "write", "print", "write_text"):
            continue
        for a in n.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                    and GRAS.search(a.value):
                out.add(a.lineno)
    return sorted(out)


def main():
    rapports = sorted(p.name for p in RESULTS.glob("nonml_*.md")
                      if not p.name.endswith("_anti_cheat.md") and MOI not in p.name)
    population, hors = [], []
    for nom in rapports:
        py = producteur(nom)
        (population if (py and py.exists()) else hors).append((nom, py))

    charges, illisibles = {}, []
    for nom, py in population:
        lits = litteraux_ast(py)
        if lits is None:
            illisibles.append(py.name)
            continue
        if lits:
            charges[py.name] = len(lits)

    affectes = len(charges)
    med = statistics.median(sorted(charges.values())) if charges else 0
    top5 = [n for n, _c in sorted(charges.items(), key=lambda kv: (-kv[1], kv[0]))[:5]]

    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    def lu(m):
        g = re.search(m, pub)
        return g.group(1) if g else None

    mesures = [
        ("population (rapports avec producteur)", len(population),
         lu(r"avec script producteur sous la convention : \*\*(\d+)\*\*")),
        ("rapports hors convention", len(hors),
         lu(r"hors convention\*[^:]*: \*\*(\d+)\*\*")),
        ("scripts avec ≥ 1 littéral", affectes,
         lu(r"au moins un\*\* chiffre littéral : \*\*(\d+) /")),
        ("médiane par rapport affecté", f"{med:.1f}".replace(".", ","),
         lu(r"\*\*médiane\*\* par rapport affecté : \*\*([\d,]+)\*\*")),
        ("maximum sur un script", max(charges.values(), default=0),
         lu(r"maximum sur un seul script : \*\*(\d+)\*\*")),
    ]

    L = ["# Audit adversarial — les chiffres littéraux (#476)", ""]
    L.append("**Recalcul par une route différente** : l'**arbre syntaxique** au lieu de")
    L.append("l'expression régulière sur le texte. `ast.Constant` exclut d'office les")
    L.append("f-strings (`ast.JoinedStr`) et les concaténations (`ast.BinOp`) — **la")
    L.append("distinction que le backtest doit reconstruire par regex est ici")
    L.append("structurelle**, donc plus sûre.")
    L.append("")
    L.append("| Grandeur | Audit (AST) | Rapport (regex) | Verdict |")
    L.append("|---|---|---|---|")
    ecarts = 0
    for nom, mien, publie in mesures:
        ok = publie is not None and str(mien) == str(publie)
        ecarts += 0 if ok else 1
        L.append(f"| {nom} | **{mien}** | {publie if publie is not None else '*non relu*'}"
                 f" | {'**concordant**' if ok else '**ÉCART**'} |")
    L.append("")
    if illisibles:
        L.append(f"- scripts non analysables par l'AST *(erreur de syntaxe)* : "
                 f"**{len(illisibles)}**")
        for n in illisibles[:6]:
            L.append(f"  - `{n}`")
        L.append("")

    L.append("## L'échantillon est-il bien le bon ?")
    L.append("")
    L.append("La règle pré-enregistrée : **les 5 plus chargés**, ex æquo par ordre")
    L.append("alphabétique. Recalculée par l'AST :")
    L.append("")
    for n in top5:
        cite = f"`{n}`" in pub
        L.append(f"- `{n}` (**{charges[n]}**) — examiné dans le rapport : "
                 f"**{'oui' if cite else 'NON'}**")
    L.append("")
    manquants = [n for n in top5 if f"`{n}`" not in pub]
    if not manquants:
        L.append("**Les cinq que l'AST désigne sont ceux que le rapport examine.**")
        L.append("La règle d'échantillonnage n'a pas dérivé entre les deux routes.")
    else:
        L.append(f"**{len(manquants)} script(s) désigné(s) par l'AST ne sont pas")
        L.append("examinés dans le rapport** — écart publié tel quel.")
    L.append("")

    L.append("## Un contrôle que le backtest ne fait pas")
    L.append("")
    L.append("Les littéraux sont-ils dans des **lignes de tableau** (`| … |`) ou dans")
    L.append("de la **prose** ? Un tableau porte plus souvent un résultat, la prose")
    L.append("plus souvent une citation. **Ce n'est pas un test de culpabilité** —")
    L.append("seulement un indice structurel, et il est publié comme tel.")
    L.append("")
    tab = pro = 0
    for nom, py in population:
        try:
            src = py.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        for ln in src.splitlines():
            if GRAS.search(ln) and (".append(" in ln or ".write(" in ln):
                if re.search(r"[\"']\s*\|", ln):
                    tab += 1
                else:
                    pro += 1
    L.append(f"- littéraux en **ligne de tableau** : **{tab}**")
    L.append(f"- littéraux en **prose** : **{pro}**")
    L.append("")

    L.append("## Effets de bord du backtest")
    L.append("")
    bt = (SCRIPTS / f"nonml_{MOI}_backtest.py").read_text(encoding="utf-8")
    dangers = re.findall(r"(checkout|subprocess|rm\s|unlink|open\s*\([^)]*[\"']w)", bt)
    L.append(f"- écritures : **{bt.count('write_text')}** (`OUT` seul)")
    L.append(f"- `subprocess` / `checkout` / suppression : **{len(dangers)}**")
    L.append("")
    L.append("**Aucun effet de bord — le script ne fait que lire le disque.**"
             if not dangers else f"**À examiner : {dangers}**")
    L.append("")

    L.append("## Verdict")
    L.append("")
    L.append(f"**{'CONCORDANT' if ecarts == 0 else 'DISCORDANT'}** — "
             f"**{len(mesures) - ecarts}/{len(mesures)}** grandeurs se retrouvent par")
    L.append("une route indépendante.")
    if ecarts:
        L.append("")
        L.append("**Les écarts sont publiés tels quels, pas alignés.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

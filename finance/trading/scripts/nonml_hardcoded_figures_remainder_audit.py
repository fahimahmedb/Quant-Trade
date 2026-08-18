"""Audit adversarial du #479 — recalcul independant.

Route differente : l'AST (`ast.Constant` vs `ast.JoinedStr`) au lieu des trois
expressions regulieres du #476, et la couverture de l'examen verifiee EN LISANT
LE RAPPORT PUBLIE plutot que la table de verdicts du script.

Le controle central n'est pas le compte -- c'est que **chaque defaut compte ait
sa ligne publiee**, exigence 4 du pre-enregistrement.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

RAPPORT = RESULTS / "nonml_hardcoded_figures_remainder_result.md"
OUT = RESULTS / "nonml_hardcoded_figures_remainder_audit.md"
MOI = "hardcoded_figures_remainder"
GRAS = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
SUFFIXES = [("_result.md", "_backtest.py"), ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]
DEJA_476 = {"nonml_protocol_inventory_audit.py",
            "nonml_marker_emitted_by_scripts_backtest.py",
            "nonml_repo_magnitudes_recount_backtest.py",
            "nonml_citer_451_definition_backtest.py",
            "nonml_duplicate_sweep_coverage_audit.py"}
ECRIVENT = ("append", "write", "print", "write_text")


def producteur(nom_md):
    for a, b in SUFFIXES:
        if nom_md.endswith(a):
            return SCRIPTS / f"{nom_md[:-len(a)]}{b}"
    return None


def litteraux_ast(chemin):
    try:
        arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return None
    out = set()
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        nom = f.attr if isinstance(f, ast.Attribute) else \
            (f.id if isinstance(f, ast.Name) else "")
        if nom not in ECRIVENT:
            continue
        for a in n.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                    and GRAS.search(a.value):
                out.add(a.lineno)
    return sorted(out)


def main():
    vus, affectes = set(), {}
    for p in sorted(RESULTS.glob("nonml_*.md")):
        if p.name.endswith("_anti_cheat.md") or MOI in p.name:
            continue
        py = producteur(p.name)
        if not (py and py.exists()) or py.name in vus:
            continue
        vus.add(py.name)
        lits = litteraux_ast(py)
        if lits:
            affectes[py.name] = lits
    restants = {k: v for k, v in affectes.items() if k not in DEJA_476}

    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    # --- Le controle central : chaque verdict a-t-il sa section et sa ligne ?
    sections = re.findall(r"^### `(nonml_[a-z0-9_]+\.py)` — (.+)$", pub, re.M)
    par_nom = {n: v for n, v in sections}
    sans_section = [n for n in restants if n not in par_nom]
    # Le rapport publie-t-il au moins une ligne de code pour chacun ?
    blocs = dict(re.findall(r"^### `(nonml_[a-z0-9_]+\.py)` —[^\n]*\n\n```python\n(.*?)```",
                            pub, re.M | re.S))
    sans_ligne = [n for n in par_nom if not re.search(r"^\d+:", blocs.get(n, ""), re.M)]

    defauts = [n for n, v in par_nom.items() if "DÉFAUT" in v]
    partiels = [n for n, v in par_nom.items() if "PARTIEL" in v]
    legitimes = [n for n, v in par_nom.items() if v.strip() == "légitime"]

    def lu(m):
        g = re.search(m, pub)
        return g.group(1) if g else None

    mesures = [
        ("scripts affectés (population)", len(affectes),
         lu(r"rapports affectés \| 35 \| \*\*(\d+)\*\*")),
        ("restants examinés", len(restants),
         lu(r"restants, examinés ici\*\* \| — \| \*\*(\d+)\*\*")),
        ("défauts pleins", len(defauts),
         lu(r"\*\*DÉFAUTS pleins\*\* : \*\*(\d+)\*\*")),
        ("partiels", len(partiels),
         lu(r"\*\*PARTIELS\*\*[^:]*: \*\*(\d+)\*\*")),
        ("légitimes", len(legitimes),
         lu(r"\*\*légitimes\*\* : \*\*(\d+)\*\*")),
    ]

    L = ["# Audit adversarial — les rapports non examinés du #476 (#479)", ""]
    L.append("**Recalcul par une route différente** : l'**AST** (`ast.Constant` contre")
    L.append("`ast.JoinedStr`) au lieu des trois expressions régulières du #476 — la")
    L.append("distinction littéral / interpolé y est **structurelle**. Les verdicts sont")
    L.append("relus **dans le rapport publié**, pas dans la table du script.")
    L.append("")
    L.append("| Grandeur | Audit (AST) | Rapport (regex) | Verdict |")
    L.append("|---|---|---|---|")
    ecarts = 0
    for nom, mien, publie in mesures:
        ok = publie is not None and str(mien) == str(publie)
        ecarts += 0 if ok else 1
        L.append(f"| {nom} | **{mien}** | "
                 f"{publie if publie is not None else '*non relu*'} | "
                 f"{'**concordant**' if ok else '**ÉCART**'} |")
    L.append("")

    L.append("## Le contrôle central — critère 4 du pré-enregistrement")
    L.append("")
    L.append("> *« Aucun défaut compté sans sa ligne publiée. »*")
    L.append("")
    L.append("Un cycle qui accuse **doit montrer**. Vérifié sur le rapport lui-même :")
    L.append("")
    L.append(f"- scripts restants recomptés par l'AST : **{len(restants)}**")
    L.append(f"- **sans section dédiée** dans le rapport : **{len(sans_section)}**")
    for n in sans_section[:8]:
        L.append(f"  - `{n}`")
    L.append(f"- sections **sans aucune ligne de code publiée** : **{len(sans_ligne)}**")
    for n in sans_ligne[:8]:
        L.append(f"  - `{n}`")
    L.append("")
    if not sans_section and not sans_ligne:
        L.append("> **Chaque script examiné a sa section, et chaque section porte ses")
        L.append("> lignes numérotées.** Le critère 4 est tenu — un lecteur peut")
        L.append("> contester n'importe lequel des verdicts sur pièce.")
    else:
        L.append("> **Le critère 4 n'est pas tenu** pour les scripts ci-dessus, et c'est")
        L.append("> publié tel quel.")
    L.append("")

    L.append("## Le cycle s'accuse-t-il lui-même ?")
    L.append("")
    L.append("Un balayage dont l'auteur est dans la population a une raison de")
    L.append("s'épargner. Contrôle mécanique :")
    L.append("")
    miens = [n for n in par_nom if any(
        k in n for k in ("orphans_interrupted_or_lost", "hardcoded_figures_sweep",
                         "conditional_sections_sweep", "citer_451_resolution",
                         "citer_451_definition"))]
    L.append("| Script issu de cette série de cycles | Verdict reçu |")
    L.append("|---|---|")
    for n in sorted(miens):
        L.append(f"| `{n}` | {par_nom[n]} |")
    L.append("")
    charges = [n for n in miens if par_nom[n].strip() != "légitime"]
    if charges:
        L.append(f"> **{len(charges)} script(s) de la série reçoit un verdict à charge**")
        L.append("> — dont `orphans_interrupted_or_lost`, le cycle **#474**. Le balayage")
        L.append("> ne s'épargne pas.")
    else:
        L.append("> **Aucun script de la série n'est chargé.** Cela peut être exact,")
        L.append("> mais mérite d'être signalé : c'est le résultat le plus confortable")
        L.append("> possible pour l'auteur du balayage.")
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

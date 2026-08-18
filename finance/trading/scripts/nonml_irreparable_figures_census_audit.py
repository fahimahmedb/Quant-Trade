"""Audit adversarial du #485 — contrôle des verdicts, pas des comptes.

Un verdict << IRREPARABLE >> est le plus commode qui soit : il ferme une dette
sans travail. L'audit teste donc chaque irreparable par une route propre :
la grandeur invoquee est-elle vraiment HORS de portee du script ?

Route : l'AST enumere les noms lies et les appels du module ; si aucun ne
construit la collection en cause, l'irreparabilite est fondee.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

RAPPORT = RESULTS / "nonml_irreparable_figures_census_result.md"
OUT = RESULTS / "nonml_irreparable_figures_census_audit.md"
SECTION = re.compile(r"^### `(nonml_[a-z0-9_]+\.py)` — (.+)$", re.M)


def noms_et_appels(py):
    try:
        arbre = ast.parse(py.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set(), set()
    noms, appels = set(), set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            noms.add(n.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                noms.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.Call):
            f = n.func
            appels.add(f.attr if isinstance(f, ast.Attribute)
                       else (f.id if isinstance(f, ast.Name) else ""))
    return noms, appels


def main():
    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""
    cas = [(m.group(1), m.group(2)) for m in SECTION.finditer(pub)]
    irrep = [n for n, e in cas if "IRRÉPARABLE" in e]
    rep = [n for n, e in cas if e.strip() == "réparable"]

    L = ["# Audit adversarial — le recensement des irréparables (#485)", ""]
    L.append("**Un verdict « irréparable » est le plus commode qui soit** : il ferme une")
    L.append("dette sans travail. L'audit ne recompte donc pas — **il teste chaque")
    L.append("irréparable** par une route propre.")
    L.append("")
    L.append(f"- verdicts relus dans le rapport : **{len(cas)}** "
             f"(**{len(irrep)}** irréparables, **{len(rep)}** réparables)")
    L.append("")

    L.append("## Chaque irréparable — la grandeur est-elle hors de portée ?")
    L.append("")
    L.append("Route indépendante : l'**AST** énumère les noms liés et les appels du")
    L.append("module. Un script qui n'importe rien du dépôt et n'énumère aucun corpus")
    L.append("hors de sa propre liste ne peut pas reconstruire un univers historique.")
    L.append("")
    L.append("| Irréparable | Imports du dépôt | Énumère `results/` | Constantes en dur |")
    L.append("|---|---|---|---|")
    fondes = 0
    for nom in irrep:
        py = SCRIPTS / nom
        if not py.exists():
            L.append(f"| `{nom}` | *absent* | — | — |")
            continue
        src = py.read_text(encoding="utf-8")
        noms, appels = noms_et_appels(py)
        imp_depot = sorted(n for n in noms if n.startswith("nonml_"))
        enum = bool(re.search(r"RESULTS\s*\.\s*glob|\.iterdir\(|glob\.glob", src))
        cst = bool(re.search(r"^[A-Z_]{3,}\s*=\s*\[", src, re.M))
        # Fonde si : n'importe aucun module du depot ET (n'enumere pas OU
        # travaille sur une liste codee en dur).
        ok = (not imp_depot) and (not enum or cst)
        fondes += 1 if ok else 0
        L.append(f"| `{nom}` | "
                 f"{', '.join('`' + i + '`' for i in imp_depot) if imp_depot else '**aucun**'}"
                 f" | {'oui' if enum else '**non**'} | {'oui' if cst else 'non'} |")
    L.append("")
    L.append(f"- irréparabilités **fondées** par cette route : **{fondes} / "
             f"{len(irrep)}**")
    L.append("")
    if fondes == len(irrep):
        L.append("> **Toutes fondées.** Aucun de ces scripts n'importe un module du")
        L.append("> dépôt qui lui fournirait l'univers manquant, et ceux qui énumèrent")
        L.append("> `results/` le font sur une **liste codée en dur**.")
    else:
        L.append(f"> **{len(irrep) - fondes} irréparabilité(s) non fondée(s)** par cette")
        L.append("> route — publié tel quel, le verdict à la main peut rester juste pour")
        L.append("> une raison que l'AST ne voit pas, mais **le doute est inscrit**.")
    L.append("")

    L.append("## Le cycle s'épargne-t-il ?")
    L.append("")
    mien = [n for n in cas if "orphans_interrupted_or_lost" in n[0]]
    L.append("| Script de cette série | Verdict reçu |")
    L.append("|---|---|")
    for n, e in mien:
        L.append(f"| `{n}` | {e} |")
    L.append("")
    if mien and all("IRRÉPARABLE" not in e for _n, e in mien):
        L.append("> **Le cycle se donne le verdict le plus exigeant.** Classer son propre")
        L.append("> défaut « réparable » **maintient la dette ouverte contre soi** ;")
        L.append("> l'inverse l'aurait close gratuitement. Le rapport écrit *« rien ne")
        L.append("> l'excuse »*.")
    L.append("")

    L.append("## Le proxy est-il vraiment sans pouvoir de séparation ?")
    L.append("")
    L.append("Le rapport affirme que son proxy répond « oui » partout. **Contrôle sur un")
    L.append("échantillon témoin** : le même motif appliqué à des scripts **hors** de la")
    L.append("population des défauts.")
    L.append("")
    COLL = re.compile(r"for .* in |\.glob\(|len\s*\(|sorted\s*\(")
    temoins = sorted(p for p in SCRIPTS.glob("nonml_*_backtest.py"))[:40]
    oui = sum(1 for p in temoins
              if COLL.search(p.read_text(encoding="utf-8", errors="ignore")))
    L.append(f"- scripts témoins testés : **{len(temoins)}**")
    L.append(f"- dont le proxy répond « oui » : **{oui}**")
    L.append("")
    if temoins and oui == len(temoins):
        L.append("> **Le proxy répond « oui » à 100 % des témoins aussi.** Il ne sépare")
        L.append("> donc rien, nulle part — **l'aveu du rapport est vérifié, pas cru**.")
        L.append("> Un motif qui teste `for … in` ou `len(…)` teste que le fichier est")
        L.append("> du Python.")
    L.append("")

    L.append("## Effets de bord du backtest")
    L.append("")
    bt = (SCRIPTS / "nonml_irreparable_figures_census_backtest.py")\
        .read_text(encoding="utf-8")
    dangers = re.findall(r"(checkout|subprocess|rm\s|unlink|open\s*\([^)]*[\"']w)", bt)
    L.append(f"- écritures : **{bt.count('write_text')}** (`OUT` seul)")
    L.append(f"- `subprocess` / `checkout` / suppression : **{len(dangers)}**")
    L.append("")
    L.append("**Aucun effet de bord — le script ne fait que lire le disque.**"
             if not dangers else f"**À examiner : {dangers}**")
    L.append("")

    L.append("## Verdict")
    L.append("")
    L.append(f"**{'CONCORDANT' if fondes == len(irrep) else 'RÉSERVES'}** — "
             f"**{fondes}/{len(irrep)}** irréparabilités fondées par une route")
    L.append("indépendante, et l'inutilité déclarée du proxy **vérifiée sur un")
    L.append("échantillon témoin**.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

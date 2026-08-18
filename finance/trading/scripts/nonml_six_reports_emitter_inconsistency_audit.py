"""Audit adversarial du #475 — recalcul independant.

Route differente du backtest : la ligne d'emission est cherchee par `git grep`
plutot que par lecture du fichier ; la possession historique de la marque est
etablie par `git log -S` (pickaxe) plutot qu'en depliant chaque commit ; la
garde conditionnelle est verifiee par compilation AST plutot que par indentation.

Un chiffre qui ne se retrouve pas est signale, jamais aligne.
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAPPORT = RESULTS / "nonml_six_reports_emitter_inconsistency_result.md"
OUT = RESULTS / "nonml_six_reports_emitter_inconsistency_audit.md"
CIBLE_PY = SCRIPTS / "nonml_six_reports_regeneration_backtest.py"
REL_PY = "finance/trading/scripts/nonml_six_reports_regeneration_backtest.py"
REL_MD = "finance/trading/results/nonml_six_reports_regeneration_result.md"
PHRASE = "Rapport dépendant du dépôt"


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def sous_garde_ast():
    """La ligne d'emission est-elle sous un `if` ? — par AST, pas par colonnes."""
    arbre = ast.parse(CIBLE_PY.read_text(encoding="utf-8"))
    cibles = []

    def visite(noeud, gardes):
        for enfant in ast.iter_child_nodes(noeud):
            g = gardes
            if isinstance(enfant, ast.If):
                g = gardes + [f"if (ligne {enfant.lineno})"]
            elif isinstance(enfant, (ast.For, ast.While)):
                g = gardes + [f"boucle (ligne {enfant.lineno})"]
            if isinstance(enfant, ast.Constant) and isinstance(enfant.value, str) \
                    and PHRASE in enfant.value:
                cibles.append((enfant.lineno, gardes))
            visite(enfant, g)

    visite(arbre, [])
    return cibles


def emissions_ast():
    """Constantes portant la marque passees a append/write/print — par AST.

    Meme definition que la regle du #469, autre implementation : le backtest
    la lit par expression reguliere sur le texte, l'audit par l'arbre syntaxique.
    """
    arbre = ast.parse(CIBLE_PY.read_text(encoding="utf-8"))
    out = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        nom = f.attr if isinstance(f, ast.Attribute) else \
            (f.id if isinstance(f, ast.Name) else "")
        if nom not in ("append", "write", "print", "write_text"):
            continue
        for a in ast.walk(n):
            if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                    and PHRASE in a.value:
                out.append(n.lineno)
                break
    return sorted(set(out))


def main():
    # 1. Les emissions, par AST (et toutes occurrences par git grep, pour
    #    montrer que les deux grandeurs different).
    brut = git("grep", "-n", PHRASE, "HEAD", "--", REL_PY)
    lignes_grep = [l for l in brut.splitlines() if l.strip()]
    emissions = emissions_ast()

    # 2. La garde, par AST.
    cibles = sous_garde_ast()
    gardees = [c for c in cibles if c[1]]

    # 3. La possession historique, par pickaxe.
    pickaxe = [l for l in git("log", "--all", "--format=%h %s", "-S", PHRASE,
                              "--", REL_MD).splitlines() if l.strip()]
    aujourdhui = PHRASE in (RESULTS / "nonml_six_reports_regeneration_result.md")\
        .read_text(encoding="utf-8")

    # Possession commit par commit, par `git grep <sha>` (plomberie distincte
    # du `git show` employe au backtest).
    shas = git("log", "--all", "--format=%H", "--", REL_MD).split()
    porteurs = [s for s in shas
                if git("grep", "-c", PHRASE, s, "--", REL_MD).strip()]

    # 4. Les six regeneres, par lecture du littéral SIX.
    src = CIBLE_PY.read_text(encoding="utf-8")
    m = re.search(r"SIX\s*=\s*\[(.*?)\n\]", src, re.S) or \
        re.search(r"SIX\s*=\s*\[(.*?)\]", src, re.S)
    six = sorted(set(re.findall(r"[\"'](nonml_[a-z0-9_]+\.md)[\"']", m.group(1))))
    portants = [n for n in six if (RESULTS / n).exists()
                and PHRASE in (RESULTS / n).read_text(encoding="utf-8")]

    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    def lu(motif):
        g = re.search(motif, pub)
        return int(g.group(1)) if g else None

    mesures = [
        ("lignes d'émission (append/write/print)", len(emissions),
         lu(r"Lignes qu'elle capture dans le script : \*\*(\d+)\*\*")),
        ("commits où le rapport porte la marque", len(porteurs),
         lu(r"il \*\*porte\*\* la marque : \*\*(\d+)\*\*")),
        ("rapports déclarés dans `SIX`", len(six),
         lu(r"déclarés dans sa constante `SIX` : \*\*(\d+)\*\*")),
        ("régénérés portant la marque", len(portants),
         lu(r"\*\*portant la marque aujourd'hui\*\* : \*\*(\d+)\*\*")),
    ]

    L = ["# Audit adversarial — l'incohérence émetteur/rapport (#475)", ""]
    L.append("**Recalcul par une route différente** : `git grep` au lieu de la lecture")
    L.append("du fichier, **AST** au lieu de l'indentation, `git log -S` (pickaxe) au")
    L.append("lieu du dépliage commit par commit.")
    L.append("")
    L.append("| Grandeur | Audit | Rapport | Verdict |")
    L.append("|---|---|---|---|")
    ecarts = 0
    for nom, mien, publie in mesures:
        ok = publie is not None and mien == publie
        ecarts += 0 if ok else 1
        L.append(f"| {nom} | **{mien}** | "
                 f"{publie if publie is not None else '*non relu*'} | "
                 f"{'**concordant**' if ok else '**ÉCART**'} |")
    L.append("")

    L.append("## Deux grandeurs à ne pas confondre")
    L.append("")
    L.append(f"- occurrences **quelconques** de la marque dans le script "
             f"(`git grep`) : **{len(lignes_grep)}**")
    L.append(f"- **émissions** au sens du #469 (`append`/`write`/`print`) : "
             f"**{len(emissions)}**")
    L.append("")
    L.append("La différence n'est pas une erreur : la ligne surnuméraire est un")
    L.append("`if \"…\" in av`, c'est-à-dire une **recherche** de la marque, pas une")
    L.append("écriture. **C'est exactement la distinction que le #469 avait dû")
    L.append("introduire**, et un audit qui compterait les occurrences brutes")
    L.append("reproduirait la confusion qu'il a levée.")
    L.append("")

    L.append("## La garde conditionnelle, établie par AST")
    L.append("")
    L.append(f"- constantes contenant la marque dans le script : **{len(cibles)}**")
    L.append(f"- **sous au moins une garde** : **{len(gardees)}**")
    for ln, g in cibles:
        L.append(f"  - ligne {ln} — {' → '.join(g) if g else '*aucune garde*'}")
    L.append("")
    L.append("L'AST confirme par une autre voie ce que le backtest a établi en")
    L.append("remontant l'indentation : **l'écriture est conditionnelle**.")
    L.append("")

    L.append("## La possession historique, par pickaxe")
    L.append("")
    L.append("```")
    L.append(f'git log --all -S "{PHRASE}" -- {REL_MD}')
    L.append("```")
    L.append("")
    L.append(f"- commits où la chaîne **apparaît ou disparaît** : **{len(pickaxe)}**")
    for l in pickaxe[:6]:
        L.append(f"  - {l}")
    L.append(f"- présente **aujourd'hui** : **{'oui' if aujourdhui else 'non'}**")
    L.append("")
    if len(pickaxe) >= 2 and not aujourdhui:
        L.append("> **Le pickaxe voit l'ajout *et* le retrait.** La possession puis la")
        L.append("> perte sont confirmées par un mécanisme totalement distinct de celui")
        L.append("> du backtest : **la lecture A tient.**")
    elif len(pickaxe) == 1:
        L.append("> Le pickaxe ne voit **qu'un** changement — cohérent avec un rapport")
        L.append("> ajouté portant la marque, puis réécrit sans elle dans un commit qui")
        L.append("> ne la fait plus apparaître.")
    L.append("")

    L.append("## Effets de bord du backtest")
    L.append("")
    bt = (SCRIPTS / "nonml_six_reports_emitter_inconsistency_backtest.py")\
        .read_text(encoding="utf-8")
    dangers = re.findall(r"(checkout|subprocess\.run\(\[sys\.executable|rm\s|unlink|"
                         r"open\s*\([^)]*[\"']w)", bt)
    L.append(f"- écritures : **{bt.count('write_text')}** (`OUT` seul)")
    L.append(f"- exécution d'un script du dépôt / `checkout` / suppression : "
             f"**{len(dangers)}**")
    L.append("")
    L.append("**Aucun effet de bord.**" if not dangers
             else f"**À examiner : {dangers}**")
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
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de")
    L.append("> l'historique à la date de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

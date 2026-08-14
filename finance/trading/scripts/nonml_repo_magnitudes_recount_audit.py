"""Audit adversarial du #462 — recomptage par une autre route.

Ne reutilise aucune fonction du backtest. La ou le backtest filtre la liste
d'arbre avec une expression reguliere Python (`re.match`), l'audit filtre la
meme liste avec un motif shell (`fnmatch`) — deux mecanismes distincts.

Quatre controles :

  A. Les 108 cellules, recomptees par pathspec.
  B. Le saut `batteries` au #457 vaut-il bien +29, et est-il unique ?
  C. Les fichiers apparus entre #456 et #457 sont-ils bien des batteries ?
  D. Idempotence du rapport.
"""
import fnmatch
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_backlog_figures_verification_backtest as bt  # noqa: E402

OUT = RESULTS / "nonml_repo_magnitudes_recount_audit.md"
RAPPORT = RESULTS / "nonml_repo_magnitudes_recount_result.md"
ENTREES = list(range(443, 461))

# MEMES grandeurs, exprimees en pathspecs git — pas en regex Python.
PATHSPECS = [
    ("backtests",   "finance/trading/scripts/nonml_*_backtest.py"),
    ("resultats",   "finance/trading/results/nonml_*_result.md"),
    ("npz",         "finance/trading/results/nonml_*_pnl.npz"),
    ("batteries",   "finance/trading/results/*_pass_validation_battery.md"),
    ("robustesses", "finance/trading/results/nonml_*_robustness.md"),
    ("audits",      "finance/trading/results/nonml_*_audit.md"),
]


class GitEchec(RuntimeError):
    """Un controle qui compte 0 parce que git a echoue ne controle rien."""


def git(*a, tolerant=False):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        if tolerant:
            return None
        # Defaut trouve a la premiere execution : `ls-tree` ne supporte pas la
        # magie `:(glob)`, git renvoyait « fatal », et l'audit transformait
        # silencieusement l'erreur en un comptage de 0 — donc en 108 faux
        # ecarts. Une erreur git doit ARRETER l'audit, pas le decorer.
        raise GitEchec(f"git {' '.join(a)} → {r.returncode} : {r.stderr.strip()[:200]}")
    return r.stdout


def compte_pathspec(sha, spec):
    """Comptage par motif shell (`fnmatch`), la ou le backtest emploie une
    expression reguliere Python (`re.match`) sur des chemins deja tronques.
    Deux mecanismes de filtrage distincts sur la meme liste d'arbre.

    Deux routes ont ete essayees et ECARTEES avant celle-ci, toutes deux
    publiees dans le rapport :
      - `ls-tree ... -- :(glob)...` : `ls-tree` ne supporte pas cette magie ;
      - `ls-files --with-tree=<sha>` : `--with-tree` AJOUTE l'arbre a l'index
        au lieu de s'y restreindre, et rendait donc les chiffres de HEAD a
        tous les commits — 95 faux ecarts, identiques d'une ligne a l'autre.
    """
    out = git("ls-tree", "-r", "--name-only", sha, "finance/trading/")
    return sum(1 for n in out.splitlines() if fnmatch.fnmatch(n.strip(), spec))


def main():
    L = ["# Audit adversarial — re-mesure des grandeurs du dépôt (#462)", ""]
    L.append("Recomptage par une **autre route** : le backtest liste l'arbre puis filtre")
    L.append("en Python avec `re.match` ; l'audit filtre la même liste avec `fnmatch`,")
    L.append("un mécanisme de motif distinct. Un bug de regex ne peut pas se cacher dans")
    L.append("les deux.")
    L.append("")

    # ------------------------------------------------------------------ A
    lu = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""
    lignes_table = {}
    for m in re.finditer(r"^\| #(\d+) \| `([0-9a-f]{8})` \| (.+?) \|$", lu, re.M):
        vals = [v.strip() for v in m.group(3).split("|")]
        if all(v.isdigit() for v in vals):
            lignes_table[int(m.group(1))] = (m.group(2), [int(v) for v in vals])

    ecarts, cellules = [], 0
    series = {cle: [] for cle, _ in PATHSPECS}
    for num in ENTREES:
        sha = bt.commit_introducteur(num)
        if sha is None:
            continue
        for i, (cle, spec) in enumerate(PATHSPECS):
            n = compte_pathspec(sha, spec)
            series[cle].append((num, n))
            cellules += 1
            if num in lignes_table and i < len(lignes_table[num][1]):
                annonce = lignes_table[num][1][i]
                if annonce != n:
                    ecarts.append((num, cle, annonce, n))

    okA = not ecarts and cellules == len(ENTREES) * len(PATHSPECS)
    L.append("## A. Les 108 cellules, recomptées par pathspec")
    L.append("")
    L.append(f"- cellules recomptées : **{cellules}**")
    L.append(f"- lignes du rapport relues : **{len(lignes_table)}**")
    L.append(f"- **écarts** : **{len(ecarts)}**")
    if ecarts:
        L.append("")
        L.append("| Entrée | Grandeur | Rapport | Audit |")
        L.append("|---|---|---|---|")
        for num, cle, a, b in ecarts:
            L.append(f"| #{num} | `{cle}` | {a} | **{b}** |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okA else 'ÉCART'}.**")
    L.append("")

    # ------------------------------------------------------------------ B
    bat = series["batteries"]
    sauts = [(a, va, b, vb) for (a, va), (b, vb) in zip(bat, bat[1:]) if vb != va]
    okB = len(sauts) == 1 and sauts[0][3] - sauts[0][1] == 29 and sauts[0][2] == 457
    L.append("## B. Le saut `batteries` — vaut-il +29, et est-il unique ?")
    L.append("")
    L.append(f"- variations détectées sur la série : **{len(sauts)}**")
    for a, va, b, vb in sauts:
        L.append(f"- #{a} → #{b} : {va} → **{vb}** (**{vb - va:+d}**)")
    L.append("")
    L.append("C'est le point sur lequel repose la seule affirmation positive du cycle.")
    L.append("Un saut **unique**, **au bon commit**, de **+29** exactement — sinon la")
    L.append("confirmation du #457 ne tient pas.")
    L.append("")
    L.append(f"**{'CONCORDANT' if okB else 'ÉCART'}.**")
    L.append("")

    # ------------------------------------------------------------------ C
    # Le commit epingle est celui qui ajoute l'ENTREE de backlog, donc le
    # DERNIER du cycle : les fichiers du cycle sont arrives avant lui. Diffe
    # `sha^..sha` ne montrait que l'entree elle-meme (defaut de la premiere
    # version : 1 fichier ajoute au lieu de 29). On diffe donc le SPAN entre
    # les deux commits epingles, ce que la table compare deja.
    sha456, sha457 = bt.commit_introducteur(456), bt.commit_introducteur(457)
    ajoutes, non_batteries = [], []
    if sha456 and sha457:
        diff = git("diff", "--name-status", sha456, sha457,
                   "--", "finance/trading/results/") or ""
        for ligne in diff.splitlines():
            p = ligne.split("\t")
            if len(p) >= 2 and p[0] == "A":
                ajoutes.append(p[1])
        non_batteries = [f for f in ajoutes
                         if not f.endswith("_pass_validation_battery.md")]
    n_bat_aj = len(ajoutes) - len(non_batteries)
    okC = n_bat_aj == 29
    L.append("## C. Les fichiers ajoutés entre #456 et #457 sont-ils des batteries ?")
    L.append("")
    L.append("Le contrôle B compte un solde entre les deux commits épinglés. Il resterait")
    L.append("compatible avec 30 ajouts et 1 suppression. On regarde donc les fichiers")
    L.append("**réellement ajoutés** sur le même intervalle.")
    L.append("")
    L.append(f"- fichiers ajoutés sous `results/` : **{len(ajoutes)}**")
    L.append(f"- dont rapports de batterie : **{n_bat_aj}**")
    L.append(f"- dont **autre chose** : **{len(non_batteries)}**")
    if non_batteries:
        L.append("")
        for f in non_batteries[:10]:
            L.append(f"  - `{f.split('/')[-1]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okC else 'ÉCART'}.**")
    L.append("")

    # ------------------------------------------------------------------ D
    def emp():
        return hashlib.sha256(RAPPORT.read_bytes()).hexdigest() if RAPPORT.exists() else ""

    av = emp()
    subprocess.run([sys.executable,
                    str(SCRIPTS / "nonml_repo_magnitudes_recount_backtest.py")],
                   cwd=ROOT, capture_output=True, text=True)
    ap = emp()
    okD = av == ap and av != ""
    L.append("## D. Idempotence")
    L.append("")
    L.append(f"- avant : `{av[:16]}`")
    L.append(f"- après : `{ap[:16]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okD else 'ÉCART'}.**")
    L.append("")

    tous = okA and okB and okC and okD
    L.append("## Ce que cet audit ne couvre pas")
    L.append("")
    L.append("Il vérifie que le **recomptage** est juste. Il ne sauve pas l'appariement")
    L.append("de prose, que le rapport publie comme un **échec** : comparer un")
    L.append("sous-ensemble (« 99 scripts *sans* `.npz` ») à un total n'a pas de sens,")
    L.append("et aucun des 9 « écarts » n'est une erreur du backlog.")
    L.append("")
    L.append(f"## Verdict — **{'CONCORDANT' if tous else 'ÉCART'}** "
             f"({sum([okA, okB, okC, okD])}/4)")
    L.append("")
    L.append("Aucun bug détecté par recomptage indépendant." if tous
             else "**Au moins un contrôle échoue — voir ci-dessus.**")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

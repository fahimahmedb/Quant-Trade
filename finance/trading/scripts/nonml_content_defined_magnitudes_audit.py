"""Audit adversarial du #465 — recompter par `git grep`.

Route franchement distincte : le backtest fait un `git show` par fichier et
filtre en Python ; l'audit delegue la recherche de contenu a `git grep` sur
l'arbre du commit. Un bug de lecture Python ne peut pas se cacher dans les deux.

  A. G1 recompte aux 18 commits.
  B. La decomposition du #449 : 2 scripts d'instrument, 6 consommateurs ?
  C. La limite avouee du backtest : porteurs et citeurs sont-ils vraiment
     indiscernables ? On cherche le script EMETTEUR, ce que le #451 avait.
  D. Idempotence de mon propre rapport (lecon du #463).
"""
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

OUT = RESULTS / "nonml_content_defined_magnitudes_audit.md"
RAPPORT = RESULTS / "nonml_content_defined_magnitudes_result.md"
ENTREES = list(range(443, 461))


def git(*a, ok=(0,)):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode in ok else None


def grep_l(sha, motif, chemin):
    """Fichiers du commit dont le contenu contient le motif. `git grep`
    renvoie 1 quand il ne trouve rien : ce n'est pas une erreur."""
    out = git("grep", "-l", "-e", motif, sha, "--", chemin, ok=(0, 1)) or ""
    return sorted(l.split(":", 1)[1] for l in out.splitlines() if ":" in l)


def main():
    lu = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    # ---------------------------------------------------------------- A
    annonces = {}
    for m in re.finditer(r"^\| #(\d+) \| `[0-9a-f]{8}` \| (\d+) \| (\d+) \|",
                         lu, re.M):
        annonces[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))

    ecarts, mesures = [], {}
    for num in ENTREES:
        sha = bt.commit_introducteur(num)
        if sha is None:
            continue
        f = grep_l(sha, r"^\s*\(import\|from\)\s\+nonml_verdict",
                   "finance/trading/scripts/")
        mesures[num] = f
        if num in annonces and annonces[num][0] != len(f):
            ecarts.append((num, annonces[num][0], len(f)))

    okA = not ecarts and len(mesures) == len(ENTREES)

    L = ["# Audit adversarial — grandeurs définies par le contenu (#465)", ""]
    L.append("Route distincte : le backtest fait un `git show` par fichier et filtre en")
    L.append("Python ; l'audit délègue la recherche à **`git grep`** sur l'arbre du")
    L.append("commit.")
    L.append("")
    L.append("## A. G1 recompté aux 18 commits")
    L.append("")
    L.append(f"- commits recomptés : **{len(mesures)}**")
    L.append(f"- lignes du rapport relues : **{len(annonces)}**")
    L.append(f"- **écarts** : **{len(ecarts)}**")
    if ecarts:
        L.append("")
        L.append("| Entrée | Rapport | Audit |")
        L.append("|---|---|---|")
        for num, a, b in ecarts:
            L.append(f"| #{num} | {a} | **{b}** |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okA else 'ÉCART'}.**")
    L.append("")

    # ---------------------------------------------------------------- B
    f449 = mesures.get(449, [])
    instrument = [x for x in f449 if "verdict_rule_propagation" in x]
    autres = [x for x in f449 if "verdict_rule_propagation" not in x]
    okB = len(instrument) == 2 and len(autres) == 6
    L.append("## B. La décomposition du #449 — le point qui évite une accusation")
    L.append("")
    L.append("Le rapport n'accuse pas le #449 parce que **2** des importateurs sont")
    L.append("l'instrument du cycle. **Si cette décomposition est fausse, l'accusation")
    L.append("redevient due** — c'est donc le contrôle le plus important de cet audit.")
    L.append("")
    L.append(f"- importateurs au commit du #449 : **{len(f449)}**")
    L.append(f"- **instrument** du cycle : **{len(instrument)}**")
    for x in instrument:
        L.append(f"  - `{x.split('/')[-1]}`")
    L.append(f"- **consommateurs** : **{len(autres)}**")
    for x in autres:
        L.append(f"  - `{x.split('/')[-1]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okB else 'ÉCART'}** — la correction « six")
    L.append("consommateurs » du #449 "
             + ("est confirmée." if okB else "**n'est pas** confirmée."))
    L.append("")

    # ---------------------------------------------------------------- C
    sha451 = bt.commit_introducteur(451)
    emetteurs = grep_l(sha451, "Rapport dépendant du dépôt",
                       "finance/trading/scripts/") if sha451 else []
    portants = grep_l(sha451, "Rapport dépendant du dépôt",
                      "finance/trading/results/") if sha451 else []
    okC = len(emetteurs) > 0
    L.append("## C. La limite avouée — peut-on retrouver l'émetteur ?")
    L.append("")
    L.append("Le rapport avoue ne pas distinguer un **porteur** d'un **citeur**, faute")
    L.append("de savoir quel script **émet** la marque. Le #451 le savait. On vérifie")
    L.append("que cette information est bien accessible — et donc que la limite est")
    L.append("**réelle mais surmontable**, ce qui en fait une piste et non une impasse.")
    L.append("")
    L.append(f"- scripts **émettant** la marque au commit du #451 : **{len(emetteurs)}**")
    for x in emetteurs[:8]:
        L.append(f"  - `{x.split('/')[-1]}`")
    L.append(f"- rapports contenant la marque : **{len(portants)}**")
    L.append("")
    if okC:
        L.append("**CONCORDANT** — l'émetteur est identifiable dans le dépôt. La limite")
        L.append("du backtest tient à **sa** méthode (lire le seul texte des rapports),")
        L.append("pas à une impossibilité : un cycle déclaré pourrait la lever en")
        L.append("croisant rapports et scripts émetteurs.")
    else:
        L.append("**ÉCART** — aucun script émetteur trouvé : la limite est plus profonde")
        L.append("que le rapport ne le dit, et il faudra le corriger.")
    L.append("")

    # ---------------------------------------------------------------- D
    def emp():
        return hashlib.sha256(RAPPORT.read_bytes()).hexdigest() if RAPPORT.exists() else ""

    av = emp()
    subprocess.run([sys.executable,
                    str(SCRIPTS / "nonml_content_defined_magnitudes_backtest.py")],
                   cwd=ROOT, capture_output=True, text=True)
    ap = emp()
    okD = av == ap and av != ""
    L.append("## D. Idempotence de mon propre rapport")
    L.append("")
    L.append(f"- avant : `{av[:16]}`")
    L.append(f"- après : `{ap[:16]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okD else 'ÉCART'}.**")
    L.append("")

    tous = okA and okB and okC and okD
    L.append("## Ce que cet audit ne couvre pas")
    L.append("")
    L.append("- Il ne recompte **pas** G2 par une autre route : `git grep` trouve les")
    L.append("  fichiers contenant la phrase, pas ceux qui la **portent** en tête de")
    L.append("  ligne — c'est précisément la distinction que le rapport déclare ne pas")
    L.append("  savoir faire.")
    L.append("- Il ne dit rien du faux du **#453**, hors de portée des deux cycles.")
    L.append("")
    L.append(f"## Verdict — **{'CONCORDANT' if tous else 'ÉCART'}** "
             f"({sum([okA, okB, okC, okD])}/4)")
    L.append("")
    L.append("Aucun écart par recomptage indépendant." if tous
             else "**Au moins un contrôle échoue — voir ci-dessus.**")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

"""Audit adversarial du #464 — recompter par une autre route.

Le backtest decoupe le backlog ligne a ligne. L'audit le decoupe par une
expression reguliere sur le texte ENTIER, et verifie chaque cas signale par un
acces disque independant.

  A. Les trois categories, recomptees autrement.
  B. Les 10 « aucun fichier » : vraiment aucun ?
  C. Les 24 orphelins reels : le nom est-il vraiment absent du backlog ?
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

OUT = RESULTS / "nonml_prereg_convention_coverage_audit.md"
RAPPORT = RESULTS / "nonml_prereg_convention_coverage_result.md"
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"


def main():
    texte = BACKLOG.read_text(encoding="utf-8")
    lu = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    # ---------------------------------------------------------------- A
    blocs = re.findall(r"(?ms)^## Backlog #(\d+)\b.*?(?=^## |\Z)", texte)
    corps = re.split(r"(?m)^## ", texte)
    corps = ["## " + c for c in corps if c.startswith("Backlog #")]
    z = u = p = 0
    for c in corps:
        n = len(set(re.findall(r"PREREG_([a-z0-9_]+)\.md", c)))
        z, u, p = (z + (n == 0), u + (n == 1), p + (n > 1))
    total = len(corps)

    def lit(motif):
        m = re.search(motif, lu)
        return int(m.group(1)) if m else -1

    att = {"total": lit(r"entrées de backlog : \*\*(\d+)\*\*"),
           "une": lit(r"citant \*\*exactement un\*\* `PREREG_` : \*\*(\d+)\*\*"),
           "zero": lit(r"citant \*\*aucun\*\* : \*\*(\d+)\*\*"),
           "plus": lit(r"citant \*\*plusieurs\*\* : \*\*(\d+)\*\*")}
    mes = {"total": total, "une": u, "zero": z, "plus": p}
    okA = all(att[k] == mes[k] for k in mes) and len(blocs) == total

    L = ["# Audit adversarial — couverture de la convention `PREREG_` (#464)", ""]
    L.append("Le backtest découpe le backlog **ligne à ligne** ; l'audit le découpe par")
    L.append("une **expression régulière sur le texte entier**. Deux routes distinctes.")
    L.append("")
    L.append("## A. Les trois catégories, recomptées")
    L.append("")
    L.append("| Grandeur | Rapport | Audit |")
    L.append("|---|---|---|")
    for k, nom in (("total", "entrées"), ("une", "exactement un"),
                   ("zero", "aucun"), ("plus", "plusieurs")):
        marque = "" if att[k] == mes[k] else " **←**"
        L.append(f"| {nom} | {att[k]} | {mes[k]}{marque} |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okA else 'ÉCART'}.**")
    L.append("")

    # ---------------------------------------------------------------- B
    bloc_b = re.search(r"(?ms)### Les seuls cas sans aucun fichier\n\n\|.*?\n\n", lu)
    noms_b = re.findall(r"\| #\d+ \| `([a-z0-9_]+)` \|", bloc_b.group(0)) if bloc_b else []
    faux_b = []
    for n in noms_b:
        trouves = [x.name for x in RESULTS.iterdir()
                   if x.is_file() and n in x.name and not x.name.endswith("_anti_cheat.md")]
        if trouves:
            faux_b.append((n, trouves[0]))
    okB = not faux_b
    L.append("## B. Les cas « aucun fichier » — vraiment aucun ?")
    L.append("")
    L.append(f"- cas relus : **{len(noms_b)}**")
    L.append(f"- **contredits** (un fichier porte pourtant ce nom) : **{len(faux_b)}**")
    if faux_b:
        L.append("")
        L.append("| `<nom>` | Fichier trouvé |")
        L.append("|---|---|")
        for n, f in faux_b:
            L.append(f"| `{n}` | `{f}` |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okB else 'ÉCART'}.**")
    L.append("")

    # ---------------------------------------------------------------- C
    bloc_c = re.search(r"(?ms)Les \*\*\d+\*\* premiers, par ordre alphabétique.*?\Z", lu)
    noms_c = re.findall(r"- `PREREG_([a-z0-9_]+)\.md`", bloc_c.group(0)) if bloc_c else []
    faux_c = [n for n in noms_c if n in texte]
    okC = not faux_c
    L.append("## C. Les orphelins réels — le nom est-il vraiment absent ?")
    L.append("")
    L.append(f"- orphelins relus : **{len(noms_c)}**")
    L.append(f"- **contredits** (le nom apparaît dans le backlog) : **{len(faux_c)}**")
    if faux_c:
        L.append("")
        for n in faux_c:
            L.append(f"- `{n}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okC else 'ÉCART'}.**")
    L.append("")

    # ---------------------------------------------------------------- D
    def emp():
        return hashlib.sha256(RAPPORT.read_bytes()).hexdigest() if RAPPORT.exists() else ""

    av = emp()
    subprocess.run([sys.executable,
                    str(SCRIPTS / "nonml_prereg_convention_coverage_backtest.py")],
                   cwd=ROOT, capture_output=True, text=True)
    ap = emp()
    okD = av == ap and av != ""
    L.append("## D. Idempotence de mon propre rapport")
    L.append("")
    L.append("Le #463 a montré qu'un cycle qui mesure les autres doit commencer par")
    L.append("lui-même. Ce rapport ne compte **pas** de rapports — il compte des")
    L.append("**entrées de backlog** — donc l'auto-inclusion du #447 ne devrait pas")
    L.append("l'atteindre. À vérifier plutôt qu'à supposer.")
    L.append("")
    L.append(f"- avant : `{av[:16]}`")
    L.append(f"- après : `{ap[:16]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okD else 'ÉCART'}.**")
    L.append("")

    tous = okA and okB and okC and okD
    L.append("## Ce que cet audit ne couvre pas")
    L.append("")
    L.append("- Il **ne juge pas** si la convention *devrait* être suivie : il mesure")
    L.append("  une couverture, il ne prononce pas d'infraction.")
    L.append("- Il relit les cas **publiés** par le rapport, pas ceux que le rapport")
    L.append("  aurait omis de produire.")
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

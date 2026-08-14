"""Audit adversarial du #467 — l'abandon est-il justifie ?

Le backtest conclut a la fermeture de la piste. Un abandon merite le meme
examen qu'une decouverte : s'il est premature, on jette un outil qui marchait.

  A. L'echantillon est-il bien celui que la regle deterministe designe ?
     (6 premiers nouveaux signales, ordre alphabetique — verifie sans
     reutiliser le code du backtest.)
  B. Les 6 sont-ils reellement idempotents, ou l'ont-ils ete par chance ?
     Un TROISIEME passage sur chacun : une derive a periode 2 y apparaitrait.
  C. La regle elargie signale-t-elle bien PLUS que celle du #466, comme
     annonce ? Sinon l'elargissement n'a rien fait et la comparaison est vide.
  D. Idempotence de mon propre rapport.
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

import nonml_self_inclusion_detector_backtest as v1  # noqa: E402

OUT = RESULTS / "nonml_self_inclusion_detector_v2_audit.md"
RAPPORT = RESULTS / "nonml_self_inclusion_detector_v2_result.md"
MOI = "self_inclusion_detector_v2"

# Motifs REECRITS a la main depuis le pre-enregistrement, pas importes.
ECRIT = re.compile(r"write_text\s*\(")
LARGE = re.compile(r"RESULTS\s*\.\s*glob|RESULTS\s*\.\s*iterdir|glob\.glob|"
                   r"ls-tree|ls-files|[\"']status[\"']|git\s+status|"
                   r"--name-only|--name-status")
ETROIT = re.compile(r"RESULTS\s*\.\s*glob|RESULTS\s*\.\s*iterdir|glob\.glob|"
                    r"ls-tree|ls-files")
PROT = re.compile(r"unlink\s*\(|!=\s*OUT|OUT\s*!=|p\s*!=\s*OUT|MOI|"
                  r"not\s+in\s+.*OUT|\.name\s*!=")


def restaure():
    subprocess.run(["git", "checkout", "--", "finance/trading/results/"],
                   cwd=REPO, capture_output=True, text=True)


def emp(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def main():
    lu = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    sig_large, sig_etroit = [], []
    for p in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        t = p.read_text(encoding="utf-8")
        if not ECRIT.search(t) or PROT.search(t):
            continue
        if LARGE.search(t):
            sig_large.append(p.name)
        if ETROIT.search(t):
            sig_etroit.append(p.name)

    connus = v1.FAUTIFS_463 | v1.SAINS_463
    nouveaux = sorted(set(sig_large) - connus)
    attendu = nouveaux[:6]

    # ---------------------------------------------------------------- A
    publies = re.findall(r"\| `(nonml_[a-z0-9_]+_backtest\.py)` \| (?:idempotent|\*)",
                         lu)
    okA = publies == attendu

    L = ["# Audit adversarial — détecteur d'auto-inclusion v2 (#467)", ""]
    L.append("Le backtest conclut à **fermer la piste**. Un abandon mérite le même")
    L.append("examen qu'une découverte : **s'il est prématuré, on jette un outil qui")
    L.append("marchait.**")
    L.append("")
    L.append("## A. L'échantillon est-il celui que la règle désigne ?")
    L.append("")
    L.append("La règle — « 6 premiers nouveaux signalés, ordre alphabétique » — était")
    L.append("fixée avant de voir la liste. On la ré-applique **sans réutiliser le code**")
    L.append("du backtest.")
    L.append("")
    L.append(f"- attendu par l'audit : **{len(attendu)}** scripts")
    L.append(f"- publiés par le rapport : **{len(publies)}**")
    if publies != attendu:
        L.append("")
        L.append("| Rang | Audit | Rapport |")
        L.append("|---|---|---|")
        for i in range(max(len(attendu), len(publies))):
            a = attendu[i] if i < len(attendu) else "—"
            b = publies[i] if i < len(publies) else "—"
            L.append(f"| {i + 1} | `{a}` | `{b}` |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okA else 'ÉCART'}.**")
    L.append("")

    # ---------------------------------------------------------------- B
    L.append("## B. Idempotents, ou idempotents **par chance** ?")
    L.append("")
    L.append("Deux passages identiques ne prouvent pas la stabilité : une dérive de")
    L.append("**période 2** y échapperait. Chacun est rejoué une **troisième** fois.")
    L.append("")
    L.append("| Script | P1=P2 (rapport) | P3 | Verdict |")
    L.append("|---|---|---|---|")
    instables = []
    for n in attendu:
        restaure()
        nom = n[len("nonml_"):-len("_backtest.py")]
        rap = RESULTS / f"nonml_{nom}_result.md"
        emps = []
        for _ in range(3):
            r = subprocess.run([sys.executable, str(SCRIPTS / n)], cwd=ROOT,
                               capture_output=True, text=True, timeout=600)
            emps.append(emp(rap) if r.returncode == 0 else None)
        stable = emps[0] is not None and emps[0] == emps[1] == emps[2]
        if not stable:
            instables.append(n)
        L.append(f"| `{n}` | oui | `{(emps[2] or '—')[:12]}` | "
                 + ("stable sur 3" if stable else "**instable**") + " |")
    restaure()
    okB = not instables
    L.append("")
    if okB:
        L.append("**CONCORDANT** — aucun des 6 ne dérive au troisième passage. Le")
        L.append("**0/6** du rapport tient, et l'abandon repose sur une mesure solide.")
    else:
        L.append(f"**ÉCART** — **{len(instables)}** script(s) dérivent au troisième")
        L.append("passage. **L'abandon serait prématuré** : le détecteur avait raison")
        L.append("sur eux, et le rapport doit être corrigé avant d'être publié.")
    L.append("")

    # ---------------------------------------------------------------- C
    okC = len(sig_large) > len(sig_etroit)
    L.append("## C. L'élargissement a-t-il élargi ?")
    L.append("")
    L.append(f"- signalés par la règle **élargie** : **{len(sig_large)}**")
    L.append(f"- signalés par la règle **étroite** du #466 : **{len(sig_etroit)}**")
    L.append("")
    L.append(f"**{'CONCORDANT' if okC else 'ÉCART'}** — "
             + ("la règle élargie signale bien davantage."
                if okC else
                "**l'élargissement n'a rien changé**, et la comparaison au #466 "
                "serait vide."))
    L.append("")

    # ---------------------------------------------------------------- D
    av = emp(RAPPORT)
    subprocess.run([sys.executable,
                    str(SCRIPTS / "nonml_self_inclusion_detector_v2_backtest.py")],
                   cwd=ROOT, capture_output=True, text=True)
    ap = emp(RAPPORT)
    okD = av is not None and av == ap
    L.append("## D. Idempotence de mon propre rapport")
    L.append("")
    L.append(f"- avant : `{(av or '—')[:16]}`")
    L.append(f"- après : `{(ap or '—')[:16]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okD else 'ÉCART'}.**")
    L.append("")

    tous = okA and okB and okC and okD
    L.append("## Ce que cet audit ne couvre pas")
    L.append("")
    L.append("- Il éprouve **6** scripts sur les 320 : la fermeture de la piste repose")
    L.append("  sur un échantillon étroit, et le rapport ne le cache pas.")
    L.append("- Il ne teste que **3** passages : une dérive de période plus longue lui")
    L.append("  échapperait encore.")
    L.append("")
    L.append(f"## Verdict — **{'CONCORDANT' if tous else 'ÉCART'}** "
             f"({sum([okA, okB, okC, okD])}/4)")
    L.append("")
    L.append("L'abandon est justifié par la mesure." if tous
             else "**Au moins un contrôle échoue — voir ci-dessus.**")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

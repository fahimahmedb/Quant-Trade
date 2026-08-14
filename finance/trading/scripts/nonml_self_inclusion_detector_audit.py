"""Audit adversarial du #466 — un detecteur rate merite-t-il qu'on le croie ?

Le backtest conclut lui-meme que son detecteur est inutilisable (rappel 1/2).
L'audit ne cherche donc pas a le confirmer : il verifie que **l'aveu est
correct** et que rien d'autre n'est surestime.

  A. Les trois comptes (hors perimetre / proteges / signales), recomptes.
  B. Le cas manque : `git status` est-il bien la forme d'enumeration ignoree ?
  C. Les 10 faux positifs sont-ils VRAIMENT faux ? Un « sain au #463 » signale
     pourrait etre un vrai expose qui n'a pas eu l'occasion de se voir.
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
sys.path.insert(0, str(SCRIPTS))

import nonml_self_inclusion_detector_backtest as det  # noqa: E402

OUT = RESULTS / "nonml_self_inclusion_detector_audit.md"
RAPPORT = RESULTS / "nonml_self_inclusion_detector_result.md"


def main():
    lu = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    def lit(motif):
        m = re.search(motif, lu)
        return int(m.group(1)) if m else -1

    # ---------------------------------------------------------------- A
    # Recomptage par une AUTRE route : lecture disque directe, sans reutiliser
    # `classe()`, avec des motifs reecrits a la main depuis le pre-enregistrement.
    ecrit = re.compile(r"write_text\s*\(")
    enumere = re.compile(r"RESULTS\s*\.\s*glob|RESULTS\s*\.\s*iterdir|"
                         r"ls-tree|ls-files|glob\.glob")
    prot = re.compile(r"unlink\s*\(|!=\s*OUT|OUT\s*!=|p\s*!=\s*OUT|MOI|"
                      r"not\s+in\s+.*OUT|\.name\s*!=")
    h = pr = si = 0
    signales = []
    for p in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        t = p.read_text(encoding="utf-8")
        if not (ecrit.search(t) and enumere.search(t)):
            h += 1
        elif prot.search(t):
            pr += 1
        else:
            si += 1
            signales.append(p.name)

    att = {"hors": lit(r"\*\*hors périmètre\*\*[^*]*\*\*(\d+)\*\*"),
           "prot": lit(r"\*\*protégés\*\* : \*\*(\d+)\*\*"),
           "sig": lit(r"\*\*signalés\*\* : \*\*(\d+)\*\*")}
    okA = att["hors"] == h and att["prot"] == pr and att["sig"] == si

    L = ["# Audit adversarial — détecteur d'auto-inclusion (#466)", ""]
    L.append("Le backtest conclut **lui-même** que son détecteur est inutilisable")
    L.append("(rappel 1/2). L'audit ne cherche donc pas à le confirmer : il vérifie que")
    L.append("**l'aveu est exact** et que rien d'autre n'est surestimé.")
    L.append("")
    L.append("## A. Les trois comptes, recomptés")
    L.append("")
    L.append("| | Rapport | Audit |")
    L.append("|---|---|---|")
    L.append(f"| hors périmètre | {att['hors']} | {h} |")
    L.append(f"| protégés | {att['prot']} | {pr} |")
    L.append(f"| signalés | {att['sig']} | {si} |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okA else 'ÉCART'}.**")
    L.append("")

    # ---------------------------------------------------------------- B
    manque = SCRIPTS / "nonml_six_reports_regeneration_backtest.py"
    t = manque.read_text(encoding="utf-8") if manque.exists() else ""
    a_git_status = bool(re.search(r"git\s*\(\s*[\"']status|[\"']status[\"']", t))
    a_glob = bool(enumere.search(t))
    okB = a_git_status and not a_glob
    L.append("## B. Le cas manqué — le diagnostic tient-il ?")
    L.append("")
    L.append("Le rapport affirme que ce script énumère par `git status`, forme que la")
    L.append("règle déclarée ne couvre pas. **Si c'était faux, l'excuse serait pire que")
    L.append("l'erreur.**")
    L.append("")
    L.append(f"- appelle `git status` : **{'oui' if a_git_status else 'non'}**")
    L.append(f"- énumère par un glob de `results/` : **{'oui' if a_glob else 'non'}**")
    L.append("")
    L.append(f"**{'CONCORDANT' if okB else 'ÉCART'}** — le diagnostic "
             + ("tient." if okB else "**ne tient pas**."))
    L.append("")

    # ---------------------------------------------------------------- C
    L.append("## C. Les faux positifs sont-ils vraiment faux ?")
    L.append("")
    L.append("Un script « sain au #463 » mais signalé n'est pas forcément un faux")
    L.append("positif : il peut être **réellement exposé** et n'avoir simplement pas")
    L.append("rencontré son propre fichier lors des deux passages du #463.")
    L.append("")
    L.append("Contrôle : ces scripts écrivent-ils leur rapport **dans le dossier qu'ils")
    L.append("énumèrent** ?")
    L.append("")
    vrais_exposes = []
    for n in sorted(det.SAINS_463 & set(signales)):
        t = (SCRIPTS / n).read_text(encoding="utf-8")
        if re.search(r"OUT\s*=\s*RESULTS\s*/", t) and enumere.search(t):
            vrais_exposes.append(n)
    L.append(f"- faux positifs examinés : **{len(det.SAINS_463 & set(signales))}**")
    L.append(f"- qui écrivent bel et bien dans `results/` **et** l'énumèrent : "
             f"**{len(vrais_exposes)}**")
    L.append("")
    if vrais_exposes:
        L.append("> **Ce ne sont pas des faux positifs au sens strict.** Ces scripts sont")
        L.append("> **structurellement exposés** ; le #463 ne les a pas vus dériver, ce")
        L.append("> qui est une observation, pas une garantie. La calibration du rapport")
        L.append("> les compte comme des erreurs du détecteur : **elle est donc")
        L.append("> pessimiste**, et le rapport ne le dit pas.")
        L.append("")
        L.append("C'est un écart **en faveur** du détecteur — et il se publie au même")
        L.append("titre qu'un écart défavorable.")
    else:
        L.append("**Aucun** : les faux positifs en sont bien.")
    L.append("")

    # ---------------------------------------------------------------- D
    def emp():
        return hashlib.sha256(RAPPORT.read_bytes()).hexdigest() if RAPPORT.exists() else ""

    av = emp()
    subprocess.run([sys.executable,
                    str(SCRIPTS / "nonml_self_inclusion_detector_backtest.py")],
                   cwd=ROOT, capture_output=True, text=True)
    ap = emp()
    okD = av == ap and av != ""
    L.append("## D. Idempotence de mon propre rapport")
    L.append("")
    L.append("Ce rapport **énumère `results/`** et **y écrit** : il est exactement le")
    L.append("genre de script qu'il signale. À vérifier, pas à supposer.")
    L.append("")
    L.append(f"- avant : `{av[:16]}`")
    L.append(f"- après : `{ap[:16]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okD else 'ÉCART'}.**")
    L.append("")

    tous = okA and okB and okD
    L.append("## Ce que cet audit ne couvre pas")
    L.append("")
    L.append("- Il ne **répare** pas le détecteur : la règle a été déclarée avant")
    L.append("  mesure, l'élargir ici la taillerait sur le cas qu'elle vient de rater.")
    L.append("- Il n'**exécute** aucun des scripts signalés : leur défaut reste")
    L.append("  **supposé**, pas prouvé.")
    L.append("")
    L.append(f"## Verdict — **{'CONCORDANT' if tous else 'ÉCART'}** "
             f"({sum([okA, okB, okD])}/3)")
    L.append("")
    L.append("L'aveu du backtest est exact et son diagnostic tient." if tous
             else "**Au moins un contrôle échoue — voir ci-dessus.**")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

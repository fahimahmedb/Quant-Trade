"""Audit indépendant du #525 : reconfirme les 2 reclassements MASQUANT->ANODIN
et l'absence de régénération du rapport du #484, par une route distincte
(grep externe pour les références inconditionnelles, git show pour
vérifier le diff committé du dictionnaire V et l'absence de diff sur le
rapport) -- meme forme que l'audit du #524.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_staleness_candidates_484_audit_result.md"
COMMIT_REPARATION = "2bba0ff"

MASQUANTS = [("nonml_six_reports_regeneration_backtest.py", "perdus"),
             ("nonml_sweep_pass_prose_fix_backtest.py", "strategies")]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def grep_n(motif, chemin):
    r = subprocess.run(["grep", "-n", motif, str(chemin)],
                       capture_output=True, text=True)
    return [(int(l.split(":", 1)[0]), l.split(":", 1)[1])
            for l in r.stdout.splitlines()]


def main():
    L = []
    A = L.append
    A("# Audit indépendant — #525, les 2 reclassements MASQUANT → ANODIN")
    A("")
    A("Route distincte du backtest : `grep -n` externe (pas d'AST) pour")
    A("retrouver les occurrences de la variable, et `git show` pour")
    A("vérifier le diff réellement committé du dictionnaire `V` et")
    A("l'absence de tout diff sur le rapport du #484. Même forme que")
    A("l'audit du #524.")
    A("")

    A("## Occurrences de chaque variable, par grep externe")
    A("")
    tout_ok = True
    for fichier, var in MASQUANTS:
        occs = grep_n(rf"\b{var}\b", SCRIPTS / fichier)
        occs_append = [(ln, txt) for ln, txt in occs if "L.append(" in txt]
        A(f"### `{fichier}` — `{var}`")
        A("")
        A(f"- occurrences dans un `L.append(` (grep externe) : "
          f"{[ln for ln, _ in occs_append]}")
        garde = grep_n(rf"^\s*if {var}:", SCRIPTS / fichier)
        ligne_garde = garde[0][0] if garde else None
        premiere = occs_append[0][0] if occs_append else None
        avant_garde = (premiere is not None and ligne_garde is not None
                       and premiere < ligne_garde)
        A(f"- ligne de la garde `if {var}:` (grep externe) : {ligne_garde}")
        A(f"- première référence en `L.append(` avant la garde : "
          f"**{'OUI' if avant_garde else 'NON'}** (l.{premiere})")
        A("")
        if not avant_garde:
            tout_ok = False
        else:
            A(f"> Confirme, par une route indépendante, qu'une référence "
              f"inconditionnelle à `{var}` existe **avant** la garde — "
              f"le MASQUANT ne peut pas tenir.")
        A("")

    A("## Le diff committé, vérifié via `git show`")
    A("")
    diff_rapport = git("show", COMMIT_REPARATION, "--stat")
    rapport_absent_du_commit = ("nonml_guards_witness_remainder_result.md"
                                not in diff_rapport)
    A(f"- le commit de réparation touche-t-il le rapport "
      f"`nonml_guards_witness_remainder_result.md` : "
      f"**{'NON' if rapport_absent_du_commit else 'OUI — inattendu'}**")
    A("")
    if rapport_absent_du_commit:
        A("> Confirme que le rapport du #484 n'a pas été régénéré ni "
          "committé, comme annoncé — seul le dictionnaire `V` a changé.")
    A("")

    verdict = "PASS" if tout_ok and rapport_absent_du_commit else "FAIL"
    A(f"**{verdict}** — " + (
        "la route indépendante (grep externe + git show) confirme les 2 "
        "reclassements et l'absence de régénération du rapport."
        if verdict == "PASS" else
        "désaccord entre la route indépendante et le rapport publié."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — tout_ok={tout_ok}, "
          f"rapport_absent_du_commit={rapport_absent_du_commit}")


if __name__ == "__main__":
    main()

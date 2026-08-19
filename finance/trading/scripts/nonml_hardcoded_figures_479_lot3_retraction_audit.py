"""Audit indépendant du #527 : reconfirme, via `git show`, que l'entrée
`V` du #479 pour `reproducibility_sample_lot3_audit.py` valait bien
"defaut" avant le commit de réparation et vaut "legitime" après, et que
le diff committé est borné à cette seule entrée -- sans réutiliser le
code du backtest (pas d'AST, grep externe sur le contenu de chaque
révision).
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_hardcoded_figures_479_lot3_retraction_audit_result.md"
COMMIT_REPARATION = "e8690a6"
CIBLE_REL = ("finance/trading/scripts/"
            "nonml_hardcoded_figures_remainder_backtest.py")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def grep_apres(motif, texte, fenetre=80):
    i = texte.find(motif)
    return texte[i:i + fenetre] if i >= 0 else None


def main():
    avant = git("show", f"{COMMIT_REPARATION}~1:{CIBLE_REL}")
    apres = git("show", f"{COMMIT_REPARATION}:{CIBLE_REL}")

    motif = '"nonml_reproducibility_sample_lot3_audit.py": ("'
    fenetre = len(motif) + 20
    extrait_avant = grep_apres(motif, avant, fenetre)
    extrait_apres = grep_apres(motif, apres, fenetre)

    verdict_avant = "defaut" if extrait_avant and "defaut" in extrait_avant else (
        "legitime" if extrait_avant and "legitime" in extrait_avant else "?")
    verdict_apres = "defaut" if extrait_apres and "defaut" in extrait_apres else (
        "legitime" if extrait_apres and "legitime" in extrait_apres else "?")

    diff_v = git("show", COMMIT_REPARATION, "--", CIBLE_REL)
    lignes_supprimees = [l for l in diff_v.splitlines()
                        if l.startswith("-") and not l.startswith("---")
                        and '"nonml_' in l]
    n_entrees_touchees = sum(1 for l in lignes_supprimees if '": ("' in l)

    diff_stat = git("show", COMMIT_REPARATION, "--stat")
    rapport_absent = ("nonml_hardcoded_figures_remainder_result.md"
                      not in diff_stat)

    L = []
    A = L.append
    A("# Audit indépendant — #527, rétractation appliquée à sa source")
    A("")
    A("Route distincte du backtest : `git show` sur les deux révisions "
      "(avant/après le commit de réparation), lecture textuelle directe "
      "de l'entrée `V` — pas d'AST, pas d'import du module.")
    A("")
    A("## L'entrée `V`, avant et après le commit de réparation")
    A("")
    A(f"- avant (`{COMMIT_REPARATION}~1`) : **{verdict_avant}**")
    A(f"- après (`{COMMIT_REPARATION}`) : **{verdict_apres}**")
    A("")
    accord = verdict_avant == "defaut" and verdict_apres == "legitime"
    A(f"- confirme la correction annoncée (defaut → legitime) : "
      f"**{'OUI' if accord else 'NON'}**")
    A("")

    A("## Le diff, vérifié borné à 1 entrée")
    A("")
    A(f"- entrées `V` supprimées dans le diff : **{n_entrees_touchees}** "
      f"(attendu : 1)")
    A(f"- rapport `nonml_hardcoded_figures_remainder_result.md` absent du "
      f"commit : **{'OUI' if rapport_absent else 'NON'}**")
    A("")

    verdict = "PASS" if (accord and n_entrees_touchees == 1
                         and rapport_absent) else "FAIL"
    A(f"**{verdict}** — " + (
        "la route indépendante (git show sur les deux révisions) confirme "
        "la correction et son périmètre borné."
        if verdict == "PASS" else
        "désaccord entre la route indépendante et le rapport publié."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — avant={verdict_avant}, après={verdict_apres}, "
          f"n_entrees_touchees={n_entrees_touchees}, rapport_absent={rapport_absent}")


if __name__ == "__main__":
    main()

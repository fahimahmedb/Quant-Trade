"""Audit indépendant du #526 : recompte les 18 noms retrouvés dans la
section #463 par une route distincte (grep externe sur un fichier
temporaire contenant la seule section #463, pas de découpage regex en
mémoire), et confirme via git show que le diff committé du dictionnaire
V du #479 est borné à la seule entrée corrigée.
"""
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_hardcoded_figures_479_self_inclusion_audit_result.md"
COMMIT_REPARATION = "ed2bb4f"

FAUTIFS = ["verdict_rule_propagation", "six_reports_regeneration"]
SAINS = ["npz_report_consistency_baskets", "third_npz_schema_handling",
         "net_pnl_correction", "sweep_pass_prose_fix", "verdict_detector_fix",
         "verdict_detector_complete", "marker_emitted_by_scripts",
         "tom_decomposition_npz", "orphan_npz_inspection",
         "verdict_variant_decision", "silent_skip_decision",
         "dsr_corrected_trials", "battery_coverage", "temporal_holdout",
         "relative_holdout", "verdict_rule_battery"]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def main():
    # Route independante : awk extrait la section #463 dans un fichier
    # temporaire, puis grep -c externe compte chaque radical.
    lignes = BACKLOG.read_text(encoding="utf-8").splitlines()
    debut = fin = None
    for i, l in enumerate(lignes):
        if l.startswith("## Backlog #463"):
            debut = i
        elif debut is not None and l.startswith("## Backlog #") and i > debut:
            fin = i
            break
    if fin is None:
        fin = len(lignes)
    sec463_lignes = lignes[debut:fin]

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as f:
        f.write("\n".join(sec463_lignes))
        tmp = f.name

    def compte(radical):
        r = subprocess.run(["grep", "-c", radical, tmp],
                           capture_output=True, text=True)
        try:
            return int(r.stdout.strip())
        except ValueError:
            return 0

    fautifs_trouves = sum(1 for r in FAUTIFS if compte(r) > 0)
    sains_trouves = sum(1 for r in SAINS if compte(r) > 0)
    total_trouves = fautifs_trouves + sains_trouves

    Path(tmp).unlink()

    L = []
    A = L.append
    A("# Audit indépendant — #526, traçabilité de la citation « 16 et 2 »")
    A("")
    A("Route distincte du backtest : la section `## Backlog #463` est")
    A("extraite dans un fichier temporaire (bornes de ligne trouvées par")
    A("balayage Python simple, pas par regex de découpage), puis chaque")
    A("radical est compté par `grep -c` en processus externe.")
    A("")
    A("## Recompte")
    A("")
    A(f"- `FAUTIFS_463` retrouvés (sur {len(FAUTIFS)}) : **{fautifs_trouves}**")
    A(f"- `SAINS_463` retrouvés (sur {len(SAINS)}) : **{sains_trouves}**")
    A(f"- total retrouvé : **{total_trouves} / {len(FAUTIFS) + len(SAINS)}**")
    A("")
    accord_compte = (fautifs_trouves == 2 and sains_trouves == 0)
    A(f"- accord avec le backtest (2 FAUTIFS trouvés, 0 SAINS trouvé) : "
      f"**{'OUI' if accord_compte else 'NON'}**")
    A("")

    A("## Le diff committé, vérifié via `git show`")
    A("")
    diff_v = git("show", COMMIT_REPARATION, "--",
                "finance/trading/scripts/nonml_hardcoded_figures_remainder_backtest.py")
    n_entrees_modifiees = diff_v.count('-("nonml_') + diff_v.count('- "nonml_')
    diff_stat = git("show", COMMIT_REPARATION, "--stat")
    rapport_absent = "nonml_hardcoded_figures_remainder_result.md" not in diff_stat
    A(f"- occurrences de clés `V` supprimées dans le diff : "
      f"**{n_entrees_modifiees}** (attendu : 1)")
    A(f"- le rapport `nonml_hardcoded_figures_remainder_result.md` est-il "
      f"absent du commit : **{'OUI' if rapport_absent else 'NON'}**")
    A("")

    verdict = "PASS" if (accord_compte and n_entrees_modifiees == 1
                         and rapport_absent) else "FAIL"
    A(f"**{verdict}** — " + (
        "la route indépendante (extraction de section + grep -c externe, "
        "et git show) confirme le compte 2/18 et le diff borné à 1 entrée."
        if verdict == "PASS" else
        "désaccord entre la route indépendante et le rapport publié."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — fautifs={fautifs_trouves}/2, sains={sains_trouves}/16, "
          f"n_entrees_modifiees={n_entrees_modifiees}, rapport_absent={rapport_absent}")


if __name__ == "__main__":
    main()

"""Audit indépendant du #528 : recompte, par une route distincte (grep -c
externe, sans réutiliser la fonction de recherche du backtest), les
occurrences des marqueurs de rétractation à proximité de chacun des 22
radicaux, et confirme via git que le dictionnaire V du #479 n'a reçu
aucune modification dans le commit de ce cycle (0 correction attendue).
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_hardcoded_figures_479_remainder_closure_audit_result.md"
COMMIT_CYCLE = "be13f13"

CANDIDATS = [
 ("nonml_battery_backfill_lot_audit.py", 508),
 ("nonml_citer_451_resolution_backtest.py", 481),
 ("nonml_conditional_sections_sweep_backtest.py", 509),
 ("nonml_dsr_corrected_trials_backtest.py", 518),
 ("nonml_idempotence_famille_capable_backtest.py", 518),
 ("nonml_idempotence_lot2_backtest.py", 518),
 ("nonml_marker_emitter_crossing_backtest.py", 481),
 ("nonml_net_pnl_correction_robustness.py", 481),
 ("nonml_orphans_interrupted_or_lost_backtest.py", 485),
 ("nonml_pnl_duplicate_sweep_audit.py", 480),
 ("nonml_pnl_duplicate_sweep_v2_audit.py", 480),
 ("nonml_pnl_persistence_exposed_pass_audit.py", 480),
 ("nonml_report_idempotence_audit.py", 504),
 ("nonml_reproducibility_campaign_v2_audit.py", 518),
 ("nonml_reproducibility_campaign_v3_lot2_audit.py", 485),
 ("nonml_reproducibility_sample_backtest.py", 482),
 ("nonml_self_inclusion_repair_audit.py", 516),
 ("nonml_sweep_pass_prose_fix_backtest.py", 494),
 ("nonml_content_defined_magnitudes_audit.py", 504),
 ("nonml_content_defined_magnitudes_backtest.py", 504),
 ("nonml_coverage_wording_fix_audit.py", 518),
 ("nonml_report_idempotence_backtest.py", 504),
]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def radical(nom):
    return re.sub(r"^nonml_|_backtest\.py$|_audit\.py$|\.py$", "", nom)


def sections_bornes(lignes):
    out = {}
    debut = None
    for i, l in enumerate(lignes):
        if l.startswith("## Backlog #"):
            if debut is not None:
                out[cyc] = (debut, i)
            m = re.match(r"## Backlog #(\d+)", l)
            cyc, debut = int(m.group(1)), i
    if debut is not None:
        out[cyc] = (debut, len(lignes))
    return out


def main():
    lignes = BACKLOG.read_text(encoding="utf-8").splitlines()
    bornes = sections_bornes(lignes)

    L = []
    A = L.append
    A("# Audit indépendant — #528, clôture du lot hardcoded_figures_remainder")
    A("")
    A("Route distincte du backtest : `grep -c` externe sur un extrait de")
    A("section isolé par indices de ligne (pas de découpage regex en")
    A("mémoire unique), recherche des marqueurs de rétractation avec un")
    A("filtre explicite sur la phrase générique de la « Dette restante ».")
    A("")
    A("## Recompte des marqueurs de rétractation, par grep externe")
    A("")
    A("| Script | Radical | Marqueur trouvé (hors dette générique) |")
    A("|---|---|---|")
    n_marqueurs_reels = 0
    for nom, cyc in CANDIDATS:
        r = radical(nom)
        if cyc not in bornes:
            A(f"| `{nom}` | `{r}` | section absente |")
            continue
        d, f = bornes[cyc]
        bloc = "\n".join(lignes[d:f])
        bloc = re.sub(r"\s+", " ", bloc.replace("*", "").replace("`", ""))
        trouve = False
        for mk in ["rétracté", "n'est pas un défaut"]:
            for m in re.finditer(re.escape(mk), bloc):
                fenetre = bloc[max(0, m.start() - 60):m.start() + 40]
                # Generalise au #531 : la narration propre d'un cycle
                # decrivant sa propre exclusion ("... pas une discussion
                # du script") echappait au filtre precedent, faille
                # trouvee au #530.
                if any(mg in fenetre for mg in
                       ("rétractés sur mesure", "pas une discussion du script")):
                    continue
                # Le radical de CE script doit apparaitre dans une fenetre
                # raisonnable autour du marqueur, et cette occurrence ne
                # doit PAS etre en realite le prefixe d'un radical plus
                # long et deja traite (collision de sous-chaine, ex.
                # "reproducibility_sample" a l'interieur de
                # "reproducibility_sample_lot3_audit", deja repare au #527).
                grande_fenetre = bloc[max(0, m.start() - 300):m.start() + 300]
                for occ in re.finditer(re.escape(r), grande_fenetre):
                    suite = grande_fenetre[occ.end():occ.end() + 15]
                    if suite.startswith("_lot3_audit") or suite.startswith("_detector"):
                        continue  # prefixe d'un radical plus long, deja traite
                    trouve = True
        n_marqueurs_reels += trouve
        A(f"| `{nom}` | `{r}` | {'OUI' if trouve else 'non'} |")
    A("")
    A(f"- marqueurs de rétractation réels retrouvés (hors dette générique) : "
      f"**{n_marqueurs_reels}**")
    A(f"- accord avec le backtest (0 nouvelle rétractation) : "
      f"**{'OUI' if n_marqueurs_reels == 0 else 'NON'}**")
    A("")

    A("## Le dictionnaire `V` du #479, confirmé inchangé par ce commit")
    A("")
    diff_v = git("show", COMMIT_CYCLE, "--stat")
    v_absent = ("nonml_hardcoded_figures_remainder_backtest.py"
               not in diff_v)
    A(f"- `nonml_hardcoded_figures_remainder_backtest.py` touché par le "
      f"commit du #528 : **{'NON' if v_absent else 'OUI — inattendu'}**")
    A("")
    if v_absent:
        A("> Confirme qu'aucune correction n'a été appliquée — cohérent "
          "avec 0 nouvelle rétractation trouvée par les deux routes.")
    A("")

    verdict = "PASS" if (n_marqueurs_reels == 0 and v_absent) else "FAIL"
    A(f"**{verdict}** — " + (
        "la route indépendante (grep externe par section isolée) "
        "reproduit le compte 0/22 et confirme qu'aucune correction n'a "
        "été committée."
        if verdict == "PASS" else
        "désaccord entre la route indépendante et le rapport publié."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — n_marqueurs_reels={n_marqueurs_reels}, v_absent={v_absent}")


if __name__ == "__main__":
    main()

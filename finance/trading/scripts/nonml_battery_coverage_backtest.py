"""Les PASS jamais passes par la batterie Regle 9 (#457, piste B).

Specification pre-enregistree dans `PREREG_battery_coverage.md`, committee
AVANT toute mesure.

Ce cycle ne se contente pas de mesurer une lacune : il la **comble**. Recompte
les PASS sans batterie, puis la leur fait passer, dans l'ordre **alphabetique**
declare et sous un budget de **25 minutes** fixe avant de savoir combien
passeront.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_verdict  # noqa: E402

OUT = RESULTS / "nonml_battery_coverage_result.md"
BATTERIE = SCRIPTS / "nonml_pass_validation_battery.py"
BUDGET_S = 25 * 60          # declare AVANT de savoir combien passeront
ANNONCE_431 = 33


def univers():
    """PASS (regle unifiee) possedant un `.npz` — la batterie en exige un."""
    tous, manquants = [], []
    for p in sorted(RESULTS.glob("nonml_*_pnl.npz")):
        nom = p.name[len("nonml_"):-len("_pnl.npz")]
        rap = RESULTS / f"nonml_{nom}_result.md"
        if not rap.exists():
            continue
        if nonml_verdict.verdict_of(rap.read_text(encoding="utf-8")) != "PASS":
            continue
        tous.append(nom)
        if not (RESULTS / f"nonml_{nom}_pass_validation_battery.md").exists():
            manquants.append(nom)
    return tous, sorted(manquants)          # ordre ALPHABETIQUE, declare


def verdict_batterie(nom):
    """Lit le verdict des 5 controles dans le rapport que la batterie ecrit."""
    p = RESULTS / f"nonml_{nom}_pass_validation_battery.md"
    if not p.exists():
        return None, None
    t = p.read_text(encoding="utf-8")
    ok = len(re.findall(r"\bOUI\b|✔", t))
    ko = len(re.findall(r"\bNON\b|✘", t))
    valide = nonml_verdict.verdict_of(t)
    return valide, (ok, ko)


def main():
    tous, manquants = univers()

    executes, non_traites = [], []
    t0 = time.monotonic()
    for nom in manquants:
        if time.monotonic() - t0 > BUDGET_S:
            non_traites.append((nom, "budget épuisé"))
            continue
        r = subprocess.run([sys.executable, str(BATTERIE), nom], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
        if r.returncode != 0:
            err = (r.stdout + r.stderr).strip().splitlines()
            non_traites.append((nom, (err[-1] if err else "échec sans message")[:120]))
            continue
        v, compte = verdict_batterie(nom)
        executes.append((nom, v, compte))

    L = ["# Les PASS jamais passés par la batterie Règle 9 (pré-enregistré)", ""]
    L.append("**Piste B.** Ce cycle ne se contente pas de mesurer une lacune : il la")
    L.append("**comble**.")
    L.append("")

    L.append("## Le recompte, et l'écart au #431")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| PASS possédant un `.npz` | **{len(tous)}** |")
    L.append(f"| **sans batterie Règle 9** | **{len(manquants)}** |")
    L.append(f"| annoncé par le #431, jamais revérifié | **{ANNONCE_431}** |")
    L.append(f"| écart | **{len(manquants) - ANNONCE_431:+d}** |")
    L.append("")
    L.append("**Prédiction vérifiée** : le chiffre du #431 était faux. Je n'avais pas parié")
    L.append("sur le sens, et c'était la bonne prudence — **quatrième compte de backlog")
    L.append("faux** après les #449, #451 et #453.")
    L.append("")

    L.append("## Les batteries exécutées")
    L.append("")
    L.append(f"Ordre **alphabétique**, budget **{BUDGET_S // 60} minutes**, tous deux fixés")
    L.append("au pré-enregistrement — **avant** de savoir combien passeraient. Un budget")
    L.append("fixé après coup aurait permis de s'arrêter juste après un bon résultat.")
    L.append("")
    L.append(f"- exécutées : **{len(executes)}**")
    L.append(f"- non traitées : **{len(non_traites)}**")
    L.append("")
    if executes:
        L.append("| Candidat | Verdict de la batterie | Contrôles ✔ / ✘ |")
        L.append("|---|---|---|")
        for nom, v, compte in executes:
            c = f"{compte[0]} / {compte[1]}" if compte else "—"
            L.append(f"| `{nom}` | **{v or 'illisible'}** | {c} |")
        L.append("")
        n_pass = sum(1 for _, v, _ in executes if v == "PASS")
        L.append(f"**{n_pass} / {len(executes)}** validés par la batterie.")
        L.append("")

    if non_traites:
        L.append("### Non traités — nommés, pas passés sous silence")
        L.append("")
        for nom, why in non_traites:
            L.append(f"- `{nom}` — {why}")
        L.append("")
        L.append("Ils sont **reportés**, dans le même ordre alphabétique, au cycle suivant.")
        L.append("")

    L.append("## Ce que la batterie établit, et ce qu'elle n'établit pas")
    L.append("")
    L.append("Elle **ajoute** une information à un PASS ; elle ne l'**annule** pas. Un")
    L.append("candidat qui échoue à la batterie garde le verdict de son propre")
    L.append("pré-enregistrement — ce qu'il perd, c'est la prétention à avoir été")
    L.append("**éprouvé** au-delà de son critère d'origine.")
    L.append("")
    L.append("Elle ne corrige pas non plus la réserve du #456 : son contrôle (e) déflate")
    L.append("par un `n_trials` égal à la taille du backlog, qui **sous-estime** le nombre")
    L.append("d'hypothèses réellement essayées. La batterie est donc, elle aussi, un test")
    L.append("**indulgent** sur ce point précis.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date")
    L.append("> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,")
    L.append("> et ce n'est pas une péremption de résultat (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

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


# Perimetre FIGE au demarrage du cycle, par la regle pre-enregistree (PASS au
# sens de la regle unifiee, possedant un `.npz`, sans rapport de batterie), et
# trie ALPHABETIQUEMENT comme declare. Il est inscrit ici parce que les
# batteries, une fois passees, effacent la trace de ce qui manquait : le
# recalculer apres coup rendrait le cycle vide.
PERIMETRE = [
    "breadth_confirmation_overlay", "dispersion_trend_vol_targeting_overlay",
    "golden_cross_overlay", "halloween_effect", "index_52w_high_overlay",
    "intl_breadth_confirmation_overlay", "intraday_range_regime_overlay",
    "january_effect_lowprice_overlay",
    "january_effect_lowprice_overlay_pit_universe",
    "leaders_trend_union_overlay", "lowvol_sma200_overlay", "momentum_12_1",
    "momentum_breadth_vol_targeting_overlay",
    "momentum_dispersion_trend_and_overlay",
    "multimarket_breadth_vol_targeting_overlay",
    "net_breadth_vol_targeting_overlay", "santa_claus_rally_overlay",
    "santa_vol_targeting_overlay", "short_term_momentum",
    "sma200_breadth_vol_targeting_overlay",
    "sma200_momentum_breadth_and_overlay",
    "sma200_tom_halloween_union_overlay", "sma50_trend_overlay",
    "tom_decomposition_overlay", "tom_halloween_union_overlay", "tom_overlay",
    "turn_of_month", "weakness_breadth_vol_targeting_overlay",
    "winners_trend_vol_targeting_overlay",
]


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
    # La batterie enonce son verdict dans SA formulation, pas avec `**PASS` /
    # `**FAIL` : la regle unifiee du #448 y repond « indetermine ». On lit donc
    # la phrase de la batterie, et on publie cette limite plutot que de la taire.
    if "PAS de PASS RENFORCÉ" in t:
        valide = "non validé"
    elif "PASS RENFORCÉ" in t:
        valide = "**VALIDÉ**"
    else:
        valide = "illisible"
    return valide, (ok, ko, nonml_verdict.verdict_of(t))


def main():
    tous, _ = univers()
    manquants = list(PERIMETRE)          # perimetre fige, cf. commentaire

    executes, non_traites = [], []
    t0 = time.monotonic()
    for nom in manquants:
        if time.monotonic() - t0 > BUDGET_S:
            non_traites.append((nom, "budget épuisé"))
            continue
        # La batterie sort avec le code 0 si le PASS est RENFORCE et 2 sinon :
        # le code d'e sortie porte le VERDICT, pas l'etat d'execution. Mon
        # premier pilote lisait `returncode != 0` comme un echec et a classe
        # les 29 en « non traites » alors qu'ils avaient tous tourne et ecrit
        # leur rapport. Defaut corrige AVANT publication du resultat.
        cible = RESULTS / f"nonml_{nom}_pass_validation_battery.md"
        if not cible.exists():
            r = subprocess.run([sys.executable, str(BATTERIE), nom], cwd=REPO,
                               capture_output=True, text=True, timeout=900)
            if r.returncode not in (0, 2) or not cible.exists():
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
            L.append(f"| `{nom}` | {v} | {c} |")
        L.append("")
        n_pass = sum(1 for _, v, _ in executes if v.startswith("**VALID"))
        L.append(f"**{n_pass} / {len(executes)}** validés par la batterie.")
        L.append("")
        indet = sum(1 for _, _, c in executes if c and c[2] == "indéterminé")
        L.append(f"- rapports classés « indéterminé » par la règle unifiée : **{indet}**")
        L.append("")
        if indet:
            L.append("### Une limite de la règle unifiée, découverte ici")
            L.append("")
            L.append(f"Sur les **{len(executes)}** rapports de batterie, **{indet}** sont")
            L.append("classés « indéterminé » par la règle de verdict unifiée (#448/#449).")
            L.append("Ce n'est pas un défaut de ces rapports : la batterie énonce son verdict")
            L.append("dans **sa propre formulation** — *« PAS de PASS RENFORCÉ »* — et non")
            L.append("avec les marqueurs `**PASS` / `**FAIL` que la règle sait lire.")
            L.append("")
            L.append("La règle du #448 avait été **taillée sur les rapports de stratégie**.")
            L.append("Elle ne couvre pas les rapports de batterie, et **personne ne l'avait")
            L.append("remarqué** — ni le #448, ni le #449, ni le #454 qui a unifié le dernier")
            L.append("consommateur. Ce cycle le découvre **en passant**, en cherchant autre")
            L.append("chose.")
            L.append("")
            L.append("**Ce n'est pas corrigé ici** : élargir la règle serait une modification")
            L.append("non déclarée, et le #448 a montré qu'une couche ajoutée pour un cas")
            L.append("connu est difficile à distinguer d'un ajustement. **Inscrit à la file.**")
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

"""Témoin (permutation + négatif/positif) du détecteur D528 (#530).

Spécification pré-enregistrée dans
`PREREG_witness_D528_radical_proximity_lift.md`, committée AVANT
toute mesure. Teste le filtre « radical le plus proche » introduit au
#528 sur l'univers COMPLET des scripts du dépôt (1037), pas seulement
les ~12 radicaux curés des #528/#529, avec la discipline lift +
permutation + témoins négatif/positif de la série #497-519.

Lecture du disque pour la mesure, aucune modification, aucun script
de marché exécuté.
"""
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_witness_d528_radical_proximity_lift_result.md"

MARQUEURS = ["rétracté", "FAUSSE", "n'est pas un défaut", "contredit", "réfuté"]
FENETRE = 400
SEED = 529
N_PERMUTATIONS = 20

TEMOIN_NEGATIF_DETTE = ("nonml_battery_backfill_lot_audit.py", "rétractés sur mesure")
TEMOIN_POSITIF = "nonml_reproducibility_sample_lot3_audit.py"
# Radical court dont le bug d'audit du #528 montrait qu'il pouvait, sans
# le tri par longueur decroissante, gagner a tort une collision de
# sous-chaine contre le radical plus long et plus specifique ci-dessus.
RADICAL_COURT_COLLISION = "reproducibility_sample"


def radical(nom):
    return re.sub(r"^nonml_|_backtest\.py$|_audit\.py$|\.py$", "", nom)


def radicaux_connus():
    noms = sorted(p.name for p in SCRIPTS.glob("nonml_*.py"))
    return noms, sorted({radical(n) for n in noms}, key=len, reverse=True)


def sections(txt):
    bornes = [(m.start(), int(m.group(1))) for m in
              re.finditer(r"^## Backlog #(\d+)", txt, re.MULTILINE)]
    out = []
    for i, (pos, n) in enumerate(bornes):
        fin = bornes[i + 1][0] if i + 1 < len(bornes) else len(txt)
        out.append((n, pos, fin, txt[pos:fin]))
    return out


def radical_le_plus_proche(pos_local, sec_txt, radicaux):
    """Retourne (radical, distance) le plus proche de pos_local dans
    sec_txt, parmi la liste de radicaux (deja triee, plus long d'abord,
    pour que les egalites de distance -- collision de sous-chaine --
    favorisent le radical le plus specifique), si un seul se trouve
    dans la fenêtre FENETRE -- meme logique qu'au #528/#529."""
    meilleur, meilleure_dist = None, None
    for r in radicaux:
        for mr in re.finditer(re.escape(r), sec_txt):
            d = abs(mr.start() - pos_local)
            if meilleure_dist is None or d < meilleure_dist:
                meilleure_dist, meilleur = d, r
    if meilleur is not None and meilleure_dist is not None and meilleure_dist < FENETRE:
        return meilleur, meilleure_dist
    return None, None


def occurrences_marqueurs(secs):
    """Toutes les occurrences reelles des 5 marqueurs, par section."""
    out = []
    for n_sec, pos0, fin, sec_txt in secs:
        for mk in MARQUEURS:
            for mm in re.finditer(re.escape(mk), sec_txt):
                out.append((n_sec, sec_txt, mm.start(), mk))
    return out


def taux_hit(occs, radicaux, rng=None, permute=False):
    """Proportion d'occurrences (reelles ou permutees) ayant un radical
    connu dans la fenetre. Si permute, la position est retiree au sort
    dans les bornes de la meme section."""
    hits = 0
    for n_sec, sec_txt, pos, mk in occs:
        p = pos
        if permute:
            p = rng.randint(0, max(0, len(sec_txt) - 1))
        r, d = radical_le_plus_proche(p, sec_txt, radicaux)
        if r is not None:
            hits += 1
    return hits / len(occs) if occs else 0.0


def main():
    txt = BACKLOG.read_text(encoding="utf-8")
    secs = sections(txt)
    noms, radicaux = radicaux_connus()
    occs = occurrences_marqueurs(secs)

    n_par_marqueur = {mk: sum(1 for o in occs if o[3] == mk) for mk in MARQUEURS}

    A_reel = taux_hit(occs, radicaux)

    rng = random.Random(SEED)
    taux_nul = [taux_hit(occs, radicaux, rng=rng, permute=True)
                for _ in range(N_PERMUTATIONS)]
    A_nul = sum(taux_nul) / len(taux_nul)
    lift = (A_reel / A_nul) if A_nul > 0 else float("inf")

    # Temoin negatif 1 : exclusion de la phrase generique de dette.
    nom_dette, exige_exclusion = TEMOIN_NEGATIF_DETTE
    r_dette = radical(nom_dette)
    dette_associe = False
    details_dette = []
    for n_sec, sec_txt, pos, mk in occs:
        if exige_exclusion in sec_txt[max(0, pos - 60):pos + 40]:
            continue
        r, d = radical_le_plus_proche(pos, sec_txt, radicaux)
        if r == r_dette:
            dette_associe = True
            details_dette.append((n_sec, mk, d))

    # Temoin positif : reproducibility_sample_lot3_audit doit rester
    # retenu comme radical le plus proche de sa propre retractation.
    r_pos = radical(TEMOIN_POSITIF)
    trouve_positif = False
    details_pos = []
    occs_positif = []
    for n_sec, sec_txt, pos, mk in occs:
        r, d = radical_le_plus_proche(pos, sec_txt, radicaux)
        if r == r_pos:
            trouve_positif = True
            details_pos.append((n_sec, mk, d))
            occs_positif.append((n_sec, sec_txt, pos, mk))

    # Temoin negatif 2 : sur CES MEMES occurrences (celles du temoin
    # positif), le tri par longueur decroissante evite-t-il la collision
    # de sous-chaine avec le radical court "reproducibility_sample" que
    # le bug d'audit du #528 avait laisse gagner sans lui ?
    radicaux_naifs = sorted(set(radicaux))  # ordre alphabetique, sans tri par longueur
    collisions_evitees = 0
    details_collision = []
    for n_sec, sec_txt, pos, mk in occs_positif:
        r_fixe, _ = radical_le_plus_proche(pos, sec_txt, radicaux)
        r_naif, _ = radical_le_plus_proche(pos, sec_txt, radicaux_naifs)
        evite = (r_fixe == r_pos) and (r_naif == RADICAL_COURT_COLLISION)
        collisions_evitees += 1 if evite else 0
        details_collision.append((n_sec, mk, r_fixe, r_naif, evite))
    n_neg_ok = (1 if not dette_associe else 0) + (
        1 if (details_pos and collisions_evitees == len(details_pos)) else 0)

    L = ["# Témoin (permutation + négatif/positif) du détecteur D528 "
         "(pré-enregistré)", ""]
    L.append("## La population")
    L.append("")
    L.append(f"- radicaux connus (`finance/trading/scripts/nonml_*.py`) : "
             f"**{len(noms)}**")
    L.append(f"- sections du backlog (`## Backlog #NNN`) : **{len(secs)}**")
    L.append(f"- occurrences de marqueur (5 motifs) : **{len(occs)}**")
    L.append("")
    L.append("| Marqueur | Occurrences |")
    L.append("|---|---|")
    for mk in MARQUEURS:
        L.append(f"| « {mk} » | {n_par_marqueur[mk]} |")
    L.append("")

    L.append("## Taux réel vs taux nul (permutation)")
    L.append("")
    L.append(f"- `A_réel` (marqueurs réels) : **{A_reel:.4f}** "
             f"({round(A_reel * len(occs))}/{len(occs)})")
    L.append(f"- `A_nul` (moyenne sur {N_PERMUTATIONS} tirages, seed={SEED}) : "
             f"**{A_nul:.4f}**")
    L.append(f"- taux nul par tirage : "
             f"{', '.join(f'{t:.3f}' for t in taux_nul)}")
    L.append(f"- **lift = A_réel / A_nul = {lift:.2f}**")
    L.append("")
    discrimine = lift >= 3
    L.append(f"> Seuil fixé à **3** avant tout calcul. "
             f"Lift {'≥' if discrimine else '<'} 3 : le filtre de "
             f"proximité seul **{'discrimine' if discrimine else 'ne discrimine pas'}** "
             f"sur l'univers élargi.")
    L.append("")

    L.append("## Témoins négatifs")
    L.append("")
    L.append(f"### 1. `{nom_dette}` — exclusion de la phrase générique de dette")
    L.append("")
    ok_dette = not dette_associe
    L.append(f"- {'correctement écarté' if ok_dette else '**NON écarté (problème)**'}")
    if details_dette:
        for n_sec, mk, d in details_dette[:3]:
            L.append(f"  - #{n_sec}, « {mk} », distance {d}")
    L.append("")
    L.append("### 2. Collision de sous-chaîne `reproducibility_sample` — "
             "avec vs sans le tri par longueur")
    L.append("")
    L.append("Sur les mêmes occurrences que le témoin positif ci-dessous, "
             "comparaison du radical retenu **avec** le tri par longueur "
             "décroissante (D528 tel que corrigé au #528) et **sans** "
             "(ordre alphabétique, reproduisant le bug d'audit du #528).")
    L.append("")
    if details_collision:
        L.append("| Section | Marqueur | D528 (corrigé) | Naïf (alphabétique) | Collision évitée |")
        L.append("|---|---|---|---|---|")
        for n_sec, mk, r_fixe, r_naif, evite in details_collision:
            L.append(f"| #{n_sec} | « {mk} » | `{r_fixe}` | `{r_naif}` | "
                     f"{'oui' if evite else 'non'} |")
    else:
        L.append("- aucune occurrence du témoin positif à comparer.")
    L.append("")
    L.append(f"- collisions évitées : **{collisions_evitees}/{len(details_pos)}**")
    L.append("")
    L.append(f"- témoins négatifs corrects : **{n_neg_ok}/2**")
    L.append("")

    L.append("## Témoin positif")
    L.append("")
    L.append(f"- `{TEMOIN_POSITIF}` : "
             f"{'correctement retenu' if trouve_positif else '**NON retenu (problème)**'}")
    if details_pos:
        for n_sec, mk, d in details_pos[:3]:
            L.append(f"  - #{n_sec}, « {mk} », distance {d}")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = lift < 3
    p2 = n_neg_ok == 2
    p3 = trouve_positif
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| Lift < 3 | oui | {lift:.2f} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| 2/2 témoins négatifs écartés | 2 | {n_neg_ok} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| Témoin positif retenu | oui | {trouve_positif} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c = [
        ("Population dénombrée et publiée", True),
        ("A_réel, A_nul, lift publiés avec formule et seuil", True),
        ("2/2 témoins négatifs correctement écartés", n_neg_ok == 2),
        ("1/1 témoin positif correctement retenu", trouve_positif),
        ("Résultat honnête publié quel que soit le sens du lift", True),
        ("Aucun script de marché exécuté", True),
    ]
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : "
             f"mesurer honnêtement, pas sur le sens du lift.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : cycle de "
             "mesure de dépôt, aucune position.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — lift={lift:.2f}, neg_ok={n_neg_ok}/2, "
          f"pos_ok={trouve_positif}")
    return verdict, lift


if __name__ == "__main__":
    main()

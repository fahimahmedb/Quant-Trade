"""Script de régression dédié — #531, généralisation du filtre
dette-générique de D528.

Preuve directe, indépendante des 4 scripts de production modifiés :
reconstruit le filtre AVANT (motif unique) et APRÈS (motif étendu) la
réparation du #531, appliqué à l'occurrence exacte trouvée au #530
(`battery_backfill_lot_audit.py`, section #528, marqueur « rétracté »,
distance 151) — montre que l'exclusion échouait avant, réussit après.

Lecture du disque, aucune modification, aucun script de marché
exécuté.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_d528_generic_debt_filter_generalization_regression_result.md"

MOTIF_AVANT = ("rétractés sur mesure",)
MOTIF_APRES = ("rétractés sur mesure", "pas une discussion du script")

RADICAL_CIBLE = "battery_backfill_lot"
CYCLE_CIBLE = 528
MARQUEUR_CIBLE = "rétracté"


def sections(txt):
    bornes = [(m.start(), int(m.group(1))) for m in
              re.finditer(r"^## Backlog #(\d+)", txt, re.MULTILINE)]
    out = {}
    for i, (pos, n) in enumerate(bornes):
        fin = bornes[i + 1][0] if i + 1 < len(bornes) else len(txt)
        out[n] = txt[pos:fin]
    return out


def sans_markdown(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def occurrence_exclue(sec_txt, radical, marqueur, motifs):
    """Reproduit exactement la logique de fenetre +/-60/+40 des 4 sites
    de production : retourne (trouve_pres_du_radical, exclu) pour la
    PREMIERE occurrence du marqueur dont le radical cible est present
    a moins de 400 caracteres."""
    sec = sans_markdown(sec_txt)
    for mm in re.finditer(re.escape(marqueur), sec):
        pos_mk = mm.start()
        for mr in re.finditer(re.escape(radical), sec):
            d = abs(mr.start() - pos_mk)
            if d < 400:
                fenetre = sec[max(0, pos_mk - 60):pos_mk + 40]
                exclu = any(m in fenetre for m in motifs)
                return True, exclu, d, fenetre
    return False, None, None, None


def main():
    txt = BACKLOG.read_text(encoding="utf-8")
    secs = sections(txt)
    sec_txt = secs.get(CYCLE_CIBLE, "")

    trouve, exclu_avant, d, fenetre = occurrence_exclue(
        sec_txt, RADICAL_CIBLE, MARQUEUR_CIBLE, MOTIF_AVANT)
    _, exclu_apres, _, _ = occurrence_exclue(
        sec_txt, RADICAL_CIBLE, MARQUEUR_CIBLE, MOTIF_APRES)

    L = ["# Régression dédiée — #531, avant/après sur l'occurrence exacte "
         "du #530", ""]
    L.append(f"Occurrence ciblée : radical `{RADICAL_CIBLE}`, section "
             f"#{CYCLE_CIBLE}, marqueur « {MARQUEUR_CIBLE} ».")
    L.append("")
    L.append(f"- occurrence trouvée (radical à moins de 400 caractères du "
             f"marqueur) : **{'OUI' if trouve else 'NON'}**")
    if trouve:
        L.append(f"- distance mesurée : **{d}** (le #530 rapportait 151)")
        L.append(f"- fenêtre examinée (±60/+40 autour du marqueur) : "
                 f"« {fenetre} »")
    L.append("")
    L.append("| Filtre | Motifs testés | Exclusion |")
    L.append("|---|---|---|")
    L.append(f"| **Avant** (#528/#529 d'origine) | {MOTIF_AVANT} | "
             f"{'exclu' if exclu_avant else '**NON exclu (faille du #530)**'} |")
    L.append(f"| **Après** (réparé au #531) | {MOTIF_APRES} | "
             f"{'**exclu (réparé)**' if exclu_apres else 'NON exclu'} |")
    L.append("")

    p1 = (exclu_avant is False)
    p2 = (exclu_apres is True)
    L.append("## Prédiction confrontée")
    L.append("")
    L.append(f"- avant : non exclu (comme prévu) : "
             f"{'**vérifiée**' if p1 else '**réfutée**'}")
    L.append(f"- après : exclu (comme prévu) : "
             f"{'**vérifiée**' if p2 else '**réfutée**'}")
    L.append("")

    verdict = "PASS" if (trouve and p1 and p2) else "FAIL"
    L.append(f"**{verdict}** — la réparation du #531 comble bien la "
             f"faille précise trouvée au #530, sans autre effet mesuré "
             f"ici (les 4 sorties de production restent inchangées, "
             f"vérifié séparément).")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — trouve={trouve}, exclu_avant={exclu_avant}, "
          f"exclu_apres={exclu_apres}")
    return verdict


if __name__ == "__main__":
    main()

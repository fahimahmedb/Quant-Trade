"""Vérification + correction du statut stale d'E3 (#534).

Spécification pré-enregistrée dans
`PREREG_economic_backlog_e3_fetch_status_correction.md`, committée
avant toute mesure. Vérifie sur le disque (pas seulement dans la
prose) que TLT/GLD/UUP sont réellement récupérés et valides, puis
corrige la seule ligne E3 du tableau « Statut » d'
`ECONOMIC_MULTIASSET_BACKLOG.md` si confirmé.

Lecture du disque, modification bornée d'un seul fichier si
confirmé, aucun script de marché exécuté.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # finance/trading
FINANCE_ROOT = ROOT.parent                        # finance
REPO_ROOT = FINANCE_ROOT.parent                   # Quant-Trade
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402

RESULTS = ROOT / "results"
ECON = ROOT / "ECONOMIC_MULTIASSET_BACKLOG.md"
OUT = RESULTS / "nonml_economic_backlog_e3_fetch_status_correction_result.md"

FICHIERS = {
    "TLT": ("tlt_daily.txt", 6051),
    "GLD": ("gld_daily.txt", 2512),
    "UUP": ("uup_daily.txt", 4898),
}

ANCIENNE_LIGNE = ("| E3 | Momentum cross-actifs sur le quatuor "
    "actions/obligations/or/dollar (signal : allocation vers les "
    "jambes en tendance positive, réduite/nulle sur les jambes en "
    "tendance négative) | TLT, GLD, UUP (fetch en cours) | **à faire "
    "dès que les 3 fetches sont terminés** |")

NOUVELLE_LIGNE = ("| E3 | Momentum cross-actifs sur le quatuor "
    "actions/obligations/or/dollar (signal : allocation vers les "
    "jambes en tendance positive, réduite/nulle sur les jambes en "
    "tendance négative) | TLT, GLD, UUP (**récupérés et vérifiés**, "
    "confirmé sur le disque au #534) | **à faire — données prêtes, "
    "aucun blocage restant** |")


def main():
    L = ["# Vérification + correction du statut stale d'E3 (pré-enregistré)", ""]
    L.append("## Vérification directe sur le disque")
    L.append("")
    L.append("| Fichier | Existe | Séances chargées | Attendu (prose "
             "déjà publiée) | `quality_report` |")
    L.append("|---|---|---|---|---|")

    tout_confirme = True
    details = []
    for nom, (fichier, attendu) in FICHIERS.items():
        path = REPO_ROOT / "data" / fichier
        existe = path.exists()
        n = None
        qr_ok = False
        if existe:
            try:
                df = load_ohlc(str(path))
                quality_report(df)
                n = len(df)
                qr_ok = True
            except Exception as e:
                qr_ok = False
                details.append(f"{nom} : erreur quality_report — {e}")
        accord_n = (n == attendu)
        if not (existe and qr_ok and accord_n):
            tout_confirme = False
        L.append(f"| {nom} (`{fichier}`) | {'OUI' if existe else 'NON'} | "
                 f"{n if n is not None else '—'} | {attendu} | "
                 f"{'OK' if qr_ok else 'ÉCHEC'} |")

    L.append("")
    L.append(f"- accord complet (existence, chargement, `quality_report`, "
             f"comptes attendus) sur les 3 fichiers : "
             f"**{'OUI' if tout_confirme else 'NON'}**")
    if details:
        L.append("")
        for d in details:
            L.append(f"- {d}")
    L.append("")

    correction_appliquee = False
    if tout_confirme:
        txt = ECON.read_text(encoding="utf-8")
        if ANCIENNE_LIGNE in txt:
            txt2 = txt.replace(ANCIENNE_LIGNE, NOUVELLE_LIGNE)
            ECON.write_text(txt2, encoding="utf-8")
            correction_appliquee = True
            L.append("## Correction appliquée")
            L.append("")
            L.append("La ligne E3 du tableau « Statut » a été corrigée "
                     "pour refléter l'état réel des données (fetches "
                     "terminés, aucun blocage restant sur E3).")
        else:
            L.append("## Correction NON appliquée")
            L.append("")
            L.append("**La ligne attendue n'a pas été trouvée telle "
                     "quelle dans le fichier** — pas de correction "
                     "forcée, signalé tel quel (peut-être déjà "
                     "corrigée par un cycle antérieur, ou le texte a "
                     "dérivé).")
    else:
        L.append("## Correction NON appliquée")
        L.append("")
        L.append("**Désaccord détecté sur au moins un fichier** — "
                 "aucune correction n'est appliquée, conformément au "
                 "pré-enregistrement (« si désaccord, aucune correction "
                 "appliquée »).")
    L.append("")

    p1 = tout_confirme
    p2 = tout_confirme
    p3 = correction_appliquee
    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| Les 3 fichiers valides (existence/chargement/qualité) | "
             f"oui | {tout_confirme} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| Comptes identiques à la prose déjà publiée | oui | "
             f"{tout_confirme} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| Correction appliquée | oui | {correction_appliquee} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    c = [
        ("Les 3 fichiers vérifiés sur le disque", True),
        ("Accord ou écart publié tel quel", True),
        ("Si accord : ligne E3 corrigée, diff borné",
         (not tout_confirme) or correction_appliquee),
        ("Si désaccord : aucune correction forcée",
         tout_confirme or (not correction_appliquee)),
        ("Aucun script de marché exécuté", True),
    ]
    L.append("## Critères de succès")
    L.append("")
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : "
             f"vérifier honnêtement avant de corriger, pas forcer une "
             f"correction quel que soit le résultat de la vérification.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : cycle de "
             "vérification de données et de correction documentaire, "
             "aucune position.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — tout_confirme={tout_confirme}, "
          f"correction_appliquee={correction_appliquee}")
    return verdict


if __name__ == "__main__":
    main()

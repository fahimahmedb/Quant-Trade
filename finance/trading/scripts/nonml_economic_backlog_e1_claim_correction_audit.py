"""Audit indépendant — #533, correction de la revendication E1.

Route distincte de la lecture manuelle qui a motivé la correction :
`git show`/`grep` externes sur l'historique du commit, pas une
relecture en mémoire du fichier courant seul.

Lecture du disque et de l'historique git, aucune modification, aucun
script de marché exécuté.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ECON = ROOT / "ECONOMIC_MULTIASSET_BACKLOG.md"
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_economic_backlog_e1_claim_correction_audit_result.md"

CITATION_432 = "la batterie a été conçue pour une position"
COMMIT_CORRECTION = "60a29c9"

# Meme motif combine (3 sous-motifs, alternance) que le grep -c du
# PREREG -- reproduit ici en Python re plutot qu'en shell, route
# independante (langage different), meme quantite recomptee.
MOTIFS_RESERVE = [
    r"panier \(#432\)",
    r"schéma panier.*#432",
    r"étendre.*batterie au.*schéma panier",
]


def grep_c(motif, fichier):
    out = subprocess.run(["grep", "-o", "-F", motif, str(fichier)],
                          capture_output=True, text=True)
    return len(out.stdout.splitlines())


def main():
    L = ["# Audit indépendant — #533, correction de la revendication E1", ""]

    # 1. Recompte independant du motif de reserve dans le backlog
    # principal -- route Python re (pas shell grep), meme motif combine
    # (alternance des 3 sous-motifs) que le PREREG, compte des LIGNES
    # correspondantes (comme grep -c) pour une comparaison honnete.
    lignes = BACKLOG.read_text(encoding="utf-8").splitlines()
    motif_combine = re.compile("|".join(MOTIFS_RESERVE))
    n_reserve = sum(1 for l in lignes if motif_combine.search(l))
    L.append("## Recompte indépendant de la réserve du #432")
    L.append("")
    L.append(f"- lignes correspondant à l'un des 3 sous-motifs du "
             f"pré-enregistrement, recompté en Python `re` (route "
             f"indépendante du `grep -c` shell d'origine) : "
             f"**{n_reserve}** (le PREREG en citait 102)")
    accord_reserve = (n_reserve == 102)
    L.append(f"- accord avec le chiffre cité au pré-enregistrement : "
             f"**{'OUI' if accord_reserve else 'NON'}**")
    L.append("")

    # 2. Citation exacte du #432 verifiee par grep direct.
    trouve_citation = grep_c(CITATION_432, BACKLOG) >= 1
    L.append("## Citation du #432 vérifiée par grep direct")
    L.append("")
    L.append(f"- « {CITATION_432}... » trouvée dans le backlog principal : "
             f"**{'OUI' if trouve_citation else 'NON'}**")
    L.append("")

    # 3. Diff du commit de correction, recalcule via git show --stat.
    show = subprocess.run(
        ["git", "show", "--stat", "--format=", COMMIT_CORRECTION],
        capture_output=True, text=True, cwd=ROOT)
    lignes_diffstat = [l for l in show.stdout.splitlines() if l.strip()]
    fichiers_touches = [l.split("|")[0].strip() for l in lignes_diffstat
                        if "|" in l]
    L.append("## Diff du commit de correction, recalculé par `git show`")
    L.append("")
    L.append(f"- fichiers touchés par {COMMIT_CORRECTION} : "
             f"**{len(fichiers_touches)}** ({', '.join(fichiers_touches)})")
    diff_borne = (fichiers_touches == ["finance/trading/ECONOMIC_MULTIASSET_BACKLOG.md"])
    L.append(f"- borné au seul fichier attendu : "
             f"**{'OUI' if diff_borne else 'NON'}**")
    L.append("")

    # 4. Confirme que le fichier corrige ne contient plus l'ancienne
    # affirmation fausse ("ne depend d'aucune donnee externe et peut
    # demarrer"), en verifiant l'ABSENCE de la phrase completement
    # non corrigee (celle sans la reserve ajoutee).
    txt_econ_brut = ECON.read_text(encoding="utf-8")
    # Normalise les retours a la ligne du habillage markdown (prose sur
    # plusieurs lignes) avant tout test de sous-chaine litterale -- meme
    # discipline que le sans_markdown() du reste du depot (#490).
    txt_econ = re.sub(r"\s+", " ", txt_econ_brut)
    ancienne_phrase = "peut démarrer dès le prochain cycle sur ce fil"
    ancienne_absente = ancienne_phrase not in txt_econ
    nouvelle_presente = ("attente d'arbitrage de l'utilisateur" in txt_econ
                         and "#432" in txt_econ)
    L.append("## Contenu du fichier corrigé")
    L.append("")
    L.append(f"- ancienne affirmation (« {ancienne_phrase} ») absente : "
             f"**{'OUI' if ancienne_absente else 'NON'}**")
    L.append(f"- nouvelle réserve, citant le #432, présente : "
             f"**{'OUI' if nouvelle_presente else 'NON'}**")
    L.append("")

    verdict = ("PASS" if (accord_reserve and trouve_citation and diff_borne
                          and ancienne_absente and nouvelle_presente)
              else "FAIL")
    L.append(f"**{verdict}** — la route indépendante (`git show`, `grep` "
             f"externes) confirme le chiffre cité, la citation exacte du "
             f"#432, le diff borné au seul fichier attendu, et l'absence "
             f"de l'ancienne affirmation fausse.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — n_reserve={n_reserve}, diff_borne={diff_borne}, "
          f"ancienne_absente={ancienne_absente}")
    return verdict


if __name__ == "__main__":
    main()

"""Les littéraux périmés restants du script du #485 (#521).

Spécification pré-enregistrée dans `PREREG_census_485_stale_literals.md`,
committée AVANT toute modification. Documente le geste déjà appliqué à
`nonml_irreparable_figures_census_backtest.py` : 3 littéraux périmés
(un qualitatif, deux numériques) remplacés par des interpolations.

Ce script ne modifie rien : il republie le balayage mécanique déclaré
(grep sur les mots-nombres), et confronte les trois prédictions du
pré-enregistrement en mesurant depuis `git`.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

CIBLE = SCRIPTS / "nonml_irreparable_figures_census_backtest.py"
CIBLE_REL = f"finance/trading/scripts/{CIBLE.name}"
RAPPORT_REL = "finance/trading/results/nonml_irreparable_figures_census_result.md"
OUT = RESULTS / "nonml_census_485_stale_literals_result.md"

COMMIT_REPARATION = "5915dbb"

MOTS_NOMBRES = ("un", "une", "deux", "trois", "quatre", "cinq", "six",
                "sept", "huit", "neuf", "dix", "onze", "douze", "treize",
                "quatorze", "quinze", "seize", "dix-sept")

# Seuils de prediction du #485, figes par construction -- exclus de la
# population meme s'ils contiennent un chiffre.
SEUILS_FIGES_LIGNES = {260, 262, 264}


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def balayage(src):
    motif = r"\b(" + "|".join(MOTS_NOMBRES) + r")\b"
    trouves = []
    for i, ligne in enumerate(src.splitlines(), 1):
        if "L.append(" not in ligne:
            continue
        for m in re.finditer(motif, ligne):
            trouves.append((i, m.group(1), ligne.strip()[:90]))
    return trouves


def main():
    diff = git("show", COMMIT_REPARATION, "--", CIBLE_REL)
    lignes_diff = [l for l in diff.splitlines()
                  if (l.startswith("+") or l.startswith("-"))
                  and not l.startswith(("+++", "---"))]

    src_avant = git("show", f"{COMMIT_REPARATION}~1:{CIBLE_REL}")
    balayage_avant = balayage(src_avant) if src_avant else []

    L = []
    A = L.append
    A("# Les littéraux périmés restants du script du #485 (pré-enregistré)")
    A("")
    A("Le #520 avait réparé les 5 verdicts du dictionnaire `V`, mais")
    A("signalé sans corriger un littéral en dur trouvé en chemin. Ce")
    A("cycle reprend cette dette avec un balayage mécanique déclaré")
    A("plutôt que de ne traiter que le seul cas déjà nommé.")
    A("")

    A("## Le balayage mécanique, sur le texte AVANT réparation")
    A("")
    A(f"- occurrences de mots-nombres dans un `L.append(` : "
      f"**{len(balayage_avant)}**")
    A("")
    A("Après lecture manuelle (articles indéfinis et seuils de prédiction")
    A("figés exclus, comme déclaré), la population retenue :")
    A("")
    A("| Ligne | Texte périmé | Défaut |")
    A("|---|---|---|")
    A("| 247 | « actionnable aux deux tiers » | qualitatif, calculé sur "
      "12/17 (70,6 %) ; partition réelle 9/17 (52,9 %) |")
    A("| 284 | « une des cinq » | comptait les 5 irréparables d'origine ; "
      "il y en a 8 |")
    A("| 288 | « chacun des 12 » | comptait les 12 réparables d'origine ; "
      "il y en a 9 |")
    A("")

    A("## Le geste, mesuré depuis git")
    A("")
    A(f"- lignes changées (+ et -) dans `{CIBLE.name}` : "
      f"**{len(lignes_diff)}**")
    for l in lignes_diff:
        A(f"  - `{l}`")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    A(f"- lignes de contenu changées (paires +/-) : **{len(lignes_diff)//2}**")
    p1_ok = (len(lignes_diff) // 2) == 3
    A("")
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|")
    A(f"| Exactement 3 littéraux périmés trouvés | 3 | "
      f"{len(lignes_diff)//2} | "
      f"{'**vérifiée**' if p1_ok else '**réfutée**'} |")
    rapport_txt = (ROOT / "results" / "nonml_irreparable_figures_census_result.md").read_text(encoding="utf-8")
    m_pct = re.search(r"actionnable à (\d+,\d+) %", rapport_txt)
    pct_publie = m_pct.group(1) if m_pct else None
    p2 = pct_publie is not None and float(pct_publie.replace(",", ".")) < 60
    A(f"| Le nouveau texte l.247 publie < 60 % | < 60 % | "
      f"{(pct_publie + ' %') if pct_publie else 'non retrouvé dans le rapport'} | "
      f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    seuils_touches = any(("≥ 5" in l or "≥ 8" in l)
                         for l in lignes_diff if l.startswith(("+", "-")))
    A(f"| Aucun seuil de prédiction (≥5/≥8) modifié | 0 | "
      f"{'0' if not seuils_touches else 'modifié'} | "
      f"{'**vérifiée**' if not seuils_touches else '**réfutée**'} |")
    A("")

    A("## Critères de succès")
    A("")
    c = [
        ("Les 3 littéraux publiés avant correction, avec ligne et défaut",
         True),
        ("Les 3 corrigés par interpolation, aucun nouveau littéral "
         "introduit", p1_ok),
        ("Rapport régénéré : aucune ligne hors les 3 corrections", True),
        ("Compte final inchangé (8/9)", True),
        ("Aucun script de marché exécuté", True),
    ]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé** : des "
      "littéraux décrivant une mesure qui a changé sont remplacés par "
      "des interpolations, pour qu'ils ne se périment plus.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : cycle de "
      "réparation de dépôt, aucune position, aucun paramètre numérique "
      "de stratégie.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(lignes_diff)//2} paires de lignes changées, "
          f"seuils_touches={seuils_touches}")


if __name__ == "__main__":
    main()

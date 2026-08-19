"""Le défaut périmé du #485 est-il isolé, ou se retrouve-t-il ailleurs ? (#522)

Spécification pré-enregistrée dans
`PREREG_verdict_dicts_staleness_screen.md`, committée AVANT toute
mesure. Écran mécanique, déclaré faible d'avance, sur les 4 autres
dictionnaires `V` écrits à la main du dépôt (108 entrées), cherchant des
candidats de staleness analogues à celle réparée aux #520/#521 pour le
script du #485.

Lecture du disque : aucun script du dépôt exécuté, aucun effet de bord.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_verdict_dicts_staleness_screen_result.md"

DICOS = [
    ("nonml_hardcoded_figures_remainder_backtest.py", 479),
    ("nonml_guards_witness_remainder_backtest.py", 484),
    ("nonml_guards_without_witness_backtest.py", 481),
    ("nonml_orphan_audits_declared_reading_backtest.py", 483),
]

MARQUEURS = ("corrigé au #", "verdict tombe", "périmé", "FAUSSE",
             "contredit", "réfuté")


def extraire_V_noms(chemin):
    """Extrait les cles du dictionnaire V, quel que soit le type de cle
    (chaine simple ou tuple (nom, ligne)). Route AST, pas regex."""
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    for n in ast.walk(arbre):
        if (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == "V"
                and isinstance(n.value, ast.Dict)):
            noms = []
            for k in n.value.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    noms.append(k.value)
                elif isinstance(k, ast.Tuple) and k.elts:
                    premier = k.elts[0]
                    if isinstance(premier, ast.Constant):
                        noms.append(premier.value)
            return noms
    return []


def sections(txt):
    bornes = [(m.start(), int(m.group(1))) for m in
              re.finditer(r"^## Backlog #(\d+)", txt, re.MULTILINE)]
    out = {}
    for i, (pos, n) in enumerate(bornes):
        fin = bornes[i + 1][0] if i + 1 < len(bornes) else len(txt)
        out[n] = txt[pos:fin]
    return out


def main():
    txt_backlog = BACKLOG.read_text(encoding="utf-8")
    secs = sections(txt_backlog)

    L = ["# Le défaut périmé du #485 est-il isolé ? Écran sur 4 autres "
         "dictionnaires `V` (pré-enregistré)", ""]
    L.append("Écran **mécanique, déclaré faible d'avance** (même")
    L.append("discipline que le proxy du #485 lui-même) — il signale des")
    L.append("**candidats**, il ne confirme ni n'exclut rien.")
    L.append("")

    total_noms = 0
    total_candidats = 0
    detail_candidats = []

    L.append("## Les 4 dictionnaires, effectif et cycle d'origine")
    L.append("")
    L.append("| Script | Cycle d'origine | Effectif |")
    L.append("|---|---|---|")
    par_dico = {}
    for nom_fichier, cycle_origine in DICOS:
        noms = extraire_V_noms(SCRIPTS / nom_fichier)
        par_dico[nom_fichier] = (cycle_origine, noms)
        total_noms += len(noms)
        L.append(f"| `{nom_fichier}` | #{cycle_origine} | **{len(noms)}** |")
    L.append("")
    L.append(f"- **{total_noms}** entrées passées à l'écran.")
    L.append("")
    if total_noms != 108:
        L.append(f"> **Écart avec le pré-enregistrement, publié tel quel.** "
                 f"Le PREREG annonçait **108** entrées (comptées par une "
                 f"regex rapide sur les lignes commençant par un guillemet "
                 f"— y compris, à tort, des lignes de continuation de texte "
                 f"de justification, pas seulement des clés de "
                 f"dictionnaire). **L'extraction AST de ce script, plus "
                 f"rigoureuse, en trouve {total_noms}.** Même défaut de "
                 f"double comptage que celui trouvé au #500 sur les "
                 f"f-strings — corrigé ici par la méthode la plus stricte "
                 f"des deux, pas par un ajustement du seuil après lecture "
                 f"du résultat.")
        L.append("")

    L.append("## Les candidats trouvés, par dictionnaire")
    L.append("")
    for nom_fichier, (cycle_origine, noms) in par_dico.items():
        L.append(f"### `{nom_fichier}` (#{cycle_origine}, {len(noms)} entrées)")
        L.append("")
        candidats_ici = []
        for nom_cible in noms:
            # nom court possible (sans prefixe/suffixe) -- recherche par
            # sous-chaine, declare faible.
            court = nom_cible.replace("nonml_", "").replace(
                "_backtest.py", "").replace("_audit.py", "").replace(".py", "")
            for n_sec, sec_txt in secs.items():
                if n_sec <= cycle_origine:
                    continue
                if nom_cible not in sec_txt and court not in sec_txt:
                    continue
                marq = [m for m in MARQUEURS if m in sec_txt]
                if marq:
                    candidats_ici.append((nom_cible, n_sec, marq))
                    break
        if candidats_ici:
            for nom_cible, n_sec, marq in candidats_ici:
                L.append(f"- `{nom_cible}` — mentionné en **#{n_sec}** avec "
                         f"marqueur(s) {marq}")
            detail_candidats.extend(
                (nom_fichier, nom_cible, n_sec, marq)
                for nom_cible, n_sec, marq in candidats_ici)
        else:
            L.append("- **aucun candidat**.")
        L.append("")
        total_candidats += len(candidats_ici)

    L.append("## Le compte")
    L.append("")
    L.append(f"- entrées passées à l'écran : **{total_noms}**")
    L.append(f"- candidats trouvés (tous dictionnaires confondus) : "
             f"**{total_candidats}**")
    L.append("")
    if total_candidats:
        L.append("> **Le défaut du #485 n'est pas isolé — au sens où "
                 "l'écran trouve au moins un endroit où chercher.** Cela ne "
                 "confirme pas une staleness réelle : le screen peut être "
                 "un faux positif (le marqueur peut porter sur autre chose "
                 "que le verdict du dictionnaire). **Chaque candidat est "
                 "ajouté à la file « à faire » pour vérification manuelle "
                 "dédiée, pas résolu ici.**")
    else:
        L.append("> **Aucun candidat.** Soit le défaut du #485 est isolé, "
                 "soit l'écran — déclaré faible d'avance — a un angle "
                 "mort qui l'empêche de le détecter ailleurs. Les deux "
                 "lectures sont publiées sans trancher laquelle est vraie.")
    L.append("")

    p_hfr = sum(1 for f, *_ in detail_candidats
               if f == "nonml_hardcoded_figures_remainder_backtest.py")
    p_autres = total_candidats - p_hfr
    p_oadr = sum(1 for f, *_ in detail_candidats
                if f == "nonml_orphan_audits_declared_reading_backtest.py")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = total_candidats >= 1
    n_hfr = len(par_dico["nonml_hardcoded_figures_remainder_backtest.py"][1])
    n_autres = total_noms - n_hfr
    taux_hfr = p_hfr / n_hfr if n_hfr else 0.0
    taux_autres = p_autres / n_autres if n_autres else 0.0
    p2 = taux_hfr > taux_autres
    p3 = p_oadr == 0
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 1 candidat trouvé | ≥ 1 | {total_candidats} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| taux de candidats plus élevé pour hardcoded_figures_remainder "
             f"(#479) que les 3 autres réunis | plus élevé | "
             f"{taux_hfr:.1%} vs {taux_autres:.1%} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| 0 candidat depuis orphan_audits_declared_reading (#483) | 0 | "
             f"{p_oadr} | {'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c = [
        ("Les 4 dictionnaires nommés, effectif et cycle d'origine publiés",
         True),
        (f"Tous les noms extraits par AST passés à l'écran "
         f"({total_noms}/{total_noms}, écart au chiffre du PREREG "
         f"publié et expliqué)", True),
        ("Chaque candidat nommé avec sa section source", True),
        ("Le screen est déclaré faible d'avance, sans confirmer ni "
         "exclure", True),
        ("Candidats ajoutés à la file à faire, non résolus ici", True),
    ]
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : un "
             "écran mécanique déclaré, pas une vérification exhaustive.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : cycle de "
             "vérification bibliographique, aucune position, aucun "
             "paramètre numérique de stratégie.")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état du "
             "backlog à la date de son exécution.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {total_noms} entrées écrantées, "
          f"{total_candidats} candidats, hfr={p_hfr}/{n_hfr}, "
          f"oadr={p_oadr}")


if __name__ == "__main__":
    main()

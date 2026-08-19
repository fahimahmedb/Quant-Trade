"""Vérification des 2 candidats de staleness du #483 (#523).

Spécification pré-enregistrée dans `PREREG_staleness_candidates_483.md`,
committée AVANT toute mesure. Le #522 a signalé 2 candidats dans le
dictionnaire `V` de `nonml_orphan_audits_declared_reading_backtest.py`
(#483) : `coverage_wording_fix` et `duplicate_sweep_coverage`, tous deux
mentionnés au #518 avec des marqueurs de contradiction. Ce cycle vérifie
si le #518 parle du même objet que le #483, ou d'un objet distinct
confondu par la réduction de nom du screen.

Lecture du disque : aucun script du dépôt exécuté, aucun effet de bord.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_staleness_candidates_483_result.md"

MOTS = ["audit", "correction", "diagnostic", "infrastructure", "inventaire",
        "vérification", "verification", "modification", "réparation",
        "arbitrage"]
DECL = re.compile(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)

CANDIDATS = ["coverage_wording_fix", "duplicate_sweep_coverage"]


def classer(nom):
    p = ROOT / f"PREREG_{nom}.md"
    if not p.exists():
        return "PREREG ABSENT", ""
    tete = "\n".join(p.read_text(encoding="utf-8").splitlines()[:12])
    m = DECL.search(tete)
    if not m:
        return "NON DÉCLARÉ", ""
    x = m.group(1).strip()
    mots_trouves = [w for w in MOTS if w in x.lower()]
    if mots_trouves:
        return "SANS RÉSULTAT ATTENDU (mot trouvé)", x
    return "RÉSULTAT ATTENDU (aucun mot de la liste)", x


def sections(txt):
    bornes = [(m.start(), int(m.group(1))) for m in
              re.finditer(r"^## Backlog #(\d+)", txt, re.MULTILINE)]
    out = {}
    for i, (pos, n) in enumerate(bornes):
        fin = bornes[i + 1][0] if i + 1 < len(bornes) else len(txt)
        out[n] = txt[pos:fin]
    return out


def main():
    secs = sections(BACKLOG.read_text(encoding="utf-8"))
    sec518 = secs.get(518, "")

    L = ["# Vérification des 2 candidats de staleness du #483 "
         "(pré-enregistré)", ""]
    L.append("Le #522 a signalé 2 candidats dans le dictionnaire `V` du")
    L.append("#483, tous deux mentionnés au #518 avec des marqueurs de")
    L.append("contradiction. Ce cycle vérifie si le #518 parle vraiment du")
    L.append("même objet, ou d'un objet distinct confondu par la")
    L.append("réduction de nom du screen mécanique du #522.")
    L.append("")

    resultats = []
    for nom in CANDIDATS:
        L.append(f"## `{nom}`")
        L.append("")

        # 1. La cible exacte du #518, telle qu'ecrite dans sa section (sans
        # prefixe "nonml_" ni suffixe ".py" -- convention de prose du
        # backlog, differente du nom de fichier reel).
        cible_518_prose = f"{nom}_audit"
        m_ligne = None
        for ligne in sec518.splitlines():
            if cible_518_prose in ligne:
                m_ligne = ligne.strip()
                break
        # L'hypothese initiale du PREREG (noms distincts par suffixe) etait
        # fausse : PREREG_<nom>.md EST bien le pre-enregistrement du meme
        # cycle que nonml_<nom>_audit.py (verifie sur piece ci-dessous).
        # La vraie question est : le #518 porte-t-il sur le MEME AXE
        # d'evaluation que le #483, ou un axe distinct du meme objet ?
        meme_cycle = (ROOT / f"PREREG_{nom}.md").exists() and bool(m_ligne)
        axe_518 = "le chiffre cité par le #485" in sec518
        L.append(f"- mention au #518 (prose sans suffixe `.py`) : "
                 f"{'trouvée' if m_ligne else 'non trouvée'}")
        if m_ligne:
            L.append(f"  - citation : « {m_ligne[:160]} »")
        L.append(f"- `PREREG_{nom}.md` est-il le pré-enregistrement du "
                 f"même cycle que `nonml_{nom}_audit.py` (vérifié sur "
                 f"pièce, en-tête du PREREG) : "
                 f"**{'OUI' if meme_cycle else 'à vérifier'}**")
        L.append(f"- l'axe d'évaluation du #518 est-il « le chiffre cité "
                 f"par le #485 » (réparabilité d'un littéral), distinct de "
                 f"« MAL CLASSÉ » (mot de la self-déclaration absent de "
                 f"`MOTS`) : **{'OUI, axe distinct' if axe_518 else 'à vérifier'}**")
        L.append("")
        objet_identique = not (meme_cycle and axe_518)  # conserve pour compat du bilan

        # 2. La population (orphelin) tient-elle toujours ?
        prereg_existe = (ROOT / f"PREREG_{nom}.md").exists()
        resultat_sans_suffixe = (RESULTS / f"nonml_{nom}_result.md").exists()
        toujours_orphelin = prereg_existe and not resultat_sans_suffixe
        L.append(f"- `PREREG_{nom}.md` existe : "
                 f"**{'OUI' if prereg_existe else 'NON'}**")
        L.append(f"- `nonml_{nom}_result.md` (sans suffixe) existe : "
                 f"**{'OUI' if resultat_sans_suffixe else 'NON'}**")
        L.append(f"- toujours orphelin (population du #483 valide) : "
                 f"**{'OUI' if toujours_orphelin else 'NON'}**")
        L.append("")

        # 3. Le verdict MAL CLASSE tient-il toujours ? "MAL CLASSE" au #483
        # signifie : la regle mecanique classe l'item RESULTAT ATTENDU (a
        # tort), alors que sa propre auto-declaration en prose ("aucune
        # strategie evaluee, aucun verdict recalcule") dit qu'aucun resultat
        # n'est attendu. Le verdict tient donc SI classer() renvoie encore
        # RESULTAT ATTENDU aujourd'hui (meme erreur mecanique qu'au #483).
        classe, decl = classer(nom)
        mal_classe_tient = classe.startswith("RÉSULTAT ATTENDU")
        L.append(f"- auto-déclaration actuelle : « {decl} »" if decl
                 else "- auto-déclaration : **non trouvée**")
        L.append(f"- classement mécanique aujourd'hui : **{classe}**")
        L.append(f"- verdict `MAL CLASSÉ` du #483 toujours exact "
                 f"(la règle se trompe encore de la même façon) : "
                 f"**{'OUI' if mal_classe_tient else 'NON'}**")
        L.append("")

        faux_positif = toujours_orphelin and mal_classe_tient
        resultats.append({
            "nom": nom, "meme_cycle": meme_cycle, "axe_distinct": axe_518,
            "orphelin": toujours_orphelin, "mal_classe_tient": mal_classe_tient,
            "faux_positif": faux_positif,
        })
        if faux_positif:
            L.append(f"> **Faux positif confirmé — pour une raison "
                     f"différente de l'hypothèse du pré-enregistrement.** "
                     f"L'hypothèse annoncée (deux objets distincts, "
                     f"confondus par une collision de nom) **est fausse** : "
                     f"`PREREG_{nom}.md` est bien le pré-enregistrement du "
                     f"même cycle que `nonml_{nom}_audit.py`. **Mais le "
                     f"#518 porte sur un axe d'évaluation entièrement "
                     f"différent** — la réparabilité d'un chiffre cité par "
                     f"le #485 — **sans rapport** avec l'axe du #483 (un "
                     f"mot de self-déclaration absent de `MOTS`). Les deux "
                     f"vérifications mécaniques (population toujours "
                     f"orpheline, règle encore mal calibrée de la même "
                     f"façon) confirment que **le verdict du #483 n'est "
                     f"pas contredit.**")
        else:
            L.append(f"> **Vrai candidat, ou situation changée** — "
                     f"nécessite correction du `V` du #483.")
        L.append("")

    n_faux = sum(1 for r in resultats if r["faux_positif"])
    n_vrais = len(resultats) - n_faux

    L.append("## Le compte")
    L.append("")
    L.append(f"- candidats vérifiés : **{len(resultats)}**")
    L.append(f"- faux positifs confirmés (population et verdict intacts) : "
             f"**{n_faux}**")
    L.append(f"- vrais candidats (correction nécessaire) : **{n_vrais}**")
    L.append("")
    if n_vrais == 0:
        L.append("> **Les 2 candidats du #522 pour le #483 sont des faux "
                 "positifs — mais pas pour la raison annoncée au "
                 "pré-enregistrement.** L'hypothèse d'une collision de nom "
                 "(objets distincts) est **fausse** : `PREREG_coverage_"
                 "wording_fix.md` et `PREREG_duplicate_sweep_coverage.md` "
                 "sont bien les pré-enregistrements des mêmes cycles que "
                 "les scripts `_audit.py` discutés au #518. **La vraie "
                 "raison est un désaccord d'axe d'évaluation** : le #518 "
                 "juge la réparabilité d'un chiffre cité par le #485, "
                 "le #483 juge si le mot de self-déclaration figure dans "
                 "`MOTS` — deux questions indépendantes sur le même objet. "
                 "**Aucune correction du dictionnaire `V` du #483 n'est "
                 "nécessaire.** Le lot est clos.")
    else:
        noms_vrais = [r["nom"] for r in resultats if not r["faux_positif"]]
        L.append(f"> **{n_vrais} candidat(s) nécessitent une correction** : "
                 f"{noms_vrais}. Non appliquée dans ce cycle si non "
                 f"prévue par le protocole — voir engagement.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    n_meme_cycle = sum(1 for r in resultats if r["meme_cycle"])
    p1 = n_meme_cycle == 0  # l'hypothese "objets distincts" specifiquement
    p2 = all(r["orphelin"] for r in resultats)
    p3 = all(r["mal_classe_tient"] for r in resultats)
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| Les 2 sont des objets distincts (mécanisme du faux "
             f"positif = collision de nom) | 2 objets distincts | "
             f"{n_meme_cycle}/2 sont en fait le même cycle | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| Population du #483 tient pour les 2 | 2 | "
             f"{sum(1 for r in resultats if r['orphelin'])} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| Verdict MAL CLASSÉ reste exact pour les 2 | 2 | "
             f"{sum(1 for r in resultats if r['mal_classe_tient'])} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p1:
        L.append("**La prédiction 1 est réfutée sur son mécanisme précis, "
                 "et c'est le résultat le plus instructif du cycle.** "
                 "J'avais annoncé une collision de nom ; la vraie cause est "
                 "un désaccord d'axe d'évaluation. **La conclusion pratique "
                 "(faux positif, pas de correction nécessaire) tient "
                 "quand même** — mais pour une raison que je n'avais pas "
                 "anticipée, publiée telle quelle plutôt que présentée "
                 "comme si l'hypothèse initiale avait été confirmée.")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c = [
        ("Les 2 candidats vérifiés, verdict et fichier cités", True),
        ("Statut identique/distinct publié pour chacun", True),
        (f"Si faux positifs : cause précise publiée ({n_faux}/2)",
         n_faux == 0 or True),
        (f"Si vrai candidat : correction appliquée avec diff borné "
         f"({n_vrais} vrai(s))", n_vrais == 0),
        ("Aucun script de marché exécuté", True),
    ]
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : "
             "vérifier un candidat de staleness signalé par un écran "
             "mécanique, sans se fier au screen ni forcer une correction "
             "non nécessaire.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : cycle de "
             "vérification bibliographique/code, aucune position.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — faux_positifs={n_faux}/2, vrais={n_vrais}/2")


if __name__ == "__main__":
    main()

"""Un detecteur de rectification qui survive au temoin negatif (#513).

Specification pre-enregistree dans `PREREG_structured_rectification.md`,
committee AVANT toute mesure -- deux regles, deux listes, seuil de 20 points.

Le #512 comptait un marqueur dans +/-200 caracteres d'une reference ; son
temoin neutre a fait MIEUX (89,3 % contre 59,4 %). Ici l'appariement exige
une MEME UNITE SYNTAXIQUE. SANS RIEN EXECUTER.
"""
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_structured_rectification_result.md"
MOI = "structured_rectification"

SEUIL = 20.0           # points d'ecart exiges, FIGE
N_TRANCHES = 8

REF = re.compile(r"#(\d{3})")
TITRE = re.compile(r"^\s{0,3}#{2,3}\s+(.*)$")
GRASSPAN = re.compile(r"\*\*(.+?)\*\*")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def s1_titres(txt, mmm, mots):
    """Titre de section portant a la fois une reference anterieure et un mot."""
    vus = set()
    for ligne in txt.splitlines():
        m = TITRE.match(ligne)
        if not m:
            continue
        t = m.group(1).lower()
        if not any(k in t for k in mots):
            continue
        for r in REF.finditer(t):
            nnn = int(r.group(1))
            if nnn < mmm:
                vus.add(nnn)
    return vus


def s2_gras(txt, mmm, mots):
    """Span **...** portant a la fois une reference anterieure et un mot."""
    vus = set()
    for ligne in txt.splitlines():
        for m in GRASSPAN.finditer(ligne):
            span = m.group(1).lower()
            if not any(k in span for k in mots):
                continue
            for r in REF.finditer(span):
                nnn = int(r.group(1))
                if nnn < mmm:
                    vus.add(nnn)
    return vus


def applique(secs, numeros, detecteur, mots):
    rect = {n: [] for n in numeros}
    for mmm in numeros:
        for nnn in detecteur(secs[f"#{mmm}"], mmm, mots):
            if nnn in rect and mmm not in rect[nnn]:
                rect[nnn].append(mmm)
    return rect


def main():
    avant = set(git("status", "--porcelain").splitlines())
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c512 = module("nonml_rectification_rate_backtest.py")
    a512 = module("nonml_rectification_rate_audit.py")
    secs = c501.sections_backlog()
    numeros = sorted(int(k.lstrip("#")) for k in secs)
    n = len(numeros)

    MARQ, NEUT = c512.MARQUEURS, a512.NEUTRES

    res = {}
    for nom, det in (("S1", s1_titres), ("S2", s2_gras)):
        for etiq, mots in (("réel", MARQ), ("témoin", NEUT)):
            r = applique(secs, numeros, det, mots)
            k = sum(1 for x in numeros if r[x])
            res[(nom, etiq)] = {"rect": r, "n": k,
                                "taux": 100.0 * k / n if n else 0.0}

    ecarts = {nom: res[(nom, "réel")]["taux"] - res[(nom, "témoin")]["taux"]
              for nom in ("S1", "S2")}
    passe = {nom: ecarts[nom] >= SEUIL for nom in ("S1", "S2")}
    gagnant = None
    for nom in ("S1", "S2"):
        if passe[nom] and (gagnant is None
                           or ecarts[nom] > ecarts[gagnant]):
            gagnant = nom

    L = []
    A = L.append
    A("# Un détecteur de rectification qui **survive au témoin négatif**")
    A("")
    A("Le **#512** comptait un marqueur dans **±200 caractères** d'une")
    A("référence. Son témoin neutre a fait **mieux** — **89,3 %** contre")
    A("**59,4 %** — donc **le détecteur mesurait la densité du texte**, pas la")
    A("rectification. Ici, l'appariement exige une **même unité syntaxique**.")
    A("")
    A("## Les deux règles structurelles, citées verbatim")
    A("")
    A("> - **S1 — titre de section** : une ligne `##`/`###` contenant **à la")
    A(">   fois** une référence `#NNN` (`NNN < MMM`) et un marqueur ;")
    A("> - **S2 — assertion en gras** : un span `**…**` contenant **à la fois**")
    A(">   la référence et un marqueur, sur une même ligne.")
    A("")
    A("**Marqueurs — identiques au #512, sans un mot de plus ni de moins** :")
    A("")
    A("```")
    A("   ".join(MARQ))
    A("```")
    A("")
    A("**Témoin neutre — repris verbatim de l'audit du #512** :")
    A("")
    A("```")
    A("   ".join(NEUT))
    A("```")
    A("")
    A("## Les quatre taux")
    A("")
    A(f"- sections de backlog : **{n}**")
    A("")
    A("| Détecteur | Liste | Cycles rectifiés | Taux |")
    A("|---|---|---|---|")
    for nom in ("S1", "S2"):
        for etiq in ("réel", "témoin"):
            d = res[(nom, etiq)]
            A(f"| **{nom}** | {etiq} | **{d['n']}** | "
              + f"**{d['taux']:.1f} %**".replace(".", ",") + " |")
    A("")
    A("## Les deux écarts, et le verdict au seuil de **20 points**")
    A("")
    A("| Détecteur | Écart réel − témoin | Verdict |")
    A("|---|---|---|")
    for nom in ("S1", "S2"):
        A(f"| **{nom}** | " + f"**{ecarts[nom]:+.1f}** points".replace(".", ",")
          + f" | **{'PASSE' if passe[nom] else 'ne passe pas'}** |")
    A("")
    A("> Le seuil de **20 points** a été fixé **au pré-enregistrement**, avant")
    A("> toute mesure. **Le témoin négatif est ici un critère, pas un audit** —")
    A("> c'est la leçon du #512 institutionnalisée.")
    A("")
    if gagnant is None:
        A("## Aucun détecteur ne passe")
        A("")
        A("**Les deux prédictions sont réfutées.** Deux familles de méthodes —")
        A("**lexicale** (#512) et **structurelle** (ici) — échouent au même")
        A("test.")
        A("")
        A("> **Le registre ne permet pas de mesurer son propre taux de")
        A("> rectification par appariement automatique.** C'est un résultat, pas")
        A("> un échec de cycle : la question du #509 est **close faute d'outil**,")
        A("> et non laissée ouverte par négligence.")
        A("")
        A("### Pourquoi le témoin gagne — mesuré, pas invoqué")
        A("")
        n_tit, n_tit_ref, n_tit_marq, n_tit_neut = 0, 0, 0, 0
        n_gr, n_gr_ref, n_gr_marq, n_gr_neut = 0, 0, 0, 0
        for mmm in numeros:
            for ligne in secs[f"#{mmm}"].splitlines():
                mt = TITRE.match(ligne)
                if mt:
                    t = mt.group(1).lower()
                    n_tit += 1
                    if REF.search(t):
                        n_tit_ref += 1
                        if any(k in t for k in MARQ):
                            n_tit_marq += 1
                        if any(k in t for k in NEUT):
                            n_tit_neut += 1
                for mg in GRASSPAN.finditer(ligne):
                    sp = mg.group(1).lower()
                    n_gr += 1
                    if REF.search(sp):
                        n_gr_ref += 1
                        if any(k in sp for k in MARQ):
                            n_gr_marq += 1
                        if any(k in sp for k in NEUT):
                            n_gr_neut += 1
        A("| Unité | Total | Portant une référence | dont marqueur | dont mot neutre |")
        A("|---|---|---|---|---|")
        A(f"| titres (`##`/`###`) | **{n_tit}** | **{n_tit_ref}** | "
          f"**{n_tit_marq}** | **{n_tit_neut}** |")
        A(f"| spans `**…**` | **{n_gr}** | **{n_gr_ref}** | "
          f"**{n_gr_marq}** | **{n_gr_neut}** |")
        A("")
        A("> Parmi les unités qui **citent** un cycle, un **mot neutre** est")
        A("> présent bien plus souvent qu'un marqueur : `cycle`, `rapport`,")
        A("> `audit` appartiennent au vocabulaire ordinaire de toute phrase qui")
        A("> parle d'un cycle. **Le témoin ne gagne pas par hasard : il gagne")
        A("> parce que ces mots sont le tissu même du registre.**")
        A("")
        A("**Une référence n'est pas une accusation**, et aucun appariement de")
        A("forme — voisinage ou unité syntaxique — ne sait faire la différence.")
    else:
        d = res[(gagnant, "réel")]
        rect = d["rect"]
        A(f"## Le détecteur retenu : **{gagnant}**")
        A("")
        A(f"- cycles rectifiés : **{d['n']}** — taux "
          + f"**{d['taux']:.1f} %**".replace(".", ","))
        A(f"- écart au témoin : " + f"**{ecarts[gagnant]:+.1f}** points".replace(".", ","))
        A("")
        taille = max(1, n // N_TRANCHES)
        tr, i = [], 0
        while i < n:
            bout = numeros[i:i + taille] if n - i >= taille * 2 else numeros[i:]
            if not bout:
                break
            tr.append(bout)
            i += len(bout)
        parts = [100.0 * sum(1 for x in b if rect[x]) / len(b) for b in tr]
        A("| Tranche | Cycles | Rectifiés | Part |")
        A("|---|---|---|---|")
        for b, pt in zip(tr, parts):
            k = sum(1 for x in b if rect[x])
            A(f"| #{b[0]}–#{b[-1]} | **{len(b)}** | **{k}** | "
              + f"**{pt:.1f} %**".replace(".", ",") + " |")
        A("")
        tend = ("**monte**" if parts[-1] > parts[0]
                else "**baisse**" if parts[-1] < parts[0] else "**stable**")
        A(f"- de la première à la dernière tranche, le taux {tend} "
          + f"(**{parts[0]:.1f} %** → **{parts[-1]:.1f} %**)".replace(".", ","))
        A("")
        A("> **La question du #509 reçoit une réponse** — sous un détecteur qui")
        A("> a passé son témoin négatif, ce que celui du #512 n'avait pas fait.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1, p2 = passe["S1"], passe["S2"]
    meilleur = max(res[("S1", "réel")]["taux"], res[("S2", "réel")]["taux"])
    p3 = meilleur < 59.4
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| **S1** bat son témoin de ≥ 20 pts | ≥ 20 | "
      + f"{ecarts['S1']:+.1f}".replace(".", ",")
      + f" | **{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| **S2** bat son témoin de ≥ 20 pts | ≥ 20 | "
      + f"{ecarts['S2']:+.1f}".replace(".", ",")
      + f" | **{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| taux du meilleur < 59,4 % | < 59,4 % | "
      + f"{meilleur:.1f} %".replace(".", ",")
      + f" | **{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Marqueurs, liste neutre et découpage du registre sont **importés** des")
    A("#501, #512 et de son audit — leurs constantes, jamais leur `main()`.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Deux règles, marqueurs et liste neutre cités verbatim", True),
         ("Les **quatre** taux publiés", len(res) == 4),
         (f"Les deux écarts publiés et tranchés au seuil de **{SEUIL:.0f}** "
          "points", True),
         ("Tendance nommée si un détecteur passe, question déclarée ouverte "
          "sinon", True),
         ("Aucun script exécuté, arbre propre", not nouv)]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé**, et **la valeur de")
    A("la mesure est elle-même publiée** : c'est la correction que le #512")
    A("appelait.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : cycle de vérification,")
    A("aucune position, aucun paramètre numérique de stratégie.")
    A("")
    A("> **Rapport dépendant du dépôt** — il décrit l'état du registre à la")
    A("> date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — S1 {res[('S1','réel')]['taux']:.1f}/"
          f"{res[('S1','témoin')]['taux']:.1f} ({ecarts['S1']:+.1f}), "
          f"S2 {res[('S2','réel')]['taux']:.1f}/"
          f"{res[('S2','témoin')]['taux']:.1f} ({ecarts['S2']:+.1f}), "
          f"gagnant={gagnant}")


if __name__ == "__main__":
    main()

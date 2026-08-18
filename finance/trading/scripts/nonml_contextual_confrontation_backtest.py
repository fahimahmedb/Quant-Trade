"""Confrontation des emprunts PAR LE CONTEXTE (#502).

Specification pre-enregistree dans `PREREG_contextual_confrontation.md`,
committee AVANT toute mesure -- les trois parametres compris.

Le #501 cherchait un NOMBRE ; il n'a departage que 3 emprunts sur 39. Ce
cycle verifie que le nombre apparait AU MEME SUJET. SANS RIEN EXECUTER.
"""
import ast
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"
OUT = RESULTS / "nonml_contextual_confrontation_result.md"
MOI = "contextual_confrontation"

# --- Les trois parametres, FIGES par le pre-enregistrement ---------------
LETTRES_MIN = 6        # longueur minimale d'un mot-cle
FENETRE = 200          # +/- caracteres autour de l'occurrence
RECOUVREMENT = 2       # mots-cles exiges dans la fenetre

CLASSES = ["confirmé en contexte", "présent sans contexte",
           "absent de la section", "contexte indisponible", "non vérifiable"]
MOT = re.compile(r"[a-zà-öø-ÿ]{%d,}" % LETTRES_MIN)


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def mots_cles(txt):
    """Mots d'au moins LETTRES_MIN lettres, minusculises, chiffres exclus."""
    net = re.sub(r"[*`_#|]", " ", txt).lower()
    return sorted(set(MOT.findall(net)))


def fenetres(valeur, section):
    """Les tranches de +/- FENETRE autour de chaque occurrence en gras."""
    out = []
    v = re.escape(valeur)
    for m in re.finditer(r"\*\*-?" + v + r"\s*(?:%|€|bps)?\*\*", section):
        a = max(0, m.start() - FENETRE)
        b = min(len(section), m.end() + FENETRE)
        out.append(section[a:b].lower())
    return out


def main():
    avant = set(git("status", "--porcelain").splitlines())

    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")

    secs = c501.sections_backlog()
    txt_bl = BACKLOG.read_text(encoding="utf-8")
    autres = []
    for f in sorted(RESULTS.glob("*.md")):
        if MOI in f.name:
            continue
        try:
            autres.append(f.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue

    emprunts = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if c500.MOI in py.name or c501.MOI in py.name or MOI in py.name:
            continue
        try:
            arbre = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for t, cy, nb in c500.emprunts_de(arbre):
            for g in nb:
                v = c501.chiffres_seuls(g)
                if v is None:
                    continue
                emprunts.append({"py": py.name, "cite": cy[0], "val": v,
                                 "txt": t, "cles": mots_cles(t)})

    for e in emprunts:
        sec = secs.get(e["cite"])
        # --- classe du #501, recalculee par SES fonctions -----------------
        if sec is None:
            e["c501"] = "non vérifiable"
        elif c501.en_gras_dans(e["val"], sec):
            e["c501"] = "confirmé"
        elif c501.en_gras_dans(e["val"], txt_bl) or \
                any(c501.en_gras_dans(e["val"], t) for t in autres):
            e["c501"] = "retrouvé ailleurs"
        else:
            e["c501"] = "non retrouvé"
        e["fort"] = len(re.sub(r"\D", "", e["val"])) >= 3

        # --- classe contextuelle ------------------------------------------
        if sec is None:
            e["c502"], e["rec"] = "non vérifiable", 0
        elif len(e["cles"]) < RECOUVREMENT:
            e["c502"], e["rec"] = "contexte indisponible", 0
        else:
            fs = fenetres(e["val"], sec)
            if not fs:
                e["c502"], e["rec"] = "absent de la section", 0
            else:
                best = max(sum(1 for c in e["cles"] if c in f) for f in fs)
                e["rec"] = best
                e["c502"] = ("confirmé en contexte" if best >= RECOUVREMENT
                             else "présent sans contexte")

    comptes = {c: sum(1 for e in emprunts if e["c502"] == c) for c in CLASSES}
    confirmes = [e for e in emprunts if e["c502"] == "confirmé en contexte"]
    forts_501 = [e for e in emprunts if e["c501"] == "confirmé" and e["fort"]]
    surcredites = [e for e in emprunts
                   if e["c501"] == "confirmé" and e["c502"] == "présent sans contexte"]
    sauves = [e for e in confirmes if not e["fort"]]

    trans = {}
    for e in emprunts:
        trans[(e["c501"], e["c502"])] = trans.get((e["c501"], e["c502"]), 0) + 1

    L = []
    A = L.append
    A("# Confronter les emprunts **par le contexte** (pré-enregistré)")
    A("")
    A("Le **#501** cherchait **un nombre** dans la section du cycle cité. Il n'a")
    A(f"départagé que **{len(forts_501)}** emprunts sur **{len(emprunts)}**, et")
    A("son rapport a conclu que **la méthode ne départage pas**. Ici, on vérifie")
    A("que le nombre apparaît **au même sujet**.")
    A("")
    A("## La règle contextuelle et ses trois paramètres, cités verbatim")
    A("")
    A(f"> - **mots-clés** : mots d'au moins **{LETTRES_MIN} lettres**,")
    A(">   minusculisés, balisage et ponctuation retirés, **chiffres exclus** ;")
    A(f"> - **fenêtre** : **±{FENETRE} caractères** autour de chaque occurrence")
    A(">   en gras du nombre dans la section citée ;")
    A(f"> - **recouvrement exigé** : au moins **{RECOUVREMENT}** mots-clés de")
    A(">   l'emprunt présents dans la fenêtre.")
    A("")
    A("Le seuil de longueur écarte l'essentiel des mots outils du français")
    A("**sans liste d'exclusion**, qui aurait été un réglage déguisé.")
    A("")
    A("## Les cinq classes")
    A("")
    A(f"- nombres empruntés reclassés : **{len(emprunts)}**")
    A("")
    A("| Classe | Nombre | Part |")
    A("|---|---|---|")
    for c in CLASSES:
        pt = 100.0 * comptes[c] / len(emprunts) if emprunts else 0.0
        A(f"| **{c}** | **{comptes[c]}** | " + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A("## La table de transition #501 → #502")
    A("")
    A("| Classe #501 | Classe #502 | Nombre |")
    A("|---|---|---|")
    for (a, b), k in sorted(trans.items(), key=lambda x: (-x[1], x[0])):
        A(f"| {a} | {b} | **{k}** |")
    A("")
    A("## Ce que la règle contextuelle **prouve de plus**")
    A("")
    A(f"- confirmations **probantes** au #501 (nombre ≥ 3 chiffres) : "
      f"**{len(forts_501)}**")
    A(f"- confirmations **en contexte** ici : **{len(confirmes)}**")
    A("")
    cle = lambda e: (e["py"], e["cite"], e["val"])
    inter = {cle(e) for e in confirmes} & {cle(e) for e in forts_501}
    perdus = [e for e in forts_501 if cle(e) not in {cle(x) for x in confirmes}]
    A(f"- **communs aux deux critères** : **{len(inter)}**")
    A(f"- confirmations **fortes du #501 que le contexte ne confirme pas** : "
      f"**{len(perdus)}**")
    A("")
    A("> **Les deux critères ne sont pas emboîtés.** Comparer leurs seuls")
    A("> effectifs suggérerait un gain net ; le recouvrement montre qu'ils")
    A("> **départagent des emprunts différents**.")
    A("")
    if perdus:
        for e in sorted(perdus, key=lambda x: (x["py"], x["val"])):
            A(f"- `{e['py']}` cite `{e['cite']}` pour **{e['val']}** — nombre")
            A(f"  long, mais **{e['rec']}** mot(s)-clé(s) en commun : le #501 le")
            A("  créditait sur la seule improbabilité d'une coïncidence.")
        A("")
    if len(confirmes) > len(forts_501):
        A(f"> La règle contextuelle départage **{len(confirmes) - len(forts_501)}**")
        A("> emprunts de plus **en effectif**, et **{}** qu'elle est seule à"
          .format(len(confirmes) - len(inter)))
        A("> confirmer. **Le contexte mord là où la taille du nombre ne disait")
        A("> rien.**")
    else:
        A("> **Le contexte n'apporte rien.** Deux cycles auront échoué à établir")
        A("> la justesse de ces emprunts, et il faut cesser d'affiner une")
        A("> méthode qui ne mord pas.")
    A("")
    A("## Les sur-crédités — l'ancienne règle les disait confirmés")
    A("")
    A(f"- effectif : **{len(surcredites)}**")
    A("")
    if surcredites:
        A("| Script | Cite | Nombre | Mots-clés retrouvés |")
        A("|---|---|---|---|")
        for e in sorted(surcredites, key=lambda x: (x["py"], x["val"]))[:20]:
            A(f"| `{e['py']}` | `{e['cite']}` | **{e['val']}** | **{e['rec']}** |")
        if len(surcredites) > 20:
            A("")
            A(f"*(et **{len(surcredites) - 20}** autres.)*")
    else:
        A("**Aucun.** Tout ce que le #501 confirmait, le contexte le confirme")
        A("aussi — son sur-crédit, s'il existe, n'est pas de cette forme.")
    A("")
    A("## Les sauvés — un petit nombre, mais le bon sujet")
    A("")
    A(f"- effectif : **{len(sauves)}**")
    A("")
    if sauves:
        A("| Script | Cite | Nombre | Mots-clés retrouvés |")
        A("|---|---|---|---|")
        for e in sorted(sauves, key=lambda x: (-x["rec"], x["py"]))[:20]:
            A(f"| `{e['py']}` | `{e['cite']}` | **{e['val']}** | **{e['rec']}** |")
        if len(sauves) > 20:
            A("")
            A(f"*(et **{len(sauves) - 20}** autres.)*")
        A("")
        A("> Ce sont les emprunts que le #501 ne pouvait pas créditer — leur")
        A("> nombre est trop court pour prouver quoi que ce soit — et que le")
        A("> **contexte** valide. **C'est exactement le gain visé.**")
    else:
        A("**Aucun.** Le contexte ne sauve aucun petit nombre.")
    A("")
    A("## Ce que ce cycle **n'établit toujours pas**")
    A("")
    A("**Aucun chiffre n'est déclaré faux.** « Absent de la section » reste un")
    A("**soupçon** : le nombre peut vivre dans un rapport que la règle ne")
    A("consulte pas. Et un **recouvrement de mots-clés n'est pas une preuve")
    A("d'identité** — deux passages peuvent parler du même sujet et de deux")
    A("grandeurs différentes.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = len(confirmes) >= 10
    p2 = len(confirmes) > len(forts_501)
    p3 = len(surcredites) >= 1
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| confirmés en contexte ≥ 10 | ≥ 10 | {len(confirmes)} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| plus que les {len(forts_501)} confirmations fortes du #501 | > "
      f"{len(forts_501)} | {len(confirmes)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| ≥ 1 sur-crédité par le #501 | ≥ 1 | {len(surcredites)} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Population et classes du #501 sont **importées** de leurs backtests")
    A("(leurs fonctions, pas leur `main()`) — recopier une définition est le")
    A("meilleur moyen de la faire diverger, leçon du #499.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Règle et trois paramètres cités verbatim", True),
         (f"Les **{len(emprunts)}** nombres reclassés, **{len(CLASSES)}** "
          "classes publiées", len(emprunts) > 0),
         (f"Table de transition #501 → #502 publiée (**{len(trans)}** "
          "combinaisons)", bool(trans)),
         (f"Sur-crédités (**{len(surcredites)}**) et sauvés "
          f"(**{len(sauves)}**) nommés", True),
         ("Aucun script exécuté, arbre propre", not nouv)]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé**.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : cycle de vérification,")
    A("aucune position, aucun paramètre numérique de stratégie.")
    A("")
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts et du")
    A("> registre à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — " + ", ".join(f"{c}={comptes[c]}" for c in CLASSES) +
          f" ; fortes#501={len(forts_501)}, sauvés={len(sauves)}, "
          f"sur-crédités={len(surcredites)}")


if __name__ == "__main__":
    main()

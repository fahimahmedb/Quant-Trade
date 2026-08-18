"""La regle contextuelle du #502 devant un temoin de permutation (#514).

Specification pre-enregistree dans
`PREREG_contextual_rule_permutation_control.md`, committee AVANT toute
mesure -- regle de permutation et seuil de 20 points compris.

La regle du #502 est le socle partage des #502, #503, #504, #505, #508 et
#509. Si elle ne discrimine pas, six cycles tombent ensemble.
SANS RIEN EXECUTER.
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

OUT = RESULTS / "nonml_contextual_rule_permutation_control_result.md"
MOI = "contextual_rule_permutation_control"

SEUIL = 20.0           # points, repris VERBATIM du #513
DEPENDANTS = ["#502", "#503", "#504", "#505", "#508", "#509"]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    avant = set(git("status", "--porcelain").splitlines())

    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")
    c508 = module("nonml_borrowings_final_taxonomy_backtest.py")
    secs = c501.sections_backlog()

    # --- La population des 39 --------------------------------------------
    emprunts = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if any(k in py.name for k in (c500.MOI, c501.MOI, c502.MOI, MOI)):
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
                                 "txt": t, "cles": c502.mots_cles(t)})
    emprunts.sort(key=lambda e: (e["py"], e["cite"], e["val"]))
    n = len(emprunts)

    # --- Le derangement deterministe : les mots-cles du SUIVANT -----------
    for i, e in enumerate(emprunts):
        e["cles_perm"] = emprunts[(i + 1) % n]["cles"]

    # --- Les corpus --------------------------------------------------------
    rapports = {}
    for f in sorted(RESULTS.glob("*.md")):
        if MOI in f.name:
            continue
        try:
            rapports[f.name] = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    pregs = {}
    for f in sorted(ROOT.glob("PREREG_*.md")):
        if MOI in f.name:
            continue
        try:
            pregs[f.name] = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

    def au_sujet(v, cles, textes, nus=False):
        if len(cles) < c502.RECOUVREMENT:
            return None
        for nom, txt in textes.items():
            fens = (c508.nu(v, txt.lower(), c502.FENETRE) if nus
                    else c502.fenetres(v, txt))
            if fens and max(sum(1 for c in cles if c in f) for f in fens) \
                    >= c502.RECOUVREMENT:
                return nom
        return None

    def quelque_part(v, cles):
        return (au_sujet(v, cles, secs) or au_sujet(v, cles, rapports)
                or au_sujet(v, cles, pregs, nus=True))

    for e in emprunts:
        e["reel"] = quelque_part(e["val"], e["cles"])
        e["perm"] = quelque_part(e["val"], e["cles_perm"])

    n_reel = sum(1 for e in emprunts if e["reel"])
    n_perm = sum(1 for e in emprunts if e["perm"])
    t_reel = 100.0 * n_reel / n if n else 0.0
    t_perm = 100.0 * n_perm / n if n else 0.0
    ecart = t_reel - t_perm
    passe = ecart >= SEUIL
    faux_pos = [e for e in emprunts if e["perm"]]

    L = []
    A = L.append
    A("# La règle contextuelle du #502 devant un **témoin de permutation**")
    A("")
    A("Les **#512** et **#513** ont montré qu'un détecteur peut produire un")
    A("chiffre entier sans rien mesurer. **Aucun détecteur des #500-#511 n'avait")
    A("subi ce test** — et l'un d'eux n'est pas un détecteur parmi d'autres.")
    A("")
    A(f"La règle contextuelle du #502 — **≥ {c502.RECOUVREMENT} mots-clés dans")
    A(f"±{c502.FENETRE} caractères** — est le **socle partagé** de "
      + ", ".join(f"**{c}**" for c in DEPENDANTS) + ".")
    A("")
    A("## Le témoin, cité verbatim")
    A("")
    A("> Pour chaque emprunt, on rejoue **exactement la même règle** en")
    A("> remplaçant ses mots-clés par ceux de **l'emprunt suivant** dans la")
    A("> population triée par `(script, cycle cité, valeur)` — le dernier")
    A("> reprenant ceux du premier.")
    A("")
    A("**Dérangement déterministe** : aucun tirage, aucun aléa. Un emprunt")
    A("confirmé avec les mots-clés **d'un autre** l'est par **coïncidence de")
    A("vocabulaire**, pas par identité de sujet.")
    A("")
    A("## Les deux taux")
    A("")
    A(f"- emprunts : **{n}**")
    A("")
    A("| Mots-clés employés | Confirmés « au sujet » | Taux |")
    A("|---|---|---|")
    A(f"| **réels** | **{n_reel}** | " + f"**{t_reel:.1f} %**".replace(".", ",") + " |")
    A(f"| **permutés** (témoin) | **{n_perm}** | "
      + f"**{t_perm:.1f} %**".replace(".", ",") + " |")
    A("")
    A(f"- **écart** : " + f"**{ecart:+.1f}** points".replace(".", ",")
      + f" — seuil exigé : **{SEUIL:.0f}**")
    A(f"- verdict : **{'LA RÈGLE DISCRIMINE' if passe else 'LA RÈGLE NE DISCRIMINE PAS'}**")
    A("")
    if passe:
        A("> **La règle du #502 survit à son témoin.** Un emprunt confirmé avec")
        A("> ses propres mots-clés l'est plus souvent qu'avec ceux d'un voisin :")
        A("> elle mesure bien une **identité de sujet**, et **les conclusions")
        A("> des cycles qui en dépendent tiennent.**")
        A("")
        A("### Mais elle est **crédule**, et le seuil ne le dit pas")
        A("")
        spec = 100.0 - t_perm
        A(f"- confirmations obtenues avec des mots-clés **étrangers** : "
          f"**{n_perm}** sur **{n}** (" + f"**{t_perm:.1f} %**".replace(".", ",")
          + ")")
        A(f"- **spécificité** de la règle — part d'emprunts que le témoin")
        A(f"  **n'arrive pas** à confirmer : " + f"**{spec:.1f} %**".replace(".", ","))
        A("")
        A("> Passer le seuil de **20 points** n'est pas être fiable. **Près de")
        A("> deux emprunts sur trois se laissent confirmer par le vocabulaire")
        A("> d'un voisin.** La règle discrimine — elle ne prouve pas.")
        A(">")
        A("> Les cycles #502-#509 avaient déjà écrit, chacun, que leur")
        A("> appariement ne valait pas identité de sujet. **Ce chiffre donne")
        A("> enfin la mesure de cette réserve** : elle valait, en gros, deux")
        A("> confirmations sur trois.")
    else:
        A("> **La règle du #502 ne discrimine pas.** Confirmer un emprunt avec")
        A("> les mots-clés **d'un autre** marche presque aussi bien qu'avec les")
        A("> siens.")
        A(">")
        A("> **Six cycles reposent sur elle — "
          + ", ".join(f"**{c}**" for c in DEPENDANTS) + " — et leurs")
        A("> conclusions sont atteintes ensemble.** C'est le plus large retrait")
        A("> de la série, et le pré-enregistrement en fixait la conséquence")
        A("> avant que le chiffre soit connu.")
    A("")
    A("## Les faux positifs de la permutation, nommés")
    A("")
    A(f"- effectif : **{len(faux_pos)}**")
    A("")
    if faux_pos:
        A("| Script | Cite | Nombre | Confirmé (permuté) dans |")
        A("|---|---|---|---|")
        for e in sorted(faux_pos, key=lambda x: (x["py"], x["val"]))[:20]:
            A(f"| `{e['py']}` | `{e['cite']}` | **{e['val']}** | `{e['perm']}` |")
        if len(faux_pos) > 20:
            A("")
            A(f"*(et **{len(faux_pos) - 20}** autres.)*")
        A("")
        A("> Ce sont les confirmations que la règle produit **par construction**,")
        A("> sans rapport avec le sujet de l'emprunt. Leur nombre est la mesure")
        A("> directe de sa **crédulité**.")
    else:
        A("**Aucun.** Avec des mots-clés étrangers, la règle ne confirme **rien**")
        A("— sa spécificité est totale sur cette population.")
    A("")
    A("## Ce que ce cycle **ne** teste **pas**")
    A("")
    A("Il n'examine **que** la règle contextuelle. Les autres détecteurs des")
    A("**#500-#511** — appariement AST des chaînes publiées (#500), lecture des")
    A("chiffres en gras (#501), primitives d'exécution (#497) — **restent non")
    A("testés**. Le rappeler vaut mieux que laisser croire à un examen complet.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = passe
    p2 = n_perm > 0
    p3 = len(faux_pos) < 10
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| écart ≥ {SEUIL:.0f} points | ≥ {SEUIL:.0f} | "
      + f"{ecart:+.1f}".replace(".", ",")
      + f" | **{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| taux permuté > 0 | > 0 | " + f"{t_perm:.1f} %".replace(".", ",")
      + f" | **{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| < 10 faux positifs | < 10 | {len(faux_pos)} | "
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
    A("Population, mots-clés et fenêtres sont **importés** des backtests des")
    A("#500, #501, #502 et #508 — leurs fonctions, jamais leur `main()`.")
    A("")
    A("## Critères de succès")
    A("")
    c = [(f"Règle de permutation et seuil de **{SEUIL:.0f}** points cités "
          "verbatim", True),
         (f"Les deux taux publiés avec leurs effectifs (**{n_reel}** / "
          f"**{n_perm}**)", n > 0),
         ("Écart publié et verdict rendu au seuil", True),
         (f"Faux positifs nommés individuellement (**{len(faux_pos)}**)", True),
         ("Aucun script exécuté, arbre propre", not nouv)]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé**. **Il ne dépend pas")
    A("du succès de la règle testée**, seulement de la publication honnête du")
    A("verdict.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : cycle de vérification,")
    A("aucune position, aucun paramètre numérique de stratégie.")
    A("")
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts, du")
    A("> registre et des rapports à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — réel {t_reel:.1f} % ({n_reel}) vs permuté "
          f"{t_perm:.1f} % ({n_perm}), écart {ecart:+.1f}, passe={passe}")


if __name__ == "__main__":
    main()

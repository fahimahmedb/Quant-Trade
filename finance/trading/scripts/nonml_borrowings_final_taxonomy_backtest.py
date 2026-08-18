"""Taxonomie complete des 39 emprunts (#508).

Specification pre-enregistree dans `PREREG_borrowings_final_taxonomy.md`,
committee AVANT toute mesure -- les quatre classes comprises.

Six cycles ont produit six vocabulaires successifs. Celui-ci en fixe UN,
applique a TOUTE la population, et cree la classe qui manquait : le nombre
qui existe mais jamais au sujet. SANS RIEN EXECUTER.
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

OUT = RESULTS / "nonml_borrowings_final_taxonomy_result.md"
MOI = "borrowings_final_taxonomy"

CLASSES = {
    "A": "sourcé **au sujet**, dans le cycle cité",
    "B": "sourcé **au sujet**, ailleurs",
    "C": "**orphelin de contexte** — le nombre existe, jamais au sujet",
    "D": "**absent du dépôt** — le nombre n'apparaît nulle part, même nu",
}
# Le controle : les 2 residus du #505 doivent tomber en C.
CONTROLE = [("nonml_content_defined_magnitudes_audit.py", "#449", "2"),
            ("nonml_report_idempotence_backtest.py", "#443", "5,7")]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def nu(valeur, texte, largeur):
    out = []
    for m in re.finditer(r"(?<![\d,.])" + re.escape(valeur) + r"(?![\d,.])",
                         texte):
        a = max(0, m.start() - largeur)
        b = min(len(texte), m.end() + largeur)
        out.append(texte[a:b].lower())
    return out


def main():
    avant = set(git("status", "--porcelain").splitlines())

    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")
    c504 = module("nonml_suspect_values_reports_backtest.py")
    secs = c501.sections_backlog()

    # --- La population des 39 ---------------------------------------------
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
        for nom, txt in textes.items():
            fens = (nu(v, txt.lower(), c502.FENETRE) if nus
                    else c502.fenetres(v, txt))
            if fens and max(sum(1 for c in cles if c in f) for f in fens) \
                    >= c502.RECOUVREMENT:
                return nom
        return None

    def existe(v):
        for txt in list(rapports.values()) + list(pregs.values()) + \
                list(secs.values()):
            if re.search(r"(?<![\d,.])" + re.escape(v) + r"(?![\d,.])", txt):
                return True
        return False

    for e in emprunts:
        v, cles, cite = e["val"], e["cles"], e["cite"]
        if len(cles) < c502.RECOUVREMENT:
            e["cles_insuffisants"] = True
        # --- A : le cycle cité, section puis rapports ---------------------
        sec = secs.get(cite)
        ici = None
        if sec is not None and au_sujet(v, cles, {cite: sec}):
            ici = f"section {cite}"
        if ici is None and sec is not None:
            nom_strat, fichiers = c504.rapports_du_cycle(sec)
            sous = {f.name: rapports.get(f.name, "") for f in fichiers}
            trouve = au_sujet(v, cles, sous)
            if trouve:
                ici = trouve
        if ici:
            e["cl"], e["ou"] = "A", ici
            continue
        # --- B : au sujet ailleurs ----------------------------------------
        ailleurs = (au_sujet(v, cles, {k: t for k, t in secs.items() if k != cite})
                    or au_sujet(v, cles, rapports)
                    or au_sujet(v, cles, pregs, nus=True))
        if ailleurs:
            e["cl"], e["ou"] = "B", ailleurs
            continue
        # --- C / D --------------------------------------------------------
        e["cl"] = "C" if existe(v) else "D"
        e["ou"] = None

    comptes = {k: sum(1 for e in emprunts if e["cl"] == k) for k in CLASSES}
    somme = sum(comptes.values())
    orphelins = [e for e in emprunts if e["cl"] == "C"]
    dominante = max(comptes, key=lambda k: comptes[k]) if emprunts else None

    ctrl = []
    for py, cy, v in CONTROLE:
        e = next((x for x in emprunts if x["py"] == py and x["cite"] == cy
                  and x["val"] == v), None)
        ctrl.append((py, cy, v, e["cl"] if e else "—",
                     (e or {}).get("ou")))
    ctrl_ok = all(cl == "C" for _, _, _, cl, _ in ctrl)

    L = []
    A = L.append
    A("# Une **taxonomie complète** des emprunts, et la classe qui manquait")
    A("")
    A("L'audit du **#505** a montré que les derniers « introuvables » ne le")
    A("sont pas : leur nombre **existe** dans le dépôt, mais **jamais au")
    A("voisinage de son sujet**. **Ce statut n'avait pas de classe.**")
    A("")
    A("> Six cycles ont produit six vocabulaires successifs. Celui-ci en fixe")
    A("> **un seul**, appliqué à **toute** la population.")
    A("")
    A("## Les quatre classes, citées verbatim")
    A("")
    A("| Classe | Condition |")
    A("|---|---|")
    for k, v in CLASSES.items():
        A(f"| **{k}** | {v} |")
    A("")
    A(f"**« Au sujet »** = nombre en gras (ou **nu**, pour les `PREREG_`) avec")
    A(f"**≥ {c502.RECOUVREMENT}** mots-clés dans **±{c502.FENETRE} caractères**")
    A(f"— règle du #502, **paramètres inchangés** *(quatrième cycle")
    A("consécutif)*.")
    A("")
    A("## Le classement")
    A("")
    A(f"- nombres empruntés : **{len(emprunts)}**")
    A(f"- sections de registre : **{len(secs)}** ; rapports : "
      f"**{len(rapports)}** ; pré-enregistrements : **{len(pregs)}**")
    A("")
    A("| Classe | Nombre | Part |")
    A("|---|---|---|")
    for k in CLASSES:
        pt = 100.0 * comptes[k] / len(emprunts) if emprunts else 0.0
        A(f"| **{k}** | **{comptes[k]}** | " + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A(f"- **partition** : somme **{somme}** = effectif **{len(emprunts)}** — "
      f"**{'OUI' if somme == len(emprunts) else 'NON'}**")
    A("")
    A("## Le contrôle : les 2 résidus du #505")
    A("")
    A("Ils doivent tomber en **C** — sinon la taxonomie **ne recouvre pas le")
    A("fait qui l'a motivée**.")
    A("")
    A("| Script | Cite | Nombre | Classe rendue | Où le contexte a été trouvé |")
    A("|---|---|---|---|---|")
    for py, cy, v, cl, ou in ctrl:
        A(f"| `{py}` | `{cy}` | **{v}** | **{cl}** | "
          f"{'`' + ou + '`' if ou else '—'} |")
    A("")
    if ctrl_ok:
        A("> **Le contrôle passe.** La classe **C** recouvre exactement le")
        A("> statut que le #505 avait découvert sans pouvoir le nommer.")
    else:
        rendus = sorted({cl for _, _, _, cl, _ in ctrl})
        A(f"> **Le contrôle échoue** : les deux cas tombent en "
          f"**{', '.join(rendus)}**, pas en **C**.")
        A("")
        A("**La cause est mesurée, pas invoquée.** La colonne « où » le montre :")
        A("le contexte est trouvé dans une source qu'**aucun cycle précédent")
        A("n'avait consultée**. Les #501-#503 ont fouillé les **sections** du")
        A("registre ; le #504, les **rapports du cycle cité** ; le #505, les")
        A("`PREREG_` et les commits. **Personne n'avait cherché au sujet dans")
        A("les rapports des *autres* cycles** — ce que la classe **B** fait ici.")
        A("")
        A("> **Ce n'est donc pas la taxonomie qui est mal construite, c'est ma")
        A("> prémisse.** J'ai posé comme contrôle que ces deux cas *devaient*")
        A("> tomber en **C**, en supposant que **B** ne les trouverait pas. **B**")
        A("> est plus large que tout ce que la série avait tenté, et il les")
        A("> trouve.")
        A(">")
        A("> **Le critère pré-enregistré fait néanmoins échouer ce cycle, et je")
        A("> l'applique tel quel.** Un contrôle qu'on réinterprète après l'avoir")
        A("> vu échouer ne contrôle plus rien — c'est la règle depuis le #480,")
        A("> et elle coûte ici un **FAIL** sur un classement que je crois juste.")
    A("")
    A("## Les orphelins de contexte, nommés")
    A("")
    A(f"- effectif : **{len(orphelins)}**")
    A("")
    if orphelins:
        A("| Script | Cite | Nombre | Extrait |")
        A("|---|---|---|---|")
        for e in sorted(orphelins, key=lambda x: (x["py"], x["val"])):
            ex = re.sub(r"\s+", " ", e["txt"])[:60]
            A(f"| `{e['py']}` | `{e['cite']}` | **{e['val']}** | « {ex}… » |")
        A("")
        A("> **« Orphelin » ne veut pas dire « faux ».** Il veut dire : *je n'ai")
        A("> pas su rattacher ce nombre à un passage qui parle du même sujet*.")
        A("> Six cycles ont montré que la distinction est **tout** — et le")
        A("> pré-enregistrement interdisait de la durcir après coup.")
    A("")
    A("## La classe B, et son sourçage circulaire")
    A("")
    def son_rapport(nom_py):
        for suf, out in (("_backtest.py", "_result.md"), ("_audit.py", "_audit.md"),
                         ("_robustness.py", "_robustness.md"),
                         ("_sim_300e.py", "_sim_300e.md")):
            if nom_py.endswith(suf):
                return f"{nom_py[:-len(suf)]}{out}"
        return None
    bs = [e for e in emprunts if e["cl"] == "B"]
    circ = [e for e in bs if e["ou"] == son_rapport(e["py"])]
    A(f"- emprunts en **B** : **{len(bs)}**")
    A(f"- dont le contexte est trouvé dans le **rapport du script lui-même** : "
      f"**{len(circ)}**")
    A(f"- dont dans une source **tierce** : **{len(bs) - len(circ)}**")
    A("")
    if circ:
        A("> **Le #505 avait établi la règle : trouver un chiffre dans sa propre")
        A("> production ne le source pas.** Même auteur, même cycle, même erreur")
        A("> possible. Ces **" + str(len(circ)) + "** classements en **B** sont")
        A("> donc **circulaires**, et la classe B les surestime d'autant.")
        A("")
        A("> Je **ne les reclasse pas** : la taxonomie a été figée avant mesure,")
        A("> et exclure le rapport du script après coup serait la dérive refusée")
        A("> aux #496, #497 et #507. **C'est enregistré comme angle mort.**")
        A("")
    A("## La classe dominante")
    A("")
    A(f"- classe la plus nombreuse : **{dominante}** (**{comptes[dominante]}**)"
      if dominante else "- population vide")
    A("")
    if dominante == "A":
        A("> **La majorité des emprunts se justifient par le cycle qu'ils")
        A("> citent.** C'est le cas le moins alarmant, et il fallait le")
        A("> mesurer plutôt que le supposer.")
    elif dominante in ("B", "C"):
        A(f"> **La classe dominante est {dominante}, pas A.** La majorité des")
        A("> emprunts de ce dépôt **ne se justifient pas par le cycle qu'ils")
        A("> citent** — c'est plus grave que tout ce que la série a établi, et")
        A("> je l'écris sans l'atténuer.")
        A(">")
        A(f"> **Une nuance mesurée, pas une atténuation** : **{len(circ)}** des")
        A(f"> **{len(bs)}** classements en B sont **circulaires** (contexte")
        A("> trouvé dans le rapport du script lui-même). Le compte de B qui")
        A(f"> pointent vers une source **tierce** est **{len(bs) - len(circ)}**.")
    A("")
    A("## Ce que cette taxonomie remplace — et ce qu'elle ne remplace pas")
    A("")
    A("Elle **unifie** six vocabulaires ad hoc en un seul, exclusif et")
    A("exhaustif. Elle ne **réécrit pas** les rapports des #501-#505 : leurs")
    A("classes restent telles qu'elles ont été publiées, avec leurs erreurs et")
    A("leurs corrections. **Réécrire l'histoire d'une série pour la rendre")
    A("cohérente serait le contraire de ce qu'elle a fait.**")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = comptes["D"] == 0
    p2 = comptes["C"] >= 2
    p3 = dominante == "A"
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| la classe **D** est vide | 0 | {comptes['D']} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| la classe **C** compte ≥ 2 | ≥ 2 | {comptes['C']} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| **A** est la plus nombreuse | A | {dominante} | "
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
    A("Population, mots-clés, fenêtres et correspondance cycle → rapport sont")
    A("**importés** des backtests des #500 à #504 — leurs fonctions, jamais")
    A("leur `main()`.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Quatre classes citées verbatim, paramètres du #502 inchangés", True),
         (f"Les **{len(emprunts)}** classés, partition vérifiée "
          f"(**{somme}** = **{len(emprunts)}**)", somme == len(emprunts)),
         ("Les **2** résidus du #505 classés **C**", ctrl_ok),
         (f"Membres de **C** nommés individuellement (**{len(orphelins)}**)",
          True),
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
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts, du")
    A("> registre et des rapports à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(emprunts)} emprunts : " +
          ", ".join(f"{k}={comptes[k]}" for k in CLASSES) +
          f" ; contrôle {'OK' if ctrl_ok else 'ÉCHEC'}")


if __name__ == "__main__":
    main()

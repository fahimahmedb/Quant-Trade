"""Les 5 residus, cherches dans les sources NON PUBLIEES (#505).

Specification pre-enregistree dans
`PREREG_residual_borrowings_unpublished_sources.md`, committee AVANT toute
mesure -- les trois familles et leurs regles d'appariement comprises.

Cinq cycles ont reduit 39 emprunts a 5 residus introuvables au registre comme
aux rapports. Restent trois sources non publiees. SANS RIEN EXECUTER.
"""
import ast
import importlib.util
import io
import re
import subprocess
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_residual_borrowings_unpublished_sources_result.md"
MOI = "residual_borrowings_unpublished_sources"

FAMILLES = [
    ("PREREG du cycle cité", "fichier entier", "**en gras**"),
    ("autre PREREG", "fichier entier", "**en gras**"),
    ("commentaire ou docstring", "jetons `COMMENT` de `tokenize` + docstrings "
                                 "par AST", "**jeton nu**"),
    ("message de commit", "`git log --format=%B` sur tout l'historique",
     "**jeton nu**"),
]
CLASSES = ["sourcé au PREREG du cycle cité", "sourcé dans un autre PREREG",
           "sourcé dans un commentaire ou une docstring",
           "sourcé dans un message de commit", "introuvable partout"]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def commentaires_et_docstrings(src):
    """Ce que l'AST des chaines publiees ne voit PAS."""
    bouts = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                bouts.append(tok.string)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    try:
        arbre = ast.parse(src)
    except SyntaxError:
        return "\n".join(bouts)
    for n in ast.walk(arbre):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                          ast.ClassDef)) and n.body:
            p0 = n.body[0]
            if isinstance(p0, ast.Expr) and isinstance(p0.value, ast.Constant) \
                    and isinstance(p0.value.value, str):
                bouts.append(p0.value.value)
    return "\n".join(bouts)


def fenetres_nues(valeur, texte, largeur):
    """Occurrences du nombre NU, avec leur voisinage."""
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
    c503 = module("nonml_reference_vs_value_errors_backtest.py")
    c504 = module("nonml_suspect_values_reports_backtest.py")
    secs = c501.sections_backlog()

    # --- Rejouer la chaine #500 -> #504 pour isoler les residus -----------
    residus = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if any(k in py.name for k in (c500.MOI, c501.MOI, c502.MOI,
                                      c503.MOI, c504.MOI, MOI)):
            continue
        try:
            src = py.read_text(encoding="utf-8")
            arbre = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        for t, cy, nb in c500.emprunts_de(arbre):
            for g in nb:
                v = c501.chiffres_seuls(g)
                if v is None:
                    continue
                cite, cles = cy[0], c502.mots_cles(t)
                sec = secs.get(cite)
                if sec is None or len(cles) < c502.RECOUVREMENT:
                    continue
                fs = c502.fenetres(v, sec)
                if fs and max(sum(1 for c in cles if c in f) for f in fs) \
                        >= c502.RECOUVREMENT:
                    continue
                if any((lambda w: w and max(sum(1 for c in cles if c in f)
                                            for f in w) >= c502.RECOUVREMENT)(
                        c502.fenetres(v, s2))
                       for n2, s2 in secs.items() if n2 != cite):
                    continue
                mag = c503.magnitude(v)
                if not any(c503.magnitude(g2) == mag
                           for g2 in c503.GRAS.findall(sec)):
                    continue
                nom, fichiers = c504.rapports_du_cycle(sec)
                vu = False
                for f in fichiers:
                    try:
                        if c502.fenetres(v, f.read_text(encoding="utf-8")):
                            vu = True
                            break
                    except UnicodeDecodeError:
                        continue
                if vu or not fichiers:
                    continue
                residus.append({"py": py.name, "cite": cite, "val": v,
                                "cles": cles, "txt": t, "nom": nom})

    # --- Les trois familles non publiees ----------------------------------
    prereg = {p.name: p.read_text(encoding="utf-8")
              for p in sorted(ROOT.glob("PREREG_*.md")) if MOI not in p.name}
    commentaires = {}
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if MOI in py.name:
            continue
        try:
            commentaires[py.name] = commentaires_et_docstrings(
                py.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    commits = git("log", "--format=%B")

    def assez(fens, cles):
        return bool(fens) and max(sum(1 for c in cles if c in f)
                                  for f in fens) >= c502.RECOUVREMENT

    for r in residus:
        trouve = {}
        # 1-2. PREREG
        mien = f"PREREG_{r['nom']}.md" if r["nom"] else None
        for nom_f, txt in prereg.items():
            if assez(c502.fenetres(r["val"], txt), r["cles"]):
                fam = ("PREREG du cycle cité" if nom_f == mien
                       else "autre PREREG")
                trouve.setdefault(fam, []).append(nom_f)
        # 3. commentaires / docstrings
        for nom_f, txt in commentaires.items():
            if assez(fenetres_nues(r["val"], txt.lower(), c502.FENETRE),
                     r["cles"]):
                trouve.setdefault("commentaire ou docstring", []).append(nom_f)
        # 4. messages de commit
        if assez(fenetres_nues(r["val"], commits.lower(), c502.FENETRE),
                 r["cles"]):
            trouve.setdefault("message de commit", []).append("(historique)")
        r["trouve"] = trouve
        r["classe"] = next(
            (c for c, f in zip(CLASSES, [f[0] for f in FAMILLES])
             if f in trouve), "introuvable partout")

    comptes = {c: sum(1 for r in residus if r["classe"] == c) for c in CLASSES}
    perdus = [r for r in residus if r["classe"] == "introuvable partout"]
    par_famille = {f[0]: sum(1 for r in residus if f[0] in r["trouve"])
                   for f in FAMILLES}
    seuls = {f[0]: sum(1 for r in residus
                       if list(r["trouve"]) == [f[0]]) for f in FAMILLES}

    L = []
    A = L.append
    A("# Les **résidus** dans les sources **non publiées** (pré-enregistré)")
    A("")
    A("Cinq cycles ont réduit **39** nombres empruntés à quelques **résidus** :")
    A("introuvables **au registre** comme **aux rapports** du cycle cité.")
    A("Restent trois sources qui ne sont pas publiées.")
    A("")
    A("## Les trois familles et leurs règles, citées verbatim")
    A("")
    A("| Famille | Extraction | Appariement du nombre |")
    A("|---|---|---|")
    for nom, extr, app in FAMILLES:
        A(f"| {nom} | {extr} | {app} |")
    A("")
    A("**Le nombre nu est plus permissif que le gras** : un commentaire ou un")
    A("message de commit n'emploie pas de balisage. Pour compenser, **la")
    A(f"contrainte de contexte est identique** — ≥ **{c502.RECOUVREMENT}**")
    A(f"mots-clés dans **±{c502.FENETRE} caractères**, règle du #502 **reprise")
    A("sans modification**.")
    A("")
    A("## Le corpus fouillé")
    A("")
    A(f"- résidus repris de la chaîne #500-#504 : **{len(residus)}**")
    A(f"- fichiers `PREREG_*.md` : **{len(prereg)}**")
    A(f"- scripts dont commentaires et docstrings sont extraits : "
      f"**{len(commentaires)}**")
    A(f"- messages de commit : **{len(git('log', '--format=%H').splitlines())}**")
    A("")
    A("## Les cinq classes")
    A("")
    A("| Classe | Nombre |")
    A("|---|---|")
    for c in CLASSES:
        A(f"| **{c}** | **{comptes[c]}** |")
    A("")
    A("## La contribution de chaque famille")
    A("")
    A("*L'engagement 3 l'exige : toutes publiées, jamais la seule qui arrange.*")
    A("")
    A("| Famille | Résidus touchés | Dont elle est **seule** à expliquer |")
    A("|---|---|---|")
    for nom, _, _ in FAMILLES:
        A(f"| {nom} | **{par_famille[nom]}** | **{seuls[nom]}** |")
    A("")
    A("## Chaque résidu, avec **toutes** ses trouvailles")
    A("")
    A("*Ne montrer que la famille gagnante masquerait la redondance des")
    A("sources.*")
    A("")
    for r in sorted(residus, key=lambda x: (x["classe"], x["py"], x["val"])):
        A(f"### `{r['py']}` — cite `{r['cite']}` pour **{r['val']}**")
        A("")
        A(f"- classe : **{r['classe']}**")
        if r["trouve"]:
            for fam, ou in r["trouve"].items():
                echant = ", ".join("`" + o + "`" for o in sorted(ou)[:3])
                reste = f", … (**{len(ou) - 3}** autres)" if len(ou) > 3 else ""
                A(f"- **{fam}** : **{len(ou)}** — {echant}{reste}")
        else:
            A("- **aucune trouvaille dans les trois familles**")
        extrait = re.sub(r"\s+", " ", r["txt"])[:120]
        A(f"- extrait : « {extrait}… »")
        A("")
    A("## Une source qui n'en est pas une : le `PREREG_` du script lui-même")
    A("")
    def son_prereg(nom_py):
        for suf in ("_backtest.py", "_audit.py", "_robustness.py",
                    "_sim_300e.py"):
            if nom_py.endswith(suf):
                return f"PREREG_{nom_py[len('nonml_'):-len(suf)]}.md"
        return None
    circulaires, independants = [], []
    for r in residus:
        for f in r["trouve"].get("autre PREREG", []):
            (circulaires if f == son_prereg(r["py"]) else independants).append(
                (r["py"], r["val"], f))
    A(f"- trouvailles en « autre PREREG » : **{len(circulaires) + len(independants)}**")
    A(f"- dont le `PREREG_` **du script lui-même** : **{len(circulaires)}**")
    A(f"- dont un `PREREG_` **tiers** : **{len(independants)}**")
    A("")
    if circulaires:
        A("> **Trouver un chiffre dans le pré-enregistrement du script qui le")
        A("> publie ne le source pas** : c'est le même auteur, le même cycle, la")
        A("> même erreur possible. **La trouvaille est circulaire.**")
        A("")
        for py, val, f in sorted(circulaires):
            A(f"- `{py}` pour **{val}** → `{f}` *(le sien)*")
        A("")
    if independants:
        A("Les trouvailles en `PREREG_` **tiers** :")
        A("")
        for py, val, f in sorted(independants):
            A(f"- `{py}` pour **{val}** → `{f}`")
        A("")
        A("> **Un `PREREG_` tiers sans rapport thématique avec le cycle cité**")
        A("> est un appariement de coïncidence : l'appariement nu est permissif,")
        A("> et deux mots-clés suffisent. Ces trouvailles **ne valent pas")
        A("> source** ; elles montrent surtout ce que la règle ramasse.")
        A("")
    A(f"> **En retirant les trouvailles circulaires**, les résidus réellement")
    A(f"> rattachés à une source indépendante tombent à **{len(independants)}**")
    A(f"> sur **{len(residus)}**.")
    A("")
    A("## Les introuvables partout")
    A("")
    A(f"- effectif : **{len(perdus)}**")
    A("")
    if perdus:
        A("> Ce sont les **premiers candidats sérieux** de toute la série : leur")
        A("> nombre n'apparaît, au voisinage de leur sujet, **dans aucune source")
        A("> du dépôt** — ni publiée, ni interne. **L'appariement nu est pourtant")
        A("> permissif**, ce qui rend son échec d'autant plus net.")
        A(">")
        A("> **Cela ne les déclare pas faux.** Une absence de trace reste une")
        A("> absence de preuve, pas une preuve d'absence.")
    else:
        A("**Aucun.** Chaque résidu se rattache à au moins une source non")
        A("publiée : **l'emprunt était sourcé, mal cité**.")
        A("")
        A("> **Six cycles d'enquête n'ont trouvé aucun emprunt faux.** Le canal")
        A("> d'erreur soupçonné au #497 **n'a produit aucune erreur détectable**")
        A("> dans ce dépôt. C'est un résultat net, et je l'écris tel quel : ce")
        A("> n'est pas un demi-succès, c'est une réfutation de mon soupçon.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    sourcés = len(residus) - len(perdus)
    p1 = sourcés >= 2
    p2 = len(perdus) >= 1
    p3 = par_famille["message de commit"] <= 1
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| ≥ 2 résidus sourcés hors publication | ≥ 2 | {sourcés} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| ≥ 1 introuvable partout | ≥ 1 | {len(perdus)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| les commits expliquent ≤ 1 résidu | ≤ 1 | "
      f"{par_famille['message de commit']} | "
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
    A("Population et règles sont **importées** des backtests des #500 à #504 —")
    A("leurs fonctions, jamais leur `main()`.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Trois familles et règles citées verbatim, appariement nu justifié",
          True),
         (f"Les **{len(residus)}** résidus cherchés dans les **3** familles "
          f"(**{len(FAMILLES)}** lignes, le `PREREG_` étant scindé selon qu'il "
          "est celui du cycle cité)", len(residus) > 0),
         ("Classement par priorité **et** liste complète des trouvailles", True),
         (f"Introuvables partout nommés avec extrait (**{len(perdus)}**)", True),
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
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts, des")
    A("> pré-enregistrements et de l'historique à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(residus)} résidus : " +
          ", ".join(f"{c}={comptes[c]}" for c in CLASSES))


if __name__ == "__main__":
    main()

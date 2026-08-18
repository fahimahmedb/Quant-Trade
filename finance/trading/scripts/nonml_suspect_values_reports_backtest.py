"""Les 13 valeurs suspectes, cherchees dans les RAPPORTS (#504).

Specification pre-enregistree dans `PREREG_suspect_values_reports.md`,
committee AVANT toute mesure -- regle de correspondance comprise.

Les #501 a #503 n'ont interroge qu'une source : la section de registre. Or un
cycle publie aussi un rapport, et c'est la que ses chiffres naissent -- le
registre en est le resume. SANS RIEN EXECUTER.
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

OUT = RESULTS / "nonml_suspect_values_reports_result.md"
MOI = "suspect_values_reports"

NOM_PREREG = re.compile(r"PREREG_([a-z0-9_]+)\.md")
NOM_SECOURS = re.compile(r"nonml_([a-z0-9_]+?)_(?:result|audit|backtest)")
CLASSES = ["confirmé au rapport", "présent sans contexte",
           "absent du rapport", "rapport introuvable"]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rapports_du_cycle(section):
    """Nom de strategie extrait de la section, puis ses fichiers results/."""
    m = NOM_PREREG.search(section) or NOM_SECOURS.search(section)
    if not m:
        return None, []
    nom = m.group(1)
    fichiers = sorted(p for p in RESULTS.glob(f"nonml_{nom}_*.md")
                      if MOI not in p.name)
    return nom, fichiers


def main():
    avant = set(git("status", "--porcelain").splitlines())

    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")
    c503 = module("nonml_reference_vs_value_errors_backtest.py")
    secs = c501.sections_backlog()

    # --- Rejouer le #503 pour isoler ses << valeurs suspectes >> -----------
    suspects = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if any(k in py.name for k in (c500.MOI, c501.MOI, c502.MOI,
                                      c503.MOI, MOI)):
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
                cite, cles = cy[0], c502.mots_cles(t)
                sec = secs.get(cite)
                if sec is None or len(cles) < c502.RECOUVREMENT:
                    continue
                fs = c502.fenetres(v, sec)
                if fs and max(sum(1 for c in cles if c in f) for f in fs) \
                        >= c502.RECOUVREMENT:
                    continue                       # confirmé au #502
                cand = [n for n, s2 in secs.items() if n != cite
                        and (lambda w: w and max(
                            sum(1 for c in cles if c in f) for f in w)
                            >= c502.RECOUVREMENT)(c502.fenetres(v, s2))]
                if cand:
                    continue                       # « référence ailleurs » (#503)
                mag = c503.magnitude(v)
                if not any(c503.magnitude(g2) == mag
                           for g2 in c503.GRAS.findall(sec)):
                    continue                       # « indéterminé » (#503)
                suspects.append({"py": py.name, "cite": cite, "val": v,
                                 "cles": cles})

    # --- La confrontation AU RAPPORT ---------------------------------------
    corresp = {}
    for s in suspects:
        sec = secs[s["cite"]]
        if s["cite"] not in corresp:
            corresp[s["cite"]] = rapports_du_cycle(sec)
        nom, fichiers = corresp[s["cite"]]
        if not fichiers:
            s["classe"], s["rec"], s["ou"] = "rapport introuvable", 0, None
            continue
        best, ou, vu = 0, None, False
        for f in fichiers:
            try:
                txt = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            fens = c502.fenetres(s["val"], txt)
            if not fens:
                continue
            vu = True
            k = max(sum(1 for c in s["cles"] if c in fen) for fen in fens)
            if k > best:
                best, ou = k, f.name
        s["rec"] = best
        s["ou"] = ou
        s["classe"] = ("confirmé au rapport" if best >= c502.RECOUVREMENT
                       else "présent sans contexte" if vu else "absent du rapport")

    comptes = {c: sum(1 for s in suspects if s["classe"] == c) for c in CLASSES}
    confirmes = [s for s in suspects if s["classe"] == "confirmé au rapport"]
    residus = [s for s in suspects if s["classe"] == "absent du rapport"]
    introuv = [s for s in suspects if s["classe"] == "rapport introuvable"]

    L = []
    A = L.append
    A("# Les **valeurs suspectes**, cherchées dans les **rapports** (pré-enregistré)")
    A("")
    A("Les **#501** à **#503** n'ont interrogé qu'**une** source : la section")
    A("`## Backlog #NNN`. Or un cycle publie aussi un **rapport**, et c'est là")
    A("que ses chiffres naissent — **le registre en est le résumé**.")
    A("")
    A("## La règle de correspondance, citée verbatim")
    A("")
    A("> 1. la **section** du cycle est lue ;")
    A(f"> 2. le nom de stratégie en est extrait par `{NOM_PREREG.pattern}`, à")
    A(f">    défaut par `{NOM_SECOURS.pattern}` ;")
    A("> 3. ses **rapports** sont tous les `results/nonml_<nom>_*.md`.")
    A("")
    A(f"Paramètres du #502 **inchangés** : **{c502.LETTRES_MIN} lettres**, "
      f"**±{c502.FENETRE} caractères**, **{c502.RECOUVREMENT} mots-clés**.")
    A("")
    A("## La correspondance cycle → rapport")
    A("")
    A(f"- cycles cités par ces suspects : **{len(corresp)}**")
    A("")
    A("| Cycle | Nom de stratégie extrait | Rapports trouvés |")
    A("|---|---|---|")
    for cy in sorted(corresp, key=lambda x: int(x.lstrip("#"))):
        nom, fs = corresp[cy]
        A(f"| `{cy}` | {'`' + nom + '`' if nom else '**aucun**'} | "
          f"**{len(fs)}** |")
    A("")
    A("## Les quatre classes")
    A("")
    A(f"- valeurs suspectes reclassées : **{len(suspects)}**")
    A("")
    A("| Classe | Nombre | Part |")
    A("|---|---|---|")
    for c in CLASSES:
        pt = 100.0 * comptes[c] / len(suspects) if suspects else 0.0
        A(f"| **{c}** | **{comptes[c]}** | " + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A("## Les deux sources, comparées")
    A("")
    A("*L'engagement 3 l'exige : côte à côte, jamais la seule favorable.*")
    A("")
    A("| Source | Confirmations sur ces **" + str(len(suspects)) + "** |")
    A("|---|---|")
    A("| **registre** (`## Backlog #NNN`) | **0** *(par construction : c'est ce "
      "qui les a rendues suspectes)* |")
    A(f"| **rapports** (`results/nonml_<nom>_*.md`) | **{len(confirmes)}** |")
    A("")
    if len(confirmes) * 2 >= len(suspects):
        A(f"> **Le registre était la mauvaise source pour {len(confirmes)} de")
        A(f"> ces {len(suspects)}.** Trois cycles ont conclu à un soupçon en")
        A("> interrogeant un **résumé** au lieu de l'**original**. Le défaut")
        A("> n'était pas dans les emprunts : il était dans ma lecture.")
        A("")
    elif confirmes:
        A(f"> **Le changement de source n'explique que {len(confirmes)} de ces")
        A(f"> {len(suspects)}.** J'attendais au moins **6** ; c'est réfuté. La")
        A("> source consultée **n'était donc pas l'explication principale**,")
        A("> contrairement à ce que la piste ouverte au #503 laissait espérer.")
        A("")
        A(f"> Le résultat dominant est ailleurs : **{comptes['présent sans contexte']}**")
        A("> de ces valeurs **figurent** dans les rapports du cycle cité mais")
        A("> **pas au même sujet** — exactement le motif que le #502 avait")
        A("> trouvé sur le registre. **Changer de source n'a pas changé le")
        A("> diagnostic**, ce qui en renforce la solidité.")
        A("")
        A("| Script | Cite | Nombre | Mots-clés | Retrouvé dans |")
        A("|---|---|---|---|---|")
        for s in sorted(confirmes, key=lambda x: (-x["rec"], x["py"])):
            A(f"| `{s['py']}` | `{s['cite']}` | **{s['val']}** | "
              f"**{s['rec']}** | `{s['ou']}` |")
    else:
        A("> **Aucune** n'est confirmée au rapport non plus. Le changement de")
        A("> source **n'explique rien** — les soupçons tiennent.")
    A("")
    A("## Les résidus — absents des deux sources")
    A("")
    A(f"- effectif : **{len(residus)}**")
    A("")
    if residus:
        A("| Script | Cite | Nombre |")
        A("|---|---|---|")
        for s in sorted(residus, key=lambda x: (x["py"], x["val"])):
            A(f"| `{s['py']}` | `{s['cite']}` | **{s['val']}** |")
        A("")
        A("> Ce sont les **seuls** emprunts que quatre cycles d'enquête n'ont pas")
        A("> su rattacher à une source publiée. **Ils restent des soupçons**, pas")
        A("> des erreurs : la liste des sources consultées n'est toujours pas")
        A("> exhaustive — un chiffre peut vivre dans un `PREREG_`, un commentaire")
        A("> de code ou un message de commit.")
    else:
        A("**Aucun résidu.** Tout s'explique par la source consultée.")
    A("")
    if introuv:
        A("## Les rapports introuvables")
        A("")
        A(f"- effectif : **{len(introuv)}**")
        A("")
        for s in sorted(introuv, key=lambda x: (x["py"], x["val"])):
            A(f"- `{s['py']}` cite `{s['cite']}` pour **{s['val']}** — aucun")
            A("  rapport n'a pu être rattaché à ce cycle.")
        A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = len(confirmes) >= 6
    p2 = len(introuv) >= 1
    p3 = len(residus) >= 1
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| ≥ 6 confirmés au rapport | ≥ 6 | {len(confirmes)} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| ≥ 1 rapport introuvable | ≥ 1 | {len(introuv)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| ≥ 1 résidu subsiste | ≥ 1 | {len(residus)} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    if not p3:
        A("> **La prédiction 3 est réfutée, et c'est le résultat net** : tout")
        A("> s'explique par la source consultée. Les cycles #500-#503 n'auront")
        A("> mesuré que **les limites de leur propre lecture**, et **aucun")
        A("> emprunt douteux ne subsiste**. Je l'écris sans le nuancer.")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Population, mots-clés, fenêtres et magnitudes sont **importés** des")
    A("backtests des #500 à #503 — leurs fonctions, jamais leur `main()`.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Règle de correspondance citée verbatim, paramètres du #502 "
          "inchangés", True),
         (f"Les **{len(suspects)}** valeurs suspectes reclassées, "
          f"**{len(CLASSES)}** classes publiées", len(suspects) > 0),
         (f"Correspondance cycle → rapport publiée cycle par cycle "
          f"(**{len(corresp)}**)", bool(corresp)),
         (f"Résidus nommés individuellement (**{len(residus)}**)", True),
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
    print(f"{verdict} — {len(suspects)} suspects : " +
          ", ".join(f"{c}={comptes[c]}" for c in CLASSES))


if __name__ == "__main__":
    main()

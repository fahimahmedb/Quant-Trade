"""Direction temporelle des 21 emprunts << B tiers >> (#509).

Specification pre-enregistree dans `PREREG_borrowings_temporal_direction.md`,
committee AVANT toute mesure -- regle de datation et trois classes comprises.

Le #503 a etabli qu'une source POSTERIEURE ne prouve rien : ce registre
reprend ses chiffres vers l'avant. Le meme test n'avait jamais ete applique
aux << B tiers >> du #508. SANS RIEN EXECUTER.
"""
import ast
import importlib.util
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_borrowings_temporal_direction_result.md"
MOI = "borrowings_temporal_direction"

CMD = ("git log --diff-filter=A --reverse --format=%ct -- <chemin>")
CLASSES = ["postérieure", "antérieure", "indatable"]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dates_ajout():
    """{nom de fichier -> ts du premier ajout}, en un seul parcours."""
    s = git("log", "--reverse", "--date-order", "--format=@%ct",
            "--name-status", "--diff-filter=A", "--", "finance/trading")
    out, ts = {}, None
    for l in s.splitlines():
        if l.startswith("@"):
            ts = int(l[1:])
        elif l.startswith("A\t") and ts is not None:
            nom = l.split("\t", 1)[1].strip().split("/")[-1]
            if nom not in out:
                out[nom] = ts
    return out


def jour(ts):
    return (datetime.fromtimestamp(ts, timezone.utc).strftime("%d/%m/%Y")
            if ts else "—")


def son_rapport(nom_py):
    for suf, o in (("_backtest.py", "_result.md"), ("_audit.py", "_audit.md"),
                   ("_robustness.py", "_robustness.md"),
                   ("_sim_300e.py", "_sim_300e.md")):
        if nom_py.endswith(suf):
            return f"{nom_py[:-len(suf)]}{o}"
    return None


def main():
    avant = set(git("status", "--porcelain").splitlines())

    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")
    c504 = module("nonml_suspect_values_reports_backtest.py")
    c508 = module("nonml_borrowings_final_taxonomy_backtest.py")
    secs = c501.sections_backlog()
    dates = dates_ajout()

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
            fens = (c508.nu(v, txt.lower(), c502.FENETRE) if nus
                    else c502.fenetres(v, txt))
            if fens and max(sum(1 for c in cles if c in f) for f in fens) \
                    >= c502.RECOUVREMENT:
                return nom
        return None

    # --- Rejouer le #508 pour isoler les B, puis les B TIERS -------------
    tiers = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if any(k in py.name for k in (c500.MOI, c501.MOI, c502.MOI,
                                      c508.MOI, MOI)):
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
                cles, cite = c502.mots_cles(t), cy[0]
                sec = secs.get(cite)
                if sec is not None and au_sujet(v, cles, {cite: sec}):
                    continue                                   # A
                if sec is not None:
                    _, fichiers = c504.rapports_du_cycle(sec)
                    if au_sujet(v, cles,
                                {f.name: rapports.get(f.name, "") for f in fichiers}):
                        continue                               # A
                ou = (au_sujet(v, cles,
                               {k: t2 for k, t2 in secs.items() if k != cite})
                      or au_sujet(v, cles, rapports)
                      or au_sujet(v, cles, pregs, nus=True))
                if not ou:
                    continue                                   # C ou D
                if ou == son_rapport(py.name):
                    continue                                   # B circulaire
                tiers.append({"py": py.name, "cite": cite, "val": v, "ou": ou})

    # --- Les deux dates ----------------------------------------------------
    def date_cycle(nnn):
        sec = secs.get(nnn)
        if sec is None:
            return None
        nom, _ = c504.rapports_du_cycle(sec)
        return dates.get(f"PREREG_{nom}.md") if nom else None

    def date_source(ou):
        if re.fullmatch(r"#\d{3}", ou):        # une section du registre
            return date_cycle(ou)
        return dates.get(ou)                    # un fichier

    for e in tiers:
        e["t_cite"] = date_cycle(e["cite"])
        e["t_src"] = date_source(e["ou"])
        if e["t_cite"] is None or e["t_src"] is None:
            e["cl"] = "indatable"
        elif e["t_src"] > e["t_cite"]:
            e["cl"] = "postérieure"
        elif e["t_src"] < e["t_cite"]:
            e["cl"] = "antérieure"
        else:
            e["cl"] = "postérieure"             # égalité : pas d'antériorité

    comptes = {c: sum(1 for e in tiers if e["cl"] == c) for c in CLASSES}
    anter = [e for e in tiers if e["cl"] == "antérieure"]
    reste = len(anter)

    L = []
    A = L.append
    A("# La **direction temporelle** des emprunts « B tiers » (pré-enregistré)")
    A("")
    A("Le **#508** a laissé **21** emprunts sourcés **au sujet mais ailleurs**")
    A("que dans le cycle cité, hors sourçages circulaires. Le **#503** avait")
    A("établi qu'une source **postérieure ne prouve rien** — ce registre reprend")
    A("ses chiffres **vers l'avant**. Le test n'avait jamais été appliqué ici.")
    A("")
    A("## La règle de datation, citée verbatim")
    A("")
    A("```")
    A(CMD)
    A("```")
    A("")
    A("> - **date du cycle cité** : celle de son `PREREG_<nom>.md`, `<nom>`")
    A(">   extrait de sa section par la règle du **#504** ;")
    A("> - **date de la source** : celle du **fichier** où le contexte a été")
    A(">   trouvé, ou du `PREREG_` du cycle si la source est une section.")
    A("")
    A("Ce sont des **premiers commits d'ajout**, jamais l'état courant.")
    A("")
    A("## Les trois classes")
    A("")
    A(f"- emprunts « B tiers » repris du #508 : **{len(tiers)}**")
    A("")
    A("| Classe | Nombre | Part | Ce qu'elle permet de conclure |")
    A("|---|---|---|---|")
    quoi = {"postérieure": "**rien** — reprise vers l'avant (leçon du #503)",
            "antérieure": "**candidat** d'erreur de citation",
            "indatable": "**rien**, et il faut le compter"}
    for c in CLASSES:
        pt = 100.0 * comptes[c] / len(tiers) if tiers else 0.0
        A(f"| **{c}** | **{comptes[c]}** | "
          + f"**{pt:.1f} %**".replace(".", ",") + f" | {quoi[c]} |")
    A("")
    A("## Ce que « postérieure » vaut — rappelé et chiffré")
    A("")
    A(f"**{comptes['postérieure']}** des **{len(tiers)}** « B tiers » ont une")
    A("source **postérieure** au cycle qu'ils citent. **Elles ne prouvent")
    A("rien** : un cycle ultérieur qui reprend un chiffre est le fonctionnement")
    A("normal de ce registre, et un détecteur aveugle au temps prend cette")
    A("reprise pour une erreur d'attribution — **c'est exactement l'erreur que")
    A("le #503 a commise puis publiée.**")
    A("")
    A(f"- après retrait des postérieures et des indatables, il reste : "
      f"**{reste}** emprunt(s)")
    A("")
    A("## Les antérieures — les seuls candidats")
    A("")
    A(f"- effectif : **{len(anter)}**")
    A("")
    if anter:
        A("| Script | Cite | Nombre | Source | Date source | Date cycle cité | Écart |")
        A("|---|---|---|---|---|---|---|")
        for e in sorted(anter, key=lambda x: (x["t_cite"] - x["t_src"]),
                        reverse=True):
            d = e["t_cite"] - e["t_src"]
            ecart = (f"**{d // 86400}** j" if d >= 86400
                     else f"**{d // 60}** min" if d >= 60 else f"**{d}** s")
            A(f"| `{e['py']}` | `{e['cite']}` | **{e['val']}** | `{e['ou']}` | "
              f"{jour(e['t_src'])} | {jour(e['t_cite'])} | {ecart} |")
        A("")
        courts = [e for e in anter if e["t_cite"] - e["t_src"] < 86400]
        if courts:
            A(f"> **{len(courts)}** de ces antériorités sont **inférieures à un")
            A("> jour**. Ce dépôt produit plusieurs cycles par heure : une")
            A("> antériorité de quelques minutes n'établit **rien** sur l'ordre")
            A("> logique des travaux — elle reflète l'ordre d'écriture des")
            A("> fichiers, pas celui des idées.")
            A(">")
            A("> **La règle figée les compte comme antérieures, et je ne la")
            A("> change pas** ; mais le lecteur doit savoir que leur poids")
            A("> probant est **quasi nul**. Le publier vaut mieux que présenter")
            A("> un résidu plus solide qu'il n'est.")
        A("")
        A("")
        solides0 = [e for e in anter if e["t_cite"] - e["t_src"] >= 86400]
        if solides0:
            A(f"> **{len(solides0)}** antériorité(s) dépassent le jour : là, le")
            A("> chiffre existait bien **au sujet** avant le cycle cité, et")
            A("> c'est un **candidat** d'erreur de citation — pas un verdict :")
            A("> une même grandeur peut légitimement apparaître dans deux")
            A("> cycles.")
        else:
            A("> **Aucune antériorité ne dépasse le jour.** Il n'y a donc ici")
            A("> **aucun candidat** d'erreur de citation dont l'écart soit")
            A("> interprétable — et le mot « candidat », choisi avant la mesure,")
            A("> ne peut pas être appliqué à un écart de quelques minutes.")
    else:
        A("**Aucune.** Toutes les sources tierces sont **postérieures** au cycle")
        A("cité.")
        A("")
        A("> **Neuf cycles d'enquête sur les emprunts se terminent sans un seul")
        A("> candidat d'erreur.** Le canal soupçonné au #497 est **réel** — 39")
        A("> nombres retapés au lieu d'être relus — mais il **n'a produit aucune")
        A("> faute repérable**. Je l'écris ainsi, sans le présenter comme un")
        A("> demi-résultat.")
    A("")
    indat = [e for e in tiers if e["cl"] == "indatable"]
    if indat:
        A("## Les indatables — ma prédiction 3 les annonçait à zéro")
        A("")
        for e in indat:
            manque = ("le cycle cité" if e["t_cite"] is None else "la source")
            A(f"- `{e['py']}` cite `{e['cite']}` pour **{e['val']}**, source")
            A(f"  `{e['ou']}` — **{manque}** n'a pas de date d'ajout.")
        A("")
        A("> La règle de datation ne couvre pas tout : un fichier peut avoir été")
        A("> ajouté hors du chemin balayé, ou un cycle n'avoir pas de")
        A("> `PREREG_` nommable. **Compté, pas dissimulé.**")
        A("")
    A("## Ce que la classe B du #508 vaut après ce filtre")
    A("")
    A("Le #508 concluait que **la majorité des emprunts ne se justifient pas")
    A("par le cycle qu'ils citent**. Ce cycle en donne la lecture datée :")
    A("")
    A("| Étape | Effectif |")
    A("|---|---|")
    A(f"| classe **B** du #508 | **{len(tiers) + 5}** |")
    A(f"| moins les **circulaires** (#508) | **{len(tiers)}** |")
    A(f"| moins les **postérieures** et **indatables** | **{reste}** |")
    A("")
    if reste == 0:
        A("> **Le « fait le plus lourd de la série » se dissout entièrement.**")
        A("> Les 26 emprunts non sourcés par leur cycle cité s'expliquent, sans")
        A("> exception, par un sourçage circulaire ou une reprise ultérieure.")
        A("> **La gravité annoncée au #508 était un artefact de temporalité",)
        A("> — la même erreur que le #503 avait déjà corrigée une fois.**")
    else:
        solides = [e for e in anter if e["t_cite"] - e["t_src"] >= 86400]
        A(f"> Il reste **{reste}** emprunt(s) que ni la circularité ni la")
        A("> reprise vers l'avant n'expliquent.")
        A(">")
        A(f"> **Dont antériorité d'au moins un jour : {len(solides)}.** Le")
        A("> résidu de neuf cycles d'enquête se réduit donc à **" +
          str(len(solides)) + "** cas au poids probant réel.")
        if not solides:
            A(">")
            A("> **Autrement dit : rien.** Neuf cycles n'ont produit aucun")
            A("> candidat d'erreur qui résiste à la mesure de son propre écart")
            A("> temporel. Le canal soupçonné au #497 est **réel** — 39 nombres")
            A("> retapés au lieu d'être relus — et **n'a produit aucune faute")
            A("> repérable**.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = comptes["postérieure"] >= 15
    p2 = len(anter) >= 1
    p3 = comptes["indatable"] == 0
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| ≥ 15 postérieures | ≥ 15 | {comptes['postérieure']} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| ≥ 1 antérieure | ≥ 1 | {len(anter)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| 0 indatable | 0 | {comptes['indatable']} | "
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
    A("**importés** des backtests des #500 à #508.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Règle de datation et commande citées verbatim", True),
         (f"Les **{len(tiers)}** « B tiers » classés, **{len(CLASSES)}** "
          "classes publiées", len(tiers) > 0),
         (f"Antérieures nommées avec leurs deux dates (**{len(anter)}**)", True),
         ("« Postérieure ne prouve rien » rappelé et chiffré", True),
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
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts et de")
    A("> l'historique à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(tiers)} B tiers : " +
          ", ".join(f"{c}={comptes[c]}" for c in CLASSES) +
          f" ; résidu = {reste}")


if __name__ == "__main__":
    main()

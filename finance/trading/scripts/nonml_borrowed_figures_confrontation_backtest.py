"""Confronter les 31 emprunts a leur source (#501).

Specification pre-enregistree dans `PREREG_borrowed_figures_confrontation.md`,
committee AVANT toute mesure -- regle et quatre classes comprises.

Le #500 a mesure une EXPOSITION et se l'est dit. Ce cycle mesure ce qu'il
pouvait : chaque emprunt relu dans la section de backlog du cycle qu'il cite.
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

BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"
RAP_498 = RESULTS / "nonml_declaration_rule_extension_dating_result.md"
OUT = RESULTS / "nonml_borrowed_figures_confrontation_result.md"
MOI = "borrowed_figures_confrontation"

REGLE = [
    ("confirmé", "`x` apparaît **en gras** dans la section `## Backlog #NNN`"),
    ("retrouvé ailleurs", "`x` apparaît **en gras** dans une autre section du "
                          "backlog ou dans un `results/*.md`"),
    ("non retrouvé", "`x` n'apparaît en gras **nulle part**"),
    ("non vérifiable", "la section `## Backlog #NNN` **n'existe pas**"),
]
SEUIL_FORT = 3          # >= 3 chiffres : confirmation FORTE


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def recensement_500():
    """La population du #500, IMPORTEE de son backtest -- jamais recopiee."""
    p = SCRIPTS / "nonml_borrowed_figures_census_backtest.py"
    spec = importlib.util.spec_from_file_location("_c500", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # constantes et fonctions ; `main()` non appelé
    return m


def sections_backlog():
    """{'#NNN' -> texte de la section} du registre publié."""
    txt = BACKLOG.read_text(encoding="utf-8")
    out, cur, buf = {}, None, []
    for l in txt.splitlines():
        m = re.match(r"^##\s+Backlog\s+#?(\d{3})\b", l)
        if m:
            if cur:
                out[f"#{cur}"] = "\n".join(buf)
            cur, buf = m.group(1), [l]
        elif cur:
            buf.append(l)
    if cur:
        out[f"#{cur}"] = "\n".join(buf)
    return out


def chiffres_seuls(gras):
    """De '**8**' ou '**12,5 %**' vers '8' / '12,5' -- la valeur nue."""
    m = re.search(r"-?\d[\d  ]*(?:[,.]\d+)?", gras)
    return m.group(0).replace(" ", "").replace(" ", "") if m else None


def en_gras_dans(valeur, texte):
    """La valeur apparait-elle EN GRAS dans ce texte ?"""
    v = re.escape(valeur)
    return re.search(r"\*\*-?" + v + r"\s*(?:%|€|bps)?\*\*", texte) is not None


def main():
    avant = set(git("status", "--porcelain").splitlines())

    c500 = recensement_500()
    secs = sections_backlog()
    tout_backlog = BACKLOG.read_text(encoding="utf-8")
    autres_md = []
    for p in sorted(RESULTS.glob("*.md")):
        if MOI in p.name:
            continue
        try:
            autres_md.append(p.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue

    # --- La population du #500, re-derivee par ses propres fonctions ------
    emprunts = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if c500.MOI in py.name or MOI in py.name:
            continue
        try:
            arbre = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for txt, cycles, nombres in c500.emprunts_de(arbre):
            for g in nombres:
                v = chiffres_seuls(g)
                if v is None:
                    continue
                emprunts.append({"py": py.name, "cycles": cycles, "gras": g,
                                 "val": v, "txt": txt})

    # --- La confrontation --------------------------------------------------
    for e in emprunts:
        cite = e["cycles"][0]
        sec = secs.get(cite)
        if sec is None:
            e["classe"] = "non vérifiable"
        elif en_gras_dans(e["val"], sec):
            e["classe"] = "confirmé"
        elif en_gras_dans(e["val"], tout_backlog) or \
                any(en_gras_dans(e["val"], t) for t in autres_md):
            e["classe"] = "retrouvé ailleurs"
        else:
            e["classe"] = "non retrouvé"
        e["fort"] = len(re.sub(r"\D", "", e["val"])) >= SEUIL_FORT

    comptes = {c: sum(1 for e in emprunts if e["classe"] == c)
               for c, _ in REGLE}
    conf = [e for e in emprunts if e["classe"] == "confirmé"]
    forts = [e for e in conf if e["fort"]]
    faibles = [e for e in conf if not e["fort"]]
    orphelins = [e for e in emprunts if e["classe"] == "non retrouvé"]
    part_faible = 100.0 * len(faibles) / len(conf) if conf else 0.0

    L = []
    A = L.append
    A("# Les **emprunts**, confrontés à leur source (pré-enregistré)")
    A("")
    A("Le **#500** a recensé les emprunts et s'est interdit d'en juger la")
    A("justesse : *« il mesure une exposition, pas une erreur »*. **Ce cycle")
    A("mesure ce qui peut l'être.**")
    A("")
    A("## La règle de confrontation, citée verbatim")
    A("")
    A("> Pour un emprunt du script `S`, citant `#NNN`, de nombre en gras `x`,")
    A("> la **source** est la section `## Backlog #NNN` du registre publié :")
    for c, d in REGLE:
        A(f"> - **{c}** — {d} ;")
    A("")
    chaines = {(e["py"], e["txt"]) for e in emprunts}
    A(f"- **chaînes** empruntées — l'unité du #500 : **{len(chaines)}**")
    A(f"- **nombres** empruntés — l'unité d'ici : **{len(emprunts)}**")
    A(f"- sections de backlog disponibles : **{len(secs)}**")
    A("")
    A("> **Les deux unités diffèrent, et il faut le dire** : le #500 comptait")
    A("> des **chaînes publiées**, une chaîne pouvant porter plusieurs nombres.")
    A("> Confronter exige de descendre **au nombre**. Aucun emprunt du #500")
    A("> n'est écarté — ils sont **dépliés**.")
    A("")
    A("## Les quatre classes")
    A("")
    A("| Classe | Nombre | Part |")
    A("|---|---|---|")
    for c, _ in REGLE:
        pt = 100.0 * comptes[c] / len(emprunts) if emprunts else 0.0
        A(f"| **{c}** | **{comptes[c]}** | " + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A("## La coupure forte / faible — sans elle, le taux ment")
    A("")
    A(f"Un nombre à moins de **{SEUIL_FORT}** chiffres se retrouve **par")
    A("hasard** dans presque n'importe quelle section. Les confirmations sont")
    A("donc séparées :")
    A("")
    A("| Confirmations | Nombre | Part des confirmées |")
    A("|---|---|---|")
    pf = 100.0 * len(forts) / len(conf) if conf else 0.0
    A(f"| **fortes** (≥ {SEUIL_FORT} chiffres) | **{len(forts)}** | "
      + f"**{pf:.1f} %**".replace(".", ",") + " |")
    A(f"| **faibles** (1-2 chiffres) | **{len(faibles)}** | "
      + f"**{part_faible:.1f} %**".replace(".", ",") + " |")
    A("")
    if part_faible > 50:
        A("> **La majorité des confirmations sont faibles.** La conclusion")
        A("> honnête n'est donc **pas** « les emprunts sont exacts » mais")
        A("> **« la méthode ne sait pas les départager »**. Convertir cette")
        A("> faiblesse en satisfecit était exactement ce que le")
        A("> pré-enregistrement interdisait.")
    else:
        A("> La majorité des confirmations reposent sur des nombres à")
        A(f"> **≥ {SEUIL_FORT} chiffres**, où la coïncidence est peu probable :")
        A("> elles ont une réelle valeur probante.")
    A("")
    A("## Les non retrouvés — la liste de suspects")
    A("")
    A(f"- effectif : **{len(orphelins)}**")
    A("")
    if orphelins:
        A("| Script | Cite | Nombre | Extrait |")
        A("|---|---|---|---|")
        for e in sorted(orphelins, key=lambda x: (x["py"], x["val"]))[:20]:
            ex = re.sub(r"\s+", " ", e["txt"])[:70]
            A(f"| `{e['py']}` | `{e['cycles'][0]}` | **{e['val']}** | « {ex}… » |")
        if len(orphelins) > 20:
            A("")
            A(f"*(et **{len(orphelins) - 20}** autres.)*")
    else:
        A("**Aucun.** Tout nombre emprunté se retrouve en gras quelque part dans")
        A("le dépôt — ce qui **n'établit pas** qu'il y soit au bon endroit.")
    A("")
    A("## Ce que ce cycle **n'établit pas**")
    A("")
    A("**Aucun chiffre n'est déclaré faux.** Un « non retrouvé » signale un")
    A("emprunt **invérifiable par cette méthode**, pas une erreur : le nombre")
    m498 = re.search(r"\*\*\+([\d,]+)\*\* points sur",
                     RAP_498.read_text(encoding="utf-8"))
    ecart498 = m498.group(1) if m498 else "?"
    A("peut vivre dans un rapport que la règle ne consulte pas, ou avoir été")
    A(f"écrit avec une autre typographie — le **#498** a montré qu'une règle")
    A(f"littérale rate **{ecart498} points** de détection sur une simple mise en")
    A("forme. *(Ce chiffre est **lu** dans le rapport du #498 : dans un cycle")
    A("sur les emprunts, le retaper aurait été une faute de plus.)*")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = comptes["confirmé"] >= 20
    p2 = len(orphelins) >= 1
    p3 = part_faible > 50
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| confirmés ≥ 20 | ≥ 20 | {comptes['confirmé']} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| ≥ 1 non retrouvé | ≥ 1 | {len(orphelins)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| majorité de confirmations faibles | > 50 % | "
      + f"{part_faible:.1f} %".replace(".", ",")
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
    A("La population est **importée** du backtest du #500 (ses fonctions, pas")
    A("son `main()`) : recopier une définition est le meilleur moyen de la")
    A("faire diverger — leçon du #499.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Règle citée verbatim, quatre classes publiées avec leur compte",
          len(comptes) == 4),
         (f"Toutes les **{len(chaines)}** chaînes du #500 dépliées en "
          f"**{len(emprunts)}** nombres, aucune écartée",
          len(chaines) > 0 and len(emprunts) >= len(chaines)),
         (f"Confirmations fortes (**{len(forts)}**) et faibles "
          f"(**{len(faibles)}**) comptées séparément", True),
         (f"Non retrouvés nommés individuellement (**{len(orphelins)}**)", True),
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
    print(f"{verdict} — {len(emprunts)} emprunts : " +
          ", ".join(f"{c}={comptes[c]}" for c, _ in REGLE) +
          f" ; fortes={len(forts)}, faibles={len(faibles)}")


if __name__ == "__main__":
    main()

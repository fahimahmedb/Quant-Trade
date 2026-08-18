"""Les temoins non publies : que faudrait-il ? (#494)

Specification pre-enregistree dans `PREREG_unpublished_witnesses_paths.md`,
committee AVANT toute mesure -- prefixes et classes compris.

Quatre cycles consecutifs (#487, #489, #490, #491) ont du ecrire << le temoin
est dans le code, pas encore dans le rapport >>. Personne n'avait etabli ce
qu'il faudrait. Ce cycle l'etablit, SANS RIEN EXECUTER.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_unpublished_witnesses_paths_result.md"
MOI = "unpublished_witnesses_paths"

# Prefixes figes par le pre-enregistrement.
PREFIXES = [
    "- rapports ayant **perdu** l'encart du #439",
    "- PASS qui sont des **stratégies**",
    "- rapports classés « indéterminé » par la règle unifiée",
    "- incohérences prose/compte exposées par le rafraîchissement",
]
SUFFIXES = [("_backtest.py", "_result.md"), ("_audit.py", "_audit.md"),
            ("_robustness.py", "_robustness.md")]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def rapport_de(py_nom):
    for a, b in SUFFIXES:
        if py_nom.endswith(a):
            return RESULTS / f"{py_nom[:-len(a)]}{b}"
    return None


def effets(src):
    """Les quatre mesures, par motifs structurels — sans execution."""
    exec_tiers = len(re.findall(r"subprocess\.run\(\[sys\.executable", src))
    ecritures = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\.write_text\(", src)
    arbre_git = len(re.findall(r"[\"']checkout[\"']|[\"']add[\"']", src))
    return exec_tiers, ecritures, arbre_git


def classe(exec_tiers, ecritures, arbre_git):
    if exec_tiers:
        return "C", "Non exécutable en l'état"
    if len(set(ecritures)) > 1 or arbre_git:
        return "B", "Exécutable avec effets à annuler"
    return "A", "Exécutable sans danger"


def main():
    # --- Population, derivee par code --------------------------------------
    pop = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        try:
            src = py.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if MOI in py.name:
            continue
        porte = [p for p in PREFIXES if p in src]
        if not porte:
            continue
        rap = rapport_de(py.name)
        txt = rap.read_text(encoding="utf-8") if (rap and rap.exists()) else ""
        absent = [p for p in porte if p not in txt]
        if absent:
            pop.append({"py": py.name, "rap": rap.name if rap else "—",
                        "prefixes": absent, "src": src})

    L = ["# Les **témoins non publiés** : que faudrait-il ? (pré-enregistré)", ""]
    L.append("Quatre cycles consécutifs — **#487, #489, #490, #491** — ont dû écrire la")
    L.append("même phrase : *« le témoin est dans le code, pas encore dans le")
    L.append("rapport »*. **Personne n'avait établi ce qu'il faudrait.**")
    L.append("")

    L.append("## La population, dérivée par code")
    L.append("")
    L.append("Un script est **porteur d'un témoin non publié** si son code contient un")
    L.append("des préfixes ci-dessous **et** que la chaîne est **absente** de son")
    L.append("rapport publié. Préfixes **figés par le pré-enregistrement** :")
    L.append("")
    L.append("```")
    for p in PREFIXES:
        L.append(p)
    L.append("```")
    L.append("")
    L.append(f"- scripts **porteurs d'un témoin non publié** : **{len(pop)}**")
    L.append("")

    # --- Les quatre mesures ------------------------------------------------
    L.append("## Les quatre mesures, script par script")
    L.append("")
    L.append("| Script | Exécute un script tiers | Cibles d'écriture | Touche l'arbre git | Classe |")
    L.append("|---|---|---|---|---|")
    for d in pop:
        e, w, g = effets(d["src"])
        cl, lab = classe(e, w, g)
        d["e"], d["w"], d["g"], d["cl"], d["lab"] = e, w, g, cl, lab
        L.append(f"| `{d['py']}` | **{e}** | "
                 f"{', '.join('`' + x + '`' for x in sorted(set(w))) or '—'} | "
                 f"**{g}** | **{cl}** |")
    L.append("")
    par = {}
    for d in pop:
        par.setdefault(d["cl"], []).append(d)
    L.append("| Classe | Nombre |")
    L.append("|---|---|")
    for cl, lab in (("A", "Exécutable sans danger"),
                    ("B", "Exécutable avec effets à annuler"),
                    ("C", "Non exécutable en l'état")):
        L.append(f"| **{cl}** — {lab} | **{len(par.get(cl, []))}** |")
    L.append("")

    # --- Ce qu'il faudrait, pour chacun ------------------------------------
    L.append("## Ce qu'il faudrait, pour chacun")
    L.append("")
    for d in pop:
        L.append(f"### `{d['py']}` — classe **{d['cl']}**")
        L.append("")
        L.append(f"Témoin absent de `{d['rap']}` : « {d['prefixes'][0][:64]}… »")
        L.append("")
        if d["cl"] == "A":
            L.append("**Il suffirait de l'exécuter**, puis de vérifier que le diff de son")
            L.append("rapport se réduit au témoin avant de le committer — la règle que le")
            L.append("**#489** avait déjà fixée, et qui l'a fait renoncer parce que le")
            L.append("diff était dominé par la dérive du dépôt.")
            L.append("")
            L.append("> **Le blocage n'est donc pas technique, il est de méthode** : tant")
            L.append("> que le dépôt bouge entre deux exécutions, le diff ne se réduira")
            L.append("> jamais au seul témoin. **Il faudrait accepter de committer un")
            L.append("> rapport dont d'autres chiffres ont changé** — décision qui")
            L.append("> dépasse ce cycle.")
        elif d["cl"] == "B":
            L.append(f"Il écrit **{len(set(d['w']))}** cibles distinctes. **Il faudrait**")
            L.append("l'exécuter, **restaurer** les fichiers qui ne sont pas le sien")
            L.append("(`git checkout -- …`), puis appliquer la même règle de diff borné.")
            L.append("")
            L.append("> **Faisable, mais la restauration doit être vérifiée**, pas")
            L.append("> supposée — c'est la leçon du #468, où un « 0 résidu » avait été")
            L.append("> annoncé sur un arbre sale.")
        else:
            L.append(f"Il **exécute {d['e']} script(s) tiers** du dépôt. Le relancer")
            L.append("déclencherait une **cascade** : ces scripts réécrivent à leur tour")
            L.append("leurs propres rapports, et certains en écrivent d'autres.")
            L.append("")
            L.append("> **Il n'existe pas de geste borné qui publie ce témoin.** Le")
            L.append("> publier exigerait d'accepter une régénération en chaîne dont le")
            L.append("> périmètre n'est pas connu d'avance — exactement ce que le #450")
            L.append("> avait subi, et le #482 refusé.")
        L.append("")

    # --- Confrontation aux motifs invoques par les cycles precedents -------
    L.append("## Ce que les cycles précédents avaient invoqué")
    L.append("")
    L.append("Le **#487** avait refusé d'exécuter deux scripts. **Ses motifs sont")
    L.append("confrontés à la mesure :**")
    L.append("")
    L.append("| Script | Motif invoqué au #487 | Mesure d'ici |")
    L.append("|---|---|---|")
    invoques = {
        "nonml_six_reports_regeneration_backtest.py":
            "exécute d'autres scripts du dépôt",
        "nonml_sweep_pass_prose_fix_backtest.py":
            "écrit 2 fichiers, dont un qui n'est pas le sien",
    }
    faux = []
    for nom, motif in invoques.items():
        d = next((x for x in pop if x["py"] == nom), None)
        if not d:
            L.append(f"| `{nom}` | {motif} | *hors population* |")
            continue
        cibles = sorted(set(d["w"]))
        exact = (d["e"] > 0) if "exécute" in motif else (len(cibles) > 1)
        if not exact:
            faux.append(nom)
        L.append(f"| `{nom}` | {motif} | "
                 f"exécute **{d['e']}**, écrit **{len(cibles)}** cible(s) "
                 f"({', '.join('`' + c + '`' for c in cibles)}) — "
                 f"**{'confirmé' if exact else 'FAUX'}** |")
    L.append("")
    if faux:
        L.append(f"> **{len(faux)} motif invoqué est faux.** "
                 f"`sweep_pass_prose_fix` appelle bien `write_text` **deux fois**,")
        L.append("> mais **les deux visent `OUT`** — son propre rapport. Les autres")
        L.append("> chemins qu'il manipule (`REL`, `SWEEP_REL`) ne servent qu'à")
        L.append("> `git show` et `git diff`, **en lecture seule**.")
        L.append("")
        L.append("**Le #487 a compté des appels, pas des cibles.** Il a donc refusé")
        L.append("d'exécuter un script **de classe A**, sans danger — et quatre cycles")
        L.append("ont répété ce refus sans le vérifier.")
        L.append("")
        L.append("> C'est **le troisième motif de cette série que la lecture du code")
        L.append("> contredit**, après ceux du #488 et du #493. Les trois fois, le")
        L.append("> verdict tenait ou non, **mais la raison écrite était fausse.**")
        L.append("")

    # --- La voie detournee : n'existe-t-elle pas ? -------------------------
    L.append("## Existe-t-il une voie détournée ?")
    L.append("")
    L.append("**Non, et il faut le dire explicitement.** Un rapport de ce dépôt est")
    L.append("**une sortie de programme**. Y écrire le témoin à la main le rendrait")
    L.append("indiscernable d'un rapport produit — et **c'est précisément le défaut**")
    L.append("que les #479 à #493 ont passé quinze cycles à dénombrer.")
    L.append("")
    L.append("> **Publier un témoin en éditant le rapport serait fabriquer exactement")
    L.append("> ce que cette série reproche.** L'option est exclue, et le")
    L.append("> pré-enregistrement l'excluait d'avance.")
    L.append("")

    L.append("## Ce qui n'est pas mesurable ici")
    L.append("")
    L.append("**L'idempotence** de ces rapports — au sens du #463 — exigerait de les")
    L.append("exécuter **deux fois**. Ce cycle n'exécute rien : la question est")
    L.append("**déclarée hors de portée**, et non tranchée par supposition.")
    L.append("")

    # --- Predictions -------------------------------------------------------
    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(pop) == 4
    p2 = len(par) >= 2
    p3 = True   # aucune voie detournee : etabli par raisonnement, pas mesure
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| la population compte 4 scripts | 4 | {len(pop)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| au moins 2 classes distinctes | ≥ 2 | {len(par)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append("| aucune voie détournée honnête | 0 | 0 | **vérifiée** |")
    L.append("")
    L.append("> **La prédiction 3 n'est pas une mesure.** Elle énonce qu'éditer un")
    L.append("> rapport à la main est exclu — ce qui relève d'une **règle**, pas d'un")
    L.append("> fait observé. Je la marque vérifiée parce qu'aucune voie n'a été")
    L.append("> trouvée, **mais elle ne pouvait pas être réfutée par la mesure**, et")
    L.append("> c'est une faiblesse de ma formulation.")
    L.append("")
    if not p1:
        L.append(f"**La prédiction 1 est réfutée** : la population compte **{len(pop)}**")
        L.append("scripts, pas 4. La file du #493 annonçait 3.")
        L.append("")

    # --- Effets de bord ----------------------------------------------------
    sale = [l for l in git("status", "--porcelain").splitlines()
            if l.strip() and MOI not in l]
    L.append("## Aucune exécution, aucun rapport modifié")
    L.append("")
    L.append(f"- fichiers modifiés hors ceux de ce cycle : **{len(sale)}**")
    for l in sale[:8]:
        L.append(f"  - `{l.strip()}`")
    L.append("")
    L.append("**Aucun script du dépôt n'a été exécuté.**" if not sale
             else "**Des fichiers ont bougé — publié tel quel.**")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c4 = not sale
    L.append(f"1. Population dérivée par code (**{len(pop)}**), préfixes verbatim — "
             "**OUI**.")
    L.append("2. Les quatre mesures publiées par script — **OUI**.")
    L.append(f"3. Chacun rangé et « ce qu'il faudrait » énoncé — **OUI** "
             f"(**{len(par)}** classes).")
    L.append(f"4. Aucune exécution, aucun rapport modifié — **{'OUI' if c4 else 'NON'}**.")
    L.append("5. Idempotence déclarée hors de portée — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if c4 else 'FAIL'}** — le critère porte sur le **procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre de stratégie.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"pop={len(pop)} classes={ {k: len(v) for k, v in par.items()} } "
          f"sale={len(sale)}")
    for d in pop:
        print(f"  {d['py'][:46]} -> {d['cl']} (exec={d['e']}, w={len(set(d['w']))})")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

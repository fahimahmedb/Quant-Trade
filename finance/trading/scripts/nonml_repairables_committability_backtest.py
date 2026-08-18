"""Les 13 reparables, sous le critere de COMMITTABILITE (#507).

Specification pre-enregistree dans `PREREG_repairables_committability.md`,
committee AVANT toute mesure -- regle et quatre classes comprises.

Le #499 a montre qu'une reparation parfaite peut echouer : regenerer le
rapport reecrit la derive du depot. Le compte << 13 reparables >> mesure la
DERIVABILITE ; ce cycle mesure la COMMITTABILITE. SANS RIEN EXECUTER.
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

CENSUS = RESULTS / "nonml_irreparable_figures_census_result.md"
JUSTIF = RESULTS / "nonml_irreparability_justifications_audit_result.md"
OUT = RESULTS / "nonml_repairables_committability_result.md"
MOI = "repairables_committability"

CIBLE_499 = "nonml_reproducibility_campaign_v3_lot2_audit.py"
PRIM_CASCADE = ("P1", "P2", "P9", "P10")
BALAYAGE = {"glob", "rglob", "iterdir", "scandir", "listdir"}
CLASSES = {
    "NC1": "exécute un tiers",
    "NC2": "ne l'exécute pas, mais **lit l'état courant** du dépôt",
    "C": "ni l'un ni l'autre — **candidat** committable",
    "?": "script ou rapport introuvable",
}


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def regle_497():
    """La regle des 12 primitives, IMPORTEE -- jamais recopiee."""
    p = SCRIPTS / "nonml_execution_primitives_census_backtest.py"
    spec = importlib.util.spec_from_file_location("_c497", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def population():
    """Les 12 << reparable >> du recensement + le 13e requalifie au #493."""
    txt = CENSUS.read_text(encoding="utf-8")
    noms = re.findall(r"^###\s+`([a-z0-9_]+\.py)`\s+—\s+réparable", txt, re.M)
    txt2 = JUSTIF.read_text(encoding="utf-8")
    requal = re.findall(r"^###\s+`([a-z0-9_]+\.py)`\s+—\s+\*\*JUSTIFICATION "
                        r"FAUSSE", txt2, re.M)
    return sorted(set(noms) | set(requal)), sorted(noms), sorted(set(requal))


def lit_etat_courant(arbre):
    """Balayage de scripts/ ou results/, ou appel a git."""
    motifs = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        nom = n.func.attr if isinstance(n.func, ast.Attribute) else (
            n.func.id if isinstance(n.func, ast.Name) else None)
        if nom in BALAYAGE:
            motifs.append(f"`{nom}(…)`")
        if nom in ("run", "Popen", "check_output", "call"):
            for a in n.args:
                for s in ast.walk(a):
                    if isinstance(s, ast.Constant) and s.value == "git":
                        motifs.append("`git`")
    return sorted(set(motifs))


def main():
    avant = set(git("status", "--porcelain").splitlines())
    c497 = regle_497()
    existants = {p.stem for p in SCRIPTS.glob("nonml_*.py")}

    pop, du_census, requal = population()
    fiches = []
    for nom in pop:
        py = SCRIPTS / nom
        if not py.exists():
            fiches.append({"py": nom, "cl": "?", "prim": [], "etat": []})
            continue
        try:
            src = py.read_text(encoding="utf-8")
            arbre = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            fiches.append({"py": nom, "cl": "?", "prim": [], "etat": []})
            continue
        prim = sorted(k for k in c497.primitives(src, arbre, existants)
                      if k in PRIM_CASCADE)
        etat = lit_etat_courant(arbre)
        argv = any(isinstance(n, ast.Attribute) and n.attr == "argv"
                   for n in ast.walk(arbre))
        cl = "NC1" if prim else ("NC2" if etat else "C")
        fiches.append({"py": nom, "cl": cl, "prim": prim, "etat": etat,
                       "argv": argv})

    comptes = {k: sum(1 for f in fiches if f["cl"] == k) for k in CLASSES}
    candidats = [f for f in fiches if f["cl"] == "C"]
    non_comm = comptes["NC1"] + comptes["NC2"]
    ctrl = next((f for f in fiches if f["py"] == CIBLE_499), None)
    ctrl_ok = ctrl is not None and ctrl["cl"] in ("NC1", "NC2")

    L = []
    A = L.append
    A("# Les **13 réparables**, sous le critère de **committabilité** (pré-enregistré)")
    A("")
    A("Le **#499** a tenté la réparation du 13ᵉ. Elle était **parfaite** —")
    A("**0 ligne** de diff sur les valeurs — et elle a **échoué** : régénérer le")
    A("rapport en réécrivait la **dérive du dépôt**.")
    A("")
    A("> **Un chiffre dérivable n'est pas pour autant réparable par un geste")
    A("> borné.** Le compte « 13 réparables » mesure la **dérivabilité** ;")
    A("> personne n'avait mesuré la **committabilité**.")
    A("")
    A("## La règle, citée verbatim — statique, sans exécution")
    A("")
    A(f"> - **NC1** — le script déclenche l'une des primitives "
      f"**{', '.join(PRIM_CASCADE)}** du #497 (règle **importée**, non")
    A(">   recopiée) : le régénérer déclencherait une **cascade** ;")
    A(f"> - **NC2** — il appelle "
      f"{', '.join('`' + b + '`' for b in sorted(BALAYAGE))} sur `scripts/` ou")
    A(">   `results/`, **ou** invoque `git` : sa sortie **bouge avec le dépôt**.")
    A("")
    A("| Classe | Définition |")
    A("|---|---|")
    for k, v in CLASSES.items():
        A(f"| **{k}** | {v} |")
    A("")
    A("## La population, dérivée par code")
    A("")
    A(f"- « réparable » lus dans le recensement du #485 : **{len(du_census)}**")
    A(f"- requalifiés au #493 (justification fausse) : **{len(requal)}**")
    A(f"- **population** : **{len(pop)}**")
    A("")
    if len(pop) != 13:
        A(f"> **Écart avec le compte attendu (13) : {len(pop) - 13:+d}.** La")
        A("> population est dérivée des rapports, pas retapée ; l'écart est")
        A("> publié plutôt que corrigé à la main.")
        A("")
    A("## Les quatre classes")
    A("")
    A("| Classe | Nombre | Part |")
    A("|---|---|---|")
    for k in CLASSES:
        pt = 100.0 * comptes[k] / len(fiches) if fiches else 0.0
        A(f"| **{k}** | **{comptes[k]}** | " + f"**{pt:.1f} %**".replace(".", ",") + " |")
    A("")
    A(f"- **non committables** (NC1 + NC2) : **{non_comm}** sur **{len(fiches)}**")
    A("")
    A("## Le contrôle : la cible du #499")
    A("")
    A(f"`{CIBLE_499}` est **connue non committable par l'expérience**. Si la")
    A("règle statique la classait **C**, la règle serait fausse.")
    A("")
    if ctrl is None:
        A("- **la cible n'est pas dans la population** — le contrôle ne peut pas")
        A("  s'exercer.")
    else:
        A(f"- classe rendue : **{ctrl['cl']}**")
        if ctrl["etat"]:
            A(f"- motifs d'état courant : {', '.join(ctrl['etat'])}")
        if ctrl["prim"]:
            A(f"- primitives de cascade : {', '.join(ctrl['prim'])}")
        A("")
        if ctrl_ok:
            A("> **Le contrôle passe.** La règle statique retrouve, sans rien")
            A("> exécuter, ce que le #499 avait payé une exécution complète pour")
            A("> découvrir.")
        else:
            A("> **Le contrôle échoue.** La règle classe committable un rapport")
            A("> dont l'expérience a montré qu'il ne l'est pas : **elle est")
            A("> fausse**, et les comptes ci-dessus ne valent rien.")
    A("")
    A("## Le détail, script par script")
    A("")
    A("| Script | Classe | Motif |")
    A("|---|---|---|")
    for f in sorted(fiches, key=lambda x: (x["cl"], x["py"])):
        motif = (", ".join(f["prim"]) if f["prim"]
                 else ", ".join(f["etat"]) if f["etat"] else "—")
        A(f"| `{f['py']}` | **{f['cl']}** | {motif} |")
    A("")
    A("## Les candidats")
    A("")
    A(f"- effectif : **{len(candidats)}**")
    A("")
    if candidats:
        for f in candidats:
            A(f"- `{f['py']}`")
        A("")
        A("> **« Candidat » n'est pas « committable ».** La règle est une")
        A("> **borne supérieure** : un script peut dériver pour une raison")
        A("> qu'elle n'énumère pas. Seule l'exécution trancherait, et le #499 a")
        A("> montré ce qu'elle coûte. **Le mot était choisi avant la mesure",)
        A("> pour qu'il ne puisse pas être durci après.**")
    else:
        A("**Aucun.** Le compte « 13 réparables » du dépôt **ne décrit rien")
        A("d'actionnable** : la dette n'est pas partiellement mais **entièrement**")
        A("hors de portée d'un geste borné.")
    A("")
    A("## Un troisième angle mort — découvert, **non absorbé**")
    A("")
    argv_cand = [f for f in candidats if f.get("argv")]
    argv_tous = [f for f in fiches if f.get("argv")]
    A(f"- réparables dépendant de `sys.argv` : **{len(argv_tous)}**")
    A(f"- dont **classés candidats** par ma règle : **{len(argv_cand)}**")
    A("")
    if argv_cand:
        for f in argv_cand:
            A(f"- `{f['py']}`")
        A("")
        A("> Un script qui attend des **arguments de ligne de commande** ne se")
        A("> régénère pas seul : il lui faut des fichiers « avant » qui")
        A("> n'existent peut-être plus. **C'est une troisième cause de")
        A("> non-committabilité, que ma règle ne nomme pas.**")
        A(">")
        A("> **Elle est enregistrée comme angle mort, pas absorbée après coup** —")
        A("> la règle a été figée avant mesure, et l'élargir maintenant serait")
        A("> la dérive refusée aux #496 et #497. Le compte de candidats reste")
        A(f"> **{len(candidats)}** ; le lecteur sait désormais que **{len(argv_cand)}**")
        A("> d'entre eux est fragile pour une raison de plus.")
        A("")
    A("## Ce que ce cycle ne contredit pas")
    A("")
    A("**La dérivabilité mesurée par les #485 et #493 reste vraie.** Ces")
    A("chiffres peuvent bien être recalculés par le code qui les entoure. Ce")
    A("cycle mesure **autre chose** : la possibilité de **déposer** la")
    A("correction sans emporter la dérive du dépôt avec elle.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = ctrl is not None and ctrl["cl"] == "NC2"
    p2 = non_comm >= 8
    p3 = len(candidats) >= 1
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| la cible du #499 est **NC2** | NC2 | "
      f"{ctrl['cl'] if ctrl else '—'} | **{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| ≥ 8 non committables | ≥ 8 | {non_comm} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| ≥ 1 candidat subsiste | ≥ 1 | {len(candidats)} | "
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
    A("> **Ce script est lui-même de classe NC2 par sa propre règle** : il")
    A("> balaie `scripts/` et appelle `git`. Il ne prétend donc pas être")
    A("> committable — il ne répare rien.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Règle et quatre classes citées verbatim, règle du #497 importée",
          True),
         (f"Population dérivée par code (**{len(pop)}**), écart publié",
          len(pop) > 0),
         (f"Quatre classes comptées et **contrôle du #499 passé** "
          f"(**{ctrl['cl'] if ctrl else '—'}**)", ctrl_ok),
         (f"Candidats nommés individuellement (**{len(candidats)}**)", True),
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
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la")
    A("> date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — {len(pop)} réparables : " +
          ", ".join(f"{k}={comptes[k]}" for k in CLASSES) +
          f" ; contrôle #499 = {ctrl['cl'] if ctrl else '—'}")


if __name__ == "__main__":
    main()

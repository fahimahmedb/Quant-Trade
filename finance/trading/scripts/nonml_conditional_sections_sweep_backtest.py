"""Les sections qui ne paraissent que sous condition (#478).

Specification pre-enregistree dans `PREREG_conditional_sections_sweep.md`,
committee AVANT toute mesure.

Le #475 a montre qu'une section entiere -- titre compris -- pouvait etre sous
garde (`if perdus:`), et que trois cycles y avaient use leur budget. Ce cycle
mesure si le motif est courant. PREVALENCE, jamais un compte de fautes.

Lecture du disque : aucun script execute, aucun effet de bord.
"""
import ast
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_conditional_sections_sweep_result.md"
MOI = "conditional_sections_sweep"
TAILLE = 5
SUFFIXES = [("_result.md", "_backtest.py"), ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]
ECRIVENT = ("append", "write", "print", "write_text")
GARDES = (ast.If, ast.For, ast.While, ast.Try)


# --- VERDICTS DE L'EXAMEN INDIVIDUEL ------------------------------------
# ECRITS A LA MAIN apres lecture de chaque garde des 5 scripts de
# l'echantillon. Aucune regle ne les produit : c'est precisement ce qu'une
# regle ne sait pas faire. "peut_disparaitre" = la garde peut etre fausse,
# donc la section entiere s'efface (forme exacte du #475).
VERDICTS = {
    "nonml_prereg_convention_coverage_backtest.py": (
        "peut_disparaitre",
        "Gardes : `if not sans_rapport:`, `if aucun_fichier:`, `if autre_nom:`, "
        "`if plusieurs:`. **Toutes peuvent être fausses** — au #474 la "
        "population `aucun_fichier` valait 10, elle pourrait valoir 0 demain et "
        "la sous-section s'effacerait. **Atténuation, et elle est réelle** : les "
        "effectifs (`10`, `104`, `9`…) sont publiés **sans garde** dans le "
        "tableau qui précède. Un lecteur voit donc *pourquoi* une section "
        "manque."),
    "nonml_repo_magnitudes_recount_backtest.py": (
        "peut_disparaitre",
        "Gardes : `if discordants:`, `if concordants:`, et surtout "
        "`if 456 in par_num and 457 in par_num and (ap - av) == 29:` — **une "
        "garde sur des valeurs de données**, pas sur une liste. Si un jour "
        "l'écart ne vaut plus exactement 29, la section « le seul recomptage qui "
        "mord » **disparaît sans que rien ne la remplace**. C'est la forme la "
        "plus proche du #475 de tout l'échantillon."),
    "nonml_reproducibility_campaign_v2_backtest.py": (
        "peut_disparaitre",
        "Gardes : `if divergent:`, `if inconclusive:`, `if identical:` — les "
        "trois issues d'un même partitionnement. **Au moins une est vide dans "
        "presque toute exécution**, donc au moins une section manque toujours. "
        "Atténuation : les trois effectifs sont publiés **sans garde** juste "
        "au-dessus."),
    "nonml_reproducibility_sample_backtest.py": (
        "peut_disparaitre",
        "Même motif à trois branches. Vérifié ligne à ligne : "
        "`| rapports **divergents** | **{len(divergent)}** |` est écrit **hors "
        "de toute garde** avant les sections. **La disparition est donc "
        "signalée**, ce qui est exactement ce qui manquait au #475."),
    "nonml_reproducibility_sample_lot2_backtest.py": (
        "peut_disparaitre",
        "Même motif que le précédent, même atténuation. Sa présence ici tient à "
        "l'ex æquo alphabétique, pas à une charge supérieure : **quatre des cinq "
        "scripts de l'échantillon portent trois titres conditionnels**, et "
        "l'ordre alphabétique a tranché."),
}


def producteur(nom_md):
    for a, b in SUFFIXES:
        if nom_md.endswith(a):
            return SCRIPTS / f"{nom_md[:-len(a)]}{b}"
    return None


def titres(chemin):
    """Titres de section ecrits dans le rapport, avec leurs gardes englobantes.

    Retourne [(ligne, titre, [gardes])] ou None si le fichier est illisible.
    """
    try:
        arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return None
    out = []

    def visite(noeud, gardes):
        for enfant in ast.iter_child_nodes(noeud):
            g = gardes
            if isinstance(enfant, GARDES):
                mot = {ast.If: "if", ast.For: "for",
                       ast.While: "while", ast.Try: "try"}[type(enfant)]
                g = gardes + [(enfant.lineno, mot)]
            if isinstance(enfant, ast.Call):
                f = enfant.func
                nom = f.attr if isinstance(f, ast.Attribute) else \
                    (f.id if isinstance(f, ast.Name) else "")
                if nom in ECRIVENT:
                    for a in enfant.args:
                        if isinstance(a, ast.Constant) \
                                and isinstance(a.value, str) \
                                and a.value.startswith(("## ", "### ")):
                            out.append((a.lineno, a.value.strip(), g))
            visite(enfant, g)

    visite(arbre, [])
    return out


def main():
    rapports = sorted(p.name for p in RESULTS.glob("nonml_*.md")
                      if not p.name.endswith("_anti_cheat.md") and MOI not in p.name)
    population, hors = [], []
    for nom in rapports:
        py = producteur(nom)
        (population if (py and py.exists()) else hors).append(nom)

    vus, illisibles, mesures = set(), [], []
    for nom in rapports:
        py = producteur(nom)
        if not (py and py.exists()) or py.name in vus:
            continue
        vus.add(py.name)
        t = titres(py)
        if t is None:
            illisibles.append(py.name)
            continue
        cond = [x for x in t if x[2]]
        mesures.append({"script": py.name, "titres": t, "cond": cond})

    affectes = [m for m in mesures if m["cond"]]
    charges = sorted(len(m["cond"]) for m in affectes)
    med = statistics.median(charges) if charges else 0
    echantillon = sorted(affectes,
                         key=lambda m: (-len(m["cond"]), m["script"]))[:TAILLE]

    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731

    L = ["# Les **sections qui ne paraissent que sous condition** (pré-enregistré)",
         ""]
    L.append("Le **#475** a montré qu'une section entière — **titre compris** — pouvait")
    L.append("être sous garde (`if perdus:`), et que **trois cycles** (#469, #472,")
    L.append("#475) y avaient usé leur budget. Ce cycle mesure si le motif est courant.")
    L.append("")

    L.append("## Ce que ce chiffre est, et ce qu'il n'est pas")
    L.append("")
    L.append("**Il mesure une prévalence, pas une culpabilité.** Une section")
    L.append("conditionnelle est souvent le bon choix : « Les défauts trouvés » suivie")
    L.append("d'un `if not fautifs: \"Aucun.\"` **paraît toujours** — c'est son *contenu*")
    L.append("qui varie, pas son existence.")
    L.append("")
    L.append("Le cas du #475 est plus étroit : **le titre lui-même est sous garde**, la")
    L.append("section **disparaît entièrement**, et deux exécutions produisent des")
    L.append("rapports dont on ne peut plus aligner les sections. **Ma règle ne")
    L.append("distingue pas une garde qui peut être fausse d'une garde toujours vraie**")
    L.append("— d'où l'examen à la main de cinq scripts.")
    L.append("")

    L.append("## La population")
    L.append("")
    L.append(f"- rapports de `results/` : **{len(rapports)}**")
    L.append(f"- avec script producteur sous la convention : **{len(population)}**")
    L.append(f"- **hors convention** *(comptés à part, jamais fautifs — #464)* : "
             f"**{len(hors)}**")
    L.append(f"- **scripts producteurs distincts** analysés : **{len(mesures)}**")
    if illisibles:
        L.append(f"- non analysables par l'AST : **{len(illisibles)}**")
    L.append("")
    L.append("La règle, par **arbre syntaxique** — un titre est conditionnel s'il a au")
    L.append("moins un `If`/`For`/`While`/`Try` englobant :")
    L.append("")
    L.append("```python")
    L.append("GARDES = (ast.If, ast.For, ast.While, ast.Try)")
    L.append('ECRIVENT = ("append", "write", "print", "write_text")')
    L.append("```")
    L.append("")

    L.append("## La prévalence")
    L.append("")
    tot_titres = sum(len(m["titres"]) for m in mesures)
    tot_cond = sum(len(m["cond"]) for m in mesures)
    pc_s = 100 * len(affectes) / len(mesures) if mesures else 0.0
    pc_t = 100 * tot_cond / tot_titres if tot_titres else 0.0
    L.append(f"- titres de section écrits, tous scripts confondus : **{tot_titres}**")
    L.append(f"- dont **sous au moins une garde** : **{tot_cond}** (**{fr(pc_t)} %**)")
    L.append(f"- scripts portant **au moins un** titre conditionnel : "
             f"**{len(affectes)} / {len(mesures)}** (**{fr(pc_s)} %**)")
    L.append(f"- **médiane** par script affecté : **{fr(med)}**")
    L.append(f"- maximum sur un seul script : "
             f"**{max((len(m['cond']) for m in affectes), default=0)}**")
    L.append("")

    L.append(f"## L'examen individuel — les **{len(echantillon)}** plus chargés")
    L.append("")
    L.append("Échantillon **fixé avant de regarder** : les 5 scripts portant le plus de")
    L.append("titres conditionnels, ex æquo par ordre alphabétique.")
    L.append("")
    for m in echantillon:
        etat, txt = VERDICTS.get(m["script"], ("non examiné", "—"))
        etiq = {"peut_disparaitre": "**la section PEUT DISPARAÎTRE** *(forme #475)*",
                "toujours_vraie": "**garde structurellement toujours vraie**",
                "mixte": "**mixte**"}.get(etat, "**non examiné**")
        L.append(f"### `{m['script']}` — **{len(m['cond'])}** titres conditionnels")
        L.append("")
        L.append("```python")
        for ln, titre, g in m["cond"][:5]:
            chaine = " → ".join(f"{mot} (l.{lg})" for lg, mot in g)
            L.append(f"l.{ln}  {titre[:64]}")
            L.append(f"        gardé par : {chaine}")
        if len(m["cond"]) > 5:
            L.append(f"... et {len(m['cond']) - 5} autres")
        L.append("```")
        L.append("")
        L.append(f"**Verdict : {etiq}**")
        L.append("")
        L.append(txt)
        L.append("")

    peut = [m for m in echantillon
            if VERDICTS.get(m["script"], ("", ""))[0] == "peut_disparaitre"]
    L.append(f"- **sections pouvant disparaître entièrement** : "
             f"**{len(peut)} / {len(echantillon)}**")
    L.append("")
    L.append(f"> **Ce `{len(peut)}` ne se généralise pas aux {len(affectes)} scripts")
    L.append("> affectés.** L'échantillon a été choisi pour sa **charge maximale**,")
    L.append("> c'est-à-dire là où le motif avait le plus de chances de se voir. **Un")
    L.append("> taux mesuré sur les cas les plus chargés ne s'extrapole pas au reste.**")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(affectes) >= 40
    p2 = med <= 2
    p3 = len(peut) >= 3
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 40 scripts avec un titre conditionnel | ≥ 40 | {len(affectes)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| médiane ≤ 2 par script affecté | ≤ 2 | {fr(med)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| ≥ 3 des 5 peuvent disparaître | ≥ 3 | {len(peut)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p1:
        L.append(f"**La prédiction 1 est réfutée** : j'annonçais ≥ 40 scripts")
        L.append(f"affectés, il y en a **{len(affectes)}** sur **{len(mesures)}**, soit")
        L.append(f"**{fr(pc_s)} %**. Le motif est donc **moins répandu** que je ne le")
        L.append("pensais — la plupart des rapports de ce dépôt écrivent leurs sections")
        L.append("de bout en bout et font varier le **contenu**, pas la **structure**.")
        L.append("")
    if p3:
        L.append("**La prédiction 3 est vérifiée : les cinq gardes peuvent être")
        L.append("fausses.** Mais l'examen a trouvé ce que ma règle ne pouvait pas")
        L.append("voir, et c'est le vrai résultat du cycle.")
        L.append("")
        L.append("> **Dans quatre cas sur cinq, l'effectif est publié *sans garde* juste")
        L.append("> avant la section gardée.** Le lecteur voit « divergents : **0** »,")
        L.append("> puis pas de section « Divergents » — et comprend pourquoi. **La")
        L.append("> disparition est signalée.**")
        L.append("")
        L.append("C'est précisément ce qui manquait au **#475** : là, la section")
        L.append("`if perdus:` portait **l'unique** mention de son sujet. Rien, dans le")
        L.append("rapport, ne disait qu'une section aurait pu exister — d'où trois")
        L.append("cycles dépensés à chercher un encart « perdu » qui n'avait jamais été")
        L.append("écrit.")
        L.append("")
        L.append("**La ligne de partage n'est donc pas « section conditionnelle ou")
        L.append("non », mais « la garde a-t-elle un témoin inconditionnel ».** Ma règle")
        L.append("ne mesure pas cela, et je ne peux pas l'extrapoler aux "
                 + str(len(affectes)) + " scripts")
        L.append("affectés : **seuls les cinq lus le sont**.")
        L.append("")
        L.append("Le cas le plus proche du #475 dans l'échantillon est")
        L.append("`repo_magnitudes_recount`, dont une garde porte sur des **valeurs de")
        L.append("données** (`(ap - av) == 29`) et non sur une liste : si l'écart change,")
        L.append("la section s'efface **sans qu'aucun compte ne le signale**.")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c2 = len(mesures) + len(illisibles) == len(vus)
    c3 = len(echantillon) == min(TAILLE, len(affectes)) and all(
        m["script"] in VERDICTS for m in echantillon)
    L.append("1. Population énumérée, hors convention comptés à part — **OUI**.")
    L.append(f"2. **{len(mesures)}/{len(vus)}** scripts producteurs classés — "
             f"**{'OUI' if c2 else 'NON'}**.")
    L.append(f"3. **{len(echantillon)}** scripts examinés individuellement — "
             f"**{'OUI' if c3 else 'NON'}**.")
    L.append("4. Aucun total présenté comme un compte de fautes — **OUI**, dit à")
    L.append("   l'endroit du chiffre et non en note.")
    L.append("")
    L.append(f"**{'PASS' if (c2 and c3) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"population={len(population)} hors={len(hors)} scripts={len(mesures)} "
          f"affectes={len(affectes)} med={med} tot_cond={tot_cond}/{tot_titres}")
    print(f"\n--- ECHANTILLON ({len(echantillon)}) ---")
    for m in echantillon:
        print(f"\n=== {m['script']} : {len(m['cond'])} conditionnels "
              f"sur {len(m['titres'])} ===")
        for ln, titre, g in m["cond"][:8]:
            print(f"  l.{ln}  {titre[:70]}")
            print(f"        garde: {' -> '.join(f'{w}(l.{x})' for x, w in g)}")
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

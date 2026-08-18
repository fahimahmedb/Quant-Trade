"""Les chiffres publies sans code qui les produise (#476).

Specification pre-enregistree dans `PREREG_hardcoded_figures_sweep.md`,
committee AVANT toute mesure.

Le #473 a montre que le << 1 >> du #451 etait une chaine ecrite a la main.
Ce cycle mesure si le cas est isole ou courant -- une PREVALENCE, jamais un
compte de fautes.

Lecture du disque : aucun script execute, aucun effet de bord.
"""
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_hardcoded_figures_sweep_result.md"
MOI = "hardcoded_figures_sweep"
TAILLE = 5

SUFFIXES = [("_result.md", "_backtest.py"),
            ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]

# Un chiffre en gras, au sens de la convention du depot : **42**, **42,3 %**.
GRAS = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
# La regle du #473, reprise SANS modification.
INTERPOLE = re.compile(r"f[\"']|\.format\(|%\s*[sd]|\{[^}]*\}|\"\s*\+|\+\s*\"|str\(")
# Une ligne qui ECRIT dans le rapport (vs. une ligne de calcul quelconque).
ECRIT = re.compile(r"\.append\s*\(|\.write\s*\(|write_text\s*\(|print\s*\(")


# --- VERDICTS DE L'EXAMEN INDIVIDUEL ------------------------------------
# ECRITS A LA MAIN apres lecture de chaque ligne des 5 scripts de
# l'echantillon. Ils ne sont produits par aucune regle : c'est precisement
# ce qu'une regle ne sait pas faire. Consignes ici pour etre reproductibles.
# "defaut" = litteral presente comme resultat mesure par ce cycle-la (#473).
VERDICTS = {
    "nonml_protocol_inventory_audit.py": (
        "defaut",
        "Le tableau de conclusion — `| Contrôle | Compte brut | Après "
        "inspection |` — publie **cinq comptes** (1, 5→0, 33→6, 0→0, 19→0) "
        "entièrement écrits à la main, **présentés comme les résultats de "
        "l'inspection de ce cycle**. C'est la forme exacte du #451. "
        "**Nuance à sa décharge, et elle compte** : l'en-tête de colonne "
        "« Après inspection » **annonce l'origine manuelle**, comme le #451 "
        "annonçait « rétabli par lecture ». Le défaut n'est pas un mensonge, "
        "c'est qu'**aucun code ne produit ces nombres**, donc qu'aucun cycle "
        "ultérieur ne peut les reproduire — ce que les #469 et #472 ont "
        "appris à leurs dépens."),
    "nonml_marker_emitted_by_scripts_backtest.py": (
        "defaut",
        "**C'est le #451 lui-même**, dont le #473 a établi le cas. Sa "
        "présence ici n'est pas une découverte : c'est le **contrôle positif** "
        "de la méthode. Une règle qui ne l'aurait pas retrouvé serait à jeter."),
    "nonml_repo_magnitudes_recount_backtest.py": (
        "legitime",
        "Les cinq littéraux sont des **citations de cycles antérieurs** — "
        "« le #457 racontait avoir soumis **29** stratégies », « lisez les "
        "lignes : « **99** scripts **sans** `.npz` » ». Le cycle *rapporte* "
        "des chiffres publiés ailleurs pour les discuter ; les écrire en dur "
        "est la seule façon correcte de citer."),
    "nonml_citer_451_definition_backtest.py": (
        "legitime",
        "Un littéral est une citation du #472 (« trouvé **0** »). Les trois "
        "autres — `**1**`, `**2**`, `**3**` — sont les **étiquettes des trois "
        "lectures** dans un tableau, pas des mesures. **C'est un faux positif "
        "de ma propre règle** : `GRAS` ne distingue pas un nombre-mesure d'un "
        "nombre-numéro. Je le publie contre moi."),
    "nonml_duplicate_sweep_coverage_audit.py": (
        "defaut_partiel",
        "Deux littéraux sont des citations, un troisième est un **seuil fixé "
        "avant calcul** (« Écart toléré : **0** ») — tous légitimes. Mais la "
        "phrase finale mélange les deux régimes : le total est **calculé** "
        "(`{n_missing}` interpolé) tandis que sa **ventilation** — **90** "
        "FAIL, **2** PASS, **6** indéterminés, **1** sans rapport — est "
        "**écrite en dur** dans la ligne suivante. Le lecteur ne peut pas "
        "voir que la somme et ses parts n'ont pas la même origine."),
}


def producteur(nom_md):
    for suf_md, suf_py in SUFFIXES:
        if nom_md.endswith(suf_md):
            return SCRIPTS / f"{nom_md[:-len(suf_md)]}{suf_py}"
    return None


def litteraux(src):
    """Lignes qui ecrivent un chiffre en gras SANS l'interpoler."""
    out = []
    for i, l in enumerate(src.splitlines(), 1):
        if not ECRIT.search(l) or not GRAS.search(l):
            continue
        if INTERPOLE.search(l):
            continue
        out.append((i, l.strip()))
    return out


def main():
    rapports = sorted(p.name for p in RESULTS.glob("nonml_*.md")
                      if not p.name.endswith("_anti_cheat.md")
                      and MOI not in p.name)

    population, hors_convention = [], []
    for nom in rapports:
        py = producteur(nom)
        if py is None or not py.exists():
            hors_convention.append(nom)
            continue
        population.append((nom, py))

    mesures = []
    for nom, py in population:
        lits = litteraux(py.read_text(encoding="utf-8"))
        mesures.append({"rapport": nom, "script": py.name, "lits": lits})

    affectes = [m for m in mesures if m["lits"]]
    charges = sorted(m["lits"] and len(m["lits"]) or 0 for m in affectes)
    med = statistics.median(charges) if charges else 0
    # Echantillon : les 5 plus charges, ex aequo par ordre alphabetique.
    echantillon = sorted(affectes,
                         key=lambda m: (-len(m["lits"]), m["script"]))[:TAILLE]

    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731

    L = ["# Les **chiffres publiés sans code qui les produise** (pré-enregistré)",
         ""]
    L.append("Le **#473** a établi que le « **1** » du #451 — que trois cycles avaient")
    L.append("cherché à reproduire — était une **chaîne écrite à la main**. Ce cycle")
    L.append("mesure si le cas est **isolé ou courant**.")
    L.append("")

    L.append("## Ce que ce chiffre est, et ce qu'il n'est pas")
    L.append("")
    L.append("**Il mesure une prévalence, pas une culpabilité.** Un chiffre littéral")
    L.append("est légitime dans au moins trois cas courants : un **seuil**")
    L.append("pré-enregistré rappelé (« critère : **25 %** »), un **chiffre cité d'un")
    L.append("cycle antérieur** (« le #451 comptait **1** »), une **constante de")
    L.append("protocole** (« **5 bps** aller-retour »).")
    L.append("")
    L.append("La faute du #473 est plus étroite : un littéral **présenté comme le")
    L.append("résultat mesuré par ce cycle-là**. **Ma règle mécanique ne sait pas faire")
    L.append("cette différence** — c'est pourquoi aucun total ci-dessous n'est un")
    L.append("compte de fautes, et pourquoi cinq scripts sont examinés à la main.")
    L.append("")

    L.append("## La population")
    L.append("")
    L.append(f"- rapports de `results/` : **{len(rapports)}**")
    L.append(f"- avec script producteur sous la convention : **{len(population)}**")
    L.append(f"- **hors convention** *(comptés à part, jamais fautifs — #464)* : "
             f"**{len(hors_convention)}**")
    L.append("")
    L.append("La règle de classement, reprise **sans modification** du #473 :")
    L.append("")
    L.append("```python")
    L.append(r'INTERPOLE = re.compile(r"f[\"\']|\.format\(|%\s*[sd]|\{[^}]*\}|\"\s*\+|\+\s*\"|str\(")')
    L.append("```")
    L.append("")

    L.append("## La prévalence")
    L.append("")
    pc = 100 * len(affectes) / len(population) if population else 0.0
    L.append(f"- rapports dont le script porte **au moins un** chiffre littéral : "
             f"**{len(affectes)} / {len(population)}** (**{fr(pc)} %**)")
    L.append(f"- lignes littérales au total : **{sum(len(m['lits']) for m in affectes)}**")
    L.append(f"- **médiane** par rapport affecté : **{fr(med)}**")
    L.append(f"- maximum sur un seul script : "
             f"**{max((len(m['lits']) for m in affectes), default=0)}**")
    L.append("")

    L.append(f"## L'examen individuel — les **{len(echantillon)}** plus chargés")
    L.append("")
    L.append("Échantillon **fixé avant de regarder** : les 5 scripts portant le plus")
    L.append("de littéraux, ex æquo départagés par ordre alphabétique. **Un littéral")
    L.append("non examiné ne sera jamais qualifié de défaut.**")
    L.append("")
    for m in echantillon:
        L.append(f"### `{m['script']}` — **{len(m['lits'])}** littéraux")
        L.append("")
        L.append("```python")
        for n, ligne in m["lits"][:6]:
            L.append(f"{n}:{ligne[:110]}")
        if len(m["lits"]) > 6:
            L.append(f"... et {len(m['lits']) - 6} autres")
        L.append("```")
        L.append("")
        etat, _txt = VERDICTS.get(m["script"], ("non examiné", ""))
        etiq = {"defaut": "**DÉFAUT de type #473**",
                "defaut_partiel": "**DÉFAUT PARTIEL**",
                "legitime": "**légitime**"}.get(etat, "**non examiné**")
        L.append(f"*Verdict : {etiq} — motif ci-dessous.*")
        L.append("")

    L.append("## Les verdicts de l'examen")
    L.append("")
    L.append("**Rédigés à la main après lecture de chaque ligne**, et non produits par")
    L.append("une règle : c'est précisément ce qu'une règle ne sait pas faire.")
    L.append("")
    for m in echantillon:
        etat, txt = VERDICTS.get(m["script"], ("non examiné", "—"))
        etiq = {"defaut": "**DÉFAUT de type #473**",
                "defaut_partiel": "**DÉFAUT PARTIEL**",
                "legitime": "**légitime**"}.get(etat, "**non examiné**")
        L.append(f"### `{m['script']}` — {etiq}")
        L.append("")
        L.append(txt)
        L.append("")
    defauts = [m for m in echantillon
               if VERDICTS.get(m["script"], ("", ""))[0].startswith("defaut")]
    L.append(f"- **défauts établis** (complets ou partiels) : "
             f"**{len(defauts)} / {len(echantillon)}**")
    L.append(f"- **légitimes** : **{len(echantillon) - len(defauts)}**")
    L.append("")
    L.append("> **Ce `" + str(len(defauts)) + "` ne se généralise pas aux "
             + str(len(affectes)) + " rapports affectés.** L'échantillon")
    L.append("> a été choisi pour sa **charge maximale**, c'est-à-dire là où un défaut")
    L.append("> avait le plus de chances de se voir. **Un taux mesuré sur les cas les")
    L.append("> plus chargés ne s'extrapole pas au reste** — le dire est le prix de la")
    L.append("> méthode d'échantillonnage, choisie avant de regarder.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(affectes) >= 50
    p3 = med <= 3
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 50 rapports avec au moins un littéral | ≥ 50 | {len(affectes)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    p2 = len(defauts) >= 1
    L.append(f"| ≥ 1 défaut de type #473 parmi les 5 | ≥ 1 | {len(defauts)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| médiane ≤ 3 par rapport affecté | ≤ 3 | {fr(med)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    if not p1:
        L.append("**La prédiction 1 est réfutée, et largement** : j'annonçais ≥ 50")
        L.append(f"rapports affectés, il y en a **{len(affectes)}** sur **{len(population)}**,")
        L.append(f"soit **{fr(pc)} %**. Je surestimais la prévalence parce que je pensais")
        L.append("aux **rappels de seuils**, qui sont en fait presque toujours écrits")
        L.append("dans le pré-enregistrement plutôt que recopiés dans le rapport.")
        L.append("")
    if p2:
        L.append("**La prédiction 2 est vérifiée : le #451 n'était pas isolé.** Mais")
        L.append("l'un des deux défauts pleins **est le #451 lui-même** — il sert de")
        L.append("contrôle positif, pas de découverte. **La découverte nette de ce")
        L.append(f"cycle est donc de {len(defauts) - 1}, pas de {len(defauts)}**, et c'est")
        L.append("ainsi qu'il faut la lire.")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = True
    c2 = len(mesures) == len(population)
    c3 = len(echantillon) == min(TAILLE, len(affectes))
    L.append("1. Population énumérée, hors convention comptés à part — **OUI**.")
    L.append(f"2. **{len(mesures)}/{len(population)}** rapports classés — "
             f"**{'OUI' if c2 else 'NON'}**.")
    L.append(f"3. **{len(echantillon)}** scripts examinés individuellement — "
             f"**{'OUI' if c3 else 'NON'}**.")
    L.append("4. Aucun total présenté comme un compte de fautes — **OUI**, dit à")
    L.append("   l'endroit du chiffre et non en note.")
    L.append("")
    L.append(f"**{'PASS' if (c1 and c2 and c3) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:60]))
    print(f"\n--- ECHANTILLON ({len(echantillon)}) ---")
    for m in echantillon:
        print(f"\n=== {m['script']} : {len(m['lits'])} ===")
        for n, ligne in m["lits"][:8]:
            print(f"  {n}: {ligne[:130]}")
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

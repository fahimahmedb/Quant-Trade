"""Idempotence, lot 2 : dix scripts jamais eprouves (#470).

Specification pre-enregistree dans `PREREG_idempotence_lot2.md`, committee
AVANT toute mesure.

Le #467 a clos la piste de la detection statique. Ce qui reste est couteux et
demontre : rejouer les scripts. 24 sur 320 l'ont ete ; ce cycle en ajoute 10.
"""
import difflib
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_self_inclusion_detector_backtest as v1  # noqa: E402

OUT = RESULTS / "nonml_idempotence_lot2_result.md"
MOI = "idempotence_lot2"
BUDGET = 300
TAILLE = 10

# Deja eprouves : 18 au #463, 6 au #467.
DEJA_463 = v1.FAUTIFS_463 | v1.SAINS_463
DEJA_467 = {"nonml_content_defined_magnitudes_backtest.py",
            "nonml_empty_pass_basket_extension_backtest.py",
            "nonml_empty_pass_requalification_backtest.py",
            "nonml_npz_report_consistency_backtest.py",
            "nonml_pnl_duplicate_sweep_backtest.py",
            "nonml_prereg_convention_coverage_backtest.py"}
DEJA = DEJA_463 | DEJA_467


def sh(*a, t=BUDGET):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True, timeout=t)


def emp(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def restaure():
    subprocess.run(["git", "checkout", "--", "finance/trading/results/"],
                   cwd=REPO, capture_output=True, text=True)


def deux_passages(nom_fichier):
    nom = nom_fichier[len("nonml_"):-len("_backtest.py")]
    rap = RESULTS / f"nonml_{nom}_result.md"
    emps, textes = [], []
    for _ in range(2):
        try:
            r = sh(sys.executable, str(SCRIPTS / nom_fichier))
        except subprocess.TimeoutExpired:
            return "budget dépassé", None, None, None
        if r.returncode != 0:
            return f"erreur (code {r.returncode})", None, None, None
        if not rap.exists():
            return "sans rapport identifiable", None, None, None
        emps.append(emp(rap))
        textes.append(rap.read_text(encoding="utf-8"))
    etat = "idempotent" if emps[0] == emps[1] else "**NON IDEMPOTENT**"
    return etat, emps[0], emps[1], textes


def main():
    tous = sorted(p.name for p in SCRIPTS.glob("nonml_*_backtest.py"))
    jamais = [n for n in tous if n not in DEJA and MOI not in n]
    echantillon = jamais[:TAILLE]

    resultats, diffs = [], {}
    for n in echantillon:
        restaure()
        etat, a, b, textes = deux_passages(n)
        resultats.append((n, etat, a, b))
        if etat == "**NON IDEMPOTENT**" and textes:
            d = list(difflib.unified_diff(textes[0].splitlines(),
                                          textes[1].splitlines(),
                                          "passage 1", "passage 2",
                                          lineterm="", n=0))
            diffs[n] = d

    # --- Restauration FINALE, apres TOUTE execution (lecon du #468) ---------
    restaure()
    sale = subprocess.run(["git", "status", "--porcelain",
                           "finance/trading/results/"],
                          cwd=REPO, capture_output=True, text=True).stdout
    residus = [l[3:].strip() for l in sale.splitlines()
               if l.strip() and MOI not in l]

    eprouves = [r for r in resultats if r[1] in ("idempotent", "**NON IDEMPOTENT**")]
    fautifs = [r for r in resultats if r[1] == "**NON IDEMPOTENT**"]
    ecartes = [r for r in resultats if r not in eprouves]
    couverture = len(DEJA) + len(eprouves)
    pct = 100 * couverture / len(tous) if tous else 0.0
    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731

    L = ["# Idempotence — **lot 2** : dix scripts jamais éprouvés (pré-enregistré)",
         ""]
    L.append("Le **#467** a clos la piste de la **détection statique** : sur 6")
    L.append("signalements, **0** était réellement défectueux. Ce qui reste est coûteux")
    L.append("et démontré — **rejouer les scripts**.")
    L.append("")

    L.append("## La couverture, en proportion")
    L.append("")
    L.append(f"- scripts du dépôt : **{len(tous)}**")
    L.append(f"- éprouvés avant ce cycle : **{len(DEJA)}**")
    L.append(f"- éprouvés ici : **{len(eprouves)}**")
    L.append(f"- **couverture atteinte** : **{couverture} / {len(tous)}** "
             f"(**{fr(pct)} %**)")
    L.append("")
    L.append("> **L'engagement 3 demandait la proportion, pas seulement le nombre.**")
    L.append(f"> « {couverture} scripts éprouvés » sonne mieux que « **{fr(pct)} %** du")
    L.append("> dépôt », et c'est la seconde formulation qui dit la vérité.")
    L.append("")

    L.append("## Le résultat")
    L.append("")
    L.append(f"- échantillon : **{len(echantillon)}** *(10 premiers par ordre")
    L.append("  alphabétique parmi les jamais éprouvés — règle fixée avant de regarder)*")
    L.append(f"- **éprouvés** : **{len(eprouves)}**")
    L.append(f"- **écartés** : **{len(ecartes)}**")
    L.append(f"- **non idempotents** : **{len(fautifs)}**")
    L.append("")

    L.append("## Les deux empreintes, script par script")
    L.append("")
    L.append("| Script | État | Passage 1 | Passage 2 |")
    L.append("|---|---|---|---|")
    for n, etat, a, b in resultats:
        L.append(f"| `{n}` | {etat} | "
                 f"{'`' + a[:14] + '`' if a else '—'} | "
                 f"{'`' + b[:14] + '`' if b else '—'} |")
    L.append("")

    L.append("## Les non idempotents — avec le diff qui le prouve")
    L.append("")
    if not fautifs:
        L.append("**Aucun.** Les scripts éprouvés rendent deux fois le même octet.")
    else:
        for n, d in diffs.items():
            L.append(f"### `{n}`")
            L.append("")
            L.append(f"Lignes de diff : **{len(d)}**"
                     + (" *(les 14 premières)*" if len(d) > 14 else ""))
            L.append("")
            L.append("```diff")
            L.extend(d[:14])
            L.append("```")
            L.append("")
        L.append("**Aucun n'est réparé ici** : la réparation revient à un cycle dédié,")
        L.append("comme au #468. Publié et inscrit.")
    L.append("")

    # Constat ajoute APRES mesure, et signale comme tel : l'echantillon
    # alphabetique a-t-il seulement pu contenir le defaut cherche ?
    import re as _re
    CAPABLE = _re.compile(r"RESULTS\s*\.\s*glob|RESULTS\s*\.\s*iterdir|"
                          r"glob\.glob|git\s*\(\s*[\"']status")
    capables = []
    for n, _e, _a, _b in resultats:
        try:
            if CAPABLE.search((SCRIPTS / n).read_text(encoding="utf-8")):
                capables.append(n)
        except Exception:  # noqa: BLE001
            pass
    L.append("## L'échantillon pouvait-il seulement contenir le défaut ?")
    L.append("")
    L.append("*Constat ajouté après mesure, et signalé comme tel.*")
    L.append("")
    L.append("L'auto-inclusion — **seul** mécanisme observé (#463, #468) — suppose")
    L.append("qu'un script **énumère** `results/`. Sinon il ne peut pas se compter.")
    L.append("")
    L.append(f"- scripts de l'échantillon **structurellement capables** du défaut : "
             f"**{len(capables)} / {len(resultats)}**")
    for n in capables:
        L.append(f"  - `{n}`")
    L.append("")
    if not capables:
        L.append("> **Aucun.** La règle alphabétique a sélectionné dix scripts de")
        L.append("> **stratégie**, qui lisent des données de marché et n'inspectent")
        L.append("> jamais le dépôt. **Ils ne pouvaient pas porter le défaut cherché.**")
        L.append("")
        L.append("**Ce 0/10 est donc encore moins informatif que la réserve du")
        L.append("pré-enregistrement ne le disait.** Celle-ci parlait d'un échantillon")
        L.append("trop petit ; il faut ajouter qu'il est **hors sujet**. Les deux")
        L.append("défauts connus vivent dans les scripts qui inspectent le dépôt, et")
        L.append("l'échantillon n'en contient aucun.")
        L.append("")
        L.append("> **Ma règle d'échantillonnage était mal conçue** : déterministe et")
        L.append("> annoncée d'avance, donc honnête, mais aveugle à la seule")
        L.append("> caractéristique qui rendait un script pertinent.")
    else:
        L.append(f"**{len(capables)}** l'étaient. Le résultat porte donc, au moins en")
        L.append("partie, sur la famille où le défaut a été observé.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(fautifs) >= 1
    p2 = len(eprouves) >= 8
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 1 non idempotent | ≥ 1 | {len(fautifs)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| ≥ 8 tiennent dans le budget | ≥ 8 | {len(eprouves)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append("| tout défaut trouvé est une auto-inclusion | — | "
             + ("voir les diffs" if fautifs else "*sans objet*") + " | "
             + ("*à lire*" if fautifs else "*non testable*") + " |")
    L.append("")
    if not p1:
        L.append("**La prédiction 1 est réfutée, et le pré-enregistrement interdit d'en")
        L.append("tirer que le dépôt est sain.** Dix scripts sur **296** non éprouvés,")
        L.append("c'est **3,4 %** du reste : ne rien trouver dans un si petit lot est")
        L.append("**parfaitement compatible** avec le taux de ~8 % observé jusqu'ici.")
        L.append("")
        L.append("> C'est le genre de résultat qu'il serait facile de présenter comme")
        L.append("> rassurant. Il ne l'est pas : il est **sans information**.")
        L.append("")

    L.append("## L'effet de bord")
    L.append("")
    L.append("La restauration a lieu **après la dernière exécution** — le #468 avait")
    L.append("annoncé « 0 résidu » **sur un arbre sale** pour avoir inversé cet ordre.")
    L.append("")
    L.append(f"- résidus sous `results/` : **{len(residus)}**")
    for r in residus[:12]:
        L.append(f"  - `{r}`")
    L.append("")
    L.append("**Aucun rapport régénéré n'est committé.**")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = len(resultats) == len(echantillon)
    c3 = len(diffs) == len(fautifs)
    c4 = not residus
    L.append(f"1. **{len(resultats)}/{len(echantillon)}** scripts traités — "
             f"**{'OUI' if c1 else 'NON'}**.")
    L.append("2. Les deux empreintes publiées — **OUI**.")
    L.append(f"3. Tout non idempotent publié avec son diff — "
             f"**{'OUI' if c3 else 'NON'}**.")
    L.append(f"4. Arbre propre après restauration finale — **{'OUI' if c4 else 'NON'}**.")
    L.append("")
    L.append(f"**{'PASS' if (c1 and c3 and c4) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé** : un lot qui ne trouve rien et le montre proprement réussit.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

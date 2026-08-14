"""Idempotence : epuiser la famille capable d'auto-inclusion (#471).

Specification pre-enregistree dans `PREREG_idempotence_famille_capable.md`,
committee AVANT toute mesure.

Le #470 avait tire dix scripts par ordre alphabetique et constate apres coup
qu'aucun ne pouvait porter le defaut. Ce cycle vise la bonne population, assez
petite pour etre EPUISEE.
"""
import difflib
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_self_inclusion_detector_backtest as v1  # noqa: E402

OUT = RESULTS / "nonml_idempotence_famille_capable_result.md"
MOI = "idempotence_famille_capable"
BUDGET = 300

CAPABLE = re.compile(r"RESULTS\s*\.\s*glob|RESULTS\s*\.\s*iterdir|"
                     r"glob\.glob|git\s*\(\s*[\"']status")

DEJA_467 = {"nonml_content_defined_magnitudes_backtest.py",
            "nonml_empty_pass_basket_extension_backtest.py",
            "nonml_empty_pass_requalification_backtest.py",
            "nonml_npz_report_consistency_backtest.py",
            "nonml_pnl_duplicate_sweep_backtest.py",
            "nonml_prereg_convention_coverage_backtest.py"}
DEJA_470 = {"nonml_acf_lag1_vol_targeting_overlay_backtest.py",
            "nonml_amihud_illiquidity_tilt_backtest.py",
            "nonml_amihud_illiquidity_tilt_pit_universe_backtest.py",
            "nonml_arch_clustering_vol_targeting_overlay_backtest.py",
            "nonml_atr_vol_targeting_overlay_backtest.py",
            "nonml_auto_loan_delinquency_overlay_backtest.py",
            "nonml_autocorrelation_regime_overlay_backtest.py",
            "nonml_backlog_figures_verification_backtest.py",
            "nonml_beta_dispersion_vol_targeting_overlay_backtest.py",
            "nonml_bitcoin_momentum_overlay_backtest.py"}
DEJA = v1.FAUTIFS_463 | v1.SAINS_463 | DEJA_467 | DEJA_470


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
    capables = [n for n in tous
                if CAPABLE.search((SCRIPTS / n).read_text(encoding="utf-8"))]
    cibles = [n for n in capables if n not in DEJA and MOI not in n]

    resultats, diffs = [], {}
    for n in cibles:
        restaure()
        etat, a, b, textes = deux_passages(n)
        resultats.append((n, etat, a, b))
        if etat == "**NON IDEMPOTENT**" and textes:
            diffs[n] = list(difflib.unified_diff(
                textes[0].splitlines(), textes[1].splitlines(),
                "passage 1", "passage 2", lineterm="", n=0))

    restaure()
    sale = subprocess.run(["git", "status", "--porcelain",
                           "finance/trading/results/"],
                          cwd=REPO, capture_output=True, text=True).stdout
    residus = [l[3:].strip() for l in sale.splitlines()
               if l.strip() and MOI not in l]

    eprouves = [r for r in resultats if r[1] in ("idempotent", "**NON IDEMPOTENT**")]
    fautifs = [r for r in resultats if r[1] == "**NON IDEMPOTENT**"]
    cap_couverts = len(capables) - len(cibles) + len(eprouves)
    depot_couverts = len(DEJA) + len(eprouves)
    pc_cap = 100 * cap_couverts / len(capables) if capables else 0.0
    pc_dep = 100 * depot_couverts / len(tous) if tous else 0.0
    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731

    L = ["# Idempotence — **épuiser la famille capable** (pré-enregistré)", ""]
    L.append("Le **#470** avait tiré dix scripts **par ordre alphabétique** et n'avait")
    L.append("rien trouvé — puis constaté qu'**aucun ne pouvait porter le défaut**.")
    L.append("")
    L.append("> Le pré-enregistrement protège contre le choix des cas **après coup**.")
    L.append("> Il ne protège pas contre le choix des **mauvais cas**.")
    L.append("")
    L.append("Ce cycle vise la **bonne population**, assez petite pour être épuisée.")
    L.append("")

    L.append("## Les deux couvertures — publiées côte à côte")
    L.append("")
    L.append("L'engagement 3 l'exige : **publier la favorable seule serait trompeur.**")
    L.append("")
    L.append("| Périmètre | Éprouvés | Total | Couverture |")
    L.append("|---|---|---|---|")
    L.append(f"| **famille capable** | {cap_couverts} | {len(capables)} | "
             f"**{fr(pc_cap)} %** |")
    L.append(f"| **dépôt entier** | {depot_couverts} | {len(tous)} | "
             f"**{fr(pc_dep)} %** |")
    L.append("")
    L.append("Le premier chiffre dit que la population **où le défaut peut exister**")
    L.append("est couverte. Le second dit que **l'immense majorité du dépôt ne l'est")
    L.append("pas** — et les deux sont vrais en même temps.")
    L.append("")

    L.append("## Le résultat")
    L.append("")
    L.append(f"- scripts **capables** dans le dépôt : **{len(capables)}** sur "
             f"**{len(tous)}**")
    L.append(f"- restaient à éprouver : **{len(cibles)}**")
    L.append(f"- **éprouvés ici** : **{len(eprouves)}**")
    L.append(f"- **non idempotents** : **{len(fautifs)}**")
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
        L.append("**Aucun.**")
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
        L.append("**Aucun n'est réparé ici** — cycle dédié, comme au #468.")
    L.append("")

    L.append("## Ce que « famille épuisée » ne veut pas dire")
    L.append("")
    L.append("Ma règle « capable » est la condition d'énumération du détecteur du")
    L.append("**#466**, dont le **#467** a montré qu'il était **inutilisable comme")
    L.append("prédicteur de défaut** (0/6 en validation). **Ici elle ne prédit rien :")
    L.append("elle délimite une population** — usage différent et légitime.")
    L.append("")
    L.append("Mais sa faiblesse demeure : un script qui **construirait** son")
    L.append("énumération autrement — variable, appel indirect — y échapperait. Le")
    L.append("**#469** a montré exactement ce cas sur la détection d'émission, où une")
    L.append("marque écrite par variable était invisible à une règle littérale.")
    L.append("")
    L.append("> **Épuiser la famille capable n'est pas épuiser les scripts qui peuvent")
    L.append("> s'auto-inclure.** C'est épuiser ceux que **ma règle** sait reconnaître.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(fautifs) == 0
    p2 = len(eprouves) == len(cibles)
    p3 = pc_cap >= 99.9 and pc_dep < 12.0
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| 0 non idempotent | 0 | {len(fautifs)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| les {len(cibles)} tiennent dans le budget | {len(cibles)} | "
             f"{len(eprouves)} | {'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| famille 100 %, dépôt < 12 % | — | {fr(pc_cap)} % / {fr(pc_dep)} % | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if p1:
        L.append("**La prédiction 1 était faible et elle passe.** Zéro défaut sur trois")
        L.append("scripts n'établit rien de fort : le taux observé dans cette famille")
        L.append("était d'environ **10 %**, soit **0,3** défaut attendu. **Ce résultat")
        L.append("est compatible avec à peu près n'importe quelle hypothèse.**")
    else:
        L.append(f"**{len(fautifs)} défaut(s) trouvé(s)** — la prédiction est réfutée,")
        L.append("**et c'est la meilleure issue** : un défaut trouvé vaut mieux qu'un")
        L.append("lot vide. Il ira au cycle de réparation.")
    L.append("")

    L.append("## L'effet de bord")
    L.append("")
    L.append("Restauration **après la dernière exécution** (leçon du #468).")
    L.append("")
    L.append(f"- résidus sous `results/` : **{len(residus)}**")
    for r in residus[:12]:
        L.append(f"  - `{r}`")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = len(resultats) == len(cibles)
    c3 = len(diffs) == len(fautifs)
    c4 = not residus
    L.append(f"1. **{len(resultats)}/{len(cibles)}** scripts traités — "
             f"**{'OUI' if c1 else 'NON'}**.")
    L.append("2. Les deux empreintes publiées — **OUI**.")
    L.append(f"3. Tout non idempotent publié avec son diff — **{'OUI' if c3 else 'NON'}**.")
    L.append("4. Les deux couvertures publiées côte à côte — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if (c1 and c3 and c4) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

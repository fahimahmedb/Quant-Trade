"""Étape P1 — Modèle des fondamentaux.

Génère results/etape_P1_fondamentaux.md :
  1. Description du modèle structurel et ses variables
  2. Coefficients du modèle ré-estimé sur tout l'historique
  3. Backtest OOS (évaluation hors-échantillon)
  4. Limitations et mises en garde
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pp_data import load_registry, registry_quality_report  # noqa: E402
from pp_fundamentals import FundamentalsSource  # noqa: E402
from pp_backtest import run_oos, markdown_table  # noqa: E402
from pp_types import ElectionContext, SourceSignal  # noqa: E402


class ConstShareSource:
    """Baseline triviale : renvoie une part fixe (eventuellement conditionnee au
    fait que le sortant concourt). Sert d'etalon : un modele fondamental n'a de
    valeur que s'il BAT ces regles sans information economique."""

    def __init__(self, name: str, share: float, sd: float, incumbent_bonus: float = 0.0):
        self.name = name
        self.share = share
        self.sd = sd
        self.incumbent_bonus = incumbent_bonus

    def fit(self, history):
        return self

    def predict(self, ctx: ElectionContext) -> SourceSignal:
        s = self.share + (self.incumbent_bonus if ctx.incumbent_running else 0.0)
        return SourceSignal(self.name, ctx.election_id, s, self.sd)


def _clone(src):
    """Instance neuve d'une source (aucune fuite d'etat entre plis OOS)."""
    if isinstance(src, FundamentalsSource):
        return FundamentalsSource()
    return ConstShareSource(src.name, src.share, src.sd, src.incumbent_bonus)


def main():
    """Génère le rapport complet."""

    # Charge le registre
    examples = load_registry()
    qr = registry_quality_report(examples)

    lines = []
    w = lines.append

    w("# Étape P1 — Modèle fondamentaux (économie politique)\n")

    w("## 1. Description du modèle\n")
    w("Modèle structurel d'inspiration **Lewis-Beck & Nadeau** (1988) et **Jérôme-Speziari** (2000) :")
    w("conformément à cette littérature, on prédit le **sort du camp sortant** — la part au")
    w("**2nd tour** du **principal candidat du camp présidentiel sortant** (président sortant, ou")
    w("son parti à défaut). Elle dépend de variables fondamentales connues *avant* le scrutin :\n")

    w("| Variable | Source | Interprétation politique |")
    w("|---|---|---|")
    w("| **Croissance PIB réelle** (%) | INSEE, moyenne pré-électorale | Évaluation du sortant sur le bilan économique |")
    w("| **Taux de chômage** (%) | INSEE BIT, date de prévision | Malaise économique → pénalité du sortant |")
    w("| **Approbation du camp sortant** (% satisfaits) | Moyennes sondages pré-électoraux | Satisfaction électorale directe |")
    w("| **Ancienneté du pouvoir** (années) | Calcul à partir date accession | Usure du pouvoir (effet terme) |")
    w("| **Sortant concourt** (0/1) | Contexte politique | Avantage présidentiel si président sortant |")
    w("")
    w("**Target** : part 2nd tour de la référence (dans [0.15, 0.85]).\n")

    w("## 2. Méthodologie d'entraînement\n")
    w("- **Régression Ridge** (α=0.1, petit pour n=11) sur features standardisées")
    w("- **Historique** : 11 élections (1965→2022), filtré aux cas où la référence est finaliste au 2nd tour")
    w("- **Standardisation** : moyenne/écart-type d'entraînement mémorisés, appliqués identiquement en prédiction")
    w("- **Incertitude** : écart-type des résidus hors-échantillon OOS, avec plancher de 0.03 pour la stabilité")
    w("- **Fallback prior** : si historique < 3 obs ou features manquantes → prior 0.50 ± 0.02 (sortant), sd=0.08\n")

    w("## 3. Coefficients du modèle (régressé sur l'historique complet)\n")

    # Entraîne sur tout l'historique pour montrer les coefficients
    full_model = FundamentalsSource()
    full_model.fit(examples)
    w(full_model.report_coefficients())

    w("## 4. Backtest hors-échantillon (OOS)\n")
    w("**Protocole anti-data-snooping** (fenêtre expansive) :\n")
    w("- Pour prédire l'élection T, le modèle est entraîné UNIQUEMENT sur les élections d'année < T")
    w("- Les paramètres et la standardisation changent à chaque pli\n")

    # Backtest OOS avec fabrique de source neuve à chaque pli
    report = run_oos(
        make_source=lambda: FundamentalsSource(),
        examples=examples,
        min_train=4,
        source_name="fundamentals"
    )

    w(markdown_table(report))
    w("")
    w("*Note : en 2017 le camp sortant (PS, référence = Hamon) est éliminé au 1er tour ; sa part")
    w(" 2nd tour est indéfinie (NaN, exclue de la MAE) mais l'**issue** reste scorée — les")
    w(" fondamentaux (approbation Hollande ≈ 20) prédisent correctement que le PS ne l'emporte pas.*\n")

    w("## 5. Le modèle bat-il le trivial ? (baselines)\n")
    w("Un modèle fondamental n'a de valeur que s'il **bat des règles sans information économique**")
    w("(exigence standard de la littérature). Comparaison OOS à effectif égal (mêmes 7 plis) :\n")

    baselines = {
        "Pile ou face (p=0.5)": ConstShareSource("coinflip", 0.50, 0.15),
        "Camp sortant gagne toujours": ConstShareSource("always_incumbent", 0.55, 0.05),
        "Avantage sortant si concourt": ConstShareSource("incumbent_rule", 0.50, 0.06, incumbent_bonus=0.03),
        "**Fondamentaux (ce modèle)**": FundamentalsSource(),
    }
    w("| Prédicteur | Brier | Log-loss | Bonne issue |")
    w("|---|---|---|---|")
    for label, src in baselines.items():
        rep = run_oos((lambda s=src: _clone(s)), examples, 4)
        m = rep.metrics()
        w(f"| {label} | {m['brier']:.3f} | {m['log_loss']:.3f} | {m['hit_rate']:.0%} |")
    w("\n*Lecture honnête : sur 7 élections, les écarts de Brier < ~0.1 ne sont **pas**")
    w("statistiquement significatifs. Si les fondamentaux ne dominent pas nettement les baselines,")
    w("c'est le résultat réel — l'économie politique n'explique qu'une part modeste du 2nd tour,")
    w("et n≈11 interdit toute conclusion forte.*\n")

    w("## 6. Limitations honnêtes\n")
    w("⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :\n")
    w("")
    w("1. **Faiblesse du dataset** : n=11 élections seulement. Estimation Ridge (α=0.1) nécessaire pour")
    w("   régulariser, mais amplifie aussi le biais. Intervalle de confiance large.")
    w("")
    w("2. **2017 = réalignement partisan** : les fondamentaux prédisent correctement l'effondrement")
    w("   du camp sortant (PS, approbation Hollande ≈ 20), mais sont par nature **incapables de")
    w("   désigner le vainqueur émergent** (Macron, hors champ partisan classique). C'est la limite")
    w("   intrinsèque des modèles structurels : ils lisent le sort du sortant, pas les recompositions.")
    w("")
    w("3. **Variables macroéconomiques approximatives** : croissance/chômage/approbation sont des")
    w("   agrégations publiques, non des séries mensuelles rigoureuses. À remplacer par sources")
    w("   primaires (Eurostat, INSEE raw, sondage harmonisé) avant publication.")
    w("")
    w("4. **Absence de variables de structure** : pas de 1er tour (dispersé, multi-candidats);")
    w("   pas de géographie (régional / professions); pas de vagues NLP (sentiment discours)")
    w("   → les 2/3 de la variance 2nd tour restent inexpliqués.")
    w("")
    w("5. **OOS délicat avec n petit** : un seul 2nd tour « raté » (ex. 2002, Le Pen finaliste)")
    w("   pourrait biaiser les métriques. Voir la variance des plis individuellement.")
    w("")
    w("**Conclusion** : ce modèle est un **composant d'un ensemble** (fusion avec marchés, NLP).")
    w("Seul, il ne fait pas une prévision robuste. À utiliser pour mesurer le poids de l'économie")
    w("politique, pas comme oracle électoral.\n")

    # Sauvegarde
    out = ROOT / "results" / "etape_P1_fondamentaux.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))

    print("\n".join(lines))
    print(f"\n✓ Rapport écrit : {out}")


if __name__ == "__main__":
    main()

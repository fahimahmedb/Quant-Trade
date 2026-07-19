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
    w("la part du candidat de **continuité** (camp sortant ou héritier) au **2nd tour** de")
    w("l'élection présidentielle française dépend de quatre variables fondamentales :\n")

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

    w("## 5. Limitations honnêtes\n")
    w("⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :\n")
    w("")
    w("1. **Faiblesse du dataset** : n=11 élections seulement. Estimation Ridge (α=0.1) nécessaire pour")
    w("   régulariser, mais amplifie aussi le biais. Intervalle de confiance large.")
    w("")
    w("2. **2017 = réalignement partisan** : le modèle échoue à capturer le basculement 2016-2017")
    w("   (Macron émergent hors champ politique classique). Les fondamentaux seuls ne suffisent pas")
    w("   en cas de rupture systémique.")
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

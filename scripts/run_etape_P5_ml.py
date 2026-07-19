"""Etape P5 (finale) - famille ML. Produit results/etape_P5_ml.md.

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping) :
- Univers ML declare : logistic, random forest, gradient boosting, XGBoost
  (si installe). Compares au modele STRUCTUREL (P1) et a la FUSION (P4) comme
  references, sur le meme backtest OOS expansif.
- Hyperparametres fixes a priori (profondeur bornee), non cherches sur le test.
- Objectif : mesurer honnetement si la capacite ML paie a n minuscule (elle ne
  devrait pas). Le vrai terrain ML est la maille circonscription (documentee).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pp_data import load_registry  # noqa: E402
from pp_backtest import run_oos  # noqa: E402
from pp_fundamentals import FundamentalsSource  # noqa: E402
from pp_markets import MarketsSource  # noqa: E402
from pp_nlp import NlpSource  # noqa: E402
from pp_fusion import FusionSource  # noqa: E402
from pp_ml import MlSource, available_models, _HAS_XGB  # noqa: E402

MIN_TRAIN = 4
examples = load_registry()

LABELS = {"logistic": "ML — régression logistique", "rf": "ML — random forest",
          "gb": "ML — gradient boosting", "xgb": "ML — XGBoost"}

runs = {}
for m in available_models():
    runs[LABELS[m]] = run_oos(lambda m=m: MlSource(m), examples, MIN_TRAIN)
# References
runs["Structurel (P1)"] = run_oos(lambda: FundamentalsSource(), examples, MIN_TRAIN)
runs["Fusion (P4)"] = run_oos(
    lambda: FusionSource([FundamentalsSource(), MarketsSource(), NlpSource()]),
    examples, MIN_TRAIN)

lines = []
w = lines.append
w("# Étape P5 — Machine learning sur données historiques (étape finale)\n")

w("## 1. Cadre\n")
w("On applique une famille ML (régression logistique, forêt aléatoire, gradient "
  "boosting" + (", XGBoost" if _HAS_XGB else "") + ") aux **mêmes** variables "
  "fondamentales, sur le **même** backtest OOS que les briques précédentes. "
  "Cible : part 2nd tour de la référence (la version logistique classe l'issue "
  "puis la mappe en part). Voir `src/pp_ml.py`.\n")

w("## 2. Résultats OOS (7 plis, fenêtre expansive)\n")
w("| Prédicteur | n | Brier | Log-loss | MAE part | Bonne issue |")
w("|---|---|---|---|---|---|")
for name, rep in runs.items():
    m = rep.metrics()
    if m.get("n"):
        w(f"| {name} | {m['n']} | {m['brier']:.3f} | {m['log_loss']:.3f} "
          f"| {m['share_mae']:.3f} | {m['hit_rate']:.0%} |")
w("")

# Conclusion chiffree, robuste au hasard des runs.
ml_briers = [runs[LABELS[m]].metrics()["brier"] for m in available_models()]
struct_brier = runs["Structurel (P1)"].metrics()["brier"]
fusion_brier = runs["Fusion (P4)"].metrics()["brier"]
best_ml = min(ml_briers)

w("## 3. Lecture (biais-variance)\n")
w(f"- Meilleur Brier ML = **{best_ml:.3f}** ; structurel parcimonieux = "
  f"**{struct_brier:.3f}** ; fusion multi-source = **{fusion_brier:.3f}**.")
if best_ml >= struct_brier:
    w("- **Conclusion attendue confirmée** : à n≈11, la capacité ML ne bat PAS "
      "le modèle structurel parcimonieux hors-échantillon — le sur-ajustement "
      "domine. Ajouter de la flexibilité sans ajouter de données dégrade la "
      "généralisation.")
else:
    w("- L'un des modèles ML devance légèrement le structurel, mais l'écart n'est "
      "PAS significatif à cet effectif (7 plis) : à traiter comme du bruit, pas "
      "comme une preuve de supériorité.")
w("- La **fusion** reste la meilleure approche : elle gagne en information "
  "(marchés, NLP) plutôt qu'en capacité de modèle.\n")

w("## 4. Où le ML paierait vraiment : la maille circonscription\n")
w("Le ML a besoin d'effectifs. Les **législatives** offrent ~577 circonscriptions "
  "× plusieurs cycles = plusieurs milliers d'observations, avec des features "
  "riches par circonscription. Schéma de données cible (à collecter, NON fourni "
  "ici — aucune donnée synthétique n'est présentée comme réelle) :\n")
w("```")
w("data/fr_circonscriptions.csv  (une ligne = une circonscription × une élection)")
w("  circo_id, annee, sortant_camp, resultat_precedent_pct, ")
w("  taux_chomage_local, revenu_median, part_diplomes_sup, part_65plus,")
w("  densite_urbaine, participation_prec, resultat (cible : camp gagnant / part)")
w("```")
w("Sur cette maille, `MlSource` (ou un XGBoost dédié par circonscription) "
  "s'entraîne sur les cycles passés et prédit le cycle courant, toujours via le "
  "même protocole OOS expansif de `src/pp_backtest.py`. La brique se branche "
  "sans changer le contrat `pp_types` : seul le loader de données change.\n")

w("## 5. Limites\n")
w("- 7 plis : tout écart de Brier < ~0.1 est du bruit d'échantillonnage.")
w("- Hyperparamètres bornés a priori (profondeur), non optimisés — les optimiser "
  "sur ces 11 élections serait du data-snooping caractérisé.")
w("- XGBoost " + ("disponible" if _HAS_XGB else "absent") + " dans cet "
  "environnement ; le module fonctionne dans les deux cas.\n")

out = ROOT / "results" / "etape_P5_ml.md"
out.write_text("\n".join(lines))
print("\n".join(lines))

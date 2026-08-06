# Pré-enregistrement — Taux de défaut sur prêts automobiles US (overlay défensif)

**Committé AVANT tout calcul.** Cycle #287 du backlog non-ML.

## Hypothèse et PRÉDICTION EXPLICITE (Règle 2, déclarée avant tout calcul)

Le #286 (crédit carte, PASS net 4/5, déclencheur revenu/emploi COURT
terme) et le #288 (hypothécaire, FAIL 1/5, déclencheur cycle
immobilier/taux LONG terme) ont donné des résultats DIVERGENTS malgré
une construction et une méthodologie strictement identiques —
suggérant que la nature du déclencheur économique (court terme vs long
terme) détermine l'exploitabilité, pas la fréquence des données ni le
traitement causal.

Le prêt automobile (FRED `DRALACBN`) est, comme la carte de crédit,
une dette de consommation à déclencheur COURT terme : une perte
d'emploi ou un choc de revenu se traduit quasi immédiatement en défaut
de paiement automobile (contrairement à un prêt hypothécaire, où le
ménage épuise typiquement d'abord ses autres options avant de risquer
la saisie de son logement — "mortgage is the last bill you skip").

**PRÉDICTION EXPLICITE DÉCLARÉE ICI, AVANT TOUT CALCUL** : ce signal
devrait **PASSER comme le #286**, pas échouer comme le #288. Un
résultat contraire (FAIL) réfuterait l'hypothèse court-terme/long-terme
émergente, ce qui serait tout aussi informatif et sera rapporté
honnêtement.

## Données

Série FRED `DRALACBN` récupérée le jour même
(`data/auto_loan_delinquency_quarterly.csv`, TRIMESTRIELLE, 1985-2026,
165 observations, gratuite — historique plus long que #286/#288
puisque 1985 au lieu de 1991).

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7
STRICTE de la construction des #286/#288 — seule la série change)

- **Construction** : NIVEAU brut du taux de défaut (même convention
  que #199/#286/#288).
- **Décalage de publication** : même délai conservateur d'un trimestre
  calendaire complet (`DateOffset(months=3)`) que #286/#288.
- Alignement causal final : `ffill` + `shift(1)` sur le calendrier
  boursier.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `DRALACBN_lag(t-1)` est dans son tercile expanding le
  PLUS HAUT (défauts auto les plus élevés observés jusqu'à présent —
  direction cohérente avec #199/#286/#288), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_auto_loan_delinquency_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode prouvée correcte au
#203/#283-#288), vérification dédiée du décalage d'un trimestre,
anti-lookahead par troncature. Sortie :
`results/nonml_auto_loan_delinquency_overlay_result.md`.

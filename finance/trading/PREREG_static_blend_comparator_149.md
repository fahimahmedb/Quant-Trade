# Pré-enregistrement — comparateur statique actions/obligations vs #149

**Committé AVANT tout calcul.** Suite directe du document de déploiement
Voie A (`results/deploiement_voie_a_risk_management_134_149.md`, §2) —
PAS un nouveau cycle du backlog non-ML (pas de nouvelle ligne de backlog,
pas de nouvelle batterie Règle 9), une question de déploiement opérationnelle
distincte : "un simple blend statique actions/obligations capture-t-il déjà
l'essentiel du bénéfice de #149 ?".

## Motivation

La décomposition du #142 a montré que 89% du gain de Sharpe de #134 (même
mécanisme que #149, seuils de vol différents) vient du portage seul, pas
d'un timing prédictif. Si un simple mélange STATIQUE actions/obligations
(rebalancé pour maintenir un poids constant) capture déjà l'essentiel du
bénéfice, il doit être préféré en déploiement (moins de paramètres, moins
de surface de bug, même résultat économique) — principe de parcimonie déjà
énoncé dans le document de déploiement.

## Définition (fixée ici, avant tout résultat)

- **Poids statique = exposition moyenne réelle de #149** sur la période
  complète (calculée directement depuis `pos` dans
  `results/nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz`,
  PAS un chiffre choisi à la main) — pour isoler l'effet du TIMING dynamique
  seul, pas une différence de niveau de risque moyen entre les deux
  portefeuilles comparés.
- Rebalancement quotidien vers ce poids constant (cohérent avec le
  rebalancement implicite quotidien de l'overlay lui-même).
- Mêmes rendements sous-jacents (`r_asset`=NDX, `r_alt`=proxy obligataire)
  et mêmes coûts (5 bps, appliqués au turnover du rebalancement quotidien
  vers poids constant).
- Métriques comparées : Sharpe annualisé, rendement total net, MDD,
  Calmar — mêmes définitions que `trading_metrics()`
  (`finance/src/prediction.py`).

## Critère de succès (fixé ici)

- Si le blend statique atteint **Sharpe ≥ Sharpe(#149) − 0,05** (à moins
  d'1 point de Sharpe annualisé, seuil déjà fixé au §8.2 du document de
  déploiement) : le blend statique est **préféré** pour le déploiement.
- Sinon : le mécanisme dynamique (#149) apporte une valeur suffisante pour
  justifier sa complexité additionnelle, on continue avec le shadow-trading
  du dynamique tel que prévu au §5 du document de déploiement.

## Anti-cheat

n_trials=1 pour cette question précise (un seul poids statique testé, celui
mesuré directement depuis les données de #149, aucun autre poids essayé).
Ce fichier committé avant `nonml_static_blend_comparator_149.py`.

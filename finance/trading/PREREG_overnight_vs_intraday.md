# Pré-enregistrement — Stratégie "nuit seulement" (overnight vs intraday)

**Committé AVANT tout calcul.** Cycle #69 du backlog non-ML. Première
stratégie du backlog qui n'est pas un overlay de levier sur Buy&Hold,
mais une DÉCOMPOSITION du rendement quotidien en deux composantes
(nuit : clôture→ouverture du lendemain ; jour : ouverture→clôture) —
teste directement une anomalie de microstructure bien documentée dans
la littérature (Cliff et al. 2008, French 1980 sur les rendements
overnight vs intraday) : la quasi-totalité du rendement actions
proviendrait de la détention de nuit, pas de la détention intra-journée.

## Hypothèse

Une stratégie qui ne détient l'indice QUE pendant la nuit (achat à la
clôture du jour t, revente à l'ouverture du jour t+1, puis rachat le
soir même à la clôture du jour t+1, etc. — flat pendant les heures de
bourse) pourrait capter l'essentiel du rendement de Buy&Hold avec une
volatilité intra-journée en moins, mais au prix d'un coût de transaction
BEAUCOUP plus élevé (2 transactions par jour au lieu d'une seule à
l'entrée pour Buy&Hold). Le test consiste à vérifier si l'edge de
rendement brut (nuit) suffit à compenser ce coût de friction structurel.

## Définition (fixée ici, avant tout résultat)

- Décomposition exacte du rendement quotidien log :
  `r_nuit(t) = log(open(t+1) / close(t))` (clôture du jour t → ouverture
  du jour t+1) et `r_jour(t) = log(close(t+1) / open(t+1))` (ouverture du
  jour t+1 → clôture du jour t+1), avec `r_nuit(t) + r_jour(t) =
  r_BH(t) = log(close(t+1)/close(t))` exactement (identité comptable).
- Stratégie "nuit seulement" : position = 1,0x de la clôture du jour t à
  l'ouverture du jour t+1, position = 0,0x (flat) pendant la séance du
  jour t+1 — répété chaque jour. **2 transactions par jour** (vente à
  l'ouverture, rachat à la clôture), chacune à 5 bps.
- Référence : Buy & Hold classique (1,0x en permanence, coût unique à
  l'entrée).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition (identique au reste du backlog, mais appliqué 2x/jour ici
  au lieu d'une seule fois à l'entrée pour BH).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`), colonnes
`open`/`close` déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

La stratégie "nuit seulement" doit battre Buy & Hold **simultanément**
en Sharpe annualisé net de coûts ET en rendement total net de coûts, sur
**au moins 4 des 5 marchés**. n_trials=1 (aucun paramètre à régler — la
décomposition nuit/jour est une identité comptable exacte, pas un
signal calibré ; le coût de 5 bps est identique à tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant `nonml_overnight_vs_intraday_backtest.py`,
vérification via `nonml_anti_cheat_check.py overnight_vs_intraday`.

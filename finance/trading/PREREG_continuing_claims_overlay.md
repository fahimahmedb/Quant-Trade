# Pré-enregistrement — Demandes continues d'allocations chômage (FRED CCSA)

**Committé AVANT tout calcul.** Cycle #322 du backlog non-ML.

## Hypothèse

Les demandes CONTINUES d'allocations chômage (FRED `CCSA`, hebdomadaire
depuis 1967) mesurent le STOCK de chômeurs encore indemnisés — distinct
des demandes INITIALES déjà testées et FAIL (#204, `ICSA`), qui mesurent
le FLUX de nouveaux licenciements. Les demandes continues sont
documentées comme un indicateur de la PERSISTANCE/DURÉE du chômage : une
hausse signale que les personnes licenciées mettent plus de temps à
retrouver un emploi, un signal généralement considéré comme plus
tardif/confirmatoire qu'avant-coureur (contrairement aux demandes
initiales, souvent citées comme réactives en temps quasi-réel), mais
mesurant un concept économique authentiquement DIFFÉRENT (stock vs
flux). Jamais exploité dans ce backlog.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `CCSA` (gratuite, hebdomadaire,
1967-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/ccsa_weekly.csv`). Réutilisation intégrale de la construction
exacte du #204 (`ICSA`, seule série hebdomadaire déjà testée) : moyenne
mobile 4 semaines (`MA_WEEKS=4`), glissement annuel 52 semaines
(`YOY_WEEKS=52`), décalage de publication de 7 jours calendaires
(`PUBLICATION_LAG_DAYS=7`, marge conservatrice), tercile expanding le
plus HAUT (`expanding_tercile_cut_high`), `CUT=0,5x` défensif,
`COST_BPS=5,0` — toutes les constantes et la fonction de porte importées
directement de `nonml_jobless_claims_overlay_backtest.py` (Règle 7),
seule la série sous-jacente change.

## Définition (fixée ici, AVANT tout calcul)

- `ClaimsContinuingYoY(t)` = `log(MA4(t)/MA4(t-52))` sur `CCSA`.
- `GateClaims(t)` = 1 si `ClaimsContinuingYoY_lag(t-1)` (décalé de 7
  jours calendaires avant `ffill`+`shift(1)`) est dans son tercile
  expanding le plus HAUT (hausse de la persistance du chômage =
  défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GateClaims(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — persistance du chômage élevée =
défensif — pas de grille).

## Risque déclaré à l'avance

**Prédiction explicite testable** : étant donné que le #204 (ICSA,
construction identique) a échoué sur le RENDEMENT malgré un Sharpe
gagnant sur 2/5 marchés (indicateur documenté comme coïncident/tardif
plutôt qu'avant-coureur), et que les demandes CONTINUES sont
généralement documentées comme ENCORE PLUS tardives que les demandes
initiales (elles mesurent la persistance après le choc initial, pas le
choc lui-même), un résultat FAIL similaire ou pire (moins de marchés
gagnant même le Sharpe seul) est plausible. Rapporté honnêtement dans
tous les cas, sans retuning, que la prédiction se confirme ou non.
Comme pour toute la famille macro-externe défensive, le design purement
défensif sans amplification limite structurellement le gain de
rendement même si un régime de risque est correctement identifié.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de `data/ccsa_weekly.csv`
est une simple vérification de disponibilité, aucun résultat n'existe
avant ce commit). Sortie : `results/nonml_continuing_claims_overlay_result.md`.

# Pré-enregistrement — Leaders 52-semaines + overlay de vol-targeting continu, cible 20%

**Committé AVANT tout calcul.** Cycle #48 du backlog non-ML. Variante
corrigée du cycle #45 (Leaders + vol-targeting cible 15%, FAIL —
rendement insuffisant car exposition moyenne 0,91x). Le cycle #46 a
montré que relever la cible de vol à 20% (au lieu de 15%) referme
l'écart de rendement sur Buy&Hold ; ce cycle teste si le même ajustement
fonctionne aussi appliqué au portefeuille Leaders (edge positif) plutôt
qu'à un indice neutre.

## Hypothèse

Le #45 a échoué car l'exposition moyenne (calibrée sur une cible de
15%) restait sous 1.0x même sur un portefeuille à edge positif. En
utilisant la cible de 20% déjà validée sur Buy&Hold au #46 (plus proche
de la vol réalisée typique de ce portefeuille), l'exposition moyenne
devrait se rapprocher ou dépasser 1.0x, permettant de battre la
référence Leaders 1.0x en rendement tout en conservant un bénéfice de
MDD.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Leaders 52-semaines, IDENTIQUE au cycle #4
  (tercile supérieur par ratio prix/plus-haut-annuel, rebalancement
  21j, univers NDX-100 dynamique).
- Vol réalisée = écart-type des rendements log quotidiens DU
  PORTEFEUILLE LEADERS lui-même (pas de l'indice), fenêtre roulante de
  **20 séances**, annualisée (× √252), calcul causal identique au
  #43/#45/#46.
- Vol cible = **20% annualisé** (SEUL paramètre modifié par rapport au
  #45, qui utilisait 15% — cohérent avec le #46).
- Exposition globale(t) = **clip(vol_cible / vol_réalisée_leaders(t-1),
  0.0, CAP=2.0)**, appliquée comme multiplicateur sur les poids du
  portefeuille Leaders.
- **Coûts** : 5 bps par unité de turnover (rebalancement mensuel ET
  changements quotidiens de l'exposition).
- **Référence** : portefeuille Leaders 1.0x (cycle #4), PAS Buy&Hold —
  même convention que #11/#23/#33/#38/#39/#42/#45.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Leaders de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (vol cible 20%, fenêtre 20j et CAP=2.0x
identiques au #46, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_leaders_vol_targeting_20_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py leaders_vol_targeting_20_overlay`.

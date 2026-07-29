# Pré-enregistrement — Momentum de constance + overlay combiné tendance + vol-targeting

**Committé AVANT tout calcul.** Cycle #85 du backlog non-ML. Applique le
mécanisme hiérarchique déjà validé aux cycles #47 (Buy&Hold), #51
(Winners) et #53 (Low-Vol) au portefeuille Momentum de constance (#82),
déjà combiné au simple overlay binaire SMA200 au #83. Complète le
quatuor des constructions de portefeuille de base (Leaders #4→#47,
Winners #14→#51, Low-Vol #15→#53, Constance #82→#85) testées avec le
mécanisme le plus sophistiqué de la session.

## Hypothèse

Le simple overlay binaire SMA200 (#83, PASS) a déjà amélioré le
portefeuille momentum de constance (Sharpe +0,67→+0,90, rendement
+81,7%→+256,4%). Le mécanisme hiérarchique (#47/#51/#53) module
l'amplification par la vol réalisée DU PORTEFEUILLE LUI-MÊME plutôt
qu'un CAP fixe uniforme dès que la tendance est haussière — sur les
trois autres constructions de base déjà testées, ce calibrage plus fin
a systématiquement égalé ou battu le simple overlay binaire équivalent
(#47>#29 sur Buy&Hold, #51>#42 sur Winners, #53≈#35 sur Low-Vol).
L'hypothèse ici est que ce résultat se généralise à une quatrième
construction de portefeuille (momentum de constance), complétant la
matrice.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Momentum de constance, IDENTIQUE au cycle #82
  (tercile supérieur de fraction de mois positifs sur 12 blocs de 21j,
  rebalancement 21j, univers NDX-100 dynamique).
- Signal de tendance = indice NDX-100 (`data/nasdaq100_daily.txt`)
  au-dessus de sa moyenne mobile 200j (SMA200, IDENTIQUE au #29/#83),
  aligné causalement (ffill) sur le calendrier du portefeuille.
- Vol réalisée = écart-type des rendements log quotidiens DU
  PORTEFEUILLE MOMENTUM DE CONSTANCE lui-même (pas de l'indice), fenêtre
  roulante de 20 séances, annualisée, calcul causal identique au
  #39/#47/#51/#53.
- Vol cible = **20% annualisé**, identique au #46/#47/#48/#51/#53.
- Position globale(t) :
  - si tendance haussière (SMA200) : **clip(vol_cible /
    vol_réalisée_constance(t-1), 1.0, CAP=2.0)** (jamais en-dessous de
    1.0x, identique à la logique du #47/#51/#53).
  - sinon : **1.0x**.
- **Coûts** : 5 bps par unité de turnover (rebalancement mensuel ET
  changements quotidiens de l'exposition).
- **Référence** : portefeuille Momentum de constance 1.0x (cycle #82),
  PAS Buy&Hold — même convention que #11/#23/#33/#35/#38/#39/#42/#45/
  #48/#51/#53/#83.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour le signal de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Momentum de constance de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (tous les paramètres repris identiques aux
#29/#46/#47/#51/#53/#82/#83, aucune grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grilles de perturbation non-tunables identiques aux #47/#51/#53 :
CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et fenêtre de vol réalisée ∈ {15j, 20j,
25j, 30j} — vérifie un plateau plutôt qu'un pic isolé sur le CAP=2.0x /
fenêtre=20j pré-enregistrés.

## Anti-cheat

Ce fichier committé avant
`nonml_momentum_consistency_trend_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
momentum_consistency_trend_vol_targeting_overlay`.

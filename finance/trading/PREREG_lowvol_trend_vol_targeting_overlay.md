# Pré-enregistrement — Low-Volatility Tilt + overlay combiné tendance + vol-targeting

**Committé AVANT tout calcul.** Cycle #53 du backlog non-ML. Applique le
mécanisme hiérarchique déjà validé aux cycles #47 (Buy&Hold) et #51
(Winners) au portefeuille Low-Volatility Tilt (#15) — complète le trio
des portefeuilles de base (Leaders #4, Winners #14, Low-Vol #15) testés
avec le meilleur mécanisme de la session (tendance + vol-targeting
hiérarchique, floor à 1.0x).

## Hypothèse

Le simple overlay binaire tendance seule (#35, PASS) a déjà amélioré le
Low-Vol Sharpe (+0,54→+0,79) en préservant bien le MDD. Le mécanisme
hiérarchique (#47/#51) module l'amplification par la vol réalisée
plutôt qu'un CAP fixe uniforme — sur un portefeuille DÉJÀ construit pour
minimiser sa propre volatilité (Low-Vol), cette modulation fine pourrait
offrir un calibrage encore plus précis de l'exposition, potentiellement
un meilleur ratio gain/MDD que le #35.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Low-Volatility Tilt, IDENTIQUE au cycle #15
  (tercile inférieur de volatilité réalisée 60j, rebalancement 21j,
  univers NDX-100 dynamique).
- Signal de tendance = indice NDX-100 (`data/nasdaq100_daily.txt`) dont
  la clôture est ≥95% de son plus haut glissant 252j (identique au
  #37/#39), aligné causalement (ffill) sur le calendrier du portefeuille.
- Vol réalisée = écart-type des rendements log quotidiens DU
  PORTEFEUILLE LOW-VOL lui-même (pas de l'indice), fenêtre roulante de
  20 séances, annualisée, calcul causal identique au #39/#47/#51.
- Vol cible = **20% annualisé**, identique au #46/#47/#48/#51.
- Position globale(t) :
  - si tendance haussière : **clip(vol_cible / vol_réalisée_lowvol(t-1),
    1.0, CAP=2.0)** (jamais en-dessous de 1.0x, identique à la logique
    du #47/#51).
  - sinon : **1.0x**.
- **Coûts** : 5 bps par unité de turnover (rebalancement mensuel ET
  changements quotidiens de l'exposition).
- **Référence** : portefeuille Low-Vol 1.0x (cycle #15), PAS Buy&Hold —
  même convention que #11/#23/#33/#35/#38/#39/#42/#45/#48/#51.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour le signal de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Low-Vol de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (tous les paramètres repris identiques aux
#37/#39/#46/#47/#51, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_lowvol_trend_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py lowvol_trend_vol_targeting_overlay`.

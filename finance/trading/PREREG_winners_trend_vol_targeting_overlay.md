# Pré-enregistrement — Winners momentum court terme + overlay combiné tendance + vol-targeting

**Committé AVANT tout calcul.** Cycle #51 du backlog non-ML. Applique le
mécanisme hiérarchique déjà validé au #47 (tendance indice + vol-targeting,
floor à 1.0x) au portefeuille Winners (#14, prudence forte) plutôt qu'à
Buy&Hold — remplace le simple overlay binaire déjà testé au #42 (PASS,
mais mécanisme plus fruste) par le mécanisme le plus sophistiqué de la
session.

## Hypothèse

Le #42 (overlay binaire tendance seule sur Winners) a déjà amélioré
l'edge extrême du #14 (Sharpe +2,35→+3,00). Le mécanisme hiérarchique du
#47 module l'amplification par la vol réalisée plutôt qu'un CAP fixe
uniforme — appliqué au portefeuille Winners, il pourrait offrir un
ajustement plus fin de l'exposition (moins de levier quand la vol du
portefeuille momentum est déjà élevée, plus de levier quand elle est
modérée), potentiellement un meilleur ratio gain/MDD que le #42.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Winners momentum court terme, IDENTIQUE au
  cycle #14 (signal = rendement 5j, tercile supérieur, rebalancement
  hebdomadaire, univers NDX-100 dynamique).
- Signal de tendance = indice NDX-100 (`data/nasdaq100_daily.txt`) dont
  la clôture est ≥95% de son plus haut glissant 252j (identique au
  #37/#42), aligné causalement (ffill) sur le calendrier du portefeuille.
- Vol réalisée = écart-type des rendements log quotidiens DU
  PORTEFEUILLE WINNERS lui-même (pas de l'indice), fenêtre roulante de
  20 séances, annualisée, calcul causal identique au #45/#48.
- Vol cible = **20% annualisé**, identique au #46/#47/#48.
- Position globale(t) :
  - si tendance haussière : **clip(vol_cible / vol_réalisée_winners(t-1),
    1.0, CAP=2.0)** (jamais en-dessous de 1.0x, identique à la logique
    du #47).
  - sinon : **1.0x**.
- **Coûts** : 5 bps par unité de turnover (rebalancement hebdomadaire ET
  changements quotidiens de l'exposition).
- **Référence** : portefeuille Winners 1.0x (cycle #14), PAS Buy&Hold —
  même convention que #11/#18/#23/#33/#38/#39/#42/#45/#48.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`) pour le portefeuille,
`data/nasdaq100_daily.txt` pour le signal de tendance indice.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Winners de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (tous les paramètres repris identiques aux
#37/#46/#47, aucune grille testée avant ce résultat). **Prudence
maintenue** : même en cas de PASS, le résultat hérite de la même mise en
garde que le #14/#42 (généralisabilité incertaine hors du bull market
2021-2026 échantillonné).

## Anti-cheat

Ce fichier committé avant
`nonml_winners_trend_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py winners_trend_vol_targeting_overlay`.

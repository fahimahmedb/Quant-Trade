# Pré-enregistrement — Overlay vol-targeting gaté par la dispersion cross-sectionnelle NDX-100

**Committé AVANT tout calcul.** Cycle #78 du backlog non-ML. Nouveau
type de signal de porte, jamais testé dans ce backlog : la dispersion
CROSS-SECTIONNELLE des rendements quotidiens (écart-type des rendements
du jour à travers les 99 titres NDX-100), distincte de toutes les portes
précédentes qui utilisaient soit un signal de PRIX (tendance, niveau,
pente), soit un signal CALENDAIRE, soit la volatilité TEMPORELLE d'une
seule série (#58, FAIL, non-directionnel).

## Hypothèse

Une forte dispersion cross-sectionnelle (les titres évoluent de façon
très différenciée le même jour) signale un marché où les fondamentaux
individuels dominent — littérature du "stock-picker's market" — par
opposition à une faible dispersion où tous les titres bougent en bloc
(souvent un marché dirigé par le sentiment macro/la liquidité globale,
plus fragile). Gater le vol-targeting de l'indice par un régime de
dispersion élevée pourrait capter un edge distinct des portes de
tendance déjà testées, motivé par un mécanisme économique différent.

## Définition (fixée ici, avant tout résultat)

- Pour chaque jour t, Dispersion(t) = écart-type cross-sectionnel des
  rendements log quotidiens des titres NDX-100 cotés ce jour-là (au
  moins 10 titres listés, sinon NaN).
- Médiane de référence = médiane glissante de Dispersion sur
  `MEDIAN_WINDOW=252` jours (identique en principe au #58, mais
  appliquée à la dispersion cross-sectionnelle et non à la vol
  temporelle d'une série unique).
- Porte = Dispersion(t) ≥ médiane glissante de Dispersion (régime de
  dispersion ÉLEVÉE, au-dessus de sa propre norme récente).
- Quand la porte est active : position sur l'indice NDX-100 = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%**, **CAP = 2,0x**,
  fenêtre de vol **VOL_WINDOW=20j** (paramètres identiques au
  #46/#47/#57/#77, aucun retuning).
- Quand la porte est inactive : position = **1,0x**.
- Alignement causal : Dispersion(t) et sa médiane sont calculées sur le
  calendrier des tickers (UNION), alignées sur le calendrier de l'indice
  NDX-100 par ffill (jamais de donnée future).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique sur NDX-100.

## Univers et période

`data/pead/prices/*.json` (titres NDX-100, pour la dispersion) et
`data/nasdaq100_daily.txt` (indice, pour le rendement testé), déjà en
local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold (NDX) **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts. Un seul
marché testé (NDX), comme au #77 (signal dérivé des constituants
NDX-100). n_trials=1 (MEDIAN_WINDOW=252j et paramètres vol-targeting
repris à l'identique des cycles validés, aucune grille testée avant ce
résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_dispersion_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py dispersion_vol_targeting_overlay`.

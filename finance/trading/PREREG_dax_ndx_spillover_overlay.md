# Pré-enregistrement — Spillover cross-marché DAX→NDX

**Committé AVANT tout calcul.** Cycle #110 du backlog non-ML.

## Hypothèse

Toutes les confirmations multi-marché déjà testées (#52, #57, #103)
exigent un alignement SIMULTANÉ (les deux/cinq marchés en tendance
haussière EN MÊME TEMPS). Ce cycle teste une relation de LEAD-LAG
DÉCALÉE, jamais exploitée dans ce backlog : la Bourse de Francfort
(DAX) clôture en fin d'après-midi européenne, systématiquement AVANT
l'ouverture de la séance américaine (NDX) du même jour calendaire. Le
rendement du DAX au jour t est donc entièrement connu avant que la
séance NDX du jour t ne commence — une information disponible ex ante,
pas une fuite. L'hypothèse est qu'un rendement DAX positif au jour t
signale un momentum global favorable qui se propage à l'ouverture/la
séance américaine du même jour.

## Définition (fixée ici, avant tout résultat)

- Marchés : NDX (`nasdaq100_daily.txt`, marché piloté) et DAX
  (`dax_daily.txt`, signal leading), les deux déjà en local.
- Alignement causal explicite : `dax_ret(t) = close_DAX(t) /
  close_DAX(t-1) - 1` est connu à la clôture européenne du jour
  calendaire t, AVANT l'ouverture de la séance NDX du même jour t (pas
  de décalage `[:-1]` nécessaire ici — c'est la séquence Europe-avant-
  US qui rend le signal causal, pas un lag artificiel).
- Alignement calendaire : dates communes aux deux séries (intersection
  stricte des jours de bourse NDX et DAX, pas de `ffill` — un jour sans
  séance DAX correspondante laisse la porte à son état par défaut
  1.0x).
- Porte active si `dax_ret(t) > 0` (rendement DAX strictement positif
  le jour calendaire t).
- Position : **CAP=2.0x** les jours de porte active (appliqué au
  rendement NDX du MÊME jour calendaire t), **1.0x** sinon.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX.

## Univers et période

`data/nasdaq100_daily.txt` et `data/dax_daily.txt`, déjà en local.
Intersection des dates de bourse communes.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold (NDX) **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts. Test sur une
seule paire de marchés (DAX→NDX, pas un test multi-marché) : le
critère est donc simplement le PASS/FAIL de cette paire, pas un seuil
de type ≥4/5. n_trials=1 (CAP=2.0x identique à la famille, aucune
grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant `nonml_dax_ndx_spillover_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py dax_ndx_spillover_overlay`.

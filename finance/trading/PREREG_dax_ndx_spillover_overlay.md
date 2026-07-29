# Pré-enregistrement — Spillover cross-marché DAX→NDX

**Committé AVANT tout calcul.** Cycle #110 du backlog non-ML.

## CORRECTION (avant tout calcul committé, bug de fuseau horaire trouvé au premier essai)

La version initiale de ce fichier affirmait que "le DAX clôture avant
l'ouverture NDX du même jour calendaire", ce qui est **factuellement
FAUX** : le Xetra (DAX) ouvre ~09:00 CET et clôture ~17:30 CET ; le
Nasdaq (NDX) ouvre 09:30 ET, soit ~15:30 CET — le DAX est donc ENCORE
OUVERT quand NDX ouvre, sa clôture du jour t tombe PENDANT la séance
NDX du jour t, pas avant. Utiliser `dax_ret(t)` pour gater le rendement
NDX du MÊME jour t constituait donc une fuite partielle (chevauchement
horaire), détectée dès la première exécution (résultat aberrant :
rendement de l'ordre de 10¹¹%, bien au-delà de tout résultat plausible
de ce backlog — signal d'alerte immédiat). **Aucun résultat n'a été
committé avec la version buguée.** Correction : le signal utilisé est
désormais le rendement DAX du jour **t-1** (jour de bourse précédent,
strictement antérieur, sans ambiguïté de fuseau horaire possible) pour
gater le rendement NDX du jour t — définition ci-dessous mise à jour en
conséquence.

## Hypothèse

Toutes les confirmations multi-marché déjà testées (#52, #57, #103)
exigent un alignement SIMULTANÉ (les deux/cinq marchés en tendance
haussière EN MÊME TEMPS). Ce cycle teste une relation de LEAD-LAG
DÉCALÉE, jamais exploitée dans ce backlog : la Bourse de Francfort
(DAX) clôture en fin d'après-midi européenne, systématiquement AVANT
l'ouverture de la séance américaine (NDX) du même jour calendaire. Le
rendement du DAX au jour t est donc entièrement connu avant que la
séance NDX du jour t ne commence — une information disponible ex ante,
pas une fuite. L'hypothèse est qu'un rendement DAX positif à la clôture de la veille
signale un momentum global favorable qui se propage à la séance
américaine du lendemain.

## Définition (fixée ici, avant tout résultat — CORRIGÉE, voir note ci-dessus)

- Marchés : NDX (`nasdaq100_daily.txt`, marché piloté) et DAX
  (`dax_daily.txt`, signal leading), les deux déjà en local.
- Alignement causal explicite : `dax_ret(t-1) = close_DAX(t-1) /
  close_DAX(t-2) - 1` (rendement du jour de bourse PRÉCÉDENT, connu
  sans ambiguïté avant l'ouverture NDX du jour t, quel que soit le
  fuseau horaire).
- Alignement calendaire : dates communes aux deux séries (intersection
  stricte des jours de bourse NDX et DAX, pas de `ffill` — un jour sans
  séance DAX correspondante laisse la porte à son état par défaut
  1.0x).
- Porte active si `dax_ret(t-1) > 0` (rendement DAX strictement positif
  la séance de bourse précédente).
- Position : **CAP=2.0x** les jours de porte active (appliqué au
  rendement NDX du jour t, décidé sur la base du DAX de t-1), **1.0x**
  sinon.
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

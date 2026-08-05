# Pré-enregistrement — Tilt Amihud illiquidité (nouvelle exploitation de la donnée volume)

**Committé AVANT tout calcul.** Cycle #261 du backlog non-ML.

## Motivation

Le #258 (momentum 12-1 + double-tri turnover, Lee & Swaminathan 2000) a
validé l'exploitation du volume comme nouvelle catégorie de données dans
ce backlog (`data/pead/volume/*.json`, récupéré au #258 via
`scripts/fetch_volume_data.py`). Ce cycle teste une **seconde hypothèse
académique, mécaniquement DISTINCTE**, exploitant la même donnée :
la **prime d'illiquidité d'Amihud** (Amihud 2002, *"Illiquidity and
stock returns: cross-section and time-series effects"*, Journal of
Financial Markets) — les titres les plus illiquides (impact-prix élevé
pour un volume donné) offrent un rendement espéré supérieur, en
compensation du risque de liquidité. Mécanisme économique différent de
Lee & Swaminathan (prime de risque de liquidité, pas continuation de
momentum par sous-couverture des investisseurs) — **déclaré explicitement
comme la DERNIÈRE hypothèse volume testée dans ce cycle isolé, pas le
début d'une recherche systématique sur toutes les constructions
volume possibles** (Règle 2 : 2 hypothèses volume comptées, #258 et
#261).

## Univers et données

`data/pead/prices/*.json` + `data/pead/volume/*.json` (mêmes 99 tickers
que #258, aucune nouvelle donnée à récupérer).

## Construction (mesure standard Amihud, causale dès le départ)

Pour chaque titre i et jour d : `ILLIQ_i,d = |r_i,d| / dollar_volume_i,d`
(`dollar_volume = close × volume`). Signal au jour t :
`ILLIQ_i(t) = moyenne glissante de ILLIQ_i,d sur ILLIQ_WINDOW=126j`
(fenêtre identique au #258, Règle 7 — pas une donnée nouvelle à
justifier séparément). Rebalancement mensuel (`REBAL_EVERY=21`, hérité).
Sélection du **tercile le PLUS illiquide** (ILLIQ le plus élevé),
poids égaux. **Convention causale appliquée dès la construction**
(`lag_one_day` sur les poids finaux, pas une correction a posteriori —
leçon du balayage #252-260).

## Référence et critère de succès (renforcé, identique au #4/#73/#78/#82)

Référence = **Buy&Hold équipondéré de l'univers éligible** (même
construction que #4/#73/#78/#82 — PAS le double-tri turnover du #258,
mécanisme différent, comparaison directe non pertinente). PASS si Sharpe
tilt > Sharpe référence ET rendement total net > rendement référence.

## Risques déclarés à l'avance

1. Par précédent proche (#75 momentum 52w-low FAIL, #79 double-tri
   momentum+lowvol FAIL, #84 skewness FAIL) : les tilts contrarian/
   défensifs qui évitent les caractéristiques des gagnants à fort
   momentum ont systématiquement sous-performé sur cet échantillon bull
   market 2021-2026 dans ce backlog — aucune garantie que la prime
   d'illiquidité, documentée sur longue période multi-cycles, survive
   sur cette fenêtre courte et haussière.
2. Les titres NDX-100 sont par construction les plus grandes/liquides
   capitalisations du marché américain — la variation d'illiquidité au
   sein de cet univers est structurellement faible comparée aux études
   originales d'Amihud (univers NYSE/AMEX complet incluant micro-caps) ;
   limite reconnue à l'avance, pas un prétexte a posteriori.
3. Aucune garantie de robustesse sur la fenêtre ILLIQ_WINDOW — testée en
   grille de plausibilité seulement si PASS (Règle anti-snooping).

## Anti-cheat

Ce fichier committé et poussé AVANT tout calcul. Sortie attendue :
`results/nonml_amihud_illiquidity_tilt_result.md`. Script :
`scripts/nonml_amihud_illiquidity_tilt_backtest.py`.

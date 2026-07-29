# Pré-enregistrement — Proximité du plus BAS 52-semaines (tilt contrarian/value)

**Committé AVANT tout calcul.** Cycle #75 du backlog non-ML. Signal
strictement inverse du #4/#37 (proximité du plus HAUT 52-semaines,
momentum) : ici sélection des titres les plus proches de leur plus BAS
annuel, un tilt contrarian/value classique (De Bondt & Thaler 1985,
"overreaction hypothesis" — les titres les plus dépréciés sur longue
période tendent à sur-performer par la suite, contrairement aux
signaux de retournement à COURT terme déjà testés et systématiquement
échoués dans ce backlog, #13/#22/#24/#55/#62).

## Hypothèse

Un titre proche de son plus bas annuel a subi une dépréciation prolongée
(12 mois) — contrairement aux chocs de prix à court terme (2-20j) qui
signalent souvent un marché en stress continu (#22, #55, #62, tous
FAIL), un creux de LONG terme pourrait signaler une survente durable et
un potentiel de retournement (littérature du "long-term reversal", De
Bondt & Thaler 1985, distincte du momentum à 12 mois qui va dans le sens
opposé). Sélectionner le tercile de titres les plus proches de leur
plus bas 52-semaines, rebalancé mensuellement, pourrait battre un
portefeuille équipondéré Buy&Hold sur le même univers.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés localement
  (`data/pead/prices/*.json`), identique au #4/#14/#73.
- Signal au jour t : `ratio_low(t) = close(t) / plus_bas_glissant_252j(t)`
  (toujours ≥1, minimal quand le titre est exactement à son plus bas).
- Rebalancement tous les **REBAL_EVERY=21** jours (mensuel, identique au
  #4), sélection du tercile avec le `ratio_low` le PLUS FAIBLE (titres
  les plus proches de leur plus bas), équipondération au sein du
  tercile.
- Référence : portefeuille équipondéré Buy&Hold sur le même univers
  (identique à la référence du #4/#73).
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement.
- Calendrier de référence = UNION des dates de cotation (même correction
  de bug documentée au #4).

## Univers et période

`data/pead/prices/*.json` (titres NDX-100), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille "proximité du plus bas 52-semaines" doit battre le
Buy&Hold équipondéré **simultanément** en Sharpe annualisé net de coûts
ET en rendement total net de coûts. n_trials=1 (LOOKBACK=252,
REBAL_EVERY=21 et tercile fixés a priori par symétrie directe avec le
#4, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_momentum_52w_low_backtest.py`,
vérification via `nonml_anti_cheat_check.py momentum_52w_low`.

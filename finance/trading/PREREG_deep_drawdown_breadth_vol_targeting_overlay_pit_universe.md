# Pré-enregistrement — breadth de drawdown profond, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Le cycle #395 a établi que 3 PASS sur 6 testés basculent en FAIL lorsqu'on
remplace l'univers de titres « liste NDX-100 de 2026 » par l'univers
**point-in-time** réel, et qu'aucun ne s'améliore. Quinze PASS restent exposés
sans vérification. `deep_drawdown_breadth_vol_targeting_overlay` est le premier
de cette liste.

## Particularité de ce candidat — à lire avant d'interpréter

Contrairement à `amihud_illiquidity_tilt` (#394), **le P&L de cette stratégie
n'est pas un panier de titres** : c'est un overlay d'exposition sur l'indice NDX
(`pnl_ov = pos * bh_full`, `bh_full` = rendement log du NDX). L'univers de titres
ne sert qu'à **construire le signal** — la breadth, c'est-à-dire la fraction de
titres en drawdown profond.

Le biais du survivant agit donc ici sur **le signal**, non sur la mesure de
performance. La prédiction n'est pas la même que pour un portefeuille :

- pour un **portefeuille** (cas #394), le biais gonfle directement le rendement ;
- pour une **breadth de signal**, il déforme le comptage. Une liste composée de
  survivants sous-estime la proportion de titres en drawdown profond aux dates
  anciennes, puisque les titres réellement sinistrés à l'époque — et sortis de
  l'indice depuis — sont absents du dénominateur comme du numérateur.

**Prédiction non tranchée à l'avance.** Le sens de l'effet sur le verdict final
n'est pas déductible : il dépend de la façon dont la déformation du signal se
propage à travers la porte et le vol-targeting. Je ne prédis donc rien, et je
consigne ce point ici précisément pour ne pas pouvoir rationaliser le résultat
après coup.

## Hypothèse testée

Le verdict PASS de `deep_drawdown_breadth_vol_targeting_overlay` est-il conservé
lorsque la breadth est calculée sur l'univers d'appartenance **réel à chaque
date** au lieu de la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique du script d'origine :

| Paramètre | Valeur |
|---|---|
| `DD_THRESHOLD` | 0,80 (drawdown ≥ 20 % sous le plus haut glissant 252j) |
| `MEDIAN_WINDOW` | 252 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `CAP` | 2,0 |
| `COST_BPS` | 5,0 |

**Seul changement :** `PRICES_DIR` (`data/pead/prices/`, liste 2026) devient
`PRICES_PIT_DIR` (`data/pead/prices_pit/`), et l'appartenance à chaque date est
résolue par `ndx100_membership.tickers_as_of_date`, exactement comme dans les
7 variantes `*_pit_universe` déjà committées.

## Univers et période

- **Signal** : titres NDX-100 point-in-time, `data/pead/prices_pit/`
  (214 tickers disponibles, historique depuis 2005).
- **P&L** : NDX (`data/nasdaq100_daily.txt`), inchangé.
- **Période** : celle que l'intersection des données rend testable, rapportée
  telle quelle dans le résultat. Aucune fenêtre n'est choisie a posteriori.

## Critère de succès — IDENTIQUE à l'original

Critère renforcé : l'overlay doit battre Buy & Hold **en Sharpe annualisé ET en
rendement total**, net de coûts.

- **PASS** : les deux jambes atteintes.
- **FAIL** : au moins une jambe manquée.

Aucun seuil n'est ajusté. `n_trials = 1` : une hypothèse, une exécution, verdict
rapporté tel quel y compris si FAIL.

## Engagements

1. Résultat rapporté **tel quel**, PASS ou FAIL, sans réexécution après lecture.
2. Aucun retuning : si le résultat est FAIL, l'entrée est close, pas réajustée.
3. Un audit à recalcul indépendant accompagne le backtest.
4. Le résultat ne remplace pas celui de l'original : les deux coexistent, comme
   pour les 7 paires existantes.

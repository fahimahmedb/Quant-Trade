# Pré-enregistrement — Rebalancement hebdomadaire du portefeuille volatility-managed GJR-t (#165), correction ciblée de l'échec au stress de coûts

**Committé AVANT tout calcul.** Cycle #167 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Ce que corrige ce cycle, et ce qu'il NE corrige PAS (honnêteté préalable)

La batterie Règle 9 du #165 (`results/nonml_volatility_managed_portfolio_gjr_pass_validation_battery.md`)
donne **2/5**, pas 4/5 ou 5/5 :

| Contrôle | Verdict #165 |
|---|---|
| a. Stress de coûts (5/15/25 bps) | **ÉCHEC** à 25 bps (rendement +3200,4% < BH +4544,0%) |
| b. Stress de crise (MDD vs BH) | OK |
| c. Stabilité temporelle (4 folds) | OK (3/4) |
| d. SPA à 1 candidat vs BH | **ÉCHEC** (p=1,0000) |
| e. DSR (n_trials=taille backlog) | **ÉCHEC** (DSR≈0,0004) |

Le libellé de la ligne #167 du backlog ("le seul contrôle qui a échoué de
peu") est **imprécis** : 3 contrôles sur 5 échouent, pas 1. Ce cycle,
reprenant exactement la méthode du #154 (rebalancement hebdomadaire pour
corriger la fissure coûts du #151), ne s'attaque **qu'au contrôle (a)** —
c'est un test isolé sur le contrôle qui a une chance raisonnable d'être
corrigé par une réduction de turnover (un coût de transaction plus faible
change mécaniquement le résultat au stress de coûts). Les contrôles (d)
et (e) sont des limites STRUCTURELLES (significativité statistique
insuffisante sur l'échantillon disponible ; barre DSR proportionnelle au
nombre d'essais du backlog) — **aucune réduction de turnover ne peut les
corriger**, et ce cycle ne prétend pas le contraire. Même en cas de succès
total sur (a), le score Règle 9 passera au mieux de 2/5 à 3/5, jamais à un
"PASS renforcé" (qui exige les 5).

## 2. Marché et échantillon (figés)

NDX uniquement (`data/nasdaq100_daily.txt`), même fenêtre OOS que le #165
(t ≥ 750, 9522 séances). Aucune nouvelle donnée.

## 3. Mécanisme (figé, réutilisation stricte de la Règle 7)

Réutilisation EXACTE de la technique du #154
(`scripts/nonml_cash_rate_correction_44_weekly_rebalance_backtest.py::weekly_hold_position`) :
la position quotidienne du #165 (`position(t) = clip(20% / vol_prévue_GJR-t(t), 0, 2.0x)`,
inchangée) est échantillonnée tous les `REBAL_FREQ = 5` jours (le jour t où
`t % 5 == 0`) et maintenue constante entre deux rebalancements — **aucun
recalcul de la vol prévue au rythme hebdomadaire, aucun retuning du signal
sous-jacent**, seule la fréquence d'APPLICATION de la position déjà
calculée change. `REBAL_FREQ = 5` est choisi par cohérence directe avec le
#154 (même valeur, même justification : semaine de bourse), pas testé
contre d'autres fréquences dans ce cycle (une grille de fréquences est
prévue en robustesse au §5, PAS un retuning).

## 4. Critère de succès (figé)

> **PASS si et seulement si** le contrôle (a) de la batterie Règle 9
> (stress de coûts à 25 bps) réussit avec la position hebdomadaire, ALORS
> qu'il échouait avec la position quotidienne — ET que Sharpe(hebdo) et
> rendement(hebdo) à 5 bps restent > Buy & Hold (ne pas dégrader le
> verdict de niveau 1 déjà obtenu au #165 pour gagner sur les coûts).

**n_trials = 1** (une fréquence, une correction ciblée, pas de balayage
pour le verdict).

## 5. Si PASS : robustesse et suites

Grille de fréquences {3j, 5j, 10j, 21j} pour vérifier un plateau (pas un
retuning — le verdict reste celui de REBAL_FREQ=5). Ré-exécution complète
de la batterie Règle 9 (5 contrôles) sur la position hebdomadaire pour
obtenir le score final réel (attendu : 3/5, (d) et (e) resteront en échec
par construction, cf. §1). Simulation 300€ sur les ~3 derniers mois.

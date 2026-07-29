# Pré-enregistrement — Momentum de constance + overlay hiérarchique trend+vol-targeting, cible 15%

**Committé AVANT tout calcul.** Cycle #88 du backlog non-ML. Reprend
EXACTEMENT le mécanisme du #85 (FAIL) appliqué au momentum de constance
(#82), en changeant UN SEUL paramètre fixé a priori dans une nouvelle
hypothèse distincte : la vol CIBLE annualisée, abaissée à 15% au lieu de
20%. Ce n'est PAS un retuning du #85 (aucun résultat du #85 n'a été
"corrigé" — le #85 reste documenté FAIL tel quel) : c'est une nouvelle
hypothèse explicative pré-enregistrée séparément, symétrique du
raisonnement #43→#46 (le #43, FAIL, avait une cible 15% jugée
insuffisante ; le #46, PASS, relevait la cible à 20% pour corriger un
sous-dimensionnement systématique). Ici le problème est inverse : le
#85 a montré (audit) que l'exposition moyenne du mécanisme hiérarchique
sur le momentum de constance restait faible (1,17x, plancher actif
54,6% du temps) car la vol propre du portefeuille est souvent déjà
proche ou sous la cible de 20% — une cible PLUS BASSE (15%) devrait
mécaniquement réduire encore le nombre de jours où
`vol_cible/vol_réalisée > 1`, ce qui semble aller dans le sens opposé
de ce qui aiderait. L'hypothèse testée ici est donc explicitement
`OUVERTE` : elle peut confirmer que réduire encore la cible aggrave le
FAIL (résultat négatif attendu mais rapporté honnêtement), ou révéler
un effet non-monotone (la modulation devient plus fréquente donc plus
souvent active mais à une amplitude par transaction différente).
Aucune attente de PASS n'est déclarée a priori — le test est exécuté
et rapporté tel quel, quel que soit le sens du résultat.

## Définition (fixée ici, avant tout résultat)

- IDENTIQUE au #85 en tout point SAUF :
  - **Vol cible = 15% annualisé** (au lieu de 20%).
- Portefeuille de base = Momentum de constance, IDENTIQUE au cycle #82.
- Signal de tendance = indice NDX-100 au-dessus de sa SMA200,
  IDENTIQUE au #29/#83/#85.
- Vol réalisée = écart-type des rendements log quotidiens DU
  PORTEFEUILLE MOMENTUM DE CONSTANCE lui-même, fenêtre roulante 20j,
  annualisée, IDENTIQUE au #85.
- Position globale(t) :
  - si tendance haussière : **clip(0.15 / vol_réalisée_constance(t-1),
    1.0, CAP=2.0)**.
  - sinon : **1.0x**.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : portefeuille Momentum de constance 1.0x (cycle #82),
  IDENTIQUE au #85.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Momentum de constance de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (seule la cible de vol change vs #85, 15% fixé
ici a priori, aucune grille testée avant ce résultat — la grille de
robustesse habituelle porte sur le CAP, pas sur la cible elle-même qui
est le paramètre au cœur de cette hypothèse).

## Anti-cheat

Ce fichier committé avant
`nonml_momentum_consistency_trend_vol_targeting_15_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
momentum_consistency_trend_vol_targeting_15_overlay`.

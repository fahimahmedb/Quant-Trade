# Pré-enregistrement — Overlay levé croisement MACD

**Committé AVANT tout calcul.** Cycle #36 du backlog non-ML. Signal de
tendance technique distinct des moyennes mobiles simples déjà testées
(#29 prix/SMA200, #34 Golden Cross) : le MACD (Moving Average
Convergence Divergence, Appel 1979), paramètres standards de la
littérature (12, 26, 9).

## Hypothèse

Le MACD (différence entre EMA12 et EMA26, comparée à sa propre EMA9,
appelée "ligne de signal") capture un momentum de tendance à plus court
terme que la SMA200 — un overlay levé quand la ligne MACD est au-dessus
de sa ligne de signal (signal haussier classique) pourrait capturer un
edge distinct (réactivité plus rapide) plutôt que redondant avec #29/#34.

## Définition (fixée ici, avant tout résultat)

- EMA12, EMA26 = moyennes mobiles exponentielles à 12 et 26 séances des
  clôtures (paramètres standards MACD).
- Ligne MACD = EMA12 − EMA26. Ligne de signal = EMA9 de la ligne MACD.
- Position = **1.0x en permanence**, SAUF si la ligne MACD au jour t est
  **strictement au-dessus** de sa ligne de signal au jour t (signal
  haussier), où position = **CAP = 2.0x**. Décision prise à la clôture
  de t, appliquée au rendement t→t+1.
- Échantillon testable = à partir de la 35e séance (26+9, marge de
  convergence des EMA, cohérent avec la pratique standard).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x et paramètres MACD 12/26/9 = standards
de la littérature, fixés a priori, aucune grille testée avant ce
résultat).

## Anti-cheat

Ce fichier committé avant `nonml_macd_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py macd_overlay`.

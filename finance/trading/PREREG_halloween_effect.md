# Pré-enregistrement — Effet Halloween ("Sell in May and go away")

**Committé AVANT tout calcul.** Cycle #17 du backlog non-ML. Soumis à la
règle de succès renforcée. Construit en overlay (leçon des cycles
#8/#11/#12, pas flat-hors-fenêtre).

## Hypothèse

Bouman & Jacobsen (2002) : rendement boursier historiquement plus fort de
novembre à avril que de mai à octobre, documenté sur de nombreux marchés
développés ("Sell in May and go away"). Règle déterministe de calendrier,
aucun paramètre appris.

## Définition (fixée ici, avant tout résultat)

- Position = **1.0x en permanence** (comme Buy & Hold), SAUF de
  **novembre à avril** (6 mois) où position = **CAP = 2.0x** (cohérent
  avec les cycles #8/#9/#10/#11/#12/#13/#16, jamais retuné).
- **Coûts** : 5 bps par unité de changement de position, 2
  transitions/an (entrée nov, sortie mai).
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_halloween_effect_backtest.py`,
vérification via `nonml_anti_cheat_check.py halloween_effect`.

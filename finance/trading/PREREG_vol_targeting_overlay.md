# Pré-enregistrement — Overlay de vol-targeting continu

**Committé AVANT tout calcul.** Cycle #43 du backlog non-ML. Dernier
item de la file actuelle. Mécanisme DIFFÉRENT de tous les overlays
testés jusqu'ici : au lieu d'un seuil binaire (1.0x / CAP), l'exposition
est **continue**, inversement proportionnelle à la volatilité réalisée
récente — approche classique de "vol-targeting" (gestion institutionnelle
du risque, cf. les outils de position sizing déjà développés à l'Étape C
du projet, bien que celle-ci n'utilise ici QUE la vol réalisée simple,
pas les modèles GARCH de l'Étape C, pour rester dans le cadre "zéro
modèle statistique complexe" du backlog non-ML).

## Hypothèse

Une exposition qui augmente quand la volatilité réalisée est faible (et
diminue quand elle est élevée) devrait stabiliser le risque du
portefeuille dans le temps et potentiellement améliorer le ratio
rendement/risque par rapport à une exposition fixe 1.0x, en réduisant
l'exposition précisément pendant les phases de vol élevée qui
coïncident souvent avec les baisses de marché (déjà documenté aux
cycles #13/#22/#24/#31).

## Définition (fixée ici, avant tout résultat)

- Vol réalisée = écart-type des rendements log quotidiens sur une
  fenêtre roulante de **20 séances**, annualisée (× √252), calculée de
  façon strictement causale (vol connue à la clôture de t-1, utilisée
  pour décider la position de t).
- Vol cible = **15% annualisé** (fixé a priori, cible institutionnelle
  standard, indépendante de l'échantillon testé — PAS calculée sur les
  données du marché testé).
- Position(t) = **clip(vol_cible / vol_réalisée(t-1), 0.0, CAP=2.0)** —
  exposition continue, pas de seuil binaire. Pas de vente à découvert
  (plancher à 0.0).
- Échantillon testable = à partir de la 21e séance (marge de la fenêtre
  de vol).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition (turnover continu, potentiellement quotidien).
- **Référence** : Buy & Hold classique (position 1.0x fixe).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (vol cible 15%, fenêtre 20j et CAP=2.0x fixés a
priori, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py vol_targeting_overlay`.

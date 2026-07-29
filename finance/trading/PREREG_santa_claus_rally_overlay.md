# Pré-enregistrement — Overlay levé "Santa Claus Rally"

**Committé AVANT tout calcul.** Cycle #64 du backlog non-ML.

## Hypothèse

Le "Santa Claus Rally" (Yale Hirsch, *Stock Trader's Almanac*) désigne
la tendance historique des marchés actions à monter durant les 5
dernières séances de bourse de décembre et les 2 premières de janvier —
une fenêtre calendaire nettement plus ÉTROITE que le turn-of-month (#8,
±4 jours autour de chaque fin de mois, récurrent 12 fois par an) ou
Halloween (#17, 6 mois complets). Un overlay qui reste investi 1,0x en
permanence mais AMPLIFIE l'exposition sur cette fenêtre précise pourrait
battre Buy&Hold, sur le même principe structurel que les overlays
calendaires déjà validés.

## Définition (fixée ici, avant tout résultat, sur la base de la
littérature — PAS un ajustement sur les données du projet)

- Fenêtre = les **5 dernières séances de bourse de décembre** de chaque
  année ET les **2 premières séances de bourse de janvier** de l'année
  suivante (`DEC_TAIL=5`, `JAN_HEAD=2`, valeurs canoniques de la
  définition de Hirsch).
- Position = **1,0x** en permanence, **CAP = 2,0x** pendant cette
  fenêtre, **1,0x** en dehors.
- Le calendrier est une information connue à l'avance (pas une donnée de
  marché) — même traitement que ToM/Halloween/January Barometer dans ce
  backlog : aucune fuite possible par construction.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2,0x identique à tous les cycles précédents,
fenêtre 5j déc + 2j jan fixée a priori sur la définition canonique de
Hirsch, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_santa_claus_rally_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py santa_claus_rally_overlay`.

# Pré-enregistrement — Décomposition du turn-of-month en deux sous-fenêtres

**Committé AVANT tout calcul.** Cycle #71 du backlog non-ML. Le #8
(ToM en overlay, PASS 4/5) combine DEUX sous-fenêtres dans un seul
masque : les derniers jours du mois ET les premiers jours du mois
suivant. Ce cycle teste chaque sous-fenêtre SÉPARÉMENT pour savoir
laquelle porte réellement l'edge (question jamais posée malgré 26
cycles utilisant des variantes du ToM dans ce backlog).

## Hypothèse

L'edge du #8 pourrait provenir majoritairement d'UNE seule des deux
sous-fenêtres (littérature du "turn-of-month effect" : historiquement,
l'essentiel de l'effet est souvent attribué aux derniers jours du mois,
liés aux flux de rebalancement/paie de fin de mois, plus qu'aux tout
premiers jours du mois suivant). Décomposer permettrait de savoir si le
#8 est porté par un effet homogène sur toute la fenêtre ou concentré sur
une seule moitié.

## Définition (fixée ici, avant tout résultat — DEUX variantes
pré-spécifiées, testées et rapportées TOUTES LES DEUX quel que soit le
résultat, ce n'est pas une recherche du meilleur sous-ensemble après
coup)

- **Variante A — "fin de mois seule"** : position = 1,0x en permanence,
  CAP = 2,0x pendant les `LAST_N_DAYS=4` dernières séances du mois
  (identique au #8), 1,0x sinon (y compris pendant les 3 premières
  séances du mois suivant, contrairement au #8).
- **Variante B — "début de mois seul"** : position = 1,0x en permanence,
  CAP = 2,0x pendant les `FIRST_N_DAYS=3` premières séances du mois
  (identique au #8), 1,0x sinon (y compris pendant les 4 dernières
  séances du mois précédent).
- Tous les paramètres (LAST_N_DAYS=4, FIRST_N_DAYS=3, CAP=2,0x) sont
  repris à l'identique du #8, aucun retuning.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique, pour CHAQUE variante.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré, appliqué SÉPARÉMENT à
chaque variante)

Chaque variante doit battre Buy & Hold **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts, sur **au
moins 4 des 5 marchés**, pour être qualifiée de PASS. n_trials=1 par
variante (2 variantes pré-spécifiées ici, pas une recherche a posteriori
— les deux résultats seront rapportés intégralement).

## Anti-cheat

Ce fichier committé avant `nonml_tom_decomposition_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py tom_decomposition_overlay`.

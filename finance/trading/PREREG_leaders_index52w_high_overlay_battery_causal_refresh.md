# Pré-enregistrement — Re-calcul causal des batteries Règle 9 #161/#162 sur le #38

**Committé AVANT toute ré-exécution.** Cycle #260 du backlog non-ML.

## Contexte et motivation

Découverte incidente au cycle #259 (en documentant le DSR record du
#258) : les deux batteries Règle 9 historiques appliquées au #38
(Leaders 52-semaines + overlay 52w-high indice) —

- **#161** (`results/nonml_leaders_index52w_high_overlay_pass_validation_battery.md`,
  commit `2d12cd3`, DSR=0,730, 4/5) ;
- **#162** (`..._extended_history.md`, commit `6737f8c`, DSR=0,612, 3/5) —

datent toutes les deux d'**avant** la correction du bug d'exécution
« même barre » (`bd5ef75`, 01/08/2026), qui a rendu `build_weights()`
causal par défaut (`causal=True`) dans
`nonml_leaders_index52w_high_overlay_backtest.py`. Seule la **troisième**
variante de cette batterie (**#163**, univers point-in-time,
`..._pit_universe.md`) a été recalculée depuis (cycle #252, DSR
0,754→0,011, 0/5) — les deux autres n'ont **jamais été ré-exécutées**
depuis que leur dépendance partagée (`build_weights()`) a changé de
comportement par défaut. C'est exactement le même défaut de propagation
que celui documenté pour le résultat #163 lui-même avant sa correction.

## Vérification par lecture directe du code (déclarée avant tout calcul)

`scripts/nonml_leaders_index52w_high_overlay_pass_validation_battery.py`
importe `build_weights` directement depuis le module de backtest et
l'appelle sans jamais passer `causal=False` dans aucun des trois modes
d'invocation (`main()` par défaut → #161 ; `--extended` → #162 ; `--pit`
→ #163, déjà corrigé). Les deux premiers modes hériteront donc
automatiquement de la correction en se contentant de RE-EXÉCUTER le
script existant, **sans aucune modification de code** — confirmé par
lecture du fichier avant ce PREREG.

## Méthode

1. Vérification de non-régression : ré-exécution avec
   `build_kwargs=dict(causal=False)` explicite pour confirmer que les
   chiffres actuellement committés (DSR=0,730 pour #161, DSR=0,612 pour
   #162) sont bien reproduits bit-identiquement — sinon un autre facteur
   expliquerait la staleness et ce cycle serait invalidé avant d'aller
   plus loin.
2. Ré-exécution en mode par défaut (`causal=True`, aucun argument
   supplémentaire) pour #161 et avec `--extended` pour #162 — chiffres
   corrigés.
3. Aucun paramètre du #38 ni de la batterie n'est modifié (Règle 7) :
   seule la dépendance partagée déjà corrigée ailleurs est reflétée.

## Résultat attendu (aucune prédiction chiffrée, cohérence uniquement)

Par analogie avec la correction du #252 (le #38 sous-jacent passe de
Sharpe +1,42 à +0,47, sous la référence Leaders 1.0x, dans sa version
PIT), une dégradation substantielle du Sharpe brut candidat est probable
pour #161/#162 également, avec un impact en cascade sur les 5 contrôles
de la batterie (notamment DSR, dont le calcul dépend directement du
Sharpe candidat) — mais **aucune valeur chiffrée n'est anticipée ici**,
le résultat sera rapporté tel quel.

## Anti-cheat

Ce fichier committé et poussé avant toute ré-exécution. Sorties
attendues : mise à jour EN PLACE de
`results/nonml_leaders_index52w_high_overlay_pass_validation_battery.md`
et `..._extended_history.md` (même convention que la correction du #252
sur `..._pit_universe.md` — pas de nouveau nom de fichier, le contenu
change pour refléter le calcul causal correct).

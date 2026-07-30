# Pré-enregistrement — Extension du test SPA famille à la famille #149

**Committé AVANT tout calcul.** Cycle #159 du backlog non-ML.

## Limite mécanique reconnue AVANT tout calcul (comme au #150, réduction de portée honnête, Règle 5)

La piste initiale (#159 du backlog) proposait de combiner dans UN SEUL
test SPA les variantes NDX (quotidien #149, hebdomadaire #154) ET
S&P 500 (quotidien #151, hebdomadaire #157). **Vérification AVANT tout
calcul** : `spa_test` compare des modèles à un SEUL et même benchmark
partagé (même actif sous-jacent, même T). Les variantes NDX et S&P 500
ont des rendements Buy&Hold DIFFÉRENTS (actifs différents) — un test
SPA joint mélangeant les deux n'a pas de sens statistique (à quel
Buy&Hold comparerait-on ?), exactement la même limite mécanique déjà
rencontrée au #150 pour la famille cross-marché #134.

**Portée corrigée, fixée ici avant tout calcul** : DEUX tests SPA
séparés, chacun sur un actif unique :
1. Famille NDX du #149 : quotidien (#149) + hebdomadaire (#154), vs
   Buy&Hold NDX (2 membres, fenêtre commune 1985-2026).
2. Famille S&P 500 du #149 : quotidien (#151) + hebdomadaire (#157),
   vs Buy&Hold S&P 500 (2 membres, fenêtre commune, intersection avec
   la disponibilité DGS10).

## Définition (fixée ici, avant tout résultat)

- `spa_test` avec paramètres par défaut déjà utilisés partout ailleurs
  dans ce backlog (B=5000, mean_block=20, seed=42).
- Aucune sélection post-hoc de la fenêtre ou des membres.

## Ce que ce cycle NE fait PAS

Ne change AUCUN verdict Règle 9 déjà rendu sur les candidats
individuels (#149, #151, #154, #157). N'est pas un remplacement du DSR
individuel déjà calculé pour chacun.

## Anti-cheat

Ce fichier committé avant
`nonml_family_spa_cash_rate_correction_44.py`. Aucune nouvelle donnée
(recalcul sur artefacts déjà committés).

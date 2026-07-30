# Pré-enregistrement — Test SPA famille-entière, sous-famille NDX de la diversification obligataire

**Committé AVANT tout calcul.** Cycle #150 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Limite mécanique reconnue AVANT tout calcul (réduction de portée honnête, Règle 5)

`spa_test(losses, bench)` (déjà implémenté, `src/volatility.py`) exige
que TOUS les modèles comparés partagent le MÊME horizon temporel T
(même benchmark, même dates) — c'est un test conjoint sur un
échantillon commun, pas une agrégation de résultats sur des marchés
différents. La famille diversification complète (#134/#136 ×3
marchés/#137/#139/#140/#141 ×2 proxys/#143 — "11 variantes"
mentionnées au #132/#145) inclut des marchés DIFFÉRENTS (NDX, S&P 500,
Russell 2000, DAX, Composite) avec des benchmarks et des T différents
— un test SPA joint sur les 11 est donc MÉCANIQUEMENT IMPOSSIBLE tel
quel, pas seulement coûteux à construire.

**Portée réduite, fixée ici avant tout calcul** : ce cycle teste le
SPA famille-entière sur la SOUS-FAMILLE des 5 variantes NDX partageant
le même actif et un horizon commun par intersection de dates :
- #134 (proxy DGS10, 10 ans)
- #141 proxy 3 mois (DGS3MO)
- #141 proxy 1 an (DGS1)
- #137 (#134 empilé sur le rebalancement hebdomadaire #131)
- #139 (#134 empilé sur l'ensemble à 3 moteurs #124)

Les variantes cross-marché (#136 S&P 500/Russell 2000, #140 DAX, #143
Composite) et le #149 (base équity différente, #44) sont EXCLUES de ce
test — pas silencieusement, documenté explicitement comme limite de
portée.

## Définition (fixée ici, avant tout résultat)

- Fenêtre commune : intersection des 5 fenêtres (la plus courte,
  1988-09-20→2026-07-13, 9522 séances, imposée par #137/#139).
- Benchmark : Buy & Hold NDX, même fenêtre.
- `spa_test` avec paramètres par défaut déjà utilisés partout ailleurs
  dans ce backlog (B=5000 bootstrap, mean_block=20, seed=42) — aucun
  paramètre retouché.

## Ce que ce cycle NE fait PAS

Ne change AUCUN verdict Règle 9 déjà rendu sur les candidats
individuels. N'est pas un remplacement du DSR individuel déjà calculé
pour chacun — un test COMPLÉMENTAIRE (significativité conjointe de
la sous-famille contre l'accusation de sélection du meilleur membre
après coup).

## Anti-cheat

Ce fichier committé avant
`nonml_family_spa_diversification_bond_ndx.py`. Aucune nouvelle
donnée (recalcul sur artefacts déjà committés + DGS3MO/DGS1 déjà
récupérés au #141).

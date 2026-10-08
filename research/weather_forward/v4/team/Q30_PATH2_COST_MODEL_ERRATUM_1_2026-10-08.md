# Q30 voie 2 — erratum 1 proposé à la spécification du modèle de coûts

Statut : `PROPOSED_BY_BUILDER_PENDING_ORCHESTRATOR_ACCEPTANCE`. Il amende uniquement les points ci-dessous de la spécification de SHA-256 `2d534927a6aa69ec3b7e51f93dc09cd2e2b0b152b75932561b7d959dbfa8bda8`, avant toute exécution. Le reste est inchangé.

## E1. Le modèle central est le modèle FILLS existant, pas une réécriture

Le scénario central est exactement `ExecutionModel()` de `src/quant/desk/execution.py` (commission 0,5 pb, demi-spread 1 pb, impact 10 pb à 5 % de participation, participation maximale 5 %, ADV sur 20 séances), dont les paramètres sont les valeurs par défaut du desk. Le harnais appelle `ExecutionModel.adv` et la même formule d'impact, sans la ré-implémenter, afin que recherche, exécution simulée et Book partagent une seule base (invariant « bases de prix cohérentes »). Les quatre premiers postes du tableau §3 sont donc des valeurs du desk, pas des hypothèses nouvelles ; seuls le borrow, le financement et les valeurs de stress sont des hypothèses étiquetées. Le résultat le déclare.

## E2. Valeur de compte (NAV) : grille pré-enregistrée

`notional_t = |delta_weight_t| × NAV`. La spécification ne fixe pas NAV, donc la participation est indéfinie. NAV est un paramètre étiqueté `ASSUMED_NAV` pris dans la grille fermée `{1 000 000 ; 100 000 000 ; 1 000 000 000}` (la première est le capital initial par défaut du système, `initial_capital = 1_000_000`), toutes évaluées et publiées, sans sélection. La question économique est la capacité : à 1 M la participation sur SPY/TLT/GLD est quasi nulle et l'impact immatériel.

## E3. Capacité : refus, pas troncature silencieuse

Une participation supérieure à `max_participation` (5 %) n'est pas tronquée pour calculer un impact plafonné : elle déclenche `CAPACITY_BREACH`, la position n'est pas réputée exécutable, et le statut vaut `COST_INFEASIBLE` pour ce NAV (§5). Le plafond `min(participation, 1,0)` de la formule d'impact est supprimé de la spécification (il n'a de sens que sans refus). Le mot « troncature » du §3 est remplacé par « refus de capacité ».

## E4. Cible et fenêtres de la première exécution

Le moteur s'applique uniquement aux lignes déjà publiées d'évaluation de B2 (expression sélectionnée de la lane 2) et de B4 (L = 252 retenue, plus les trois autres expressions pour comparaison étiquetée, sans sélection), dans leurs fenêtres d'évaluation pré-enregistrées respectives, jamais au-delà du 2025-03-11. Toute autre cible exige son propre pré-enregistrement. Résultat descriptif seulement (§5).

## E5. Définitions manquantes

1. `COST_SENSITIVE` « un poste consomme au moins 50 % du P&L brut positif » : si le P&L brut est négatif ou nul, le statut est `COST_INFEASIBLE` (le critère de poste n'est pas évalué).
2. `break_even_*` : recherche déterministe par bissection sur `[0 ; 10 000]` pb avec tolérance 1e-6 ; s'il n'y a pas de changement de signe sur l'intervalle, la valeur publiée est `NOT_BRACKETED` avec le signe de l'extrémité.
3. Financement : débité sur l'exposition brute par séance, à `taux / 252`, déjà exprimé en proportion du NAV ; aucun intérêt n'est crédité sur le cash.
4. La grille de multiplicateurs `0x ... 3x` multiplie ensemble commission, demi-spread, impact, borrow et financement ; `0x` est un diagnostic de P&L brut, jamais un scénario d'admissibilité.

## E6. Portée des affirmations

La voie 2 produit un diagnostic de robustesse reproductible. Elle n'« améliore » pas la chaîne `VET -> SIZE -> RISK -> FILLS` : aucune de ces étapes n'est modifiée ni branchée sur ses statuts ; toute intégration au desk est un livrable distinct, avec ses propres tests et preuves.

```text
EXECUTION_AUTHORIZED_BY_ERRATUM = FALSE
NEW_MARKET_DATA_USED = FALSE
DISCOVERY_CLAIM = FALSE
STRATEGY_PROMOTION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```

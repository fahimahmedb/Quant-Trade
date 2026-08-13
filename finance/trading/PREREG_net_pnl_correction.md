# Pré-enregistrement — correction de `net_pnl` dans le balayage de doublons

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION** — le premier depuis longtemps. Contrairement aux cycles
#442-#444 qui ne faisaient que lire, celui-ci **change du code** et
**régénère un rapport publié**. C'est pourquoi tout y est déclaré à l'avance :
la ligne changée, l'effet attendu, et ce qui compterait comme échec.

## Le défaut à corriger, établi au #444

Le #444 a montré (verdict **FAIL**) que `nonml_pnl_duplicate_sweep_backtest.py`
applique une formule fausse au troisième schéma `.npz` :

```python
# lignes 40-42, actuelles
if {"pnl_candidate", "turn_candidate"} <= files:
    return (np.asarray(d["pnl_candidate"], dtype=float)
            - np.asarray(d["turn_candidate"], dtype=float) * c), "candidat+turnover"
```

`pnl_candidate` est enregistré **déjà net** par ses producteurs
(`pnl_sleeve_net`) ; `turn_candidate` n'est stocké que pour information. La
branche soustrait donc les coûts **une seconde fois**.

Effet mesuré au #444 sur `dollar_neutral_composite_pit` : P&L cumulé lu
**+0,1705** au lieu de **+0,2028**.

## La modification — une seule, annoncée ligne à ligne

**Suppression des lignes 40-42**, et rien d'autre. Aucune ligne ajoutée, aucune
autre ligne modifiée.

Justification : la branche suivante (lignes 43-44) lit déjà `pnl_candidate` tel
quel. Supprimer la branche fautive suffit à faire tomber ces fichiers sur la
lecture correcte — c'est le changement **minimal**, pas une réécriture.

Le régime de modification déclaré est donc : **suppression de trois lignes
contiguës annoncées, zéro insertion**. Toute ligne touchée hors de cet intervalle
constitue un **échec du cycle**, indépendamment du résultat numérique.

## Ce cycle modifie un rapport publié — dit à l'avance

Ré-exécuter le balayage réécrit `results/nonml_pnl_duplicate_sweep_result.md`.
C'est assumé, et c'est la raison d'être d'un cycle de modification. L'engagement
n'est pas de ne rien changer, mais que **tout changement soit publié** :

- le rapport **avant** est capturé (copie de travail, non committée) ;
- le rapport **après** est comparé ligne à ligne ;
- **chaque ligne modifiée est publiée** dans le résultat du cycle.

## Prédiction — falsifiable, chiffrée, tirée du #444

1. **Exactement 1** série change : `dollar_neutral_composite_pit`. C'est le seul
   `.npz` du dépôt portant à la fois `pnl_candidate` et `turn_candidate`.
2. **Aucun groupe de doublons ne change** — ni exact, ni quasi. Raison : le #444 a
   vérifié qu'une **seule** série du dépôt a la même longueur que celle-ci, avec
   une corrélation de **+0,017**. Elle n'est donc appariée à rien, ni avant ni
   après.
3. Le rapport du balayage ne change que dans les champs dépendant de cette série.

Si (2) est **réfutée** — si un groupe bouge — cela signifierait qu'un doublon
était masqué par le défaut, et **ce serait un résultat plus important que la
correction elle-même**. Il serait publié comme tel, en tête du rapport.

## Critère de succès — chiffré, et il peut échouer

1. Le `git diff` du script corrigé montre **3 suppressions, 0 insertion**, toutes
   dans l'intervalle annoncé.
2. **Chaque différence** entre le rapport avant et le rapport après est
   **identifiée et publiée**. Aucun changement inexpliqué.
3. Après correction, `dollar_neutral_composite_pit` est lu **exactement** comme
   `pnl_candidate` (écart maximal nul, pas « petit »).
4. Un **audit indépendant** (`nonml_net_pnl_correction_audit.py`) recalcule les
   groupes de doublons **sans réutiliser** la fonction corrigée, à partir des
   `.npz`, et retrouve les mêmes groupes.

> **PASS** = les quatre points tenus.
> **FAIL** = diff hors intervalle, ou un changement de sortie non expliqué, ou
> l'audit indépendant qui ne retrouve pas les groupes.

**Le PASS ne dépend pas de la prédiction.** La prédiction est rapportée
vérifiée ou réfutée, séparément du verdict : un cycle qui découvre un doublon
masqué reste un PASS s'il l'explique et le publie.

## Ce qui n'est pas fait ici

- **Aucun verdict de stratégie n'est recalculé.** La correction change une série
  lue par le balayage, pas les rapports des stratégies elles-mêmes, qui
  n'utilisent pas cette fonction.
- Les **3 consommateurs de catégorie C** du #444 (écart silencieux) ne sont pas
  touchés : leur cas est une lacune de couverture, pas un défaut, et relève d'un
  autre cycle.
- `nonml_leaders_trend_union_pnl_persistence_audit.py`, second D du #444, est
  corrigé **par ricochet** puisqu'il appelle `sw.main()`. Aucune modification ne
  lui est appliquée directement ; son rapport n'est **pas** régénéré par ce
  cycle.

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL** de ma propre correction.
2. Aucune ligne touchée hors de l'intervalle annoncé — vérifié par `git diff`,
   pas affirmé.
3. Toute différence de rapport publiée, y compris si elle est ennuyeuse.
4. Aucun retuning : la correction est celle décrite ci-dessus, décidée avant
   d'avoir vu son effet sur les groupes.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).

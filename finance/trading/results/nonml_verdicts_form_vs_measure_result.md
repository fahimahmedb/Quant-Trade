# Les verdicts du dépôt : **forme** ou **mesure** ? (pré-enregistré)

Le **#498** a montré qu'un verdict pouvait basculer de **C** à **A**
**sans qu'aucun fait ne change** : seul le détecteur avait changé.
**Un verdict vaut ce que vaut son détecteur** — et personne n'avait
compté combien, dans ce dépôt, reposent sur un appariement de forme.

## Les quatre classes, citées verbatim

> - **lit des données** : littéral finissant par `.txt`, `.npz`, `.csv`, ou mentionnant
>   `data/`, ou import de `data_loader` / `load_ohlc` ;
> - **lit le texte du dépôt** : littéral finissant par `.md`, `.py` ;
> - **apparie** : `import re`.

| Classe | Définition |
|---|---|
| **F** | forme — lit le texte **et** apparie, **sans** lire de données |
| **D** | mesure — lit des données, **sans** lire le texte du dépôt |
| **M** | mixte — lit **les deux** |
| **N** | ni l'un ni l'autre |

**Rapport porteur de verdict** : son `.md` contient `**PASS**` ou
`**FAIL**`.

## Le recensement

- rapports **porteurs d'un verdict** : **60**
  *(au sens figé — verdict **en gras**. La section « couverture » plus
  bas montre que ce critère écarte la majorité du corpus : **les comptes
  ci-dessous décrivent une minorité des rapports du dépôt**.)*
- scripts écartés faute de date d'introduction : **0**

| Classe | Nombre | Part |
|---|---|---|
| **F** | **40** | **66,7 %** |
| **D** | **0** | **0,0 %** |
| **M** | **12** | **20,0 %** |
| **N** | **8** | **13,3 %** |

## La chronologie — le dépôt a-t-il dérivé ?

| Classe | Effectif | Date médiane d'introduction |
|---|---|---|
| **F** | **40** | 18/08/2026 |
| **D** | **0** | — |
| **M** | **12** | 13/08/2026 |
| **N** | **8** | 14/08/2026 |

| Population | Part de **F** |
|---|---|
| **ensemble** (**60**) | **66,7 %** |
| **20 plus récents** | **95,0 %** |

- écart : **+28,3** points

> **La question de la dérive ne peut pas être tranchée** : la classe
> **D** est vide **par construction de ma règle**, comme la section
> suivante le montre. Une médiane sans effectif ne se compare à rien,
> et je ne remplace pas D par M après coup pour sauver la
> comparaison — ce serait choisir sa population après avoir vu le
> résultat.

## Les **20** plus récents, nommés

| Script | Classe | Introduit le |
|---|---|---|
| `nonml_residual_borrowings_unpublished_sources_backtest.py` | **F** | 18/08/2026 |
| `nonml_suspect_values_reports_backtest.py` | **F** | 18/08/2026 |
| `nonml_reference_vs_value_errors_backtest.py` | **F** | 18/08/2026 |
| `nonml_contextual_confrontation_backtest.py` | **F** | 18/08/2026 |
| `nonml_borrowed_figures_confrontation_backtest.py` | **F** | 18/08/2026 |
| `nonml_borrowed_figures_census_backtest.py` | **F** | 18/08/2026 |
| `nonml_lot2_bound_interpolation_backtest.py` | **F** | 18/08/2026 |
| `nonml_declaration_rule_extension_dating_backtest.py` | **F** | 18/08/2026 |
| `nonml_execution_primitives_census_backtest.py` | **F** | 18/08/2026 |
| `nonml_execution_detection_rule_backtest.py` | **F** | 18/08/2026 |
| `nonml_class_a_witness_publication_backtest.py` | **N** | 18/08/2026 |
| `nonml_unpublished_witnesses_paths_backtest.py` | **F** | 18/08/2026 |
| `nonml_irreparability_justifications_audit_backtest.py` | **F** | 18/08/2026 |
| `nonml_declaration_convention_decay_backtest.py` | **F** | 18/08/2026 |
| `nonml_battery_indet_hoist_declared_backtest.py` | **F** | 18/08/2026 |
| `nonml_battery_witness_hoist_backtest.py` | **F** | 18/08/2026 |
| `nonml_remaining_masking_guards_patch_backtest.py` | **F** | 18/08/2026 |
| `nonml_duplicate_sweep_irreparability_backtest.py` | **F** | 18/08/2026 |
| `nonml_masking_guards_witness_patch_backtest.py` | **F** | 18/08/2026 |
| `nonml_declaration_convention_dating_backtest.py` | **F** | 18/08/2026 |

- dont de classe **D** (mesure pure) : **0**

## Un défaut de ma propre règle, mesuré

**La classe D est vide, et c'est un artefact.** « Lit le texte du dépôt »
se déclenche sur le littéral que **tout** script porte : le chemin de
**son propre rapport**. Aucun script ne peut donc être « données sans
texte ». **La classe D était impossible à peupler par construction.**

En excluant le rapport du script lui-même du critère « lit le texte » —
**diagnostic, non verdict : la règle reste celle du pré-enregistrement** :

| Classe | Règle figée | Sans son propre rapport |
|---|---|---|
| **F** | **40** | **40** |
| **D** | **0** | **3** |
| **M** | **12** | **9** |
| **N** | **8** | **8** |

> La famille qui **lit réellement des données** est donc **M**
> (**12**), et non **D**. C'est elle qu'il faut lire comme
> « verdict adossé à une mesure ».

## La couverture de la population

- rapports retenus (verdict **en gras**) : **60**
- rapports portant `PASS`/`FAIL` **sans gras**, donc **écartés** : **286**

> La définition figée exigeait le **gras**. Elle laisse donc de côté
> **286** rapports qui rendent bien un verdict. **La population n'est
> pas exhaustive**, et le dire vaut mieux que présenter les comptes
> ci-dessus comme un recensement complet.

## Ce que ce compte ne dit pas

**Un verdict de forme n'est pas un faux verdict.** Vérifier qu'un script
ne contient pas de défaut est un travail légitime, et le #498 montre
seulement qu'un tel verdict est **fragile au détecteur** — pas qu'il est
faux. Ce recensement mesure une **nature**, pas une **qualité**.

## Auto-exclusion, déclarée d'avance

**Ce cycle ne se compte pas lui-même**, et il serait, par sa propre
règle, un **F** de plus : il lit des `.md` et des `.py`, il importe `re`,
il ne touche aucune donnée de marché. **L'auto-exclusion était déclarée
au pré-enregistrement** (règle du #447) — elle est rappelée ici, non tue.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| part de **F** ≥ 50 % | ≥ 50 % | 66,7 % | **vérifiée** |
| ≥ 1 **D** parmi les 20 plus récents | ≥ 1 | 0 | **réfutée** |
| médiane **F** postérieure à médiane **D** | oui | classe D vide | **non testable** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Les seuls appels externes visent `git log` et `git status`, **en
lecture**.

## Critères de succès

1. Quatre classes citées verbatim, établies par AST — **OUI**.
2. Population (**60**) et quatre comptes publiés — **OUI**.
3. Dates médianes par classe publiées — **OUI**.
4. Les **20** plus récents nommés, deux parts de **F** comparées — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts et de
> l'historique à la date de son exécution.

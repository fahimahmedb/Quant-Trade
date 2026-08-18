# Les **valeurs suspectes**, cherchées dans les **rapports** (pré-enregistré)

Les **#501** à **#503** n'ont interrogé qu'**une** source : la section
`## Backlog #NNN`. Or un cycle publie aussi un **rapport**, et c'est là
que ses chiffres naissent — **le registre en est le résumé**.

## La règle de correspondance, citée verbatim

> 1. la **section** du cycle est lue ;
> 2. le nom de stratégie en est extrait par `PREREG_([a-z0-9_]+)\.md`, à
>    défaut par `nonml_([a-z0-9_]+?)_(?:result|audit|backtest)` ;
> 3. ses **rapports** sont tous les `results/nonml_<nom>_*.md`.

Paramètres du #502 **inchangés** : **6 lettres**, **±200 caractères**, **2 mots-clés**.

## La correspondance cycle → rapport

- cycles cités par ces suspects : **8**

| Cycle | Nom de stratégie extrait | Rapports trouvés |
|---|---|---|
| `#427` | `pnl_persistence_lot5` | **2** |
| `#443` | `npz_report_consistency_baskets` | **3** |
| `#449` | `verdict_rule_propagation` | **3** |
| `#451` | `marker_emitted_by_scripts` | **2** |
| `#463` | `report_idempotence` | **3** |
| `#469` | `marker_emitter_crossing` | **2** |
| `#479` | `hardcoded_figures_remainder` | **3** |
| `#483` | `orphan_audits_declared_reading` | **3** |

## Les quatre classes

- valeurs suspectes reclassées : **13**

| Classe | Nombre | Part |
|---|---|---|
| **confirmé au rapport** | **1** | **7,7 %** |
| **présent sans contexte** | **7** | **53,8 %** |
| **absent du rapport** | **5** | **38,5 %** |
| **rapport introuvable** | **0** | **0,0 %** |

## Les deux sources, comparées

*L'engagement 3 l'exige : côte à côte, jamais la seule favorable.*

| Source | Confirmations sur ces **13** |
|---|---|
| **registre** (`## Backlog #NNN`) | **0** *(par construction : c'est ce qui les a rendues suspectes)* |
| **rapports** (`results/nonml_<nom>_*.md`) | **1** |

> **Le changement de source n'explique que 1 de ces
> 13.** J'attendais au moins **6** ; c'est réfuté. La
> source consultée **n'était donc pas l'explication principale**,
> contrairement à ce que la piste ouverte au #503 laissait espérer.

> Le résultat dominant est ailleurs : **7**
> de ces valeurs **figurent** dans les rapports du cycle cité mais
> **pas au même sujet** — exactement le motif que le #502 avait
> trouvé sur le registre. **Changer de source n'a pas changé le
> diagnostic**, ce qui en renforce la solidité.

| Script | Cite | Nombre | Mots-clés | Retrouvé dans |
|---|---|---|---|---|
| `nonml_hardcoded_tables_repair_backtest.py` | `#479` | **17** | **2** | `nonml_hardcoded_figures_remainder_result.md` |

## Les résidus — absents des deux sources

- effectif : **5**

| Script | Cite | Nombre |
|---|---|---|
| `nonml_content_defined_magnitudes_audit.py` | `#449` | **2** |
| `nonml_content_defined_magnitudes_backtest.py` | `#451` | **8** |
| `nonml_report_idempotence_backtest.py` | `#443` | **5,7** |
| `nonml_self_inclusion_detector_backtest.py` | `#463` | **16** |
| `nonml_self_inclusion_detector_backtest.py` | `#463` | **2** |

> Ce sont les **seuls** emprunts que quatre cycles d'enquête n'ont pas
> su rattacher à une source publiée. **Ils restent des soupçons**, pas
> des erreurs : la liste des sources consultées n'est toujours pas
> exhaustive — un chiffre peut vivre dans un `PREREG_`, un commentaire
> de code ou un message de commit.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 6 confirmés au rapport | ≥ 6 | 1 | **réfutée** |
| ≥ 1 rapport introuvable | ≥ 1 | 0 | **réfutée** |
| ≥ 1 résidu subsiste | ≥ 1 | 5 | **vérifiée** |


## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Population, mots-clés, fenêtres et magnitudes sont **importés** des
backtests des #500 à #503 — leurs fonctions, jamais leur `main()`.

## Critères de succès

1. Règle de correspondance citée verbatim, paramètres du #502 inchangés — **OUI**.
2. Les **13** valeurs suspectes reclassées, **4** classes publiées — **OUI**.
3. Correspondance cycle → rapport publiée cycle par cycle (**8**) — **OUI**.
4. Résidus nommés individuellement (**5**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts, du
> registre et des rapports à la date de son exécution.

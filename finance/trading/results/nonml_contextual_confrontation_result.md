# Confronter les emprunts **par le contexte** (pré-enregistré)

Le **#501** cherchait **un nombre** dans la section du cycle cité. Il n'a
départagé que **3** emprunts sur **39**, et
son rapport a conclu que **la méthode ne départage pas**. Ici, on vérifie
que le nombre apparaît **au même sujet**.

## La règle contextuelle et ses trois paramètres, cités verbatim

> - **mots-clés** : mots d'au moins **6 lettres**,
>   minusculisés, balisage et ponctuation retirés, **chiffres exclus** ;
> - **fenêtre** : **±200 caractères** autour de chaque occurrence
>   en gras du nombre dans la section citée ;
> - **recouvrement exigé** : au moins **2** mots-clés de
>   l'emprunt présents dans la fenêtre.

Le seuil de longueur écarte l'essentiel des mots outils du français
**sans liste d'exclusion**, qui aurait été un réglage déguisé.

## Les cinq classes

- nombres empruntés reclassés : **39**

| Classe | Nombre | Part |
|---|---|---|
| **confirmé en contexte** | **8** | **20,5 %** |
| **présent sans contexte** | **14** | **35,9 %** |
| **absent de la section** | **15** | **38,5 %** |
| **contexte indisponible** | **2** | **5,1 %** |
| **non vérifiable** | **0** | **0,0 %** |

## La table de transition #501 → #502

| Classe #501 | Classe #502 | Nombre |
|---|---|---|
| retrouvé ailleurs | absent de la section | **15** |
| confirmé | présent sans contexte | **14** |
| confirmé | confirmé en contexte | **8** |
| retrouvé ailleurs | contexte indisponible | **2** |

## Ce que la règle contextuelle **prouve de plus**

- confirmations **probantes** au #501 (nombre ≥ 3 chiffres) : **3**
- confirmations **en contexte** ici : **8**

- **communs aux deux critères** : **2**
- confirmations **fortes du #501 que le contexte ne confirme pas** : **1**

> **Les deux critères ne sont pas emboîtés.** Comparer leurs seuls
> effectifs suggérerait un gain net ; le recouvrement montre qu'ils
> **départagent des emprunts différents**.

- `nonml_declaration_convention_dating_backtest.py` cite `#483` pour **113** — nombre
  long, mais **0** mot(s)-clé(s) en commun : le #501 le
  créditait sur la seule improbabilité d'une coïncidence.

> La règle contextuelle départage **5**
> emprunts de plus **en effectif**, et **6** qu'elle est seule à
> confirmer. **Le contexte mord là où la taille du nombre ne disait
> rien.**

## Les sur-crédités — l'ancienne règle les disait confirmés

- effectif : **14**

| Script | Cite | Nombre | Mots-clés retrouvés |
|---|---|---|---|
| `nonml_citer_451_definition_backtest.py` | `#472` | **0** | **0** |
| `nonml_citer_451_resolution_backtest.py` | `#469` | **0** | **0** |
| `nonml_content_defined_magnitudes_backtest.py` | `#449` | **6** | **0** |
| `nonml_declaration_convention_dating_backtest.py` | `#483` | **113** | **0** |
| `nonml_declaration_convention_decay_backtest.py` | `#486` | **0** | **1** |
| `nonml_duplicate_sweep_coverage_audit.py` | `#427` | **1** | **0** |
| `nonml_hardcoded_figures_sweep_backtest.py` | `#451` | **1** | **1** |
| `nonml_hardcoded_figures_sweep_backtest.py` | `#451` | **1** | **1** |
| `nonml_hardcoded_tables_repair_backtest.py` | `#479` | **17** | **1** |
| `nonml_hardcoded_tables_repair_backtest.py` | `#479` | **17** | **1** |
| `nonml_hardcoded_tables_repair_backtest.py` | `#479` | **18** | **1** |
| `nonml_orphan_npz_inspection_backtest.py` | `#442` | **20** | **0** |
| `nonml_repo_magnitudes_recount_backtest.py` | `#457` | **29** | **1** |
| `nonml_self_inclusion_detector_backtest.py` | `#463` | **18** | **0** |

## Les sauvés — un petit nombre, mais le bon sujet

- effectif : **6**

| Script | Cite | Nombre | Mots-clés retrouvés |
|---|---|---|---|
| `nonml_hardcoded_figures_remainder_backtest.py` | `#476` | **35** | **4** |
| `nonml_guards_witness_remainder_backtest.py` | `#481` | **14** | **3** |
| `nonml_hardcoded_figures_remainder_backtest.py` | `#474` | **1** | **2** |
| `nonml_hardcoded_tables_repair_backtest.py` | `#479` | **18** | **2** |
| `nonml_orphans_interrupted_or_lost_backtest.py` | `#464` | **10** | **2** |
| `nonml_orphans_interrupted_or_lost_backtest.py` | `#464` | **24** | **2** |

> Ce sont les emprunts que le #501 ne pouvait pas créditer — leur
> nombre est trop court pour prouver quoi que ce soit — et que le
> **contexte** valide. **C'est exactement le gain visé.**

## Ce que ce cycle **n'établit toujours pas**

**Aucun chiffre n'est déclaré faux.** « Absent de la section » reste un
**soupçon** : le nombre peut vivre dans un rapport que la règle ne
consulte pas. Et un **recouvrement de mots-clés n'est pas une preuve
d'identité** — deux passages peuvent parler du même sujet et de deux
grandeurs différentes.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| confirmés en contexte ≥ 10 | ≥ 10 | 8 | **réfutée** |
| plus que les 3 confirmations fortes du #501 | > 3 | 8 | **vérifiée** |
| ≥ 1 sur-crédité par le #501 | ≥ 1 | 14 | **vérifiée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Population et classes du #501 sont **importées** de leurs backtests
(leurs fonctions, pas leur `main()`) — recopier une définition est le
meilleur moyen de la faire diverger, leçon du #499.

## Critères de succès

1. Règle et trois paramètres cités verbatim — **OUI**.
2. Les **39** nombres reclassés, **5** classes publiées — **OUI**.
3. Table de transition #501 → #502 publiée (**4** combinaisons) — **OUI**.
4. Sur-crédités (**14**) et sauvés (**6**) nommés — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts et du
> registre à la date de son exécution.

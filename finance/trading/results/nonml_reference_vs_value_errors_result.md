# **Erreur de référence** ou **erreur de valeur** ? (pré-enregistré)

Le **#502** laisse des emprunts « suspects » sans dire de quoi ils
souffrent. Deux maladies s'y confondent : le **bon chiffre attribué au
mauvais cycle**, ou le **mauvais chiffre attribué au bon cycle**.

## Les trois définitions, citées verbatim

> - **magnitude** — nombre de chiffres de la partie entière ;
> - **section candidate** — une section **autre** que celle citée où le
>   nombre est en gras **et** ≥ **2** mots-clés de
>   l'emprunt tombent dans **±200 caractères** ;
> - **grandeur présente** — la section **citée** contient un nombre en
>   gras de **même magnitude**.

Les paramètres du #502 — **6 lettres**, **±200 caractères**, **2 mots-clés** — sont
**repris tels quels**. Les retoucher ici serait régler un détecteur sur
la population qu'il doit juger.

## Les trois classes

- suspects classés : **29**
- sections de backlog explorées : **299**

| Classe | Nombre | Part |
|---|---|---|
| **référence probable ailleurs** | **15** | **51,7 %** |
| **valeur suspecte** | **13** | **44,8 %** |
| **indéterminé** | **1** | **3,4 %** |

## Les deux groupes, **séparément**

*L'engagement 3 l'exige : les fondre en un total masquerait leur
différence, qui est la question même de ce cycle.*

| Origine (#502) | Effectif | référence ailleurs | valeur suspecte | indéterminé |
|---|---|---|---|---|
| **sur-crédité** | **14** | **7** | **7** | **0** |
| **absent** | **15** | **8** | **6** | **1** |

| Groupe | Part « référence probable ailleurs » |
|---|---|
| **sur-crédité** | **50,0 %** |
| **absent** | **53,3 %** |

- écart entre les deux parts : **3,3** points

> **Les deux groupes se répartissent de la même façon.** La
> distinction du #502 entre « sur-crédité » et « absent »
> **ne recouvre rien** — et cela affaiblit rétrospectivement sa
> lecture, qu'il faut donc corriger ici.

## Les « référence probable ailleurs », nommés

- effectif : **15**
- dont à section candidate **unique** : **12**

| Script | Cite | Nombre | Candidates | Lesquelles |
|---|---|---|---|---|
| `nonml_citer_451_definition_backtest.py` | `#472` | **0** | **1** | `#473` |
| `nonml_content_defined_magnitudes_backtest.py` | `#449` | **8** | **1** | `#465` |
| `nonml_content_defined_magnitudes_backtest.py` | `#449` | **6** | **1** | `#465` |
| `nonml_declaration_convention_decay_backtest.py` | `#486` | **33** | **1** | `#492` |
| `nonml_declaration_convention_decay_backtest.py` | `#486` | **0** | **1** | `#492` |
| `nonml_duplicate_sweep_coverage_audit.py` | `#427` | **6** | **1** | `#428` |
| `nonml_marker_emitted_by_scripts_backtest.py` | `#450` | **4** | **1** | `#451` |
| `nonml_orphan_npz_inspection_backtest.py` | `#442` | **20** | **1** | `#453` |
| `nonml_repo_magnitudes_recount_backtest.py` | `#457` | **29** | **1** | `#462` |
| `nonml_reproducibility_sample_backtest.py` | `#416` | **44** | **1** | `#434` |
| `nonml_self_inclusion_detector_backtest.py` | `#463` | **18** | **1** | `#466` |
| `nonml_sweep_pass_prose_fix_backtest.py` | `#427` | **4** | **1** | `#445` |
| `nonml_self_inclusion_detector_backtest.py` | `#463` | **2** | **2** | `#466`, `#482` |
| `nonml_dsr_corrected_trials_backtest.py` | `#445` | **3** | **3** | `#426`, `#427`, `#456` |
| `nonml_duplicate_sweep_coverage_audit.py` | `#427` | **1** | **4** | `#428`, `#439`, `#440`, `#441` |

### Les seuls pour lesquels une correction serait **nommable**

- `nonml_citer_451_definition_backtest.py` cite `#472` pour **0** — une seule
  section candidate : `#473`.
- `nonml_content_defined_magnitudes_backtest.py` cite `#449` pour **8** — une seule
  section candidate : `#465`.
- `nonml_content_defined_magnitudes_backtest.py` cite `#449` pour **6** — une seule
  section candidate : `#465`.
- `nonml_declaration_convention_decay_backtest.py` cite `#486` pour **33** — une seule
  section candidate : `#492`.
- `nonml_declaration_convention_decay_backtest.py` cite `#486` pour **0** — une seule
  section candidate : `#492`.
- `nonml_duplicate_sweep_coverage_audit.py` cite `#427` pour **6** — une seule
  section candidate : `#428`.
- `nonml_marker_emitted_by_scripts_backtest.py` cite `#450` pour **4** — une seule
  section candidate : `#451`.
- `nonml_orphan_npz_inspection_backtest.py` cite `#442` pour **20** — une seule
  section candidate : `#453`.
- `nonml_repo_magnitudes_recount_backtest.py` cite `#457` pour **29** — une seule
  section candidate : `#462`.
- `nonml_reproducibility_sample_backtest.py` cite `#416` pour **44** — une seule
  section candidate : `#434`.
- `nonml_self_inclusion_detector_backtest.py` cite `#463` pour **18** — une seule
  section candidate : `#466`.
- `nonml_sweep_pass_prose_fix_backtest.py` cite `#427` pour **4** — une seule
  section candidate : `#445`.

## La direction des candidates — ce que ma classe **sur-affirme**

- « référence ailleurs » dont **toutes** les candidates sont
  **postérieures** au cycle cité : **14** sur **15**
- dont **au moins une** est **antérieure** : **1**

> **Ma classe s'appelle mal.** Une candidate **postérieure** au cycle
> cité n'indique aucune erreur de référence : elle indique qu'un
> cycle **ultérieur a repris le chiffre** — ce qui est le
> fonctionnement normal de ce registre, où chaque cycle commente les
> précédents.
>
> **La lecture honnête de « référence probable ailleurs » est donc :
> le nombre est repris plus tard, pas attribué au mauvais cycle.**
> Je garde le nom figé au pré-enregistrement — le changer après
> mesure serait renommer un résultat gênant — mais son sens est
> corrigé ici, par la mesure et non par une impression.

> **Conséquence sur la prédiction 3** : les **12** candidates uniques ne
> sont **pas** des corrections nommables si elles sont postérieures. Le
> compte de corrections réellement nommables tombe à **1**.

## Ce que « probable » veut dire ici

**Aucune référence n'est corrigée, aucun nombre n'est déclaré faux.**
Une section candidate peut parler du même sujet **par hasard** : ce
dépôt répète ses thèmes d'un cycle à l'autre, et c'est précisément ce
qui rend la méthode faillible. Un suspect à **plusieurs** candidates
n'est d'ailleurs **pas** corrigeable — la méthode dit seulement que le
nombre vit ailleurs **aussi**.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| « référence ailleurs » ≥ 5 | ≥ 5 | 15 | **vérifiée** |
| écart entre groupes ≥ 20 points | ≥ 20 | 3,3 | **réfutée** |
| ≥ 1 candidate unique | ≥ 1 | 12 | **vérifiée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Population, mots-clés et fenêtres sont **importés** des backtests des
#500, #501 et #502 — leurs fonctions, jamais leur `main()`.

## Critères de succès

1. Trois définitions citées verbatim, paramètres du #502 inchangés — **OUI**.
2. Les **29** suspects classés, **3** classes publiées — **OUI**.
3. Détail sur-crédités / absents publié séparément — **OUI**.
4. « Référence ailleurs » nommés (**15**), candidates uniques distinguées (**12**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts et du
> registre à la date de son exécution.

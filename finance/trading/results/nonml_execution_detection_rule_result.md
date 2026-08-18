# Une règle de classe qui **voit l'exécution en process** (pré-enregistré)

Le **#494** classait « exécute un tiers » sur la seule forme
`subprocess\.run\(\[sys\.executable`. Le **#495** a montré qu'un script peut exécuter un tiers
**en process**, sans sous-processus — et que la règle ne le voit pas.

## La règle corrigée, citée verbatim

> Un script **exécute un tiers du dépôt** si l'une au moins de ces
> conditions est vraie, établie par **AST** :
> 1. `subprocess.run([sys.executable, …])` — la forme du #494 ;
> 2. importe un module `nonml_*` du dépôt **et** appelle `.main()` sur l'alias de cet import — la forme découverte au #495 ;
> 3. appelle `runpy.run_path`, `exec(open(…).read())` ou `importlib` sur un chemin de `scripts/` ;

- scripts `nonml_*.py` analysés : **969**
- scripts que la règle corrigée classe « exécute un tiers » : **30**

| Condition | Scripts déclenchés |
|---|---|
| **1** | **23** |
| **2** | **8** |
| **3** | **1** |

## Les quatre témoins du #494, reclassés

Les noms sont **lus dans le rapport du #494**, pas réécrits ici.

| Témoin | Classe #494 | Conditions déclenchées | Verdict règle corrigée |
|---|---|---|---|
| `nonml_battery_coverage_backtest.py` | **C** | 1 | **exécute un tiers** |
| `nonml_net_pnl_correction_backtest.py` | **A** | 2 | **exécute un tiers** |
| `nonml_six_reports_regeneration_backtest.py` | **C** | 1 | **exécute un tiers** |
| `nonml_sweep_pass_prose_fix_backtest.py` | **A** | 2 | **exécute un tiers** |

- témoins classés « exécute un tiers » par la règle corrigée : **4** sur **4**

> La conclusion du #495 — « les 4 sont de classe C » — **tient sur les
> quatre**, alors qu'il n'en avait lu que deux.

## L'ampleur de l'angle mort du #494

Scripts que la règle du #494 classait **« sans exécution »** et qui
**exécutent pourtant un tiers** :

- scripts dans l'angle mort : **8**

| Script | Condition | Cibles exécutées |
|---|---|---|
| `nonml_capitulation_gate_floor_sweep_audit.py` | 2 | `nonml_capitulation_gate_floor_sweep_backtest.py` |
| `nonml_empty_pass_requalification_audit.py` | 2 | `nonml_empty_pass_requalification_backtest.py` |
| `nonml_leaders_trend_union_pnl_persistence_audit.py` | 2 | `nonml_pnl_duplicate_sweep_backtest.py` |
| `nonml_net_pnl_correction_backtest.py` | 2 | `nonml_pnl_duplicate_sweep_backtest.py` |
| `nonml_pnl_persistence_lot4_audit.py` | 1, 2 | `nonml_capitulation_gate_floor_sweep_backtest.py` |
| `nonml_sweep_basket_schema_support_audit.py` | 2 | `nonml_capitulation_gate_floor_sweep_backtest.py` |
| `nonml_sweep_pass_prose_fix_backtest.py` | 2 | `nonml_pnl_duplicate_sweep_backtest.py` |
| `nonml_third_npz_schema_handling_backtest.py` | 3 | `importlib.util.spec_from_file_location` |

## Les cibles des exécutions

- modules distincts exécutés par un tiers : **11**

Une cible n'est **pas toujours nommable statiquement** : quand le chemin
est construit dans une variable (`str(BATTERIE)`, `SCRIPTS / script`),
l'AST ne voit qu'un **fragment** — les entrées qui ne commencent pas par
`nonml_` en sont. Elles sont publiées **telles quelles**, non filtrées :
filtrer après lecture serait choisir ses chiffres.

| Cible | Nombre d'appels |
|---|---|
| `nonml_pnl_duplicate_sweep_backtest.py` | **8** |
| `_backtest.py` | **6** |
| `nonml_capitulation_gate_floor_sweep_backtest.py` | **3** |
| `importlib.util.spec_from_file_location` | **1** |
| `nonml_backlog_figures_verification_backtest.py` | **1** |
| `nonml_content_defined_magnitudes_backtest.py` | **1** |
| `nonml_empty_pass_requalification_backtest.py` | **1** |
| `nonml_prereg_convention_coverage_backtest.py` | **1** |
| `nonml_repo_magnitudes_recount_backtest.py` | **1** |
| `nonml_self_inclusion_detector_backtest.py` | **1** |
| `nonml_self_inclusion_detector_v2_backtest.py` | **1** |

## Une forme que ma propre règle corrigée ne voit pas

`from nonml_x import main` puis `main()` exécute un tiers **sans**
attribut sur un alias — la condition 2 exige `.main()` **sur l'alias**.
La forme est comptée ici **hors règle**, sans reclassement : la règle a
été figée avant mesure et **ne sera pas élargie après coup**.

- scripts employant cette forme, non déjà classés : **0**

## Deux bugs de mon propre détecteur, corrigés avant tout résultat

Ils sont publiés parce qu'ils auraient **fabriqué une conclusion fausse**.

1. **La condition 1 confondait « déclenchée » et « cible nommable ».**
   Elle ne se déclenchait que si un littéral `"….py"` figurait dans
   l'appel. Or `battery_coverage` et `six_reports_regeneration` passent
   une **variable** de chemin. Le premier jet les classait donc
   « n'exécute rien » — **2 témoins sur 4** — et j'aurais publié que le
   **#495 avait extrapolé**. Après correction : **4 sur 4**, et c'est le
   contraire qui est vrai.
2. **Le critère 5 se mesurait par regex sur ma propre source.** Ma source
   **cite** la règle du #494 en clair ; le motif s'y trouvait donc, et le
   critère tombait à **NON** pour un script qui n'exécute rien. C'est la
   distinction **porteur / citeur** du #473, retombée sur moi. Mesuré par
   **AST** — des appels, pas des chaînes — il vaut **0**.

> Les deux fois, le détecteur était faux **dans le sens qui m'accusait**.
> Cela ne les rend pas anodins : un détecteur faux reste faux, et rien ne
> garantissait le signe.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| les 4 témoins exécutent un tiers | 4 | 4 | **vérifiée** |
| ≥ 5 scripts dans l'angle mort du #494 | ≥ 5 | 8 | **vérifiée** |
| la condition 3 ne trouve rien | 0 | 1 | **réfutée** |

## Aucune exécution

- occurrences du motif du #494 dans ma source, **par regex** : **3** — je **cite** la règle, je ne l'exerce pas ;
- **appels** d'exécution dans ma source, **par AST** : **0**.
- fichiers modifiés par ce cycle hors les siens : **0**

## Critères de succès

1. Règle corrigée citée verbatim, trois conditions publiées séparément avec leur compte — **OUI**.
2. Les **4** témoins reclassés, chacun avec sa condition — **OUI**.
3. Ampleur de l'angle mort du #494 mesurée sur tout le dépôt — **OUI**.
4. Cibles des exécutions nommées (**11**) — **OUI**.
5. Aucun script exécuté, arbre vérifié propre — **OUI**.

**PASS** — le critère porte sur le **procédé**, pas sur un rendement.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution.

# Recenser les primitives d'exécution, au lieu de les rattraper une par une

## Le principe d'inclusion, cité verbatim

> Une règle qui prétend dire « ce script exécute un tiers » doit nommer **toute primitive qui exécute effectivement**. Le critère est **factuel, pas historique** : une forme entre parce qu'elle lance du code tiers, **jamais** parce qu'un cycle antérieur l'a rencontrée.

Il **aurait pu exclure** `Popen` : la variante rejetée était — la règle nomme les formes déjà observées en usage — un critère **historique**, qui aurait laissé `Popen` dehors.
Le principe retenu étant **factuel**, `Popen` entre.

## Les rapiéçages de cette règle

- amendements successifs : **3**

- **#494** — `subprocess.run([sys.executable, …])` — la règle d'origine ;
- **#495** — découvre l'exécution **en process** (`import nonml_x ; x.main()`) ;
- **#496** — ajoute la condition 2 ; son audit découvre `subprocess.Popen` ;

> Chaque cycle rattrapait la forme que le précédent avait manquée.
> **Ce recensement compte les 12 d'un coup, zéros compris.**

## Les 12 primitives, comptées séparément

- scripts `nonml_*.py` analysés : **971**

| # | Primitive | Scripts | Appels |
|---|---|---|---|
| P1 | `subprocess.run([sys.executable, …])` | **23** | **24** |
| P2 | `subprocess.Popen([sys.executable, …])` | **3** | **3** |
| P3 | `subprocess.call` / `check_call` / `check_output` sur `sys.executable` | **0** | **0** |
| P4 | `os.system(…)` | **0** | **0** |
| P5 | `os.popen(…)` | **0** | **0** |
| P6 | `os.execv*` / `os.spawn*` | **0** | **0** |
| P7 | `runpy.run_path` / `runpy.run_module` | **0** | **0** |
| P8 | `exec(open(…).read())` ou `eval` sur un fichier | **0** | **0** |
| P9 | `importlib` (`spec_from_file_location`, `import_module`) sur `scripts/` | **1** | **1** |
| P10 | `import nonml_* as a` + `a.main()` — l'exécution en process du #495 | **8** | **10** |
| P11 | `from nonml_* import main` + `main()` | **0** | **0** |
| P12 | `multiprocessing.Process(target=…)` | **0** | **0** |

- primitives **jamais employées** : **8** (P3, P4, P5, P6, P7, P8, P11, P12)

## Le recompte, et son écart avec le #496

Les chiffres du #496 sont **lus dans son rapport**, pas retapés ici.

| Grandeur | #496 | #497 | Écart |
|---|---|---|---|
| scripts exécutants | **30** | **33** | **+3** |
| angle mort du #494 | **8** | **10** | **+2** |
| cibles distinctes | **11** | **12** | **+1** |
| témoins « exécute un tiers » | **4** | **4** | **+0** |

## Les quatre témoins sous la règle amendée

| Témoin | Primitives déclenchées |
|---|---|
| `nonml_battery_coverage_backtest.py` | P1 |
| `nonml_net_pnl_correction_backtest.py` | P10 |
| `nonml_six_reports_regeneration_backtest.py` | P1 |
| `nonml_sweep_pass_prose_fix_backtest.py` | P10 |

## Les cibles

- cibles distinctes : **12**

| Cible | Appels |
|---|---|
| `(chemin en variable)` | **10** |
| `_backtest.py` | **9** |
| `nonml_pnl_duplicate_sweep_backtest.py` | **8** |
| `nonml_capitulation_gate_floor_sweep_backtest.py` | **3** |
| `importlib.util.spec_from_file_location` | **1** |
| `nonml_backlog_figures_verification_backtest.py` | **1** |
| `nonml_content_defined_magnitudes_backtest.py` | **1** |
| `nonml_empty_pass_requalification_backtest.py` | **1** |
| `nonml_prereg_convention_coverage_backtest.py` | **1** |
| `nonml_repo_magnitudes_recount_backtest.py` | **1** |
| `nonml_self_inclusion_detector_backtest.py` | **1** |
| `nonml_self_inclusion_detector_v2_backtest.py` | **1** |

Une cible n'est **pas toujours nommable statiquement** : les entrées
`(… en variable)` sont des appels dont l'AST ne voit pas la destination.
Elles sont publiées **telles quelles** — les retirer flatterait le compte.

## Mes prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| le recompte donne 32 exécutants | 32 | 33 | **réfutée** |
| ≥ 1 primitive hors P1/P2/P9/P10 employée | ≥ 1 | 0 | **réfutée** |
| les 4 témoins restent classés | 4 | 4 | **vérifiée** |

### Les deux premières sont réfutées **ensemble**

Le pré-enregistrement affirmait que les prédictions 1 et 2 étaient
**mutuellement exclusives par construction** : l'une devait tomber,
pas les deux. **Elles tombent toutes les deux.**

> **Ma construction était fausse.** Elle supposait que le seul écart
> possible au « 30 + 2 » venait d'une primitive inconnue. Il venait
> d'ailleurs : **le « + 2 » lui-même était faux.**

**Aucune** primitive hors P1/P2/P9/P10 n'est employée : les huit
autres valent **zéro**. Le recensement n'a rien découvert — et c'est
**exactement ce qu'un recensement doit pouvoir donner** : sans lui,
l'absence n'était pas établie, seulement supposée.

## D'où vient l'écart — réconciliation nom par nom

La règle du #496 se reconstruit ici comme **P1 ∪ P9 ∪ P10** (ses
conditions 1, 3 et 2). Tout script exécutant hors de cet ensemble est
**nouveau**, et il est nommé :

- exécutants sous la règle du #496 reconstruite : **30**
- exécutants supplémentaires sous la règle amendée : **3**

- `nonml_reproducibility_campaign_v3_lot2_backtest.py` → P2
- `nonml_reproducibility_campaign_v3_lot3_backtest.py` → P2
- `nonml_selfref_reports_marking_backtest.py` → P2

- résidu inexpliqué : **0**

> **L'audit du #496 avait compté 2 script(s) `Popen` ; il
> y en a 3.** Ce compte venait de sa route **regex**, et
> une route textuelle se trompe **une fois de plus** là où l'AST voit
> juste. **Ma prédiction 1 reposait sur ce chiffre emprunté sans le
> refaire** — c'est ce qui l'a fait tomber, pas une primitive exotique.

## Aucune exécution

- primitives d'exécution **d'un tiers du dépôt** dans ma source : **0**
  *(mes propres appels `subprocess` ne visent que `git`, jamais `sys.executable`)*
- fichiers modifiés par ce cycle hors les siens : **0**

## Critères de succès

1. Principe d'inclusion cité verbatim, avec la variante qui aurait exclu `Popen` — **OUI**.
2. Les **12** primitives comptées séparément, **8** zéros publiés — **OUI**.
3. Recompte publié avec son écart vs le #496 sur les quatre grandeurs — **OUI**.
4. Rapiéçages nommés et comptés (**3**) — **OUI**.
5. Aucun script exécuté, arbre vérifié propre — **OUI**.

**PASS** — le critère porte sur le **procédé**, pas sur un rendement.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution.

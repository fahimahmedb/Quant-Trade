# La règle contextuelle du #502 devant un **témoin de permutation**

Les **#512** et **#513** ont montré qu'un détecteur peut produire un
chiffre entier sans rien mesurer. **Aucun détecteur des #500-#511 n'avait
subi ce test** — et l'un d'eux n'est pas un détecteur parmi d'autres.

La règle contextuelle du #502 — **≥ 2 mots-clés dans
±200 caractères** — est le **socle partagé** de **#502**, **#503**, **#504**, **#505**, **#508**, **#509**.

## Le témoin, cité verbatim

> Pour chaque emprunt, on rejoue **exactement la même règle** en
> remplaçant ses mots-clés par ceux de **l'emprunt suivant** dans la
> population triée par `(script, cycle cité, valeur)` — le dernier
> reprenant ceux du premier.

**Dérangement déterministe** : aucun tirage, aucun aléa. Un emprunt
confirmé avec les mots-clés **d'un autre** l'est par **coïncidence de
vocabulaire**, pas par identité de sujet.

## Les deux taux

- emprunts : **39**

| Mots-clés employés | Confirmés « au sujet » | Taux |
|---|---|---|
| **réels** | **37** | **94,9 %** |
| **permutés** (témoin) | **25** | **64,1 %** |

- **écart** : **+30,8** points — seuil exigé : **20**
- verdict : **LA RÈGLE DISCRIMINE**

> **La règle du #502 survit à son témoin.** Un emprunt confirmé avec
> ses propres mots-clés l'est plus souvent qu'avec ceux d'un voisin :
> elle mesure bien une **identité de sujet**, et **les conclusions
> des cycles qui en dépendent tiennent.**

### Mais elle est **crédule**, et le seuil ne le dit pas

- confirmations obtenues avec des mots-clés **étrangers** : **25** sur **39** (**64,1 %**)
- **spécificité** de la règle — part d'emprunts que le témoin
  **n'arrive pas** à confirmer : **35,9 %**

> Passer le seuil de **20 points** n'est pas être fiable. **Près de
> deux emprunts sur trois se laissent confirmer par le vocabulaire
> d'un voisin.** La règle discrimine — elle ne prouve pas.
>
> Les cycles #502-#509 avaient déjà écrit, chacun, que leur
> appariement ne valait pas identité de sujet. **Ce chiffre donne
> enfin la mesure de cette réserve** : elle valait, en gros, deux
> confirmations sur trois.

## Les faux positifs de la permutation, nommés

- effectif : **25**

| Script | Cite | Nombre | Confirmé (permuté) dans |
|---|---|---|---|
| `nonml_citer_451_definition_backtest.py` | `#472` | **0** | `nonml_borrowed_figures_census_result.md` |
| `nonml_citer_451_resolution_backtest.py` | `#469` | **0** | `nonml_battery_witness_hoist_audit.md` |
| `nonml_content_defined_magnitudes_audit.py` | `#449` | **2** | `#457` |
| `nonml_content_defined_magnitudes_backtest.py` | `#449` | **6** | `#465` |
| `nonml_content_defined_magnitudes_backtest.py` | `#451` | **6** | `PREREG_repo_magnitudes_recount.md` |
| `nonml_declaration_convention_decay_backtest.py` | `#486` | **0** | `#492` |
| `nonml_declaration_convention_decay_backtest.py` | `#486` | **33** | `PREREG_pnl_duplicate_sweep.md` |
| `nonml_dsr_corrected_trials_backtest.py` | `#445` | **3** | `#477` |
| `nonml_duplicate_sweep_coverage_audit.py` | `#427` | **1** | `#428` |
| `nonml_hardcoded_figures_remainder_backtest.py` | `#474` | **1** | `#428` |
| `nonml_hardcoded_figures_sweep_backtest.py` | `#451` | **1** | `nonml_hardcoded_figures_remainder_result.md` |
| `nonml_hardcoded_figures_sweep_backtest.py` | `#451` | **1** | `#476` |
| `nonml_hardcoded_tables_repair_backtest.py` | `#479` | **17** | `nonml_hardcoded_tables_repair_result.md` |
| `nonml_hardcoded_tables_repair_backtest.py` | `#479` | **17** | `nonml_hardcoded_figures_remainder_result.md` |
| `nonml_hardcoded_tables_repair_backtest.py` | `#479` | **18** | `nonml_hardcoded_tables_repair_result.md` |
| `nonml_marker_emitted_by_scripts_backtest.py` | `#450` | **4** | `nonml_battery_coverage_result.md` |
| `nonml_orphan_npz_inspection_backtest.py` | `#442` | **20** | `nonml_hardcoded_figures_remainder_result.md` |
| `nonml_orphans_interrupted_or_lost_backtest.py` | `#464` | **10** | `#464` |
| `nonml_reproducibility_sample_lot2_audit.py` | `#434` | **8,0** | `nonml_hardcoded_figures_remainder_result.md` |
| `nonml_self_inclusion_detector_backtest.py` | `#463` | **16** | `nonml_hardcoded_figures_remainder_result.md` |

*(et **5** autres.)*

> Ce sont les confirmations que la règle produit **par construction**,
> sans rapport avec le sujet de l'emprunt. Leur nombre est la mesure
> directe de sa **crédulité**.

## Ce que ce cycle **ne** teste **pas**

Il n'examine **que** la règle contextuelle. Les autres détecteurs des
**#500-#511** — appariement AST des chaînes publiées (#500), lecture des
chiffres en gras (#501), primitives d'exécution (#497) — **restent non
testés**. Le rappeler vaut mieux que laisser croire à un examen complet.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| écart ≥ 20 points | ≥ 20 | +30,8 | **vérifiée** |
| taux permuté > 0 | > 0 | 64,1 % | **vérifiée** |
| < 10 faux positifs | < 10 | 25 | **réfutée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Population, mots-clés et fenêtres sont **importés** des backtests des
#500, #501, #502 et #508 — leurs fonctions, jamais leur `main()`.

## Critères de succès

1. Règle de permutation et seuil de **20** points cités verbatim — **OUI**.
2. Les deux taux publiés avec leurs effectifs (**37** / **25**) — **OUI**.
3. Écart publié et verdict rendu au seuil — **OUI**.
4. Faux positifs nommés individuellement (**25**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**. **Il ne dépend pas
du succès de la règle testée**, seulement de la publication honnête du
verdict.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts, du
> registre et des rapports à la date de son exécution.

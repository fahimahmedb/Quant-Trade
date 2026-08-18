# **Publier** les témoins de classe A (pré-enregistré)

Le **#494** a établi que ces deux scripts n'exécutent aucun tiers et
n'écrivent que **leur propre rapport**. Leur témoin est dans le code
depuis les #487/#489 et **n'a jamais paru**.

> **La décision a été prise dans le pré-enregistrement** : j'accepte un
> diff non borné au témoin, **à condition de le publier en entier et
> d'attribuer chaque ligne**. Un rapport dont les chiffres bougent en
> silence serait pire que le témoin manquant.

## La prémisse du cycle est fausse — et c'est le résultat

Le #494 avait classé ces deux scripts **A — exécutable sans danger**, sa
règle cherchant `subprocess.run([sys.executable, …])`. **Elle ne voit pas
l'exécution en process.**

| Script | Modules du dépôt importés | Appels `.main()` |
|---|---|---|
| `nonml_net_pnl_correction_backtest.py` | `nonml_pnl_duplicate_sweep_backtest` | **[222]** |
| `nonml_sweep_pass_prose_fix_backtest.py` | `nonml_pnl_duplicate_sweep_backtest` | **[72, 76, 251]** |

> **Les 2 importent un script du dépôt et appellent
> son `main()`.** Ils **exécutent** bien un tiers — simplement pas par
> `subprocess`. **Ils sont de classe C, pas A.**

`net_pnl_correction` l'écrit même dans son propre rapport :
*« corrigé **par ricochet** puisqu'il appelle `sw.main()` »*.
**Personne ne l'avait lu.**

### Ce que cela fait à la chaîne #487 → #494 → #495

- le **#487** a refusé d'exécuter `sweep_pass_prose_fix` — **il avait
  raison**, mais son motif écrit (« écrit 2 fichiers ») était faux ;
- le **#494** a déclaré ce motif faux — **c'était exact** — et en a
  conclu que le script était sans danger : **c'était faux** ;
- le **#495** exécute, et découvre que le refus initial était fondé
  **pour une troisième raison** que ni l'un ni l'autre n'avait vue.

> **Trois cycles, trois motifs, un seul geste juste : ne pas
> exécuter.** L'instinct du #487 valait mieux que les deux
> raisonnements qui l'ont suivi.

## Les deux exécutions

| Script | État | Passage 1 | Passage 2 | Témoin présent | Lignes de diff |
|---|---|---|---|---|---|
| `nonml_net_pnl_correction_backtest.py` | idempotent | `a0053678c1e790` | `a0053678c1e790` | **OUI** | 84 |
| `nonml_sweep_pass_prose_fix_backtest.py` | idempotent | `892c98f9bb8999` | `892c98f9bb8999` | **OUI** | 175 |

## `nonml_net_pnl_correction_result.md` — diff complet

**84 lignes**, publiées **en entier** :

```diff
--- committé
+++ régénéré
@@ -25,2 +25,2 @@
-- séries lues **avant** : **218**
-- séries lues **après** : **218**
+- séries lues **avant** : **219**
+- séries lues **après** : **219**
@@ -59,2 +59,2 @@
-- lignes avant : **96** — lignes après : **92** (écart -4)
-- lignes **modifiées** : **10**
+- lignes avant : **96** — lignes après : **133** (écart +37)
+- lignes **modifiées** : **58**
@@ -62 +62 @@
-**1 ligne imputable à la correction ; 9 à la dérive du
+**1 ligne imputable à la correction ; 57 à la dérive du
@@ -69,10 +69,42 @@
-| 28 | dérive | `| scripts de backtest non-ML du dépôt | **284** |` | `| scripts de backtest non-ML du dépôt | **298** |` |
-| 29 | dérive | `| **couverture non-ML** | **73.2 %** |` | `| **couverture non-ML** | **69.8 %** |` |
-| 31 | dérive | `**La soustraction 284 − 208 ne compte rien de réel** : les deux` | `**La soustraction 298 − 208 ne compte rien de réel** : les deux` |
-| 36 | dérive | `> **99** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` | `> **113** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` |
-| 43 | dérive | `| FAIL | **90** |` | `| FAIL | **91** |` |
-| 44 | dérive | `| PASS | **2** |` | `| PASS | **4** |` |
-| 45 | dérive | `| indéterminé | **6** |` | `| indéterminé | **17** |` |
-| 48 | dérive | `Les **90** FAIL ne peuvent pas changer de verdict, mais un doublon` | `Les **91** FAIL ne peuvent pas changer de verdict, mais un doublon` |
-| 50 | dérive | `**2** PASS sont les deux candidats écartés au #427 avec leur raison` | `**4** PASS sont les deux candidats écartés au #427 avec leur raison` |
-| 58 | **correction** | `Répartition par schéma : indiciel (182), panier (21), deux jambes (13), candidat+turnover (1), ` | `Répartition par schéma : indiciel (182), panier (21), deux jambes (13), candidat seul (2).` |
+| 10 | dérive | `- fichiers `*_pnl.npz` trouvés : **218**` | `- fichiers `*_pnl.npz` trouvés : **219**` |
+| 11 | dérive | `- P&L reconstruits : **218**` | `- P&L reconstruits : **219**` |
+| 25 | dérive | `| séries lues (`results/*_pnl.npz`) | **218** |` | `| séries lues (`results/*_pnl.npz`) | **219** |` |
+| 26 | dérive | `| dont candidats non-ML (`nonml_*`) | **208** |` | `| dont candidats non-ML (`nonml_*`) | **209** |` |
+| 28 | dérive | `| scripts de backtest non-ML du dépôt | **284** |` | `| scripts de backtest non-ML du dépôt | **348** |` |
+| 29 | dérive | `| **couverture non-ML** | **73.2 %** |` | `| **couverture non-ML** | **60.1 %** |` |
+| 31 | dérive | `**La soustraction 284 − 208 ne compte rien de réel** : les deux` | `**La soustraction 348 − 209 ne compte rien de réel** : les deux` |
+| 36 | dérive | `> **99** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` | `> **162** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` |
+| 43 | dérive | `| FAIL | **90** |` | `| FAIL | **95** |` |
+| 44 | dérive | `| PASS | **2** |` | `| PASS | **38** |` |
+| 45 | dérive | `| indéterminé | **6** |` | `| indéterminé | **28** |` |
+| 48 | dérive | `Les **90** FAIL ne peuvent pas changer de verdict, mais un doublon` | `Les **95** FAIL ne peuvent pas changer de verdict, mais un doublon` |
+| 50 | dérive | `**2** PASS sont les deux candidats écartés au #427 avec leur raison` | `Les **38** PASS sans `.npz` sont nommés ici plutôt` |
+| 51 | dérive | `publiée (variantes multiples, et un diagnostic qui n'est pas une stratégie).` | `qu'affirmés — la version précédente les disait « les deux candidats écartés` |
+| 52 | dérive | `` | `au #427 », phrase figée qu'un compte calculé a fini par démentir (#446) :` |
+| 53 | dérive | `Le balayage lit `results/*_pnl.npz` **sans filtre de préfixe** : les 10 séries` | `` |
+| 54 | dérive | `ML / Étape D sont comparées aux candidats non-ML. C'est voulu — un doublon` | `- `backlog_figures_verification`` |
+| 55 | dérive | `inter-familles est une information — mais il faut le savoir pour lire les groupes` | `- `battery_indet_hoist_declared`` |
+| 56 | dérive | `ci-dessous, dont l'un associe précisément une série d'Étape D à un candidat non-ML.` | `- `battery_witness_hoist`` |
+| 57 | dérive | `` | `- `citer_451_definition`` |
+| 58 | **correction** | `Répartition par schéma : indiciel (182), panier (21), deux jambes (13), candidat+turnover (1), ` | `- `citer_451_resolution`` |
+| 59 | dérive | `` | `- `class_a_witness_publication`` |
+| 60 | dérive | `## Doublons exacts` | `- `conditional_sections_sweep`` |
+| 61 | dérive | `` | `- `content_defined_magnitudes`` |
+| 62 | dérive | `- paires à P&L **bit-à-bit identique** : **3**` | `- `declaration_convention_dating`` |
+| 63 | dérive | `- groupes de doublons : **3**` | `- `declaration_convention_decay`` |
+| 64 | dérive | `- entrées surnuméraires (essais comptés en trop) : **3**` | `- `duplicate_sweep_irreparability`` |
+| 65 | dérive | `` | `- `guards_without_witness`` |
+| 66 | dérive | `- **groupe de 2** : `etape_D_overlay_optimized`, `nonml_etape_d_garch_defensive_overlay`` | `- `guards_witness_remainder`` |
+| 67 | dérive | `- **groupe de 2** : `nonml_leaders_trend_union_overlay`, `nonml_sma200_leaders_overlay`` | `- `hardcoded_figures_remainder`` |
+| 68 | dérive | `- **groupe de 2** : `nonml_leaders_trend_union_overlay_pit_universe`, `nonml_sma200_leaders_ove` | `- `hardcoded_figures_sweep`` |
+| 69 | dérive | `` | `- `hardcoded_tables_repair`` |
+| 70 | dérive | `## Quasi-doublons (corrélation ≥ seuil, non identiques)` | `- `idempotence_famille_capable`` |
+| 71 | dérive | `` | `- `idempotence_lot2`` |
+| 72 | dérive | `- paires signalées : **1**` | `- `irreparability_justifications_audit`` |
+| 73 | dérive | `` | `- `irreparable_figures_census`` |
+| 74 | dérive | `| Candidat A | Candidat B | Corrélation |` | `- `marker_emitted_by_scripts`` |
+| 75 | dérive | `|---|---|---|` | `- `marker_emitter_crossing`` |
+| 76 | dérive | `| `nonml_momentum_breadth_vol_targeting_overlay` | `nonml_sma200_momentum_breadth_and_overlay` ` | `- `masking_guards_witness_patch`` |
+| 77 | dérive | `` | `- `orphan_audits_declared_reading`` |
+
+*(les 18 lignes suivantes ne sont pas listées)*
@@ -86,14 +118 @@
-### Une incohérence exposée par le rafraîchissement
-
-Le rapport régénéré contient désormais :
-
-> **4** PASS sont les deux candidats écartés au #427 avec leur raison
-
-Le compte est **calculé**, la prose (« les deux ») est **figée**. Tant que
-le compte valait 2, la phrase était juste ; la dérive du dépôt l'a rendue
-fausse. Ce n'est **pas** un effet de ma correction.
-
-**Je ne la corrige pas ici.** Le pré-enregistrement n'autorisait qu'une
-modification, aux lignes 40-42 d'un autre fichier ; toucher à cette
-phrase serait une modification non déclarée — exactement ce que le
-régime de modification annoncé interdit. Elle est **inscrite à la file**.
+- incohérences prose/compte exposées par le rafraîchissement : **0**
```

### Attribution

- lignes **imputables au témoin** : **1**
- lignes **imputables à la dérive du dépôt** : **76**

| Ligne modifiée | Attribution |
|---|---|
| `-- séries lues **avant** : **218**` | dérive |
| `-- séries lues **après** : **218**` | dérive |
| `+- séries lues **avant** : **219**` | dérive |
| `+- séries lues **après** : **219**` | dérive |
| `-- lignes avant : **96** — lignes après : **92** (écart -4)` | dérive |
| `-- lignes **modifiées** : **10**` | dérive |
| `+- lignes avant : **96** — lignes après : **133** (écart +37)` | dérive |
| `+- lignes **modifiées** : **58**` | dérive |
| `-**1 ligne imputable à la correction ; 9 à la dérive du` | dérive |
| `+**1 ligne imputable à la correction ; 57 à la dérive du` | dérive |
| `-| 28 | dérive | `| scripts de backtest non-ML du dépôt | **284** |` | `| scripts de backtest no` | dérive |
| `-| 29 | dérive | `| **couverture non-ML** | **73.2 %** |` | `| **couverture non-ML** | **69.8 %*` | dérive |
| `-| 31 | dérive | `**La soustraction 284 − 208 ne compte rien de réel** : les deux` | `**La soust` | dérive |
| `-| 36 | dérive | `> **99** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` | `>` | dérive |
| `-| 43 | dérive | `| FAIL | **90** |` | `| FAIL | **91** |` |` | dérive |
| `-| 44 | dérive | `| PASS | **2** |` | `| PASS | **4** |` |` | dérive |
| `-| 45 | dérive | `| indéterminé | **6** |` | `| indéterminé | **17** |` |` | dérive |
| `-| 48 | dérive | `Les **90** FAIL ne peuvent pas changer de verdict, mais un doublon` | `Les **9` | dérive |
| `-| 50 | dérive | `**2** PASS sont les deux candidats écartés au #427 avec leur raison` | `**4** ` | dérive |
| `-| 58 | **correction** | `Répartition par schéma : indiciel (182), panier (21), deux jambes (13)` | dérive |
| `+| 10 | dérive | `- fichiers `*_pnl.npz` trouvés : **218**` | `- fichiers `*_pnl.npz` trouvés : ` | dérive |
| `+| 11 | dérive | `- P&L reconstruits : **218**` | `- P&L reconstruits : **219**` |` | dérive |
| `+| 25 | dérive | `| séries lues (`results/*_pnl.npz`) | **218** |` | `| séries lues (`results/*_` | dérive |
| `+| 26 | dérive | `| dont candidats non-ML (`nonml_*`) | **208** |` | `| dont candidats non-ML (`` | dérive |
| `+| 28 | dérive | `| scripts de backtest non-ML du dépôt | **284** |` | `| scripts de backtest no` | dérive |
| `+| 29 | dérive | `| **couverture non-ML** | **73.2 %** |` | `| **couverture non-ML** | **60.1 %*` | dérive |
| `+| 31 | dérive | `**La soustraction 284 − 208 ne compte rien de réel** : les deux` | `**La soust` | dérive |
| `+| 36 | dérive | `> **99** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` | `>` | dérive |
| `+| 43 | dérive | `| FAIL | **90** |` | `| FAIL | **95** |` |` | dérive |
| `+| 44 | dérive | `| PASS | **2** |` | `| PASS | **38** |` |` | dérive |
| `+| 45 | dérive | `| indéterminé | **6** |` | `| indéterminé | **28** |` |` | dérive |
| `+| 48 | dérive | `Les **90** FAIL ne peuvent pas changer de verdict, mais un doublon` | `Les **9` | dérive |
| `+| 50 | dérive | `**2** PASS sont les deux candidats écartés au #427 avec leur raison` | `Les **` | dérive |
| `+| 51 | dérive | `publiée (variantes multiples, et un diagnostic qui n'est pas une stratégie).` ` | dérive |
| `+| 52 | dérive | `` | `au #427 », phrase figée qu'un compte calculé a fini par démentir (#446) :` | dérive |
| `+| 53 | dérive | `Le balayage lit `results/*_pnl.npz` **sans filtre de préfixe** : les 10 séries` | dérive |
| `+| 54 | dérive | `ML / Étape D sont comparées aux candidats non-ML. C'est voulu — un doublon` | ` | dérive |
| `+| 55 | dérive | `inter-familles est une information — mais il faut le savoir pour lire les grou` | dérive |
| `+| 56 | dérive | `ci-dessous, dont l'un associe précisément une série d'Étape D à un candidat no` | dérive |
| `+| 57 | dérive | `` | `- `citer_451_definition`` |` | dérive |
| *… et 36 autres* | dérive |

## `nonml_sweep_pass_prose_fix_result.md` — diff complet

**175 lignes**, publiées **en entier** :

```diff
--- committé
+++ régénéré
@@ -5,0 +6 @@
+- PASS qui sont des **stratégies** et non des scripts d'inventaire : **32**
@@ -12,3 +13,34 @@
-**C'est le cas de 1 sur 4 :**
-
-- **`tom_decomposition_overlay`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+**C'est le cas de 32 sur 38 :**
+
+- **`backlog_figures_verification`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`battery_indet_hoist_declared`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`battery_witness_hoist`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`citer_451_definition`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`citer_451_resolution`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`class_a_witness_publication`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`conditional_sections_sweep`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`content_defined_magnitudes`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`declaration_convention_dating`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`declaration_convention_decay`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`duplicate_sweep_irreparability`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`guards_without_witness`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`guards_witness_remainder`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`hardcoded_figures_remainder`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`hardcoded_figures_sweep`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`idempotence_famille_capable`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`idempotence_lot2`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`irreparability_justifications_audit`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`irreparable_figures_census`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`marker_emitter_crossing`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`orphan_audits_declared_reading`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`orphan_audits_fate`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`orphan_cycles_entries`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`orphans_interrupted_or_lost`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`prereg_convention_coverage`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`repo_magnitudes_recount`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`report_idempotence`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`self_inclusion_detector`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`self_inclusion_detector_v2`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`self_inclusion_repair`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`six_reports_emitter_inconsistency`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
+- **`unpublished_witnesses_paths`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au balayage de doublons**
@@ -44,3 +76 @@
-- insertions : **23** — suppressions : **2**
-- hunks du diff : **1**
-  - `-194,2 +194,23`
+- hunks du diff : **0**
@@ -65,2 +95,2 @@
-- lignes avant : **92** — après : **99**
-- lignes réellement ajoutées ou retirées : **21** — dont **11** au bloc, **10** à la dérive du dépôt
+- lignes avant : **92** — après : **133**
+- lignes réellement ajoutées ou retirées : **73** — dont **45** au bloc, **28** à la dérive du dépôt
@@ -69,0 +100,8 @@
+| retirée | dérive | `- fichiers `*_pnl.npz` trouvés : **218**` |
+| retirée | dérive | `- P&L reconstruits : **218**` |
+| ajoutée | dérive | `- fichiers `*_pnl.npz` trouvés : **219**` |
+| ajoutée | dérive | `- P&L reconstruits : **219**` |
+| retirée | dérive | `| séries lues (`results/*_pnl.npz`) | **218** |` |
+| retirée | dérive | `| dont candidats non-ML (`nonml_*`) | **208** |` |
+| ajoutée | dérive | `| séries lues (`results/*_pnl.npz`) | **219** |` |
+| ajoutée | dérive | `| dont candidats non-ML (`nonml_*`) | **209** |` |
@@ -72,2 +110,2 @@
-| ajoutée | dérive | `| scripts de backtest non-ML du dépôt | **299** |` |
-| ajoutée | dérive | `| **couverture non-ML** | **69.6 %** |` |
+| ajoutée | dérive | `| scripts de backtest non-ML du dépôt | **348** |` |
+| ajoutée | dérive | `| **couverture non-ML** | **60.1 %** |` |
@@ -75 +113 @@
-| ajoutée | dérive | `**La soustraction 299 − 208 ne compte rien de réel** : les deux` |
+| ajoutée | dérive | `**La soustraction 348 − 209 ne compte rien de réel** : les deux` |
@@ -77 +115,4 @@
-| ajoutée | dérive | `> **114** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` |
+| ajoutée | dérive | `> **162** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et` |
+| retirée | dérive | `| FAIL | **91** |` |
+| retirée | dérive | `| PASS | **4** |` |
+| retirée | dérive | `| indéterminé | **17** |` |
@@ -78,0 +120,3 @@
+| ajoutée | dérive | `| FAIL | **94** |` |
+| ajoutée | dérive | `| PASS | **38** |` |
+| ajoutée | dérive | `| indéterminé | **28** |` |
@@ -79,0 +124,2 @@
+| retirée | dérive | `Les **91** FAIL ne peuvent pas changer de verdict, mais un doublon` |
+| ajoutée | dérive | `Les **94** FAIL ne peuvent pas changer de verdict, mais un doublon` |
@@ -82 +128 @@
-| ajoutée | **bloc** | `Les **4** PASS sans `.npz` sont nommés ici plutôt` |
+| ajoutée | **bloc** | `Les **38** PASS sans `.npz` sont nommés ici plutôt` |
@@ -84,7 +130,2 @@
-| ajoutée | **bloc** | `au #427 », phrase figée qu'un compte calculé a fini par démentir (#446) :` |
-| ajoutée | **bloc** | `` |
-| ajoutée | **bloc** | `- `capitulation_gate_floor_sweep`` |
-| ajoutée | **bloc** | `- `npz_report_consistency_baskets`` |
-| ajoutée | **bloc** | `- `protocol_inventory`` |
-| ajoutée | **bloc** | `- `tom_decomposition_overlay`` |
-| ajoutée | **bloc** | `` |
+
+*(les 43 lignes suivantes ne sont pas listées)*
@@ -109,6 +150,40 @@
-**4** scripts nommés par la phrase nouvelle :
-
-- `capitulation_gate_floor_sweep`
-- `npz_report_consistency_baskets`
-- `protocol_inventory`
-- `tom_decomposition_overlay`
+**38** scripts nommés par la phrase nouvelle :
+
+- `backlog_figures_verification`
+- `battery_indet_hoist_declared`
+- `battery_witness_hoist`
+- `citer_451_definition`
+- `citer_451_resolution`
+- `class_a_witness_publication`
+- `conditional_sections_sweep`
+- `content_defined_magnitudes`
+- `declaration_convention_dating`
+- `declaration_convention_decay`
+- `duplicate_sweep_irreparability`
+- `guards_without_witness`
+- `guards_witness_remainder`
+- `hardcoded_figures_remainder`
+- `hardcoded_figures_sweep`
+- `hardcoded_tables_repair`
+- `idempotence_famille_capable`
+- `idempotence_lot2`
+- `irreparability_justifications_audit`
+- `irreparable_figures_census`
+- `marker_emitted_by_scripts`
+- `marker_emitter_crossing`
+- `masking_guards_witness_patch`
+- `orphan_audits_declared_reading`
+- `orphan_audits_fate`
+- `orphan_cycles_entries`
+- `orphans_interrupted_or_lost`
+- `prereg_convention_coverage`
+- `repo_magnitudes_recount`
+- `report_idempotence`
+- `self_inclusion_detector`
+- `self_inclusion_detector_v2`
+- `self_inclusion_repair`
+- `six_reports_emitter_inconsistency`
+- `six_reports_regeneration`
+- `tom_decomposition_npz`
+- `unpublished_witnesses_paths`
+- `verdict_detector_complete`
@@ -128,22 +203,4 @@
-- noms publiés avant auto-inclusion : **4** — `capitulation_gate_floor_sweep`, `npz_report_consistency_baskets`, `protocol_inventory`, `tom_decomposition_overlay`
-- noms publiés après : **5** — `capitulation_gate_floor_sweep`, `npz_report_consistency_baskets`, `protocol_inventory`, `sweep_pass_prose_fix`, `tom_decomposition_overlay`
-
-**NON stable.** Le rapport de ce cycle s'ajoute lui-même à la liste : `sweep_pass_prose_fix`.
-
-### Le défaut que ma propre correction a mis au jour
-
-Ce n'est pas un accident de nommage. Le balayage détecte un PASS par
-`"**PASS" in t` — **n'importe où** dans le rapport. Le rapport de ce cycle
-contient la phrase « stratégie portant un **PASS** » à propos d'un *autre*
-candidat : il est donc compté comme un PASS.
-
-**Le détecteur de verdict du balayage confond « porter un PASS » et
-« parler d'un PASS ».** Tout rapport d'inventaire qui commente un PASS est
-compté comme candidat PASS.
-
-La correction de prose de ce cycle est correcte ; elle a rendu **visible**
-un défaut plus profond, en nommant ce qui n'était jusque-là qu'un compte.
-C'est l'argument même du cycle : nommer ce qu'on compte.
-
-**Non corrigé ici** — hors du bloc annoncé. **Inscrit en tête de file.**
-
+- noms publiés avant auto-inclusion : **38** — `backlog_figures_verification`, `battery_indet_hoist_declared`, `battery_witness_hoist`, `citer_451_definition`, `citer_451_resolution`, `class_a_witness_publication`, `conditional_sections_sweep`, `content_defined_magnitudes`, `declaration_convention_dating`, `declaration_convention_decay`, `duplicate_sweep_irreparability`, `guards_without_witness`, `guards_witness_remainder`, `hardcoded_figures_remainder`, `hardcoded_figures_sweep`, `hardcoded_tables_repair`, `idempotence_famille_capable`, `idempotence_lot2`, `irreparability_justifications_audit`, `irreparable_figures_census`, `marker_emitted_by_scripts`, `marker_emitter_crossing`, `masking_guards_witness_patch`, `orphan_audits_declared_reading`, `orphan_audits_fate`, `orphan_cycles_entries`, `orphans_interrupted_or_lost`, `prereg_convention_coverage`, `repo_magnitudes_recount`, `report_idempotence`, `self_inclusion_detector`, `self_inclusion_detector_v2`, `self_inclusion_repair`, `six_reports_emitter_inconsistency`, `six_reports_regeneration`, `tom_decomposition_npz`, `unpublished_witnesses_paths`, `verdict_detector_complete`
+- noms publiés après : **38** — `backlog_figures_verification`, `battery_indet_hoist_declared`, `battery_witness_hoist`, `citer_451_definition`, `citer_451_resolution`, `class_a_witness_publication`, `conditional_sections_sweep`, `content_defined_magnitudes`, `declaration_convention_dating`, `declaration_convention_decay`, `duplicate_sweep_irreparability`, `guards_without_witness`, `guards_witness_remainder`, `hardcoded_figures_remainder`, `hardcoded_figures_sweep`, `hardcoded_tables_repair`, `idempotence_famille_capable`, `idempotence_lot2`, `irreparability_justifications_audit`, `irreparable_figures_census`, `marker_emitted_by_scripts`, `marker_emitter_crossing`, `masking_guards_witness_patch`, `orphan_audits_declared_reading`, `orphan_audits_fate`, `orphan_cycles_entries`, `orphans_interrupted_or_lost`, `prereg_convention_coverage`, `repo_magnitudes_recount`, `report_idempotence`, `self_inclusion_detector`, `self_inclusion_detector_v2`, `self_inclusion_repair`, `six_reports_emitter_inconsistency`, `six_reports_regeneration`, `tom_decomposition_npz`, `unpublished_witnesses_paths`, `verdict_detector_complete`
+
+**Stable.** L'auto-inclusion ne change pas la liste.
@@ -154 +211 @@
-| 1 | diff confiné au bloc annoncé | ✔ |
+| 1 | diff confiné au bloc annoncé | **non** |
@@ -156 +213 @@
-| 3 | rapport idempotent | **NON** |
+| 3 | rapport idempotent | ✔ |
```

### Attribution

- lignes **imputables au témoin** : **1**
- lignes **imputables à la dérive du dépôt** : **156**

| Ligne modifiée | Attribution |
|---|---|
| `-**C'est le cas de 1 sur 4 :**` | dérive |
| `-` | dérive |
| `-- **`tom_decomposition_overlay`** — stratégie portant un **PASS**, sans `.npz`, donc **invisibl` | dérive |
| `+**C'est le cas de 32 sur 38 :**` | dérive |
| `+` | dérive |
| `+- **`backlog_figures_verification`** — stratégie portant un **PASS**, sans `.npz`, donc **invis` | dérive |
| `+- **`battery_indet_hoist_declared`** — stratégie portant un **PASS**, sans `.npz`, donc **invis` | dérive |
| `+- **`battery_witness_hoist`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au` | dérive |
| `+- **`citer_451_definition`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au ` | dérive |
| `+- **`citer_451_resolution`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au ` | dérive |
| `+- **`class_a_witness_publication`** — stratégie portant un **PASS**, sans `.npz`, donc **invisi` | dérive |
| `+- **`conditional_sections_sweep`** — stratégie portant un **PASS**, sans `.npz`, donc **invisib` | dérive |
| `+- **`content_defined_magnitudes`** — stratégie portant un **PASS**, sans `.npz`, donc **invisib` | dérive |
| `+- **`declaration_convention_dating`** — stratégie portant un **PASS**, sans `.npz`, donc **invi` | dérive |
| `+- **`declaration_convention_decay`** — stratégie portant un **PASS**, sans `.npz`, donc **invis` | dérive |
| `+- **`duplicate_sweep_irreparability`** — stratégie portant un **PASS**, sans `.npz`, donc **inv` | dérive |
| `+- **`guards_without_witness`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible a` | dérive |
| `+- **`guards_witness_remainder`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible` | dérive |
| `+- **`hardcoded_figures_remainder`** — stratégie portant un **PASS**, sans `.npz`, donc **invisi` | dérive |
| `+- **`hardcoded_figures_sweep`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible ` | dérive |
| `+- **`idempotence_famille_capable`** — stratégie portant un **PASS**, sans `.npz`, donc **invisi` | dérive |
| `+- **`idempotence_lot2`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au bala` | dérive |
| `+- **`irreparability_justifications_audit`** — stratégie portant un **PASS**, sans `.npz`, donc ` | dérive |
| `+- **`irreparable_figures_census`** — stratégie portant un **PASS**, sans `.npz`, donc **invisib` | dérive |
| `+- **`marker_emitter_crossing`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible ` | dérive |
| `+- **`orphan_audits_declared_reading`** — stratégie portant un **PASS**, sans `.npz`, donc **inv` | dérive |
| `+- **`orphan_audits_fate`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au ba` | dérive |
| `+- **`orphan_cycles_entries`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au` | dérive |
| `+- **`orphans_interrupted_or_lost`** — stratégie portant un **PASS**, sans `.npz`, donc **invisi` | dérive |
| `+- **`prereg_convention_coverage`** — stratégie portant un **PASS**, sans `.npz`, donc **invisib` | dérive |
| `+- **`repo_magnitudes_recount`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible ` | dérive |
| `+- **`report_idempotence`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au ba` | dérive |
| `+- **`self_inclusion_detector`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible ` | dérive |
| `+- **`self_inclusion_detector_v2`** — stratégie portant un **PASS**, sans `.npz`, donc **invisib` | dérive |
| `+- **`self_inclusion_repair`** — stratégie portant un **PASS**, sans `.npz`, donc **invisible au` | dérive |
| `+- **`six_reports_emitter_inconsistency`** — stratégie portant un **PASS**, sans `.npz`, donc **` | dérive |
| `+- **`unpublished_witnesses_paths`** — stratégie portant un **PASS**, sans `.npz`, donc **invisi` | dérive |
| `-- insertions : **23** — suppressions : **2**` | dérive |
| `-- hunks du diff : **1**` | dérive |
| `-  - `-194,2 +194,23`` | dérive |
| *… et 116 autres* | dérive |

## Ce qui est committé

- `nonml_net_pnl_correction_result.md` : **committé** *(diff 84 lignes, idempotent, témoin présent)*
- `nonml_sweep_pass_prose_fix_result.md` : **committé** *(diff 175 lignes, idempotent, témoin présent)*


> **Un fichier hors cible a été modifié : `nonml_pnl_duplicate_sweep_result.md`.**

C'est l'**effet de bord** que la classe A excluait, et il vient de
l'appel `sw.main()`. **Le critère 5 échoue.**

**Conséquence tirée, et non inventée après coup** : le critère 5 est
pré-enregistré et décide du PASS. Committer des rapports tout en
échouant le critère qui les conditionne serait incohérent. **Rien
n'est committé, tout est restauré.**

> **Les témoins sont apparus — et je ne les publie pas.** Ils étaient
> là, corrects, dans deux rapports idempotents. **Le prix de la
> discipline est visible une deuxième fois**, après le #490.

## L'arbre, après

- fichiers modifiés sous `results/` : **0**
- **hors des rapports retenus** : **0**

**Aucun script de classe C n'a été exécuté** : la cascade reste
interdite.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| les 2 idempotents | 2 | 2 | **vérifiée** |
| témoin présent dans les 2 | 2 | 2 | **vérifiée** |
| le diff dépasse le témoin dans les 2 | 2 | 2 | **vérifiée** |

**Les témoins sont apparus dans les deux rapports régénérés** — et
**aucun n'est publié.** Ils étaient là, corrects, dans deux rapports
idempotents ; le critère 5 les retient.

> **La dette reste entière, et pour une meilleure raison qu'avant** :
> non plus « on n'a pas essayé », mais **« on a essayé, et l'essai a
> montré que ces scripts ne sont pas ce que le #494 croyait ».**

## Critères de succès

1. Les 2 exécutés deux fois, empreintes publiées — **OUI**.
2. Témoin vérifié présent — **OUI**.
3. Diff complet publié ou refus déclaré — **OUI**.
4. Chaque ligne attribuée — **OUI**.
5. Aucun autre fichier modifié **par l'exécution** — **NON** (`nonml_pnl_duplicate_sweep_result.md`).

*(Ce critère porte sur ce que l'exécution a modifié, **pas sur l'arbre
après restauration**. Le mesurer après coup l'aurait rendu toujours
vrai — un critère qui s'auto-absout ne contrôle rien.)*

**FAIL** — le critère porte
sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).
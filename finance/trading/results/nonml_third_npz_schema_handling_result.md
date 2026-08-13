# Le troisième schéma `.npz` et son traitement par les balayages (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.

## Verdict : **FAIL**

Le critère pré-enregistré était : **FAIL si au moins un consommateur applique une formule fausse** (catégorie D). Il y en a **2**.

## La concordance — et une correction du pré-enregistrement

Le pré-enregistrement déclarait la concordance **connue d'avance** et comptée
zéro. **C'était trop large** : le sondage post-hoc du #443 n'avait porté que sur
`dollar_neutral_composite_pit`. `dollar_neutral_composite_vol_targeted` n'avait
jamais été vérifié — il compte donc pour **1 vérification neuve**, et c'est lui
qui a livré le résultat intéressant.

| Fichier | Jambe | Sharpe (log) | Sharpe (simple) | Convention retenue |
|---|---|---|---|---|
| `dollar_neutral_composite_pit` | `pnl_candidate` | +0.18 | **+0.07** ✔ | simple |
| `dollar_neutral_composite_pit` | `pnl_ref` | +0.73 | **+0.62** ✔ | simple |
| `dollar_neutral_composite_vol_targeted` | `pnl_candidate` | **+0.36** ✔ | +0.28 | log |
| `dollar_neutral_composite_vol_targeted` | `pnl_ref` | **+0.74** ✔ | +0.64 | log |

**Les quatre jambes se retrouvent** dans leur rapport — mais pas sous la même
convention.

### Le schéma ne détermine pas la convention

C'est le résultat de fond de ce cycle :

- `dollar_neutral_composite_pit` stocke des rendements **simples** — son
  producteur calcule le Sharpe sur `log1p(pnl)` ;
- `dollar_neutral_composite_vol_targeted` stocke des rendements **log** — son
  producteur appelle `trading_metrics(r_vt)` **directement**, et le rendement
  total par `np.exp(sum)`.

**Deux fichiers, un seul schéma de clés, deux conventions opposées.** Les clés
`pnl_candidate` / `pnl_ref` ne suffisent donc **pas** à interpréter un fichier :
il faut lire le script producteur. Tout balayage qui déduirait la convention du
seul schéma se tromperait sur l'un des deux, quel que soit son choix.

C'est la **troisième** fois sur cet axe que ma propre reconstruction est en
cause avant le dépôt (#442 `r_alt` ignoré, #443 coûts comptés deux fois, ici
`log1p` appliqué aux deux) : mon premier passage appliquait `log1p` aux deux et
déclarait `vol_targeted` discordant. Le pré-enregistrement engageait à me
méfier d'abord de ma reconstruction ; appliqué, il a évité une fausse accusation.

## Le traitement par les 12 consommateurs

Classement par **lecture**, chacun justifié par la ligne qui décide du
traitement — pas par un balayage de garde-fous. Dans ce projet, aucun défaut
réel n'a jamais été trouvé par la mesure mécanique elle-même (#428, #436,
#442, #443).

| | Catégorie | Nombre |
|---|---|---|
| **A** | traité correctement | **5** |
| **B** | écarté explicitement (compté) | **2** |
| **C** | écarté **silencieusement** | **3** |
| **D** | **formule fausse appliquée** | **2** |

**12/12 classés.** Dont **2** connus
d'avance (les miens, #442 et #443) ⇒ **10 classements neufs**.

| Consommateur | Cat. | Ligne qui décide | Lecture |
|---|---|---|---|
| `nonml_duplicate_sweep_coverage_audit.py` | **A** | l.40 : `all_npz = sorted(RESULTS.glob("*_pnl.npz"))` -- aucun `np.load` dans le script | Ne compte que des fichiers, n'applique aucune formule : les inclure au compte est le traitement correct. |
| `nonml_npz_report_consistency_baskets_backtest.py` *(connu d'avance)* | **A** | l.55-58 : `if not BASKET_KEYS <= files: if not {"pos","r_asset"} <= files: third.append(...)` | **Connu d'avance** (le mien, #443) : isole le schema dans une categorie a part et le publie nommement. |
| `nonml_pnl_duplicate_sweep_audit.py` | **A** | l.93-94 : `key = "pos" if ... else ("pnl_gross_ov" if ... else "pnl_candidate")` | Le troisieme schema est **explicitement prevu** dans la cascade de cles. |
| `nonml_pnl_duplicate_sweep_v2_audit.py` | **A** | l.44 `sw.net_pnl(d)` importe la fonction defectueuse, mais l.111-112 et l.152 ne l'appellent que sur `A`, `B` et `PAIR_414` -- noms codes en dur, aucun de ce schema ; l.60 `glob` ne fait que compter | **Classement corrige en cours de cycle** : je l'avais d'abord ecrit D par « heritage », sans verifier qu'un fichier de ce schema atteigne la fonction. Il ne l'atteint jamais. |
| `nonml_reproducibility_campaign_v2_audit.py` | **A** | aucun `np.load` : le motif `*_pnl.npz` n'apparait que dans du texte cite (l.66, l.69) | Ne decode aucun fichier. |
| `nonml_empty_pass_basket_extension_backtest.py` | **B** | l.64 : `return "autre", sorted(f)` -> `other.append(name)` (l.96), compte publie l.126 | Compte publie, mais **fondu** avec les inexploitables : `autres / inexploitables : N`. Compte, donc B -- pas nomme, donc a signaler. |
| `nonml_log_return_compounding_audit.py` | **B** | l.121-122 : `if not REQUIRED <= set(npz.files): skipped.append((name, "schema non standard"))` | Ecarte avec une raison **nommee et publiee** dans la liste des ecartes. |
| `nonml_empty_pass_requalification_backtest.py` | **C** | l.52 : `if "pos" not in d.files or "r_asset" not in d.files:` -> `continue` | Ecarte **silencieusement** : ni compte ni signale. |
| `nonml_npz_report_consistency_backtest.py` *(connu d'avance)* | **C** | l.72-74 : `skipped.append((name, "schema panier (pas de position scalaire)"))` | **Connu d'avance** (le mien, #442). Compte, mais sous une etiquette **fausse** : ces 2 fichiers ne sont pas des paniers. C'est ce faux libelle qui a produit le « 23 paniers » corrige au #443. |
| `nonml_pnl_persistence_lot5_audit.py` | **C** | l.169-170 : `if "pos" not in p.files: continue` | Ecarte silencieusement. `n_sessions()` (l.52-54) planterait sur ce schema, mais n'est jamais atteint pour ces noms. |
| `nonml_leaders_trend_union_pnl_persistence_audit.py` | **D** | l.55 : `dup_groups, quasi, unknown = sw.main()` -- execute le balayage entier | Defaut **herite et reellement atteint** : `sw.main()` parcourt tous les `.npz`, donc la branche fausse est exercee. |
| `nonml_pnl_duplicate_sweep_backtest.py` | **D** | l.40-42 : `if {"pnl_candidate", "turn_candidate"} <= files:` -> `pnl_candidate - turn_candidate * c` | Soustrait les couts d'un P&L **deja net** : exactement l'erreur que j'ai commise moi-meme au #443. |

## Le défaut D, mesuré

`nonml_pnl_duplicate_sweep_backtest.py` fait prendre à
`dollar_neutral_composite_pit` la branche **« candidat+turnover »** et lui soustrait
des coûts qu'il porte déjà :

| | Valeur |
|---|---|
| P&L cumulé **selon le balayage** | **+0.1705** |
| P&L cumulé **réel** (`pnl_candidate` tel quel) | **+0.2028** |
| écart maximal séance par séance | 5.0e-04 |

Le second fichier, `dollar_neutral_composite_vol_targeted`, **échappe au
défaut** : dépourvu de `turn_candidate`, il tombe sur la branche « candidat
seul » (l.43-44) qui le lit correctement. Le défaut ne frappe donc que les
fichiers de ce schéma qui stockent leur turnover — **1 sur 2**.

### Conséquence, bornée et vérifiée

Ce chiffre faux **n'a été publié nulle part** : le fichier n'apparaît sous son
nom dans aucun rapport de balayage. Le seul effet possible était un **faux
négatif** — un doublon manqué parce que la série comparée était déformée.

Vérifié : **1** série(s) du dépôt seulement ont la même longueur
et sont donc comparables. La plus proche est `nonml_momentum_12_1_pit_universe_pnl.npz`, corrélation
**+0.0169**. **Aucun doublon n'a été manqué.**

Le défaut est donc **réel dans le code et sans conséquence publiée à ce jour**.
Les deux moitiés de cette phrase comptent : la seconde ne l'annule pas, car
tout futur `.npz` de ce schéma portant un turnover serait mal lu.

**Ce cycle ne corrige rien** — il ne fait que lire, comme annoncé. La
correction du balayage est une modification de code à déclarer, mesurer et
committer dans son propre cycle.

## Les écartés silencieux (C)

**3** consommateurs laissent leur lecteur mal informé sur ces
fichiers. Deux les écartent en silence — ni comptés ni signalés ; leur résultat
reste juste, mais leur rapport laisse croire à un balayage complet.

Le troisième, `nonml_npz_report_consistency_backtest.py` (#442), **ne rentre
proprement dans aucune des quatre catégories déclarées** : il les compte — donc
pas C au sens strict — mais sous une raison **fausse** — donc pas B non plus.
Je le classe C parce que l'effet sur le lecteur est celui d'un silence, et je
signale l'entorse plutôt que d'élargir une catégorie après coup.

- `nonml_empty_pass_requalification_backtest.py` — l.52 : `if "pos" not in d.files or "r_asset" not in d.files:` -> `continue`
- `nonml_npz_report_consistency_backtest.py` — l.72-74 : `skipped.append((name, "schema panier (pas de position scalaire)"))`
- `nonml_pnl_persistence_lot5_audit.py` — l.169-170 : `if "pos" not in p.files: continue`

Le cas de `nonml_npz_report_consistency_backtest.py` (#442) est le plus
instructif : il **comptait** ces fichiers, donc paraissait exemplaire, mais
sous l'étiquette **fausse** « schéma panier ». Un compte publié sous un mauvais
libellé est plus trompeur qu'un silence, parce qu'il a l'air d'une couverture.

## Ce que ce cycle ne permet pas de conclure

- **La prédiction du pré-enregistrement est vérifiée sur un point, réfutée sur
  aucun** : j'attendais « au moins un C », il y en a
  **3**. Je disais n'avoir aucune idée s'il existait un D : il y
  en a **2**, et l'un d'eux est un défaut que j'avais moi-même
  commis au #443 sans voir qu'il dormait déjà dans le dépôt.
- **Aucune stratégie n'est validée ni invalidée** par ce cycle.
- Le classement porte sur **ce schéma**. Rien n'est établi sur la façon dont
  ces 12 consommateurs traitent d'autres schémas non catalogués — s'il en
  existe encore, ce cycle ne les a pas cherchés.

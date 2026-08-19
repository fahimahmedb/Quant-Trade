# Les 11 justifications RÉPARABLE du #485 jamais relues (pré-enregistré)

Le **#517** a établi que le tableau des **5** justifications IRRÉPARABLE du #485 est entièrement couvert depuis le #493. Le #485 classait aussi **12** figures RÉPARABLE ; une seule (`battery_backfill_lot_audit`) a été relue depuis (#511, tombée). **Les 11 autres n'avaient jamais été relues.**

> `nonml_battery_backfill_lot_audit`, tranché au #511, est **exclu** de ce cycle : il n'est pas rejugé.

## Ce que chacun énumère — mécanique, avant toute lecture

| Script | Énumère | Constantes en dur | Interpolations | Fonctions |
|---|---|---|---|---|
| `nonml_duplicate_sweep_coverage_audit.py` | `glob`, `read_text` | — | **15** | 2 |
| `nonml_content_defined_magnitudes_audit.py` | `read_text`, import du dépôt, `git` (subprocess) | — | **18** | 4 |
| `nonml_content_defined_magnitudes_backtest.py` | import du dépôt, `git` (subprocess) | — | **16** | 5 |
| `nonml_coverage_wording_fix_audit.py` | `read_text` | `INSERTED_EXPECTED` | **10** | 2 |
| `nonml_dsr_corrected_trials_backtest.py` | `glob`, `read_text`, import du dépôt | — | **24** | 5 |
| `nonml_idempotence_famille_capable_backtest.py` | `glob`, `read_text`, import du dépôt, `git` (subprocess) | — | **18** | 5 |
| `nonml_idempotence_lot2_backtest.py` | `glob`, `read_text`, import du dépôt, `git` (subprocess) | — | **23** | 5 |
| `nonml_marker_emitter_crossing_backtest.py` | `glob`, `read_text` | `SUFFIXES` | **17** | 3 |
| `nonml_orphans_interrupted_or_lost_backtest.py` | `glob`, `read_text`, import du dépôt, `git` (subprocess) | — | **39** | 11 |
| `nonml_report_idempotence_backtest.py` | `read_text`, `git` (subprocess) | `NOMS` | **21** | 4 |
| `nonml_reproducibility_campaign_v2_audit.py` | `glob`, `read_text` | — | **7** | 2 |

## Les verdicts, un par un

**Écrits à la main après lecture, chacun adossé à une ligne de code.**

### `nonml_duplicate_sweep_coverage_audit.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « `n_missing` interpolé, la ventilation porte sur l'ensemble déjà construit »

`n_missing = len(names_scripts - names_npz)` (l.164) est une différence ensembliste calculée dans le script, puis interpolée trois fois (`f"...est **{n_missing}**"`, l.168 et l.176). **La justification tient à la lettre.**

### `nonml_content_defined_magnitudes_audit.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « l'audit énumère les importateurs pour les examiner »

`f449 = grep_l(...)`, `len(f449)`, `len(instrument)`, `len(autres)` sont tous calculés par `grep_l()` (grep sur objets git) puis interpolés dans le rapport (l.90-101). **Le script énumère bien les importateurs.**

### `nonml_content_defined_magnitudes_backtest.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « mesure sur objets git que le script lit déjà (+ 1 ligne signalée par le #485 lui-même comme une estimation en prose, non réparable) »

Le module définit `git()` (l.33-34) et lit les objets via `ls-tree`/`show` (l.39, 60, 67) ; `po`/`me` (porteurs/mentionneurs) en sont dérivés et interpolés à la ligne 135 (`**{v451}**`). **La mesure sur objets git existe bel et bien.** Réserve : le « 8 » de la ligne 154-155 est écrit en dur plutôt que réinterpolé depuis `po` — la même valeur apparaît donc à la fois interpolée (l.135) et littérale (l.154-155), défaut mineur de la même famille que le #499, mais qui ne change pas la dérivabilité : la ligne 154-155 duplique une valeur que le script calcule ailleurs, il ne l'invente pas. La ligne « 7 porteurs et 1 citeur » (l.165) reste, comme le #485 l'avait lui-même annoncé, une **estimation en prose non réparable — non rejugée ici**.

### `nonml_coverage_wording_fix_audit.py` — **JUSTIFICATION FAUSSE, VERDICT À REVOIR**

Justification du #485, **verbatim** : « un `glob` — le cas le plus trivialement réparable »

**Aucun appel `.glob(` nulle part dans le fichier.** Le script ne lit que `nonml_pnl_duplicate_sweep_result.md` (l.46) ; « 284 » (l.133) est un littéral brut dans une chaîne simple (pas de `f"..."`), absent aussi du fichier qu'il lit. **La justification du #485 — « un glob, le cas le plus trivialement réparable » — est fausse : ce script précis ne calcule ce chiffre par aucune voie.**

### `nonml_dsr_corrected_trials_backtest.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « le résultat de la fusion que le script opère »

`groupes = groupes_exacts(series)` (l.81), `gros = [g for g in groupes if len(g) > 1]` (l.128), et `L.append(f"**{len(gros)}** groupes de doublons exacts fusionnés")` (l.129). **« fusionne 2 » est le résultat de `len(gros)`, calculé, pas tapé.**

### `nonml_idempotence_famille_capable_backtest.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « se dérive de `v1.FAUTIFS_463`/`v1.SAINS_463`, importés »

`import nonml_self_inclusion_detector_backtest as v1` (l.23) et `DEJA = v1.FAUTIFS_463 | v1.SAINS_463 | ...` (l.48). **Correspond littéralement à la justification.**

### `nonml_idempotence_lot2_backtest.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « le script construit `tous` et `DEJA` »

`tous = sorted(p.name for p in SCRIPTS.glob("nonml_*_backtest.py"))` (l.72) et `DEJA = DEJA_463 | DEJA_467` (l.36). **Les deux variables citées existent et sont construites comme décrit.**

### `nonml_marker_emitter_crossing_backtest.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « le compte que ce script calcule (`douteux`) »

`douteux = [e for e in examen if e[2]]` (l.169), suivi de `len(douteux)` interpolé (l.171). **Le compte cité est bien calculé par le script.**

### `nonml_orphans_interrupted_or_lost_backtest.py` — **JUSTIFICATION EXACTE**

Justification du #485, **verbatim** : « le script calcule `len(ent) + len(orp)` »

`ent = examiner(aucun_fichier)` (l.160), `orp = examiner(orphelins)` (l.161), `total = len(ent) + len(orp)` (l.433). **La somme citée par la justification est exactement celle du code.**

### `nonml_report_idempotence_backtest.py` — **JUSTIFICATION FAUSSE, VERDICT À REVOIR**

Justification du #485, **verbatim** : « rapport de l'univers figé #443-#460 au total, lu par `glob` »

**Aucun appel `.glob(` nulle part dans le fichier.** « Le dépôt compte **314** `nonml_*_backtest.py` » (l.123) est un littéral brut à l'intérieur d'une f-string qui n'interpole que `len(NOMS)`, pas 314 ; « soit **5,7 %** » (l.124) est une chaîne simple, non calculée. **Contrairement à `idempotence_lot2_backtest.py` (même famille de constat, ci-dessus), ce script ne lit jamais le dépôt pour obtenir son dénominateur — la justification du #485 est fausse, et par le même critère que le #511 a appliqué à `battery_backfill_lot_audit`** (ouvrir une source que le script n'ouvre pas n'est pas une interpolation), **le verdict ne tient pas.**

### `nonml_reproducibility_campaign_v2_audit.py` — **JUSTIFICATION FAUSSE, VERDICT À REVOIR**

Justification du #485, **verbatim** : « un `glob` sur `results/*.npz` »

Le seul `.glob(` du fichier porte sur `SCRIPTS.glob("nonml_*_backtest.py")` (l.28), pour une fonction `eligible()` sans rapport avec le compte cité. « 208 » (l.53 et l.56) est un littéral brut, jamais issu d'un `RESULTS.glob("nonml_*_pnl.npz")` que **ce script** n'exécute nulle part — seul le rapport qu'il *audite* est censé le faire. **La justification du #485 attribuait à cet audit un calcul qu'il ne fait pas ; verdict à revoir, même critère qu'au-dessus.**

## Le compte

- justifications **exactes** : **8 / 11**
- justifications **fausses** : **3**
- **verdicts réparables qui tombent** (reclassés IRRÉPARABLE) : **3**
  - `nonml_coverage_wording_fix_audit.py`
  - `nonml_report_idempotence_backtest.py`
  - `nonml_reproducibility_campaign_v2_audit.py`

### Le compte courant du #485 est corrigé une troisième fois

| | #485 | #493 | #511 | Ici |
|---|---|---|---|---|
| irréparables | 5 | 4 | 5 | **8**|
| réparables | 12 | 13 | 12 | **9** |

> **Ma prédiction 2 annonçait qu'au plus 2 tomberaient. Elle est réfutée : 3 tombent.** Les trois partagent le même défaut — un chiffre publié en prose, sans aucun `.glob(` ni lecture de dépôt dans le fichier qui le publie — exactement le critère que le **#511** avait déjà appliqué à `battery_backfill_lot_audit`, appliqué ici de façon identique, pas assoupli ni durci après avoir vu le résultat.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 1 justification fausse | ≥ 1 | 3 | **vérifiée** |
| au plus 2 verdicts tombent | ≤ 2 | 3 | **réfutée** |
| `coverage_wording_fix_audit` exacte | exacte | FAUSSE | **réfutée** |

**La prédiction 3 est la plus instructive : réfutée.** Le #485 désignait ce cas comme *« le plus trivialement réparable de la liste »*, précisément parce qu'il semblait le plus évident à l'œil. **C'est celui-là qui ne contient aucun calcul du tout** — le chiffre le plus "évidemment un glob" est un pur littéral.

**La prédiction 2 est réfutée** — 3 tombent, pas au plus 2. Publié tel quel, sans ajuster le seuil après mesure.

## Critères de succès

1. Les **11** nommés, justification citée verbatim — **OUI**.
2. **11/11** examinés, chacun adossé à une ligne de code — **OUI**.
3. Tout verdict renversé publié, compte du #485 corrigé — **OUI**.
4. `content_defined_magnitudes_backtest.py` traité en deux parties, sans rejuger la partie déjà tranchée — **OUI**.
5. `nonml_battery_backfill_lot_audit` exclu explicitement — **OUI**.

**PASS** — le critère porte sur le **procédé** : un cycle qui relit ses propres verdicts et publie les chutes, y compris quand elles sont plus nombreuses qu'annoncé.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun paramètre de stratégie. **Aucun script du dépôt n'a été exécuté.**

> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date de son exécution.
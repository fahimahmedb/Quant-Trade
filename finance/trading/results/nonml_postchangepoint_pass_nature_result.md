# Le régime post-basculement : **PASS procédural** ou **substantiel** ? (pré-enregistré)

Le **#510** a daté un basculement — **13/08/2026 21:51** — après
lequel les scripts cessent d'ouvrir des données de marché. Le **#512**
a montré qu'un cycle peut satisfaire tous ses critères tout en
produisant une mesure **sans valeur** — un PASS purement procédural.

## La règle, citée verbatim

> Date pivot **reprise du #510, non recalculée** : **13/08/2026 21:51 UTC**. Population : scripts `nonml_*_backtest.py`
> à verdict, introduits à cette date ou après. **PROCÉDURAL** si le
> rapport contient « porte sur le procédé » ; **SUBSTANTIEL** sinon.

## Le recensement

- scripts du régime postérieur : **68**
- dont **PASS** : **61** ; dont **FAIL** : **7**

| Classe | Nombre | Part des PASS |
|---|---|---|
| **PROCÉDURAL** | **50** | **82,0 %** |
| **SUBSTANTIEL** | **11** | **18,0 %** |

> **11** exception(s) — les seuls PASS du régime qui ne
> se déclarent pas procéduraux, nommés ci-dessous.

## Les substantiels, nommés

- `nonml_verdict_detector_complete_backtest.py` — introduit le 13/08/2026 22:31 : « # La règle complète du détecteur de verdict (pré-enregistré) **Cycle de MODIFICATION**, quatrième après les #445, #446 et #447. ## Ce qui change Deux changements, tous deux déclarés **avant** d'écr… »
- `nonml_six_reports_regeneration_backtest.py` — introduit le 14/08/2026 01:01 : « # Régénération des six rapports laissés en écart au #449 (pré-enregistré) **Cycle de MODIFICATION**, sixième après les #445 → #449. Il **exécute et compare** ; il ne corrige rien. ## La dette résorb… »
- `nonml_marker_emitted_by_scripts_backtest.py` — introduit le 14/08/2026 01:17 : « # L'encart « dépendant du dépôt », émis par les scripts (pré-enregistré) **Cycle de MODIFICATION**, septième après les #445 → #450. ## Critère 4 — le périmètre réel, et l'écart au backlog Le backlo… »
- `nonml_tom_decomposition_npz_backtest.py` — introduit le 14/08/2026 01:25 : « # Un `.npz` pour `tom_decomposition_overlay`, et le balayage enfin possible (pré-enregistré) **Cycle de MODIFICATION**, huitième après les #445 → #451, et le premier depuis longtemps à toucher une **… »
- `nonml_verdict_variant_decision_backtest.py` — introduit le 14/08/2026 02:09 : « # Faut-il convertir la dernière variante du détecteur ? (pré-enregistré) **Cycle de décision.** Il pouvait se conclure par « on ne touche à rien » ; la règle de décision était fixée **avant** toute m… »
- `nonml_dsr_corrected_trials_backtest.py` — introduit le 14/08/2026 02:38 : « # Le DSR avec un décompte d'essais corrigé des doublons (pré-enregistré) **Piste A.** La question vers laquelle toute la discipline anti-snooping du dépôt pointe depuis le début, et que 450 cycles n'… »
- `nonml_battery_coverage_backtest.py` — introduit le 14/08/2026 02:56 : « # Les PASS jamais passés par la batterie Règle 9 (pré-enregistré) **Piste B.** Ce cycle ne se contente pas de mesurer une lacune : il la **comble**. ## Le recompte, et l'écart au #431 | | Nombre | … »
- `nonml_temporal_holdout_backtest.py` — introduit le 14/08/2026 03:22 : « # Hors-échantillon temporel sur les PASS (pré-enregistré) **Piste C**, la dernière des trois du #455. ## Ce que ce test est — et ce qu'il n'est pas **Ce n'est pas un vrai hors-échantillon.** Les rè… »
- `nonml_relative_holdout_backtest.py` — introduit le 14/08/2026 03:37 : « # Hors-échantillon **relatif au benchmark** — la piste C refaite (pré-enregistré) Le #458 mesurait le Sharpe **absolu** et concluait à tort à une persistance : Buy & Hold faisait **mieux** sur la mêm… »
- `nonml_verdict_rule_battery_backtest.py` — introduit le 14/08/2026 03:56 : « # Étendre la règle de verdict aux rapports de batterie (pré-enregistré) Défaut trouvé au #457 **en cherchant autre chose**. La règle unifiée, taillée sur les rapports de **stratégie**, répondait « in… »
- `nonml_self_inclusion_repair_backtest.py` — introduit le 14/08/2026 10:37 : « # Réparer les deux scripts auto-inclusifs (pré-enregistré) **Premier cycle de RÉPARATION de la série.** Le #463 avait trouvé les défauts sans les corriger et le #466 avait refusé de le faire : l'enga… »

### Ce que ces 11 exceptions sont réellement — mesuré après coup

La phrase « porte sur le procédé » est elle-même une **convention
adoptée en cours de série**, pas une règle depuis l'origine.
- première occurrence du régime avec cette phrase : **14/08/2026 05:38**
- substantiels **antérieurs** à cette adoption (artefact de
  calendrier, pas une vraie exception) : **10**
- substantiels **postérieurs** — vraies exceptions, la convention
  existait déjà et n'a pas été appliquée : **1**

| Script | Introduit le |
|---|---|
| `nonml_self_inclusion_repair_backtest.py` | 14/08/2026 10:37 |

> **Sur 68 scripts du régime, une seule vraie exception** —
> `nonml_self_inclusion_repair_backtest.py`, le premier cycle de
> **réparation** de toute la série (le #463 avait trouvé les
> défauts, le #466 avait refusé de les corriger). Son PASS porte
> sur une action réelle sur le dépôt, pas sur la publication d'un
> procédé — et c'est la **seule** fois où c'est arrivé depuis
> l'adoption de la convention.

## Le compte des FAIL, pour situer le total

- FAIL du régime : **7**

## Ce que ce cycle ne juge pas

Un PASS procédural n'est pas un défaut en soi — c'est le mode de
fonctionnement **déclaré** de cette série depuis le #513 : le critère
porte sur la publication honnête d'un verdict, pas sur la découverte
d'un fait nouveau à chaque cycle. Ce recensement mesure une
**proportion**, pas une faute.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 90 % des PASS procéduraux | ≥ 90 % | 82,0 % | **réfutée** |
| SUBSTANTIEL = 0 | 0 | 11 | **réfutée** |
| régime ≥ 62 scripts | ≥ 62 | 68 | **vérifiée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Les seuls appels externes visent `git log` et `git status`, **en
lecture**.

## Critères de succès

1. Règle citée verbatim, date pivot rappelée — **OUI**.
2. Population (**68**) et PASS/FAIL publiés (**61**/**7**) — **OUI**.
3. Compte PROCÉDURAL/SUBSTANTIEL publié (**50**/**11**) — **OUI**.
4. Substantiels nommés ou absence explicite — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts et de
> l'historique à la date de son exécution.

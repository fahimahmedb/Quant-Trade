# Audit adversarial — le sort des 3 audits orphelins (#480)

**Recalcul par une route différente** : l'existence historique est
établie par `git rev-list --all --objects` (énumération des **blobs**)
au lieu de `git log --diff-filter=A`, et la déclaration du
pré-enregistrement est relue sur ses **dix premières lignes**.

| Grandeur | Audit | Rapport | Verdict |
|---|---|---|---|
| `_result.md` jamais existants (blobs) | **0** | 0 | **concordant** |
| scripts `_backtest.py` présents | **0** | 0 | **concordant** |
| audits présents | **3** | 3 | **concordant** |

## Ce que les pré-enregistrements disent d'eux-mêmes

Relu **hors du backtest**, sur les dix premières lignes de chacun :

- `n_trials_dependence_correction` → « Cycle de **correction statistique** »
- `pnl_duplicate_sweep_v2` → « Cycle de **diagnostic** »
- `pnl_persistence_exposed_pass` → « Cycle de **infrastructure et de mesure** »

- pré-enregistrements se déclarant explicitement : **3 / 3**

> **Les trois se déclarent, dès leur en-tête, comme des cycles qui
> n'évaluent aucune stratégie.** Aucun ne promet de `_result.md`. La
> route indépendante aboutit donc à la **lecture C pour les trois**.

## Le contrôle central — le rapport publie-t-il ce qui le contredit ?

Un cycle dont la règle mécanique et la lecture à la main divergent peut
cacher la seconde. **Vérifié dans le rapport publié :**

| Contrôle | Résultat |
|---|---|
| le rapport signale que sa règle a mal lu | **OUI** |
| il nomme le mot manqué (« diagnostic ») | **OUI** |
| il nomme son faux positif | **OUI** |
| il énonce la lecture à la main (les trois en C) | **OUI** |
| il **refuse** de reclasser à son avantage | **OUI** |
| la prédiction 1 reste marquée réfutée | **OUI** |

> **Le rapport publie intégralement ce qui contredit son propre
> classement, et refuse d'en tirer parti.** C'est la condition pour
> qu'un lecteur puisse reclasser sans croire l'auteur — et elle est
> tenue.

**L'audit ne conclut pas que le classement mécanique est bon** : il
conclut que **le désaccord est visible**. Sur le fond, la route
indépendante donne **C pour les trois**, et le rapport le dit
lui-même sans se l'attribuer.

## Effets de bord du backtest

- écritures : **1** (`OUT` seul)
- exécution d'un script du dépôt / `checkout` / suppression : **0**

**Aucun effet de bord — lecture de `git` et du disque.**

## Verdict

**CONCORDANT** — **3/3** grandeurs se retrouvent, et
**6/6** contrôles de
transparence sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution (cycles #436-#438).
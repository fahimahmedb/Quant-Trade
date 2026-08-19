# Vérification des 3 candidats du #484 (pré-enregistré)

Le #522 a signalé 3 candidats dans `nonml_guards_witness_
remainder_backtest.py` (#484). Ce cycle vérifie mécaniquement
chacun, par AST pour les 2 MASQUANT et par comparaison
d'axe pour l'ANODIN, avant tout verdict.

## Les 2 candidats MASQUANT — présence d'une référence inconditionnelle

### `nonml_six_reports_regeneration_backtest.py` — variable `perdus`, garde citée l.232

- **la garde a dérivé** : citée l.232 par le #484, retrouvée l.233 aujourd'hui
- plage de la garde (AST, noeud `If` réel) : **[233, 259]**
- toutes les références à `perdus` dans un `L.append(` : [231, 236]
- références **hors** de la garde (inconditionnelles) : **1**
  - l.231 : `L.append(f"- rapports ayant **perdu** l'encart du #439 en étant régénérés : **{len(perdus)}**")`

> **Le MASQUANT ne tient plus.** La justification du #484 affirmait qu'aucune référence n'existait hors de la garde ; il en existe **1** aujourd'hui. **Reclassé ANODIN.**

### `nonml_sweep_pass_prose_fix_backtest.py` — variable `strategies`, garde citée l.134

- **la garde a dérivé** : citée l.134 par le #484, retrouvée l.135 aujourd'hui
- plage de la garde (AST, noeud `If` réel) : **[135, 160]**
- toutes les références à `strategies` dans un `L.append(` : [133, 142]
- références **hors** de la garde (inconditionnelles) : **1**
  - l.133 : `L.append(f"- PASS qui sont des **stratégies** et non des scripts d'inventaire : **{len(strategies)}*`

> **Le MASQUANT ne tient plus.** La justification du #484 affirmait qu'aucune référence n'existait hors de la garde ; il en existe **1** aujourd'hui. **Reclassé ANODIN.**

> **Le « contrôle positif » du #475/#484 tombe.** `six_reports_regeneration` / `perdus` était cité comme *« le cas exact du #475... une règle qui ne le classerait pas masquant serait à jeter »*. Ce n'est pas la règle qui a changé — **c'est l'état du script**, qui a depuis reçu un témoin en l.231. **Le cas reste valide historiquement (au #475/#484) ; il ne l'est plus aujourd'hui.**

## Le candidat ANODIN — même protocole d'axe qu'aux #523/#524

- `nonml_self_inclusion_detector_backtest.py` (l.106) est mentionné au #504 pour l'axe « emprunts non rattachés à une source publiée » (16 et 2, résidus) : **OUI**
- cet axe est-il celui du #484 (MASQUANT/ANODIN d'une section) : **NON, axe distinct**

> **Faux positif confirmé, même mécanisme qu'aux #523/#524** : le #504 juge la traçabilité d'un chiffre emprunté, sans rapport avec la classification MASQUANT/ANODIN du #484. **Le verdict ANODIN n'est pas contredit.**

## Le compte

- candidats vérifiés : **3**
- verdicts qui tombent (MASQUANT → ANODIN) : **2**
- faux positifs confirmés : **1**

## Le geste appliqué, et une régénération refusée par précaution

Les **2** verdict(s) `V` du #484 corrigés (`MASQUANT` → `ANODIN`), diff vérifié borné aux entrées déclarées.

**Le rapport du #484 n'a délibérément PAS été régénéré ni committé**, même garde-fou qu'au #524 : régénérer capture aussi toute dérive de la population que le script recalcule à l'exécution, non vérifiée comme bornée aux verdicts corrigés dans ce cycle. Restauré à l'identique si l'exécution a eu lieu pour vérification.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| Les 2 MASQUANT tombent (reclassés ANODIN) | 2 | 2 | **vérifiée** |
| `self_inclusion_detector` est un faux positif | oui | oui | **vérifiée** |
| Régénération du rapport refusée | oui | oui | **vérifiée** |

## Critères de succès

1. Les 3 candidats vérifiés, verdict et ligne de code à l'appui — **OUI**.
2. Présence/absence de référence inconditionnelle établie par AST pour les 2 MASQUANT — **OUI**.
3. Axe du #504 comparé à celui du #484 pour self_inclusion_detector — **OUI**.
4. Tout verdict renversé publié avec diff borné à cette seule entrée (par cible) — **OUI**.
5. Régénération refusée et documentée si elle déborderait du périmètre — **OUI**.

**PASS** — le critère porte sur le **procédé** : vérifier des candidats de staleness, réparer ceux confirmés avec un diff borné, y compris quand le cas tombé est le contrôle positif de référence de toute la série.

Simulation 300 € et robustesse **sans objet** : cycle de vérification/réparation de dépôt, aucune position.

# Vérification des 3 candidats du #481 (pré-enregistré)

Le #522 a signalé 3 candidats dans `nonml_guards_without_
witness_backtest.py` (#481). Ce cycle vérifie mécaniquement
chacun, par AST pour les 2 MASQUANT et par comparaison
d'axe pour l'ANODIN, avant tout verdict.

## Les 2 candidats MASQUANT — présence d'une référence inconditionnelle

### `nonml_battery_coverage_backtest.py` — variable `indet`, garde citée l.159

- plage de la garde (AST, noeud `If` réel) : **[159, 177]**
- toutes les références à `indet` dans un `L.append(` : [147, 162]
- références **hors** de la garde (inconditionnelles) : **1**
  - l.147 : `L.append(f"- rapports classés « indéterminé » par la règle unifiée : **{indet}**")`

> **Le MASQUANT ne tient plus.** La définition du #481 exigeait qu'aucune référence n'existe hors de la garde ; le témoin ajouté au #489 en introduit **1**. **Reclassé ANODIN.**

### `nonml_net_pnl_correction_backtest.py` — variable `incoh`, garde citée l.279

- **la garde a dérivé** : citée l.279 par le #481, retrouvée l.281 aujourd'hui (trouvée par nom de variable, pas par numéro de ligne — le fichier a changé depuis)
- plage de la garde (AST, noeud `If` réel) : **[281, 297]**
- toutes les références à `incoh` dans un `L.append(` : [278]
- références **hors** de la garde (inconditionnelles) : **1**
  - l.278 : `L.append(f"- incohérences prose/compte exposées par le rafraîchissement : **{len(incoh)}**")`

> **Le MASQUANT ne tient plus.** La définition du #481 exigeait qu'aucune référence n'existe hors de la garde ; le témoin ajouté au #489 en introduit **1**. **Reclassé ANODIN.**

## Le candidat ANODIN — même protocole d'axe qu'au #523

- `nonml_marker_emitter_crossing_backtest.py` (l.175) est mentionné au #518 pour l'axe « le chiffre cité par le #485 » (réparabilité d'un littéral) : **OUI**
- cet axe est-il celui du #481 (MASQUANT/ANODIN d'une section) : **NON, axe distinct**

> **Faux positif confirmé, même mécanisme qu'au #523** : le #518 juge la réparabilité d'un chiffre du #485, sans rapport avec la classification MASQUANT/ANODIN du #481. **Le verdict ANODIN n'est pas contredit.**

## Le compte

- candidats vérifiés : **3**
- verdicts qui tombent (MASQUANT → ANODIN) : **2**
- faux positifs confirmés : **1**

## Le geste appliqué — et une limite découverte en l'appliquant

Les 2 verdicts `V` du #481 corrigés (`MASQUANT` → `ANODIN`), diff vérifié borné aux 2 entrées déclarées.

**Le rapport du #481 n'a délibérément PAS été régénéré ni committé.** Régénérer `nonml_guards_without_witness_result.md` recalcule aussi la population entière des sections conditionnelles du dépôt — passée de **58** (au #481) à **67** aujourd'hui (le dépôt a grandi de 9 sections conditionnelles depuis). Cette dérive **change l'échantillon des 5 examinés à la main**, remplaçant les deux cibles corrigées par deux scripts jamais vus (`class_a_witness_publication_backtest.py`, `hardcoded_tables_repair_backtest.py`, classés « NON EXAMINÉ »), ce qui ferait **échouer le critère du #481 lui-même** (5/5 examinés devient faux). **Même situation que le #489** (« le rapport régénéré n'est pas committé, et l'arbre est restauré ») : le diff déborderait de ce qui est déclaré ici — un repérage de population, pas une correction des 2 verdicts. **Restauré à l'identique.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| Les 2 MASQUANT tombent (reclassés ANODIN) | 2 | 2 | **vérifiée** |
| `marker_emitter_crossing` est un faux positif | oui | oui | **vérifiée** |
| Compte final `V` du #481 : 0 MASQUANT / 5 ANODIN | 0/5 | 0/5 MASQUANT | **vérifiée** |

## Critères de succès

1. Les 3 candidats vérifiés, verdict et ligne de code à l'appui — **OUI**.
2. Présence/absence de référence inconditionnelle établie par AST pour les 2 MASQUANT — **OUI**.
3. Axe du #518 comparé à celui du #481 pour marker_emitter_crossing — **OUI**.
4. Tout verdict renversé publié avec diff borné à cette seule entrée (par cible) — **OUI**.
5. Aucun script de marché exécuté — **OUI**.

**PASS** — le critère porte sur le **procédé** : vérifier des candidats de staleness, réparer ceux confirmés avec un diff borné, et refuser de committer un effet de bord plus large découvert en tentant de le faire.

Simulation 300 € et robustesse **sans objet** : cycle de vérification/réparation de dépôt, aucune position.

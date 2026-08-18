# Audit adversarial — les justifications d'irréparabilité (#493)

**Faire tomber un verdict qu'on a signé est peu suspect de
complaisance.** L'audit vérifie donc l'inverse : la chute est-elle
**réelle**, et surtout — **les 3 verdicts maintenus le sont-ils à bon
droit** ?

## 1. Le cas qui tombe — vérifié en exécutant `bound` **isolément**

Le rapport affirme que `100*bound(cum)` vaut le **6,2 %** écrit en dur.
**Contrôle : extraire `bound` du script et l'évaluer**, sans exécuter le
script lui-même.

- `bound` extraite et évaluée : **OUI**
- corps de `bound`, verbatim : `return 1.0 - 0.05 ** (1.0 / n)`
- constantes de module lues : **SEED_LOT1=20260817, SIZE_LOT1=24, DENOM_LOT1=23, SEED_LOT2=20260818, SIZE_LOT2=24**
- il existe `cum = 47` tel que `100*bound(cum)` = **6.2 %**

> **La chute est réelle et vérifiée par calcul.** Le `6,2 %` écrit en
> dur **est** une valeur que la fonction du script produit. Le #485
> avait tort de le dire irréparable, et le #493 a raison de le dire.

**Et la projection aussi** : `100*bound(47 + 24)` = **4.1 %**, soit le « ~4,1 % » de la ligne incriminée.

## 2. Les **3 maintenus** — le sont-ils à bon droit ?

C'est ici que la complaisance serait payante : maintenir trois verdicts
en n'en lâchant qu'un donne l'air rigoureux à peu de frais. **Contrôle
AST : chacun définit-il une fonction, ou énumère-t-il un corpus, qui
permettrait de recalculer la grandeur ?**

| Script | Fonctions définies | Énumère un corpus | Interpolations |
|---|---|---|---|
| `nonml_protocol_inventory_audit.py` | 1 | **non** | 4 |
| `nonml_marker_emitted_by_scripts_backtest.py` | 3 | **non** | 9 |
| `nonml_pnl_persistence_exposed_pass_audit.py` | 2 | **non** | 13 |

- maintenus **suspects** *(énumèrent **et** définissent des fonctions)* : **0**

> **Aucun des trois n'a la double capacité** qui a fait tomber le
> quatrième. **Les maintiens ne sont pas de complaisance** : ces
> scripts n'ont ni le corpus ni la fonction pour recalculer.

## 3. Le cycle publie-t-il ce qui l'accuse ?

| Contrôle | Résultat |
|---|---|
| il marque sa prédiction 2 réfutée | **OUI** |
| il corrige le compte du #485 (5 → 4) | **OUI** |
| il dit que c'est un verdict qu'il a signé | **OUI** |
| il qualifie le cas d'aggravant | **OUI** |
| il refuse de généraliser le taux 2/5 | **OUI** |

> **Le cycle corrige un compte qu'il avait lui-même publié**, marque
> sa prédiction réfutée, et refuse de tirer un taux de deux cas.

## Verdict

**CONCORDANT** — la chute est **vérifiée par
calcul**, les 3 maintiens **n'ont pas la capacité** qui a fait tomber le
quatrième, et **5/5**
contrôles de transparence sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).
# Audit adversarial — le patch des sections masquantes (#487)

**Un cycle de modification qui se vérifie lui-même statiquement** est le
cas où la complaisance est la plus facile. L'audit contrôle donc par des
routes propres, et **il ne se fie à aucune annonce**.

## 1. La réparation est-elle réelle ?

Route : l'**AST** cherche une écriture mentionnant la variable de garde
**à profondeur zéro** — hors de tout `if`/`for`/`while`/`try`.

| Script | Variable | Témoin hors garde | Mentions sous garde |
|---|---|---|---|
| `nonml_six_reports_regeneration_backtest.py` | `perdus` | **OUI** | 2 |
| `nonml_sweep_pass_prose_fix_backtest.py` | `strategies` | **OUI** | 2 |

> **Les deux témoins existent bien hors garde.** La réparation n'est
> pas seulement annoncée : elle est **structurellement présente**, et
> une route qui ignore entièrement la règle du #481 la retrouve.

## 2. Le dépôt est-il resté intact ailleurs ?

| Fichier | Ajouts | Suppressions |
|---|---|---|
| `finance/trading/scripts/nonml_six_reports_regeneration_backtest.py` | 2 | 0 |
| `finance/trading/scripts/nonml_sweep_pass_prose_fix_backtest.py` | 2 | 0 |

- fichiers touchés hors des deux cibles : **0**
- **suppressions totales** : **0**

> **Deux fichiers touchés, zéro ligne supprimée.** Le patch est
> **purement additif** — il ne peut pas avoir altéré un comportement
> existant.

## 3. Les rapports publiés ont-ils été touchés ? — ils ne doivent pas

Le cycle annonce n'avoir **exécuté aucun** des deux scripts. Si c'était
faux, leurs rapports porteraient une modification.

| Rapport | État git |
|---|---|
| `nonml_six_reports_regeneration_result.md` | **inchangé** |
| `nonml_sweep_pass_prose_fix_result.md` | **inchangé** |

> **Les deux rapports sont inchangés.** L'annonce « aucune exécution »
> est **vérifiée par ses conséquences**, pas crue sur parole.

**Et c'est bien la situation que le rapport décrit** : la réparation
est **dans le code, pas encore dans les rapports**. Un lecteur qui les
ouvrirait aujourd'hui ne verrait aucun témoin.

## 4. Le cycle a-t-il dit ce qui l'affaiblit ?

| Contrôle | Résultat |
|---|---|
| il publie les deux comptes de lignes (4 insertions / 2 instructions) | **OUI** |
| il écrit que les rapports ne portent pas encore le témoin | **OUI** |
| il nomme les 2 masquants qu'il ne répare pas | **OUI** |
| il justifie la non-exécution par un effet de bord constaté | **OUI** |
| il ne corrige pas la règle du #481 | **OUI** |

*(Le quatrième contrôle a d'abord échoué sur un motif de recherche mal
écrit de ma part : la phrase du rapport court sur **deux lignes**, si
bien qu'aucune sous-chaîne contiguë ne la portait. **C'est mon matcher
qui était fautif, pas le rapport** — même nature d'erreur qu'aux #478,
#482 et #484, et je la publie plutôt que de la corriger en silence.)*

> **Le cycle publie ce qui l'affaiblit** : que son diff compte 4
> insertions et non 2, que la réparation n'est pas encore visible, et
> que la moitié des masquants reste non traitée.

## Verdict

**CONCORDANT** — réparation **structurellement
confirmée** par une route indépendante, patch **purement additif**,
rapports **inchangés** *(donc aucune exécution)*, et
**5/5** contrôles de
transparence tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).
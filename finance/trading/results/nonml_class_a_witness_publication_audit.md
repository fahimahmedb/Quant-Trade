# Audit adversarial — l'exécution puis le renoncement (#495)

Le cycle a **exécuté** deux scripts, **obtenu ce qu'il voulait** — témoins
présents, rapports idempotents — puis **tout restauré**. C'est le
renoncement le plus coûteux de la série. **L'audit vérifie qu'il est
fondé, et non théâtral.**

## 1. L'appel en process existe-t-il vraiment ?

Route : **AST** — résoudre l'alias d'import vers le module du dépôt, et
ne retenir que les `.main()` appelés **sur cet alias**.

| Script | Module importé | Lignes d'appel `.main()` |
|---|---|---|
| `nonml_net_pnl_correction_backtest.py` | `nonml_pnl_duplicate_sweep_backtest` | **[222]** |
| `nonml_sweep_pass_prose_fix_backtest.py` | `nonml_pnl_duplicate_sweep_backtest` | **[72, 76, 251]** |

> **Confirmé par résolution d'alias.** Les deux appellent le `main()`
> d'un module du dépôt. **Le classement A du #494 était faux**, et sa
> règle — qui cherchait `subprocess.run([sys.executable, …])` — ne
> pouvait pas le voir.

## 2. L'effet collatéral est-il attribuable à cet appel ?

Le cycle impute la modification de `nonml_pnl_duplicate_sweep_result.md` à `sw.main()`.
**Contrôle : le module appelé écrit-il bien ce fichier ?**

- module appelé : **`nonml_pnl_duplicate_sweep_backtest`**
- son `OUT` : **`nonml_pnl_duplicate_sweep_result.md`**
- correspond au fichier collatéral : **OUI**

> **L'attribution est exacte.** Le fichier modifié est le rapport
> propre du module appelé. **L'effet de bord n'est pas une
> supposition** : il se lit dans le code du module.

## 3. L'arbre est-il réellement propre ?

- fichiers modifiés hors ceux du cycle : **0**

> **Rien n'a été laissé.** Le renoncement va jusqu'au bout : les
> rapports régénérés **et** le fichier collatéral sont restaurés.

## 4. Le critère 5 mesure-t-il l'exécution, ou l'arbre après coup ?

**C'est le point où un cycle pourrait se blanchir sans mentir** :
restaurer, puis constater que l'arbre est propre, et cocher le critère.

| Contrôle | Résultat |
|---|---|
| le critère 5 est marqué NON | **OUI** |
| le fichier collatéral est nommé dans le critère | **OUI** |
| le rapport dit que mesurer après coup l'auto-absoudrait | **OUI** |
| le verdict est FAIL | **OUI** |
| rien n'est committé alors que les témoins étaient présents | **OUI** |
| la chaîne #487 → #494 → #495 est publiée | **OUI** |

> **Le critère mesure l'exécution, pas l'arbre restauré**, et le
> rapport écrit pourquoi. **Le FAIL est réel** : un cycle qui aurait
> mesuré après restauration aurait pu cocher le critère et publier.

## Verdict

**CONCORDANT** — l'appel en process est
**confirmé par résolution d'alias**, l'effet collatéral est **attribué
sur pièce**, l'arbre est **réellement propre**, et le critère 5
**ne s'auto-absout pas**. **6/6** contrôles de transparence tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).
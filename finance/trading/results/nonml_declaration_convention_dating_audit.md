# Audit adversarial — la datation de la convention (#486)

**Recalcul par une route différente** : un **seul** balayage de
l'historique (`git log --reverse --diff-filter=A --name-only`) au lieu
d'un `git log` par fichier, et la bascule établie par ordre plutôt que
par médianes.

| Grandeur | Audit | Rapport | Verdict |
|---|---|---|---|
| PREREG_ datés | **461** | 461 | **concordant** |
| déclarés | **33** | 33 | **concordant** |
| introduits avant le 1er déclaré | **380** | 380 | **concordant** |

## La bascule — contrôle direct, sans médiane

Le rapport affirme qu'**aucun** pré-enregistrement antérieur au premier
déclaré ne porte d'auto-déclaration. **Contrôle en balayant l'ordre
chronologique**, sans passer par une statistique de position :

- premier déclaré : **13/08/2026**
- pré-enregistrements strictement antérieurs : **380**
- **parmi eux, déclarés** : **0**

> **La bascule est confirmée, et elle est nette.** Zéro déclaré
> sur **380** antérieurs : ce n'est pas une tendance,
> c'est une **date d'apparition**.

## Le contrôle central — le rapport publie-t-il ce qui le contredit ?

Le verdict retenu est **C** (« aucune structure temporelle »), alors que
la bascule est nette. **Un rapport pourrait s'abriter derrière son
critère et n'en rien dire.**

| Contrôle | Résultat |
|---|---|
| le rapport publie la date de bascule | **OUI** |
| il publie le compte d'antérieurs déclarés (0) | **OUI** |
| il écrit que la phrase du #483 est corroborée | **OUI** |
| il dit que c'est SON critère qui échoue | **OUI** |
| il refuse de rebaisser le seuil après mesure | **OUI** |
| le verdict C est maintenu malgré tout | **OUI** |
| les deux médianes sont publiées côte à côte | **OUI** |

> **Le rapport publie contre son propre verdict.** Il maintient **C**
> parce que le seuil était préalable, **et** publie le fait qui aurait
> donné **A** avec un seuil plus bas. C'est la seule façon honnête de
> tenir les deux à la fois.

## Effets de bord du backtest

- écritures : **1** (`OUT` seul)
- exécution d'un script du dépôt / `checkout` / suppression : **0**

**Aucun effet de bord — lecture de `git` et du disque.**

## Verdict

**CONCORDANT** — **3/3** grandeurs se retrouvent par
une route indépendante, la bascule est **confirmée**, et
**7/7** contrôles de
transparence sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution (cycles #436-#438).
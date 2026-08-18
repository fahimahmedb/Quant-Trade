# Audit adversarial — la convention et son détecteur (#492)

**Le cycle soupçonnait un artefact de format, et le trouve.** C'est
**le résultat qui l'arrange** : il transforme un abandon de convention —
dont il serait responsable — en défaut de détecteur. **L'audit teste
donc l'hypothèse contre elle-même.**

## 1. La variante typographique existe-t-elle vraiment ?

Route : extraire **le texte réel** des déclarations captées par la
tolérante mais pas par la littérale, et vérifier qu'il s'agit bien de la
phrase entière en gras.

- `PREREG_` captés par la **tolérante seule** : **38**

Extraits **verbatim** :

```
PREREG_backlog_figures_verification.md : **Cycle de VÉRIFICATION.**
PREREG_battery_indet_hoist_declared.md : **Cycle de MODIFICATION**
PREREG_battery_witness_hoist.md : **Cycle de MODIFICATION**
PREREG_citer_451_definition.md : **Cycle de VÉRIFICATION**
PREREG_citer_451_resolution.md : **Cycle de VÉRIFICATION**
```

> **La variante est réelle et lisible.** Ce ne sont pas des
> déclarations approximatives rattrapées par une règle lâche : ce sont
> **les mêmes mots, avec les astérisques déplacés**.

## 2. La tolérante n'élargit-elle **que** la typographie ?

Contrôle : les déclarations qu'elle capte en plus contiennent-elles
toutes littéralement `Cycle de` / `Cycle d'` ? Si l'une ne le contenait
pas, la règle aurait élargi la **notion**, pas la mise en forme.

- captés en plus **sans** la locution « Cycle de » : **0**

> **Aucun.** La tolérante ne reconnaît rien que la littérale aurait
> refusé sur le fond. **L'élargissement est purement typographique**,
> comme annoncé.

## 3. Le déclin **littéral** était-il réel ?

Le #486 avait raison **sous sa règle**. Contrôle indépendant : parmi les
20 plus récents, combien la littérale en voit-elle ?

- littérale sur les 20 plus récents : **1 / 20**
- tolérante sur les 20 plus récents : **19 / 20**

> **Le déclin littéral est réel — et sans signification.** Le #486
> mesurait la couverture d'un détecteur ; il ne s'est pas trompé, il
> a mesuré autre chose que ce qu'on lui a fait dire.

## 4. Le cycle se donne-t-il le beau rôle ?

| Contrôle | Résultat |
|---|---|
| il déclare **dans le PREREG** que l'hypothèse l'arrange | **OUI** |
| il publie la réserve sur son propre mérite à l'avoir prédit | **OUI** |
| il dit qu'aucun chiffre du #486 n'est faux | **OUI** |
| il refuse de changer la règle du #483 ailleurs | **OUI** |
| il nomme les 5 cycles concernés un par un | **OUI** |

> **Le cycle publie que le résultat l'arrange**, que son mérite à
> l'avoir prédit n'est pas vérifiable par un tiers, et que le #486
> n'a écrit aucun chiffre faux. **Il refuse aussi d'étendre la règle**
> hors de son propre rapport.

## Verdict

**CONCORDANT** — la variante est **réelle**,
l'élargissement est **purement typographique**, le déclin littéral est
**réel mais sans signification**, et **5/5** contrôles de transparence sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date
> de son exécution (cycles #436-#438).
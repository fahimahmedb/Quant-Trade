# Audit adversarial — les sections conditionnelles (#478)

**Recalcul par une route différente** : les gardes sont établies par
**indentation** (remontée textuelle) au lieu de l'arbre syntaxique, et
les titres par **expression régulière** au lieu de `ast.Constant`.

| Grandeur | Audit (indentation) | Rapport (AST) | Verdict |
|---|---|---|---|
| scripts producteurs distincts | **766** | 766 | **concordant** |
| rapports hors convention | **308** | 308 | **concordant** |
| scripts avec ≥ 1 titre conditionnel | **26** | 31 | **ÉCART** |
| médiane par script affecté | **2,0** | 2,0 | **concordant** |
| maximum sur un script | **3** | 3 | **concordant** |

- titres conditionnels comptés par l'audit : **47** sur **792** titres

## L'écart — et laquelle des deux routes est fautive

**Un audit qui diverge doit dire s'il a raison.** Ici, non.

Ma règle de titre s'écrit `[^"']*` : elle **s'arrête à la première
apostrophe**. Dans un dépôt dont tous les titres sont en français, cela
écarte « L'appariement de prose », « Ce que ce cycle n'établit pas »,
« Les « écarts » — et pourquoi aucun n'en est un »…

- titres capturés par une variante corrigée mais **pas** par la mienne : **198**
- dont contenant une **apostrophe** : **198**

> **C'est mon instrument qui sous-compte, pas le backtest qui
> sur-compte.** `ast.Constant` lit la valeur de la chaîne après analyse
> syntaxique : les apostrophes lui sont indifférentes.

**Le backtest n'est donc pas réaligné sur l'audit** — ce serait aligner
le bon chiffre sur le mauvais. L'écart est publié, sa cause est
démontrée, et les deux nombres restent lisibles côte à côte.

La variante corrigée est publiée **à côté** de la règle d'origine, jamais
à sa place :

```python
TITRE  = r"""(append|write|print)\s*\(\s*(["'])(#{2,3}\s[^"']*)"""  # la mienne
TITRE2 = r"""(append|write|print)\s*\(\s*"(#{2,3}\s[^"]*)""""      # corrigée
```

## L'échantillon est-il bien le bon ?

- `nonml_prereg_convention_coverage_backtest.py` (**3**) — examiné dans le rapport : **oui**
- `nonml_reproducibility_campaign_v2_backtest.py` (**3**) — examiné dans le rapport : **oui**
- `nonml_reproducibility_sample_backtest.py` (**3**) — examiné dans le rapport : **oui**
- `nonml_reproducibility_sample_lot2_backtest.py` (**3**) — examiné dans le rapport : **oui**
- `nonml_reproducibility_sample_lot3_backtest.py` (**3**) — examiné dans le rapport : **NON**

**1 script(s) diffèrent** — l'ex æquo à trois titres
rend l'ordre alphabétique décisif ; écart publié tel quel.
  - `nonml_reproducibility_sample_lot3_backtest.py` (**3**)

## Le contrôle que le backtest ne fait pas : le témoin inconditionnel

Le rapport conclut que la ligne de partage n'est pas « conditionnel ou
non » mais « **la garde a-t-elle un témoin inconditionnel** ». Il l'établit
**à la main sur cinq scripts**. Voici une approximation mécanique, sur
les mêmes cinq, pour voir si elle va dans le même sens.

Un titre gardé par `if <var>:` a un **témoin** si une ligne d'écriture
**non gardée** de la même fonction mentionne `<var>`.

| Script | Gardes sur variable | Avec témoin |
|---|---|---|
| `nonml_prereg_convention_coverage_backtest.py` | 3 | **1** |
| `nonml_reproducibility_campaign_v2_backtest.py` | 3 | **3** |
| `nonml_reproducibility_sample_backtest.py` | 3 | **3** |
| `nonml_reproducibility_sample_lot2_backtest.py` | 3 | **3** |
| `nonml_reproducibility_sample_lot3_backtest.py` | 3 | **3** |

**Cette approximation ne remplace pas la lecture** : elle ne sait pas si
le témoin *explique* l'absence, seulement s'il existe. Elle est publiée
comme indice, **pas comme mesure**.

## Effets de bord du backtest

- écritures : **3** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire le disque.**

## Verdict

**DISCORDANT** — **4/5** grandeurs se retrouvent par
une route indépendante.

**L'écart est publié tel quel, et sa cause établie : il vient de
l'audit.** Une route de contrôle plus faible que celle qu'elle
contrôle reste utile — elle a obligé à démontrer *pourquoi* l'AST
était le bon outil, ce que la seule concordance n'aurait jamais
prouvé.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).
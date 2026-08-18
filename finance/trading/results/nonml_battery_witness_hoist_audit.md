# Audit adversarial — le témoin non déplacé (#490)

**Ne rien faire est le résultat le moins coûteux.** L'audit vérifie donc
que l'abstention est **décidée par la mesure**, et non commode.

*(Les motifs de recherche de cet audit **normalisent le markdown** —
gras, code, retours à la ligne. Cinq audits de cette série ont échoué
sur du texte français mis en gras ; la classe d'erreur est corrigée ici
plutôt que constatée une sixième fois.)*

## 1. La portée annoncée est-elle exacte ?

Route : parcours **ascendant** des parents AST — l'inverse du parcours
descendant du backtest.

| Nom | Ligne | Profondeur (parcours ascendant) |
|---|---|---|
| `indet` | 157 | **1** |
| `executes` | 97 | **0** |

> **Confirmé par une route indépendante.** `indet` est sous garde,
> `executes` ne l'est pas. **L'abstention repose sur un fait, pas sur
> une impression.**

## 2. Le hissage serait-il vraiment anodin ?

Le rapport l'affirme **contre lui-même** : hisser le calcul serait sans
effet. **Contrôle : l'expression n'appelle-t-elle que des fonctions
pures ?**

- appels dans l'expression de `indet` : **sum**
- tous **purs** *(builtins sans effet de bord)* : **OUI**

> **L'aveu du rapport est vérifié.** Le hissage n'aurait eu aucun
> effet observable — **le cycle s'est donc privé d'une réparation
> inoffensive**, par la seule lettre de son pré-enregistrement.

**C'est le coût réel de la discipline, et il est ici visible :** un
geste sûr n'a pas été fait parce qu'il n'avait pas été annoncé.

## 3. Est-ce bien SON pré-enregistrement qui l'a empêché ?

- le pré-enregistrement interdit explicitement le hissage : **OUI**
- il a été committé **avant** le résultat : **OUI**

> **L'interdiction est bien dans le texte pré-enregistré**, écrite
> avant de connaître la portée de `indet`. **L'abstention n'est pas
> une justification construite après coup.**

## 4. Le dépôt est-il intact ?

- fichiers modifiés hors ceux du cycle : **0**
- rapport de `battery_coverage` : **inchangé**

> **Aucune modification, aucune exécution.** Le cycle a fait exactement
> ce qu'il annonçait : **rien**.

## 5. Le cycle publie-t-il ce qui l'accuse ?

| Contrôle | Résultat |
|---|---|
| il déclare d'avance que le résultat sur la règle serait non informatif | **OUI** |
| il écrit que son pré-enregistrement était trop strict | **OUI** |
| il dit que le hissage aurait été anodin | **OUI** |
| il refuse d'assouplir la règle après mesure | **OUI** |
| il inscrit le hissage comme piste à déclarer | **OUI** |

> **Le cycle publie que sa propre règle lui a coûté une réparation
> sûre**, et refuse quand même de l'assouplir. C'est la seule façon
> de rendre une abstention crédible.

## Verdict

**CONCORDANT** — la portée est **confirmée**
par une route ascendante, le caractère anodin du hissage **vérifié**,
l'interdiction **présente dans le texte pré-enregistré**, le dépôt
**intact**, et **5/5**
contrôles de transparence tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).
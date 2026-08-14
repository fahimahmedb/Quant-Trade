# Séparer **porteurs** et **citeurs** par le script émetteur (pré-enregistré)

Le **#465** n'y arrivait pas, et avait publié pourquoi : une citation
verbatim de la marque produit une ligne **textuellement identique** à la
marque. Le **#451** le pouvait, parce qu'il savait **quel script émet**
l'encart. Ce cycle utilise cette information.

## Le résultat

- rapports **contenant** la marque : **22**
- **PORTEURS** *(le script producteur l'émet)* : **21**
- **CITEURS** *(le producteur ne l'émet pas)* : **1**
- **INDÉTERMINÉS** *(aucun script producteur)* : **0**
- dont le producteur **mentionne** la marque sans l'écrire *(forme du cas)* : **1**

### Ma règle reproduisait la confusion qu'elle devait résoudre

*Diagnostic ajouté après mesure, et signalé comme tel.*

La règle déclarée disait : **le script contient la chaîne ⇒ il l'émet.**
C'est faux. Un script qui **cherche** la marque la contient aussi — le
`content_defined_magnitudes` du #465 la porte en constante (`PHRASE =`)
précisément pour la chercher.

> **J'ai transposé dans le code la confusion *porter / mentionner* que ce
> cycle devait lever dans les rapports.** Le #446 l'avait résolue pour les
> verdicts, le #451 pour l'encart, le #465 avait échoué à la lever — et
> elle revient ici, d'un cran plus haut.

La lecture ci-dessus applique donc un critère **plus étroit** : le script
doit **écrire** la marque (`append`/`write`/`print`), pas seulement la
contenir.

> **La distinction existe.** Le #465 la cherchait dans le texte des
> rapports, où elle est invisible ; elle se lit dans le **code des
> scripts**.

## Les citeurs, **examinés un par un**

L'engagement 3 l'exige : un compte ne suffit pas. Un script peut
**construire** la marque par variable ou concaténation, et son rapport
serait alors classé citeur **à tort**.

| Rapport | Script producteur | Indices de construction dans le code |
|---|---|---|
| `nonml_selfref_reports_marking_result.md` | `nonml_selfref_reports_marking_backtest.py` | `dépendant`, `dépôt` |

**1** citeur(s) présentent des **indices de
construction** de la marque dans leur code : leur classement est
**incertain**, et je ne les compte pas comme des citeurs établis.

### L'examen, mené — et il retire le seul citeur

`selfref_reports_marking` est **le script du #439 qui a posé les
marques** dans les autres rapports. Son code porte la marque dans
une **variable** (`MARKER = "..."`) qu'il écrit dans les fichiers
candidats — **son propre rapport compris**.

Mon détecteur d'émission cherche la marque **littérale** sur une
ligne d'écriture ; il ne peut pas voir une écriture par variable.
**C'est exactement le cas que le pré-enregistrement annonçait comme
un faux citeur**, et c'en est un.

> **Conclusion de l'examen : 0 citeur établi.** Le seul candidat
> est un **porteur** que ma règle ne sait pas reconnaître.

## Contrôle de cohérence — un script qui émet, un rapport qui contient

Si un script émet la marque, son rapport doit la contenir. L'inverse
signalerait une régénération perdue, comme au #450.

- **incohérences** : **1**

| Script émetteur | Rapport sans la marque |
|---|---|
| `nonml_six_reports_regeneration_backtest.py` | `nonml_six_reports_regeneration_result.md` |

> Ces rapports **ont perdu** un encart que leur script émet. C'est
> exactement la perte que le #450 avait constatée sans la réparer.

## Les indéterminés — **pas des fautifs**

**0** rapports contiennent la marque sans qu'un script
producteur soit trouvé sous la convention de nommage. Le **#464** a
établi que cette convention **n'est pas universelle** : ce sont des
rapports **hors convention**, pas des anomalies.


## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| au moins 1 citeur **établi** | ≥ 1 | 0 *(1 candidat(s), retiré(s) par l'examen)* | **réfutée** |
| porteurs < rapports contenant la marque | < 22 | 21 | **vérifiée** |
| aucune incohérence émetteur/rapport | 0 | 1 | **réfutée** |

**Aucun citeur établi.** Le compte mécanique en donnait **1** ; l'examen exigé par l'engagement 3 l'a retiré.

**Retenir le chiffre flatteur alors que mon propre examen le
contredit serait l'erreur exacte des #462, #464 et #465.**

**Aucun citeur trouvé.** Le pré-enregistrement prévoyait ce cas et
interdit d'en conclure que le #451 s'est trompé : **soit** son citeur
a disparu du dépôt depuis, **soit** ma règle le classe porteur à tort.
Je ne tranche pas ici — il faudrait remonter au commit du #451, ce que
ce cycle n'a pas déclaré faire.

## Critères de succès

1. **22/22** rapports classés — **OUI**.
2. Tout citeur publié nominativement avec son producteur — **OUI**.
3. Chaque citeur examiné (construction par variable) — **OUI**.
4. Indéterminés listés sans être présentés comme fautifs — **OUI**.

**PASS** — le critère porte sur le procédé.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun rapport ni aucun script.
- Il n'**exécute** rien : lecture seule, aucun effet de bord.
- Il ne **remonte** à aucun commit ancien : il décrit le dépôt
  d'aujourd'hui.


> **Rapport dépendant du dépôt** — il décrit l'état du dépôt à la date de
> son exécution (cycles #436-#438).
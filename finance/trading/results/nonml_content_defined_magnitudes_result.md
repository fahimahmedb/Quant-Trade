# Les grandeurs définies par le **contenu** (pré-enregistré)

Le **#462** a conclu **contre lui-même** que trois des quatre faux connus
lui échappaient : ils se définissent par le **contenu** des fichiers, pas
par leur nom. Ce cycle en compte **deux**.

## La distinction qui décide — **porter** n'est pas **mentionner**

Le #451 a établi que le « 6 » du backlog était faux parce qu'il comptait
comme marqués des rapports qui **parlent** de l'encart. C'est exactement le
défaut du #446 sur la règle de verdict.

**Porte** = une ligne, décoration retirée, **commence par** la marque.
**Mentionne** = la phrase apparaît, sans être portée en tête de ligne.

## La table

**36/36** cellules.

| Entrée | Commit | G1 total | dont instrument du #449 | G1 hors instrument | G2 porteurs |
|---|---|---|---|---|---|
| #443 | `7d1fe406` | 0 | 0 | **0** | 7 |
| #444 | `d33c53ad` | 0 | 0 | **0** | 7 |
| #445 | `a0c7b818` | 0 | 0 | **0** | 6 |
| #446 | `98858d2e` | 0 | 0 | **0** | 6 |
| #447 | `bda9171d` | 0 | 0 | **0** | 6 |
| #448 | `64c19b43` | 0 | 0 | **0** | 6 |
| #449 | `8aea8994` | 8 | 2 | **6** | 6 |
| #450 | `fcef6f48` | 8 | 2 | **6** | 3 |
| #451 | `1d764963` | 8 | 2 | **6** | 8 |
| #452 | `2dd64b47` | 8 | 2 | **6** | 10 |
| #453 | `d01dd7a9` | 8 | 2 | **6** | 11 |
| #454 | `76a60944` | 10 | 2 | **8** | 12 |
| #455 | `88b45b8a` | 10 | 2 | **8** | 13 |
| #456 | `d33c32ca` | 11 | 2 | **9** | 14 |
| #457 | `7e1414ca` | 12 | 2 | **10** | 15 |
| #458 | `7e310dd6` | 13 | 2 | **11** | 16 |
| #459 | `e2f80f77` | 14 | 2 | **12** | 17 |
| #460 | `5d98fce5` | 15 | 2 | **13** | 18 |

## Les deux faux connus, recomptés

| Entrée | Annoncé | Recompté au commit | Verdict |
|---|---|---|---|
| #449 | **8** consommateurs, corrigé en **6** | **8** importateurs dont **2** d'instrument, soit **6** consommateurs, à `8aea8994` | **la correction « 6 » est CONFIRMÉE** |
| #451 | **6** porteurs | **8** à `1d764963` | **le « 6 » était bien faux** |

### Le mécanisme du « 6 »

Au commit du #451 : **8** rapports **portent** la marque,
**0** la **mentionnent** sans la porter.

**Aucun mentionneur** — alors que le #451 en identifiait **un**.
Vérifié plutôt que supposé : au commit du #451, **8** fichiers
contiennent la phrase, et ma règle en classe **8** comme porteurs.

> **Ma distinction ne peut pas tenir, et c'est le résultat le plus
> utile de ce cycle.** Un rapport qui **cite verbatim** la marque
> produit une ligne **textuellement identique** à celle d'un rapport
> qui la porte. Aucune règle de début de ligne ne les sépare.

Le #451, qui avait accès au *script émetteur*, pouvait trancher :
il savait quel script émet la marque. **Moi qui ne lis que le
texte, je ne le peux pas.** Le « 8 » ci-dessus est donc un
**majorant** : il vaut probablement **7** porteurs et **1** citeur,
conformément au #451 — et dans les deux cas **≠ 6**.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| G1 ≠ 8 au commit du #449 | ≠ 8 | 8 | **réfutée** |
| et précisément G1 = 6 | 6 | 8 | **réfutée** |
| G2 ≠ 6 au commit du #451 | ≠ 6 | 8 | **vérifiée** |
| mentionneurs > porteurs au #451 | > | 0 vs 8 | **réfutée** |

### Pourquoi je **n'accuse pas** le #449 — vérifié avant de conclure

Le pré-enregistrement disait que si G1 valait 8, alors **la correction
du #449 était fausse**. Le chiffre est tombé sur 8. **J'ai regardé les
fichiers avant de l'écrire.**

Sur les **8** importateurs, **2** sont les scripts du cycle
#449 **lui-même** (`verdict_rule_propagation_backtest.py` et son audit) :
**l'instrument qui a propagé la règle, pas un consommateur de la règle.**
Les **6** autres sont exactement les « six consommateurs »
que l'entrée cite.

> **La correction du #449 est juste.** Ma prédiction reposait sur une
> définition plus large que la sienne, et l'écart mesure la définition,
> pas une erreur. **Publier « la correction était fausse » aurait été
> une accusation infondée** — la faute du #462 avec ses 9 discordances,
> et du #464 avec ses 70 rapports « manquants ».

C'est la **troisième fois de suite** qu'un de mes comptes accuse à tort
la trace du dépôt. Le point commun est toujours le même : **une
définition à moi, confrontée à une définition d'eux, présentée comme un
écart de fait.**

## Ce que ce cycle ne peut pas faire

- **G1 est une borne inférieure.** `import nonml_verdict` ne capture pas
  un script qui **réimplémenterait** la règle sans l'importer — et les
  #446-#448 ont montré que de telles copies ont existé.
- Le faux du **#453** (« 13 orphelins ») est une **relation** entre deux
  globs : toujours hors de portée, et **rien n'a été ajouté pour lui**.
- Il ne couvre que **deux** grandeurs de contenu sur toutes celles que le
  backlog énonce en prose.

## Critères de succès

1. **36/36** cellules — **OUI**.
2. Les deux faux recomptés — **OUI**.
3. Distinction porte / mentionne publiée avec ses deux chiffres — **OUI**.
4. Définitions inchangées après mesure — **OUI**.

**PASS** — le critère porte sur le procédé.


> **Rapport épinglé** — chaque grandeur est comptée au commit qui a créé
> l'entrée. Réexécuté dans dix cycles, il doit rendre les mêmes chiffres.
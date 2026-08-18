# Les **emprunts**, confrontés à leur source (pré-enregistré)

Le **#500** a recensé les emprunts et s'est interdit d'en juger la
justesse : *« il mesure une exposition, pas une erreur »*. **Ce cycle
mesure ce qui peut l'être.**

## La règle de confrontation, citée verbatim

> Pour un emprunt du script `S`, citant `#NNN`, de nombre en gras `x`,
> la **source** est la section `## Backlog #NNN` du registre publié :
> - **confirmé** — `x` apparaît **en gras** dans la section `## Backlog #NNN` ;
> - **retrouvé ailleurs** — `x` apparaît **en gras** dans une autre section du backlog ou dans un `results/*.md` ;
> - **non retrouvé** — `x` n'apparaît en gras **nulle part** ;
> - **non vérifiable** — la section `## Backlog #NNN` **n'existe pas** ;

- **chaînes** empruntées — l'unité du #500 : **31**
- **nombres** empruntés — l'unité d'ici : **39**
- sections de backlog disponibles : **297**

> **Les deux unités diffèrent, et il faut le dire** : le #500 comptait
> des **chaînes publiées**, une chaîne pouvant porter plusieurs nombres.
> Confronter exige de descendre **au nombre**. Aucun emprunt du #500
> n'est écarté — ils sont **dépliés**.

## Les quatre classes

| Classe | Nombre | Part |
|---|---|---|
| **confirmé** | **22** | **56,4 %** |
| **retrouvé ailleurs** | **17** | **43,6 %** |
| **non retrouvé** | **0** | **0,0 %** |
| **non vérifiable** | **0** | **0,0 %** |

## La coupure forte / faible — sans elle, le taux ment

Un nombre à moins de **3** chiffres se retrouve **par
hasard** dans presque n'importe quelle section. Les confirmations sont
donc séparées :

| Confirmations | Nombre | Part des confirmées |
|---|---|---|
| **fortes** (≥ 3 chiffres) | **3** | **13,6 %** |
| **faibles** (1-2 chiffres) | **19** | **86,4 %** |

> **La majorité des confirmations sont faibles.** La conclusion
> honnête n'est donc **pas** « les emprunts sont exacts » mais
> **« la méthode ne sait pas les départager »**. Convertir cette
> faiblesse en satisfecit était exactement ce que le
> pré-enregistrement interdisait.

## Les non retrouvés — la liste de suspects

- effectif : **0**

**Aucun.** Tout nombre emprunté se retrouve en gras quelque part dans
le dépôt — ce qui **n'établit pas** qu'il y soit au bon endroit.

## Ce que ce cycle **n'établit pas**

**Aucun chiffre n'est déclaré faux.** Un « non retrouvé » signale un
emprunt **invérifiable par cette méthode**, pas une erreur : le nombre
peut vivre dans un rapport que la règle ne consulte pas, ou avoir été
écrit avec une autre typographie — le **#498** a montré qu'une règle
littérale rate **85,0 points** de détection sur une simple mise en
forme. *(Ce chiffre est **lu** dans le rapport du #498 : dans un cycle
sur les emprunts, le retaper aurait été une faute de plus.)*

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| confirmés ≥ 20 | ≥ 20 | 22 | **vérifiée** |
| ≥ 1 non retrouvé | ≥ 1 | 0 | **réfutée** |
| majorité de confirmations faibles | > 50 % | 86,4 % | **vérifiée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

La population est **importée** du backtest du #500 (ses fonctions, pas
son `main()`) : recopier une définition est le meilleur moyen de la
faire diverger — leçon du #499.

## Critères de succès

1. Règle citée verbatim, quatre classes publiées avec leur compte — **OUI**.
2. Toutes les **31** chaînes du #500 dépliées en **39** nombres, aucune écartée — **OUI**.
3. Confirmations fortes (**3**) et faibles (**19**) comptées séparément — **OUI**.
4. Non retrouvés nommés individuellement (**0**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts et du
> registre à la date de son exécution.

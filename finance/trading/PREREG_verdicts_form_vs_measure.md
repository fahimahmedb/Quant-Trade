# Pré-enregistrement — les verdicts du dépôt : **forme** ou **mesure** ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #505.

## D'où vient la question

Le **#498** a montré qu'un verdict pouvait basculer de **C** à **A** **sans
que rien ne change dans les faits** : seul le détecteur avait changé, d'une
règle littérale à une règle tolérante. **Un verdict vaut ce que vaut son
détecteur.**

Le dépôt publie des centaines de verdicts. **Personne n'a jamais compté
combien reposent sur un appariement de forme** — une expression régulière sur
du texte — plutôt que sur une **mesure** de séries de prix ou de P&L.

> C'est une question sur la **nature** de ce projet, pas sur un de ses
> détails. Un outil censé étudier des marchés qui passerait son temps à
> s'ausculter lui-même devrait au moins le savoir.

## Les quatre classes — **figées ici**, établies par AST

Pour chaque script `nonml_*_backtest.py` dont le rapport publie un verdict :

- **lit des données** : il porte un littéral finissant par `.txt`, `.npz` ou
  `.csv`, **ou** mentionnant `data/`, **ou** importe `data_loader` /
  `load_ohlc` ;
- **lit le texte du dépôt** : il porte un littéral finissant par `.md` ou
  `.py`, **ou** un `glob` sur ces extensions ;
- **apparie** : il fait `import re`.

| Classe | Condition |
|---|---|
| **F — forme** | lit le texte **et** apparie, **sans** lire de données |
| **D — mesure** | lit des données, **sans** lire le texte du dépôt |
| **M — mixte** | lit **les deux** |
| **N — ni l'un ni l'autre** | aucun des deux |

**Rapport porteur de verdict** : son `.md` contient `**PASS**` ou `**FAIL**`.

## Ce qui est mesuré

1. La population des rapports **porteurs d'un verdict**, et les **quatre
   classes**.
2. La **chronologie** : date médiane d'introduction de chaque classe, par
   `git log --diff-filter=A`.
3. Les **20 plus récents**, nommés avec leur classe.
4. La part de **F** parmi les 20 plus récents contre sa part sur **l'ensemble**
   — c'est la mesure de la dérive.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **quatre classes** citées verbatim, établies par **AST**.
2. Population et **quatre comptes** publiés.
3. Les **dates médianes** par classe publiées.
4. Les **20 plus récents** nommés avec leur classe, et les deux parts de **F**
   comparées.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. La part de **F** sur l'ensemble est **≥ 50 %**.
2. Parmi les **20 plus récents**, il reste **≥ 1** script de classe **D** —
   la dérive vers le texte n'est **pas** totale.
3. La date médiane des **F** est **postérieure** à celle des **D** : le dépôt
   a commencé par mesurer des marchés et a fini par se mesurer lui-même.

Si la prédiction 3 est réfutée, alors les deux familles sont **contemporaines**
et il n'y a **pas de dérive** — seulement deux activités menées en parallèle
depuis le début. Je devrai l'écrire ainsi, contre l'intuition qui m'a fait
poser la question.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucun verdict.
- Il ne **juge pas** qu'un verdict de forme soit **faux** : vérifier qu'un
  script n'a pas de défaut d'exécution est un travail légitime, et le #498
  montre seulement qu'un tel verdict est **fragile au détecteur**.
- Il ne **classe pas** ce cycle-ci — qui serait, par sa propre règle, un **F**
  de plus. **Cette auto-exclusion est déclarée**, conformément à la règle du
  #447 : elle sera **rappelée dans le rapport**, pas tue.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que ce projet a cessé
   d'étudier les marchés.
2. Classes et population **inchangées** après mesure.
3. Les quatre classes publiées, jamais les seules qui arrangent.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

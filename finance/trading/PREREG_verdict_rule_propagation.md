# Pré-enregistrement — propager la règle du #448 aux autres consommateurs

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, cinquième après les #445 → #448.

## Le point de départ, et pourquoi il est déjà suspect

Le #447 a compté **9 scripts** portant le motif `"**PASS" in`, le #448 en a
laissé **8** non corrigés. Ce compte vient d'un `grep` — c'est-à-dire d'une
**recherche en sous-chaîne**, exactement l'instrument dont ces quatre cycles
viennent de démontrer qu'il confond **le code et le discours sur le code**.

Il y a donc tout lieu de penser que ce compte est faux, et de la même manière.
Certaines occurrences sont des **usages** (la règle sert à classer quelque
chose) ; d'autres sont des **réimplémentations délibérées de l'ancienne règle**,
écrites pour la *mesurer* — notamment dans les scripts des #446 et #447, qui
comparent l'ancienne et la nouvelle.

**Toucher à une réimplémentation historique détruirait la mesure qu'elle porte.**

## Le périmètre — établi par lecture, pas par grep

Chaque occurrence est **lue** et classée :

- **usage** — la règle décide d'un classement, d'un compte, d'un verdict :
  elle est convertie ;
- **réimplémentation historique** — la règle *ancienne* est reproduite
  volontairement pour être comparée : elle est **laissée intacte**, et la raison
  est publiée.

Le compte de 8 n'est **pas** repris comme acquis : il sera recompté par lecture,
et l'écart avec le grep publié.

## La modification — un module partagé, et pourquoi cette fois

Les #447 et #448 ont dû écrire la règle **en clair**, puis en **opérations de
chaînes**, pour ne pas sortir de régions trop étroitement déclarées. Répliquer
cela dans sept scripts produirait sept copies destinées à diverger.

**Régime déclaré ici — trois catégories de région :**

(a) un **nouveau fichier** `scripts/nonml_verdict.py` portant `_nu` et
    `porte_verdict`, repris **à l'identique** du balayage ;
(b) dans chaque script converti, la **zone d'imports** ;
(c) dans chaque script converti, **les lignes de l'occurrence**.

La zone d'imports est déclarée **d'avance** cette fois. Aux #447 et #448 elle ne
l'était pas, ce qui m'a obligé à contorsionner le code pour respecter mon propre
régime. La leçon est tirée **avant** d'écrire, pas après avoir buté dessus.

Le fichier `nonml_verdict.py` ne se termine ni par `_backtest.py` ni par
`_audit.py` : il n'entre donc dans aucun des `glob` du dépôt, et n'ajoute pas de
candidat fantôme aux inventaires.

## Ce que ce cycle ne fait PAS — dit d'avance

**Aucun des rapports publiés par ces scripts n'est régénéré.** Les régénérer
mélangerait l'effet de la règle et la dérive du dépôt (démonstration au #445 :
9 lignes sur 10 n'étaient pas dues à la modification), et sept fois plutôt qu'une.

Ce cycle crée donc **sciemment** un écart entre le code corrigé et les rapports
publiés. Cet écart est **mesuré, publié et inscrit à la dette** — il n'est pas
un oubli. Le régénérer proprement est un cycle à lui seul.

## Critère de succès — chiffré, et il peut échouer

1. **Chaque occurrence classée** *usage* ou *réimplémentation*, avec sa
   justification. Le compte par lecture est comparé au compte par grep.
2. **Équivalence** : `nonml_verdict.porte_verdict` et la fonction du balayage
   donnent le **même verdict sur les 300+ rapports du dépôt**, 0 divergence.
3. **Diff confiné** aux trois catégories de région déclarées. Toute ligne
   touchée ailleurs vaut échec.
4. **Aucune réimplémentation historique modifiée** — vérifié après coup :
   les scripts des #446/#447 doivent encore contenir l'ancienne règle sous sa
   forme exécutable.
5. Pour chaque script converti, **le nombre de rapports de son corpus qui
   changent de classe** est publié.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédiction — falsifiable

- **Le compte de 8 est faux.** Je m'attends à trouver **moins** de 8 usages, le
  reste étant des réimplémentations. Je ne sais pas combien.
- Au moins un script converti verra **≥ 1** rapport changer de classe — sans
  quoi la propagation serait sans effet et il faudrait se demander pourquoi on
  la fait.
- Je **n'exclus pas** qu'un script utilise une variante du motif (par exemple
  sans le littéral `"PASS (niveau 1)"`), auquel cas le convertir **changerait sa
  sémantique** au-delà de la correction visée. Ce cas serait publié et le script
  **laissé tel quel**, faute de pouvoir le corriger sans le redéfinir.

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL**.
2. Aucune ligne hors des régions déclarées.
3. Aucune réimplémentation historique touchée.
4. Aucun rapport publié régénéré ; l'écart créé est mesuré et inscrit.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).

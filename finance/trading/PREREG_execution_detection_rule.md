# Pré-enregistrement — une règle de classe qui **voit l'exécution en process**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #495.

## Ce que le #495 a cassé

Le **#494** classait un script « exécute un tiers » sur la présence de
`subprocess.run([sys.executable, …])`. Le **#495** a montré que cette règle est
**aveugle** : deux scripts importaient `nonml_pnl_duplicate_sweep_backtest` et
appelaient son `main()` **en process**, sans passer par un sous-processus.

**Les 4 témoins non publiés ont donc été mal classés** — 2 en A, 2 en C, alors
que le #495 conclut qu'ils sont **tous de classe C**. Cette conclusion repose
sur une lecture de 2 cas ; **elle n'a jamais été mesurée sur les 4**.

## La règle corrigée — déclarée ici

Un script **exécute un tiers du dépôt** si l'une au moins de ces conditions est
vraie, établie par **AST** :

1. `subprocess.run([sys.executable, …])` — la forme du #494 ;
2. il **importe un module `nonml_*`** du dépôt **et** appelle `.main()` sur
   l'alias de cet import — la forme découverte au #495 ;
3. il appelle `runpy.run_path`, `exec(open(…).read())` ou `importlib` sur un
   chemin de `scripts/`.

La condition 3 est ajoutée **parce que 1 et 2 ne couvrent que ce qui a déjà été
vu**. Elle peut ne rien trouver ; **c'est le but d'une règle qu'on veut moins
étroite que les faits qui l'ont motivée**.

## Ce qui est mesuré

1. **Les 4 témoins** du #494, reclassés par la règle corrigée — chacun avec la
   **condition** qui le déclenche.
2. **Tout le dépôt** : combien de scripts la règle du #494 classait « sans
   exécution » alors qu'ils exécutent en process ? **C'est l'ampleur de
   l'angle mort**, jamais mesurée.
3. Les **cibles** de ces exécutions — quels modules sont appelés, et combien de
   fois.

## Critère de succès — chiffré, il porte sur le procédé

1. La règle corrigée **citée verbatim**, ses **trois conditions** publiées
   séparément avec leur compte.
2. Les **4 témoins** reclassés, chacun avec la condition qui le déclenche.
3. L'**ampleur de l'angle mort** du #494 mesurée **sur tout le dépôt**.
4. Les **cibles** des exécutions en process nommées.
5. **Aucun script exécuté** — lecture d'AST uniquement, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les **4** témoins sont classés « exécute un tiers » — la conclusion du #495
   tient sur les 4, pas seulement sur les 2 qu'il a lus.
2. **≥ 5** scripts du dépôt échappaient à la règle du #494 et sont rattrapés par
   la condition 2.
3. La condition 3 ne trouve **aucun** script — les formes exotiques
   (`runpy`, `exec`) ne sont pas employées ici.

Si la prédiction 1 est réfutée — un des 4 n'exécute rien — alors le #495 a
**généralisé de 2 cas à 4**, et je devrai l'écrire : sa conclusion « les 4 sont
de classe C » aurait été une extrapolation, pas une mesure.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script : **AST uniquement**.
- Il ne **modifie** aucune règle ailleurs dans le dépôt — la règle corrigée
  n'existe que dans ce rapport, comme la tolérante du #492.
- Il ne **publie** aucun témoin, ne **régénère** aucun rapport.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que le #495 a extrapolé.
2. Règle, conditions et population **inchangées** après mesure.
3. **Chaque classement adossé à la condition qui le déclenche**, jamais à une
   impression.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

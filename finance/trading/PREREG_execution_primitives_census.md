# Pré-enregistrement — **recenser les primitives d'exécution**, au lieu de les rattraper une par une

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de DÉCISION + RECOMPTE**, première piste de la file ouverte au #496.

## Le motif qui se répète

La règle « ce script exécute un tiers du dépôt » a été **rapiécée trois fois** :

- **#494** : `subprocess.run([sys.executable, …])` ;
- **#495** : découvre l'exécution **en process** (`import nonml_x ; x.main()`) ;
- **#496** : ajoute la condition 2, et son audit découvre `subprocess.Popen`.

**Chaque cycle rattrape la forme que le précédent avait manquée.** C'est un
procédé qui ne converge pas : rien ne dit que `Popen` est la dernière.

> **Ce cycle change de méthode** : au lieu d'ajouter la forme du jour, il **fige
> d'avance l'univers des primitives d'exécution de Python** et les compte
> **toutes**, y compris celles qui vaudront zéro.

## La décision sur `Popen`, prise sur un principe déclaré d'avance

> **Principe d'inclusion.** Une règle qui prétend dire « ce script exécute un
> tiers » doit nommer **toute primitive qui exécute effectivement**. Le critère
> est **factuel, pas historique** : une forme entre parce qu'elle lance du code
> tiers, **jamais** parce qu'un cycle antérieur l'a rencontrée.

Ce principe **aurait pu exclure** `Popen` : s'il avait été *historique* — « la
règle nomme les formes déjà observées en usage » — `Popen` serait resté dehors
jusqu'à preuve d'usage. Il est **factuel**, donc **`Popen` entre**.

Le principe est énoncé **ici**, avant tout recompte, précisément parce que le
#496 s'est interdit de l'absorber après coup.

## L'univers des primitives — **figé ici, non négociable après mesure**

Chacune est comptée **séparément**, zéro compris :

| # | Primitive |
|---|---|
| P1 | `subprocess.run([sys.executable, …])` |
| P2 | `subprocess.Popen([sys.executable, …])` |
| P3 | `subprocess.call` / `check_call` / `check_output` sur `sys.executable` |
| P4 | `os.system(…)` |
| P5 | `os.popen(…)` |
| P6 | `os.execv*` / `os.spawn*` |
| P7 | `runpy.run_path` / `runpy.run_module` |
| P8 | `exec(open(…).read())` ou `eval` sur un fichier |
| P9 | `importlib` (`spec_from_file_location`, `import_module`) sur `scripts/` |
| P10 | `import nonml_* as a` + `a.main()` — l'exécution en process du #495 |
| P11 | `from nonml_* import main` + `main()` |
| P12 | `multiprocessing.Process(target=…)` |

Toutes établies par **AST**, jamais par regex sur le texte — la distinction
**porteur / citeur** du #473 l'exige.

## Ce qui est mesuré

1. Les **12 primitives**, comptées séparément sur tous les `nonml_*.py`.
2. Le **recompte** avec la règle amendée, et son **écart** avec le #496 :
   scripts exécutants, angle mort du #494, cibles, les **4 témoins**.
3. Le **nombre de rapiéçages** qu'a subis cette règle, nommés un par un.

## Critère de succès — chiffré, il porte sur le procédé

1. Le **principe d'inclusion** cité verbatim, avec la variante qui aurait
   exclu `Popen`.
2. Les **12** primitives comptées **séparément**, zéros publiés.
3. Le recompte publié **avec son écart** vs le #496 sur les quatre grandeurs.
4. Les **rapiéçages** de la règle nommés et comptés.
5. **Aucun script exécuté** — AST uniquement, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Le recompte donne **32** scripts exécutants (30 au #496 **+ 2** `Popen`) —
   c'est-à-dire qu'**aucune** des primitives P3-P8, P11, P12 n'est employée.
2. **Au moins une** primitive hors P1/P2/P9/P10 est trouvée avec un compte
   **non nul** — ce qui **réfuterait** la prédiction 1.
3. Les **4 témoins** restent classés « exécute un tiers » : l'amendement
   **n'change rien** pour eux.

Les prédictions 1 et 2 sont **mutuellement exclusives par construction**. C'est
délibéré : je ne sais pas laquelle est vraie, et un pré-enregistrement qui
n'énonce qu'un seul côté d'une alternative que j'ignore **cache mon ignorance**.
Une des deux sera **réfutée**, et ce sera écrit.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script : **AST uniquement**.
- Il ne **modifie** aucun script du dépôt, ne **régénère** aucun rapport.
- Il ne **publie** aucun témoin — la file du #494 reste ouverte.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si l'univers figé se révèle **encore**
   incomplet — auquel cas ce serait le **quatrième** rapiéçage, et il serait
   écrit comme tel.
2. Univers des primitives et principe **inchangés** après mesure.
3. Chaque compte adossé à un motif AST, jamais à une impression.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

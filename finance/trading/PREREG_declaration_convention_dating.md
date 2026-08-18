# Pré-enregistrement — la convention d'auto-déclaration est-elle **récente ou abandonnée** ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #485.

## Ce que le #483 a trouvé sans l'expliquer

Le #483 a classé **126** pré-enregistrements sans résultat et constaté que
**113 d'entre eux (89,7 %) ne portent aucune auto-déclaration** de la forme
`Cycle de **X**` dans leurs douze premières lignes. Il a écrit que ces 113
**ne sont pas fautifs** — la convention « date d'un moment du projet, pas de son
origine » — mais **il n'a pas vérifié cette phrase**.

**C'est une hypothèse commode**, et elle mérite d'être mise à l'épreuve : si la
convention était au contraire **ancienne puis abandonnée**, les 113 seraient
une régression et non une antériorité.

## Le protocole — dater chaque `PREREG_` par son commit introducteur

Population : **tous** les `PREREG_*.md` du dépôt, déclarés ou non — et non plus
les seuls sans résultat, pour que la mesure porte sur la convention elle-même.

Pour chacun :

1. **date d'introduction** = date du **premier** commit ayant ajouté le fichier,
   par `git log --diff-filter=A --reverse --format=%ct -- <chemin>` ;
2. **déclaré** = son en-tête (douze premières lignes) contient
   `Cycle de **X**` / `Cycle d'**X**` — **la règle du #483, reprise sans
   modification**.

## Les trois lectures — toutes publiables

- **A. Convention récente** — les déclarés sont **postérieurs** aux non
  déclarés : il existe une date de bascule, et la phrase du #483 est vérifiée.
- **B. Convention abandonnée** — les déclarés sont **antérieurs** : la
  convention a existé puis cessé, et le #483 s'est rassuré à tort.
- **C. Aucune structure temporelle** — déclarés et non déclarés sont
  **entremêlés** sur toute la période : ce n'est pas une convention datée mais
  un **usage irrégulier**, et il faudra le dire.

## Le critère qui départage — fixé ici, chiffré

Soit `m_d` la **médiane** des dates des déclarés et `m_n` celle des non
déclarés, et soit `p` la **part des déclarés parmi les 40 `PREREG_` les plus
récents**.

- **A** si `m_d > m_n` **et** `p ≥ 50 %` ;
- **B** si `m_d < m_n` **et** `p < 20 %` ;
- **C** sinon.

Ce seuil est **arbitraire mais préalable**. Toute autre valeur choisie après
mesure serait un retuning.

## Critère de succès — il porte sur le procédé

1. **100 %** des `PREREG_` datés, ou l'échec à les dater **publié et compté**.
2. Les deux médianes et la part `p` **publiées**, avec la commande de datation.
3. **Une** des trois lectures explicitement nommée par le critère chiffré.
4. Si la lecture **B** sort, la phrase du #483 — « la convention date d'un
   moment du projet » — **explicitement rétractée**.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. La lecture **A** est retenue : la convention est **récente**.
2. La part `p` des déclarés parmi les 40 plus récents est **≥ 50 %**.
3. **Aucun** `PREREG_` ne résiste à la datation — l'historique les contient
   tous.

Si la lecture **B** ou **C** sort, la phrase rassurante du #483 tombe, et je
devrai l'écrire aussi nettement qu'il avait écrit « ils ne sont pas fautifs ».

## Ce que ce cycle ne fait pas

- Il n'**ajoute** aucune auto-déclaration à aucun fichier.
- Il n'**exécute** aucun script du dépôt : lecture de `git log` et du disque,
  **aucun effet de bord**.
- Il ne **juge pas** la qualité des cycles concernés, seulement la date de leur
  en-tête.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que le #483 s'est rassuré
   à tort.
2. Population, règle de déclaration et **seuils du critère** inchangés après
   mesure.
3. Les deux médianes publiées **côte à côte**, jamais la seule favorable.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

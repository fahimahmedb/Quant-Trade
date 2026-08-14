# Pré-enregistrement — les PASS jamais passés par la batterie Règle 9

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.
**Piste B**, deuxième des trois proposées au #455.

## Ce qui est en cause

La **batterie Règle 9** (`nonml_pass_validation_battery.py`) soumet un PASS à
**cinq contrôles**, tous devant passer : stress de coûts (3×, 5×), stress de
crise, stabilité temporelle par folds, SPA à 1 candidat, et DSR avec
`n_trials = taille du backlog` — **jamais 1**.

Le #431 avait compté **33** rapports PASS ne l'ayant jamais subie. Ce chiffre
date, et les #449, #451 et #453 ont chacun montré qu'**un compte de backlog non
revérifié est faux**. Il sera donc **recompté**, l'écart publié — puis la
batterie sera **effectivement passée** à ceux qui ne l'ont pas eue.

C'est la différence avec les cycles précédents : celui-ci ne se contente pas de
mesurer une lacune, il **la comble**.

## L'univers et l'ordre — figés ici

- **Univers** : candidats dont le rapport porte un **PASS** (règle unifiée
  #448/#449/#454) **et** qui possèdent un `.npz` — la batterie en exige un.
- **Manquants** : ceux sans `results/nonml_<nom>_pass_validation_battery.md`.
- **Ordre de passage : alphabétique**, fixé ici. Aucun choix de candidat, aucune
  priorité donnée à un profil.

## Le budget, déclaré parce qu'il sera contraignant

La batterie est lourde (bootstrap SPA, folds, stress). Budget de ce cycle :
**25 minutes** d'exécution cumulée.

> Les candidats traités dans ce budget sont **ceux que l'ordre alphabétique
> désigne**, pas ceux qui donnent les meilleurs résultats. Les non traités sont
> **listés nommément** avec la mention « budget épuisé », et reportés.

Ce point est déclaré **avant** de savoir combien passeront : un budget fixé après
coup permettrait de s'arrêter juste après un bon résultat.

## Critère de succès — chiffré

1. Le **compte réel** de PASS sans batterie est publié, avec l'écart aux **33**
   du #431.
2. Chaque manquant est **soit exécuté, soit listé** avec sa raison (budget,
   échec technique, `.npz` absent). Aucun écarté en silence.
3. Pour chaque batterie exécutée, le **verdict des 5 contrôles** est publié tel
   quel — y compris et surtout les échecs.
4. Aucun verdict de stratégie réécrit : la batterie **ajoute** une information,
   elle n'annule pas un PASS pré-enregistré.

> **PASS** = les quatre points. **FAIL** = un seul manque.

**Le verdict du cycle ne dépend pas du nombre de candidats qui passent la
batterie.** Zéro est un résultat publiable.

## Prédiction — falsifiable

- **Le chiffre de 33 est faux.** Sens inconnu : des batteries ont pu être passées
  depuis, et des PASS ont pu apparaître. Je ne parie pas sur la direction.
- J'attends que **peu de candidats passent les cinq contrôles**. Le contrôle
  (e) impose un DSR avec `n_trials` égal à la taille du backlog — de l'ordre de
  **150+** essais, soit une barre bien plus haute que le N de **207** corrigé du
  #456 ne le laisse croire… non : **plus basse**. Je note l'ambiguïté plutôt que
  de la trancher au doigt mouillé, et la mesure la lèvera.
- J'attends au moins un **échec au stress de crise** : c'est le contrôle qui a
  historiquement éliminé le plus de candidats dans ce projet.

## Ce que ce cycle ne fait pas

- Il ne **retire** aucun PASS. La batterie qualifie, elle ne requalifie pas.
- Il ne **modifie** aucun script de stratégie.
- Il ne **choisit** pas ses candidats : l'ordre alphabétique est la seule règle.

## Engagements

1. Résultat rapporté tel quel, y compris **0 candidat validé**.
2. L'ordre et le budget sont ceux déclarés ici, sans exception.
3. Les non traités sont nommés, pas passés sous silence.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

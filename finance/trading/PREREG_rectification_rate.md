# Pré-enregistrement — le **taux de rectification** : combien de cycles ont été corrigés par un successeur ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #511.

## D'où vient la question

Le #509 a clos la série des emprunts sur ce constat : **treize détecteurs
successifs et leurs limites**, dont plusieurs corrigés par le cycle suivant ou
par leur propre audit. Le #511 a fait tomber une **deuxième** justification du
#485.

**Personne n'a compté.** Le dépôt affirme régulièrement qu'un cycle en
rectifie un autre ; le **taux** n'a jamais été mesuré, ni sa **tendance**.

## La règle — **figée ici**

- **Population** : toutes les sections `## Backlog #NNN` du registre.
- Un cycle `#NNN` est **rectifié** si une section **postérieure** (`#MMM` avec
  `MMM > NNN`) contient une référence `#NNN` avec, dans une fenêtre de
  **±200 caractères** — la fenêtre du **#502, reprise sans modification** —
  au moins un **marqueur** de cette liste, **figée ici** :

```
réfut   rétract   corrig   invalid   fauss   faux
erron   sur-affirm   surestim   sur-estim   dissou   tombe
```

- **Auto-rectification exclue** : une section ne peut pas se rectifier
  elle-même. Seul un **successeur** compte.

## Ce que cette mesure **ne** mesure **pas** — dit d'avance

Elle mesure **la fréquence à laquelle une rectification est écrite**, pas la
fréquence à laquelle une erreur est commise.

> **Un dépôt qui n'avouerait jamais rien obtiendrait un taux de zéro.** Un
> taux élevé peut donc signaler soit beaucoup d'erreurs, soit beaucoup de
> franchise — et **cette mesure ne les distingue pas**. Toute lecture qui
> l'oublierait serait fausse, y compris la mienne.

## Ce qui est mesuré

1. Le nombre de cycles **rectifiés**, et le **taux** sur l'ensemble.
2. Le taux **par tranche chronologique** — la question « monte ou baisse ».
3. Les cycles **les plus rectifiés** (par plusieurs successeurs), nommés.
4. Le **délai médian** entre un cycle et sa première rectification.

## Critère de succès — chiffré, il porte sur le procédé

1. La **liste de marqueurs** et la **fenêtre** citées verbatim.
2. Population, nombre de rectifiés et **taux** publiés.
3. Taux **par tranche** publié, et la tendance **nommée**.
4. Cycles les plus rectifiés nommés, **délai médian** publié.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Le taux global est **≤ 20 %**.
2. Le taux sur les **30 derniers** cycles est **strictement supérieur** au
   taux global.
3. **≥ 10** cycles sont rectifiés.

Si la prédiction 2 est réfutée et que le taux récent est **inférieur**, alors
la vague de rectifications des #493-#511 est une **impression** que la mesure
dément — et il faudra l'écrire, parce que c'est mon propre récit du dépôt qui
serait en cause.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucune section.
- Il ne **juge pas** qu'une rectification soit un défaut : un dépôt qui se
  corrige vaut mieux qu'un dépôt qui ne se relit pas.
- Il ne **se compte pas lui-même** : sa propre section n'existera qu'après la
  mesure. **Auto-exclusion structurelle**, déclarée (règle du #447).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, **y compris s'il dément mon propre récit**.
2. Marqueurs, fenêtre et population **inchangés** après mesure.
3. La limite « franchise ou erreurs » **rappelée dans le rapport**, pas
   reléguée au pré-enregistrement.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

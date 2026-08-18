# Pré-enregistrement — un détecteur de rectification qui **survive au témoin négatif**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #512.

## Ce que le #512 a détruit

Le #512 comptait une rectification dès qu'un marqueur lexical (`faux`,
`corrig`, `tombe`…) tombait dans **±200 caractères** d'une référence `#NNN`.
Son audit a monté un **témoin négatif** — la même règle avec des mots
**neutres** — et le témoin a fait **mieux** : **89,3 %** contre **59,4 %**.

> **Le détecteur ne mesurait pas la rectification, mais la densité du texte.**
> La méthode lexicale est disqualifiée, et la question du #509 — *le taux de
> rectification monte-t-il ou baisse-t-il ?* — reste **sans réponse**.

## Le changement de méthode : **structure**, pas vocabulaire

Deux détecteurs, **figés ici**, qui exigent que le marqueur et la référence
soient dans une **même unité syntaxique** du markdown — et non dans un
voisinage de caractères :

- **S1 — titre de section** : une ligne commençant par `##` ou `###`, dans une
  section `#MMM`, contenant **à la fois** une référence `#NNN` (`NNN < MMM`)
  et un marqueur.
- **S2 — assertion en gras** : un **span `**…**`** contenant **à la fois** la
  référence `#NNN` et un marqueur, sur une même ligne.

**Liste de marqueurs — identique à celle du #512, sans un mot de plus ni de
moins**, pour que la comparaison porte sur la **structure** et sur rien
d'autre :

```
réfut   rétract   corrig   invalid   fauss   faux
erron   sur-affirm   surestim   sur-estim   dissou   tombe
```

## Le témoin négatif devient un **critère**, pas un audit

C'est la leçon institutionnalisée du #512. Chaque détecteur est rejoué avec
la liste **neutre** de l'audit du #512, reprise verbatim :

```
cycle  rapport  mesure  script  publie  critère
verdict  audit  population  chiffre  règle  dépôt
```

> **Un détecteur ne « passe » que s'il bat son propre témoin d'au moins
> 20 points.** Le seuil est fixé **ici**, avant toute mesure.

## Ce qui est mesuré

1. Pour **S1** et **S2** : le nombre de cycles rectifiés, le taux, et le taux
   du **témoin neutre** correspondant.
2. L'**écart** détecteur − témoin, pour chacun.
3. **Si au moins un détecteur passe** : le taux par tranche et la **tendance**
   — la réponse à la question du #509.
4. **Si aucun ne passe** : le constat que la question reste ouverte, et que
   **deux méthodes** auront échoué.

## Critère de succès — chiffré

1. Les **deux règles structurelles**, la liste de marqueurs et la liste neutre
   citées verbatim.
2. Les **quatre taux** (S1, S1-témoin, S2, S2-témoin) publiés.
3. Les **deux écarts** publiés, et le verdict « passe / ne passe pas » rendu
   pour chacun **au seuil de 20 points**.
4. Si un détecteur passe : **tendance nommée**. Sinon : **question déclarée
   ouverte**.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.
> **Le PASS ne dépend pas de la réussite d'un détecteur** — il dépend de la
> publication honnête de leur échec ou de leur succès. Le #512 a montré qu'un
> cycle peut cocher ses critères en produisant une mesure sans valeur ; ici,
> **la valeur de la mesure est elle-même un des chiffres publiés**.

## Prédictions — falsifiables

1. **S1** bat son témoin d'au moins **20 points**.
2. **S2** bat son témoin d'au moins **20 points**.
3. Le taux du meilleur détecteur est **inférieur** à **59,4 %**, le taux
   lexical du #512.

Si les prédictions 1 et 2 sont **toutes deux réfutées**, alors **deux familles
de méthodes** auront échoué au même test, et il faudra écrire que le registre
**ne permet pas** de mesurer son propre taux de rectification par appariement
automatique — ce qui serait un résultat, et non un échec de cycle.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucune section.
- Il ne **change pas** la liste de marqueurs : la comparaison avec le #512
  n'aurait aucun sens si les mots changeaient en même temps que la structure.
- Il ne **se compte pas lui-même** — auto-exclusion structurelle (règle #447).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, **y compris si les deux détecteurs échouent**.
2. Règles, marqueurs, liste neutre et seuil de 20 points **inchangés** après
   mesure.
3. Les **quatre** taux publiés, jamais les seuls favorables.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

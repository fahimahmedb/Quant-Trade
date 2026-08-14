# Pré-enregistrement — faut-il convertir la dernière variante du détecteur de verdict ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.
Cycle de **décision**, pas de modification par défaut : il peut se conclure par
*« on ne touche à rien »*, et ce serait un résultat.

## Ce qui reste, et pourquoi il a été laissé

Le #449 a converti six consommateurs à la règle du #448 et en a **laissé un** :
`nonml_sessions_column_backfill_audit.py`, dont la règle locale est

```python
def verdict_of(text):
    if "**PASS" in text:      # PAS de littéral "PASS (niveau 1)"
```

Le convertir **ajouterait** ce littéral : ce serait redéfinir sa sémantique, pas
corriger un défaut. Le #449 s'est abstenu et a inscrit la décision à ce cycle.

## Ce que cette fonction sert réellement — lu, pas supposé

Elle n'établit pas un classement absolu. Elle sert le **contrôle 3** de ce
script : comparer le verdict d'un rapport **avant** et **après** l'ajout d'une
colonne, pour prouver que l'ajout n'a pas changé de verdict.

C'est une **comparaison à règle constante**. Une règle grossière y est
largement inoffensive : elle ne trompe que si sa grossièreté crée une différence
entre avant et après là où il n'y en a pas, ou en masque une.

**Cette différence de nature justifie de décider séparément**, et non d'appliquer
mécaniquement la conversion faite ailleurs.

## Les deux écarts, à mesurer séparément

La règle du #448 diffère de celle-ci sur **deux** points, qu'il ne faut pas
confondre :

1. **porter ≠ mentionner** — le #448 lit le verdict en tête de ligne
   (décoration retirée), la règle locale n'importe où ;
2. **le littéral `"PASS (niveau 1)"`** — présent dans la règle partagée, absent
   ici.

## La règle de décision — fixée AVANT de mesurer

Univers : les **3 rapports cibles** du script — `halloween_effect`,
`intraday_range_regime_overlay`, `tom_overlay`.

> **Convertir si et seulement si** les deux règles donnent le **même verdict**
> sur **les trois**. La conversion serait alors sans effet observable ici, et
> l'uniformité du dépôt vaut mieux qu'une exception.
>
> **Ne pas convertir** si elles divergent sur au moins un : la conversion
> changerait ce que ce script mesure, et il faudrait d'abord savoir pourquoi.

Dans les deux cas, les verdicts sous chaque règle sont publiés.

## Critère de succès — chiffré

1. Les **3** rapports sont évalués sous **les deux** règles, et les résultats
   publiés.
2. La décision est **celle que dicte la règle ci-dessus**, sans appréciation
   après coup.
3. Si la décision est *convertir*, la conversion est faite et le diff confiné à
   la zone d'imports + la ligne de l'occurrence (régime du #449).
4. Le cycle dit explicitement si le **contrôle 3 est vide** en exécution
   ordinaire — il compare à un instantané passé en argument, absent par défaut.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédiction — falsifiable

- J'attends que les deux règles **coïncident** sur les trois : ce sont des
  rapports de stratégie, qui énoncent leur verdict en tête de ligne. La décision
  serait donc *convertir*.
- J'attends que le **contrôle 3 soit vide** en exécution ordinaire, faute
  d'instantané — auquel cas la question de la règle est, ici, largement
  théorique, et il faudra le dire plutôt que de faire semblant d'avoir tranché
  quelque chose d'important.

## Engagements

1. La décision suit la règle déclarée, **même si elle me déplaît**.
2. Les verdicts sous les deux règles sont publiés, coïncidents ou non.
3. Aucun autre script touché.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

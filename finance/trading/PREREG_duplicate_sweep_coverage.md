# Pré-enregistrement — inscrire sa propre couverture dans le rapport du balayage de doublons

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**outillage documentaire** : aucune stratégie évaluée, aucun verdict
recalculé, aucun seuil de détection touché.

## Ce qui manque, et pourquoi ça compte

Le rapport du balayage annonce aujourd'hui un total brut :

```
- fichiers `*_pnl.npz` trouvés : 218
- P&L reconstruits : 218
```

Ces deux lignes laissent croire que le balayage voit tout le dépôt. **Il n'en
voit qu'une partie, et il mélange deux familles.** Mesuré au #427 et
**re-mesuré à l'instant** pour écrire ce pré-enregistrement (règle du #425, que
le #426 m'a rappelée pour l'avoir enfreinte) :

| | Nombre |
|---|---|
| séries lues (`results/*_pnl.npz`) | **218** |
| dont candidats non-ML (`nonml_*`) | **208** |
| dont séries **ML / Étape D** | **10** |
| scripts de backtest non-ML du dépôt | **284** |
| **couverture non-ML** | **73,2 %** |

Un lecteur qui prend « 218 P&L reconstruits » pour le dépôt entier surestime la
portée du balayage de deux façons : il ignore que **10** séries ne sont pas des
candidats non-ML, et que **76** candidats non-ML n'ont aucun `.npz`.

Ce n'est pas une hypothèse de marché : c'est une **lacune de documentation** dans
un outil dont les trois autres cycles se servent pour compter les hypothèses.

## Le mélange des familles n'est pas anodin — constat déjà visible

Le balayage lit `results/*_pnl.npz` **sans filtre de préfixe**. L'un de ses trois
groupes de doublons exacts est justement inter-familles :

> `etape_D_overlay_optimized` (Étape D) et `nonml_etape_d_garch_defensive_overlay`
> (non-ML)

Publier la composition n'est donc pas cosmétique : elle explique pourquoi un
groupe de doublons peut associer une série qui n'appartient pas à l'univers
non-ML. Je le note comme **constat déjà présent dans le rapport**, pas comme une
découverte de ce cycle.

## Ce que ce cycle change — et ne change pas

**Change** : la section « Couverture » gagne la décomposition non-ML / ML et le
ratio de couverture, calculés par le script lui-même et non écrits en dur.

**Ne change pas** : les seuils de détection (égalité bit-à-bit, corrélation
≥ 0,9999), la liste des fichiers lus, les décomptes de doublons, les paires
listées, l'effet sur le décompte d'essais.

## Contrôle de non-régression — adapté, et je dis en quoi

Les quatre lots de persistance (#416, #423, #424, #426, #427) tenaient un régime
« **0 différence octet à octet** ». **Ce cycle en sort délibérément** : son objet
même est d'ajouter des lignes à un rapport publié. Le déclarer ici plutôt que de
laisser croire que le régime tient toujours.

Le contrôle devient donc :

> Le `diff` du rapport avant / après ne doit contenir **que des insertions**.
> **0 ligne supprimée, 0 ligne modifiée.** Toute suppression ou modification
> d'une ligne existante bloque la conclusion et devient le résultat du cycle.

C'est le même critère que celui appliqué aux 16 scripts du #427 (159 insertions,
0 suppression), transposé du code au rapport.

## Contrôle de cohérence — les chiffres ajoutés doivent se recouper

Deux vérifications, indépendantes du script modifié :

1. `non-ML + ML = total` — la décomposition doit sommer au nombre de séries lues.
2. Le nombre de candidats non-ML doit égaler le décompte direct de
   `results/nonml_*_pnl.npz` obtenu hors du script (par l'audit).

Écart toléré sur les deux : **0**.

## Critère de succès — chiffré

1. `diff` du rapport : **0 suppression, 0 modification**, insertions seulement.
2. Décomptes de doublons **inchangés** : 3 groupes exacts, 1 quasi-doublon,
   218 séries — les mêmes qu'au #427.
3. Contrôles de cohérence : **2/2** à écart nul.
4. La couverture figure dans le rapport du balayage, plus seulement dans l'audit
   d'un autre cycle.

## Prédiction — déductive

Ajouter des lignes calculées à partir des mêmes fichiers ne touche aucun critère
de détection.

> **Attente : 0 suppression, décomptes inchangés (218 / 3 / 1), cohérence 2/2.**

Les prédictions de cette série qui se sont vérifiées (#419, #422, #425, #426,
#427) étaient déductives comme celle-ci ; les deux démenties (#407, #408) étaient
des mécanismes économiques. Je maintiens la distinction plutôt que de compter
une série de succès qui ne dit rien de ma capacité à prévoir un marché.

## Engagements

1. Résultat rapporté tel quel, y compris si le `diff` révèle une modification
   inattendue.
2. Aucun seuil de détection touché ; aucun chiffre écrit en dur dans le rapport.
3. Aucun verdict PASS/FAIL modifié, aucun décompte d'hypothèses corrigé.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).

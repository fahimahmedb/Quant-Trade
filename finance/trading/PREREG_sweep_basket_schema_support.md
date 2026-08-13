# Pré-enregistrement — faire lire le schéma panier au balayage du #415

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**outillage** : aucune stratégie évaluée, aucun verdict recalculé.

## La limite est celle de l'outil, pas des données

Après les lots #416, #423 et #424, le balayage `capitulation_gate_floor_sweep`
mesure **55 candidats sur 62**. Sur les 7 restants, **3 possèdent un `.npz`** :
leur activation n'est pas mesurable parce que le volet B ne sait lire que le
schéma indiciel (`pos`), pas le schéma panier.

C'est une limite d'**outil**, corrigeable, et non un manque de données — le #424
l'avait notée comme telle.

## Comment l'activation se récupère sur un panier

Le schéma panier stocke `pnl_gross_ov` et `pnl_gross_bh` — les P&L **bruts** des
deux jambes, avant coûts. Or, dans tous les scripts de cette famille, la jambe
candidate vaut `exposure[t−1] × jambe de référence` : l'exposition est un
**scalaire par date** (identité établie et vérifiée au #402, contrôle 1b).

L'exposition se récupère donc par division :

```
exposure[t] = pnl_gross_ov[t] / pnl_gross_bh[t]   quand pnl_gross_bh[t] ≠ 0
```

Les séances où la référence est quasi nulle sont **exclues du calcul et
comptées**, pas remplacées par une valeur par défaut.

## Contrôle de validation — l'outil doit retrouver un chiffre déjà publié

C'est le cœur du cycle. Plusieurs rapports de candidats panier annoncent en toutes
lettres leur taux d'activation (« Overlay actif X % du temps »). La récupération
par division doit **retrouver ce chiffre**.

> **Tolérance fixée avant calcul : 1 point de pourcentage.**

Un écart supérieur signifierait que l'identité `ov = exposure × bh` ne tient pas
pour ce candidat, et invaliderait la méthode — ce serait alors le résultat
principal du cycle.

## Contrôle de non-régression

Les activations des **55** candidats déjà mesurés au schéma indiciel doivent
rester **identiques**. L'extension ne doit toucher que la branche panier.

## Critère de succès — chiffré

1. Les **3** candidats panier détectés sont mesurés, ou la raison de leur échec
   est publiée.
2. Écart maximal entre activation récupérée et activation publiée **≤ 1 point**
   pour tous les candidats dont le rapport annonce un taux.
3. **0 changement** sur les 55 activations déjà mesurées.
4. Couverture du volet B publiée, avant et après.

## Prédiction — déductive

L'identité `ov = exposure × bh` est établie au #402 et vérifiée par son contrôle
1b. La récupération devrait donc retrouver les taux publiés à la tolérance près.

> **Attente : écart maximal ≤ 1 point, 0 régression, couverture 55 → 58.**

Les deux prédictions de cette série qui se sont vérifiées (#419, #422) étaient
déductives comme celle-ci ; les deux démenties (#407, #408) étaient des
mécanismes économiques. Je note la distinction plutôt que de m'attribuer un
mérite qui n'existe pas.

## Engagements

1. Résultat rapporté tel quel, y compris si la validation échoue.
2. Aucune tolérance ajustée après lecture.
3. Le balayage garde ses seuils inchangés (2 % d'activation, repris du #410).
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).

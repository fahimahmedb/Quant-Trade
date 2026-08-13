# Pré-enregistrement — campagne v3, lot 2 : resserrer la borne de 12,2 %

**Écrit et committé AVANT tout tirage.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## Ce que ce lot vise

Le #438 a publié la première borne valide de la campagne : **p ≤ 12,2 %** sur
**23** tirages retenus (24 tirés, 1 divergence structurelle exclue du
dénominateur). Elle laisse encore place à **~35** divergences substantielles non
détectées sur ~290 rapports.

> **24 tirages de plus**, graine **20260818**, **disjoints** des 24 du #438.

La borne cumulée vaudra `1 − 0,05^(1/d)` où `d` est le nombre de tirages retenus
(identiques + substantiels), les structurels restant exclus. Si le lot donne
0 substantiel et 1 structurel, `d = 23 + 23 = 46` et la borne tombe à **≈ 6,3 %**.

Je publie la **formule** plutôt qu'une seule valeur, parce que `d` dépend du
nombre de structurels tirés, que je ne peux pas connaître d'avance.

## Une correction reportée — explicitement, cette fois

Le #438 s'est fait prendre à ne **pas avoir reporté** dans un nouveau script une
correction déjà faite au #434. Le #439 a découvert un défaut plus grave :

> `subprocess.run(timeout=…)` ne tue que l'**enfant direct**. Les candidats qui
> relancent eux-mêmes des backtests laissent des **petits-enfants orphelins** qui
> continuent d'écrire — au #439, l'un d'eux a **réécrit un rapport publié après
> sa restauration**.

Le script de campagne v3 utilise encore `subprocess.run`. **Je reporte donc la
correction du #439 avant de lancer ce lot** : exécution en **groupe de processus
isolé** (`start_new_session=True`), tué entier au délai via `os.killpg`.

C'est une modification du script de mesure, pas du protocole : elle **renforce**
la garantie « aucun rapport publié modifié » au lieu de l'assouplir, et elle est
déclarée ici avant tout tirage.

## Ce qui ne change pas

- **Classification par test sentinelle**, telle que fixée au #438 : rapport
  modifié par des fichiers neutres ⇒ **structurel** ; inchangé ⇒ **substantiel**.
- **Structurels exclus du dénominateur**, règle du #438 reprise sans retouche.
- **Régime** : sauvegarde, comparaison, **restauration à l'identique** ;
  `git status` vide de toute modification de `results/*_result.md` et de toute
  sentinelle en fin de cycle, sous peine d'échec déclaré.
- Délai **300 s** par exécution.

Les **6 rapports marqués au #439** restent dans le vivier : le marqueur documente
leur dérive, il ne les en soustrait pas. S'ils sont tirés, ils seront classés
structurels comme n'importe quel autre.

## Critère de succès — chiffré

1. **24** tirés, liste publiée **avant** les résultats individuels.
2. Chaque divergent **classé par le test sentinelle**, avec son `diff`.
3. `git status` vide de toute modification de rapport **et** de toute sentinelle.
4. Borne cumulée publiée **si et seulement si** 0 divergence substantielle ;
   sinon, les cas substantiels sont le résultat du cycle.

## Prédiction

**Aucune prédiction chiffrée** sur les 24 tirages, ni sur le nombre de
structurels.

Une attente **déductive** sur la correction reportée : elle ne peut pas changer
un verdict, seulement empêcher un orphelin de réécrire un rapport. Si un rapport
publié se retrouvait malgré tout modifié en fin de cycle, la correction serait
insuffisante et **ce serait le résultat principal**.

## Engagements

1. Résultat rapporté tel quel, y compris si une divergence substantielle annule
   de nouveau la borne.
2. Aucun script exclu du tirage après l'avoir vu.
3. Aucun rapport publié modifié ni committé ; aucune sentinelle laissée derrière.
4. La correction du #439 est reportée **avant** le tirage, pas après en avoir vu
   les effets.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).

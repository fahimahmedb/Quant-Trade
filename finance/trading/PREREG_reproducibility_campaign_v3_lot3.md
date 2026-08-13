# Pré-enregistrement — campagne v3, lot 3 : le dernier lot au bénéfice net

**Écrit et committé AVANT tout tirage.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## La décision, prise sur le chiffre publié au #440

Le #440 a porté la borne à **p ≤ 6,2 %** sur **47** tirages retenus, et a publié
le rendement décroissant pour que la suite ne se décide pas à l'impression :

| Dénominateur | Borne | Divergences substantielles encore possibles |
|---|---|---|
| 47 (actuel) | 6,2 % | ~17 |
| **71 (après ce lot)** | **~4,1 %** | **~11** |
| 100 | 3,0 % | ~8 |
| 150 | 2,0 % | ~5 |

Le gain visé — **~17 → ~11** — est réel et **modeste**. Le #440 l'a qualifié de
« dernier lot dont le bénéfice reste net ». J'exécute donc ce lot, et je déclare
d'avance ce qui suit :

> **Ce lot est le dernier de la campagne**, sauf si une divergence
> **substantielle** apparaît — auquel cas la campagne reprend pour l'instruire.

Sans cette clause, la boucle continuerait indéfiniment à acheter des dixièmes de
point. Je préfère fixer le terme **avant** de voir le résultat plutôt que de
décider après coup que « c'est assez ».

## Le lot

> **24** scripts tirés avec la graine **20260819**, **disjoints des 48** déjà
> tirés aux #438 et #440.

Délai **300 s** par exécution, en **groupe de processus isolé** (`os.killpg`) —
correction du #439, déjà reportée au #440 et conservée ici.

## Ce qui ne change pas

- **Classification par test sentinelle** (#438) : rapport modifié par des
  fichiers neutres ⇒ **structurel** ; inchangé ⇒ **substantiel**.
- **Structurels exclus du dénominateur**, règle du #438.
- **Régime** : sauvegarde, comparaison, **restauration à l'identique** ;
  `git status` vide de toute modification de rapport et de toute sentinelle en
  fin de cycle, sous peine d'échec déclaré.

## Critère de succès — chiffré

1. **24** tirés, disjoints des 48 précédents, liste publiée **avant** les
   résultats individuels.
2. Chaque divergent **classé par le test**, avec son `diff`.
3. `git status` vide de toute modification de rapport **et** de toute sentinelle.
4. Borne cumulée publiée **si et seulement si** 0 divergence substantielle ;
   sinon les cas substantiels sont le résultat du cycle.
5. **Clôture de la campagne prononcée** si 0 substantielle, avec son chiffre
   final.

## Prédiction

**Aucune prédiction chiffrée** sur les 24 tirages ni sur le nombre de
structurels.

Une remarque **déductive**, sans mérite : la borne finale sera d'autant meilleure
que peu de structurels seront tirés, puisqu'ils sortent du dénominateur. Ce n'est
pas une prévision sur le dépôt, c'est de l'arithmétique.

## Engagements

1. Résultat rapporté tel quel, y compris si une divergence substantielle annule
   la borne et rouvre la campagne que je viens de déclarer close.
2. Aucun script exclu du tirage après l'avoir vu.
3. Aucun rapport publié modifié ni committé ; aucune sentinelle laissée derrière.
4. La clôture annoncée ici n'est **pas** conditionnée au chiffre obtenu : elle
   vaut pour 4,1 % comme pour 4,5 %.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).

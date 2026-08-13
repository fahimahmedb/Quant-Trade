# Pré-enregistrement — campagne v3 : classer les divergences par un test, pas par une orthographe

**Écrit et committé AVANT tout tirage.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## Pourquoi une troisième tentative, et ce qui change

Deux campagnes ont échoué sur le même écueil :

- **#436** — divergence de `pnl_duplicate_sweep`, causée par un compteur du dépôt
  que j'avais moi-même ajouté au #428.
- **#437** — divergence de `empty_pass_requalification`, que mon critère
  d'exclusion n'avait pas capturée : il énumérait **trois écritures exactes**
  (`glob("*_pnl.npz")`…) alors que le script écrivait `glob("nonml_*_pnl.npz")`.

Le défaut de fond est identique dans les deux cas : **j'ai essayé de reconnaître
une propriété en devinant comment elle serait écrite.** Une troisième énumération
de motifs échouerait sur une quatrième orthographe.

> **Changement de méthode : la propriété est désormais *testée*, pas devinée.**

## Le critère — behavioral, et fixé avant tout tirage

Un rapport est **dépendant du dépôt** si son contenu change lorsqu'on ajoute au
dépôt un fichier neutre qui n'a aucun rapport avec la stratégie testée.

> **Test sentinelle.** On crée deux fichiers temporaires —
> `results/nonml__sentinelle_tmp_result.md` et
> `scripts/nonml__sentinelle_tmp_backtest.py` — on ré-exécute le script, on
> compare son rapport à celui obtenu sans sentinelle, puis **on supprime les
> sentinelles quoi qu'il arrive** (`try/finally`).
>
> - rapport **modifié** par la présence des sentinelles ⇒ divergence
>   **STRUCTURELLE** : le rapport compte le dépôt, il dérivera à chaque cycle ;
> - rapport **inchangé** ⇒ divergence **SUBSTANTIELLE** : un résultat publié ne
>   se reproduit plus, ce que la campagne cherche.

Ce test ne dépend d'aucune orthographe : il constate le comportement.

## Procédure — et pourquoi elle coûte peu

1. **24** scripts tirés avec la graine **20260817** dans le vivier **entier**
   (aucune exclusion syntaxique préalable : le critère v2 est abandonné, pas
   corrigé).
2. Chacun ré-exécuté une fois, rapport comparé au publié, puis **restauré**.
3. **Seuls les divergents** subissent le test sentinelle. Les identiques n'en ont
   pas besoin, ce qui rend la classification quasi gratuite.

Délai **300 s** par exécution. Régime inchangé : sauvegarde, comparaison,
**restauration à l'identique**, `git status` vide en fin de cycle.

## Ce que la borne mesurera — défini avant de voir les résultats

> La borne porte sur les divergences **substantielles uniquement**. Les
> divergences structurelles sont **comptées, listées et exclues du dénominateur**,
> puisqu'elles ne mesurent pas la péremption d'un résultat.

Si `k` divergences substantielles apparaissent sur `n` tirages classés, aucune
borne « zéro divergence » n'est publiée et le résultat du cycle devient ces `k`
cas.

Si `k = 0` sur `n` tirages, la borne est `p ≤ 1 − 0,05^(1/n)`, soit **11,7 %**
pour `n = 24`.

**Les 84 tirages des #434-#437 ne sont pas réutilisés** — troisième remise à zéro,
et je l'écris sans chercher à l'adoucir.

## Le risque de ce test, assumé

Créer un fichier dans `results/` est une manipulation du dépôt. Garde-fous fixés
d'avance :

1. noms **distinctifs** commençant par `nonml__sentinelle_tmp` ;
2. suppression dans un `finally`, exécutée même en cas d'exception ou de délai ;
3. **contrôle final** : `git status` doit être vide de tout fichier sentinelle.
   S'il en subsiste un, le cycle est déclaré **en échec** et le signale.

## Critère de succès — chiffré

1. **24** tirés, liste publiée **avant** les résultats individuels.
2. Chaque divergent **classé par le test sentinelle**, structurel ou substantiel,
   avec son `diff`.
3. `git status` vide de toute modification de `results/*_result.md` **et** de tout
   fichier sentinelle.
4. Borne publiée **si et seulement si** `k = 0` divergence substantielle.

## Prédiction

**Aucune prédiction chiffrée** sur les 24 tirages.

Une attente **déductive** sur le test lui-même : appliqué à
`pnl_duplicate_sweep` ou `empty_pass_requalification`, il doit les classer
**structurels** — c'est ce qu'ils sont, indépendamment de la façon dont leur
`glob` est écrit. Si le test échouait sur ces cas connus, il serait invalide et
ce serait le résultat du cycle.

## Engagements

1. Résultat rapporté tel quel, y compris si une troisième campagne ne publie
   encore aucune borne.
2. Le critère sentinelle n'est **pas** modifié après avoir vu son verdict sur un
   cas particulier.
3. Aucun rapport publié modifié ni committé ; aucune sentinelle laissée derrière.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).

# Audit — concordance `.npz` / rapport, schémas panier (#443)

Audit zéro-ML du cycle d'inventaire #443. Pré-enregistrement :
`PREREG_npz_report_consistency_baskets.md`, committé (`c84adb6`) **avant toute
mesure d'ensemble**. Anti-cheat : **CONFORME** (4/4).

## 1. Ce que le cycle a mesuré, et ce qu'il n'a pas mesuré

**Mesuré** : pour chaque `.npz` au schéma panier possédant un rapport publié, les
deux jambes sont reconstruites par la formule du #419
(`pnl_gross_* − turn_* × cost_bps/1e4`), converties par `log1p` — les P&L de
panier sont des rendements **simples** — et leur Sharpe annualisé est cherché
parmi les valeurs `+X.XX` du rapport.

**Non mesuré** : que la stratégie soit bonne, que le verdict soit juste, que le
`.npz` soit *complet*. Une série tronquée qui produirait par coïncidence le même
Sharpe à deux décimales passerait ce contrôle. C'est un test de **cohérence**,
pas de correction.

## 2. Le critère est plus strict qu'au #442, et il fallait le dire avant

Au #442, une seule valeur retrouvée suffisait. Ici, **les deux jambes** doivent
être retrouvées, sans quoi le candidat est classé *partiel*. Ce durcissement est
inscrit au pré-enregistrement (§ « Le contrôle — deux jambes »), **avant** la
mesure : ce n'est pas un critère choisi après avoir vu que 21/21 passaient.

Vérification : `git show c84adb6` précède `3687755` (le résultat).

## 3. Les 6 essais de faisabilité sont déclarés, pas dissimulés

Six paniers avaient été testés **avant** l'écriture du pré-enregistrement, pour
valider la méthode. Ils y figurent nommément (§ « Vérification de faisabilité »)
et sont recomptés dans le rapport : **21 examinés, dont 6 connus d'avance, 15
vérifications neuves**.

Les exclure aurait faussé le compte de couverture ; les taire aurait gonflé le
compte de vérifications. Les deux chiffres sont publiés séparément.

## 4. Le défaut trouvé n'a pas été trouvé par la mesure

**Encore une fois.** Le balayage a rendu 21/21 sans rien signaler. C'est en
**relisant** le chiffre du #442 — « 23 paniers écartés » — et en constatant que
ce cycle n'en trouvait que 21 que le défaut est apparu :

> Le lot de 23 du #442 était un **reste de soustraction**, pas une énumération.
> Il contenait 21 paniers réels et **2 fichiers d'un troisième schéma**
> (`pnl_candidate` / `pnl_ref`) jamais catalogué.

C'est exactement le défaut du #428 (`284 − 208 = 76`, soustraction entre
ensembles non alignés), reproduit quinze cycles plus tard. Le rapport du #443 le
dit dans son propre corps plutôt que de laisser l'étiquette fausse se propager.

## 5. Le sondage post-hoc, et pourquoi il ne compte pas

Ayant découvert ces 2 fichiers, j'ai sondé leur concordance — **hors périmètre
déclaré**, donc hors protocole. La reconstruction naïve
(`pnl_candidate − turn_candidate × coût`) donnait une jambe absente du rapport.

Le pré-enregistrement engageait à me méfier **d'abord de ma reconstruction avant
d'accuser un rapport** (§ Prédiction, § Engagement 2). Appliqué : lecture du
script d'origine, où `pnl_candidate=pnl_sleeve_net` est sauvegardé **déjà net**,
`turn_candidate` n'étant stocké que pour information. Je soustrayais les coûts
**deux fois**. Sans la seconde soustraction, les deux jambes se retrouvent.

Ce sondage est consigné mais **ne compte pas comme vérification** : il est
post-hoc, et un résultat obtenu après avoir vu le problème n'a pas la valeur d'un
résultat pré-enregistré. Les 2 fichiers sont **en file, pas couverts**.

**Ce que je n'ai pas fait** : élargir le périmètre du cycle pour les y inclure
une fois constaté qu'ils passaient. C'est le refus du #437, appliqué ici sans
qu'il faille le redécouvrir.

## 6. Bilan de fiabilité de mon propre outillage

Sur cet axe, **deux cycles, deux écarts, tous deux dans mon contrôle** :

| Cycle | Écart apparent | Cause réelle |
|---|---|---|
| #442 | 7 discordants | formule indicielle appliquée aux fichiers portant `r_alt` |
| #443 | 1 jambe absente (post-hoc) | coûts soustraits deux fois sur un P&L déjà net |

Le dépôt n'a, à ce jour, jamais été pris en défaut sur cet axe. **Mon
outillage, si — deux fois sur deux.** C'est le résultat le plus utile du cycle,
et il n'est pas dans le tableau de comptage.

## 7. Ce que le cycle ne permet pas de conclure

- **186/186 ne dit rien des 20 `.npz` sans rapport publié** ni des 2 du troisième
  schéma. Le taux porte sur le périmètre examiné, pas sur le dépôt.
- **Aucune stratégie n'est validée par ce cycle.** Un `.npz` concordant avec un
  rapport FAIL reste un FAIL.
- **100 % est une absence, pas un exploit.** Elle signifie seulement que les
  séries consommées par les balayages du #406, #415 et #422 correspondent aux
  stratégies décrites, sur ce périmètre.

## 8. Conformité au protocole

| Point | État |
|---|---|
| Pré-enregistrement committé avant mesure d'ensemble | ✔ (`c84adb6` < `3687755`) |
| `n_trials = 1` déclaré | ✔ |
| Aucun retuning après résultat | ✔ — le critère « deux jambes » est antérieur |
| Résultat publié tel quel, y compris 100 % | ✔ |
| Aucun rapport ni `.npz` publié modifié | ✔ — le cycle ne fait que lire |
| Essais de faisabilité déclarés et décomptés | ✔ (6 / 21) |
| Discordants inspectés avant qualification | ✔ — aucun ; le sondage post-hoc l'a été |
| Relecture intégrale avant commit (#414) | ✔ — a corrigé « troisième fois » en « deuxième fois sur deux » |
| Zéro ML | ✔ — aucune estimation, aucun paramètre ajusté |

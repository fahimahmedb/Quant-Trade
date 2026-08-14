# Pré-enregistrement — le DSR avec un décompte d'essais corrigé des doublons

**Écrit et committé AVANT toute mesure.** `n_trials = 1` *(pour ce cycle
lui-même ; tout le sujet est le `n_trials` des **autres**)*.

## La question, jamais posée en 450 cycles

Le **Deflated Sharpe Ratio** (Bailey & López de Prado 2014) déflate un Sharpe
par le nombre d'essais **N** : plus on a testé d'hypothèses, plus le meilleur
résultat est facile à obtenir par chance, et plus la barre monte.

Le projet compte ses essais **par entrées de backlog**. Or les #406, #445 et
#452 ont établi que cette unité est fausse :

- **3 groupes de doublons exacts** — des stratégies écrites deux fois, dont les
  P&L sont bit-à-bit identiques ;
- des **variantes par marché** portant chacune un nom (#453) ;
- des familles où l'union et une sous-fenêtre sont comptées séparément (#452).

> **Un essai devrait être une série de P&L distincte, pas une ligne de backlog.**

Toute la discipline anti-snooping du dépôt pointe vers cette question, et
**personne ne l'a posée**.

## Le sens de la correction — dit d'avance, parce qu'il est contre-intuitif

Dédupliquer **réduit** N. Réduire N **abaisse** le seuil `SR0`, donc **augmente**
le DSR. **La correction est donc favorable aux candidats.**

Ce n'est pas un durcissement déguisé, et il faut le dire avant de mesurer : si
des PASS survivent grâce à elle, ce sera parce que la barre a baissé, pas parce
qu'ils sont devenus meilleurs.

## L'univers et les grandeurs — figés ici

- **Univers d'essais** : toutes les séries `nonml_*_pnl.npz` reconstructibles par
  la fonction du balayage (règle du #445).
- **N_brut** : le nombre de ces séries, sans déduplication.
- **N_distinct** : le même après fusion des **groupes de doublons exacts** du
  balayage — un essai par série distincte.
- **var_trials** : variance des Sharpes **journaliers** de l'univers retenu,
  recalculée pour chaque N.
- **Candidats évalués** : ceux dont le rapport **porte un PASS** au sens de la
  règle unifiée (#448/#449/#454).
- **Seuil** : **DSR > 0,95**, la barre déjà employée par le projet (Étape B,
  `CLAUDE.md`).

`dsr(sr_hat_daily, T, var_trials, n_trials, skew, kurt_excess)` de
`prediction.py` est utilisée **telle quelle** — pas de réimplémentation.

## Critère de succès — chiffré

1. **Chaque PASS** de l'univers est évalué, ou **listé non évaluable avec sa
   raison**. Aucun écarté en silence.
2. **N_brut et N_distinct sont calculés**, non affirmés, et l'écart publié.
3. Le nombre de PASS franchissant **DSR > 0,95** est publié sous **les deux** N.
4. Aucun rapport de stratégie modifié, aucun verdict réécrit : ce cycle
   **mesure**, il ne requalifie pas.

> **PASS** = les quatre points. **FAIL** = un seul manque.

**Le verdict du cycle ne dépend pas du nombre de survivants.** Zéro survivant
est un résultat aussi publiable que dix.

## Prédiction — falsifiable, et probablement décevante

- **L'écart entre N_brut et N_distinct sera faible** : 3 groupes exacts sur ~200
  séries. La correction que la discipline du dépôt appelle depuis le début est
  sans doute **quantitativement négligeable**, et je m'attends à ce qu'**aucun
  verdict ne change**.
- J'attends **très peu, voire aucun** PASS au-dessus de 0,95 sous l'un ou
  l'autre N. `CLAUDE.md` rappelle qu'à l'Étape B **aucun signal actif** ne
  passait ce seuil, Buy & Hold compris à 0,567.
- Si beaucoup passaient, je devrais **d'abord douter de mon `var_trials`** avant
  de crier au succès — c'est le paramètre le plus facile à mal calculer, et il
  contrôle toute la sévérité du test.

## Ce que ce cycle ne fera pas

- Il ne **retire** aucun essai d'aucun décompte publié.
- Il ne **promeut** aucune stratégie, quel que soit son DSR : un DSR élevé sur
  un univers d'essais mal défini ne prouve rien.
- Il ne touche **pas** au seuil de 0,95.

## Engagements

1. Résultat rapporté tel quel, y compris **0 survivant** — surtout 0.
2. `var_trials` et N publiés, pas seulement les DSR qu'ils produisent.
3. Aucun retuning : ni le seuil, ni l'univers, ni la règle de déduplication ne
   changent après avoir vu les chiffres.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

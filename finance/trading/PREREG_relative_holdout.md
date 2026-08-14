# Pré-enregistrement — la piste C refaite : hors-échantillon **relatif au benchmark**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

## Pourquoi ce cycle existe

Le #458 a mesuré le Sharpe **absolu** des PASS sur les 252 dernières séances et
trouvé +1,34 médian contre +0,59 avant — trois prédictions réfutées, toutes dans
le sens flatteur.

Le diagnostic post-hoc a montré que **Buy & Hold faisait mieux (+1,39) sur la
même fenêtre** : la découpe mesurait le **régime de marché**, pas l'edge. Le
test était **confondu**, et il a été publié comme tel plutôt que remplacé —
changer la métrique après avoir vu le résultat aurait été un retuning.

**Ce cycle est la version correcte, déclarée d'avance.**

## La métrique — l'edge, pas la performance

Pour chaque candidat et chaque fenêtre :

```
edge = Sharpe(stratégie) − Sharpe(benchmark)     sur la MÊME fenêtre
```

Le benchmark est celui que porte le `.npz`, selon son schéma :

| Schéma | Benchmark |
|---|---|
| indiciel / deux jambes (`pos`, `r_asset`) | `r_asset` — acheter et conserver |
| panier (`pnl_gross_bh`, `turn_bh`) | la jambe de référence, nette de ses coûts |
| troisième schéma (`pnl_ref`) | `pnl_ref`, déjà net (#444) |

**Un edge n'est pas une performance.** Une stratégie qui gagne 30 % dans un
marché qui gagne 35 % n'a pas d'edge, et c'est exactement ce que le #458 n'a pas
su voir.

## Les découpes — identiques au #458, volontairement

**252** séances (principale) et **504** (secondaire), **les mêmes qu'au #458**.
Les changer permettrait d'attribuer un résultat différent à la fenêtre plutôt
qu'à la métrique. Seule la **métrique** change d'un cycle à l'autre.

Exclusion : moins de **756** séances, comme au #458. Les exclus sont listés.

## Ce qui est publié — les quatre chiffres, décidés ici

1. **edge médian avant** la fenêtre ;
2. **edge médian sur** la fenêtre ;
3. **fraction à edge positif** sur la fenêtre ;
4. **fraction dont l'edge se contracte** entre les deux.

Les **deux** découpes, pas seulement celle qui arrange.

## Critère de succès — chiffré, et il porte sur le procédé

1. **100 %** des PASS sont traités ou listés exclus **avec leur raison**.
2. Les **deux** découpes publiées.
3. Les **quatre** chiffres publiés pour chacune.
4. Aucun verdict de stratégie réécrit, aucun seuil introduit après coup.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédiction — falsifiable et chiffrée

Le #457 a donné **0/29** à la batterie renforcée, et le diagnostic du #458 a
montré que les stratégies **traînent derrière Buy & Hold** sur la fenêtre
récente. J'en tire :

- **edge médian sur la fenêtre ≤ 0** ;
- **fraction à edge positif < 50 %** ;
- **plus de la moitié voient leur edge se contracter**.

Si ces prédictions sont réfutées **dans le sens favorable**, je devrai — comme au
#458 — **douter d'abord de ma mesure** : un edge qui apparaît quand on change de
métrique mérite plus de méfiance qu'un edge qui disparaît.

**Je note que mes prédictions du #458 ont été réfutées à 3 sur 3.** Cela ne rend
pas celles-ci plus fiables ; cela rappelle seulement qu'elles engagent, et qu'un
score de 0/3 se publie.

## Ce que ce cycle ne fait pas

- Il ne **corrige** ni ne retire le rapport du #458 : le test confondu reste
  publié, avec son diagnostic.
- Il ne **promeut** aucune stratégie : un edge positif sur une fenêtre choisie
  après coup par l'histoire du dépôt reste contaminé par la **sélection**.
- Il n'introduit **aucun seuil** de succès pour les stratégies.

## Engagements

1. Résultat rapporté tel quel, y compris s'il contredit le #457 et le #458.
2. Découpes et métrique inchangées après mesure.
3. Les deux découpes publiées.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).

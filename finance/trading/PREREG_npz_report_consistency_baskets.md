# Pré-enregistrement — concordance `.npz` / rapport, extension aux schémas panier

**Écrit et committé AVANT toute mesure d'ensemble.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.

## Ce que le #442 a laissé de côté, chiffré

Le #442 a vérifié que le `.npz` produit bien les chiffres publiés : **165/165**
concordants. Mais **43** fichiers étaient écartés, dont **23 paniers**, faute de
position scalaire — la formule indicielle ne s'y applique pas.

Ces 23 ne sont pas un détail : ce sont les stratégies de **portefeuille**
(`amihud_illiquidity_tilt`, `leaders_*`, `january_effect_lowprice_*`, …), et
plusieurs portent un **PASS**. Si leur `.npz` ne correspondait pas à la stratégie
décrite, le balayage de doublons du #406 et la requalification du #422 seraient
alimentés par des séries fausses.

## Le contrôle — deux jambes, deux vérifications

Le schéma panier stocke les **deux** jambes. La reconstruction reprend la formule
du #419, déjà utilisée par le #422 :

```
pnl_ov = pnl_gross_ov − turn_ov × cost_bps/1e4      (jambe candidate)
pnl_bh = pnl_gross_bh − turn_bh × cost_bps/1e4      (jambe de référence)
```

**Détail qui compte** : les scripts de panier calculent leur Sharpe sur
`np.log1p(pnl)` — les P&L y sont des rendements **simples**, pas des log. La
reconstruction applique donc `log1p` avant `trading_metrics`, sans quoi le Sharpe
recalculé ne serait celui de personne. C'est exactement l'erreur de schéma qui a
produit 7 faux discordants au #442.

> **Concordant** : les Sharpes des **deux** jambes apparaissent parmi les valeurs
> `+X.XX` du rapport.
> **Partiellement concordant** : une seule des deux y figure.
> **Discordant** : aucune des deux.

Un candidat n'est déclaré concordant que si **les deux jambes** se retrouvent —
critère plus exigeant que celui du #442, où une seule valeur suffisait.

## Vérification de faisabilité déjà faite, et déclarée

Avant d'écrire ces lignes, j'ai testé la méthode sur **6** paniers : les deux
jambes concordaient dans **6 cas sur 6**. Ces six sont **connus d'avance** ; ils
restent dans le balayage — les exclure fausserait le compte — mais leur
concordance ne compte pas comme vérification neuve et sera signalée.

## Ce qui n'est pas couvert, et le restera

Les `.npz` **sans rapport publié** (20 au #442) ne sont pas traités ici : leur cas
relève d'une inspection nom par nom, inscrite séparément à la file. Ce cycle ne
prétend pas les couvrir.

## Critère de succès — chiffré

1. **100 %** des `.npz` au schéma panier possédant un rapport sont examinés, ou
   listés comme inexaminables avec leur raison.
2. Chaque candidat classé **concordant / partiel / discordant**, les deux
   dernières catégories **inspectées individuellement** avant qualification —
   discipline des contrôles B et E du #431, qui a déjà évité une fausse
   conclusion au #442.
3. Le taux est publié **tel quel**, y compris s'il est de 100 %.
4. **Aucun rapport ni `.npz` modifié.**

## Prédiction

**Aucune prédiction chiffrée.** Les 6 essais de faisabilité ne disent rien des 17
autres.

Une attente **déductive** en revanche, tirée du #442 : s'il y a des discordants,
la cause la plus probable est une **convention de calcul** différente dans le
script (log1p oublié, coût appliqué autrement) plutôt qu'une série fausse. Au
#442, les 7 discordants venaient tous de mon propre contrôle, pas du dépôt. Je
me méfierai donc d'abord de ma reconstruction avant d'accuser un rapport.

## Engagements

1. Résultat rapporté tel quel, y compris **0 discordant**.
2. Tout discordant est **inspecté** avant d'être qualifié ; aucune accusation
   portée sur la foi du seul compte mécanique.
3. Aucun rapport publié modifié ni committé.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).

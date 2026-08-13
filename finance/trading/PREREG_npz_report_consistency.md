# Pré-enregistrement — concordance entre le P&L sauvegardé et les chiffres publiés

**Écrit et committé AVANT toute mesure d'ensemble.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## L'angle que huit cycles de campagne n'ont pas couvert

La campagne #434-#441 a comparé **le rapport à son code** : le script, ré-exécuté,
reproduit-il son rapport ? Réponse : oui, sur 69 tirages retenus, borne 4,2 %.

Une question **différente** n'a jamais été posée :

> Le fichier `.npz` que le script a sauvegardé produit-il **les chiffres que le
> rapport annonce** ?

Ce n'est pas la même chose. Un script peut se reproduire parfaitement et
sauvegarder une série de P&L qui **ne correspond pas** à la stratégie décrite —
mauvaise branche de marché, décalage d'indice, série tronquée. Tous les balayages
qui consomment ces `.npz` (doublons #406, activation #415, batterie Règle 9)
seraient alors alimentés par des séries fausses **sans qu'aucun d'eux ne s'en
aperçoive**, puisqu'ils ne comparent jamais le `.npz` au texte du rapport.

C'est une dette **réelle, jamais mesurée, et distincte de tout ce qui précède**.

## Le contrôle — mécanique, défini avant toute mesure

Pour chaque `.npz` au schéma indiciel (`pos`, `r_asset`, `dates`, `cost_bps`)
possédant un rapport :

1. reconstruire le P&L net : `pnl = pos × r_asset − |Δpos| × cost_bps/1e4` ;
2. calculer le Sharpe annualisé avec `prediction.trading_metrics`, **la fonction
   du dépôt**, pas une réimplémentation ;
3. le comparer aux nombres publiés dans le rapport, au format `%+.2f` qu'ils
   utilisent tous.

> **Concordant** : le Sharpe recalculé apparaît parmi les valeurs `+X.XX` du
> rapport.
> **Discordant** : il n'y apparaît pas.

**Le compte de discordants ne se conclut pas mécaniquement.** Un rapport
multi-marchés publie une ligne par marché ; un rapport de panier peut n'afficher
aucun Sharpe indiciel. Chaque discordant sera donc **inspecté individuellement**
et qualifié **confirmé** ou **faux positif**, avec sa raison — la discipline des
contrôles B et E du #431.

## Vérification de faisabilité déjà faite, et déclarée

Avant d'écrire ces lignes, j'ai testé la méthode sur **5** `.npz` : le Sharpe
recalculé apparaissait dans le rapport dans **5 cas sur 5**. Ces cinq-là sont
donc **connus d'avance** ; ils restent dans le balayage — les exclure fausserait
le compte — mais leur concordance ne compte pas comme une vérification neuve, et
le rapport les signalera.

## Critère de succès — chiffré

1. **100 %** des `.npz` au schéma indiciel avec rapport sont examinés, ou listés
   comme inexaminables avec leur raison.
2. Chaque discordant est **inspecté** et qualifié (confirmé / faux positif).
3. Le taux de concordance est publié **tel quel**, y compris s'il est de 100 %.
4. **Aucun rapport ni `.npz` modifié** par ce cycle.

## Prédiction

**Aucune prédiction chiffrée** sur le taux. Les 5 essais de faisabilité ne disent
rien des ~200 autres, et prédire sans base m'a déjà trompé deux fois (#407, #408).

J'attends en revanche des **faux positifs** parmi les discordants, pour une
raison déductive : les rapports multi-marchés publient plusieurs lignes et le
`.npz` n'en sauvegarde qu'une (convention NDX du #416). Si un tel cas était
compté comme incohérence, ce serait mon contrôle qui aurait tort, pas le dépôt.

## Engagements

1. Résultat rapporté tel quel, y compris **0 discordant** — ce serait alors une
   absence confirmée, écrite sans être présentée comme un exploit.
2. Aucun discordant écarté sans raison publiée.
3. Aucun rapport publié modifié ni committé ; ce cycle ne fait que **lire**.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).

# Comparaison A vs B — Daily Breakout baseline vs Score multi-facteurs /10

Comparaison purement descriptive des deux résultats déjà figés
indépendamment (chacun avec son propre pré-enregistrement, backtest,
audit adversarial CONFORME et vérification anti-cheat CONFORME). Aucun
paramètre n'est ajusté à ce stade — les deux stratégies partagent le même
moteur d'exécution (SL=1,5×ATR14, TP=3×ATR14=2R fixe, risque 0,5 % de
l'equity composée par trade, coûts 5 bps/transition, capital initial
5 000 €, même marché : Composite pré-enregistré) : seule la génération
du signal d'entrée diffère, ce qui rend la comparaison directe.

| | Stratégie A (Daily Breakout) | Stratégie B (Score /10, seuil ≥7) | Buy & Hold |
|---|---|---|---|
| Séances testables | 1196 | 1045 | — |
| Sharpe annualisé | +0,55 | +0,49 | +0,54 (A) / +0,79 (B)* |
| Rendement total | +5,6% | +5,7% | +80,1% (A) / +108,5% (B)* |
| Max drawdown | — | -4,2% | — / -24,3% (B)* |
| Nombre de trades | 41 | 58 | — |
| Taux de réussite | 43,9% | 41,4% | — |
| R moyen / trade | +0,32R | +0,24R | — |
| Profit factor | 1,45 | 1,31 | — |
| Verdict | **FAIL** | **FAIL** | — |

*Le Buy & Hold de référence diffère légèrement entre A et B car les deux
stratégies démarrent leur échantillon testable à des dates différentes
(A : 56e séance, amorçage SMA50 ; B : 206e séance, amorçage SMA200 — le
facteur le plus lent de B). Chaque B&H est calculé sur exactement le même
sous-échantillon que sa stratégie correspondante, condition nécessaire
pour que le critère PASS/FAIL de chacune soit valide individuellement.

## Lecture

- **Les deux stratégies échouent** leur critère pré-enregistré (battre
  B&H simultanément en Sharpe ET en rendement, net de coûts).
- Sur Sharpe seul, A (+0,55) dépasse de peu son B&H (+0,54) tandis que B
  (+0,49) reste en dessous du sien (+0,79) — différence due en partie à
  la fenêtre de test plus courte et plus tardive de B (206e séance vs
  56e), qui exclut une partie de la hausse initiale captée par B&H sur A.
- Sur le rendement total, l'écart est massif et dans le même sens pour
  les deux : A capture +5,6% quand B&H capture +80,1% sur sa fenêtre ; B
  capture +5,7% quand B&H capture +108,5% sur la sienne. Rester
  majoritairement hors marché (35,6% du temps en position pour A, 60,7%
  pour B) coûte l'essentiel de la hausse haussière du Composite sur cette
  période — le facteur dominant de l'échec des deux stratégies n'est pas
  la qualité du signal d'entrée en soi, mais le temps passé hors marché
  combiné à un take-profit à 2R qui plafonne le gain par trade gagnant
  bien en-dessous de ce qu'un trend suivi jusqu'au bout aurait capté.
- Le score multi-facteurs (B), malgré 9 facteurs actifs au lieu des 3
  filtres de A, ne fait **pas mieux** que la baseline A sur aucune des
  deux métriques du critère — plus de facteurs ne s'est pas traduit ici
  par un edge supplémentaire sur ce dataset. Le max drawdown de B
  (-4,2%) est nettement plus faible que celui de B&H (-24,3%) sur sa
  fenêtre, ce qui est attendu (une stratégie hors marché 39% du temps
  réduit mécaniquement le drawdown) mais ne compense pas le déficit de
  rendement au regard du critère pré-enregistré.
- Ce résultat **prolonge et confirme** la conclusion déjà établie par ce
  repo à l'Étape B (ML) : aucun signal actif testé (ML ou règles) ne bat
  Buy & Hold sur le Composite pré-enregistré (5 ans). Ni la stratégie A
  ni la stratégie B n'y font exception — même conclusion, obtenue
  indépendamment, avec un moteur de trades discrets plutôt que les
  overlays continus utilisés jusqu'ici.

## Suite

Conformément à ce que l'utilisateur a indiqué vouloir faire, la
comparaison B vs C (moteur intraday 1H→15m→5m) est différée jusqu'au
chargement des données 5 minutes, non disponibles dans ce repo à ce
jour. Les architectures de gestion du risque non verrouillées (BE à 1R,
trailing à partir de 1,5R) restent non testées et non implémentées ici,
conformément à la réserve explicite de l'utilisateur sur leur statut.

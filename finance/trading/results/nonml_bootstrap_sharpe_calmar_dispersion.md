# Bootstrap Sharpe/Calmar — dispersion de l'estimateur pour le #121 (cycle #125)

Bootstrap stationnaire de Politis-Romano, B=2000, mean_block=20j (mêmes paramètres que `spa_test`, aucun retuning). 9522 séances (fenêtre du #121).

## Point estimé (déjà committé)

Sharpe overlay = +0.692, Calmar overlay = 0.162 ; Sharpe BH = +0.521, Calmar BH = 0.077.

## Intervalles de confiance bootstrap (95%)

| Quantité | IC 95% | Contient 0 (ou BH) ? |
|---|---|---|
| Sharpe overlay | [+0.373, +1.022] | -- |
| Calmar overlay | [0.088, 0.500] | -- |
| Sharpe overlay - Sharpe BH | [+0.008, +0.332] | NON (0 hors IC) |
| Calmar overlay - Calmar BH | [-0.042, +0.238] | OUI (0 dans l'IC) |

Fraction des répétitions bootstrap où l'overlay bat BH en Sharpe : 98.2%.
Fraction des répétitions bootstrap où l'overlay bat BH en Calmar : 90.4%.

## Lecture honnête

L'IC bootstrap de la DIFFÉRENCE de Sharpe exclut 0 -- en tension apparente avec le SPA (p=0,45, non significatif), possible car les deux tests utilisent des statistiques et des corrections différentes (SPA corrige pour un univers de comparaison, ce bootstrap ne teste qu'un intervalle de confiance simple sur CE seul candidat). Ne change PAS le verdict Règle 9 officiel (basé sur le SPA, pas ce bootstrap).

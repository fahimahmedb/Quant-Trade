# Pré-enregistrement — VaR/Expected Shortfall du #149 (risk management)

**Committé AVANT tout calcul.** Cycle #155 du backlog non-ML. Analyse
méthodologique sur un résultat DÉJÀ committé, PAS un nouveau backtest —
même démarche que le #135 (VaR/ES du #134), appliquée cette fois au
nouveau meilleur candidat du backlog (#149).

## Question posée (fixée ici, avant tout calcul)

Le #135 a documenté que le #134 réduisait le VaR/ES de +27% à +67%
selon la fenêtre. Le #149 (mécanisme plus agressivement défensif,
cible 15%, meilleur résultat brut du backlog) n'a pas encore reçu
cette caractérisation. Cette analyse répond à la question : le #149
réduit-il le risque de queue mesuré directement (pas seulement le
Sharpe/MDD déjà documentés), et de combien par rapport au #134 ?

## Méthode (fixée ici, identique au #135)

- Recalcul sur le pnl DÉJÀ committé du #149
  (`results/nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz`).
- VaR historique à 95% et 99% (quantile empirique des pertes
  quotidiennes) : Buy&Hold vs #149, sur l'échantillon complet ET sur
  les 4 fenêtres de crise déjà utilisées par la Règle 9b.
- Expected Shortfall (CVaR) à 95% et 99%.
- Comparaison directe aux chiffres déjà committés du #135 (#134) —
  aucun recalcul du #134, simple lecture croisée des résultats déjà
  publiés.
- Aucun paramètre à choisir après coup (95%/99% = seuils standards,
  identiques au #135).

## Ce que cette analyse NE fait PAS

Ne change AUCUN verdict Règle 9 déjà rendu (le #149 reste FAIL sous la
convention officielle SPA/DSR). N'introduit pas un nouveau critère de
succès PASS/FAIL.

## Anti-cheat

Analyse committée en un seul passage, sans itération sur le résultat.

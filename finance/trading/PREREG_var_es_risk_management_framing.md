# Pré-enregistrement — Le #134 comme outil de RISK MANAGEMENT (VaR/Expected Shortfall)

**Committé AVANT tout calcul.** Cycle #135 du backlog non-ML. Analyse
méthodologique sur un résultat DÉJÀ committé, PAS un nouveau backtest.

## Adaptation du sujet initial (documentée honnêtement)

La ligne #135 du backlog ciblait à l'origine le #131 (meilleur candidat
au moment où l'idée a été proposée, cycle #132). Le #134 (committé
depuis) l'a strictement dominé sur tous les axes pertinents à cette
analyse : meilleur Sharpe (+0,77 vs +0,72), meilleur MDD (-50,9% vs
-55,3%) et surtout meilleur score Règle 9 (4/5 vs 3/5, stabilité
temporelle 4/4 folds contre 3/4). Appliquer l'idée pré-enregistrée au
candidat désormais le plus abouti est plus informatif que de l'appliquer
à un candidat dépassé — décision prise AVANT tout calcul de cette
analyse, pas après avoir vu un résultat VaR/ES qui favoriserait l'un ou
l'autre.

## Question posée (fixée ici, avant tout calcul)

L'Étape C du projet conclut déjà que "le modèle de volatilité est utile
pour le risk management (position sizing, VaR), pas pour prédire une
direction". Le backlog non-ML a jusqu'ici évalué le #134 uniquement
avec des métriques de PERFORMANCE (Sharpe, rendement, Calmar, MDD) et
de SIGNIFICATIVITÉ (SPA, DSR) — jamais avec les métriques de risque
qu'un gérant utiliserait réellement pour dimensionner une position
(VaR, Expected Shortfall). Cette analyse répond à une question
DIFFÉRENTE de "bat-il le benchmark ?" (déjà tranchée, non) :
"réduit-il le risque de queue mesuré directement, et de combien ?"

## Méthode (fixée ici)

- Recalcul sur le pnl DÉJÀ committé du #134
  (`results/nonml_defensive_diversification_bond_overlay_pnl.npz`).
- VaR historique à 95% et 99% (quantile empirique des pertes
  quotidiennes, pas paramétrique) : Buy&Hold vs #134, sur l'échantillon
  complet ET sur les 4 fenêtres de crise déjà utilisées par la Règle 9b
  (dot-com, 2008, COVID, 2022).
- Expected Shortfall (CVaR) à 95% et 99% : moyenne des pertes AU-DELÀ du
  VaR — mesure la sévérité de la queue, pas seulement son seuil.
- Aucun paramètre à choisir après coup (95%/99% sont les seuils
  standards de la littérature risk management, pas sélectionnés après
  avoir vu un résultat).

## Ce que cette analyse NE fait PAS

Ne change AUCUN verdict Règle 9 déjà rendu (le #134 reste FAIL sous la
convention officielle SPA/DSR). N'introduit pas un nouveau critère de
succès "PASS/FAIL" — une caractérisation descriptive complémentaire,
cohérente avec la 2e voie de recommandation du #132 (formaliser comme
outil de gestion du risque plutôt que de chercher un edge de Sharpe).

## Anti-cheat

Analyse committée en un seul passage, sans itération sur le résultat
(seuils VaR/ES fixés avant tout calcul).

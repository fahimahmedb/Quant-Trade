# Résultat — Portefeuille long/short dollar-neutre composite (#4+#73+#82+#15), univers PIT (pré-enregistré)

Univers PIT : 174 tickers avec prix PIT disponibles. Couverture moyenne éligibles/membres : 87.5%. 139 dates de rebalancement, dont 139 avec ≥30 titres éligibles (portefeuille actif). 2907 séances testables (2015-01-02 → 2026-07-27). Poids continus dollar-neutre (z-score composite #4+#73+#82+(-#15) équipondéré, Σ|w|=2), rebalancement 21j, exécution causale. Coûts 5 bps sur turnover.

| | Sharpe ann. | Sharpe journalier | t-stat | Rendement total net | MDD |
|---|---|---|---|---|---|
| Buy&Hold équipondéré (univers PIT, contexte) | +0.39 | — | — | +98.9% | -36.4% |
| **Sleeve L/S dollar-neutre composite** | **+0.45** | +0.0281 | **+1.52** | +136.4% | -28.2% |

Corrélation quotidienne sleeve vs Buy&Hold PIT : -0.279 (proche de 0 attendu pour un portefeuille dollar-neutre).

1. Sharpe annualisé > 0 : OUI
2. t-stat > 2 : non

**FAIL — critère pré-enregistré (Sharpe>0 ET t-stat>2, réutilisé du #PEAD) NON atteint.**

**Limite non modélisée, rappelée ici** : aucun coût d'emprunt de titres ni contrainte de disponibilité/rappel de prêt sur la jambe courte (situation la plus favorable possible sur cet univers de méga-capitalisations liquides, mais pas nulle en réalité).

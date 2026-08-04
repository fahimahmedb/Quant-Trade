# Audit indépendant — effet pré-FOMC drift (cycle #171)

- **Composite (5 ans)** : recalcul indépendant (recherche linéaire) IDENTIQUE au masque du backtest (OK). Dates FOMC dans la plage de couverture : 39, jours marqués : 39 (OK, correspondance exacte).
- **NDX (40 ans)** : recalcul indépendant (recherche linéaire) IDENTIQUE au masque du backtest (OK). Dates FOMC dans la plage de couverture : 90, jours marqués : 90 (OK, correspondance exacte).
- **Russell 2000** : recalcul indépendant (recherche linéaire) IDENTIQUE au masque du backtest (OK). Dates FOMC dans la plage de couverture : 90, jours marqués : 90 (OK, correspondance exacte).
- **S&P 500** : recalcul indépendant (recherche linéaire) IDENTIQUE au masque du backtest (OK). Dates FOMC dans la plage de couverture : 90, jours marqués : 90 (OK, correspondance exacte).
- **DAX** : recalcul indépendant (recherche linéaire) IDENTIQUE au masque du backtest (OK). Dates FOMC dans la plage de couverture : 90, jours marqués : 90 (OK, correspondance exacte).

## Anti-lookahead

Le masque pré-FOMC ne dépend QUE des dates (fixes, sourcées avant tout calcul) et de l'index de dates du marché -- aucune dépendance aux prix ou rendements. Il est donc structurellement impossible qu'une perturbation des rendements futurs modifie une décision passée : la fonction `pre_fomc_mask` ne lit jamais la série de prix. Vérifié ici par un recalcul totalement indépendant (méthode différente) donnant un résultat identique.

**Verdict global : CONFORME**.

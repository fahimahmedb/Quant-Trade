# Audit indépendant — cycle #176 (mid-term election overlay)

- **NDX (40 ans)** : recalcul indépendant (boucle explicite, division/modulo manuels) IDENTIQUE au masque du backtest (OK). Années marquées : [1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026] (toutes vérifiées (année%4)==2).
- **Russell 2000** : recalcul indépendant (boucle explicite, division/modulo manuels) IDENTIQUE au masque du backtest (OK). Années marquées : [1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026] (toutes vérifiées (année%4)==2).
- **S&P 500** : recalcul indépendant (boucle explicite, division/modulo manuels) IDENTIQUE au masque du backtest (OK). Années marquées : [1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026] (toutes vérifiées (année%4)==2).
- **DAX** : recalcul indépendant (boucle explicite, division/modulo manuels) IDENTIQUE au masque du backtest (OK). Années marquées : [2002, 2006, 2010, 2014, 2018, 2022, 2026] (toutes vérifiées (année%4)==2).

## Anti-lookahead

Le masque mid-term ne dépend QUE de l'année calendaire de chaque date (fait public, connu des décennies à l'avance) -- aucune dépendance aux prix ou rendements. Il est donc structurellement impossible qu'une perturbation des rendements futurs modifie une décision passée. Vérifié par un recalcul totalement indépendant (méthode différente) donnant un résultat identique.

**Verdict global : CONFORME**.

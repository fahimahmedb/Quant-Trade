# Audit — Indice d'incertitude de politique économique US (FRED USEPUINDXD)

## 1. Recalcul indépendant (searchsorted explicite, side="right" inclusif + tercile tri+interpolation manuel)

### Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- **3/1250 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

### NDX (40 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

### Russell 2000
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- **2/9781 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

### S&P 500
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- **1/10460 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

### DAX
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- **1/6776 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

**OK — position confirmée par recalcul indépendant sur les 5 marchés.**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 6000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 8500 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**

## Verdict global : **CONFORME**

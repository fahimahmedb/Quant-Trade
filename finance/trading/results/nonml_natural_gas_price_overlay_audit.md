# Audit — Prix du gaz naturel US Henry Hub (DHHNGSP)

## 1. Recalcul indépendant (searchsorted explicite, side="right" inclusif + tercile tri+interpolation manuel)

### Composite (5 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

### NDX (40 ans)
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

### Russell 2000
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

### S&P 500
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00
- **OK**

### DAX
- Écart max alignement causal (pandas reindex/ffill/shift vs searchsorted manuel) : 0.00e+00
- **1/6776 désaccords de position** — sensibilité de bord flottante documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203) : confirmé.
- **OK**

**OK — position confirmée par recalcul indépendant sur les 5 marchés.**

## 2. Absence de valeur négative (contrairement à l'épisode WTI du 20/04/2020)

Nombre de valeurs négatives dans la série brute : 0 (confirmé absent, contrairement au pétrole WTI où un épisode négatif réel existe en 2020) — aucune gestion spéciale de NaN issue d'un log négatif requise pour cette série.
**OK**

## 3. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 6000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 8500 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**

## Verdict global : **CONFORME**

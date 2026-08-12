# Robustesse — cycle #193, grille jointe ±20% sur CUT et CORR_WINDOW

Point pré-enregistré : CUT=0.5x, CORR_WINDOW=60j. Grille CUT : {0.4x, 0.5x, 0.6x}. Grille CORR_WINDOW : {48j, 60j, 72j}.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré (0.5x / 60j) quelle que soit la lecture de ce tableau.

| Marché | CUT | CORR_WINDOW | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |
|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 0.4x | 48j | +0.33 | +38.2% | -36.4% | non | non | non |
| Composite (5 ans) | 0.5x | 48j | +0.37 | +44.3% | -36.2% | non | non | non |
| Composite (5 ans) | 0.6x | 48j | +0.40 | +50.6% | -36.1% | non | non | non |
| Composite (5 ans) | 0.4x | 60j | +0.37 | +42.4% | -32.3% | non | non | non |
| Composite (5 ans) (point pré-enregistré) | 0.5x | 60j | +0.40 | +48.0% | -32.8% | non | non | non |
| Composite (5 ans) | 0.6x | 60j | +0.43 | +53.7% | -33.5% | non | non | non |
| Composite (5 ans) | 0.4x | 72j | +0.44 | +51.2% | -29.2% | non | non | non |
| Composite (5 ans) | 0.5x | 72j | +0.46 | +55.5% | -29.9% | non | non | non |
| Composite (5 ans) | 0.6x | 72j | +0.47 | +60.0% | -30.8% | non | non | non |
| NDX (40 ans) | 0.4x | 48j | +0.30 | +431.5% | -65.1% | OUI | non | non |
| NDX (40 ans) | 0.5x | 48j | +0.31 | +472.8% | -69.0% | OUI | non | non |
| NDX (40 ans) | 0.6x | 48j | +0.31 | +517.3% | -72.5% | OUI | non | non |
| NDX (40 ans) | 0.4x | 60j | +0.35 | +577.2% | -63.1% | OUI | non | non |
| NDX (40 ans) (point pré-enregistré) | 0.5x | 60j | +0.34 | +604.2% | -67.6% | OUI | non | non |
| NDX (40 ans) | 0.6x | 60j | +0.33 | +632.3% | -71.5% | OUI | non | non |
| NDX (40 ans) | 0.4x | 72j | +0.34 | +562.3% | -59.6% | OUI | non | non |
| NDX (40 ans) | 0.5x | 72j | +0.34 | +574.4% | -64.8% | OUI | non | non |
| NDX (40 ans) | 0.6x | 72j | +0.33 | +586.8% | -69.5% | OUI | non | non |
| Russell 2000 | 0.4x | 48j | +0.27 | +277.7% | -41.3% | non | non | non |
| Russell 2000 | 0.5x | 48j | +0.28 | +307.9% | -44.9% | non | non | non |
| Russell 2000 | 0.6x | 48j | +0.28 | +340.5% | -48.3% | OUI | non | non |
| Russell 2000 | 0.4x | 60j | +0.31 | +352.3% | -43.8% | OUI | non | non |
| Russell 2000 (point pré-enregistré) | 0.5x | 60j | +0.31 | +372.2% | -46.9% | OUI | non | non |
| Russell 2000 | 0.6x | 60j | +0.30 | +392.9% | -49.8% | OUI | non | non |
| Russell 2000 | 0.4x | 72j | +0.32 | +382.1% | -37.7% | OUI | non | non |
| Russell 2000 | 0.5x | 72j | +0.31 | +392.3% | -42.1% | OUI | non | non |
| Russell 2000 | 0.6x | 72j | +0.30 | +402.7% | -46.2% | OUI | non | non |
| S&P 500 | 0.4x | 48j | +0.32 | +249.2% | -40.0% | OUI | non | non |
| S&P 500 | 0.5x | 48j | +0.33 | +273.4% | -43.0% | OUI | non | non |
| S&P 500 | 0.6x | 48j | +0.33 | +299.4% | -46.0% | OUI | non | non |
| S&P 500 | 0.4x | 60j | +0.39 | +346.1% | -42.3% | OUI | non | non |
| S&P 500 (point pré-enregistré) | 0.5x | 60j | +0.38 | +362.3% | -44.9% | OUI | non | non |
| S&P 500 | 0.6x | 60j | +0.37 | +379.1% | -47.4% | OUI | non | non |
| S&P 500 | 0.4x | 72j | +0.38 | +338.8% | -40.5% | OUI | non | non |
| S&P 500 | 0.5x | 72j | +0.38 | +353.7% | -43.5% | OUI | non | non |
| S&P 500 | 0.6x | 72j | +0.37 | +369.1% | -46.3% | OUI | non | non |
| DAX | 0.4x | 48j | +0.23 | +191.0% | -52.6% | OUI | non | non |
| DAX | 0.5x | 48j | +0.23 | +202.0% | -56.8% | OUI | non | non |
| DAX | 0.6x | 48j | +0.23 | +213.5% | -60.6% | OUI | non | non |
| DAX | 0.4x | 60j | +0.25 | +208.3% | -53.0% | OUI | non | non |
| DAX (point pré-enregistré) | 0.5x | 60j | +0.24 | +215.6% | -57.1% | OUI | non | non |
| DAX | 0.6x | 60j | +0.24 | +223.0% | -60.8% | OUI | non | non |
| DAX | 0.4x | 72j | +0.27 | +240.9% | -51.2% | OUI | OUI | OUI |
| DAX | 0.5x | 72j | +0.26 | +240.6% | -55.7% | OUI | OUI | OUI |
| DAX | 0.6x | 72j | +0.25 | +240.2% | -59.8% | OUI | OUI | OUI |

**3/45 cellules de la grille battent Buy&Hold sur les deux jambes (Sharpe ET rendement).**

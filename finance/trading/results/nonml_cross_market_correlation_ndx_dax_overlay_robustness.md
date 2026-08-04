# Robustesse — cycle #193, grille jointe ±20% sur CUT et CORR_WINDOW

Point pré-enregistré : CUT=0.5x, CORR_WINDOW=60j. Grille CUT : {0.4x, 0.5x, 0.6x}. Grille CORR_WINDOW : {48j, 60j, 72j}.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré (0.5x / 60j) quelle que soit la lecture de ce tableau.

| Marché | CUT | CORR_WINDOW | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |
|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 0.4x | 48j | +0.33 | +25.3% | -36.4% | non | non | non |
| Composite (5 ans) | 0.5x | 48j | +0.37 | +30.4% | -36.2% | non | non | non |
| Composite (5 ans) | 0.6x | 48j | +0.40 | +35.6% | -36.1% | non | non | non |
| Composite (5 ans) | 0.4x | 60j | +0.37 | +29.9% | -32.3% | non | non | non |
| Composite (5 ans) (point pré-enregistré) | 0.5x | 60j | +0.40 | +34.5% | -32.8% | non | non | non |
| Composite (5 ans) | 0.6x | 60j | +0.43 | +39.0% | -33.5% | non | non | non |
| Composite (5 ans) | 0.4x | 72j | +0.44 | +38.1% | -29.2% | non | non | non |
| Composite (5 ans) | 0.5x | 72j | +0.46 | +41.5% | -29.9% | non | non | non |
| Composite (5 ans) | 0.6x | 72j | +0.47 | +44.8% | -30.8% | non | non | non |
| NDX (40 ans) | 0.4x | 48j | +0.30 | +198.4% | -65.1% | OUI | non | non |
| NDX (40 ans) | 0.5x | 48j | +0.31 | +208.3% | -69.0% | OUI | non | non |
| NDX (40 ans) | 0.6x | 48j | +0.31 | +215.6% | -72.5% | OUI | OUI | OUI |
| NDX (40 ans) | 0.4x | 60j | +0.35 | +280.3% | -63.1% | OUI | OUI | OUI |
| NDX (40 ans) (point pré-enregistré) | 0.5x | 60j | +0.34 | +279.3% | -67.6% | OUI | OUI | OUI |
| NDX (40 ans) | 0.6x | 60j | +0.33 | +274.8% | -71.5% | OUI | OUI | OUI |
| NDX (40 ans) | 0.4x | 72j | +0.34 | +273.5% | -59.6% | OUI | OUI | OUI |
| NDX (40 ans) | 0.5x | 72j | +0.34 | +264.8% | -64.8% | OUI | OUI | OUI |
| NDX (40 ans) | 0.6x | 72j | +0.33 | +253.0% | -69.5% | OUI | OUI | OUI |
| Russell 2000 | 0.4x | 48j | +0.27 | +138.5% | -41.3% | non | non | non |
| Russell 2000 | 0.5x | 48j | +0.28 | +148.7% | -44.9% | non | non | non |
| Russell 2000 | 0.6x | 48j | +0.28 | +157.3% | -48.3% | OUI | non | non |
| Russell 2000 | 0.4x | 60j | +0.31 | +186.6% | -43.8% | OUI | OUI | OUI |
| Russell 2000 (point pré-enregistré) | 0.5x | 60j | +0.31 | +188.8% | -46.9% | OUI | OUI | OUI |
| Russell 2000 | 0.6x | 60j | +0.30 | +188.7% | -49.8% | OUI | OUI | OUI |
| Russell 2000 | 0.4x | 72j | +0.32 | +203.1% | -37.7% | OUI | OUI | OUI |
| Russell 2000 | 0.5x | 72j | +0.31 | +199.1% | -42.1% | OUI | OUI | OUI |
| Russell 2000 | 0.6x | 72j | +0.30 | +192.8% | -46.2% | OUI | OUI | OUI |
| S&P 500 | 0.4x | 48j | +0.32 | +163.6% | -40.0% | OUI | non | non |
| S&P 500 | 0.5x | 48j | +0.33 | +175.6% | -43.0% | OUI | non | non |
| S&P 500 | 0.6x | 48j | +0.33 | +186.7% | -46.0% | OUI | non | non |
| S&P 500 | 0.4x | 60j | +0.39 | +236.7% | -42.3% | OUI | non | non |
| S&P 500 (point pré-enregistré) | 0.5x | 60j | +0.38 | +241.1% | -44.9% | OUI | OUI | OUI |
| S&P 500 | 0.6x | 60j | +0.37 | +243.9% | -47.4% | OUI | OUI | OUI |
| S&P 500 | 0.4x | 72j | +0.38 | +230.5% | -40.5% | OUI | OUI | OUI |
| S&P 500 | 0.5x | 72j | +0.38 | +234.2% | -43.5% | OUI | OUI | OUI |
| S&P 500 | 0.6x | 72j | +0.37 | +236.3% | -46.3% | OUI | OUI | OUI |
| DAX | 0.4x | 48j | +0.23 | +95.8% | -52.6% | OUI | OUI | OUI |
| DAX | 0.5x | 48j | +0.23 | +97.3% | -56.8% | OUI | OUI | OUI |
| DAX | 0.6x | 48j | +0.23 | +97.5% | -60.6% | OUI | OUI | OUI |
| DAX | 0.4x | 60j | +0.25 | +108.9% | -53.0% | OUI | OUI | OUI |
| DAX (point pré-enregistré) | 0.5x | 60j | +0.24 | +107.5% | -57.1% | OUI | OUI | OUI |
| DAX | 0.6x | 60j | +0.24 | +104.8% | -60.8% | OUI | OUI | OUI |
| DAX | 0.4x | 72j | +0.27 | +131.0% | -51.2% | OUI | OUI | OUI |
| DAX | 0.5x | 72j | +0.26 | +124.0% | -55.7% | OUI | OUI | OUI |
| DAX | 0.6x | 72j | +0.25 | +115.8% | -59.8% | OUI | OUI | OUI |

**27/45 cellules de la grille battent Buy&Hold sur les deux jambes (Sharpe ET rendement).**

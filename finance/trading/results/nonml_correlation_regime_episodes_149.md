# Comportement de #149 pendant les 21 épisodes historiques de corrélation élevée

Spécification pré-enregistrée. Fenêtre de #149 : 1985-10-30 → 2026-07-13 (10252 séances).

| Épisode | Séances couvertes | Sharpe overlay | Sharpe BH | MDD overlay | MDD BH | MDD overlay pire que BH |
|---|---|---|---|---|---|---|
| 1985-12-30→1986-06-05 | 110 | +3.85 | +3.84 | -3.7% | -3.9% | non |
| 1986-09-11→1986-12-08 | 62 | +0.69 | +0.54 | -4.5% | -4.5% | non |
| 1986-12-16→1987-01-30 | 32 | +5.81 | +5.89 | -2.1% | -2.3% | non |
| 1987-04-08→1987-08-12 | 88 | +1.72 | +1.97 | -5.6% | -5.1% | non |
| 1987-08-31→1987-10-16 | 34 | -4.05 | -4.04 | -11.3% | -14.3% | non |
| 1988-02-23→1988-04-12 | 35 | +2.63 | +2.71 | -5.4% | -5.4% | non |
| 1988-04-14→1989-08-03 | 331 | +0.94 | +0.95 | -14.6% | -14.6% | non |
| 1990-05-01→1991-01-04 | 173 | +0.08 | -0.28 | -25.8% | -32.9% | non |
| 1991-02-14→1991-05-02 | 54 | +1.26 | +1.36 | -5.0% | -7.0% | non |
| 1991-06-05→1991-07-15 | 28 | -2.45 | -1.92 | -8.6% | -9.5% | non |
| 1993-07-01→1993-08-23 | 37 | +0.45 | +0.49 | -4.2% | -4.4% | non |
| 1994-02-23→1994-07-18 | 100 | -1.67 | -1.46 | -15.4% | -15.9% | non |
| 1994-08-11→1994-12-06 | 82 | +1.30 | +1.28 | -5.7% | -6.0% | non |
| 1996-08-01→1996-11-08 | 71 | +3.93 | +4.17 | -4.7% | -5.7% | non |
| 1997-08-22→1997-10-15 | 38 | +0.12 | +0.01 | -2.4% | -4.1% | non |
| 1999-08-11→1999-11-22 | 73 | +4.01 | +4.04 | -4.7% | -8.4% | non |
| 2021-03-03→2021-07-16 | 95 | +1.30 | +1.62 | -7.0% | -7.4% | non |
| 2022-10-04→2022-11-03 | 23 | -2.52 | -1.57 | -5.6% | -8.4% | non |
| 2022-11-10→2023-01-23 | 49 | +2.51 | +1.67 | -7.4% | -11.3% | non |
| 2023-11-02→2023-12-26 | 37 | +7.09 | +7.34 | -1.5% | -1.5% | non |
| 2026-05-04→2026-07-13 | 48 | +1.36 | +1.30 | -6.5% | -7.0% | non |

Épisodes couverts par la fenêtre de #149 : 21/21.
Épisodes où le MDD overlay est pire que BH : 0/21.
Sharpe overlay - Sharpe BH médian sur ces épisodes : -0.04.

**Le mécanisme reste défensif même pendant les épisodes de corrélation élevée (le portage protège indépendamment du timing de corrélation) : le kill-switch §3.2 est une précaution supplémentaire, pas une correction d'un comportement observé comme dangereux.**

Ne change aucun verdict Règle 9 déjà rendu sur #149 (reste 3/5, SPA et DSR à n_trials=125 toujours en échec).

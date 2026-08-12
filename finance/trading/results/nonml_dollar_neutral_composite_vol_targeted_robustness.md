# Robustesse — cycle #350 (sleeve vol-targeted), grille jointe ±20% sur TARGET_VOL_ANNUAL et CAP

Point pré-enregistré : TARGET_VOL_ANNUAL=15%, CAP=2.0x. Grille TARGET_VOL_ANNUAL : {12%, 15%, 18%}. Grille CAP : {1.6x, 2.0x, 2.4x}.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré (15% / 2.0x) quelle que soit la lecture de ce tableau.

| TARGET_VOL_ANNUAL | CAP | Sharpe ann. | t-stat | Rendement total | Sharpe>0 | t-stat>2 | Les deux |
|---|---|---|---|---|---|---|---|
| 12% | 1.6x | +0.36 | +1.22 | +73.4% | OUI | non | non |
| 12% | 2.0x | +0.37 | +1.24 | +75.0% | OUI | non | non |
| 12% | 2.4x | +0.37 | +1.24 | +75.0% | OUI | non | non |
| 15% | 1.6x | +0.34 | +1.15 | +89.5% | OUI | non | non |
| 15% (point pré-enregistré) | 2.0x | +0.36 | +1.22 | +98.9% | OUI | non | non |
| 15% | 2.4x | +0.37 | +1.24 | +101.3% | OUI | non | non |
| 18% | 1.6x | +0.32 | +1.08 | +102.7% | OUI | non | non |
| 18% | 2.0x | +0.34 | +1.16 | +118.5% | OUI | non | non |
| 18% | 2.4x | +0.36 | +1.22 | +128.2% | OUI | non | non |

**0/9 cellules de la grille passent le critère complet (Sharpe>0 ET t-stat>2).**

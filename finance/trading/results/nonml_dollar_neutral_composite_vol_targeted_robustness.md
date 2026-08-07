# Robustesse — cycle #350 (sleeve vol-targeted), grille jointe ±20% sur TARGET_VOL_ANNUAL et CAP

Point pré-enregistré : TARGET_VOL_ANNUAL=15%, CAP=2.0x. Grille TARGET_VOL_ANNUAL : {12%, 15%, 18%}. Grille CAP : {1.6x, 2.0x, 2.4x}.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré (15% / 2.0x) quelle que soit la lecture de ce tableau.

| TARGET_VOL_ANNUAL | CAP | Sharpe ann. | t-stat | Rendement total | Sharpe>0 | t-stat>2 | Les deux |
|---|---|---|---|---|---|---|---|
| 12% | 1.6x | +0.61 | +2.08 | +130.6% | OUI | OUI | OUI |
| 12% | 2.0x | +0.62 | +2.11 | +133.6% | OUI | OUI | OUI |
| 12% | 2.4x | +0.62 | +2.11 | +133.6% | OUI | OUI | OUI |
| 15% | 1.6x | +0.60 | +2.02 | +162.7% | OUI | OUI | OUI |
| 15% (point pré-enregistré) | 2.0x | +0.61 | +2.08 | +175.3% | OUI | OUI | OUI |
| 15% | 2.4x | +0.62 | +2.11 | +179.7% | OUI | OUI | OUI |
| 18% | 1.6x | +0.58 | +1.96 | +189.9% | OUI | non | non |
| 18% | 2.0x | +0.60 | +2.03 | +210.7% | OUI | OUI | OUI |
| 18% | 2.4x | +0.61 | +2.08 | +224.4% | OUI | OUI | OUI |

**8/9 cellules de la grille passent le critère complet (Sharpe>0 ET t-stat>2).**

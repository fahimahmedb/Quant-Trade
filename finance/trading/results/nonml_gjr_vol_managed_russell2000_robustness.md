# Robustesse — portefeuille volatility-managed GJR-t, Russell 2000 (cycle #166, perturbation ±20 %)

Point pré-enregistré : TARGET_VOL = 20 %, CAP = 2.0x (identique au #165, aucun retuning par marché). Grille : TARGET_VOL ∈ {16 %, 20 %, 24 %} × CAP ∈ {1.6x, 2.0x, 2.4x}.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré quelle que soit la lecture de ce tableau.

Référence Buy & Hold sur la même fenêtre OOS (9031 séances) : Sharpe +0.39, rendement +2014.8 %, MDD -59.9 %.

| TARGET_VOL | CAP | Expo. moy. | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH | Les deux |
|---|---|---|---|---|---|---|---|---|
| 16 % | 1.6x | 1.00x | +0.44 | +1161.0% | -41.6% | OUI | non | non |
| 16 % | 2.0x | 1.04x | +0.46 | +1415.2% | -41.2% | OUI | non | non |
| 16 % | 2.4x | 1.04x | +0.46 | +1441.7% | -41.2% | OUI | non | non |
| 20 % | 1.6x | 1.17x | +0.42 | +1839.5% | -49.8% | OUI | non | non |
| 20 % **(pré-enregistré)** | 2.0x | 1.25x | +0.44 | +2276.6% | -48.9% | OUI | OUI | OUI |
| 20 % | 2.4x | 1.29x | +0.46 | +2797.5% | -48.5% | OUI | OUI | OUI |
| 24 % | 1.6x | 1.31x | +0.43 | +2988.3% | -55.6% | OUI | OUI | OUI |
| 24 % | 2.0x | 1.43x | +0.42 | +3533.4% | -56.1% | OUI | OUI | OUI |
| 24 % | 2.4x | 1.50x | +0.44 | +4379.2% | -55.3% | OUI | OUI | OUI |

**5/9 combinaisons de la grille battent Buy & Hold sur les DEUX jambes.**

Lecture : un plateau (toutes ou presque toutes les cellules) indique un mécanisme peu sensible au calibrage ; quelques cellules isolées indiqueraient au contraire que le point pré-enregistré doit sa réussite à une coïncidence de paramétrage.

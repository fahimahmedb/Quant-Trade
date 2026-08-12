# Robustesse — portefeuille volatility-managed GJR-t, DAX (cycle #166, perturbation ±20 %)

Point pré-enregistré : TARGET_VOL = 20 %, CAP = 2.0x (identique au #165, aucun retuning par marché). Grille : TARGET_VOL ∈ {16 %, 20 %, 24 %} × CAP ∈ {1.6x, 2.0x, 2.4x}.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré quelle que soit la lecture de ce tableau.

Référence Buy & Hold sur la même fenêtre OOS (6026 séances) : Sharpe +0.43, rendement +779.1 %, MDD -54.8 %.

| TARGET_VOL | CAP | Expo. moy. | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH | Les deux |
|---|---|---|---|---|---|---|---|---|
| 16 % | 1.6x | 0.95x | +0.40 | +352.3% | -40.5% | non | non | non |
| 16 % | 2.0x | 0.95x | +0.40 | +352.3% | -40.5% | non | non | non |
| 16 % | 2.4x | 0.95x | +0.40 | +352.3% | -40.5% | non | non | non |
| 20 % | 1.6x | 1.15x | +0.41 | +555.2% | -47.2% | non | non | non |
| 20 % **(pré-enregistré)** | 2.0x | 1.18x | +0.40 | +559.7% | -47.7% | non | non | non |
| 20 % | 2.4x | 1.19x | +0.40 | +559.9% | -47.7% | non | non | non |
| 24 % | 1.6x | 1.30x | +0.42 | +833.1% | -52.9% | non | OUI | non |
| 24 % | 2.0x | 1.39x | +0.41 | +860.0% | -53.8% | non | OUI | non |
| 24 % | 2.4x | 1.42x | +0.40 | +862.1% | -54.1% | non | OUI | non |

**0/9 combinaisons de la grille battent Buy & Hold sur les DEUX jambes.**

Lecture : un plateau (toutes ou presque toutes les cellules) indique un mécanisme peu sensible au calibrage ; quelques cellules isolées indiqueraient au contraire que le point pré-enregistré doit sa réussite à une coïncidence de paramétrage.

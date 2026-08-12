# Robustesse — portefeuille volatility-managed GJR-t, S&P 500 (cycle #166, perturbation ±20 %)

Point pré-enregistré : TARGET_VOL = 20 %, CAP = 2.0x (identique au #165, aucun retuning par marché). Grille : TARGET_VOL ∈ {16 %, 20 %, 24 %} × CAP ∈ {1.6x, 2.0x, 2.4x}.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré quelle que soit la lecture de ce tableau.

Référence Buy & Hold sur la même fenêtre OOS (13501 séances) : Sharpe +0.44, rendement +6325.6 %, MDD -56.8 %.

| TARGET_VOL | CAP | Expo. moy. | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH | Les deux |
|---|---|---|---|---|---|---|---|---|
| 16 % | 1.6x | 1.17x | +0.49 | +6606.1% | -52.0% | OUI | OUI | OUI |
| 16 % | 2.0x | 1.20x | +0.49 | +6845.9% | -52.0% | OUI | OUI | OUI |
| 16 % | 2.4x | 1.21x | +0.49 | +6898.7% | -52.0% | OUI | OUI | OUI |
| 20 % | 1.6x | 1.35x | +0.51 | +17308.3% | -59.9% | OUI | OUI | OUI |
| 20 % **(pré-enregistré)** | 2.0x | 1.47x | +0.49 | +19088.3% | -60.0% | OUI | OUI | OUI |
| 20 % | 2.4x | 1.50x | +0.49 | +19782.5% | -60.0% | OUI | OUI | OUI |
| 24 % | 1.6x | 1.45x | +0.51 | +30922.5% | -65.1% | OUI | OUI | OUI |
| 24 % | 2.0x | 1.66x | +0.51 | +51375.1% | -66.7% | OUI | OUI | OUI |
| 24 % | 2.4x | 1.76x | +0.49 | +54803.6% | -66.7% | OUI | OUI | OUI |

**9/9 combinaisons de la grille battent Buy & Hold sur les DEUX jambes.**

Lecture : un plateau (toutes ou presque toutes les cellules) indique un mécanisme peu sensible au calibrage ; quelques cellules isolées indiqueraient au contraire que le point pré-enregistré doit sa réussite à une coïncidence de paramétrage.

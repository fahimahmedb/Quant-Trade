# Robustesse — portefeuille volatility-managed GJR-t (perturbation ±20 %)

Point pré-enregistré : TARGET_VOL = 20 %, CAP = 2.0x. Grille annoncée au §8 du PREREG avant tout calcul : TARGET_VOL ∈ {16 %, 20 %, 24 %} × CAP ∈ {1.6x, 2.0x, 2.4x}.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré quelle que soit la lecture de ce tableau.

Référence Buy & Hold sur la même fenêtre OOS (9522 séances) : Sharpe +0.52, rendement +4553.2 %, MDD -82.9 %.

| TARGET_VOL | CAP | Expo. moy. | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH | Les deux |
|---|---|---|---|---|---|---|---|---|
| 16 % | 1.6x | 0.83x | +0.67 | +3391.7% | -51.9% | OUI | non | non |
| 16 % | 2.0x | 0.83x | +0.66 | +3375.4% | -51.9% | OUI | non | non |
| 16 % | 2.4x | 0.83x | +0.66 | +3375.4% | -51.9% | OUI | non | non |
| 20 % | 1.6x | 1.03x | +0.67 | +7140.1% | -59.9% | OUI | OUI | OUI |
| 20 % **(pré-enregistré)** | 2.0x | 1.04x | +0.67 | +7178.8% | -59.9% | OUI | OUI | OUI |
| 20 % | 2.4x | 1.04x | +0.66 | +7135.1% | -59.9% | OUI | OUI | OUI |
| 24 % | 1.6x | 1.19x | +0.68 | +14683.8% | -66.6% | OUI | OUI | OUI |
| 24 % | 2.0x | 1.24x | +0.67 | +14061.3% | -66.6% | OUI | OUI | OUI |
| 24 % | 2.4x | 1.25x | +0.67 | +14165.9% | -66.6% | OUI | OUI | OUI |

**6/9 combinaisons de la grille battent Buy & Hold sur les DEUX jambes.**

Lecture : un plateau (toutes ou presque toutes les cellules) indique un mécanisme peu sensible au calibrage ; quelques cellules isolées indiqueraient au contraire que le point pré-enregistré doit sa réussite à une coïncidence de paramétrage. Cette grille ne modifie en aucun cas le verdict du cycle.

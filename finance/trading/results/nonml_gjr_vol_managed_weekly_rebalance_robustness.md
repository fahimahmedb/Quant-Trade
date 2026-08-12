# Robustesse — cycle #167, grille de fréquences de rebalancement

Point pré-enregistré : REBAL_FREQ = 5 jours. Grille annoncée au §5 du PREREG : {3, 5, 10, 21} jours.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré (5 jours) quelle que soit la lecture de ce tableau.

Référence Buy & Hold : Sharpe +0.52 / rendement +16660.8% (5 bps), Sharpe +0.52 / rendement +16660.8% (25 bps).

| Fréquence | Turnover réduit | Sharpe (5bps) | Rdt (5bps) | Sharpe (25bps) | Rdt (25bps) | 5bps OK | 25bps OK |
|---|---|---|---|---|---|---|---|
| 3j | 32.1% | +0.67 | +16659.6% | +0.60 | +9690.6% | non | non |
| 5j **(pré-enregistré)** | 46.1% | +0.70 | +21892.3% | +0.64 | +14251.0% | OUI | non |
| 10j | 61.6% | +0.70 | +24994.4% | +0.66 | +18417.1% | OUI | OUI |
| 21j | 75.3% | +0.65 | +21627.9% | +0.63 | +17768.4% | OUI | OUI |

**2/4 fréquences de la grille corrigent le stress de coûts à 25 bps.**

Lecture : un plateau indique que la correction n'est pas spécifique au choix 5j, mais générale à toute réduction significative de turnover.

# Robustesse — cycle #167, grille de fréquences de rebalancement

Point pré-enregistré : REBAL_FREQ = 5 jours. Grille annoncée au §5 du PREREG : {3, 5, 10, 21} jours.

**Perturbation, pas retuning** : le verdict du cycle reste celui du point pré-enregistré (5 jours) quelle que soit la lecture de ce tableau.

Référence Buy & Hold : Sharpe +0.52 / rendement +4555.6% (5 bps), Sharpe +0.52 / rendement +4555.6% (25 bps).

| Fréquence | Turnover réduit | Sharpe (5bps) | Rdt (5bps) | Sharpe (25bps) | Rdt (25bps) | 5bps OK | 25bps OK |
|---|---|---|---|---|---|---|---|
| 3j | 32.1% | +0.67 | +7612.8% | +0.60 | +4406.5% | OUI | non |
| 5j **(pré-enregistré)** | 46.1% | +0.70 | +9864.9% | +0.64 | +6402.7% | OUI | OUI |
| 10j | 61.6% | +0.70 | +10930.9% | +0.66 | +8040.0% | OUI | OUI |
| 21j | 75.3% | +0.65 | +8657.5% | +0.63 | +7101.3% | OUI | OUI |

**3/4 fréquences de la grille corrigent le stress de coûts à 25 bps.**

Lecture : un plateau indique que la correction n'est pas spécifique au choix 5j, mais générale à toute réduction significative de turnover.

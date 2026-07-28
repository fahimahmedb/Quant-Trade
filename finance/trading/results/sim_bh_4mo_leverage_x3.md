# Simulation — Buy & Hold NDX, levier max 3.0x, 4 derniers mois (300 EUR)

Fenetre : 2026-03-12 -> 2026-07-13 (84 seances, NDX). Levier CAP=3.0x = plafond deja utilise dans les analyses Kelly/diversification (pas un parametre nouveau choisi pour ce resultat). Cout 5 bps a l'entree, proportionnel au levier. **Pas de frais de financement du levier modelises (limite assumee).**

| | Capital final | Rendement periode | MDD % (periode) | Sharpe ann. |
|---|---|---|---|---|
| BuyHold (1.0x) | 351.26 EUR | +17.1% | -7.4 | +2.13 |
| **Leve x3.0** | **455.35 EUR** | **+51.8%** | -20.5 | +2.13 |

## Courbe de capital journaliere (levier x3)

| Date | Capital (EUR) |
|---|---|
| 2026-03-12 | 283.86 |
| 2026-03-18 | 279.61 |
| 2026-03-24 | 264.65 |
| 2026-03-30 | 230.28 |
| 2026-04-06 | 268.12 |
| 2026-04-10 | 298.93 |
| 2026-04-16 | 343.53 |
| 2026-04-22 | 366.95 |
| 2026-04-28 | 369.88 |
| 2026-05-04 | 395.66 |
| 2026-05-08 | 465.29 |
| 2026-05-14 | 481.44 |
| 2026-05-20 | 466.58 |
| 2026-05-27 | 498.91 |
| 2026-06-02 | 533.67 |
| 2026-06-08 | 465.04 |
| 2026-06-12 | 472.28 |
| 2026-06-18 | 505.71 |
| 2026-06-25 | 456.39 |
| 2026-07-01 | 471.37 |
| 2026-07-08 | 443.94 |
| 2026-07-13 | 455.35 |

**Lecture honnete** : resultat d'UNE seule fenetre historique recente (pas une moyenne sur plusieurs fenetres, pas une prevision). Le levier amplifie mecaniquement le rendement ET le risque dans les DEUX sens : le MDD de la periode passe de -7.4% (non leve) a -20.5% (x3.0). Une baisse de marche sur cette fenetre aurait produit une perte x3 amplifiee, pas un gain — le sens du resultat ci-dessus depend entierement de la direction prise par le marche sur CES 4 mois precis, pas d'une competence de timing.

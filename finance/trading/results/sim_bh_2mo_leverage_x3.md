# Simulation — Buy & Hold NDX, levier max 3.0x, 2 derniers mois (300 EUR)

Fenetre : 2026-05-12 -> 2026-07-13 (42 seances, NDX). Levier CAP=3.0x = plafond deja utilise dans les analyses Kelly/diversification (pas un parametre nouveau choisi pour ce resultat). Cout 5 bps a l'entree, proportionnel au levier. **Pas de frais de financement du levier modelises (limite assumee).**

| | Capital final | Rendement periode | MDD % (periode) | Sharpe ann. |
|---|---|---|---|---|
| BuyHold (1.0x) | 301.86 EUR | +0.6% | -7.0 | +0.14 |
| **Leve x3.0** | **305.62 EUR** | **+1.9%** | -19.6 | +0.14 |

## Courbe de capital journaliere (levier x3)

| Date | Capital (EUR) |
|---|---|
| 2026-05-12 | 291.78 |
| 2026-05-14 | 307.58 |
| 2026-05-18 | 289.66 |
| 2026-05-20 | 298.85 |
| 2026-05-22 | 304.51 |
| 2026-05-27 | 320.01 |
| 2026-05-29 | 331.67 |
| 2026-06-02 | 342.52 |
| 2026-06-04 | 334.12 |
| 2026-06-08 | 302.43 |
| 2026-06-10 | 275.33 |
| 2026-06-12 | 309.32 |
| 2026-06-16 | 319.83 |
| 2026-06-18 | 334.07 |
| 2026-06-23 | 300.37 |
| 2026-06-25 | 303.23 |
| 2026-06-29 | 313.68 |
| 2026-07-01 | 314.77 |
| 2026-07-06 | 311.26 |
| 2026-07-08 | 297.47 |
| 2026-07-10 | 315.28 |
| 2026-07-13 | 305.62 |

**Lecture honnete** : resultat d'UNE seule fenetre historique recente (pas une moyenne sur plusieurs fenetres, pas une prevision). Le levier amplifie mecaniquement le rendement ET le risque dans les DEUX sens : le MDD de la periode passe de -7.0% (non leve) a -19.6% (x3.0). Une baisse de marche sur cette fenetre aurait produit une perte x3 amplifiee, pas un gain — le sens du resultat ci-dessus depend entierement de la direction prise par le marche sur CES 2 mois precis, pas d'une competence de timing.

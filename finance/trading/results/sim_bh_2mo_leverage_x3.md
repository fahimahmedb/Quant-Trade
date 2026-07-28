# Simulation — Buy & Hold NDX, levier max 3.0x, 2 derniers mois (300 EUR)

Fenetre : 2026-05-12 -> 2026-07-13 (42 seances, NDX). Levier CAP=3.0x = plafond deja utilise dans les analyses Kelly/diversification (pas un parametre nouveau choisi pour ce resultat). Cout 5 bps a l'entree, proportionnel au levier. **Pas de frais de financement du levier modelises (limite assumee).**

| | Capital final | Rendement periode | MDD % (periode) | Sharpe ann. |
|---|---|---|---|---|
| BuyHold (1.0x) | 300.20 EUR | +0.1% | -7.0 | +0.14 |
| **Leve x3.0** | **290.59 EUR** | **-3.1%** | -19.6 | +0.14 |

## Courbe de capital journaliere (levier x3)

| Date | Capital (EUR) |
|---|---|
| 2026-05-12 | 291.66 |
| 2026-05-14 | 307.24 |
| 2026-05-18 | 288.99 |
| 2026-05-20 | 297.75 |
| 2026-05-22 | 303.37 |
| 2026-05-27 | 318.39 |
| 2026-05-29 | 329.86 |
| 2026-06-02 | 340.57 |
| 2026-06-04 | 332.16 |
| 2026-06-08 | 296.77 |
| 2026-06-10 | 269.51 |
| 2026-06-12 | 301.39 |
| 2026-06-16 | 309.91 |
| 2026-06-18 | 322.72 |
| 2026-06-23 | 288.60 |
| 2026-06-25 | 291.25 |
| 2026-06-29 | 300.48 |
| 2026-07-01 | 300.81 |
| 2026-07-06 | 296.89 |
| 2026-07-08 | 283.31 |
| 2026-07-10 | 299.91 |
| 2026-07-13 | 290.59 |

**Lecture honnete** : resultat d'UNE seule fenetre historique recente (pas une moyenne sur plusieurs fenetres, pas une prevision). Le levier amplifie mecaniquement le rendement ET le risque dans les DEUX sens : le MDD de la periode passe de -7.0% (non leve) a -19.6% (x3.0). Une baisse de marche sur cette fenetre aurait produit une perte x3 amplifiee, pas un gain — le sens du resultat ci-dessus depend entierement de la direction prise par le marche sur CES 2 mois precis, pas d'une competence de timing.

# Quantification — put-write / covered-call vs S&P 500 (données réelles CBOE via Yahoo)

Indices officiels CBOE (méthodologie publique) — produit déjà construit par le marché des options, pas une stratégie qu'on bâtit soi-même. Deux fenêtres rapportées : plein historique (30 ans) ET la crise 2007-2009 isolément — éviter de choisir la seule fenêtre favorable à un camp (le bull run 2011-2026 favorise mécaniquement le Buy&Hold pur face au covered-call).

## Plein historique (30 ans, inclut 2000-02 et 2008)

| Indice | Historique | CAGR | Vol ann. | Sharpe ann. | MDD |
|---|---|---|---|---|---|
| Covered-call (Buy-Write) (^BXM) | 1996-08-05 → 2026-07-17 (7535 obs) | +7.3% | 14.1% | +0.50 | -40.1% |
| Put-Write (^PUT) | 1996-08-05 → 2026-07-27 (7534 obs) | +8.5% | 15.3% | +0.53 | -37.1% |
| S&P 500 (référence) (^GSPC) | 1996-08-05 → 2026-07-27 (7541 obs) | +8.4% | 19.1% | +0.42 | -56.8% |

## Sous-période crise (2007-06 → 2009-12, GFC)

| Indice | Obs | CAGR (période) | Vol ann. | Sharpe ann. | MDD (période) |
|---|---|---|---|---|---|
| Covered-call (Buy-Write) (^BXM) | 653 | -3.2% | 23.4% | -0.14 | -40.1% |
| Put-Write (^PUT) | 652 | +0.4% | 22.7% | +0.02 | -37.1% |
| S&P 500 (référence) (^GSPC) | 653 | -11.6% | 31.9% | -0.39 | -56.8% |

**Lecture honnête** : le put-write/covered-call n'est pas de l'alpha au sens strict (pas un edge de prévision) — c'est une reconfiguration du profil de risque de la prime actions (moins de volatilité, moins de risque de queue à la hausse en échange d'un plafonnement des gains extrêmes). Comparable à Étape C par l'esprit (les deux monétisent la prime de risque de volatilité plutôt qu'un pari directionnel), mais Étape C n'a jamais été testé sur le marché des options lui-même — ce tableau donne juste la référence empirique de ce que le marché encaisse déjà pour ce type de risque, à comparer avec le funding rate arbitrage crypto (voir `funding_rate_arb_quantification.md`).

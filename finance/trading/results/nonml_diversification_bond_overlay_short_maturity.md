# Extension de robustesse — Diversification obligataire du #134, proxys COURTS (3 mois / 1 an)

PAS un nouveau candidat indépendant (pas de batterie Règle 9 séparée) -- extension de la grille de robustesse de maturité déjà prévue pour le #134, avec de VRAIES séries de taux courts (pas juste un paramètre de duration appliqué à DGS10).

| Proxy | Séances | Sharpe ann. | Rendement total | MDD | Calmar | vs Buy&Hold (Sharpe/rdt) | vs Buy&Hold (Calmar) |
|---|---|---|---|---|---|---|---|
| 3 mois (DGS3MO, duration~0.25an) | 10252 | +0.74 | +11140.6% | -55.9% | 199.357 | PASS | PASS |
| 1 an (DGS1, duration~1an) | 10252 | +0.74 | +11682.2% | -55.0% | 212.581 | PASS | PASS |
| Buy&Hold (référence, fenêtre 3 mois) | 10252 | +0.53 | +6416.7% | -82.9% | 77.406 | -- | -- |
| Buy&Hold (référence, fenêtre 1 an) | 10252 | +0.53 | +6416.7% | -82.9% | 77.406 | -- | -- |

Rappel #134 (proxy DGS10, 10 ans, fenêtre plus longue car série DGS10 débute avant DGS3MO) : Sharpe +0,53→+0,77, MDD -82,9%→-50,9%.

**Conclusion** : les proxys courts PASSENT aussi (au moins un critère) -- le mécanisme reste robuste même en réduisant fortement la duration/le risque de taux, contredisant partiellement l'intuition d'une protection qui viendrait uniquement de l'effet-prix des obligations longues.

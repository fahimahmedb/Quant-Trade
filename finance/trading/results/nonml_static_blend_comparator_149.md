# Comparateur blend statique vs #149 (Voie A, spécification pré-enregistrée)

Poids statique = exposition moyenne réelle de #149 sur la période : 0.7614
(10252 séances, coût 5.0 bps, rebalancement quotidien vers poids constant).

| Portefeuille | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold pur | +0.53 | +6416.7% | -82.9% | 0.077 |
| Blend statique (poids=0.761) | +0.60 | +5204.1% | -71.9% | 0.092 |
| #149 dynamique (vol-targeting + diversification) | +0.84 | +10425.6% | -37.9% | 0.264 |

Critère pré-enregistré : blend statique préféré si Sharpe(statique) >= Sharpe(#149) - 0.05.
Sharpe(statique) - Sharpe(#149) = -0.239

**Verdict : DYNAMIQUE CONSERVE UNE VALEUR SUFFISANTE (continuer le shadow-trading du dynamique)**

Ne change aucun verdict Règle 9 déjà rendu sur #149 (reste 3/5, SPA et DSR à n_trials=125 toujours en échec). Cette comparaison porte uniquement sur le choix opérationnel de déploiement (§2 du document de déploiement Voie A), pas sur la validité statistique du timing.

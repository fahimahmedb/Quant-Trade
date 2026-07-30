# Étape D v3 — Overlay défensif (vol-targeting réalisée) + diversification obligataire vs Buy & Hold

Formalise dans l'infrastructure officielle Étape D le mécanisme déjà validé dans le backlog non-ML (`PREREG_defensive_calmar_vol_targeting_overlay.md` = #115, `PREREG_defensive_diversification_bond_overlay.md` = #134, PASS niveau 1, meilleur score Règle 9 du backlog non-ML : 4/5 — coûts/crise/stabilité OK, SPA/DSR à n_trials=backlog encore en échec).

**Protocole figé** : `TARGET_VOL_ANNUAL=20%`, `VOL_WINDOW=20j`, `CAP=1.0×` (jamais de levier — mécanisme DÉFENSIF), proxy obligataire Trésor US 10 ans (DGS10, duration modifiée, formule fermée) ; coûts 5 bps aller-retour ; univers de 3 variantes (N=3 pour le DSR), figé avant évaluation.

## Composite (5 ans)

- Fenêtre : 11/08/2021 → 10/07/2026 (1230 obs, ~4.9 ans).
- Exposition équity : moy. 0.89×, min 0.33×, max 1.00× (cap 1.0×, jamais de levier).

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.72 | +0.26 | -36.4 | +12.5 | 1.09 | 0.851 |
| VolTarget-Défensif | +0.62 | +0.89 | +0.32 | -29.8 | +12.1 | 1.11 | 0.898 |
| VolTarget-Défensif+Diversification | +0.59 | +0.85 | +0.28 | -32.5 | +11.5 | 1.10 | 0.882 |

- **VolTarget-Défensif vs BuyHold** : réduction MDD relative = +18.2% (seuil >25%), rendement ann. conservé = 97.0% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**
- **VolTarget-Défensif+Diversification vs BuyHold** : réduction MDD relative = +10.6% (seuil >25%), rendement ann. conservé = 91.8% du BuyHold (seuil ≥80%) → **critère de succès NON atteint**

## NDX (40 ans)

- Fenêtre : 30/10/1985 → 13/07/2026 (10252 obs, ~40.7 ans).
- Exposition équity : moy. 0.87×, min 0.19×, max 1.00× (cap 1.0×, jamais de levier).

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.53 | +0.68 | +0.08 | -82.9 | +14.6 | 1.10 | 0.996 |
| VolTarget-Défensif | +0.71 | +0.99 | +0.15 | -58.5 | +13.6 | 1.13 | 1.000 |
| VolTarget-Défensif+Diversification | +0.77 | +1.08 | +0.19 | -50.9 | +14.8 | 1.14 | 1.000 |

- **VolTarget-Défensif vs BuyHold** : réduction MDD relative = +29.4% (seuil >25%), rendement ann. conservé = 93.4% du BuyHold (seuil ≥80%) → **critère de succès atteint**
- **VolTarget-Défensif+Diversification vs BuyHold** : réduction MDD relative = +38.6% (seuil >25%), rendement ann. conservé = 101.7% du BuyHold (seuil ≥80%) → **critère de succès atteint**

## Verdict — critère de succès explicite (identique à run_etape_d.py)

Succès = réduction du MDD >25% (relatif) **et** rendement annualisé conservé ≥80% de Buy & Hold. Vérifié, pas supposé :

| Jeu de données | Variante | ΔMDD relatif | Rdt ann. / BuyHold | Calmar (overlay vs BH) | Critère |
|---|---|---|---|---|---|
| Composite (5 ans) | VolTarget-Défensif | +18.2% | 97.0% | +0.32 vs +0.26 | NON |
| Composite (5 ans) | VolTarget-Défensif+Diversification | +10.6% | 91.8% | +0.28 vs +0.26 | NON |
| NDX (40 ans) | VolTarget-Défensif | +29.4% | 93.4% | +0.15 vs +0.08 | OUI |
| NDX (40 ans) | VolTarget-Défensif+Diversification | +38.6% | 101.7% | +0.19 vs +0.08 | OUI |

**Verdict honnête** : le critère de succès Étape D est atteint pour au moins une combinaison jeu de données/variante ci-dessus. Rappel important (cf. backlog non-ML, cycle #142) : la décomposition du gain de la diversification obligataire montre que 86-89% de l'amélioration vient du simple PORTAGE (taux positif au lieu de 0% cash pendant les phases dé-risquées), pas principalement d'un effet de couverture actions/obligations authentique ('flight to quality') — à documenter honnêtement si ce résultat est repris dans un rapport exécutif. Rappel Règle 9 (backlog non-ML) : ce mécanisme atteint 4/5 sur la batterie renforcée (coûts/crise/stabilité OK) mais échoue SPA et DSR à n_trials=backlog (~140) — PAS un PASS RENFORCÉ au sens strict de cette batterie plus sévère.
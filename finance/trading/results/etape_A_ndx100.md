# Étape A — Diagnostics préliminaires (NASDAQ Composite, quotidien)

## 1. Qualité des données

- Période : 01/10/1985 → 13/07/2026 — **10273 séances** (10272 rendements)
- Jours ouvrés manquants vs calendrier : 367 (attendu ≈ 367 fériés US sur la période)
- Dates dupliquées : 0 | lignes OHLC incohérentes : 0 | écart calendaire max : 7 j
- |rendement| max : 17.20 % | rendements >8 % abs. : 30
- Volume = 0 partout → colonne inutilisable, ignorée.

## 2. Statistiques descriptives des rendements log quotidiens

| Statistique | Valeur |
|---|---|
| n | 10272 |
| Moyenne quotidienne | 0.0543 % |
| Moyenne annualisée | 13.67 % |
| Volatilité annualisée | 25.87 % |
| Skewness | -0.157 |
| Kurtosis en excès | 7.750 |
| Min / Max | -16.35 % / 17.20 % |
| Jarque-Bera (p) | 25746.3 (0.00e+00) |

## 3. Ratio de variance Lo-MacKinlay (H₀ : random walk)

| q | VR(q) | z homoscéd. | p | z* robuste hétéro. | p |
|---|---|---|---|---|---|
| 2 | 0.9622 | -3.83 | 0.000 | -1.99 | 0.046 |
| 5 | 0.8891 | -5.13 | 0.000 | -2.68 | 0.007 |
| 10 | 0.8422 | -4.74 | 0.000 | -2.53 | 0.011 |

*Seule z\* (robuste) est interprétable en présence de clustering de volatilité (Lo-MacKinlay 1988). VR<1 = anti-persistance (renversement), VR>1 = momentum.*

## 4. Autocorrélations

| Lag | ACF rendements | ACF rendements² |
|---|---|---|
| 1 | -0.038 | +0.277 |
| 2 | -0.038 | +0.294 |
| 3 | -0.008 | +0.238 |
| 4 | +0.001 | +0.207 |
| 5 | -0.007 | +0.266 |
| 6 | -0.016 | +0.235 |
| 7 | +0.018 | +0.171 |
| 8 | -0.041 | +0.242 |
| 9 | +0.019 | +0.175 |
| 10 | -0.004 | +0.201 |

*Bande ±1.96/√n = ±0.019 (indicative ; non robuste à l'hétéroscédasticité pour les rendements bruts).*

### Ljung-Box

| Lags | Q rendements (p) | Q rendements² (p) |
|---|---|---|
| 5 | 30.3 (0.000) | 3420.6 (0.00e+00) |
| 10 | 56.8 (0.000) | 5625.7 (0.00e+00) |
| 22 | 124.1 (0.000) | 8452.5 (0.00e+00) |

## 5. Test ARCH-LM d'Engle (clustering de volatilité)

- LM(10) = 1910.6, p = 0.00e+00 → **effet ARCH massif confirmé**

## 6. Queues de distribution — Student-t non conditionnelle

- ν estimé (MV) : **2.84** | loc 0.1128 | scale 0.9980
- LR t vs normale : 2359.0 (χ²(1) ; >6.63 = rejet de la normale à 1 %)
- NB : ν non conditionnel < ν conditionnel (résidus GARCH), car le clustering de volatilité explique une partie des queues. Voir Étape C.

## 7. Volatilité réalisée range-based (Parkinson)

- Ratio E[ε²] / E[RV_Parkinson] = **1.549** → la variance intra-séance sous-estime la variance close-to-close (gap overnight non couvert). Toute utilisation de la RV Parkinson (HAR) est ré-échelonnée par ce ratio, estimé sur fenêtre d'entraînement uniquement.

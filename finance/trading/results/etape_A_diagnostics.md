# Étape A — Diagnostics préliminaires (NASDAQ Composite, quotidien)

## 1. Qualité des données

- Période : 13/07/2021 → 10/07/2026 — **1251 séances** (1250 rendements)
- Jours ouvrés manquants vs calendrier : 53 (attendu ≈ 45 fériés US sur la période)
- Dates dupliquées : 0 | lignes OHLC incohérentes : 0 | écart calendaire max : 5 j
- |rendement| max : 11.48 % | rendements >8 % abs. : 1
- Volume = 0 partout → colonne inutilisable, ignorée.

## 2. Statistiques descriptives des rendements log quotidiens

| Statistique | Valeur |
|---|---|
| n | 1250 |
| Moyenne quotidienne | 0.0466 % |
| Moyenne annualisée | 11.74 % |
| Volatilité annualisée | 22.64 % |
| Skewness | 0.057 |
| Kurtosis en excès | 4.574 |
| Min / Max | -6.15 % / 11.48 % |
| Jarque-Bera (p) | 1090.1 (1.90e-237) |

## 3. Ratio de variance Lo-MacKinlay (H₀ : random walk)

| q | VR(q) | z homoscéd. | p | z* robuste hétéro. | p |
|---|---|---|---|---|---|
| 2 | 0.9700 | -1.06 | 0.289 | -0.75 | 0.451 |
| 5 | 0.8945 | -1.70 | 0.089 | -1.26 | 0.209 |
| 10 | 0.8552 | -1.52 | 0.129 | -1.11 | 0.266 |

*Seule z\* (robuste) est interprétable en présence de clustering de volatilité (Lo-MacKinlay 1988). VR<1 = anti-persistance (renversement), VR>1 = momentum.*

## 4. Autocorrélations

| Lag | ACF rendements | ACF rendements² |
|---|---|---|
| 1 | -0.032 | +0.149 |
| 2 | +0.003 | +0.052 |
| 3 | -0.058 | +0.182 |
| 4 | -0.041 | +0.225 |
| 5 | +0.021 | +0.115 |
| 6 | -0.002 | +0.066 |
| 7 | +0.006 | +0.051 |
| 8 | -0.020 | +0.083 |
| 9 | +0.057 | +0.094 |
| 10 | -0.022 | +0.058 |

*Bande ±1.96/√n = ±0.055 (indicative ; non robuste à l'hétéroscédasticité pour les rendements bruts).*

### Ljung-Box

| Lags | Q rendements (p) | Q rendements² (p) |
|---|---|---|
| 5 | 8.1 (0.151) | 153.2 (2.79e-31) |
| 10 | 13.3 (0.205) | 186.0 (1.30e-34) |
| 22 | 37.0 (0.024) | 242.4 (4.73e-39) |

## 5. Test ARCH-LM d'Engle (clustering de volatilité)

- LM(10) = 112.9, p = 1.36e-19 → **effet ARCH massif confirmé**

## 6. Queues de distribution — Student-t non conditionnelle

- ν estimé (MV) : **4.78** | loc 0.0924 | scale 1.0938
- LR t vs normale : 116.2 (χ²(1) ; >6.63 = rejet de la normale à 1 %)
- NB : ν non conditionnel < ν conditionnel (résidus GARCH), car le clustering de volatilité explique une partie des queues. Voir Étape C.

## 7. Volatilité réalisée range-based (Parkinson)

- Ratio E[ε²] / E[RV_Parkinson] = **1.722** → la variance intra-séance sous-estime la variance close-to-close (gap overnight non couvert). Toute utilisation de la RV Parkinson (HAR) est ré-échelonnée par ce ratio, estimé sur fenêtre d'entraînement uniquement.

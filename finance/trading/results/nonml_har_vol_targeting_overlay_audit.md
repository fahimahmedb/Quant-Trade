# Audit adversarial — Overlay de vol-targeting estimateur HAR-P (Corsi 2009)

## 1. Recalcul totalement indépendant (équations normales explicites, sans `np.linalg.lstsq` ni `fit_har`/`har_forecast`)

| Marché | Écart position max (hors marge T0) |
|---|---|
| Composite (5 ans) | 3.77e-15 |
| NDX (40 ans) | 7.11e-15 |
| Russell 2000 | 6.55e-14 |
| S&P 500 | 1.24e-14 |
| DAX | 1.40e-14 |

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur, OHLC)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | (fenêtre trop courte pour tester) |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

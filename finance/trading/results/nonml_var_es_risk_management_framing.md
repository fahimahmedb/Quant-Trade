# Le #134 comme outil de RISK MANAGEMENT — VaR / Expected Shortfall (cycle #135, INFORMATIF)

PAS un nouveau backtest. Ne change AUCUN verdict Règle 9 déjà rendu (le #134 reste FAIL sous SPA/DSR) — caractérisation complémentaire du profil de risque, cohérent avec la conclusion de l'Étape C et la 2e voie de recommandation du #132.

## 1. VaR / ES sur l'échantillon complet

| Métrique | Buy&Hold (NDX 100%) | #134 (diversification obligataire) | Réduction |
|---|---|---|---|
| VaR 95% (perte quotidienne) | 2.58% | 1.87% | +27.7% |
| Expected Shortfall 95% | 3.92% | 2.58% | +34.1% |
| VaR 99% (perte quotidienne) | 4.54% | 2.87% | +36.9% |
| Expected Shortfall 99% | 6.26% | 3.82% | +39.0% |

## 2. VaR / ES sur les fenêtres de crise (mêmes fenêtres que la Règle 9b)

| Fenêtre | VaR99 BH | VaR99 #134 | ES99 BH | ES99 #134 | Réduction ES99 |
|---|---|---|---|---|---|
| Dot-com crash | 7.64% | 2.75% | 8.56% | 3.45% | +59.7% |
| Crise financière 2008 | 6.33% | 3.40% | 8.96% | 4.21% | +53.1% |
| Krach COVID | 11.01% | 4.17% | 13.00% | 4.23% | +67.4% |
| Resserrement 2022 | 4.95% | 3.44% | 5.36% | 3.93% | +26.7% |

## Conclusion

Le #134 réduit systématiquement le VaR ET l'Expected Shortfall par rapport à Buy&Hold, sur l'échantillon complet ET sur chacune des 4 fenêtres de crise historiques (cohérent avec le MDD déjà documenté à la Règle 9b). Cette caractérisation NE CHANGE PAS le verdict Règle 9 officiel (SPA/DSR restent en échec, le #134 ne bat pas le benchmark à un niveau de preuve statistique strict) — mais elle documente, avec des métriques qu'un gérant de risque utilise réellement, que le mécanisme réduit mesurablement le risque de queue, cohérence directe avec la conclusion déjà établie de l'Étape C ("le modèle de volatilité est utile pour le risk management, pas pour prédire une direction") et la 2e voie de recommandation du #132.

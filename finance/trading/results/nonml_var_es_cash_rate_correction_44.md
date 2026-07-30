# Le #149 comme outil de RISK MANAGEMENT — VaR / Expected Shortfall (cycle #155, INFORMATIF)

PAS un nouveau backtest. Ne change AUCUN verdict Règle 9 déjà rendu (le #149 reste FAIL sous SPA/DSR) — même démarche que le #135 (#134), appliquée au nouveau meilleur candidat.

## 1. VaR / ES sur l'échantillon complet

| Métrique | Buy&Hold (NDX 100%) | #149 (cible 15%+diversification) | Réduction |
|---|---|---|---|
| VaR 95% (perte quotidienne) | 2.58% | 1.57% | +39.0% |
| Expected Shortfall 95% | 3.92% | 2.17% | +44.6% |
| VaR 99% (perte quotidienne) | 4.54% | 2.45% | +46.0% |
| Expected Shortfall 99% | 6.26% | 3.25% | +48.1% |

## 2. VaR / ES sur les fenêtres de crise (mêmes fenêtres que la Règle 9b)

| Fenêtre | VaR99 BH | VaR99 #149 | ES99 BH | ES99 #149 | Réduction ES99 |
|---|---|---|---|---|---|
| Dot-com crash | 7.64% | 2.10% | 8.56% | 2.60% | +69.6% |
| Crise financière 2008 | 6.33% | 2.65% | 8.96% | 3.00% | +66.5% |
| Krach COVID | 11.01% | 3.16% | 13.00% | 3.24% | +75.1% |
| Resserrement 2022 | 4.95% | 2.73% | 5.36% | 3.19% | +40.5% |

## 3. Comparaison directe au #134 (#135, lecture croisée, aucun recalcul du #134)

Le #135 avait documenté pour le #134 : réduction de l'ES99 de **+39,0%** sur l'échantillon complet, et de **+26,7% à +67,4%** sur les 4 fenêtres de crise (meilleure réduction pendant le krach COVID, +67,4%). Comparaison directe avec les chiffres du #149 ci-dessus (§1-2).

## Conclusion

Le #149 réduit systématiquement le VaR ET l'Expected Shortfall par rapport à Buy&Hold, sur l'échantillon complet ET sur chacune des 4 fenêtres de crise historiques (cohérent avec le MDD -37,9% déjà documenté, le meilleur du backlog). Cette caractérisation NE CHANGE PAS le verdict Règle 9 officiel (SPA/DSR restent en échec) — mais elle confirme, avec des métriques de gestion du risque réelles, que le #149 est un outil de réduction de risque de queue au moins aussi solide que le #134, cohérent avec son MDD supérieur déjà documenté.

# Diagnostic — activation de la porte pente-des-taux pendant les crises (NDX vs S&P 500)

PAS un nouveau backtest -- recalcul sur les artefacts déjà committés des #114/#126.

## Dot-com crash (2000-01-01 → 2002-12-31)

| Marché | Séances | %activation porte | %activation (pire décile de rendement) |
|---|---|---|---|
| NDX (#114) | 752 | 0.0% | 0.0% |
| S&P 500 (#126) | 752 | 35.1% | 22.4% |

## Crise financière 2008 (2007-10-01 → 2009-03-31)

| Marché | Séances | %activation porte | %activation (pire décile de rendement) |
|---|---|---|---|
| NDX (#114) | 378 | 8.7% | 5.3% |
| S&P 500 (#126) | 378 | 29.4% | 15.8% |

## Interprétation

Si %activation (pire décile) est nettement PLUS ÉLEVÉ sur S&P 500 que sur NDX pendant ces deux fenêtres, cela confirme mécaniquement que le levier a été appliqué plus souvent précisément pendant les pires séances sur S&P 500 -- expliquant le MDD dégradé (#126) malgré un mécanisme et un signal identiques à ceux qui fonctionnent sur NDX (#114). Ceci documente une explication plausible, pas une preuve de causalité unique -- aucune correction n'est proposée ici (nécessiterait un nouveau pré-enregistrement séparé).

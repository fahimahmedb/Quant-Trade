# Audit adversarial — Stratégie nuit seulement

## 1. Recalcul indépendant de la décomposition (boucle explicite)

| Marché | Écart max r_nuit | Écart max r_jour | Écart identité r_nuit+r_jour-r_BH |
|---|---|---|---|
| Composite (5 ans) | 1.79e-15 | 1.70e-15 | 2.67e-16 |
| NDX (40 ans) | 1.77e-15 | 1.88e-15 | 3.13e-16 |
| Russell 2000 | 1.08e-15 | 1.36e-15 | 3.10e-16 |
| S&P 500 | 1.78e-15 | 1.81e-15 | 3.22e-16 |
| DAX | 1.85e-15 | 1.81e-15 | 3.06e-16 |

**OK — décomposition et identité comptable confirmées par recalcul indépendant.**

## 2. Rendement BRUT (sans coûts) de la stratégie nuit vs Buy&Hold brut

| Marché | Rdt brut nuit (somme r_nuit) | Rdt brut BH (somme r_BH) | Nuit bat BH en BRUT ? |
|---|---|---|---|
| Composite (5 ans) | +36.5% | +79.1% | non |
| NDX (40 ans) | +594.8% | +26222.0% | non |
| Russell 2000 | +108.5% | +1647.7% | non |
| S&P 500 | +112.9% | +7981.0% | non |
| DAX | +504.7% | +353.7% | OUI |

**Lecture** : même AVANT tout coût de transaction, le rendement brut de nuit ne dépasse Buy&Hold que sur certains marchés (voir tableau) -- l'anomalie overnight/intraday documentée dans la littérature US historique ne se traduit pas systématiquement en un edge de RENDEMENT TOTAL brut sur cet échantillon, même avant de considérer les coûts de friction qui, eux, sont de toute façon rédhibitoires (voir §3).

## 3. Sensibilité au coût de transaction (illustration, PAS un retuning du coût pré-enregistré)

| Marché | Coût/transaction pour lequel Nuit net ≈ 0% (2 transactions/jour) |
|---|---|
| Composite (5 ans) | 1.245 bps |
| NDX (40 ans) | 0.944 bps |
| Russell 2000 | 0.376 bps |
| S&P 500 | 0.265 bps |
| DAX | 1.328 bps |

**Lecture** : le coût pré-enregistré est de 5.0 bps/transaction -- très largement supérieur au seuil de rentabilité (souvent une fraction de bp) sur tous les marchés, confirmant que le FAIL n'est pas un artefact d'un coût mal calibré mais une conclusion structurelle robuste : la stratégie nuit seule ne peut être rentable qu'à des coûts de transaction quasi nuls, hors de portée d'un investisseur particulier.

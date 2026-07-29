# Audit adversarial — Overlay combiné tendance + vol-targeting

## 1. Recalcul totalement indépendant (boucle explicite jour par jour)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 7.99e-15 |
| NDX (40 ans) | 6.35e-14 |
| Russell 2000 | 3.33e-14 |
| S&P 500 | 1.04e-13 |
| DAX | 4.22e-14 |

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Note sur le bug initial** : la première version du backtest utilisait `trend[1:]` au lieu de `trend[:-1]` pour aligner le signal de tendance sur les rendements -- cela appliquait la tendance du jour i+1 (qui dépend de close[i+1], inconnu à la clôture du jour i) à la décision du jour i. Bug trouvé et corrigé AVANT toute exécution committée (aucun résultat basé sur la version buguée n'a été généré ni committé) ; ce audit confirme l'absence de fuite résiduelle par une seconde méthode de calcul indépendante.

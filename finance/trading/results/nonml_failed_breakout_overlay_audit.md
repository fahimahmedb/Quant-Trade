# Audit adversarial — Overlay défensif faux breakout Donchian

## 1. Recalcul indépendant (union d'intervalles vs compte à rebours à état)

| Marché | Écart position (nb j., hors 20 premiers) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — position confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture économique du FAIL** : le signal se déclenche ~35-37% du temps sur tous les marchés (fréquence homogène, cohérente avec un breakout Donchian 20j étant un événement fréquent -- cf. #40) mais la réduction défensive à 0.5x coupe l'exposition sur des phases qui restent en moyenne haussières (Buy&Hold reste positif sur le long terme sur les 5 marchés) : le coût d'opportunité du manque à gagner dépasse largement la protection de drawdown apportée (MDD quasi inchangé voire légèrement amélioré, jamais suffisant pour compenser le rendement total perdu). Seul le DAX, le marché le plus erratique/le moins tendanciel de l'échantillon, bénéficie marginalement de la réduction défensive.

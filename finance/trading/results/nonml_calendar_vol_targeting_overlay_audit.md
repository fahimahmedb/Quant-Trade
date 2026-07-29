# Audit adversarial — Overlay de vol-targeting gaté par le calendrier

## 1. Recalcul indépendant (boucle explicite, ddof=1, masque calendaire recalculé)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 6.22e-15 |
| NDX (40 ans) | 6.35e-14 |
| Russell 2000 | 3.33e-14 |
| S&P 500 | 1.04e-13 |
| DAX | 4.22e-14 |

**OK — position confirmée par recalcul indépendant.**

## 2. Test anti-lookahead sur la vol réalisée (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture** : confirme que le principe de gating hiérarchique (#47) se généralise à un signal calendaire (pas seulement un signal de tendance) -- 4/5 marchés PASS, MDD bien préservé sur 4/5 marchés (ex. NDX -82,9%→-82,9%, inchangé), Composite échoue uniquement sur le Sharpe (marge fine, cohérent avec l'échantillon le plus court du backlog).

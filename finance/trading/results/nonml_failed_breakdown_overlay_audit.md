# Audit adversarial — Overlay levé faux breakdown Donchian

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

**Lecture économique du FAIL** : le signal se déclenche 20-24% du temps sur tous les marchés (fréquence homogène), mais l'amplification qui en résulte coïncide systématiquement avec un MDD massivement dégradé (ex. NDX -82,9%→-94,2%) -- confirmant, comme au #22 (pullback rebound), qu'une récupération de court terme après une cassure de plus bas glissant est un marqueur de marché en stress PROLONGÉ (souvent le début ou une pause dans un krach) plutôt qu'un signal de capitulation fiable. Ni le miroir haussier (#62) ni le miroir baissier (#55) de ce pattern Donchian ne passent le critère renforcé -- les deux confirment que le backlog ne trouve aucun edge exploitable dans les signaux de prix à horizon court (2-20j), qu'ils soient utilisés en amplification ou en réduction.

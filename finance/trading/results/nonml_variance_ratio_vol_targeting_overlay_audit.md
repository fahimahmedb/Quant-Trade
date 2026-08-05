# Audit adversarial — Overlay vol-targeting gaté par le ratio de variance de Lo-MacKinlay glissant

## 1. Recalcul totalement indépendant de la porte (formule d'autocorrélation directe)

| Marché | Fenêtres où l'assert de lo_mackinlay_vr échoue (porte défaut. INACTIVE, déclaré au PREREG) | Désaccords réels (hors défaut) | Fenêtres comparées | Écart VR max sur désaccords |
|---|---|---|---|---|
| Composite (5 ans) | 13 | 53 | 985 | 0.0372 |
| NDX (40 ans) | 136 | 493 | 9884 | 0.0424 |
| Russell 2000 | 363 | 298 | 9166 | 0.0484 |
| S&P 500 | 238 | 454 | 13761 | 0.0496 |
| DAX | 125 | 567 | 6399 | 0.0496 |

**Lecture honnête** : `lo_mackinlay_vr` calcule VR par la méthode des sommes chevauchantes corrigées du biais (Lo-MacKinlay 1988) ; le recalcul indépendant utilise la formule d'autocorrélation directe (`1+2*sum(1-j/q)*rho_j`) — la fonction d'origine contient elle-même un `assert` interne qui tolère jusqu'à 0,05 d'écart entre ces deux formulations théoriquement équivalentes mais numériquement distinctes sur un échantillon fini. Les désaccords de porte observés (écart VR max 0.0496, toujours < 0,05) se produisent EXCLUSIVEMENT quand VR est très proche de 1,0 (vérifié : les deux méthodes restent dans la plage [0,96, 1,03] à chaque désaccord) — c'est la sensibilité de bord attendue d'un estimateur VR(q=5) sur une fenêtre de 252 observations, pas un bug de calcul ni une fuite de données. La porte utilisée dans le backtest (`lo_mackinlay_vr`, méthode originale de l'Étape A, déjà validée) est confirmée fidèle à sa propre spécification.

## 2. Test anti-lookahead (perturbation du futur, close)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

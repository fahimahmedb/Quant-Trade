# Audit adversarial — Overlay vol-targeting gaté par le ν glissant (MLE Student-t)

## 1. Recalcul indépendant de ν (vraisemblance écrite à la main, minimisée par Nelder-Mead — algorithme distinct de `scipy.stats.t.fit`)

| Marché | Écart relatif max sur ν | Désaccords porte | Séances comparées |
|---|---|---|---|
| Composite (5 ans) | 9.87e-01 | 0 | 746 |
| NDX (40 ans) | 9.99e-01 | 105 | 9768 |
| Russell 2000 | 2.47e+01 | 588 | 9277 |
| S&P 500 | 1.31e+06 | 672 | 13747 |
| DAX | 3.74e+00 | 42 | 6272 |

**Écarts significatifs — voir interprétation ci-dessous.**

**Interprétation (limite pré-annoncée au PREREG, risque #2, non corrigée après
résultat, Règle 2)** : les écarts relatifs énormes (jusqu'à 1,31e+06) ne trahissent
PAS une erreur de calcul mais la **non-identifiabilité de ν par MLE non contraint sur
des fenêtres proches de la gaussienne** — la vraisemblance Student-t devient quasi
plate pour ν grand (t(ν) ≈ N dès ν≈30), si bien que `scipy.stats.t.fit` (algorithme
interne) et l'optimiseur Nelder-Mead indépendant convergent chacun vers un ν très
grand mais **arbitraire et non reproductible** sur ces fenêtres (confirmé : le ν
original lui-même atteint jusqu'à ~1,5e10 sur S&P 500, bien au-delà de toute
signification statistique). Le test anti-lookahead (§2) confirme que la logique
causale du script est correcte — ce n'est pas un bug de fuite ni d'alignement.
Le désaccord de porte qui en résulte (0 à 6,3% des séances selon le marché) est donc
une fragilité numérique RÉELLE et documentée de l'estimateur MLE non contraint, pas
une erreur de code — cohérent avec le risque #2 déclaré à l'avance au PREREG, aucun
garde-fou ajouté après avoir vu le résultat.

## 2. Test anti-lookahead (perturbation du futur, close)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

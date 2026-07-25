# Étape C — Modèles de volatilité : estimation et évaluation walk-forward

## 1. Estimation in-sample (échantillon complet, 1250 obs)

| Modèle | ω | α | γ (levier) | β | ν | λ(skew) | persistance | demi-vie (j) | LogL | BIC |
|---|---|---|---|---|---|---|---|---|---|---|
| GARCH-n | 0.0477 | 0.0838 | nan | 0.8928 | nan | nan | 0.9766 | 29 | -2101.0 | 4230.5 |
| GARCH-t | 0.0383 | 0.0904 | nan | 0.8932 | 8.23 | nan | 0.9837 | 42 | -2083.9 | 4203.4 |
| GJR-t | 0.0386 | 0.0000 | 0.1362 | 0.9077 | 9.78 | nan | 0.9758 | 28 | -2064.1 | 4171.1 |
| GJR-skewt | 0.0380 | 0.0000 | 0.1386 | 0.9089 | nan | -0.169 | 0.9782 | 31 | -2055.5 | 4161.0 |

*GJR-t : t-stat de γ = 4.74 → effet de levier **significatif** ; α = 0.0000 (t=0.00) : les chocs positifs contribuent peu, l'essentiel passe par les chocs négatifs — fait stylisé indice actions.*

## 2. Validation d'implémentation

- Prévision 1 pas GJR-t : récursion maison 1.562595 vs `arch` 1.562595 (écart relatif 0.00e+00) → **OK**

## 3. Protocole out-of-sample (figé avant exécution)

- Fenêtre initiale : 750 obs (14/07/2021 → 10/07/2024), expansive, ré-estimation tous les 5 j (100 ré-estimations)
- OOS : 11/07/2024 → 10/07/2026 — **500 prévisions 1 pas**, 496 prévisions cumulées 5 pas (chevauchantes)
- ν (GJR-t) au fil des ré-estimations : min 9.4 / méd. 13.0 / max 151.2
- Univers de modèles : EWMA, GARCH-n, GARCH-t, GJR-t, GJR-skewt, HAR-P — benchmark : **GARCH-n**

## 4. Résultats out-of-sample

### Horizon 1 jour — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)

| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |
|---|---|---|---|---|---|---|
| EWMA | 1.7543 | +0.0459 | -2.07 | 0.981 | 0.5390 | 45.261 |
| GARCH-n (bench) | 1.7083 | — | — | — | 0.4883 | 45.353 |
| GARCH-t | 1.7122 | +0.0038 | -1.19 | 0.883 | 0.4918 | 45.194 |
| GJR-t | 1.6576 | -0.0507 | +2.19 | 0.014 | 0.4314 | 42.189 |
| GJR-skewt | 1.6614 | -0.0469 | +2.06 | 0.020 | 0.4351 | 42.329 |
| HAR-P | 1.7766 | +0.0683 | -0.74 | 0.770 | 0.5765 | 42.395 |

### Horizon 5 jours (cumulé, chevauchant) — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)

| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |
|---|---|---|---|---|---|---|
| EWMA | 0.5381 | +0.0494 | -1.93 | 0.973 | 0.4041 | 364.297 |
| GARCH-n (bench) | 0.4887 | — | — | — | 0.3465 | 365.541 |
| GARCH-t | 0.4936 | +0.0049 | -1.32 | 0.907 | 0.3515 | 362.539 |
| GJR-t | 0.4381 | -0.0506 | +1.87 | 0.031 | 0.2939 | 289.519 |
| GJR-skewt | 0.4416 | -0.0471 | +1.76 | 0.039 | 0.2973 | 291.983 |
| HAR-P | 0.4944 | +0.0057 | -0.11 | 0.545 | 0.3427 | 320.205 |

*Vol. annualisée prédite (GJR-t) sur l'OOS : min 11.5 % / méd. 19.5 % / max 50.3 %.*

## 5. Test SPA de Hansen (2005) — correction du data-snooping

H₀ : le benchmark GARCH(1,1)-n n'est battu par AUCUN des 5 modèles de l'univers (bootstrap stationnaire Politis-Romano, bloc moyen 20 j, 5000 réplications, recentrage consistant).

- **Horizon 1 jour** : t_SPA = 1.67, **p = 0.1100** (meilleur modèle : GJR-t) → H₀ non rejetée : la surperformance PEUT être un artefact de sélection.
- **Horizon 5 jours** : t_SPA = 1.53, **p = 0.1502** (meilleur modèle : GJR-t) → H₀ non rejetée : la surperformance PEUT être un artefact de sélection.

## 6. Verdict contre les seuils du cahier des charges

- Meilleur modèle 1 pas (QLIKE ε²) : **GJR-t** (1.6576 vs 1.7083 bench)
  - EWMA : ne bat pas le bench (p=0.981)
  - GARCH-t : ne bat pas le bench (p=0.883)
  - GJR-t : bat le bench, significatif à 10 % (p=0.014)
  - GJR-skewt : bat le bench, significatif à 10 % (p=0.020)
  - HAR-P : ne bat pas le bench (p=0.770)

### Lecture honnête des deux niveaux d'inférence

1. **Hypothèse primaire pré-enregistrée** (GJR-t vs GARCH-n, choisie AVANT de voir les données sur la base de Hansen-Lunde 2005 / Liu-Hung 2010) : DM unilatéral p=0.014 (h=1) et p=0.031 (h=5), cohérente sur les deux horizons → **validée**.
2. **Correction famille entière** (SPA sur les 5 modèles) : p=0.1100 (h=1) et p=0.1502 (h=5) → la significativité **ne survit PAS** à la correction au seuil de 10 %. Avec 500 obs OOS (~2 ans), la puissance est limitée : c'est une limite de l'ÉCHANTILLON, pas un feu vert pour élargir l'univers de modèles jusqu'à ce que ça passe.

**Conclusion opérationnelle** : GJR-GARCH(1,1)-t est adopté comme moteur de volatilité v1 (direction conforme à la littérature, gain régulier, benchmark battu partout où il doit l'être). Le renforcement statistique passe par PLUS DE DONNÉES (historique ≥ 2000, incluant 2008 et la bulle dot-com), pas par plus d'itérations de modèles sur ce même échantillon.
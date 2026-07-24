# Étape C — Modèles de volatilité : estimation et évaluation walk-forward

## 1. Estimation in-sample (échantillon complet, 10272 obs)

| Modèle | ω | α | γ (levier) | β | ν | λ(skew) | persistance | demi-vie (j) | LogL | BIC |
|---|---|---|---|---|---|---|---|---|---|---|
| GARCH-n | 0.0336 | 0.1006 | nan | 0.8860 | nan | nan | 0.9866 | 51 | -17366.4 | 34769.7 |
| GARCH-t | 0.0202 | 0.0958 | nan | 0.8997 | 7.24 | nan | 0.9955 | 155 | -17182.9 | 34411.9 |
| GJR-t | 0.0256 | 0.0359 | 0.1130 | 0.8962 | 7.71 | nan | 0.9886 | 60 | -17120.8 | 34297.0 |
| GJR-skewt | 0.0265 | 0.0346 | 0.1180 | 0.8959 | nan | -0.130 | 0.9895 | 66 | -17074.8 | 34214.3 |

*GJR-t : t-stat de γ = 8.17 → effet de levier **significatif** ; α = 0.0359 (t=6.42) : les chocs positifs contribuent peu, l'essentiel passe par les chocs négatifs — fait stylisé indice actions.*

## 2. Validation d'implémentation

- Prévision 1 pas GJR-t : récursion maison 2.530973 vs `arch` 2.530973 (écart relatif 0.00e+00) → **OK**

## 3. Protocole out-of-sample (figé avant exécution)

- Fenêtre initiale : 750 obs (02/10/1985 → 19/09/1988), expansive, ré-estimation tous les 21 j (454 ré-estimations)
- OOS : 20/09/1988 → 13/07/2026 — **9522 prévisions 1 pas**, 9518 prévisions cumulées 5 pas (chevauchantes)
- ν (GJR-t) au fil des ré-estimations : min 4.8 / méd. 7.9 / max 10.0
- Univers de modèles : EWMA, GARCH-n, GARCH-t, GJR-t, GJR-skewt, HAR-P — benchmark : **GARCH-n**

## 4. Résultats out-of-sample

### Horizon 1 jour — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)

| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |
|---|---|---|---|---|---|---|
| EWMA | 1.5054 | +0.0194 | -3.06 | 0.999 | 0.4332 | 50.724 |
| GARCH-n (bench) | 1.4860 | — | — | — | 0.3987 | 50.118 |
| GARCH-t | 1.4846 | -0.0014 | +0.86 | 0.195 | 0.4012 | 50.284 |
| GJR-t | 1.4696 | -0.0164 | +6.33 | 0.000 | 0.3884 | 48.900 |
| GJR-skewt | 1.4698 | -0.0163 | +6.27 | 0.000 | 0.3883 | 48.868 |
| HAR-P | 1.4585 | -0.0275 | +4.10 | 0.000 | 0.3602 | 48.603 |

### Horizon 5 jours (cumulé, chevauchant) — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)

| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |
|---|---|---|---|---|---|---|
| EWMA | 0.3821 | +0.0221 | -3.03 | 0.999 | 0.2806 | 393.682 |
| GARCH-n (bench) | 0.3600 | — | — | — | 0.2410 | 383.459 |
| GARCH-t | 0.3589 | -0.0011 | +0.55 | 0.291 | 0.2426 | 387.071 |
| GJR-t | 0.3512 | -0.0088 | +2.94 | 0.002 | 0.2399 | 360.064 |
| GJR-skewt | 0.3508 | -0.0092 | +3.12 | 0.001 | 0.2391 | 359.602 |
| HAR-P | 0.3431 | -0.0168 | +2.29 | 0.011 | 0.2027 | 350.924 |

*Vol. annualisée prédite (GJR-t) sur l'OOS : min 8.6 % / méd. 19.1 % / max 111.2 %.*

## 5. Test SPA de Hansen (2005) — correction du data-snooping

H₀ : le benchmark GARCH(1,1)-n n'est battu par AUCUN des 5 modèles de l'univers (bootstrap stationnaire Politis-Romano, bloc moyen 20 j, 5000 réplications, recentrage consistant).

- **Horizon 1 jour** : t_SPA = 6.09, **p = 0.0000** (meilleur modèle : GJR-t) → H₀ rejetée : la surperformance survit à la correction du data-snooping.
- **Horizon 5 jours** : t_SPA = 2.96, **p = 0.0034** (meilleur modèle : GJR-skewt) → H₀ rejetée : la surperformance survit à la correction du data-snooping.

## 6. Verdict contre les seuils du cahier des charges

- Meilleur modèle 1 pas (QLIKE ε²) : **HAR-P** (1.4585 vs 1.4860 bench)
  - EWMA : ne bat pas le bench (p=0.999)
  - GARCH-t : bat le bench, NON significatif (p=0.195)
  - GJR-t : bat le bench, significatif à 10 % (p=0.000)
  - GJR-skewt : bat le bench, significatif à 10 % (p=0.000)
  - HAR-P : bat le bench, significatif à 10 % (p=0.000)

### Lecture honnête des deux niveaux d'inférence

1. **Hypothèse primaire pré-enregistrée** (GJR-t vs GARCH-n, choisie AVANT de voir les données sur la base de Hansen-Lunde 2005 / Liu-Hung 2010) : DM unilatéral p=0.000 (h=1) et p=0.002 (h=5), cohérente sur les deux horizons → **validée**.
2. **Correction famille entière** (SPA sur les 5 modèles) : p=0.0000 (h=1) et p=0.0034 (h=5) → la surperformance **survit** à la correction du data-snooping. Sur 9522 obs OOS (~38 ans, plusieurs cycles), le signal est statistiquement robuste — ce que l'échantillon court ne permettait pas de trancher.

**Conclusion opérationnelle** : GJR-GARCH(1,1)-t est adopté comme moteur de volatilité v1 (direction conforme à la littérature, gain régulier, benchmark battu partout où il doit l'être). Sur l'historique long, la robustesse statistique est confirmée (SPA) : la voie de progrès devient la finesse des données (RV intraday) et non le volume d'historique.
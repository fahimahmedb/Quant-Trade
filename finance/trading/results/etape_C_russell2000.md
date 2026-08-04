# Étape C — Modèles de volatilité : estimation et évaluation walk-forward

## 1. Estimation in-sample (échantillon complet, 9781 obs)

| Modèle | ω | α | γ (levier) | β | ν | λ(skew) | persistance | demi-vie (j) | LogL | BIC |
|---|---|---|---|---|---|---|---|---|---|---|
| GARCH-n | 0.0169 | 0.1122 | nan | 0.8816 | nan | nan | 0.9938 | 111 | -14591.9 | 29220.5 |
| GARCH-t | 0.0082 | 0.1025 | nan | 0.8975 | 7.78 | nan | 1.0000 | inf | -14393.8 | 28833.6 |
| GJR-t | 0.0092 | 0.0521 | 0.0962 | 0.8965 | 7.97 | nan | 0.9967 | 211 | -14349.5 | 28754.1 |
| GJR-skewt | 0.0088 | 0.0518 | 0.0918 | 0.9000 | nan | -0.171 | 0.9977 | 299 | -14280.2 | 28624.6 |

*GJR-t : t-stat de γ = 6.93 → effet de levier **significatif** ; α = 0.0521 (t=7.80) : les chocs positifs contribuent peu, l'essentiel passe par les chocs négatifs — fait stylisé indice actions.*

## 2. Validation d'implémentation

- Prévision 1 pas GJR-t : récursion maison 0.974887 vs `arch` 0.974887 (écart relatif 0.00e+00) → **OK**

## 3. Protocole out-of-sample (figé avant exécution)

- Fenêtre initiale : 750 obs (11/09/1987 → 28/08/1990), expansive, ré-estimation tous les 21 j (431 ré-estimations)
- OOS : 29/08/1990 → 13/07/2026 — **9031 prévisions 1 pas**, 9027 prévisions cumulées 5 pas (chevauchantes)
- ν (GJR-t) au fil des ré-estimations : min 3.3 / méd. 7.3 / max 8.3
- Univers de modèles : EWMA, GARCH-n, GARCH-t, GJR-t, GJR-skewt, HAR-P — benchmark : **GARCH-n**

## 4. Résultats out-of-sample

### Horizon 1 jour — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)

| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |
|---|---|---|---|---|---|---|
| EWMA | 1.4308 | +0.0135 | -1.92 | 0.972 | 0.5585 | 28.755 |
| GARCH-n (bench) | 1.4173 | — | — | — | 0.5347 | 27.351 |
| GARCH-t | 1.4117 | -0.0056 | +3.84 | 0.000 | 0.5211 | 27.683 |
| GJR-t | 1.4025 | -0.0148 | +5.79 | 0.000 | 0.5175 | 27.246 |
| GJR-skewt | 1.4057 | -0.0116 | +5.03 | 0.000 | 0.5240 | 27.289 |
| HAR-P | 1.3828 | -0.0345 | +5.12 | 0.000 | 0.4498 | 27.713 |

### Horizon 5 jours (cumulé, chevauchant) — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)

| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |
|---|---|---|---|---|---|---|
| EWMA | 0.3832 | +0.0175 | -1.97 | 0.976 | 0.3539 | 296.122 |
| GARCH-n (bench) | 0.3657 | — | — | — | 0.3250 | 269.293 |
| GARCH-t | 0.3622 | -0.0036 | +1.94 | 0.026 | 0.3107 | 279.923 |
| GJR-t | 0.3573 | -0.0084 | +2.84 | 0.002 | 0.3183 | 275.920 |
| GJR-skewt | 0.3586 | -0.0071 | +2.74 | 0.003 | 0.3223 | 276.306 |
| HAR-P | 0.3347 | -0.0310 | +4.53 | 0.000 | 0.2464 | 274.110 |

*Vol. annualisée prédite (GJR-t) sur l'OOS : min 6.5 % / méd. 16.7 % / max 141.4 %.*

## 5. Test SPA de Hansen (2005) — correction du data-snooping

H₀ : le benchmark GARCH(1,1)-n n'est battu par AUCUN des 5 modèles de l'univers (bootstrap stationnaire Politis-Romano, bloc moyen 20 j, 5000 réplications, recentrage consistant).

- **Horizon 1 jour** : t_SPA = 5.64, **p = 0.0000** (meilleur modèle : GJR-t) → H₀ rejetée : la surperformance survit à la correction du data-snooping.
- **Horizon 5 jours** : t_SPA = 4.49, **p = 0.0000** (meilleur modèle : HAR-P) → H₀ rejetée : la surperformance survit à la correction du data-snooping.

## 6. Verdict contre les seuils du cahier des charges

- Meilleur modèle 1 pas (QLIKE ε²) : **HAR-P** (1.3828 vs 1.4173 bench)
  - EWMA : ne bat pas le bench (p=0.972)
  - GARCH-t : bat le bench, significatif à 10 % (p=0.000)
  - GJR-t : bat le bench, significatif à 10 % (p=0.000)
  - GJR-skewt : bat le bench, significatif à 10 % (p=0.000)
  - HAR-P : bat le bench, significatif à 10 % (p=0.000)

### Lecture honnête des deux niveaux d'inférence

1. **Hypothèse primaire pré-enregistrée** (GJR-t vs GARCH-n, choisie AVANT de voir les données sur la base de Hansen-Lunde 2005 / Liu-Hung 2010) : DM unilatéral p=0.000 (h=1) et p=0.002 (h=5), cohérente sur les deux horizons → **validée**.
2. **Correction famille entière** (SPA sur les 5 modèles) : p=0.0000 (h=1) et p=0.0000 (h=5) → la surperformance **survit** à la correction du data-snooping. Sur 9031 obs OOS (~36 ans, plusieurs cycles), le signal est statistiquement robuste — ce que l'échantillon court ne permettait pas de trancher.

**Conclusion opérationnelle** : GJR-GARCH(1,1)-t est adopté comme moteur de volatilité v1 (direction conforme à la littérature, gain régulier, benchmark battu partout où il doit l'être). Sur l'historique long, la robustesse statistique est confirmée (SPA) : la voie de progrès devient la finesse des données (RV intraday) et non le volume d'historique.
# Étape C — Modèles de volatilité : estimation et évaluation walk-forward

## 1. Estimation in-sample (échantillon complet, 6776 obs)

| Modèle | ω | α | γ (levier) | β | ν | λ(skew) | persistance | demi-vie (j) | LogL | BIC |
|---|---|---|---|---|---|---|---|---|---|---|
| GARCH-n | 0.0300 | 0.0985 | nan | 0.8857 | nan | nan | 0.9842 | 44 | -10733.0 | 21501.3 |
| GARCH-t | 0.0206 | 0.0974 | nan | 0.8955 | 6.94 | nan | 0.9929 | 98 | -10619.0 | 21282.1 |
| GJR-t | 0.0251 | 0.0021 | 0.1637 | 0.9005 | 7.48 | nan | 0.9845 | 44 | -10524.3 | 21101.6 |
| GJR-skewt | 0.0261 | 0.0015 | 0.1659 | 0.9013 | nan | -0.121 | 0.9858 | 48 | -10497.8 | 21057.4 |

*GJR-t : t-stat de γ = 8.60 → effet de levier **significatif** ; α = 0.0021 (t=0.35) : les chocs positifs contribuent peu, l'essentiel passe par les chocs négatifs — fait stylisé indice actions.*

## 2. Validation d'implémentation

- Prévision 1 pas GJR-t : récursion maison 1.510308 vs `arch` 1.510308 (écart relatif 0.00e+00) → **OK**

## 3. Protocole out-of-sample (figé avant exécution)

- Fenêtre initiale : 750 obs (02/11/1999 → 14/10/2002), expansive, ré-estimation tous les 21 j (287 ré-estimations)
- OOS : 15/10/2002 → 10/07/2026 — **6026 prévisions 1 pas**, 6022 prévisions cumulées 5 pas (chevauchantes)
- ν (GJR-t) au fil des ré-estimations : min 7.3 / méd. 11.1 / max 127.1
- Univers de modèles : EWMA, GARCH-n, GARCH-t, GJR-t, GJR-skewt, HAR-P — benchmark : **GARCH-n**

## 4. Résultats out-of-sample

### Horizon 1 jour — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)

| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |
|---|---|---|---|---|---|---|
| EWMA | 1.5438 | +0.0238 | -3.59 | 1.000 | 0.4254 | 25.987 |
| GARCH-n (bench) | 1.5200 | — | — | — | 0.4406 | 25.744 |
| GARCH-t | 1.5207 | +0.0008 | -0.74 | 0.771 | 0.4395 | 25.803 |
| GJR-t | 1.4900 | -0.0299 | +5.02 | 0.000 | 0.4202 | 24.748 |
| GJR-skewt | 1.4902 | -0.0297 | +4.95 | 0.000 | 0.4194 | 24.752 |
| HAR-P | 1.5079 | -0.0121 | +1.13 | 0.129 | 0.3728 | 25.204 |

### Horizon 5 jours (cumulé, chevauchant) — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)

| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |
|---|---|---|---|---|---|---|
| EWMA | 0.4176 | +0.0286 | -3.69 | 1.000 | 0.2326 | 174.054 |
| GARCH-n (bench) | 0.3890 | — | — | — | 0.2515 | 165.005 |
| GARCH-t | 0.3903 | +0.0013 | -1.08 | 0.860 | 0.2499 | 167.592 |
| GJR-t | 0.3671 | -0.0219 | +3.58 | 0.000 | 0.2348 | 148.919 |
| GJR-skewt | 0.3673 | -0.0217 | +3.53 | 0.000 | 0.2350 | 149.316 |
| HAR-P | 0.3965 | +0.0074 | -0.54 | 0.705 | 0.1852 | 162.339 |

*Vol. annualisée prédite (GJR-t) sur l'OOS : min 8.2 % / méd. 16.9 % / max 100.1 %.*

## 5. Test SPA de Hansen (2005) — correction du data-snooping

H₀ : le benchmark GARCH(1,1)-n n'est battu par AUCUN des 5 modèles de l'univers (bootstrap stationnaire Politis-Romano, bloc moyen 20 j, 5000 réplications, recentrage consistant).

- **Horizon 1 jour** : t_SPA = 4.73, **p = 0.0000** (meilleur modèle : GJR-t) → H₀ rejetée : la surperformance survit à la correction du data-snooping.
- **Horizon 5 jours** : t_SPA = 3.44, **p = 0.0016** (meilleur modèle : GJR-t) → H₀ rejetée : la surperformance survit à la correction du data-snooping.

## 6. Verdict contre les seuils du cahier des charges

- Meilleur modèle 1 pas (QLIKE ε²) : **GJR-t** (1.4900 vs 1.5200 bench)
  - EWMA : ne bat pas le bench (p=1.000)
  - GARCH-t : ne bat pas le bench (p=0.771)
  - GJR-t : bat le bench, significatif à 10 % (p=0.000)
  - GJR-skewt : bat le bench, significatif à 10 % (p=0.000)
  - HAR-P : bat le bench, NON significatif (p=0.129)

### Lecture honnête des deux niveaux d'inférence

1. **Hypothèse primaire pré-enregistrée** (GJR-t vs GARCH-n, choisie AVANT de voir les données sur la base de Hansen-Lunde 2005 / Liu-Hung 2010) : DM unilatéral p=0.000 (h=1) et p=0.000 (h=5), cohérente sur les deux horizons → **validée**.
2. **Correction famille entière** (SPA sur les 5 modèles) : p=0.0000 (h=1) et p=0.0016 (h=5) → la surperformance **survit** à la correction du data-snooping. Sur 6026 obs OOS (~24 ans, plusieurs cycles), le signal est statistiquement robuste — ce que l'échantillon court ne permettait pas de trancher.

**Conclusion opérationnelle** : GJR-GARCH(1,1)-t est adopté comme moteur de volatilité v1 (direction conforme à la littérature, gain régulier, benchmark battu partout où il doit l'être). Sur l'historique long, la robustesse statistique est confirmée (SPA) : la voie de progrès devient la finesse des données (RV intraday) et non le volume d'historique.
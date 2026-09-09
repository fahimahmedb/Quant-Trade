# Résultat — Expérience C' : sensibilité de la Stratégie A à la règle de sortie

Entrée identique à la Stratégie A (close>SMA50, breakout 20j, RSI14∈[50,75], entrée open(t+1)), Composite pré-enregistré, 1195 séances testables (à partir de la 56e). Seule la sortie change, 6 variantes, n_trials=6, DSR appliqué (seuil 0.95).

| Variante | Trades | Hit rate | R moyen | Sharpe | Rdt total | MDD | Sharpe>BH | Rdt>BH | PASS naïf | DSR |
|---|---|---|---|---|---|---|---|---|---|---|
| TP=2R (référence A) | 41 | 43.9% | +0.32R | +0.55 | +5.6% | -2.8% | OUI | non | FAIL | 0.745 |
| TP=3R | 32 | 43.8% | +0.75R | +0.96 | +11.7% | -2.5% | OUI | non | FAIL | 0.937 |
| TP=4R | 27 | 33.3% | +0.67R | +0.66 | +8.5% | -4.8% | OUI | non | FAIL | 0.817 |
| Trailing stop (chandelier, pas de TP) | 39 | 43.6% | +0.22R | +0.42 | +3.3% | -2.2% | non | non | FAIL | 0.649 |
| Pas de TP, sortie rupture tendance (close<SMA20) | 26 | 42.3% | +0.49R | +0.53 | +5.8% | -3.2% | non | non | FAIL | 0.729 |
| Time stop 10j (structure TP=2R) | 46 | 52.2% | +0.28R | +0.57 | +5.3% | -2.8% | OUI | non | FAIL | 0.757 |

Référence Buy & Hold sur le même échantillon : Sharpe +0.54, rendement total +80.1%.

**0/6 variantes PASS naïf (bat B&H en Sharpe ET rendement) ; 0/6 PASS naïf ET DSR>0.95.**

**Réponse à la question posée : NON** — aucune des 6 variantes de sortie (TP élargi, trailing, rupture de tendance, time stop) ne bat Buy & Hold simultanément en Sharpe et en rendement sur cet échantillon. Le take-profit court (2R) n'est pas le facteur limitant identifiable : élargir ou supprimer le TP ne suffit pas à transformer la Stratégie A en signal profitable net de coûts. Cohérent avec la conclusion déjà établie du repo (aucun signal actif testé ne bat B&H sur le Composite).

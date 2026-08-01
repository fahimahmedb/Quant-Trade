# Audit adversarial — exécution « même barre » dans les backtests de portefeuille

**Nature de ce document** : contrôle de correction de code sur des résultats DÉJÀ COMMITTÉS, découvert incidemment en lisant `build_weights()` pendant la conception d'un nouveau mécanisme. Ce n'est PAS un nouveau backtest, PAS une nouvelle hypothèse, et aucun paramètre n'a été touché. Produit par `scripts/nonml_same_bar_execution_audit.py`. Déclenché par la Règle 9 (un bug de code trouvé oblige à relancer les tests) et la Règle 6 (traçabilité).

## Le défaut, précisément

Dans `nonml_leaders_index52w_high_overlay_backtest.py::build_weights` (#38) et dans `nonml_short_term_momentum_backtest.py` (#14) :

```python
signal[t]      = f(close[t], ...)        # calculé sur la CLÔTURE du jour t
weights[t:end] = w(signal[t])            # poids en vigueur DÈS le jour t
pnl[t]         = (weights[t] * R[t]).sum()   # R[t] = log(close[t]/close[t-1])
```

`R[t]` est le rendement déjà réalisé entre la clôture de `t-1` et celle de `t`. Le portefeuille encaisse donc un rendement **antérieur à la décision qui l'a sélectionné**. C'est une fuite d'un jour, active sur une séance de rebalancement sur 21 pour le #38 et sur 5 pour le #14. Elle est d'autant plus forte que le signal contient le rendement du jour `t` lui-même — ce qui est le cas des deux : le #38 classe par `close(t)/max252(t)` et le #14 par `close(t)/close(t-5)−1`.

**Pourquoi les audits précédents ne l'ont pas détectée.** `nonml_leaders_index52w_high_overlay_audit.py` contient bien un « test anti-lookahead », mais il vérifie une propriété DIFFÉRENTE : que perturber les prix FUTURS ne modifie pas les valeurs PASSÉES du signal (causalité du CALCUL). Un signal parfaitement causal peut malgré tout être exécuté sur la mauvaise barre. La convention correcte est pourtant déjà appliquée ailleurs dans ce backlog — cycle #47 : « bug de fuite d'un jour trouvé et corrigé (`trend[:-1]` au lieu de `trend[1:]`) » — mais elle n'a jamais été portée aux backtests de PORTEFEUILLE.

## Mesure de l'impact

Une seule chose change entre les deux lignes de chaque tableau : la matrice de poids est décalée d'un jour (`W_causal[t] = W[t−1]`, « décider à la clôture de t−1, détenir pendant t »). Même signal, mêmes paramètres, même univers, mêmes coûts (5 bps), même fonction de PnL (`portfolio_pnl`).

## A. Cycle #38 — Leaders 52 semaines + overlay 52w-high indice

### A.1 Univers point-in-time 2015-2026 (référence d'évaluation, cycle #163)

2907 séances (2015-01-02 → 2026-07-27), rebalancement tous les 21 jours (soit ~5 % des séances où la sélection est renouvelée).

| Série | Convention | Sharpe ann. | Rendement total | MDD | Sharpe quotidien |
|---|---|---|---|---|---|
| Leaders 1.0x (référence) | telle quelle (fuite) | +0.785 | +361.9% | -28.8% | +0.04945 |
| Leaders 1.0x (référence) | **décalée +1j (causale)** | **+0.540** | **+169.0%** | -29.3% | +0.03403 |
| **#38** (Leaders + overlay ×2) | telle quelle (fuite) | +1.416 | +6489.1% | -30.9% | +0.08917 |
| **#38** (Leaders + overlay ×2) | **décalée +1j (causale)** | **+0.474** | **+201.1%** | -35.0% | +0.02986 |
| **#38** (Leaders + overlay ×2) | décalée +2j (placebo) | +0.491 | +222.2% | -36.8% | +0.03095 |

Critère renforcé du backlog (Sharpe **et** rendement > référence) : **PASS** avec la fuite → **FAIL** sans la fuite.

*Placebo* : passer de +1j à +2j de décalage ne coûte que +0.017 de Sharpe, contre -0.942 pour le passage de 0j à +1j. L'effondrement est donc bien spécifique à la **première** barre (celle qui a servi à calculer le signal), pas une sensibilité générale au décalage — c'est la signature d'une fuite, pas d'une décroissance rapide du signal.

Localisation de l'écart de PnL candidat (fuite − causale) : **98.0 %** de l'écart cumulé total est concentré sur les 275 séances où les poids changent (9.5 % des séances — renouvellement de la sélection, plus les bascules de l'overlay quand il y en a un). Gain moyen de la fuite : **+109.0 bps sur ces séances** contre +0.23 bps les autres jours. Un écart de calendrier ordinaire serait réparti uniformément ; celui-ci ne l'est pas.

### A.2 Univers d'origine 2022-2026 (cycle #38 tel que committé le 28/07)

1144 séances (2022-01-03 → 2026-07-27), rebalancement tous les 21 jours (soit ~5 % des séances où la sélection est renouvelée).

| Série | Convention | Sharpe ann. | Rendement total | MDD | Sharpe quotidien |
|---|---|---|---|---|---|
| Leaders 1.0x (référence) | telle quelle (fuite) | +0.784 | +81.6% | -25.7% | +0.04937 |
| Leaders 1.0x (référence) | **décalée +1j (causale)** | **+0.589** | **+53.5%** | -27.6% | +0.03711 |
| **#38** (Leaders + overlay ×2) | telle quelle (fuite) | +1.499 | +508.3% | -25.9% | +0.09444 |
| **#38** (Leaders + overlay ×2) | **décalée +1j (causale)** | **+0.650** | **+96.0%** | -30.7% | +0.04095 |
| **#38** (Leaders + overlay ×2) | décalée +2j (placebo) | +0.701 | +110.8% | -31.7% | +0.04418 |

Critère renforcé du backlog (Sharpe **et** rendement > référence) : **PASS** avec la fuite → **PASS** sans la fuite.

*Placebo* : passer de +1j à +2j de décalage ne coûte que +0.051 de Sharpe, contre -0.849 pour le passage de 0j à +1j. L'effondrement est donc bien spécifique à la **première** barre (celle qui a servi à calculer le signal), pas une sensibilité générale au décalage — c'est la signature d'une fuite, pas d'une décroissance rapide du signal.

Localisation de l'écart de PnL candidat (fuite − causale) : **96.6 %** de l'écart cumulé total est concentré sur les 112 séances où les poids changent (9.8 % des séances — renouvellement de la sélection, plus les bascules de l'overlay quand il y en a un). Gain moyen de la fuite : **+97.6 bps sur ces séances** contre +0.37 bps les autres jours. Un écart de calendrier ordinaire serait réparti uniformément ; celui-ci ne l'est pas.

## B. Cycle #14 — momentum court terme « Winners » (rebalancement hebdomadaire)

### B.1 Univers point-in-time 2015-2026 (cycle #164)

2907 séances (2015-01-02 → 2026-07-27), rebalancement tous les 5 jours (soit ~20 % des séances où la sélection est renouvelée).

| Série | Convention | Sharpe ann. | Rendement total | MDD | Sharpe quotidien |
|---|---|---|---|---|---|
| Équipondéré (référence) | telle quelle (fuite) | +0.368 | +88.5% | -36.1% | +0.02317 |
| Équipondéré (référence) | **décalée +1j (causale)** | **+0.373** | **+91.0%** | -36.2% | +0.02351 |
| **#14** (Winners, tercile sup.) | telle quelle (fuite) | +1.854 | +8303.4% | -28.4% | +0.11678 |
| **#14** (Winners, tercile sup.) | **décalée +1j (causale)** | **-0.007** | **-25.3%** | -44.6% | -0.00047 |
| **#14** (Winners, tercile sup.) | décalée +2j (placebo) | +0.118 | +2.1% | -42.5% | +0.00742 |

Critère renforcé du backlog (Sharpe **et** rendement > référence) : **PASS** avec la fuite → **FAIL** sans la fuite.

*Placebo* : passer de +1j à +2j de décalage ne coûte que +0.125 de Sharpe, contre -1.861 pour le passage de 0j à +1j. L'effondrement est donc bien spécifique à la **première** barre (celle qui a servi à calculer le signal), pas une sensibilité générale au décalage — c'est la signature d'une fuite, pas d'une décroissance rapide du signal.

Localisation de l'écart de PnL candidat (fuite − causale) : **95.8 %** de l'écart cumulé total est concentré sur les 581 séances où les poids changent (20.0 % des séances — renouvellement de la sélection, plus les bascules de l'overlay quand il y en a un). Gain moyen de la fuite : **+78.1 bps sur ces séances** contre +0.85 bps les autres jours. Un écart de calendrier ordinaire serait réparti uniformément ; celui-ci ne l'est pas.

### B.2 Univers d'origine 2021-2026 (cycle #14 tel que committé le 28/07)

1391 séances (2021-01-11 → 2026-07-27), rebalancement tous les 5 jours (soit ~20 % des séances où la sélection est renouvelée).

| Série | Convention | Sharpe ann. | Rendement total | MDD | Sharpe quotidien |
|---|---|---|---|---|---|
| Équipondéré (référence) | telle quelle (fuite) | +0.630 | +87.2% | -35.1% | +0.03966 |
| Équipondéré (référence) | **décalée +1j (causale)** | **+0.626** | **+86.4%** | -35.1% | +0.03944 |
| **#14** (Winners, tercile sup.) | telle quelle (fuite) | +2.346 | +1813.4% | -22.4% | +0.14777 |
| **#14** (Winners, tercile sup.) | **décalée +1j (causale)** | **+0.671** | **+107.2%** | -40.6% | +0.04229 |
| **#14** (Winners, tercile sup.) | décalée +2j (placebo) | +0.708 | +117.7% | -44.7% | +0.04457 |

Critère renforcé du backlog (Sharpe **et** rendement > référence) : **PASS** avec la fuite → **PASS** sans la fuite.

*Placebo* : passer de +1j à +2j de décalage ne coûte que +0.036 de Sharpe, contre -1.674 pour le passage de 0j à +1j. L'effondrement est donc bien spécifique à la **première** barre (celle qui a servi à calculer le signal), pas une sensibilité générale au décalage — c'est la signature d'une fuite, pas d'une décroissance rapide du signal.

Localisation de l'écart de PnL candidat (fuite − causale) : **95.6 %** de l'écart cumulé total est concentré sur les 278 séances où les poids changent (20.0 % des séances — renouvellement de la sélection, plus les bascules de l'overlay quand il y en a un). Gain moyen de la fuite : **+76.6 bps sur ces séances** contre +0.89 bps les autres jours. Un écart de calendrier ordinaire serait réparti uniformément ; celui-ci ne l'est pas.

## Conclusion

Les quatre configurations testées donnent le même verdict qualitatif, sur deux univers indépendants et deux mécanismes indépendants : **le PASS disparaît dès que l'exécution est décalée d'un jour.** L'écart est concentré à plus de 90 % sur les séances de rebalancement, ce qui identifie la cause sans ambiguïté (si c'était un simple effet de décalage de calendrier, l'écart serait réparti uniformément).

Ce que cela implique, sans enjoliver :

1. **Le #38 n'est pas le meilleur candidat du backlog — il n'a probablement aucun edge.** Une fois l'exécution rendue causale, il ne bat plus sa propre référence Leaders 1.0x. Le DSR record de 0,754 (#163), le SPA à p=0,0000 (#161/#163) et les 4/4 folds de stabilité portaient tous sur une série de PnL contaminée.
2. **Le #14 est le cycle le plus touché**, parce qu'il rebalance chaque semaine (20 % des séances contaminées contre 4,8 % pour le #38) et que son signal — le rendement des 5 derniers jours **incluant le jour même** — est celui qui recoupe le plus directement le rendement encaissé. Son Sharpe spectaculaire (+2,35 à l'origine, +1,85 corrigé du biais du survivant au #164) était en grande partie une sélection des gagnants du jour, payée le jour même.
3. **Les cycles #161 à #164 restent méthodologiquement valides** — biais du survivant, analyse de puissance, univers point-in-time : tout ce travail est correct et reste utile. Mais il a été appliqué à un candidat dont l'edge était artificiel. La correction du biais du survivant (#163) et la correction de l'exécution (ici) sont deux défauts indépendants qui s'additionnent.
4. **Portée exacte, à ne pas exagérer.** Ce défaut concerne les backtests de PORTEFEUILLE (matrice de poids titre par titre) : #4, #14, #15, #38, #39, #42, #51, #73, #75, #79, #82, #84, #86, et leurs dérivés. Les overlays scalaires sur indice (la majorité du backlog, familles #29/#37/#47/#54/#57/#115/#134/#149…) utilisent une autre infrastructure, où l'alignement causal a été explicitement vérifié et corrigé dès le cycle #47 — ils ne sont **pas** concernés a priori, mais aucun d'eux n'a jamais atteint le seuil DSR de toute façon.
5. **Ce que ce document ne fait PAS.** Il ne corrige pas les scripts d'origine. Corriger `build_weights()` invaliderait rétroactivement une vingtaine de rapports déjà committés (#4, #14, #33, #38, #42, #51, #73, #82, #161→#164…) : c'est une décision de protocole qui revient à l'utilisateur, pas une décision d'analyse. Le chiffrage est fourni ici pour qu'elle soit prise en connaissance de cause.

**Lecture positive, et elle est réelle** : le protocole a fonctionné. Ce n'est pas une statistique défavorable qui a révélé le défaut, c'est la lecture ligne à ligne du code exigée par la Règle 7 avant de réutiliser une brique. Et le diagnostic chiffré de la Phase 2 (`nonml_dsr_decomposition_38.md`) reste valable dans sa partie méthodologique — il faut simplement lire sa conclusion comme « il fallait un Sharpe de 1,71 et nous n'en avions même pas 0,48 », au lieu de « il en manquait 0,29 ».

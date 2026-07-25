# Nouvelle phase de recherche — univers de 9 signaux techniques classiques (NDX 40 ans)
## 1. Cadrage et discipline anti-data-snooping
Base propre, independante des Etapes A/B/C/D et de la pipeline integree deja publiees dans le repo : aucun modele entraine, aucune reutilisation de features/labels ML. Seuls les utilitaires generiques (chargement des donnees, backtest a couts, metriques de trading, Deflated Sharpe Ratio) sont repris de `finance/src/`.
- Donnees : NDX (`data/nasdaq100_daily.txt`), 10273 seances, 1985-10-01 -> 2026-07-13.
- Walk-forward : T0=750, refit declare 21 j, embargo declare 21 j, couts 5 bps aller-retour.
- Fenetre OOS evaluee : 9522 observations (jour 750 a l'avant-dernier jour de l'historique).
- **Note de methode (honnetete)** : Signaux techniques deterministes (regles causales sur OHLC passes), aucun parametre estime par apprentissage sur labels futurs. refit_every/embargo declares dans la tache n'ont donc pas d'effet sur la construction des signaux (pas de fit, pas de fuite train/test a purger) ; seul T0 (debut de la fenetre OOS commune) est actif. Le seul parametre estime sur donnees (target_vol de S6/S6b) est calcule une seule fois sur l'echantillon in-sample [0:T0[, jamais retouche.
- Univers de **9 signaux figes a priori** (Phase 1, avant toute execution) : voir tableau ci-dessous. Aucun signal n'a ete ajoute apres avoir vu un resultat.
- 2 variantes supplementaires **declarees a l'avance** (Phase 3, S6b/S7b) : parametres choisis a priori sur l'echantillon in-sample [0:T0[ uniquement, jamais retouches apres coup. Comptees comme extension de l'univers (N=11 au total) pour le DSR, conformement a `CLAUDE.md`.

## 2. Univers figé (Phase 1)
| # | Signal |
|---|---|
| 0 | S0: Buy & Hold |
| 1 | S1: Momentum EMA 12/26 |
| 2 | S2: RSI(14) seuils 30/70 |
| 3 | S3: Donchian 20 breakout |
| 4 | S4: Momentum + RSI confluence |
| 5 | S5: EMA trend (50>200), long seul |
| 6 | S6: Vol-adjusted momentum (cap 1.5x) |
| 7 | S7: EMA confluence 12>50>200 |
| 8 | S8: Dual momentum (ROC 12j/20j) |

Variantes Phase 3 (hors univers principal, ajoutees a l'univers étendu N=11) :

| Variante | Description |
|---|---|
| S6b: Vol-adjusted momentum (cap 2.0x) [Phase 3] | parametre cap/filtre choisi a priori sur [0:T0[ |
| S7b: EMA confluence + filtre EMA200>SMA250 [Phase 3] | parametre cap/filtre choisi a priori sur [0:T0[ |

## 3. Résultats bruts (nets de coûts, fenêtre OOS complète)
| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Hit rate | Turnover/j |
|---|---|---|---|---|---|---|---|---|
| S0: Buy & Hold | +0.52 | +0.69 | +0.08 | +14.5 % | -82.9 % | +1.10 | 54.8 % | 0.000 |
| S1: Momentum EMA 12/26 | +0.23 | +0.31 | +0.06 | +6.2 % | -60.9 % | +1.04 | 52.2 % | 0.065 |
| S2: RSI(14) seuils 30/70 | +0.28 | +0.20 | +0.06 | +2.4 % | -31.9 % | +1.19 | 5.1 % | 0.060 |
| S3: Donchian 20 breakout | +0.18 | +0.24 | +0.04 | +4.8 % | -65.9 % | +1.03 | 51.8 % | 0.047 |
| S4: Momentum + RSI confluence | +0.17 | +0.21 | +0.04 | +4.1 % | -66.0 % | +1.03 | 44.2 % | 0.144 |
| S5: EMA trend (50>200), long seul | +0.67 | +0.79 | +0.30 | +14.3 % | -36.1 % | +1.14 | 44.6 % | 0.004 |
| S6: Vol-adjusted momentum (cap 1.5x) | -0.34 | -0.50 | -0.02 | -7.7 % | -98.2 % | +0.95 | 50.6 % | 0.338 |
| S7: EMA confluence 12>50>200 | +0.48 | +0.53 | +0.18 | +11.1 % | -44.9 % | +1.11 | 41.4 % | 0.026 |
| S8: Dual momentum (ROC 12j/20j) | +0.10 | +0.12 | +0.03 | +2.4 % | -61.2 % | +1.02 | 41.8 % | 0.209 |
| S6b: Vol-adjusted momentum (cap 2.0x) [Phase 3] | -0.36 | -0.53 | -0.02 | -8.7 % | -98.9 % | +0.94 | 50.6 % | 0.381 |
| S7b: EMA confluence + filtre EMA200>SMA250 [Phase 3] | +0.41 | +0.43 | +0.16 | +9.0 % | -41.1 % | +1.10 | 36.1 % | 0.023 |

## 4. Ranking par Sharpe annualisé (univers principal N=9)
1. **S5: EMA trend (50>200), long seul** — Sharpe ann. +0.67
2. **S0: Buy & Hold** — Sharpe ann. +0.52
3. **S7: EMA confluence 12>50>200** — Sharpe ann. +0.48
4. **S2: RSI(14) seuils 30/70** — Sharpe ann. +0.28
5. **S1: Momentum EMA 12/26** — Sharpe ann. +0.23
6. **S3: Donchian 20 breakout** — Sharpe ann. +0.18
7. **S4: Momentum + RSI confluence** — Sharpe ann. +0.17
8. **S8: Dual momentum (ROC 12j/20j)** — Sharpe ann. +0.10
9. **S6: Vol-adjusted momentum (cap 1.5x)** — Sharpe ann. -0.34

## 5. Deflated Sharpe Ratio
### 5.1 Univers principal officiel de la tâche (N=9, σ²(SR essais)=3.3873e-04)

| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| S0: Buy & Hold | +0.0328 | 0.0280 | +0.47 | **0.681** |
| S1: Momentum EMA 12/26 | +0.0147 | 0.0280 | -1.30 | **0.097** |
| S2: RSI(14) seuils 30/70 | +0.0178 | 0.0280 | -1.06 | **0.146** |
| S3: Donchian 20 breakout | +0.0114 | 0.0280 | -1.62 | **0.053** |
| S4: Momentum + RSI confluence | +0.0105 | 0.0280 | -1.70 | **0.044** |
| S5: EMA trend (50>200), long seul | +0.0421 | 0.0280 | +1.36 | **0.914** |
| S6: Vol-adjusted momentum (cap 1.5x) | -0.0214 | 0.0280 | -4.82 | **0.000** |
| S7: EMA confluence 12>50>200 | +0.0303 | 0.0280 | +0.22 | **0.587** |
| S8: Dual momentum (ROC 12j/20j) | +0.0064 | 0.0280 | -2.10 | **0.018** |

### 5.2 Univers étendu honnête (N=11, inclut les variantes Phase 3, σ²(SR essais)=4.2378e-04)

| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| S0: Buy & Hold | +0.0328 | 0.0334 | -0.06 | **0.477** |
| S1: Momentum EMA 12/26 | +0.0147 | 0.0334 | -1.82 | **0.034** |
| S2: RSI(14) seuils 30/70 | +0.0178 | 0.0334 | -1.62 | **0.053** |
| S3: Donchian 20 breakout | +0.0114 | 0.0334 | -2.15 | **0.016** |
| S4: Momentum + RSI confluence | +0.0105 | 0.0334 | -2.23 | **0.013** |
| S5: EMA trend (50>200), long seul | +0.0421 | 0.0334 | +0.84 | **0.799** |
| S6: Vol-adjusted momentum (cap 1.5x) | -0.0214 | 0.0334 | -5.35 | **0.000** |
| S7: EMA confluence 12>50>200 | +0.0303 | 0.0334 | -0.30 | **0.381** |
| S8: Dual momentum (ROC 12j/20j) | +0.0064 | 0.0334 | -2.63 | **0.004** |
| S6b: Vol-adjusted momentum (cap 2.0x) [Phase 3] | -0.0227 | 0.0334 | -5.48 | **0.000** |
| S7b: EMA confluence + filtre EMA200>SMA250 [Phase 3] | +0.0261 | 0.0334 | -0.71 | **0.240** |

Verdict multiple-testing (seuil DSR>0.95 = edge réel même après correction) : aucun signal actif ne passe ce seuil (univers N=9). Univers étendu N=11 : aucun signal actif ne passe ce seuil.

## 6. Leçons
- Les signaux techniques déterministes testés ici n'ont, par construction, aucun paramètre appris sur des labels futurs : le couple refit/embargo hérité du protocole de l'Étape B (modèles ML) est donc **vide de contenu opérationnel** pour cet univers — seul le point de départ T0 de la fenêtre OOS commune compte. Ce constat est déclaré explicitement plutôt que de prétendre silencieusement à un embargo qui n'a aucun effet mesurable ici.
- Le coût de transaction (5 bps) pénalise fortement les signaux à turnover élevé (mean-reversion RSI, ajustement de volatilité quotidien) : comparer le tableau Sharpe brut/écarté du turnover est essentiel avant toute conclusion.
- Ajouter S6b/S7b après coup sans les compter dans le DSR aurait été une violation de la discipline anti-snooping du repo ; ils sont donc inclus dans un univers étendu à N=11 pour un DSR honnête (section 5.2), même si la tâche ne demandait formellement que N=9.
- Résultat notable (**à ne pas sur-interpréter**) : dans cet univers N=9, le DSR le plus élevé n'est **pas** Buy & Hold (DSR=0.681) mais **S5: EMA trend (50>200), long seul** (DSR=0.914), un filtre de tendance long-terme long-seul à très faible turnover (0.004/j) qui évite une bonne partie des grands drawdowns (MDD -36.1 % vs -82.9 % pour Buy & Hold) tout en gardant un rendement annualisé proche. Il reste toutefois **sous le seuil 0.95** retenu pour parler d'edge réel certain après correction multi-essais (N=9 puis N=11 en univers étendu) : à traiter comme un signal prometteur mais **non confirmé**, pas comme une découverte actionnable.

## 7. Recommandation honnête
**Buy & Hold reste la conclusion par défaut la plus défendable**, mais avec une nuance honnête à signaler : sur ce protocole précis (NDX 40 ans, T0=750, coûts 5 bps), **S5: EMA trend (50>200), long seul** affiche un Sharpe/DSR ponctuellement supérieur à Buy & Hold (0.914 vs 0.681) avec un MDD nettement plus faible (-36.1 % vs -82.9 %). Ni l'un ni l'autre ne franchit le seuil DSR>0.95 qui signerait un edge réel certain après correction multi-essais (N=9, puis N=11 avec les variantes Phase 3) : aucun des deux résultats n'est donc statistiquement distinguable du hasard de sélection à ce niveau de rigueur. **Recommandation** : ne pas déployer ce signal sur la seule base de ce résultat ; le signaler comme piste à re-tester sur un échantillon indépendant (ex. Composite) avant toute conclusion, exactement la discipline qui a évité de sur-interpréter les signaux de l'Étape B.

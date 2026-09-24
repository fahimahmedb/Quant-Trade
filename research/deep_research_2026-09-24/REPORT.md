# Lab : démarrer vite en apprenant des gens qui ont réussi (v2, 2026-09-24)

Ce document est de la recherche de lab, en paper/shadow uniquement. Il ne modifie ni le code produit ni la gouvernance, et n'accorde aucune autorisation de capital réel. Il vit sur la branche de lab `claude/deep-research-project-6vr22g`.

Chaque question suit le même déroulé : **Process → Info → Test → Conclusion → Recommandation**.

Tous les tests sont reproductibles avec les scripts `exp_*.py` de ce dossier. Au total, **environ 140 configurations ont été testées**, et ce nombre sert à ajuster le seuil de significativité (correction pour tests multiples).

---

## Synthèse en 10 lignes

1. **La vitesse d'apprentissage dépend du Sharpe et du nombre de paris indépendants, pas de la patience.** Pour prouver une stratégie, il faut environ (2/SR)² années d'observation. En shadow, un test séquentiel (SPRT) tranche en **3 mois pour une stratégie à SR 4**, 13 mois pour SR 2, et 4 ans pour SR 1.
2. **Les 12 ETF du repo ne valent qu'environ 1,2 pari indépendant.** Aucune stratégie n'y bat l'achat simple.
3. **Sur 190 futures, trend + carry donne un SR de 1,28 (t = 8,7), positif dans chaque période depuis 1980.** Le Sharpe monte avec le nombre d'instruments : 0,29 avec 1 instrument, 0,75 avec 40. C'est l'edge le mieux prouvé. Il faut environ 150 à 300 k$ pour le trader réellement.
4. Sur les marchés de prédiction, **acheter systématiquement les favoris ou les longshots n'est pas un edge stable** : le signe s'inverse selon l'échantillon. L'edge robuste est structurel : **être teneur de marché plutôt que preneur** (+1,1 % contre −1,1 % par trade sur 72 M de trades Kalshi).
5. **Le « lag Binance → Polymarket » des posts X existe, mais seulement à ≤ 1 s de latence** (+32 % par $ misé, t = 3,1 avec regroupement par heure, sur 1 jour de données). Il disparaît dès 3 s. C'est une course d'infrastructure, pas un edge accessible à un opérateur solo sans colocalisation.
6. **Le carry crypto s'est effondré.** Le funding BTC est passé de 20 %/an (2021) à 3 % (2025), puis 1 % (2026), sous le taux sans risque stablecoin ou T-bill d'environ 4 %. Le carry cross-sectionnel sur altcoins perd de l'argent après coûts.
7. **Les facteurs actions classiques (taille, value, CMA) sont morts depuis 2000.** Seuls le low-risk (BAB) avec gestion de volatilité, la qualité et le momentum avec gestion de volatilité survivent, et ils faiblissent sur 2020-25.
8. **Les LLM ne battent pas le prix de marché en prévision** (Brier 0,109 contre 0,096 pour le prix seul). Les concours de trading LLM en live sont surtout négatifs. Leur rôle utile : générer des hypothèses, lire les règles de résolution, compléter le prix de marché.
9. **Le vol-targeting divise le drawdown par deux** sur SPY (−34 % → −18 %) avec un Sharpe au moins égal. C'est la couche RISK/SIZE par défaut.
10. **Les données historiques longues existent déjà gratuitement**, via GitHub : 190 futures depuis 1980, facteurs AQR jusqu'en 2025, funding crypto, carnets d'ordres Polymarket, S&P 500 point-in-time. Il n'y a pas besoin d'attendre 3 à 4 ans.

---

## 1. Vitesse d'apprentissage : la vraie contrainte

**Process** : calculer la puissance statistique, puis simuler un test séquentiel SPRT en Monte Carlo avec des queues épaisses (t de Student à 4 degrés de liberté).

**Tests** : `exp_shiller_timing_power.py` et `exp_sprt_kill_rule.py`.

| SR réel | Années pour t = 2 | SPRT : mois médians pour décider | SPRT : p90 (mois) | Taux d'erreur |
|---|---|---|---|---|
| 1 | 4 | 51 | 120 | 3 % |
| 2 | 1 | 13 | 32 | 5 % |
| 4 | 0,25 | 3,3 | 8 | 4 % |

**Conclusion** : le shadow ne peut pas confirmer vite un SR de 1. Il **tue vite** les stratégies à SR élevé qui ne tiennent pas leurs promesses. Ceux qui ont réussi vite ont démarré sur des edges structurels à SR élevé (arbitrage, market making), ou ont fondé leur a priori sur une histoire longue (Carver, AQR).

**Reco** :
- Classer chaque ticket de recherche par temps de validation estimé, (2/SR)² / N_eff.
- Brancher un SPRT mensuel qui arrête automatiquement les stratégies en shadow.

## 2. Breadth : la preuve par 190 futures

**Test** (`exp_futures_trend_carry.py`) : données pysystemtrade (`git clone github.com/pst-group/pysystemtrade`), 1980-2024.
- Signal trend : EWMAC 16/32/64.
- Carry : calculé à partir de l'écart entre deux contrats.
- Signaux causaux ; coût = demi-spread de chaque instrument.

| Stratégie | SR | t | 1980-99 | 2000-12 | 2013-19 | 2020-24 | MDD à 10 % de vol |
|---|---|---|---|---|---|---|---|
| Trend EWMAC | 1,09 | 7,4 | 1,62 | 0,99 | 0,88 | 0,56 | −33 % |
| Carry | 1,15 | 7,8 | 1,46 | 1,23 | 1,19 | 0,10 | −27 % |
| **Trend + carry** | **1,28** | **8,7** | 1,76 | 1,27 | 1,12 | 0,46 | −27 % |

Courbe de breadth (trend + carry, 2000-2024) :

| Nombre d'instruments | 1 | 3 | 5 | 10 | 20 | 40 | 63 |
|---|---|---|---|---|---|---|---|
| SR médian | 0,29 | 0,41 | 0,51 | 0,60 | 0,68 | 0,75 | 0,74 |

Pour comparaison, le même type de trend sur les 12 ETF du repo donne un SR de 0,15.

**Capital minimum** (`exp_futures_min_capital.py`, avec micro-futures, 20 % de volatilité cible, au moins 4 contrats de granularité par instrument) :
- 5 classes d'actifs : environ 160 k$ ;
- 10 classes d'actifs : environ 320 k$.

**Conclusion** : c'est l'edge le mieux documenté, depuis 1880 selon AQR, et le plus facile à mettre en shadow tout de suite. Il **décroît sur 2020-24**, avec un carry proche de 0.

**Reco** : **premier vertical shadow = trend + carry multi-actifs**, en réutilisant pysystemtrade comme référence indépendante, pour recouper les résultats.

## 3. Marchés de prédiction (le périmètre de tes posts X)

**Test du biais favori-longshot** (`exp_pm_favorite_longshot.py`) : trois échantillons Polymarket indépendants, plus 12 704 matchs de Premier League avec les cotes bookmakers.

| Échantillon | Favoris > 0,9 | Longshots < 0,1 |
|---|---|---|
| A (septembre 2026, prix mid) | −5,6 % (t −3,9) | +92 % (t +3,0) |
| B (2025-26, 1 jour avant résolution) | +0,8 % (t 0,8) | −42 % (t −2,0) |
| C (vrais prix ask exécutables, 7 événements) | +2,8 % (t 2,1) | −71 % (t −3,1) |
| Foot, Bet365 (retail) | ≈ −2 % | −10 à −18 % (t −3,0) ; négatif 16 saisons sur 24 |
| Foot, Pinnacle à la clôture (sharp) | ≈ 0 | ≈ 0 |

**Littérature** :
- Kalshi, 72 M de trades : les teneurs de marché gagnent +1,12 % par trade, les preneurs −1,12 %.
- Polymarket : environ 70 % des wallets perdent, et moins de 1 % des wallets prennent la moitié des profits.
- 40 M$ extraits par arbitrage combinatoire entre avril 2024 et avril 2025.
- Environ 1 % des marchés sont contestés à l'oracle UMA.

**Test de lag BTC Up/Down** (`exp_pm_btc_lag.py`) : vrais carnets L2 sur 405 marchés, confrontés au flux Binance.

| Latence | Seuil d'edge | n | Rendement par $ | t |
|---|---|---|---|---|
| 1 s | 10c | 337 | +33 % | 3,2 (3,1 regroupé par heure) |
| 3 s | 10c | 373 | −4 % | −0,7 |
| 5 s | 10c | 382 | −3 % | −0,5 |

Brier du prix mid : 0,1557, du modèle : 0,1571, du mélange : 0,1549. Le marché est globalement efficient ; l'edge tient uniquement à la vitesse.

Limites : 1 seul jour, profondeur du carnet non vérifiée, résolution Chainlink et non Binance. La ligne « latence 0 » est exclue parce qu'elle contient jusqu'à 1 s de regard vers le futur.

**Conclusion** :
- Les posts X ont raison sur l'**existence** des edges, mais pas sur leur **accessibilité**.
- La latence se joue à la sub-seconde.
- Les biais de prix changent de signe selon l'échantillon.
- Ce qui reste durable : **la tenue de marché, l'arbitrage combinatoire, et la comparaison avec une cote de référence fiable** (Pinnacle).

**Reco** :
- Vertical shadow n°2 : **market making plus scanner d'arbitrage combinatoire** sur Polymarket et Kalshi. Il faut modéliser la file d'attente, la sélection adverse, les rebates, les frais par catégorie, le coût de l'argent immobilisé et une décote de 1 % pour le risque de contestation UMA.
- Statistiques toujours **regroupées par événement**.
- Rejouer le test de lag sur 30 jours ou plus avant toute conclusion.

## 4. Crypto

**Test** (`exp_crypto_edges.py`) : 35 configurations sur des données Bybit, Hyperliquid et Binance récupérées sur GitHub.

| Stratégie | Rendement annuel | SR | t | 2025 |
|---|---|---|---|---|
| Carry BTC toujours actif (2020-26) | 7,9 % | 8,4 | 21,5 | +3,4 % |
| Carry cross-sectionnel Bybit, top 10 | 1,0 % | 0,17 | 0,26 | −15 % |
| Momentum 28 jours Hyperliquid | 22 % | 0,71 | 1,15 | +58 % (2026 : −83 %) |

Funding BTC annualisé :

| Année | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| Funding | 11 % | 20 % | 3 % | 5 % | 8 % | 3 % | 1 % |

**Conclusion** : le carry est structurel, mais il est **aujourd'hui sous le taux sans risque**. Aucune stratégie de momentum ou de reversal n'atteint t > 3.

**Reco** :
- Utiliser le rendement stablecoin ou T-bill comme **hurdle explicite dans SIZE**.
- Au plus une poche de carry BTC/ETH, qui ne s'active que si le rendement dépasse le hurdle de 3 points ou plus.
- Garde-fous contre l'auto-déleveraging (ADL) et les liquidations dans RISK : plafond par venue, jambe courte à 2x maximum, stress test sur le scénario du 10/10/2025.

## 5. Actions et facteurs (débloquer la voie `RESEARCH`)

**Test** (`exp_equity_factor_lab.py`) : 65 configurations sur les facteurs AQR (jusqu'en 2025-09) et Kenneth French (jusqu'en 2021-11), via des miroirs GitHub LFS. Seuil de Bonferroni : |t| > 3,36.

| Facteur | SR total | SR depuis 2000 | SR 2020-25 |
|---|---|---|---|
| Taille (SMB) | 0,22 | 0,10 | −0,32 |
| Value (HML) | 0,28 | 0,13 | 0,08 |
| Momentum (UMD) | 0,51 | 0,18 | 0,12 |
| Low-risk (BAB) | 0,71 | 0,64 | 0,12 |
| Qualité (QMJ) | 0,51 | 0,41 | 0,03 |

- Seul le **BAB avec gestion de volatilité** passe le seuil depuis 2000 (t = 4,8).
- Le momentum sectoriel devient quasi nul net de coûts depuis 2000.

**Conclusion** : il n'y a pas de nouvel alpha à chercher dans les facteurs publiés. Ce qui vaut la peine : une exposition bon marché, diversifiée et pilotée par le risque. Le vrai blocage n'est pas la liste des composants de l'indice (on la trouve sur `fja05680/sp500`) mais **les prix des titres délistés**, qui ne sont disponibles gratuitement nulle part.

**Reco** :
- Débloquer la voie actions avec les facteurs AQR et French (en enregistrant la provenance).
- Pour un panel titre par titre, il faudra une source payante (CRSP, Norgate ou Sharadar). Cela demande l'accord du propriétaire du projet.

## 6. LLM et agents IA : ce qui est prouvé

- **ForecastBench** : superforecasters 0,081, meilleur LLM 0,101 ; la parité est projetée pour fin 2026. Sur les questions de marché, le **prix seul (0,096) bat le LLM (0,109)**.
- **Alpha Arena S1** (trading live) : 4 modèles sur 6 perdent de 40 à 60 %.
- **PolyBench** : 2 modèles sur 7 sont rentables.
- **Signal de sentiment d'actualités GPT** : le SR passe de 6,5 à 1,2 entre 2021 et 2024.
- **Piège n°1 : le biais de regard vers le futur des LLM** (mémoire des modèles, cutoffs peu fiables). Parades :
  - n'évaluer que sur des questions ouvertes après le cutoff ;
  - mesurer la contamination avec le « lookahead propensity » ;
  - masquer les noms des entités ;
  - utiliser une recherche documentaire strictement point-in-time.
- « Jev », Hermes et consorts : aucune preuve indépendante d'edge. `Polymarket/agents` montre les anti-patterns : taille de position extraite par regex du texte du LLM, relances d'appel sans limite.

**Reco (VET / Research Factory)**, chaque point avec son test falsifiable :
1. **Masque causal** (modèle, cutoff, as-of) sur toute preuve produite par un LLM. Test : toute preuve antérieure au cutoff est rejetée.
2. Le LLM prévoit **l'écart au prix de marché**, fusionné en log-odds, avec un poids initial de 0. Test : Brier du mélange < Brier du marché, sur 300 questions ou plus postérieures au cutoff.
3. **Lecteur de règles de résolution**. Il alimente RISK (décote) et jamais la direction du trade.
4. **Générateur d'hypothèses** avec registre des essais. Test : les idées du LLM doivent battre des facteurs aléatoires hors échantillon.
5. **Sizing déterministe** : le LLM ne dimensionne jamais une position.
6. **Cache hashé des sorties LLM** pour un replay idempotent, conforme aux invariants de Quant.

## 7. Méthode (s'applique à tout)

- Pré-enregistrer chaque test et tenir un **registre global des essais** (environ 140 à ce jour).
- Deflated Sharpe, barre t > 3.
- Tester le **même** signal sur tout le panel.
- CPCV + PBO ; block bootstrap.
- Shrinkage d'environ 50 % du SR de backtest (McLean-Pontiff).
- Shadow + SPRT pour **tuer** vite.

## 8. Feuille de route

| # | Action | Test de sortie | Priorité |
|---|---|---|---|
| R0 | Ouvrir le réseau vers : data.binance.vision, Polymarket, Kalshi, FRED, Kenneth French, CFTC, SEC, s3.jbecker.dev (36 Go de trades Kalshi et Polymarket) | Les adapters téléchargent avec empreinte | **Immédiat** |
| R1 | Adapters Data Plane pour les miroirs GitHub (pysystemtrade, AQR, fja05680, carnets Polymarket) avec provenance « tiers » | Panel ≥ 100 instruments enregistré | Immédiat |
| R2 | Vertical shadow **trend + carry futures** (190 instruments) | Rejoue le SR ≥ 1 historique ; SPRT en shadow | **P1** |
| R3 | Overlay vol-target + filtre de tendance dans SIZE/RISK | MDD shadow < MDD du buy & hold | P1 |
| R4 | Hurdle explicite = taux sans risque, et `NO_TRADE` s'il n'est pas battu | Toute poche doit battre le hurdle net | P1 |
| R5 | Vertical shadow **market making + arbitrage combinatoire** sur marchés de prédiction | Rendement net > 0, t > 3 regroupé par événement, sur ≥ 500 marchés | P2 |
| R6 | SPRT mensuel et registre global des essais | Arrêt automatique si PSR < 5 % | P1 |
| R7 | LLM = générateur d'hypothèses et lecteur de règles, sous masque causal | Tests du §6 | P2 |
| R8 | Rejouer le test de lag BTC sur ≥ 30 jours, avec vérification de profondeur | Edge ≤ 1 s confirmé ou réfuté | P3 (infrastructure) |
| R9 | Panel actions sans biais de survivance : **décision d'achat de données** (CRSP, Norgate, Sharadar) | Accord du propriétaire | Décision |

**Garde-fous tirés des échecs documentés** :
- poly-maker : P&L nul à cause de bugs ;
- décroissance post-publication de −58 % ;
- changements de règles des venues (frais dynamiques, ADL) ;
- carry qui passe sous le hurdle.

## 9. Blocage d'environnement

Le proxy refuse les API de marché (Binance, Bybit, OKX, Polymarket, Kalshi, Yahoo, FRED, Kenneth French, SEC, CFTC, Hugging Face, x.com). Ce qui passe : `git clone` GitHub, raw.githubusercontent.com, media.githubusercontent.com (LFS) et pypi. À ouvrir dans les réglages réseau de l'environnement.

## Fichiers

| Script | Sujet |
|---|---|
| `exp_etf_baselines.py`, `exp_vol_managed.py`, `exp_shiller_timing_power.py` | Données du repo et Shiller/VIX (inclus) |
| `exp_futures_trend_carry.py`, `exp_futures_min_capital.py` | Argument = `pysystemtrade/data/futures` (git clone) |
| `exp_sprt_kill_rule.py` | Simulation pure |
| `exp_pm_favorite_longshot.py`, `exp_pm_btc_lag.py` | Dépôts GitHub listés en tête de chaque script (git clone) |
| `exp_crypto_edges.py`, `exp_crypto_carry_decomp.py` | Dépôts crypto listés au §4 et dans `SOURCES.md` |
| `exp_equity_factor_lab.py` | Miroirs AQR et French (media.githubusercontent.com) |

Les résultats bruts sont dans les fichiers `*.results.*`. La provenance et les sources sont dans `SOURCES.md`. Les données tierces ne sont pas vendorisées, sauf Shiller et VIX (petits fichiers, sha256 indiqués).

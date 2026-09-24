# Recherche approfondie : démarrer vite, apprendre en marchant (2026-09-24)

Statut : recherche uniquement, paper/shadow. Aucun capital réel n'est autorisé. Ce rapport ne modifie ni le code produit ni la gouvernance.

Pour chaque question, le rapport suit le même déroulé : **Process → Info → Test → Conclusion → Recommandation**.

---

## 0. Le diagnostic en une phrase

Aujourd'hui, Quant a une architecture complète mais **0 fill**. La recherche est `BLOCKED` en attendant un panel d'actions sans biais de survivance. Les seules données sont 12 ETF très corrélés. Et le repo compte environ 190 fichiers de gouvernance et de handoff.

Les gens qui ont réussi ont fait l'inverse. Ils ont choisi des marchés où **l'edge se mesure en semaines, pas en années**, et ils ont appris à petite taille sur le flux réel.

---

## 1. Pourquoi « attendre 3-4 ans de données » est la mauvaise question

**Process** : calculer, pour une stratégie, la durée d'observation nécessaire pour distinguer son Sharpe de zéro. Deux approches : la formule du t-stat et la Minimum Track Record Length de Bailey & López de Prado.

**Info** : le nombre d'années nécessaire vaut à peu près T ≈ (z / SR)².
- Trader plus souvent n'aide que si les paris sont **indépendants**.
- Poser un pari sur N instruments corrélés à ρ ne vaut que N / (1 + (N−1)ρ) instruments indépendants.

**Test** (`exp_shiller_timing_power.py`) : années requises pour atteindre t = 2.

| SR annuel réel | 0,3 | 0,5 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| Années | 44 | 16 | 4 | 1 | 0,4 |

Le calcul de breadth sur les données actuelles donne :
- 11 ETF sectoriels à ρ ≈ 0,8 valent environ **1,2 instrument indépendant**.
- 30 à 100 perpétuels crypto, ou des centaines de marchés de prédiction indépendants, valent un **N effectif de dizaines à centaines**.

**Conclusion** : ceux qui réussissent sans années de données ne sont pas plus patients. Ils exploitent des edges à **SR élevé et forte breadth** : arbitrage, carry de funding, mispricing sur marchés de prédiction, market making. Ces edges se valident ou se réfutent en quelques semaines de shadow.

Les edges « beta-like » à SR 0,3-0,5 (timing actions, momentum sectoriel) ne se valident **jamais** vite. On les prend pour la gestion du risque, sur la base de la littérature, pas comme preuve d'alpha.

**Reco R1** : réorienter le Research Factory vers des **univers à grande breadth** (crypto perps, marchés de prédiction). Classer chaque hypothèse selon le temps de validation attendu, (2/SR)² divisé par le N effectif, avant de la tester.

---

## 2. Ce que disent les données actuelles du repo (12 ETF, 2016-2026)

**Process** : 11 stratégies classiques issues de la littérature, **sans aucun paramètre ajusté**.
- Signal causal : décision à la clôture t, détention en t+1.
- Coût : 5 pb par unité de turnover.
- Le Sharpe est coupé en deux moitiés de l'échantillon.

**Test** (`exp_etf_baselines.py`) :

| Stratégie | SR | SR 1re moitié | SR 2e moitié | MDD |
|---|---|---|---|---|
| SPY buy & hold | 0,88 | 0,98 | 0,78 | −34 % |
| Inverse-vol SPY/TLT/GLD | **0,93** | 1,14 | 0,77 | −22 % |
| SPY > SMA200, sinon cash | 0,89 | 0,95 | 0,82 | **−21 %** |
| Momentum sectoriel top 3 (12-1) | 0,73 | 0,53 | 0,95 | −30 % |
| TSMOM 12m long/short, vol-target | 0,15 | −0,02 | 0,45 | −25 % |
| Retournement sectoriel 1 semaine | 0,52 | 0,43 | 0,63 | −46 % |
| Turn-of-month SPY | 0,31 | 0,45 | 0,17 | −11 % |
| SPY overnight only (après coûts) | −0,27 | 0,01 | −0,60 | −39 % |

Le test vol-managed (`exp_vol_managed.py`, Moreira-Muir) donne :

| Variante | SR | MDD |
|---|---|---|
| Buy & hold | 0,89 | −34 % |
| Vol-target sur vol réalisée | 1,01 | **−18 %** |
| Vol-target sur VIX | 1,02 | −20 % |

**Conclusion** : sur cet univers, **aucune stratégie ne bat le beta** de façon significative, et 11 essais imposent de corriger pour le multiple testing (Deflated Sharpe). Seules deux familles sont robustes, et ce sont des overlays de risque :
- le **vol-targeting**, qui divise le drawdown par deux avec un SR à peu près égal ou supérieur ;
- les **filtres de tendance**.

La recherche n'était pas bloquée par un manque d'actions sans biais de survivance. Elle l'était par un **univers sans breadth**.

**Reco R2** : garder le vol-targeting et le filtre de tendance comme **couche RISK/SIZE par défaut** dans le Desk. C'est un gain de drawdown prouvé, pas de l'alpha. Arrêter de chercher de l'alpha sur les 12 ETF.

---

## 3. Données longues disponibles tout de suite (pas besoin d'attendre)

**Test** (`exp_shiller_timing_power.py`) : S&P 500 mensuel Shiller, 1871-2026, dividendes inclus.
- Le signal est décalé de 2 mois, car les prix Shiller sont des moyennes mensuelles.
- Coût : 10 pb.

| Stratégie | SR total | MDD | SR 1872-1913 | SR 1914-45 | SR 1946-81 | SR 1982-07 | SR 2008-26 |
|---|---|---|---|---|---|---|---|
| Buy & hold | 0,50 | −82 % | 0,41 | 0,40 | 0,62 | 0,74 | 0,62 |
| SMA10 timing | 0,63 | −49 % | 0,47 | 0,67 | 0,63 | 0,77 | 0,78 |
| TSMOM12 timing | 0,56 | −42 % | 0,47 | 0,57 | 0,40 | 0,86 | 0,63 |

Cependant, le timing SMA10 **perd face au buy & hold dans 66 % des fenêtres de 10 ans** en rendement brut.

**Conclusion** : 150 ans de données sont gratuits et confirment la conclusion du §2. Le filtre de tendance améliore le SR et le drawdown dans les 5 ères, mais c'est une **assurance, pas un alpha**. Il sous-performe la plupart du temps.

Le point méthodologique est plus général : **l'histoire longue publique existe déjà pour la plupart des classes d'actifs** (crypto depuis 2017-2019, marchés de prédiction résolus depuis 2020-2021). Il n'y a pas à la collecter soi-même pendant des années.

**Reco R3** : ajouter au Data Plane des adapters d'**historique public long**. Chacun enregistre sa provenance et ses caveats point-in-time.
- Binance Vision : klines et funding, y compris les paires délistées, donc quasi sans biais de survivance.
- Marchés Polymarket et Kalshi résolus.
- Kenneth French, pour les facteurs.
- FRED/ALFRED, pour des données macro vintagées.
- CFTC COT.

---

## 4. Le périmètre de tes liens (posts X de sept. 2026)

**Info** : le texte exact des posts n'a pas pu être récupéré, car l'egress vers x.com et les miroirs est bloqué. Leur contenu a été reconstitué par recherche sur les auteurs.

Le fil commun :
- des **bots Polymarket et marchés de prédiction**, avec de la crypto court terme (BTC/ETH Up/Down 5-15 min, lag Binance → Polymarket) ;
- pilotés par des **LLM ou agents** : Claude, Grok, GPT-6, et récemment « Jev », un modèle de décision rapide.

Les edges revendiqués :
- arbitrage de complete set (YES + NO < 1 $) ;
- latence ou lag sur la résolution et le flux ;
- market making / spread farming ;
- copy-trading de wallets gagnants ;
- probabilité du modèle comparée au prix, avec un sizing Kelly.

**Red flags** communs :
- P&L en capture d'écran et biais de survivance, par exemple « 98,6 % des joueurs perdent » cité à côté d'un gagnant ;
- ni frais, ni slippage, ni file d'attente, ni sélection adverse ;
- échantillons de quelques centaines de trades ;
- autorité mal attribuée, comme une « spec Anthropic » ;
- incitations d'affiliation.

**Conclusion** : le périmètre est bon, car c'est un marché à forte breadth, avec des edges structurels mesurables vite. Les preuves, elles, sont nulles. Il faut traiter ces posts comme des **hypothèses à falsifier**, jamais comme des résultats.

---

## 5. Edges prouvés et accessibles à un opérateur solo

**Process** : environ 20 recherches web sur les praticiens documentés et la littérature. Certaines pages primaires étaient bloquées par le proxy, donc certains chiffres viennent d'abstracts. Il faut les **vérifier sur le papier source** avant de s'en servir comme preuve de gouvernance.

**Comment les praticiens ont démarré** :
- **Kevin Davey** est passé en live à temps partiel en 2003. Il a fait +148 %, +107 %, puis +112 % au championnat Robbins, en partant de 15 k$. Son process : walk-forward, puis Monte Carlo, puis **incubation** en live-sim avant l'argent réel.
- **Rob Carver** (pysystemtrade) conseille de construire son a priori sur **l'histoire longue et le mécanisme**. Son argument : aucun track record live ne prouvera jamais un SR de 0,4.
- **Kris Longmore** (Robot Wealth) avait un système parfait en backtest qui s'est effondré en live. Sa leçon : partir de « qui est en face et pourquoi il me paie ». Il considère les petits edges « trop petits pour les institutions » comme le terrain naturel du solo.
- **warproxxx** (poly-maker, market making Polymarket) annonçait environ 200 à 800 $/jour sur ~10 k$ grâce aux récompenses de liquidité. Il a ensuite reconnu **un P&L net nul, à cause de bugs**. C'est le risque opérationnel qui tue.
- **Quantpedia** : attendre un SR hors échantillon plus bas d'un tiers à la moitié que dans l'échantillon.

**Top 8 des edges pour un opérateur solo** (score = preuve × accessibilité × capacité à petite taille) :

| # | Edge | Preuve | Risque principal | Temps de validation |
|---|---|---|---|---|
| 1 | Tendance + carry diversifiés (micro-futures / ETF) | Positif chaque décennie depuis 1880 (AQR) | Capital nécessaire pour diversifier | Années : se juge sur l'a priori et l'histoire longue |
| 2 | **Market making sur marchés de prédiction, contrats à forte probabilité** | Kalshi, 300 k+ contrats : < 10c perdent > 60 %, > 50c légèrement positifs ; les makers perdent 10 %, les takers 32 % (Whelan) | Sélection adverse, bugs | **Semaines** |
| 3 | Carry de funding crypto, levier faible, uniquement quand le funding est élevé | SR ≈ 6 sur 2020-25, mais ≈ 4 en 2024 et **négatif en 2025** | ADL / crash du 10/10/2025, risque d'exchange | Semaines à mois |
| 4 | Arbitrage combinatoire ou logique entre marchés de prédiction liés (pas de latence) | 39,7 M$ extraits sur Polymarket (avril 2024 → avril 2025) | Concurrence, résolution | Semaines |
| 5 | Arbitrage cross-venue Polymarket / Kalshi | Écarts fréquents | **Règles de settlement différentes** : une couverture « sans risque » peut payer YES d'un côté et NO de l'autre | Semaines |
| 6 | Prime de volatilité à risque défini (put spreads, structure VIX) | Prime réelle | Queue gauche (Volmageddon 2018 : −90 % en un jour) | Mois |
| 7 | Saisonnalité overnight du momentum, en overlay | Tout l'alpha momentum est overnight (Lou-Polk-Skouras) | Coûts. Notre test : overnight SPY seul = **−0,27 SR après coûts** | — |
| 8 | PEAD sur micro-caps | Disparu sur les large caps depuis ~2006 | Spreads | — |

Deux paires d'edges sont **morts ou mourants** (preuves datées 2025-26) :
- La latence pure sur Polymarket : le délai de ~500 ms a été supprimé et des frais taker dynamiques allant jusqu'à ~3 % s'appliquent sur les marchés crypto courts. Le lag Binance → Polymarket vanté dans les posts X en fait partie.
- Le carry de funding naïf en 2025.

**Test sur les frais Kalshi** (formule publique 0,07·C·P·(1−P), maker = 25 % du taker) :

| Prix du contrat | Frais taker (% du prix) | Frais maker (% du prix) |
|---|---|---|
| P = 0,90 | 0,7 % | 0,18 % |
| P = 0,05 | **6,7 %** | 1,7 % |

**Conclusion** : les frais écrasent les longshots et les preneurs. **Il faut être maker sur les favoris**, ce qui rejoint exactement le biais favori-longshot.

**Reco R4** : premier vertical à haute breadth = **shadow market making / achat maker de favoris sur Kalshi et Polymarket**.
- Utiliser les marchés résolus comme historique immédiat.
- Modéliser explicitement les frais, la file d'attente et la sélection adverse.

**Reco R5** : deuxième vertical = **carry de funding crypto conditionnel** (funding > seuil, levier ≤ 2, multi-venue).
- Le stress test ADL et exchange fait partie du critère d'acceptation.
- L'historique Binance Vision couvre 2019 à aujourd'hui, avec les paires délistées.

---

## 6. Méthode d'apprentissage rapide et honnête

Chaque méthode est à brancher sur l'étape existante du Research Factory.

1. **Pré-enregistrement et comptage des essais.** Le Deflated Sharpe doit être calculé sur *tous* les essais. Harvey-Liu fixent la barre à t > 3.
2. **Pooling cross-sectionnel.** On teste une hypothèse sur tout le panel, pas un paramètre par instrument.
3. **CPCV** (validation croisée combinatoire purgée) avec embargo, plus la **PBO**. On rejette si PBO > 0,2.
4. **Block bootstrap** stationnaire, avec le test SPA de Hansen ou Romano-Wolf pour la famille de stratégies.
5. **Shrinkage** : le SR retenu vaut environ 50 % du SR du backtest (décroissance post-publication de McLean-Pontiff).
6. **Shadow + SPRT / PSR mensuel.** Le shadow sert à **tuer vite** ce qui ne marche pas, puisqu'il ne peut pas confirmer un SR de 1 en moins de 3 ans. Il détecte immédiatement les erreurs d'exécution et de coûts.
7. **Données synthétiques** (Ornstein-Uhlenbeck / GARCH) pour régler les stops et les horizons **sans consommer l'échantillon réel**. Elles ne servent jamais à prouver un edge.

---

## 7. Blocage d'environnement constaté

La politique réseau de cet environnement cloud refuse les connexions (CONNECT → 403) vers :
- data.binance.vision, fapi.binance.com, api.bybit.com, okx.com ;
- gamma-api.polymarket.com, api.elections.kalshi.com ;
- query1.finance.yahoo.com, fred.stlouisfed.org, stooq.com ;
- mba.tuck.dartmouth.edu (Kenneth French), data.sec.gov, publicreporting.cftc.gov ;
- huggingface.co.

Seuls raw.githubusercontent.com et pypi.org passent.

Pour débloquer, il faut changer l'accès réseau dans les réglages de l'environnement, ou ajouter ces domaines à la liste autorisée.

---

## 8. Feuille de route recommandée (chaque étape a un test de sortie)

| # | Action | Test de sortie (falsifiable) | Coût |
|---|---|---|---|
| R0 | Ouvrir le réseau vers les domaines listés au §7 | Les adapters téléchargent et enregistrent leur empreinte | 5 min de réglages |
| R1 | Score de « temps de validation » (2/SR)²/N_eff sur chaque ticket de recherche | Les tickets sont ordonnés par ce score dans la file | Petit |
| R2 | Overlay vol-target + filtre de tendance dans SIZE/RISK | MDD shadow < MDD du buy & hold, sans dégrader le SR | Petit |
| R3 | Adapters historiques : Binance Vision (klines + funding), marchés Kalshi/Polymarket résolus | Panel ≥ 100 instruments, délistés inclus, avec provenance | Moyen |
| R4 | Vertical shadow « maker favoris » sur les marchés de prédiction | Sur ≥ 500 marchés résolus hors échantillon : rendement net (frais, spread, rejets) > 0 avec t > 3 après DSR | Moyen |
| R5 | Vertical shadow carry de funding conditionnel | SR net > 1 hors 2025, et survit au scénario ADL 10/10/2025 | Moyen |
| R6 | Chaque stratégie en shadow passe un SPRT mensuel | Arrêt automatique si PSR(SR > 0) < 5 % | Petit |
| R7 | Les posts X, LLM et « Jev » entrent comme **générateurs d'hypothèses** seulement, jamais comme preuve | Chaque idée devient un ticket avec un test pré-enregistré | Nul |

**Garde-fous tirés des échecs documentés** :
- les coûts réels (voir le test overnight) ;
- la décroissance post-publication (−58 %) ;
- les changements de règles des venues (frais, délais, ADL) ;
- les bugs opérationnels (poly-maker).

Ce dernier point justifie les invariants existants de Quant (idempotence, restart-safety). **Il faut les garder, mais cesser d'ajouter des couches de gouvernance avant le premier fill shadow.**

## Reproductibilité

```bash
python3 research/deep_research_2026-09-24/exp_etf_baselines.py
python3 research/deep_research_2026-09-24/exp_shiller_timing_power.py
python3 research/deep_research_2026-09-24/exp_vol_managed.py
```

- Dépendances : numpy, pandas.
- Données : `data/datasets/us_sector_etf_daily.csv` (repo) et deux miroirs GitHub copiés ici :
  - `datasets/s-and-p-500`, qui est le jeu de données Shiller ;
  - `datasets/finance-vix`, qui vient du CBOE.
- Leur provenance est déclarée dans `SOURCES.md`.
- Caveat pour `exp_vol_managed.py` : la cible de volatilité est la médiane de l'échantillon complet. Cela n'affecte que le niveau de levier, pas le Sharpe.

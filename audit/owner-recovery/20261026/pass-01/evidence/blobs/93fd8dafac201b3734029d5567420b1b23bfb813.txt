# Du lab au produit : où chaque résultat s'implémente dans Quant

Ce document est une carte d'implémentation, pas une implémentation. Il vit sur la branche de lab, et aucune branche projet n'est modifiée.

Selon la gouvernance actuelle, l'intégration produit est en pause (`PRODUCT_INTEGRATION = PAUSED`). Chaque ligne ci-dessous devra donc devenir une mission Builder bornée, soumise à la réception Blue.

## Constat : ce que le code actuel suppose et qui bloque les edges trouvés

| Hypothèse codée | Où | Pourquoi ça bloque |
|---|---|---|
| Une seule famille de signaux, `cross_sectional` (relative value market-neutral) | `factory/signals.py:23` (StrategySpec), `:149` (weights_for) | Ni trend, ni carry, ni vol-targeting ne sont exprimables. |
| La falsification exige un **beta < 0,15** | `factory/evaluate.py` (`falsify`) | Une stratégie trend/carry directionnelle est rejetée par construction, même si elle est valide. |
| RISK plafonne l'**exposition nette à 10 %** | `desk/risk.py:22` (`RiskLimits.max_net_ratio`) | Tout book directionnel est coupé. |
| SIZE = capital × fraction × poids | `desk/desk.py` (bloc SIZE) | Pas de ciblage de volatilité ni de taux minimum à battre. |
| `PricePanel` = barres quotidiennes, rendements en % | `dataplane/panel.py:36` | Les prix futures back-adjustés peuvent être ≤ 0, et le carry exige une 2e série de prix (le contrat suivant). |
| Univers = 12 ETF Yahoo | `dataplane/ingest.py:94` | Le N effectif est d'environ 1,2, donc aucun edge n'est détectable. |
| Registre des essais par dataset | `factory/strategies.py:117` | Il n'existe pas de compteur global pour le Deflated Sharpe. |

Ce qui est déjà bon et doit être gardé :
- **même chemin de signal pour la recherche et le Desk** (`weights_for`) ;
- seuil t Bonferroni (`required_t_statistic`) ;
- stress test à 2× les coûts ;
- sleeves par stratégie ;
- idempotence et replay.

## Plan par phases

### Phase 1 : vertical trend + carry sur futures (l'edge le mieux prouvé ; s'insère dans l'architecture quotidienne existante)

| # | Plane | Fichier | Changement | Test d'acceptation |
|---|---|---|---|---|
| 1.1 | Data | `dataplane/adapters.py`, `ingest.py` | Adapter `pst_futures_mirror` : lit `adjusted_prices_csv` et `multiple_prices_csv` d'un clone pysystemtrade épinglé par commit. Provenance = URL + commit + sha256. Caveat « tiers, univers actuel ». | Fingerprint stable. Le rechargement donne le même digest. Les 190 instruments sont validés. |
| 1.2 | Data | `dataplane/panel.py` | Base de prix additive pour les futures : rendement en points / σ(points), pas en %. Champs `carry_price`, `price_contract` et `carry_contract`. | Un prix négatif ne casse rien. Le carry est calculé point-in-time. |
| 1.3 | Factory | `factory/signals.py` | `StrategySpec.family = "ts_trend_carry"`. `weights_for` dispatche selon la famille : EWMAC 16/32/64 + carry, normalisés par instrument de façon causale, bornés à ±2. | Test d'équivalence : les rendements Factory = ceux de `exp_futures_trend_carry.py` à 1e-9 près sur un échantillon fixe. |
| 1.4 | Factory | `factory/evaluate.py` | Falsification **par famille** : pour `ts_trend_carry`, le test beta < 0,15 est remplacé par « SR du signal démoyenné > 0 » (test du beta obligataire), plus SR positif sur 4 sous-périodes et coûts incluant commissions et rolls. | La stratégie `always_long` est rejetée ; trend + carry passe. |
| 1.5 | Factory | `factory/lanes.py` | Lane `ts_trend_carry_futures`, **pré-enregistrée à 3 variantes** (trend, carry, 50/50) pour éviter une grille géante. Priorité = temps de validation (2/SR)² / N_eff. | Exactement 3 essais comptés au registre. |
| 1.6 | Desk SIZE | `desk/desk.py` | Ciblage de volatilité : poids × σ_cible / σ_prévue (causal), levier plafonné, financement coûté. | MDD en replay < MDD sans overlay. Aucune donnée future (seul l'historique est lu). |
| 1.7 | Desk RISK | `desk/risk.py` | `RiskLimits` par famille : net directionnel autorisé pour `ts_trend_carry`, et nouveaux plafonds par classe d'actifs et par corrélation. | RISK évalue le portefeuille final post-scale (invariant existant). |
| 1.8 | Desk VET | `desk/desk.py` | **Hurdle** : si le rendement net attendu est inférieur au taux sans risque, `NO_TRADE`. | Un ticket `NO_TRADE` est créé quand le carry < hurdle. |

### Phase 2 : Learning qui tue vite

| # | Plane | Fichier | Changement | Test |
|---|---|---|---|---|
| 2.1 | Learning | `learning/store.py`, `factory/strategies.py` (`transition`) | t-SPRT mensuel sur les rendements shadow de chaque sleeve. S'il rejette, transition vers un état retiré avec la preuve jointe. | Crash puis replay donnent la même décision. Faux positif ≤ 5 % sur données simulées à σ mal spécifié. |
| 2.2 | Factory | `factory/strategies.py` | Registre **global** des essais (140 déjà faits en lab) alimentant le Deflated Sharpe. | Le seuil t monte avec le nombre global d'essais. |
| 2.3 | Status | `status/brief.py` | Chief Brief : temps de validation restant par stratégie, P&L net au-dessus du hurdle. | La sortie est déterministe. |

### Phase 3 : vertical marchés de prédiction (plus lourd : nouveau type d'instrument)

- Nouvel instrument **contrat binaire à règlement**. Dans le Book, le règlement (0 ou 1) est un cash-flow idempotent, et le risque de contestation UMA devient un état.
- Le Data Plane ingère des carnets L2 et des trades (miroirs GitHub d'abord, puis s3.jbecker.dev si le réseau est ouvert).
- Le module FILLS simule la tenue de marché : file d'attente, sélection adverse, rebates, frais par catégorie. Aucun fill au prix mid.
- Stratégies :
  - scanner d'arbitrage combinatoire ;
  - tenue de marché ;
  - comparaison avec une cote de référence fiable (Pinnacle) pour le sport.
- Statistiques regroupées par événement. Le test de lag (≤ 1 s) reste un sujet d'infrastructure, hors vertical.

### Phase 4 : LLM (après les phases 1 et 3)

- Dans VET : lecteur de règles de résolution. Il alimente la décote RISK, jamais la direction.
- Dans la Factory : générateur d'hypothèses qui écrit des tickets de recherche et consomme le budget d'essais.
- Masque causal (modèle, cutoff, as-of) et cache des sorties hashé pour un replay idempotent.

## Hors code (décisions du propriétaire)

1. Ouvrir le réseau de l'environnement : Binance Vision, Polymarket, Kalshi, FRED, Kenneth French, CFTC, SEC, s3.jbecker.dev.
2. Décider d'acheter des données actions sans biais de survivance (CRSP, Norgate ou Sharadar).
3. Ouvrir une mission Builder pour la Phase 1, après la réception Blue du vertical en cours (Rail B).

# Pistes à challenger : recherche croisée du 2026-09-27

Méthode : littérature récente, grands échantillons publics (Becker, 72 M de trades Kalshi ; Whelan, 300 k contrats ; arXiv 2609.23969, 5 ans de météo Kalshi), les registres des deux builders et un calcul de puissance.
Critères : un mécanisme (qui paie, et pourquoi), la puissance (nombre d'événements par an et longueur d'historique), un jeu de données frais (prior_trials = 0), des données gratuites en point-in-time, et une niche trop petite pour les institutions.

## Leçon transversale

L'edge survit là où **un prix de référence sharp externe existe** et où **la venue est retail et fine**. Là où le marché est liquide ou bien couvert par des modèles publics, il est déjà efficient :
- la catégorie Finance de Kalshi ne laisse que 0,17 pp d'écart maker/taker ;
- sur la météo, le marché bat le NBM de 10 %.

L'edge durable se trouve aussi dans le **paiement d'un service** : porter un risque, comme les dealers aux adjudications, ou fournir de la liquidité.

## Classement

| # | Piste | Mécanisme | Puissance (t attendu, 1 essai, seuil 1,96) | Données | Verdict |
|---|---|---|---|---|---|
| 1 | **Consensus sharp (Pinnacle + autres books sharp de l'Odds API, marge retirée par power/Shin) contre sport Polymarket/Kalshi**, taker seulement si écart > frais + 1 % | Les takers sport perdent (maker +1,12 % sur 43,6 M de trades) ; Pinnacle est la référence sharp | **Très forte si on juge sur la CLV** (écart entre prix d'entrée et juste valeur de clôture, σ de quelques %) : t ≈ 7 sur 200 paris. Sur le P&L seul, il faut des milliers de paris | Odds API (clé fournie, 500 req/mois : cibler 1 à 2 ligues), historique football-data + PM | **Priorité 1** : c'est H-001. KPI = CLV, confirmation P&L en forward |
| 2 | **Cycle des adjudications du Trésor** (Lou-Yan-Zhang 2013) : long IEF/TLT de la clôture du jour d'adjudication à J+N, N fixé par l'article | Capacité de risque limitée des primary dealers : le Trésor paie 9 à 18 bp par adjudication | ≈ 50 à 60 adjudications par an. En validation post-publication (2014 → 2026, environ 600 événements) : t ≈ 1,6 à 2,7 selon la décroissance | Calendrier TreasuryDirect (annoncé à l'avance, donc point-in-time) + prix ETF (relais) ou FRED | **Challenger fort**, décorrélé du reste. Jeu de données neuf |
| 3 | **Base perp-spot hors bornes de no-arbitrage** (He-Manela-Ross-von Wachter), règle et coûts retail de l'article, archives Binance 2020 → aujourd'hui | Demande de levier retail qui paie le funding ; SR 1,8 sur BTC avec coûts retail, **en déclin** | SR récent probablement ≈ 1 : sur 2,5 ans de validation, t ≈ 1,6 → **UNDERPOWERED** en historique | data.binance.vision (200, frais) | Candidat **SHADOW_DIRECT** si Blue l'adopte ; sinon, attendre |
| 4 | Maker sur sport PM/Kalshi, cotes guidées par le consensus sharp de #1 | Les makers captent l'écart des takers | Forte en markouts | Demande l'enregistreur L2 et une file d'attente (fills papier réalistes) | Étape 2, après #1 |
| — | Fin de mois pension, veille de FOMC | Flux forcés | Forward seulement : 12 et 8 événements par an, donc SPRT lent (des années) | Déjà là | Ne rien retester |

## À ne PAS tester (économise des essais : preuve externe déjà négative)

| Piste | Pourquoi |
|---|---|
| Juste valeur météo Kalshi tirée des prévisions publiques (NBM, NWS) | Le marché bat le NBM dans 6 villes sur 7 sur 5 ans (arXiv 2609.23969). Un test pré-enregistré public le rejette (Brier du mid 2 fois meilleur). Nos deux builders l'ont aussi rejetée (H-004) |
| Kalshi CPI contre le nowcast de Cleveland | Marché au moins aussi précis ; 12 événements par an seulement |
| Longshot Kalshi (acheter NO sur les contrats bon marché) | Le biais est réel, mais les makers ne gagnent que +1,6 % à 1 ¢, avant frais. Notre H-003 : binomial p = 0,71 |
| Catégorie Finance de Kalshi | Écart maker/taker de 0,17 pp : efficient |
| Funding HL contre dYdX | Jeu de données brûlé (50 essais) |

## Ce qui change la donne : le choix de la statistique

Pour le sport, juger sur la **CLV** plutôt que sur le P&L divise la variance par 10 à 30. La même preuve arrive donc en quelques centaines de paris au lieu de plusieurs milliers. La littérature (Buchdahl, Kaunitz, rapport du lab) donne une CLV qui prédit le ROI à environ 1:1.

À faire valider par Blue : la CLV comme statistique d'entrée en `CANDIDATE` et de t-SPRT, avec le P&L net comme confirmation obligatoire avant `FORWARD_PASS`.

## Sources

- [Becker, *The Microstructure of Wealth Transfer in Prediction Markets*](https://www.jbecker.dev/research/prediction-market-microstructure)
- [Whelan, *Makers and Takers: The Economics of the Kalshi Prediction Market*](https://www.karlwhelan.com/Papers/Kalshi.pdf)
- [arXiv 2609.23969, *Prediction Markets Beat the Weather Forecast*](https://arxiv.org/abs/2609.23969)
- [anaborne/kalshi-temperature-calibration (pré-enregistré, rejeté)](https://github.com/anaborne/kalshi-temperature-calibration)
- [He, Manela, Ross, von Wachter, *Fundamentals of Perpetual Futures*](https://arxiv.org/abs/2212.06888)
- [Lou, Yan, Zhang, *Anticipated and Repeated Shocks in Liquid Markets*](https://personal.lse.ac.uk/loud/Shocks.pdf)
- [Sigaux, *Trading ahead of Treasury auctions* (BCE)](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2208.en.pdf)
- [Cleveland Fed, évaluation en temps réel du nowcasting](https://www.clevelandfed.org/publications/economic-commentary/2023/ec-202306-real-time-assessment-inflation-nowcasting-cleveland-fed)

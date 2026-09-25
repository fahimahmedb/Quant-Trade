# Failles structurelles légales : ce que les gagnants exploitent vraiment (2026-09-25)

**Statut** : recherche de lab, paper/shadow uniquement. Ce rapport n'accorde aucune autorité de capital.

**Méthode** : 4 recherches parallèles (forums, dépôts GitHub, X, papiers, post-mortems). Chacune a testé ses hypothèses sur des données réelles récupérées via des miroirs GitHub. Les scripts et les résultats bruts sont dans `scripts/`. Environ 60 variantes ont été testées au total : un t de 2 à 2,5 ne vaut donc qu'indice, et la validation doit se faire sur des données futures.

**Exclu d'emblée** (illégal ou contraire aux CGU) :
- wash trading et auto-trading pour toucher des récompenses ;
- spoofing ;
- manipulation d'oracle (votes UMA) ou de marché, par exemple les attaques de type JELLY/POPCAT sur le vault HLP de Hyperliquid ;
- délit d'initié, matchs truqués, courtsiding ;
- exploitation de bugs de smart contracts ;
- sandwich MEV ;
- sybil et multi-comptes.

## 1. Le constat commun

1. **Une faille publique et facile est déjà morte, ou mangée par les frais.**
   - Arbitrage negRisk sur Polymarket : de 0 à 5,5 $ par événement après frais en 2026.
   - Latence : tuée par les frais dynamiques.
   - Effets d'entrée en indice S&P et Russell, flux des ETF à levier, effet janvier : tous décrus ou encombrés.
   - `poly-maker`, le bot de market making open source de référence, écrit lui-même dans son README : « not profitable, will lose money ».
2. **Les gagnants durables sont payés pour un service** : fournir de la liquidité, porter un risque dont les autres veulent se débarrasser, arbitrer des contrats. Ils opèrent **dans des niches trop petites pour les institutions**.
3. **Le vrai goulot n'est pas le signal.** C'est l'exécution : sélection adverse, remplissage d'une seule jambe, ADL, limites de mise, données fraîches. Plusieurs bots open source (hummingbot, polymm) ont échoué sur l'idempotence et les double-fills, précisément là où Quant est déjà solide.

## 2. Classement des opportunités (preuve × accessibilité × capacité à petite taille)

| # | Opportunité | Test du lab | Capacité | Verdict |
|---|---|---|---|---|
| 1 | **Écart de funding entre Hyperliquid et un CEX**, surtout sur les listings récents ou peu liquides | 149 coins, 2023 → 2025-05. Seuil 50 %/an : **35 %/an net** (47 → 33 → 19 % par an). Persistance jour à jour : 0,54. Signe conservé 91 % du temps au-dessus de 30 %. Coins liquides en 2025 : ≈ 1 % | 10–100 k$ (volumes de 0,05 à 5 M$/j) | **Shadow prioritaire.** Risques : ADL, liquidation d'une seule jambe, effondrement du coin (OM) |
| 2 | **Nuit précédant une réunion FOMC** (achat SPY à la clôture, vente à l'ouverture) | 79 événements. **+18 bp, t = 3,57** (net t = 3,18), positif sur les deux moitiés. La littérature le disait mort après 2015 | Grande | **Shadow immédiat** : les données sont déjà dans le repo |
| 3 | **Rééquilibrage de fin de mois des fonds de pension** (contrarien sur l'écart SPY−TLT depuis le début du mois) | 119 mois. **+26 bp net, t = 2,15**, plus fort sur 2021-26 (t = 2,20) | Grande | **Shadow immédiat.** Indicatif (≈ 20 variantes testées) |
| 4 | **Cote sharp (Pinnacle, marge retirée par méthode power/Shin) comme juste valeur, appliquée aux marchés sport de Polymarket et Kalshi** | Foot, 69 k matchs : **+4,3 à +4,8 % de ROI, t ≈ 4** au meilleur prix. La CLV prédit le ROI à ≈ 1:1. Bet365 seul : 0. Retirer la marge par la méthode multiplicative crée de faux edges | 10–50 k$ par compte. Les marchés de prédiction ne limitent pas les gagnants | **Shadow** dès qu'un flux de cotes est disponible (ressource payante) |
| 5 | **Market making en catégorie peu disputée** (météo, niches) + récompenses de liquidité + rebates | 244 k trades. Météo : **+0,57 ¢/part à 300 s, t = 8,1**. Sport, esport et crypto : le spread est entièrement repris en 1 à 5 minutes | Quelques dizaines de $/j par ville aujourd'hui | Shadow de recherche, avec juste valeur tirée des prévisions NWS |
| 6 | **Arbitrage de trust SPAC** (plancher de trust + warrants) et **merger arbitrage** | Littérature : SPAC 6-8 % (T-bill + option gratuite). Merger arb : spread médian 5,9 %, 95 % des deals conclus | 1–20 M$ | Demande un adapter EDGAR (données d'événements) |
| 7 | Short sur les déblocages de tokens / fade des nouveaux listings | Keyrock : 90 % des déblocages négatifs. 89-93 % des listings Binance 2025 négatifs | 10–300 k$ | Étude d'événements à faire (il manque un calendrier point-in-time) |
| 8 | Cash-and-carry BTC / sUSDe | 2025 : 3-8 % | Grande | **Seuil de rendement minimum**, pas un edge |
| 9 | Vente de volatilité à risque défini (index, Deribit) | Prime réelle, avec des queues de crash | Grande | Demande des données d'options |
| 10 | Récompenses de détention Polymarket (4 % APR) | Programme documenté | Discrétionnaire | Rendement de trésorerie, pas un edge |

### Testé et rejeté

| Opportunité | Résultat |
|---|---|
| Arbitrage negRisk/combinatoire sur Polymarket | Mort après frais |
| Arbitrage croisé Polymarket–Kalshi | 0 paire sur 74 avec des règles de règlement identiques : c'est du risque de base, pas un arbitrage |
| Rebond après liquidations en cascade (barres 1 h) | Négatif en 2025 |
| Turn-of-month | Pas mieux que le beta |
| Overnight seul | Net ≈ 0 |
| Flux des ETF à levier et reconstitution Russell | Encombrés |
| Pumps de listing Upbit | Course de latence perdue d'avance |
| « Bonding » : acheter à 95-99 ¢ | Espérance négative |

## 3. Ce qu'il faut construire dans Quant (ordre recommandé)

1. **Deux sleeves calendaires en shadow tout de suite**, sans nouvelle donnée. Chacune est une stratégie distincte avec son propre sleeve et sa propre attribution, jugée **uniquement sur les données futures** par le test mensuel déjà en place :
   - FOMC-eve ;
   - fin de mois pension.
2. **Sleeve funding spread HL-vs-CEX** :
   - adapters de funding horaire (un accès réseau est nécessaire) ;
   - seuils 50 %/25 % ;
   - plafond de 1 % du volume quotidien ;
   - ADL et liquidation d'une jambe modélisés comme des événements de fill explicites ;
   - une jambe par venue dans le Book.
3. **Enregistreur L2 + replay avec frais et files d'attente** pour les marchés de prédiction. Chaque fill papier porte ses markouts à 5 s, 60 s et 300 s, ainsi que frais, rebates et récompenses sur des lignes séparées. La sélection adverse devient ainsi une mesure, et non plus une hypothèse.
4. **Lane « juste valeur sharp vs marchés sport de Polymarket/Kalshi »**, avec la CLV comme KPI et comme kill-switch : promotion seulement si la CLV est supérieure à 0 avec t > 3, avant même que le P&L compte.
5. **Adapter EDGAR** (trusts SPAC, termes des deals) pour le SPAC arb et le merger arb.
6. **Règle de conformité dans VET** : refus automatique de tout ce qui figure dans la liste « exclu ». Cela comprend l'auto-trading, les marchés dont on influence l'issue et les arbitrages entre venues sans comparaison des règles de règlement clause par clause.

## 4. Décisions qui reviennent au propriétaire

- Ouvrir l'accès réseau : API de funding Hyperliquid et Bybit/Binance, Polymarket, Kalshi, EDGAR.
- Choisir un flux de cotes sportives légitime et payant (Pinnacle ferme son API ; alternatives : The Odds API, OddsPapi).
- Préciser le périmètre juridictionnel : Polymarket international est interdit aux résidents US, et Kalshi est régulé par la CFTC.

## Sources

Les sources détaillées (URLs) sont dans les rapports des agents, repris dans l'historique de la session. Les principales :
- Harvey-Mazzoleni-Melone 2025 (rééquilibrage des pensions) ;
- Kurov et al. (dérive pré-FOMC) ;
- Greenwood-Sammon (effet d'entrée au S&P) ;
- Whelan et Becker (microstructure Kalshi) ;
- Saguillo et al. (arbitrage Polymarket) ;
- Gebele et al. 2026 ;
- BIS WP 1087 (carry crypto) ;
- Keyrock (déblocages de tokens) ;
- Buchdahl, Kaunitz et al. (CLV, cotes sharp) ;
- données UKGC sur les limitations de comptes ;
- dépôts GitHub : warproxxx/poly-maker, kachence/polymm, gajesh2007/funding-arb-bot, hummingbot, marketlenstrade/polymarket-historical-data, LorenzoBaggi/funding_arb, guibvieira/freqtrade-hyperliquid-data, Mentat-Uran/ScoutFootball_for_World_Cup.

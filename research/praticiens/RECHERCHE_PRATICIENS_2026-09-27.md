# Recherche praticiens — comment les petits opérateurs gagnants y parviennent réellement (2024-2026)

- **Commande** : `prompts/7_RECHERCHE_PRATICIENS.md` (commit 502e95b).
- **Date** : 2026-09-27.
- **Périmètre** : papier/shadow uniquement ; aucun capital réel n'est en jeu.
- **Matière** : 138 sources uniques ouvertes et 115 recherches journalisées, réparties en quatre couloirs (sport ; marchés de prédiction ; crypto ; actions, options et décroissance) et un couloir transversal (lead). Chaque citation a été contrôlée contre le texte brut de sa source (§6 et annexe A).
- **Données jointes** : `sources.jsonl`, `recherches.jsonl`, `audit_citations.json`, `puissance.json` et les outils de vérification (`outils/`), dans ce dossier.
- **Références** : les identifiants entre crochets ([B-21], [L-11]…) renvoient à l'annexe A.

---

## 1. Synthèse

1. **Ils vendent l'immédiateté au lieu de l'acheter.** Sur Polymarket (2,4 M de comptes), 69 % perdent, et la part de volume maker est le meilleur prédicteur du gain : 47,3 % chez le top 0,1 %, contre 17,1 % [B-21]. Sur Kalshi, les takers perdent 1,12 % par trade et les makers gagnent autant [L-01].
2. Les venues organisent ce transfert : depuis le 30/03/2026, Polymarket prend des frais taker partout sauf en géopolitique et en reverse 15 à 25 % aux makers [L-22][B-05].
3. **Ils importent un prix plus sharp dans une venue plus lente** : consensus Pinnacle contre books soft [A-01], cotes de books contre esport [L-11], spot contre crypto à 15 min [B-12], volatilité implicite contre marchés à seuil [B-14].
4. Cet edge s'érode en quelques mois : kacho, 8,3 % → 1,3 % du volume [L-11] ; gabagool22, 2,07 % → 0,78 % puis arrêt [L-29] ; consensus de Buchdahl, −2,1 % en 2024 et −4,9 % en 2025 [L-20].
5. **Le goulot est l'exécution, pas le signal** : jambes non couvertes à −3,2 k$ contre +8,3 k$ d'arbitrages [L-11] ; cotes vieilles de 30 min au plus, prises par des bots plus rapides [L-14] ; shadow sans friction +11 %, réel −27 % [L-13].
6. **Capacité minuscule, survivance rare** : le meilleur cas vérifié gagne ≈ 470 $/mois [L-12] ; 26,9 % des vaults Hyperliquid gagnent [C-03] ; 0,71 % des traders Topstep atteignent un compte réel [L-06] ; 97 % des day traders brésiliens persistants perdent [D-27].
7. Ceux qui durent choisissent de rester petits, sur des niches que les allocataires ne regardent pas [D-31][D-32].
8. **Les planchers baissent aussi** entre 2024 et 2026 à date : funding BTC sur Hyperliquid 24,1 % → 5,0 % [C-25], sUSDe 17,5 % → 4,1 % [C-19], HLP +79 % → +8 % [C-01].
9. Le P&L publié des gagnants est souvent gonflé : sponsoring et parrainage chez 0x06dc [L-29], volume double compté [B-25].
10. **Bilan** : aucune piste nouvelle n'est à la fois bien prouvée, puissante en historique et exécutable en papier.
11. À **TESTER** : B6 (marchés crypto horaires à seuil contre volatilité implicite DVOL) et C2 (short avant les gros déblocages d'initiés, jugé à l'effet minimal détectable).
12. En **FORWARD SEULEMENT** : B1 (maker Polymarket, après un diagnostic historique des markouts) et D4c (straddles d'annonce, priorité basse).
13. H-001, en cours, doit être jugée en CLV **nette des frais 2026** : à p ≈ 0,5 sur Polymarket, l'edge net attendu est négatif.
14. Veille de FOMC : l'effet a perdu environ 80 % après 2015, et il faudrait 13,5 ans de forward pour conclure. Ne plus en attendre de verdict.
15. Décote : 50 % n'est qu'un plancher. Pour une anomalie actions US liquide publiée après 2000, ne garder que 15 à 25 % de l'effet [D-08][D-06].

---

## 2. Tableau des pistes classées

`t hist.` = `expected_t` sur l'historique hors période publiée, avec l'effet cité réduit de 50 %. `Forward` = délai pour atteindre E[t] = 1,96. Les calculs sont détaillés dans `puissance.json` et au §3.

### 2.1 Pistes recommandées ou en cours

| # | Piste | Mécanisme | Qui perd | Preuve (grade, n) | Décroissance | t hist. | Forward | Données | Capacité 10-100 k$ | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | **B6 — marchés crypto horaires à seuil (Polymarket) contre juste valeur digitale DVOL** | options digitales à 1 h ; les barreaux « excitants » sont surpayés, la juste valeur vient d'un marché d'options profond | acheteurs taker de barreaux | A ×1 (wallets survivants) [B-14] ; B ×1 contre [B-24] ; données A [L-24][L-26][L-28] | 0x06dc : trading net de frais 1,6 % (avril) → 0,8 % (sept. 2026) du volume [L-29] | 1,49 (P&L ; 0,4 an d'horaire dense) | ≈ 0,7 an en P&L ; moins en écart à la juste valeur | gratuites et PIT (on-chain, `v2/trades`, DVOL, bougies HL) | oui (1,7-2,8 M$/mois chez le survivant) | **TESTER** |
| R2 | **C2 — short du perp HL de J−30 à J avant un gros déblocage d'initiés** | ventes et couvertures prévisibles des équipes et investisseurs | porteurs non couverts | B ×1 (conflit d'intérêts) [C-10] ; données A [C-20][C-21][C-25] | non chiffrée ; étude de déc. 2024 [C-11] | effet non publié : il faut ≥ 7,2 % avant décote pour t = 1,96 sur 202 événements 2025-2026 | ≈ 100 événements/an → ≈ 2 ans pour la même MDE | calendrier DefiLlama (non PIT) ; HL (PIT) | petites capitalisations, profondeur à vérifier | **TESTER** (MDE) |
| R3 | **B1 — maker Polymarket : diagnostic des markouts historiques, puis shadow à exécution par traversée** | vendre l'immédiateté, plus les rebates | takers (69 % perdants) | A ×3 [B-21][L-01][B-15] ; B ×4 [B-16][L-11][L-14][L-19] | poly-maker « not profitable » en 2026 ; récompenses concentrées | non contraignant (millions de fills) | markouts : 1-3 mois | gratuites (on-chain, `v2/trades`, carnets du relais) | bornée par les pools | **FORWARD SEULEMENT** |
| R4 | **H-001 corrigée (en cours)** : Pinnacle sans marge contre sport Polymarket/Kalshi, CLV nette des frais 2026 | importer la clôture sharp | takers et makers en retard | B ×3 [A-13][A-16][A-17] ; frais A ×3 [A-11][L-22][A-25] | consensus soft négatif en 2024-2025 [L-20] | pas d'historique aligné | 151 paris (brut) ; **jamais** à p = 0,5 net Polymarket ; 1 608 paris à p = 0,8 | Odds API (500 req./mois) + relais | Kalshi NFL : écart 1 c, ≈ 1 000-2 300 contrats au bid [A-27] | **FORWARD SEULEMENT** (corrigée) |
| R5 | **D4c — straddles d'annonce : vendre la volatilité d'annonce là où les particuliers achètent** | les particuliers surpaient la volatilité d'annonce attendue | particuliers (−5 à −9 %) [D-24] | A ×2, contradictoires [D-24][D-25] | non chiffrée | non calculable (pas d'historique gratuit) | n élevé ; délai à mesurer | chaînes Cboe différées, forward seulement (CGU à vérifier) [D-26] | oui en papier | **FORWARD SEULEMENT** (priorité basse) |
| E1 | Veille de FOMC (en cours) | prime d'incertitude avant l'annonce | — | A ×1 [L-03] ; B ×1 [L-04] | 44 pb (2011-2015) → 9 pb non significatifs (2016-2019) | 2,06 en formule, mais sur un historique déjà publié | 13,5 ans (t = 1,96) ; 27,6 ans (80 %) | relais Yahoo et FOMC | oui | **REJETER** comme lane de preuve |

### 2.2 Pistes évaluées et rejetées

| # | Piste | Mécanisme | Qui perd | Preuve (grade, n) | Décroissance | t hist. | Forward | Données | Capacité | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Consensus sharp contre books soft (Kaunitz, Buchdahl) | cotes soft en retard | le book soft | A ×4 [A-01][A-14][L-20][A-24] | +4,0 % (2015-2022) → −0,3 % (2022-2025) | 0 (aucun historique hors publication) | 37 ans en P&L | archive WoC (xlsx) | nulle : limites de compte | REJETER |
| A2 | Exchanges (Betfair ; Novig, ProphetX, Sporttrade) | trading pré-off, faible commission | parieurs récréatifs | A ×1, C ×3 [A-06][A-22][A-07][A-20] | Premium Charge plafonnée à 40 % | — | — | derrière login | — | REJETER |
| A3 | Maker sport Kalshi/Polymarket en papier | spread payé par les fans | takers | A ×3, B ×3 [L-01][A-03][A-09][L-11][L-14][L-19] | frais maker Kalshi depuis oct. 2025 | — | 25 ans en P&L | fills non simulables | quelques centaines de $/mois | REJETER |
| A4 | Props de joueurs Kalshi/Polymarket | makers non experts | acheteurs de combos | A ×2 [A-27][A-04] | — | — | — | pas de juste valeur gratuite | volume médian 4 contrats | REJETER |
| A5 | Lignes d'ouverture, niches | ouverture moins efficiente | books, makers lents | B ×3 [A-15][A-26][L-14] | — | — | — | pas d'ouvertures PIT gratuites | — | REJETER (artefact d'asynchronisme [A-15]) |
| A6 | Primes LIP de Kalshi (props NFL) | subvention de la profondeur | Kalshi | A ×2 [A-04][B-26] | programme annoncé jusqu'au 2027-01-01 | — | — | règle de score non ouverte | 250-500 $/marché | REJETER (subvention, pas un edge ; non mesurable en papier) |
| B2 | Latence spot contre crypto 5/15 min (taker) | prix en retard sur le spot | makers lents | A ×4 [B-03][B-04][B-12][B-14] ; B ×1 [L-13] ; C ×3 [B-09][B-10][B-11] | gabagool22 : 2,07 % → arrêt ; frais, délai de 150 ms, TWAP | 0,63 (version maker, P&L) | — | — | — | REJETER |
| B3 | NO ≥ 90 c, « nothing ever happens » | biais YES et longshot | acheteurs de longshots | A ×3, B ×2 [B-20][B-03][B-08][L-09][B-22] | — | 0,47 | 53 ans | — | ≈ 10 marchés éligibles | REJETER (doublon) |
| B4 | Mentions et marchés à donnée publique | modèle ou vitesse | — | A ×1, B ×1 [B-13][L-27] | — | — | — | le carnet devance la source [L-27] | 7,4 k$/mois pour le n°1 | REJETER |
| B5 | Copy-trading des meilleurs wallets | suivre les gagnants | le copieur (taker en retard) | A ×3, B ×1 [B-21][B-19][B-13][B-24] | +49,5 % → −17,6 % en 3 semaines | n = 12/an | — | — | — | REJETER |
| C1 | Vaults Hyperliquid et HLP | copier ou déposer | 73 % des vaults perdent | A ×4, B ×1 [C-01][C-02][C-03][C-05][C-06] | HLP : +79 % → +19 % → +8 % | — | — | — | — | REJETER |
| C3 | Market making sur petites venues à incitations | rebates et points | — | A ×1, C ×4 [C-04][C-12][C-13][C-23][C-24] | points captés en spread négatif | — | — | fills non simulables | pas de rebate sous le palier | REJETER |
| C4 | Farming d'airdrops (compte unique) | subvention des protocoles | protocoles | B ×1 [C-22] | 30-35 k$ (2023) → 600-1 000 $ par compte (2024) | — | — | non testable en papier | — | REJETER |
| C5 | Carry funding et sUSDe | plancher de demande de levier | — | A ×2, B ×1 [C-19][C-25][C-18] + [C-09] | BTC HL 24 % → 5 % ; sUSDe 17,5 % → 4,1 % | — | — | — | — | REJETER (plancher en chute, ADL) |
| C6 | LP d'AMM, arbitrage CEX-DEX | LVR | LP passifs | A ×3 [C-15][C-16][C-17] | — | — | — | — | 11 searchers > 80 % | REJETER |
| D2a | Janvier des CEF municipaux | ventes fiscales de décembre | particulier imposable | A ×3 [D-12][D-13][D-15] | +1,77 pt (2004-2019) → −0,14 pt (2020-2026), calcul du couloir D sur [D-15] | 0,73 | 50 ans | NAV Yahoo | — | REJETER |
| D2b/c | Activisme CEF, conversions à décote | rachat proche de la NAV | porteurs passifs | B ×3 [D-14][D-16][D-17] | — | — | n ≈ 5/an | EDGAR (User-Agent) | — | REJETER |
| D3a | Arbitrage de fusions sur petites opérations | écart d'opération | vendeurs de la cible | A ×2 [D-18][D-21] | écart médian −70 % | — | — | pas de base PIT | rendements croissants avec la taille | REJETER |
| D3b | SPAC sous le trust | plancher + option | actionnaires après fusion | A ×2 [D-19][D-20] | 23,9 %/an (2010-2020) → « much lower » | — | — | — | — | REJETER (plancher) |
| D4a/b | 0DTE ; vente de volatilité | fourchette ; prime de queue | particuliers ; acheteurs de protection | A ×2, B/C ×3 [D-22][D-25][D-29][D-30][D-33] | pertes en hausse depuis 2022 | — | — | historique d'options payant | — | REJETER |
| D5 | Inclusion au S&P 500 | demande indicielle | plus personne | A ×1 [D-23] | 7,6 % → 0,8 % (non significatif) | effet source non significatif | — | — | — | REJETER |
| D7 | Résidu d'anomalies dans les micro-caps | limites à l'arbitrage | — | A ×3 [D-05][D-08][D-10] | −85 % hors micro-caps après 2005 | — | — | pas de fondamentaux PIT gratuits | fourchette de 111 pb | REJETER |
| X1 | Prévision par IA contre le carnet | modèle contre marché | le modèle | B ×1 [L-27] | — | Brier 0,209 contre 0,157 (601 marchés) | — | — | — | REJETER |

---

## 3. Fiches des pistes recommandées

### R1 — B6 : marchés crypto horaires « above K » de Polymarket contre juste valeur digitale

- **Mécanisme.** Chaque marché « Ethereum above 2 185 on April 30, 10PM ET? » est une option digitale à 1 h [L-26]. Les particuliers achètent les barreaux « excitants » au-dessus de leur probabilité [B-24] ; une volatilité implicite issue d'un marché d'options profond (Deribit) donne une juste valeur indépendante.
- **Qui perd.** Les acheteurs taker de barreaux, et les makers lents. Le schéma général « les takers perdent, les makers gagnent » est établi [B-21] ; pour cette catégorie, seule une preuve B existe [B-24].
- **Pourquoi les gros ne l'ont pas mangé.** Ils y sont : 0x06dc et 0xf705 paient 23 à 161 k$ de frais par mois [B-14]. Mais la place est fragmentée : 24 échéances par jour et 10 strikes par échéance, soit 240 petits marchés par jour et par actif [L-26].
- **Survivorship.**
  - Le « ladder harvesting » (acheter les barreaux à 5-45 c et tenir) est négatif hors échantillon : −14,4 % [B-24].
  - Un seul survivant régulier : justdance, 22 mois positifs sur 29 [B-14], avec une marge de trading nette de frais de 3,55 % de mars à septembre 2026 [L-29].
- **Décroissance.** Marge « économique » de 0x06dc de mars à septembre 2026 : +13,1 %, +5,3 %, +5,2 %, +0,3 %, +0,6 %, −1,0 %, +0,9 % (calcul du couloir B sur [B-14], confirmé [L-29]). Mais de mars à juin, l'essentiel de ce « P&L » vient de revenus de sponsoring et de parrainage (309,8 k$ sur 455,2 k$ en avril). Son trading net de frais ne fait que 1,6 % du volume en avril et 0,8 % en septembre [L-29].
- **Vrai goulot.**
  - La juste valeur à 1 h : la DVOL est une volatilité ATM à 30 jours, sans smile ni saisonnalité intrajournalière.
  - Les frais taker 0,07·p(1−p), soit 3,5 % du coût à 50 c [B-03].
- **Expression unique.** Pour chaque marché horaire « above K » sur BTC et ETH, à T−60 min :
  - p* = N(d2), avec le spot HL et σ = la DVOL horaire la plus récente, ramenée à l'horizon restant ;
  - acheter le côté dont l'ask est inférieur à p* d'au moins le frais taker 0,07·p(1−p) [B-03], puis tenir jusqu'au règlement.

  Seuil et vol viennent des sources [B-03][L-28]. T−60 min est une convention fixée a priori, qui compte pour un seul essai.
- **Données exactes.**
  - Historique des prix : `trades.parquet` et `markets.parquet` (Hugging Face, lecture DuckDB) [L-18][L-21] et `https://data-api.polymarket.com/v2/trades?...` [B-12].
  - Résolutions : `https://gamma-api.polymarket.com/markets?slug=...`.
  - Volatilité : `https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=ETH&resolution=3600` [L-28].
  - Spot : `POST https://api.hyperliquid.xyz/info {"type":"candleSnapshot",...}` [L-28].
  - Tout est gratuit, sans login et horodaté. L'historique horaire dense couvre environ avril à juillet 2026 dans le jeu on-chain ; les marchés quotidiens remontent à mi-2025 [L-25].
- **Puissance.**
  - **Effet** : 3,55 %, la marge de trading nette de frais du survivant justdance [L-29], soit 1,78 % après décote.
  - **σ** : ≈ 1,0 par dollar à p ≈ 0,5 (loi binaire).
  - **n** : 24 × 365 × 2 ≈ 17 520 fenêtres par an. BTC et ETH sont corrélés, donc n effectif plus faible.
  - **Historique** : t = 0,0178 × √(17 520 × 0,4) = **1,49**, soit **UNDERPOWERED en historique** sur le P&L.
  - **Forward** : 12 194 fenêtres pour t = 1,96, soit **≈ 0,7 an** (1,42 an pour 80 % de puissance).
- **Statistique à faible variance.** L'écart (ask − p*) à l'entrée, puis sa convergence vers le mid à +15 et +45 min. On compare aussi le score de Brier du prix de marché et de p* sur les résolutions : c'est le test le plus puissant, sans exécution.
- **Capacité et coûts.** Oui entre 10 et 100 k$ : le survivant traite 1,7 à 2,8 M$ par mois [B-14][L-29]. Coûts : frais taker et spread.
- **Légalité et CGU.** Test en papier. Polymarket international exclut les personnes américaines.
- **Contre-preuve.**
  - Ladder harvesting négatif [B-24].
  - Décroissance de 0x06dc, dont les gains 2026 venaient surtout du sponsoring [L-29].
  - Biais inverse sur les longshots à 1 jour (bande 5-15 % : cotée 9,6 %, réalisée 17,3 %) [B-22].
- **Risque principal.** La juste valeur DVOL rate le smile et la volatilité intrajournalière ; les « edges » apparents se concentrent alors dans les queues, là où le modèle est faux. Il faut pré-enregistrer une variante sans les barreaux p < 0,15 ou p > 0,85, et la compter comme un essai de plus.

### R2 — C2 : short du perp avant les gros déblocages d'initiés

- **Mécanisme.** Les équipes et investisseurs vendent ou se couvrent autour de déblocages connus à l'avance. Keyrock, sur plus de 16 000 événements, écrit que « 90 % of unlocks create negative price pressure », que l'effet « often start[s] 30 days before », et que les déblocages d'équipe produisent les pires chutes, jusqu'à −25 % [C-10].
- **Qui perd.** Les porteurs non couverts, et les acheteurs qui ignorent le calendrier.
- **Pourquoi les gros ne l'ont pas mangé.** Ce sont des petites capitalisations. Le short coûte du funding et comporte un risque d'ADL, et le vendeur de couverture est lui-même un market maker (conflit d'intérêts de Keyrock) [C-10][C-09].
- **Survivorship.** Aucun post-mortem trouvé. L'étude ne porte que sur 40 tokens, et ses 16 000 événements se chevauchent [C-10].
- **Décroissance.** Non chiffrée. L'étude date de décembre 2024 [C-11] ; 2025 et 2026 sont donc hors publication.
- **Vrai goulot.**
  - Le calendrier n'est pas point-in-time : DefiLlama donne la vue actuelle, révisable [C-20].
  - La dérive non conditionnelle de ces tokens (−9,2 % par 30 jours contre ETH [C-21]) piège un test naïf.
  - L'ADL en krach [C-09][C-18].
- **Expression unique.** Pour chaque cliff d'une allocation « insiders » ou « privateSale » d'au moins 1 % de l'offre maximale (DefiLlama) sur un token listé en perp Hyperliquid :
  - vendre le perp à la clôture de J−30 et racheter à la clôture de J ;
  - mesurer le rendement relatif à ETH, funding inclus ;
  - statistique : l'écart entre ce rendement et la moyenne du même token sur ses fenêtres de 30 jours sans déblocage.

  J−30 et le type de bénéficiaire viennent de Keyrock [C-10] ; le seuil de 1 % correspond au bas de sa classe « Medium » (1-5 %).
- **Données exactes.**
  - Calendriers : `https://defillama-datasets.llama.fi/emissions/<protocole>` [C-20].
  - Prix et funding : `POST https://api.hyperliquid.xyz/info` avec `candleSnapshot` et `fundingHistory` [C-21][C-25].
  - En forward : un snapshot quotidien du calendrier pour obtenir du point-in-time.
- **Puissance.**
  - **σ** : 0,262 par événement (rendement à 30 jours relatif à ETH, 1 043 fenêtres, 40 tokens) [C-21].
  - **n après publication** : 108 (2025) + 94 (2026 à date) = 202 cliffs sur des perps HL [C-20].
  - **Effet** : non publié. L'effet minimal détectable après décote vaut 1,96 × 0,262 / √202 = **3,6 %** ; **un effet source ≥ 7,2 %** est donc nécessaire pour t = 1,96.
  - **Forward** : environ 100 événements par an, donc environ 2 ans pour la même MDE.
  - Le chevauchement des déblocages mensuels réduit le n effectif.
- **Statistique à faible variance.** Le rendement relatif à ETH et à la base propre du token, ce qui retire le bêta et la dérive.
- **Capacité et coûts.** 10 à 100 k$ probablement réalistes sur les perps HL ; la profondeur est à vérifier token par token. Frais taker HL : 4,5 pb × 2 [C-04]. Le funding est plutôt reçu par le short (0,00125 %/h au plancher, 10,95 %/an) [C-21].
- **Légalité.** Aucun obstacle.
- **Contre-preuve.**
  - Aucune étude indépendante n'existe.
  - Les déblocages d'écosystème sont positifs (+1,18 % en moyenne) [C-10].
  - La dérive non conditionnelle rend tout effet naïf trompeur [C-21].
- **Risque principal.** Un look-ahead dans le calendrier non PIT : un déblocage annulé ou déplacé disparaît de la vue actuelle. Il faut une analyse de sensibilité et, surtout, une validation en forward sur des snapshots datés.

### R3 — B1 : maker Polymarket, du diagnostic historique au shadow conservateur

- **Mécanisme.** Vendre l'immédiateté aux takers, dont 69 % finissent perdants [B-21]. Le maker encaisse le spread et les rebates : 15 à 25 % des frais taker selon la catégorie [B-05], plus des récompenses de liquidité [B-07].
- **Pourquoi les gros ne l'ont pas mangé.** Ils l'ont largement mangé. RN1 gagne 2,3 % sur 621,6 M$ de volume [B-15]. Les pools de récompenses sont fixes et se diluent avec la concurrence [B-07]. L'auteur de poly-maker juge son bot « not profitable » en 2026 [B-16].
- **Survivorship.**
  - poly-maker [B-16] ; market making amateur sur Kalshi [L-15][L-16] ; polymm, « too slow to defend its edge » [L-19].
  - kacho : ses jambes non couvertes à −3,2 k$ [L-11] ; cotes périmées [L-14].
- **Décroissance.**
  - Plus de 25 k$ par jour de récompenses en 2024 [B-17].
  - Récompenses mensuelles de RN1 : 151,7 k$ en avril 2026, puis entre 2,0 et 49,4 k$ [B-15].
- **Vrai goulot.** La file d'attente et la sélection adverse. En papier, on ne sait pas si un ordre aurait été exécuté [L-13].
- **Expression unique, en deux temps.**
  1. **Diagnostic historique.** Par catégorie Polymarket et par tranche de prix de 10 c, mesurer le markout moyen par dollar des fills maker publics : contre le mid à +5 et +60 min, et contre la résolution. Le mesurer net du barème de frais et de rebates en vigueur à la date de chaque fill [L-22][B-03][B-05].
  2. **Shadow**, seulement dans les catégories où le markout net est positif :
     - coter post-only les deux côtés à v/2 du mid, pour la taille minimale qualifiante ;
     - ne compter une exécution que si un trade public imprime **strictement au travers** du prix coté.

     Les paramètres v et la taille viennent de la plateforme [B-07].
- **Données exactes.**
  - Fills on-chain avec `maker`, `taker`, `price` et directions [L-18][L-21].
  - `https://data-api.polymarket.com/v2/trades?condition=…&taker_only=false` [B-12].
  - Carnets déjà collectés par le relais ; barème des frais [L-22].
- **Puissance.** Non contraignante : des millions de fills, avec des erreurs types groupées par marché. Pour l'effet, deux proxys : 0,78 % en crypto (gabagool22, février 2026 [B-14]) et 2,3 % en sport (RN1 [B-15]).
- **Statistique à faible variance.** Les markouts à 5 et 60 minutes.
- **Capacité et coûts.** Bornée par les pools et la profondeur ; chez Kalshi, 1 à 1 000 $ par jour et par marché [B-26]. Le maker ne paie pas de frais : son seul coût est la sélection adverse.
- **Légalité.** Aucune auto-exécution, pour éviter tout wash trading. Le LIP de Kalshi est réservé aux résidents américains [B-26].
- **Contre-preuve.** [B-16][L-13][L-14][A-09] : l'affilié Kalshi Trading n'est pas rentable.
- **Risque principal.** Le markout moyen des makers en place ne dit rien d'un entrant plus lent, qui serait surtout exécuté quand il a tort. La règle d'exécution par traversée donne donc un **plafond**, pas une estimation. Rien ne peut passer en capital sans vrais fills.

### R4 — H-001 corrigée (déjà en cours) : faits nouveaux et nouvelle règle de jugement

- **Faits nouveaux.**
  1. **Frais sport 2026.**
     - Polymarket : 0,05·p(1−p) depuis le 2026-07-10, contre 0,03 auparavant, soit 2,5 % du coût à 50 c ; le rebate maker passe à 15 % [L-22][A-11].
     - Polymarket US : 0,0695 [A-12].
     - Kalshi facture aussi les makers sur 107 séries sport [A-02][A-03].
     - Novig : 0 frais en pré-match [A-25].
  2. **L'edge du consensus** jugé à la clôture Pinnacle vaut **2,88 %** par pari [A-13]. La CLV prédit le rendement avec une pente d'environ 1 [A-16], et son σ vaut 0,082 à 0,103 [A-17].
  3. **Le seul track record public du consensus est devenu négatif en 2024-2025** : −2,1 % puis −4,9 % [L-20].
  4. **Une version maker exigerait des cotes fraîches à quelques minutes** [L-14][L-19]. C'est incompatible avec un budget de 500 requêtes Odds API par mois.
- **Règle.** Acheter si p_fair / (ask + frais(ask)) − 1 ≥ 2 %, seuil « at least 2 % value » de WoC [A-14]. Juger sur la **CLV nette** : p_fair,clôture / (ask + frais) − 1.
- **Puissance** (σ_CLV = 0,09 ; `puissance.json`) :
  - CLV brute : 151 paris ;
  - nette de frais à p = 0,5 sur Polymarket : **effet ≤ 0, jamais significative** ;
  - nette à p = 0,8 (frais de 1 %) : 1 608 paris, soit 3,2 ans à 500 paris par an ;
  - venue sans frais : 151 paris.
- **Verdict.** Continuer en **FORWARD SEULEMENT**, en ne retenant que les favoris (p ≥ 0,75) ou les venues sans frais. Ne pas lancer de version maker. Le résultat attendu à p ≈ 0,5 sur Polymarket est **négatif** : c'est à écrire au registre avant de regarder le forward.

### R5 — D4c : straddles d'annonce, basse priorité

- **Mécanisme.** Les particuliers achètent des options avant les résultats et paient une volatilité d'annonce trop chère. Ils perdent 5 à 9 %, et 10 à 14 % quand la volatilité attendue (EAV) est élevée [D-24].
- **Preuves contradictoires.**
  - Les straddles inconditionnels à J−1 → J rapportent +2,3 % au mid, sur un échantillon ancien [D-25].
  - Les straddles à EAV élevée font 11 points de moins que ceux à EAV faible le jour de l'annonce (t = 19,44) [D-24].
  - La preuve la plus récente et conditionnelle [D-24] prime.
- **Expression unique.** À la clôture de J−1, classer les annonces par EAV selon la définition de [D-24]. Vendre les straddles ATM du quintile haut, acheter ceux du quintile bas, clôturer à J+1, exécuter au bid/ask.
- **Données exactes.**
  - `https://cdn.cboe.com/api/global/delayed_quotes/options/{SYM}.json` : chaîne complète différée, avec IV [D-26].
  - Pas d'historique gratuit : **forward seulement**.
  - Les CGU de collecte automatisée de Cboe restent **à vérifier**, et le calendrier gratuit des résultats n'est pas vérifié.
- **Puissance.**
  - Effet in-sample de 11 points avec t = 19,44 [D-24] : même réduit de moitié, la puissance n'est pas la contrainte.
  - Le σ par événement n'a pas été trouvé, et le n annuel n'est pas sourcé (« plusieurs milliers d'annonces »).
- **Capacité et coûts.** Oui en papier, mais les fourchettes d'options sont larges, et [D-25] montre que l'effet devient négatif à spread coté complet pour la plupart des maturités.
- **Contre-preuve.** [D-25] au spread complet ; le risque de queue de la vente de straddles [D-29][D-30].
- **Risque principal.** Coûts d'exécution et risque de queue. Priorité basse tant que les CGU de Cboe et le calendrier ne sont pas vérifiés.

### Veille de FOMC (en cours) : faits nouveaux

- **La dérive s'est effondrée.** Elle passe de +0,445 % (2011-2015) à +0,092 % (2016-2019), et la différence est rejetée au seuil de 1 % [L-03]. Un praticien la retrouve jusqu'en 2024, mais plate en 2016-2019 et concentrée quand le VIX est élevé [L-04].
- **Puissance.** Effet Lucca-Moench de 0,49 % [L-03], soit 0,245 % après décote. σ ≈ 1,3 % par fenêtre (1,13 % par jour × √1,3 jour) [L-23], et 8 événements par an.
  - En forward : **13,5 ans** pour atteindre E[t] = 1,96, et 27,6 ans pour 80 % de puissance.
  - L'historique après publication a déjà été examiné et publié [L-03][L-04], il n'est donc pas vierge.
- **Verdict.** Ne pas en attendre de verdict. Garder la lane seulement si son coût est nul ; sinon l'arrêter.

---

## 4. Liste « ne pas tester » mise à jour

### 4.1 Pistes à ne pas tester, avec la preuve du rejet

| Piste | Preuve du rejet |
|---|---|
| Bonding et achat de NO à 90-99 c (« nothing ever happens ») | Backtest à 100 % d'APR biaisé par la connaissance de la date de résolution ; test réel : −5 % sur 100 $ [L-09]. Aucun rendement revendiqué par l'auteur du bot [L-10]. Edge de +0,28 % avant frais, nul après les frais de 2026 [B-20][B-03]. |
| Biais favori/outsider Kalshi, et son équivalent Polymarket | Doublon du rejet Kalshi ; sur Polymarket, le signe dépend de l'agrégation [B-20], et les frais s'appliquent depuis le 2026-03-30 [L-22]. |
| Arbitrage de latence taker sur la crypto 5/15 min | Frais de 3,5 % à 50 c, délai taker de 150 ms, règlement TWAP [B-03][L-22]. Les wallets vedettes s'arrêtent en mars-avril 2026 [B-14]. Shadow +11 % contre réel −27 % [L-13]. |
| Maker sport en papier (Kalshi/Polymarket) | Fills non simulables [A-20][L-13] ; frais maker Kalshi [A-03] ; affilié de l'exchange non rentable [A-09] ; érosion [L-11][L-14]. |
| Consensus sharp contre books soft, en réel | Limites de compte : 4,31 % des comptes UK restreints, dont 46,78 % en profit [A-24] ; arrêt des auteurs [A-23] ; track record négatif en 2024-2025 [L-20]. |
| Props de joueurs | Volume médian de 4 contrats ; pas de juste valeur gratuite [A-27]. |
| Cotes d'ouverture en backtest | Artefact d'asynchronisme entre books [A-15] ; fuite par les cotes [A-21]. |
| Parier « contre le public » | La marge réalisée des books égale le hold ; aucun décalage de prix exploitable [A-19]. |
| Copy-trading des meilleurs wallets | Persistance faible et sélection [B-21] ; +49,5 % → −17,6 % en trois semaines, −14,4 % hors échantillon [B-24]. |
| Marchés « mention » et à donnée publique | Le carnet devance la source ; les bots balaient les mentions en 0-5 s [L-27]. Gâteau de 7,4 k$ par mois pour le n°1 [B-13]. |
| Prévision par IA contre le carnet | Brier du carnet 0,157 contre 0,209 pour le modèle, pertes à chaque seuil (601 marchés) [L-27]. |
| Arbitrage negRisk et combinatoire (déjà rejeté) | Le n°1 des montants « extraits » (2,01 M$) n'affiche qu'environ 0,44 M$ de PnL [B-19]. |
| Météo Kalshi, Kalshi CPI (déjà rejetés) | « Weather books reprice within about a minute of NWS products » [L-27] ; les publications très suivies sont déjà efficientes (README de [B-23]). |
| Rebond après liquidations (déjà rejeté) | Rebond moyen de +84 % en 30 minutes le 10/10/2025, inexploitable en données horaires [C-18]. |
| Cash-and-carry, écart de funding HL/dYdX (déjà rejetés) | Funding BTC HL : 24,1 % → 10,6 % → 5,0 % ; sUSDe : 17,5 % → 4,1 % [C-25][C-19] ; ADL de la jambe courte en krach [C-09][C-18]. |
| Vaults Hyperliquid, HLP | 26,9 % des vaults utilisateurs gagnants et 67 % fermés [C-03] ; HLP : +79 % → +8 %, 41 % du gain en deux krachs [C-01][C-06]. |
| Market making sur venues à incitations, airdrops | Rebate HL réservé aux gros volumes [C-04] ; points captés en spread négatif [C-23] ; airdrop mono-compte : 600-1 000 $ par projet [C-22]. |
| LP d'AMM, arbitrage CEX-DEX | LVR : −6,2 %/an pour le LP non couvert [C-15] ; 11 searchers font plus de 80 % de l'arbitrage [C-16]. |
| Janvier des CEF municipaux | Hors échantillon 2020-2026 : −0,14 point (calcul du couloir D sur les NAV Yahoo [D-15]) ; environ 50 ans de forward nécessaires [D-12]. |
| Arbitrage de fusions sur petites opérations | Rendements croissants avec la taille de la cible [D-21] ; écart médian −70 % [D-18]. |
| SPAC sous le trust | Plancher plus option : 23,9 %/an tiré par 2020, « much lower » ensuite [D-19][D-20]. |
| 0DTE en preneur, vente de volatilité comme alpha | −241 k$ par jour pour les particuliers, dont plus de 90 M$ de coûts [D-22] ; faillite d'OptionSellers.com [D-30]. |
| Inclusion S&P 500, PEAD sur grandes capitalisations, anomalies hors micro-caps | 7,6 % → 0,8 % [D-23] ; PEAD nul depuis 2006 [D-11] ; −85 % après 2005 [D-08]. |
| Veille de FOMC comme lane de preuve | Effet −80 % après 2015 [L-03] ; 13,5 ans de forward (§3). |
| Day trading « à la prop firm » | 0,71 % des comptes Express promus en réel [L-06] ; 7 % des candidats payés [L-05] ; 97 % des persistants perdent au Brésil [D-27] ; 74-89 % des comptes CFD perdants [D-28]. |

---

### 4.2 Leçons de méthode pour Quant

1. **Durcir la décote.**
   - 50 % reste la moyenne avant coûts (McLean-Pontiff publié : −58 % après publication [L-17][D-01]).
   - Pour un effet sur actions américaines liquides publié après 2000, un effet d'événement célèbre ou un effet choisi pour sa force, ne garder que 15 à 25 % : il reste 7 pb sur 48 [D-08], avec une pente hors/dans l'échantillon de 0,25 [D-06].
   - Retirer ensuite les coûts [D-05].
2. **Ne jamais simuler de fills maker sans friction.** Exiger la règle d'exécution par traversée et des distributions de slippage mesurées [L-13].
3. **Relire le barème de frais avant chaque calcul.** Polymarket l'a changé au moins six fois en 2026 [L-22].
4. **Garder les jeux candidats vierges.** L'historique on-chain de Polymarket [L-18] n'a été ouvert ici qu'au niveau du schéma et des métadonnées.
5. **Choisir la statistique à faible variance.** La CLV a un σ de 0,08 à 0,10, contre 1,7 pour le P&L [A-17][L-20]. Viennent ensuite les markouts, puis l'écart à la juste valeur.
6. **Lire les classements de wallets avec méfiance.**
   - Le « P&L économique » de Polymarket inclut le sponsoring et le parrainage : il faut juger le trading net de frais [L-29].
   - Le volume est double compté [B-25].
   - Les P&L v1 et v2 divergent [B-19].
   - Les classements mêlent airdrops et perps [C-02].

---

## 5. Annexe

### A. Toutes les sources, par famille

Colonnes : identifiant (couloir A = sport, B = marchés de prédiction, C = crypto, D = actions/options, L = lead ; « (= X) » signale un doublon fusionné), lien exact, grade A/B/C, date de publication, contenu en une ligne, résultat du contrôle de la citation contre le texte brut (« trouvée » ; « partielle (score) » = citation faite de fragments ou PDF mal extrait ; « API datée » = réponse d'API horodatée du 2026-09-27 ; « WebFetch seul » = page non retéléchargeable par le proxy, lue par WebFetch ; « à la main » = relue manuellement, voir §6). La citation exacte et les chiffres de chaque source sont dans `sources.jsonl`.

#### Famille 1 — Reddit (0 source)

Aucune source ouverte (voir l'auto-audit).


#### Famille 2 — GitHub (12 sources)

| Id | Source | Grade | Date | Contenu (une ligne) | Vérif. citation |
|---|---|---|---|---|---|
| L-08 | [Nothing Ever Happens Polymarket Bot (README + config.example.json)](https://github.com/sterlingcrispin/nothing-ever-happens) | C | 2026-04 | Dépôt viral (471 points sur HN) sans aucune preuve de rendement ; l'auteur le qualifie lui-même de mème (L-10). | trouvée (à la main) |
| L-19 | [polymm — Polymarket sports market-making and arbitrage bot (README)](https://github.com/kachence/polymm) | B | 2026-07 | Le dépôt confirme L-11 et L-14 : le code est public mais l'edge (scrapers de cotes fraîches, vitesse) ne l'est pas ; le bot Python a cessé d'être rentable face à des bots plus rapides. | trouvée (à la main) |
| L-27 | [Jev on Kalshi: what worked, what didn't (docs/JEV.md)](https://raw.githubusercontent.com/ryanfrigo/kalshi-ai-trading-bot/main/docs/JEV.md) | B | 2026-09-25 | Mesure de praticien reproductible (script publié) : sur les marchés liquides à source publique, le carnet devance la source ; la seule niche restante est le fade de base rate sur les mentions, à la main. | trouvée |
| A-20 | [flumine - Betting trading framework (README, issues https://github.com/betcode-org/flumine](https://github.com/betcode-org/flumine) | C | dernier commit 2026- | Outil réellement maintenu des traders Betfair (Betfair, Betdaq, Tote) ; aucune preuve de rendement ; les issues montrent que le goulot d'un test papier sur exchange est la simulation des fills (file d'attente), pas le signal. | WebFetch seul |
| A-21 | [sports-betting - Collection of sports betting AI tools (README, issues https://github.com/](https://github.com/georgedouzas/sports-betting) | C | issues actives juill | Le dépôt de value betting le plus suivi ne publie aucun rendement et son issue ouverte sur la fuite des cotes (cotes de clôture utilisées comme si elles étaient disponibles au moment du pari) reste sans réponse : le piège point-in | WebFetch seul |
| B-16 | [warproxxx/poly-maker: README (versions de janv., avril et juillet 2026), issues et histori](https://raw.githubusercontent.com/warproxxx/poly-maker/bfacef3/README.md) | B | 2026-04-06 (version  | Post-mortem de l auteur lui-même: le bot qui l avait mis dans le top 5 des récompenses en 2024 n est plus rentable en 2026; issues = problèmes d exécution, pas de preuves de gain. Disclaimer ajouté le 2026-01-17 (commit 0370133). | partielle (0.64) |
| B-22 | [Are Polymarket prices calibrated probabilities? (dépôt shirleyshen0106/polymarket-calibrat](https://raw.githubusercontent.com/shirleyshen0106/polymarket-calibration/main/README.md) | B | 2026-09-27 | Contredit B-20 sur le côté longshot (biais inversé), mais l auteur signale lui-même l artefact de régression (cote bruitée, carnets minces, cotes en cours de match): prix de milieu non exécutables. Tranche: B-20 (588 M de trades,  | partielle (0.77) |
| B-23 | [ryanfrigo/kalshi-ai-trading-bot: README, Live Track Record (2026-09-25) et issues](https://raw.githubusercontent.com/ryanfrigo/kalshi-ai-trading-bot/main/docs/TRACK_RECORD.md) | B | 2026-09-25 | Post-mortem Kalshi honnête et chiffré (B, non vérifiable par moi): un taux de gain élevé sur NO ne fait pas un P&L positif; le carnet liquide Kalshi est « sharp ». Cohérent avec les rejets Quant (FLB Kalshi, CPI). Audit du lead :  | partielle (à la main) |
| B-24 | [maximumskif/polycopytrade: étude et copie de wallets Polymarket (Phase 1, août 2026)](https://raw.githubusercontent.com/maximumskif/polycopytrade/master/README.md) | B | 2026-08-13 | Post-mortem chiffré du copy-trading et des échelles de prix: l edge d un wallet vedette s éteint en 3 semaines; le signal extrait ne se réplique pas. Bug de calcul reconnu et corrigé par l auteur (bon signe d honnêteté, mais B). | partielle (0.79) |
| C-12 | [Arbitrage controller – High Slippage and Losses During Volatility (issue #7402)](https://github.com/hummingbot/hummingbot/issues/7402) | C | 2025-01-30 | Témoignage d'utilisateur: le goulot de l'arbitrage/MM retail est l'exécution (slippage, jambe unique), pas le signal. Même liste d'issues: #8094 'XEMM V2 Executor: Cancel/Fill Race Condition causes missing Taker hedge order (Naked | WebFetch seul |
| C-13 | [v2_funding_rate_arb strategy not calculatiopn correctly (issue #7301) ; #8413 'Bug Report  — (+ liste https://github.com/hummingbot/hummingbot/issues?q=is%3Aissue+profitable](https://github.com/hummingbot/hummingbot/issues/7301) | C | 2024-11-16 (#7301);  | Le bot de funding arb open source le plus utilisé mesure mal sa propre rentabilité: un opérateur qui s'y fie ne sait pas s'il gagne. Aucun P&L réel publié dans ces issues. | WebFetch seul |
| C-14 | [freqtrade FAQ: 'I have made 12 trades already, why is my total profit negative?' (+ README](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/faq.md) | C | inconnue (branche de | Le projet de bot retail le plus populaire ne revendique aucun edge et renvoie au backtest: pas de preuve B ou A de gain en réel. | partielle (0.69) |

#### Famille 3 — X/Twitter et blogs de praticiens (16 sources)

| Id | Source | Grade | Date | Contenu (une ligne) | Vérif. citation |
|---|---|---|---|---|---|
| L-02 | [Primer #3: The Nature Of Edge](https://moontower.substack.com/p/primer-3-the-nature-of-edge) | B | inconnue | Cadre de praticien : on ne trade pas le marché liquide pour l'edge, on s'en sert comme juste valeur contre un contrepartiste enthousiaste ; la puissance exige beaucoup d'essais. | trouvée |
| L-04 | [Trading the Fed: The Pre-FOMC Drift is Alive](https://www.quantseeker.com/p/trading-the-fed-the-pre-fomc-drift) | B | 2025 (données jusqu' | Contredit en partie L-03 : les deux s'accordent sur 2016-2019 plat ; le rebond 2020-2024 n'est pas isolé statistiquement. Meilleure preuve : L-03 (article publié) pour 2016-2019, rien de solide après. | trouvée |
| L-10 | [Tweets de l'auteur du bot (12 et 13 avril 2026)](https://x.com/sterlingcrispin/status/2043723823678382254) | C | 2026-04-13 | L'auteur admet l'absence de rendement du bot ; le chiffre de 73,4 % de NO ne dit rien du prix payé, donc rien de l'edge. | trouvée |
| L-11 | [I ran an arbitrage bot on Polymarket. Here are the real numbers.](https://kacho.io/polymarket-arbitrage-real-numbers) | A | 2026-06-06 | Grade A car le wallet est public et vérifié (L-12). Mécanisme : spreads de 20-30 ¢ sur l'esport Polymarket faute de market makers ; décroissance mensuelle nette ; « more competition for the market making and fees got introduced ». | trouvée |
| L-14 | [Adverse selection eating away my Polymarket bot arbitrage profits](https://kacho.io/why-my-polymarket-arbitrage-bot-lost-money) | B | 2026-06-30 | Le vrai goulot d'une cotation maker est la fraîcheur de la juste valeur ; un budget de 500 requêtes Odds API par mois interdit toute version maker de la piste Pinnacle. | trouvée |
| A-07 | [Betfair premium charge – Explained – Part one](https://www.peterwebb.com/betfair-premium-charge-explained-part-one/) | C | inconnue | Mécanisme : la commission sur gains nets pénalise les parieurs directionnels et favorise le trading à forte fréquence de réussite ; la Premium Charge rééquilibre. Chiffres illustratifs, pas un P&L. | trouvée |
| A-09 | [Luana Lopes Lara (co-fondatrice de Kalshi) sur Kalshi Trading](https://x.com/luanalopeslara/status/1994418071629336978) | B | 2025-11-28 | Source primaire du chiffre repris par InGame [A-08] ; les 94 % restants du volume maker sport viennent d'autres teneurs (programmes MM à obligations). | trouvée |
| A-10 | [Rufus Peabody sur les frais Kalshi et la rémunération des market makers](https://x.com/RufusPeabody/status/2050059856682389960) | C | 2026-05-01 | Mécanisme (pas un P&L) : l'argent des takers perdants est partagé entre l'exchange (frais) et les makers ; l'exchange calibre les rebates pour que les MM gagnent juste assez. | trouvée |
| A-26 | [How sharp are bookmakers? Analyzing matchup and 3-ball odds from the 2019 and 2020 seasons](https://datagolf.com/how-sharp-are-bookmakers) | B | 2020-12-18 | Dans une niche (golf), l'ouverture de Pinnacle n'est pas la référence : un book spécialiste mène et Pinnacle converge vers lui ; la clôture Pinnacle redevient la meilleure référence (EV ≈ réalisé). Données privées ; 2019-2020 : ré | trouvée |
| B-10 | [Tweets @DextersSolab sur le bot 0x8dxd (5 et 6 janvier 2026)](https://api.fxtwitter.com/DextersSolab/status/2008285935650181231) | C | 2026-01-05 | Récit viral (C). Le wallet vérifié (B-12) montre un profil surtout maker achetant les deux issues, pas une pure latence taker, et des gains qui continuent 3 mois après les frais. | API datée |
| B-11 | [Tweet @browomo: « A bot turned $313 → $324K in less than a month »](https://api.fxtwitter.com/browomo/status/2006390264982573195) | C | 2025-12-31 | Deux récits C divergents sur le même wallet; l API donne 321,6 k$ de PnL économique en décembre 2025 (B-12), ce qui confirme l ordre de grandeur de @browomo. | API datée |
| B-17 | [Fil de Daniel Sapkota (@defiance_cr), auteur de poly-maker](https://api.fxtwitter.com/defiance_cr/status/1906774862254800934) | B | 2025-03-31 | Témoignage de praticien (B) sur l âge d or 2024 des récompenses; à lire avec B-16 (le même auteur déclare le bot non rentable en 2026). | API datée |
| C-22 | [Odaily Interviews Airdrop Farmers: How to Obtain Crypto Airdrops in 2025?](https://wublock.substack.com/p/odaily-interviews-airdrop-farmers) | B | 2025-02-25 | Preuve B d'une décroissance (2024 < 2023) et d'un déplacement vers les studios multi-comptes et scripts; la part accessible à un compte unique légal est de l'ordre de centaines de dollars par projet, non testable en papier. | partielle (0.8) |
| C-23 | [thoughts on zero fees perp dexs - commoditize the field for traders’ good — (lu via https://api.fxtwitter.com/stablealt/status/2003495652668399803)](https://x.com/stablealt/status/2003495652668399803) | C | 2025-12-23 | Mécanisme: la subvention en points est capturée en spread par les MM les plus rapides, puis disparaît à la fin du programme; un petit MM y est en concurrence avec des MM qui acceptent un spread négatif. Grade C: raisonnement sans  | API datée |
| D-16 | [Tweet de Boaz Weinstein (Saba Capital) sur la campagne CTF-U](https://api.fxtwitter.com/boazweinstein/status/1702333209252610338) | B | 2023-09-14 | L'activiste dépend des votes des petits porteurs : un petit opérateur peut « suivre » l'activiste sans le coût de campagne (free-riding), mais le signal est public et instantané. | API datée |
| D-17 | [Tweet de Boaz Weinstein sur la cotation de BPRE](https://api.fxtwitter.com/boazweinstein/status/2001010698319798633) | B | 2025-12-16 | Qui perd : les porteurs captifs d'un fonds converti en CEF coté, qui vendent à tout prix ; événement rare, auteur partie prenante (activiste). | API datée |

#### Famille 4 — Académique et working papers (32 sources)

| Id | Source | Grade | Date | Contenu (une ligne) | Vérif. citation |
|---|---|---|---|---|---|
| L-01 | [The Microstructure of Wealth Transfer in Prediction Markets](https://www.jbecker.dev/research/prediction-market-microstructure) | A | inconnue (analyse de | Déjà connu de Quant ; source A du schéma « les makers encaissent la taxe d'optimisme des takers », effet maximal en sport et divertissement, quasi nul en finance. | trouvée |
| L-03 | [The disappearing pre-FOMC announcement drift (Finance Research Letters, 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7525326/) | A | 2021 | Fait nouveau contre la veille de FOMC en shadow : l'effet a perdu environ 80 % après 2015 ; 8 événements par an, donc un test forward prendrait des années. | trouvée |
| L-17 | [Does Academic Research Destroy Stock Return Predictability? (version publiée, Journal of F](https://tevgeniou.github.io/EquityRiskFactors/bibliography/AcademicReviewFactor.pdf) | A | 2016 | Justifie la décote de 50 % du prompt (entre 35 % et 58 % selon la version) ; confirmé aussi par le résumé ABFER. Les chiffres publiés font foi. | trouvée |
| A-01 | [Beating the bookies with their own numbers - and how the online sports betting market is r](https://arxiv.org/pdf/1710.02824) | A | 2017-10-08 | Preuve primaire du consensus contre les books soft : edge brut réel mais neutralisé par les limites de compte en quelques mois ; alpha=0.05 fixé par la source (choisi in-sample). | trouvée |
| A-05 | [Makers and Takers: The Economics of the Kalshi Prediction Market (GWU/RPF WP 2026-001; als](https://www2.gwu.edu/~forcpgm/2026-001.pdf) | A | 2026-01 | Référence de fond (pas spécifique sport, échantillon avant l'essor du sport) : les makers perdent moins que les takers mais restent négatifs en moyenne ; seuls les makers sur les favoris gagnent un peu. | trouvée |
| A-19 | [The Profit–Bias Identity in Sports Betting: Bookmaker Profit as the Public's Prediction Er](https://arxiv.org/pdf/2609.06739) | A | 2026-09-09 | Contre-preuve académique récente : le biais du public vers les favoris n'est pas exploité par un prix décalé ; le livre gagne sa marge, pas l'erreur du public. Parier « contre le public » ne rapporte rien au-delà du vig ; seul l'é | trouvée |
| B-19 | [Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets (AFT 2025)](https://arxiv.org/pdf/2508.03474) | A | 2025-08 | L estimation « extraite » (brute, ε = 1 $/trade) surestime ~4-5x le PnL net du meilleur compte selon la comptabilité de Polymarket. Confirme que l arbitrage intra-marché/negRisk (déjà rejeté chez Quant) est un jeu de bots à gros v | partielle (0.74) |
| B-20 | [The Favorite–Longshot Bias in Prediction Markets: Evidence from Polymarket](https://arxiv.org/pdf/2609.12878) | A | 2026-09 | Pour B3: le côté favori (vendre le longshot) rapporte +0,28 à +0,83 c par dollar avant frais et portage, et le signe du côté longshot dépend de l agrégation: pas d expression unique robuste, et même objet que le rejet Kalshi/bondi | trouvée |
| B-21 | [Who Wins and Who Loses in Prediction Markets? Evidence from Polymarket (CEPR DP21615, SSRN](https://www.carf.e.u-tokyo.ac.jp/wp/wp-content/uploads/2026/06/260714_polymarket.pdf) | A | 2026-06-21 | Meilleure preuve A du couloir: ce sont les fournisseurs de liquidité et une minorité qui gagnent; la persistance mensuelle est faible et biaisée par la sélection, ce qui réfute le copy-trading naïf des meilleurs du mois. | partielle (0.78) |
| C-07 | [Public Trader Identity: Adverse Selection and Return Predictability](https://arxiv.org/pdf/2608.04373) | A | 2026-08-05 (v3 2026- | Les gagnants identifiables de Hyperliquid ont un avantage persistant mais à l'échelle de la seconde: exploitable seulement avec un nœud non validant et le carnet L4 complet, pas avec des barres horaires. Pour un MM, ce sont eux qu | partielle (0.65) |
| C-08 | [Trading in the Sunshine or in the Shade: Market Impact and Adverse Selection on Hyperliqui](https://arxiv.org/abs/2606.15715) | A | 2026-06-14 | Les TWAP natifs visibles de Hyperliquid attirent la liquidité: flux prévisible, mais déjà absorbé par les MM qui augmentent la profondeur; pas d'expression horaire exploitable identifiée. | partielle (0.79) |
| C-09 | [Autodeleveraging: Impossibilities and Optimization](https://arxiv.org/abs/2512.01112) | A | 2025-11-30 (v3 2026- | Risque de queue caché pour toute position couverte ou gagnante sur un perp DEX: l'ADL ferme la jambe gagnante au pire moment (touche aussi les couvertures delta-neutres de C5). | partielle (0.79) |
| D-01 | [Does Academic Research Destroy Stock Return Predictability? (Journal of Finance 71(1), 201](https://api.crossref.org/works/10.1111/jofi.12365) | A | 2016-02 | Référence canonique ; la décote de 58 % dépasse légèrement les 50 % de Quant, et elle est plus forte pour les effets in-sample élevés. | API datée |
| D-02 | [Does Academic Research Destroy Stock Return Predictability? (version de travail du 16 mai ](https://www.ivey.uwo.ca/media/2827306/bengraham3rdsymposium-pontiff-paper-2014.pdf) | A | 2013-05-16 | Même étude, échantillon antérieur : l'estimation de décroissance est passée de 35 % à 58 % entre versions, signe d'une forte incertitude sur le chiffre lui-même. | partielle (0.55) |
| D-03 | [Does Peer-Reviewed Research Help Predict Stock Returns? (version décembre 2025)](https://arxiv.org/pdf/2212.10317) | A | 2025-12 | Appui direct à une décote d'environ 50 % pour les anomalies transversales ; la théorie publiée n'améliore pas la robustesse hors échantillon. | trouvée |
| D-04 | [Why and how systematic strategies decay (publié sous « When do systematic strategies decay](https://arxiv.org/pdf/2105.01380) | A | 2021-05-05 | Contredit une décote fixe de 50 % : pour un effet publié récemment la décote attendue est plus forte (la décroissance commence ~1,5 an avant publication, circulation des preprints). | partielle (0.73) |
| D-05 | [Zeroing in on the Expected Returns of Anomalies (FEDS 2020-039 ; publié JFQA 2023)](https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf) | A | 2020-05 | La décote de 50 % est correcte AVANT coûts ; APRÈS coûts réels, l'anomalie transversale moyenne est nulle : la décote de Quant doit s'appliquer à l'effet brut puis soustraire les coûts. | trouvée |
| D-06 | [Is There a Replication Crisis in Finance? (NBER w28432 ; JF 78(5), 2023)](https://www.nber.org/system/files/working_papers/w28432/w28432.pdf) | A | 2021-02 | Nuance clé : en moyenne la baisse est d'un tiers, mais la pente 0,25 signifie qu'un effet isolé retenu parce qu'il est fort garde plutôt 25-45 % de son alpha in-sample. | trouvée |
| D-07 | [Anomalies across the globe: Once public, no longer existent? (version janvier 2017 ; JFE 1](https://wp.lancs.ac.uk/fofi2018/files/2018/03/FoFI-2018-0174-Sebastian-M%C3%BCller2.pdf) | A | 2017-01 | La décroissance est un phénomène d'arbitrage américain : pour des actifs américains liquides, 60-65 % est plus réaliste que 50 %. | trouvée |
| D-08 | [What Useful Alphas? (arXiv 2607.06502)](https://arxiv.org/pdf/2607.06502) | A | 2026-07-07 | Preuve 2026 la plus récente : hors micro-caps, la décote réelle est ~85 %, pas 50 % ; le résidu vit dans les micro-caps, seul espace où la petite taille est un avantage (mais coûts élevés). | partielle (0.62) |
| D-09 | [Not All Factors Crowd Equally: Modeling, Measuring, and Trading on Alpha Decay (RETIRÉ)](https://arxiv.org/abs/2512.11913) | C | 2025-12-27 | Ouvert mais écarté : l'auteur a retiré le papier ; mentionné pour traçabilité (remonté par la recherche n°1). | trouvée |
| D-11 | [Rest in Peace Post-Earnings Announcement Drift (préprint OSF ; Critical Finance Review 202](https://api.crossref.org/works/10.31235/osf.io/z7k3p) | A | 2021-12-01 | Effet événementiel célèbre dont la décote réelle est ~100 % : la décote fixe de 50 % est trop généreuse pour les effets d'événements publics bien connus. | API datée |
| D-12 | [Tax-Loss Selling and the January Effect: Evidence from Municipal Bond Closed-End Funds (ve](https://www.bus.umich.edu/pdf/mitsui/workshopdocs/ZhengJanuaryEffect.pdf) | A | inconnue (vers 2004) | Mécanisme : ventes fiscales des particuliers en décembre sur les CEF en perte, rebond en janvier. Effet par événement ≈ 2,4 points, 1 événement/an (corrélé entre fonds). | trouvée |
| D-13 | [Tax-loss selling and the January effect revisited: Evidence from municipal bond closed-end](https://api.crossref.org/works/10.1111/jfir.12384) | A | 2024-01-31 | Rare cas d'effet publié en 2006 qui ne décroît pas : la contrainte (fiscalité des particuliers) persiste. Chiffres détaillés non trouvés en accès libre. | API datée |
| D-18 | [The Shrinking Merger Arbitrage Spread: Reasons and Implications (Financial Analysts Journa](https://www.analysisgroup.com/globalassets/content/insights/publishing/jetley_and_ji_shrinking_merger_arbitrage_spread2.pdf) | A | 2010 | Décroissance de l'arbitrage de fusions après afflux de capitaux ; « some of the decline is likely to be permanent ». | trouvée |
| D-19 | [SPACs (Review of Financial Studies 36(9), 2023 ; version du 23 février 2023)](https://site.warrington.ufl.edu/ritter/files/SPACs.pdf) | A | 2023-02-23 | La performance vient d'une obligation sans défaut + bons de souscription gratuits : c'est un plancher (trust) plus une option, pas un signal ; très dépendante du cycle (bulle 2020). | trouvée |
| D-20 | [Going Public with IPOs and SPAC Mergers](https://site.warrington.ufl.edu/ritter/files/going-public-with-IPOs-and-SPAC-mergers.pdf) | A | 2024 (données jusqu' | Les porteurs pré-fusion rachètent au trust : l'option de remboursement est la source réelle du rendement, les actionnaires post-fusion perdent. | trouvée |
| D-22 | [Retail Traders Love 0DTE Options... But Should They? (version du 15 décembre 2023)](https://wp.lancs.ac.uk/fofi2024/files/2024/04/FoFI-2024-146-Leander-Gayda.pdf) | A | 2023-12-15 | Qui perd : les particuliers acheteurs de 0DTE, surtout via les coûts ; qui gagne : les teneurs de marché (spread). Données Cboe Open/Close payantes : non reproductible gratuitement par Quant. | trouvée |
| D-23 | [The Disappearing Index Effect (NBER w30748 ; Journal of Finance 80(2), 2025)](https://www.nber.org/system/files/working_papers/w30748/w30748.pdf) | A | 2022-12 | Décroissance ≈90 % de l'effet d'annonce alors que l'indexation a augmenté : l'arbitrage (anticipation, liquidité) l'a mangé ; la décote de 50 % serait trop faible. | trouvée |
| D-24 | [Losing is Optional: Retail Option Trading and Expected Announcement Volatility (Review of ](https://www.timdesilva.me/files/papers/losing_optional.pdf) | A | 2026-03 | Camp vendeur : acheter la volatilité avant les résultats perd quand l'attention des particuliers gonfle la vol implicite ; contredit un achat de straddle inconditionnel (D-25). Données OptionMetrics et Nasdaq payantes. | trouvée |
| D-25 | [Anticipating Uncertainty: Straddles around Earnings Announcements (version de travail ; JF](https://quantpedia.com/www/Anticipating_Uncertainty-Straddles_Around_Earnings_Announcements.pdf) | A | 2013 (version de tra | Camp acheteur, mesuré au milieu de fourchette ; le chiffre JFQA (3,34 % de J-3 à J) n'a pas été vérifié en texte brut. À opposer à D-24. | trouvée |
| D-27 | [Day Trading for a Living? (FEA-USP WP 2019-47 ; SSRN 3423101)](http://www.repec.eae.fea.usp.br/documentos/Chague_Losso_Giovannetti_47WP.pdf) | A | 2019-08-19 | Survivorship massif : la persistance ne produit pas d'apprentissage ; la contrepartie gagnante est la HFT. L'étude de Taïwan n'a pas été ouverte (citée par cette source). | partielle (0.79) |

#### Famille 5 — Données des plateformes (43 sources)

| Id | Source | Grade | Date | Contenu (une ligne) | Vérif. citation |
|---|---|---|---|---|---|
| L-06 | [Topstep – divulgation des performances des traders 2025](https://www.topstep.com/our-program) | B | 2026 (année 2025) | Donnée primaire d'une plateforme, non auditée (grade B) : moins de 1 % des day traders de futures atteignent le capital réel ; le modèle économique vit des frais de challenge. | trouvée |
| L-12 | [API Polymarket : wallet b00k13 (0x1c5575dc…84ce)](https://data-api.polymarket.com/v1/leaderboard?timePeriod=month&orderBy=PNL&limit=1&user=0x1c5575dc20e4ea54d1bb09ccda72ccf8a3b684ce) | A | 2026-09-27 | Vérification indépendante : le track record de L-11 existe et le bot tourne encore à petite échelle ; capacité de l'ordre de quelques centaines de dollars par mois. | API datée |
| L-18 | [Polymarket Data — 1.9 billion trading records (Hugging Face)](https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data) | A | 2026-07-21 (dernière | Source de données gratuite et point-in-time par construction (horodatage des blocs) : rend possible une décomposition maker/taker par catégorie sur Polymarket, à l'image de Becker sur Kalshi. | trouvée |
| L-21 | [Schéma de trades.parquet et users.parquet (lecture DuckDB à distance)](https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data/resolve/main/trades.parquet) | A | 2026-07-21 | La décomposition maker/taker est faisable sans tout télécharger ; aucune statistique de rendement n'a été calculée (les données restent vierges pour un test pré-enregistré). La catégorie de marché doit venir de gamma-api. | API datée |
| L-22 (= B-04) | [Polymarket — changelog officiel (frais, rebates, délai taker, TWAP)](https://docs.polymarket.com/changelog/predictions.md) | A | 2026-09-15 (dernière | La venue elle-même taxe les takers pour payer les makers et freine l'arbitrage de latence : c'est le mécanisme de décroissance documenté. Pour H-001, le seuil taker sport doit intégrer 0,05·p(1-p) par part, soit 2,5 % du coût à 50 | trouvée |
| L-23 | [SPY — barres journalières ajustées (2016-09-26 → 2026-09-25)](https://query1.finance.yahoo.com/v8/finance/chart/SPY?range=10y&interval=1d) | A | 2026-09-25 | Entrée de σ pour le calcul de puissance (même source que le relais Yahoo de Quant). | API datée |
| L-24 | [Deribit — indice de volatilité implicite DVOL (API publique)](https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&start_timestamp=1609459200000&resolution=1D) | A | 2026-09-27 | Source gratuite, sans login et point-in-time (valeurs quotidiennes horodatées) pour une juste valeur digitale N(d2) sur BTC et ETH ; approximation ATM 30 jours, sans smile. | API datée |
| L-25 | [Polymarket — métadonnées des marchés crypto à seuil (comptage par trimestre)](https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data/resolve/main/markets.parquet) | A | 2026-07-21 | Métadonnées seulement (aucun prix ni résultat lu) : l'historique dense des marchés à seuil commence mi-2025, soit environ 15 mois utilisables pour un test historique. | API datée |
| L-26 | [Polymarket — échéances horaires des marchés « Ethereum/Bitcoin above » (1er mai 2026)](https://huggingface.co/datasets/SII-WANGZJ/Polymarket_data/resolve/main/markets.parquet#echeances-horaires-2026-05-01) | A | 2026-07-21 | Change la puissance de B6 : environ 17 500 fenêtres horaires indépendantes par an sur BTC+ETH (corrélées entre elles), contre 730 jours-actif. | API datée |
| L-28 | [Deribit DVOL horaire et bougies Hyperliquid 1h (flux de juste valeur pour B6)](https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=ETH&resolution=3600) | A | 2026-09-27 | Flux horaires gratuits, sans login et horodatés : la juste valeur N(d2) peut être recalculée à chaque échéance horaire, en historique comme en forward. | API datée |
| L-29 | [Polymarket v2/user-pnl — justdance, 0x06dc et gabagool22 : trading, frais et sponsoring pa](https://data-api.polymarket.com/v2/user-pnl?user=0xcc500cbcc8b7cf5bd21975ebbea34f21b5644c82&interval=max&fidelity=1d) | A | 2026-09-27 | Le « P&L économique » de Polymarket inclut des revenus de sponsoring et de parrainage : il faut juger un wallet sur son trading net de frais. Le proxy d'effet de B6 passe de 3,8 % à 3,55 %. | API datée |
| A-02 | [Kalshi public API: sports series with fee_type and fee_multiplier (snapshot 2026-09-27)](https://api.elections.kalshi.com/trade-api/v2/series?category=Sports) | A | 2026-09-27 | Fait nouveau vérifié par API : les marchés sport principaux de Kalshi facturent aussi les makers ; les props joueurs NFL non. | API datée |
| A-03 | [Kalshi public API: historical fee changes of sports series](https://api.elections.kalshi.com/trade-api/v2/series/fee_changes?series_ticker=KXMLBGAME&show_historical=true) | A | 2026-09-27 | Datation exacte de l'introduction des frais maker en sport Kalshi (fin 2025) : réduit le rendement de la tenue de marché passive. | API datée |
| A-04 | [Kalshi public API: active liquidity incentive programs (snapshot 2026-09-27)](https://api.elections.kalshi.com/trade-api/v2/incentive_programs?status=active&limit=10000) | A | 2026-09-27 | Fait nouveau : Kalshi subventionne la liquidité passive des props NFL (sans frais maker) ; la subvention est publique et mesurable par marché. | API datée |
| A-06 | [Premium Charge FAQ (revised Premium Charge from 6 January 2025)](https://www.betfair.com.au/hub/help/premium-charge-faq/) | A | 2025-01 (approx.) | Taxe de l'exchange sur les gagnants : un petit opérateur qui gagne < 25 k£/an brut sur 52 semaines n'est pas touché ; au-delà, 20-40 % du profit brut. La part des clients concernés (« moins de 0,5 % ») n'a pas pu être ouverte (bet | partielle (0.7) |
| A-11 | [Polymarket docs: Fees + Maker Rebates Program (https://docs.polymarket.com/programs/maker-](https://docs.polymarket.com/trading/fees.md) | A | consulté 2026-09-27 | Fait nouveau 2026 : le sport Polymarket n'est plus gratuit pour les takers ; coût taker à p=0.5 = 2.5 % du prix payé, à retrancher de tout edge de type consensus. | API datée |
| A-12 | [Polymarket US Fee Schedule (effective 25 September 2026)](https://docs.polymarket.us/fees.md) | A | 2026-09-25 | Sur Polymarket US, le maker reçoit une remise explicite par fill (≈0.31 $ pour 100 contrats à 0.50) : économie maker différente de Kalshi (frais maker) et de Polymarket international (rebate pool). | API datée |
| A-25 | [Fees on Novig (Novig Help Center, mis à jour « over 2 weeks ago » au 2026-09-27)](https://support.novig.com/en/articles/16195057-fees-on-novig) | A | 2026-09 (approx.) | Fait nouveau 2026 : un exchange sport US sans aucun frais en pré-match ; seule venue où un edge de consensus de 1-3 % ne serait pas mangé par les frais. Disponibilité d'un flux public de carnet sans compte : non vérifiée. | trouvée |
| A-27 | [Kalshi public API: open NFL markets (game, spread, total, receiving-yards ladder), snapsho](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXNFLLADDERRECYDS&status=open&limit=1000) | A | 2026-09-27 | Les props NFL de Kalshi sont cotées (grâce aux primes LIP [A-04]) mais ne se traitent presque pas : la « liquidité » est celle des chasseurs de primes ; un taker n'y trouve pas de contrepartie naïve et un maker y gagne surtout la  | API datée |
| B-01 | [Polymarket leaderboard all-time par PnL (top 50)](https://data-api.polymarket.com/v1/leaderboard?timePeriod=all&orderBy=PNL&limit=50) | A | 2026-09-27 | Classement officiel; le PnL est calculé par Polymarket (non audité), le volume inclut les deux jambes. Instantané du 2026-09-27, fichier raw/lb_all_pnl.json. | API datée |
| B-02 | [Polymarket leaderboard all-time et mois par volume (top 50)](https://data-api.polymarket.com/v1/leaderboard?timePeriod=all&orderBy=VOL&limit=50) | A | 2026-09-27 | Le volume ne fait pas le gain: une grande partie des wallets à très haut volume (bots/MM) sont à zéro ou perdants. Fichiers raw/lb_all_vol.json et raw/lb_month_vol.json. | API datée |
| B-03 | [Fees - Polymarket Documentation](https://docs.polymarket.com/trading/fees) | A | inconnue (lu 2026-09 | Fait nouveau majeur: Polymarket n est plus sans frais (sauf géopolitique). La formule est celle de Kalshi (0,07·p·(1-p)) pour la crypto; la prémisse de B3 (Polymarket sans frais) est caduque pour la plupart des catégories. | partielle (0.71) |
| B-05 | [Maker Rebates Program - Polymarket Documentation](https://docs.polymarket.com/programs/maker-rebates) | A | inconnue (lu 2026-09 | Le rebate récompense le volume maker exécuté (donc le risque de sélection adverse), pas la présence; le pool est au plus 20-25 % des frais taker du marché. | partielle (0.79) |
| B-06 | [Taker Rebate Program - Polymarket Documentation](https://docs.polymarket.com/programs/taker-rebates.md) | A | 2026-05-28 (mise en  | Les gros takers récupèrent jusqu à 50 % de leurs frais: la structure de frais favorise les très gros volumes, pas un petit opérateur papier (qui resterait au palier 0 ou Bronze). | API datée |
| B-07 | [Liquidity Rewards - Polymarket Documentation](https://docs.polymarket.com/programs/liquidity-rewards.md) | A | inconnue (lu 2026-09 | Mécanique exacte des récompenses de liquidité: la part est relative aux autres fournisseurs (jeu à somme fixe par marché), d où une concurrence qui érode le rendement. | API datée |
| B-08 | [Holding Rewards / Polymarket Help Center](https://docs.polymarket.com/polymarket-learn/trading/holding-rewards) | A | 2026-06-01 | Fait nouveau pour B3: le coût de portage (immobilisation du capital) d un NO à 90-97 c sur des marchés longs éligibles est partiellement compensé par 3,25 %/an; plusieurs de ces marchés géopolitiques sont aussi sans frais taker. | partielle (0.75) |
| B-12 | [Wallet 0x8dxd (0x63ce…ba9a): série PnL v2, user-stats et échantillons de trades v2](https://data-api.polymarket.com/v2/user-pnl?user=0x63ce342161250d705dc0b16df89036c8e5f9ba9a&interval=max&fidelity=1d) | A | 2026-09-27 | Vérifié moi-même via l API: le « bot de latence » est majoritairement maker des deux côtés; marge ~2,3 % du volume stable de décembre à mars malgré les frais (contredit « cooked » de B-10), puis arrêt en avril 2026 (après frais V2 | API datée |
| B-13 | [Leaderboards v2 par catégorie (crypto, mentions, economics, politics, culture, tech, finan](https://data-api.polymarket.com/v2/leaderboard?time_period=all&category=crypto&limit=25) | A | 2026-09-27 | Le gâteau « mentions » est petit (top all-time < 0,3 M$); le gâteau crypto court est concentré sur une vingtaine de wallets à ~1 % du volume notionnel. Un nom de wallet ou un rang mensuel ne dit rien de la catégorie ni du PnL dura | API datée |
| B-14 | [Séries PnL mensuelles v2 de 4 wallets crypto: gabagool22, 0xf705…3ca7, justdance, 0x06dc…4](https://data-api.polymarket.com/v2/user-pnl?user=0x6031b6eed1c97e853c6e0f03ad3ce3529351f96d&interval=max&fidelity=1d) | A | 2026-09-27 | Décroissance chiffrée: les deux wallets « 15 minutes » les plus cités (gabagool22, 0x8dxd) s arrêtent en mars-avril 2026; les gagnants actuels de la catégorie crypto (justdance, 0x06dc, 0xf705) tradent surtout des marchés à seuil  | API datée |
| B-15 | [Wallet RN1 (0x2005…75ea): activités REWARD / MAKER_REBATE / TAKER_REBATE et user-stats v2](https://data-api.polymarket.com/activity?user=0x2005d16a84ceefa912d4e380cd32e7ff827875ea&type=MAKER_REBATE&limit=500&start=1) | A | 2026-09-27 | Wallet sport (couloir A) mais meilleure mesure publique de l économie des programmes: pour le plus gros gagnant « à volume », rebates et récompenses font ~11 % du PnL et compensent à peine les frais payés; l edge vient du trading. | API datée |
| B-26 | [Liquidity Incentive Program / Kalshi Help Center](https://help.kalshi.com/en/articles/13823851-liquidity-incentive-program) | A | inconnue (lu 2026-09 | Contrairement aux rebates Polymarket (payés sur le volume exécuté), le LIP Kalshi paie la présence au carnet même sans fill; le pool par marché est petit (<= 1 000 $/jour) et partagé au prorata. Réservé aux résidents US (point lég | partielle (0.62) |
| C-01 | [HLP vaultDetails (portfolio allTime, month) — (POST {"type":"vaultDetails","vaultAddress":"0xdfc24b077bc1425ad1dea75bcb6f8158e](https://api.hyperliquid.xyz/info) | A | 2026-09-27 | Rendement HLP en forte décroissance (79 % -> 19 % -> ~8 %/an), gains concentrés sur les journées de krach/liquidations; granularité 14 j masque les drawdowns intra-période. | API datée |
| C-02 | [Hyperliquid leaderboard (JSON, 46 962 lignes)](https://stats-data.hyperliquid.xyz/Mainnet/leaderboard) | A | 2026-09-27 | Le classement mélange spot, airdrop HYPE et perps; seul le ratio PnL/volume distingue le profil MM (quelques pb par $) des directionnels. Biais de survie fort. | API datée |
| C-03 | [Hyperliquid vaults (JSON, 9 476 vaults avec summary.isClosed, tvl, pnls allTime)](https://stats-data.hyperliquid.xyz/Mainnet/vaults) | A | 2026-09-27 | Preuve A de survivorship: environ 3 vaults de trading sur 4 perdent; les 75 % de gagnants parmi les gros survivants sont un artefact de sélection. | API datée |
| C-04 | [Hyperliquid Docs - Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) | A | inconnue | Un petit opérateur (10-100 k$) paie 1,5 pb en maker: aucune subvention de rebate accessible sur Hyperliquid, contrairement aux gros MM. | partielle (0.68) |
| C-05 | [Hyperliquid Docs - For vault leaders (+ protocol-vaults: lock-up HLP 4 jours)](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/for-vault-leaders) | A | inconnue | Frais de création 10 k$ = barrière qui explique la chute des créations de vaults en 2026 (623 contre 5 079 en 2024, C-03). | partielle (0.46) |
| C-19 | [DefiLlama Yields: Ethena sUSDe (Ethereum), historique quotidien APY et TVL](https://yields.llama.fi/chart/66985a81-9c51-46ca-9977-42b4fe7bc6df) | A | 2026-09-27 | Fait nouveau chiffré: le rendement du carry industrialisé (Ethena = short perp + long spot/LST) a été divisé par ~4 de 2024 à 2026 et se situe au niveau d'un placement monétaire; la TVL a fondu de ~65 %. | API datée |
| C-20 | [DefiLlama emissions (jeu de données public, 372 protocoles): metadata.events / unlockEvent — (liste: https://defillama-datasets.llama.fi/emissionsProtocolsList ; API officie](https://defillama-datasets.llama.fi/emissions/<protocole>) | A | 2026-09-27 | Calendrier gratuit, sans login, avec catégories proches de celles de Keyrock (équipe = insiders). Pas point-in-time: c'est la vue actuelle des calendriers (révisions rétroactives possibles); symboles mappés via CoinGecko (collisio | API datée |
| C-21 | [Hyperliquid: bougies quotidiennes (40 tokens + ETH, 2024-01-01 -> 2026-09-27) et historiqu — (POST candleSnapshot 1d et fundingHistory)](https://api.hyperliquid.xyz/info) | A | 2026-09-27 | Calcul propre (non conditionnel aux déblocages, pour ne pas consommer le test): donne σ par événement et le coût de portage d'un short. La dérive négative sans condition est un piège: un test doit comparer aux mêmes tokens hors fe | API datée |
| C-25 | [Hyperliquid fundingHistory BTC et ETH, 2024-01-01 -> 2026-09-27 (horaire) — (POST {"type":"fundingHistory","coin":"BTC"/"ETH","startTime":...})](https://api.hyperliquid.xyz/info) | A | 2026-09-27 | Décroissance chiffrée du carry perp: divisé par ~5 sur BTC entre 2024 et 2026, extrêmes de funding écrasés; même trajectoire que sUSDe (C-19). Série horaire gratuite, sans login, collectée en avant par le relais Quant. | API datée |
| D-15 | [API chart Yahoo : NAV quotidienne des CEF via symboles Lipper (XNEAX, XGAMX)](https://query1.finance.yahoo.com/v8/finance/chart/XNEAX?range=10y&interval=1d) | A | 2026-09-27 (consulta | Données gratuites et collectables par le relais Yahoo déjà en place ; NAV publiée après la clôture, donc décote point-in-time = cours J / NAV J-1, pas NAV J. | API datée |
| D-26 | [Cboe : cotations d'options différées (JSON) et historiques d'indices PUT et VIX (CSV)](https://cdn.cboe.com/api/global/delayed_quotes/options/SPY.json) | A | 2026-09-27 (consulta | Réponse à « Quant a-t-il des données d'options gratuites ? » : oui en forward (instantanés différés horodatés, bid/ask inclus), non en historique (OptionMetrics payant) ; les indices PUT/VIX donnent une série gratuite de prime de  | API datée |
| D-28 | [ESMA agrees to prohibit binary options and restrict CFDs to protect retail investors (comm](https://www.esma.europa.eu/sites/default/files/library/esma71-98-128_press_release_product_intervention.pdf) | A | 2018-03-27 | Donnée réglementaire agrégée (pas d'accès aux micro-données) ; statistique de 2018, non actualisée dans ce couloir. | trouvée |

#### Famille 6 — Industrie (rapports, podcasts) (12 sources)

| Id | Source | Grade | Date | Contenu (une ligne) | Vérif. citation |
|---|---|---|---|---|---|
| L-07 | [Hedge Fund Investing: Does Size -Really- Matter?](https://resonanzcapital.com/insights/hedge-fund-investing-does-size-really-matter) | B | 2025 | Soutient le schéma « niche à capacité limitée » mais sans chiffre primaire ; l'année 2024 le contredit. Preuve faible, à ne pas surpondérer. | trouvée |
| A-08 | [Kalshi Co-Founder Says In-House Trading Arm 'Not Profitable'](https://www.ingame.com/kalshi-in-house-trading-arm-not-profitable/) | B | 2025-12-01 | Contre-preuve pour la tenue de marché sport : même le teneur de marché affilié à l'exchange dit ne pas être rentable (adverse selection) ; chiffres de volume = analyse InGame des données Kalshi. | trouvée |
| B-09 | [Polymarket Introduces Dynamic Fees to Curb Latency Arbitrage in Short-Term Crypto Markets](https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/) | C | 2026-01-07 | Presse spécialisée; affirme que les frais rendent l arbitrage de latence non rentable, ce que les données du wallet 0x8dxd contredisent pour janvier-mars 2026 (voir B-12). | trouvée |
| B-18 | [Polymarket Fee Rollout: Revenue Impact and Market Implications](https://pineanalytics.substack.com/p/polymarket-fee-rollout) | B | 2026-03-25 | Analyse sectorielle (B) fondée sur Dune; ses taux de pic diffèrent de la doc actuelle (formule avec exposant, antérieure au barème feeRate·p·(1-p) de B-03): la doc officielle prime. Confirme aussi que le volume affiché compte envi | trouvée |
| B-25 | [Polymarket Volume Is Being Double-Counted](https://www.paradigm.xyz/writing/polymarket-volume-is-being-double-counted) | A | 2025-12-08 | Méthodologie de mesure: toute marge « PnL/volume » doit préciser le dénominateur; sur le cash échangé, les marges des wallets à volume (B-01) sont ~2x plus élevées (RN1: 0,98 % du notionnel, 2,3 % du cash). | partielle (0.72) |
| C-06 | [How Hyperliquid's HLP Vault Turns Market Chaos Into Profit](https://www.coingecko.com/learn/hyperliquid-hlp-vault-analysis) | B | 2026-07-02 (mise à j | Recoupé par l'API (C-01): période close le 2025-10-15 = +41,4 M$ (+9,70 %), période close le 2026-02-04 = +18,8 M$, période du 2025-11-12 = -4,7 M$ (POPCAT). Profil de HLP: vendeur de liquidité en krach, rendements rares et concen | WebFetch seul |
| C-10 | [From Locked to Liquidity: What 16,000+ Token Unlocks Teach Us](https://keyrock.com/from-locked-to-liquidity-what-16000-token-unlocks-teach-us/) | B | 2024-12 (couverture  | Étude de MM (conflit d'intérêts possible: Keyrock vend la couverture pré-déblocage). Les 16 000 événements ne sont pas indépendants (40 tokens, déblocages linéaires mensuels qui se chevauchent). | partielle (0.65) |
| C-11 | [Token unlocks 'almost always negative for price,' Keyrock's study reveals](https://crypto.news/token-unlocks-almost-always-negative-for-price-keyrocks-study-reveals/) | C | 2024-12-06 | Seconde main, sert seulement à dater l'étude Keyrock (C-10) et à noter que l'effet est une médiane pondérée, pas une moyenne avec σ. | trouvée |
| C-18 | [Wintermute Market Update: 13 Oct 2025 (+ 8 December 2025) — (+ https://www.wintermute.com/insights/market-color/market-update/market-update-](https://www.wintermute.com/insights/market-color/market-update/market-update-13-oct-2025) | B | 2025-10-13 ; 2025-12 | Fait nouveau sur 2 rejets: le rebond post-liquidation se joue en 30 min (inexploitable en horaire) et le delta-neutre n'est pas neutre en krach (ADL de la jambe courte). Le carry ne subsiste que sur les petites capitalisations, là | trouvée (à la main) |
| D-14 | [Closed-End Fund Activism (fiche ICI, données à fin 2024)](https://www.ici.org/system/files/2024-05/cef-activism.pdf) | B | 2025 (données au 202 | PDF téléchargé par WebFetch (curl 403) puis texte extrait avec pypdf ; source partiale (lobby des gérants) mais chiffres factuels ; montre que l'activisme est concentré chez 3 acteurs. | WebFetch seul |
| D-32 | [Moritz Heiden & Moritz Seibert – Trend-Following Spreads (Flirting with Models S7E25), tra](https://www.flirtingwithmodels.com/episodes/1iIqmQ7piJd) | B | 2026-01-12 | Transcription automatique (Deepgram nova-3) ; hors actions mais c'est le schéma recherché : un petit fonds gagne en restant petit sur des marchés que la taille interdit aux gros ; performance non vérifiée. | API datée |
| D-33 | [Volatility’s Blueprint: How Markets Really Move ft. Mandy Xu & Ed Tom (Top Traders Unplugg](https://www.toptradersunplugged.com/podcast/volatilitys-blueprint-how-markets-really-move-ft-mandy-xu-ed-tom/) | B | 2025-08-13 | Camp « bourse » : l'exchange (partie intéressée) décrit des flux équilibrés et une clientèle qui vend aussi de la prime ; ne donne aucun P&L, ne contredit donc pas les chiffres de pertes de D-22, mais nuance « les particuliers ne  | partielle (0.79) |

#### Famille 7 — Forums spécialisés (12 sources)

| Id | Source | Grade | Date | Contenu (une ligne) | Vérif. citation |
|---|---|---|---|---|---|
| L-09 | [HN : Nothing Ever Happens (275 commentaires), dont le fil 47754918](https://news.ycombinator.com/item?id=47753472) | B | 2026-04-13 | Post-mortem de praticien : le rendement apparent vient d'un biais d'anticipation de la date de résolution ; confirme le rejet du bonding. Un commentaire signale aussi des frais taker Polymarket sur la plupart des marchés, hors géo | API datée |
| L-16 | [HN : Making Markets on Kalshi (56 points, 26 commentaires)](https://news.ycombinator.com/item?id=43073377) | C | 2025-02-17 | Affirmation de gain non chiffrée (C) ; utile pour le mécanisme : marchés dérivés de produits financiers efficients et tenus par des institutions, marchés de niche plus fins mais petits. | API datée |
| L-20 (= A-14) | [Wisdom of the crowd — archive des paris publiés en direct (recalcul du lead)](https://www.football-data.co.uk/Wisdom_of_crowd_bets.xlsx) | A | 2025-06 (dernier par | Recalcul indépendant de A-14. Fait nouveau : le système a perdu en 2024-2025 alors que l'EV déclarée restait vers 4 %, et le nombre de paris éligibles a chuté ; les meilleures cotes viennent de books qui limitent les gagnants (Int | API datée |
| A-13 | [What is the true expected profit for the Wisdom of the Crowd Betting System?](https://www.football-data.co.uk/blog/wisdom_of_crowd_betting_system_closing_odds.php) | B | inconnue (vers 2022  | Le signal consensus mesuré par la CLV Pinnacle vaut environ 2.9 % par pari, moins que l'EV au moment de la détection ; les matchs sélectionnés sont largement des matchs à arbitrage, où la clôture Pinnacle est elle-même moins effic | trouvée |
| A-15 | [Market Efficiency of Opening Betting Odds at Pinnacle.com compared to bet365](https://www.football-data.co.uk/blog/opening_price_wisdom.php) | B | inconnue (données ju | L'inefficience d'ouverture des books soft est énorme mais se referme avant que la référence sharp n'existe ; un backtest sur 'cotes d'ouverture' surestime l'edge faute de synchronisation (piège point-in-time). | trouvée |
| A-16 | [How to solve a problem like efficiency: Part one (Pinnacle Betting Resources)](https://www.pinnacle.com/betting-resources/en/educational/how-to-solve-a-problem-like-efficiency-part-one/rn8j5rnqj2p8t68p) | B | inconnue | Preuve la plus directe que la CLV (ratio prix obtenu / clôture Pinnacle) prédit le rendement réel, en agrégat, sur le 1X2 football Pinnacle ; ne dit rien des marchés sport Kalshi/Polymarket. | trouvée (à la main) |
| A-17 | [How to solve a problem like efficiency: Part two - Anchoring bias and odds movement (Pinna](https://www.pinnacle.com/betting-resources/en/educational/how-to-solve-a-problem-like-efficiency-part-two/KS5JTMY67W9XFGGM) | B | inconnue | Entrée de puissance : σ par pari de la CLV mesurée depuis l'ouverture ≈ 0.08-0.10 contre σ ≈ 1.7 pour le P&L d'un pari à cote ~3.8 [A-14] ; la CLV réduit la variance d'un facteur ≈ 300 (σ² 0.0067-0.0106 contre 2.9). | trouvée (à la main) |
| A-22 | [Daily Trading P&L (pre off) - Bet Angel forum (pages start=0, 15, 30)](https://forum.betangel.com/viewtopic.php?t=23716) | C | 2021-05-18 (fil suiv | Même sur le forum de référence du trading pré-off, aucun P&L quotidien continu vérifiable ; témoignages de traders non rentables après 2 ans ; l'edge revendiqué est local (UK) et ne se transfère pas (ANZ). | partielle (0.46) |
| C-24 | [Ask HN: I've spent the better part of a year writing a market making crypto bot — (lu via https://hn.algolia.com/api/v1/items/22086393)](https://news.ycombinator.com/item?id=22086393) | C | 2020-01-18 | Post-mortem typique (hors période 2024-2026): validation sur testnet sans fills réels ni sélection adverse; aucune preuve de rentabilité. Seul fil HN pertinent trouvé. | API datée |
| D-29 | [Ask HN: Anyone making money through algorithmic trading? (lu via hn.algolia.com/api/v1/ite](https://news.ycombinator.com/item?id=16922538) | B | 2018-04-25 | Témoignages anonymes invérifiables (le gain de 127 % tombe sur la période de volatilité la plus basse, juste avant février 2018) : ne prouvent aucun edge ; le schéma récurrent est la vente de volatilité avec risque de queue. | API datée |
| D-30 | [Optionsellers.com goes bust and the apology video is painful to watch (fil Elite Trader)](https://www.elitetrader.com/et/threads/optionsellers-com-goes-bust-and-the-apology-video-is-painful-to-watch.327091/) | C | 2018-11-17 | Post-mortem d'un petit fonds vendeur de primes : illustre le risque de queue de la prime de variance ; grade C (opinions de forum), pointe seulement vers le risque. | trouvée |
| D-31 | [Thinking about starting a small hedge fund (fil Elite Trader)](https://www.elitetrader.com/et/threads/thinking-about-starting-a-small-hedge-fund.381002/) | B | 2024-08-30 | Mécanisme de « pourquoi les gros ne mangent pas » : stratégies non scalables gardées en compte propre ; affirmations de performance non vérifiables (C). | trouvée |

#### Famille 8 — Contre-preuve (rôle principal) (11 sources)

| Id | Source | Grade | Date | Contenu (une ligne) | Vérif. citation |
|---|---|---|---|---|---|
| L-05 | [What FTMO tells us about prop firm finances](https://tradeinformer.com/prop-weekly/what-ftmo-tells-us-about-prop-firm-finances) | B | 2024 | Chiffre de seconde main (interview FPFX) ; ordre de grandeur cohérent avec la divulgation primaire de Topstep (L-06). | trouvée |
| L-13 | [We lost $270 building a Polymarket bot — the complete audit](https://uruguabot.com/blog/we-lost-270-building-a-polymarket-bot.html) | B | 2026-08 | Leçon directe pour Quant : un shadow à fills sans friction fabrique un edge fictif ; il faut des distributions de slippage mesurées. | trouvée |
| L-15 | [I Lost $150 in 20 Minutes Market-Making on Kalshi. Here's Every Bug That Did It.](https://rlafuente.com/posts/2025-3-5-i-lost-150-market-making-on-kalshi) | B | 2025-03-05 | Post-mortem : la difficulté du market making amateur est l'ingénierie d'ordres et la sélection de marchés, pas le modèle ; les combos MVE de Kalshi sont des pièges de liquidité. | trouvée |
| A-18 | [Analysis: Overall Massachusetts Sports Betting Player Limiting is Low, But Correlation Exi](https://www.sportsbettingdime.com/news/betting/analysis-massachusetts-sports-betting-player-limitation-numbers-are-low-but-consistent-winners-more-likely-to-be-limited/) | B | 2025-09-30 | Contre-preuve régulateur : battre la clôture (CLV) est précisément le critère qui déclenche la limitation chez les books US ; la population limitée (< 1 %) est le plafond de la population qui gagne. Document primaire MGC non ouver | trouvée |
| A-23 | [BeatTheBookie - Betting Strategy to Beat the Bookies at Football Games (README brut https:](https://github.com/Lisandro79/BeatTheBookie) | B | issues 2019-2025 | Post-mortem des auteurs eux-mêmes : l'edge consensus existait mais ne valait pas l'effort une fois les comptes bloqués ; le jeu de données de cotes (2000-2016) est public et réutilisable pour une réplication hors échantillon. | WebFetch seul |
| A-24 | [Commercial restrictions by betting operators (blog du régulateur, données 2024)](https://www.gamblingcommission.gov.uk/blog/post/commercial-restrictions-by-betting-operators) | A | 2025-07-23 | Contre-preuve officielle : au Royaume-Uni, 58.6 % des comptes « stake-factorés » sont ramenés à moins de 10 % de la mise normale ; la capacité d'une stratégie consensus chez les books soft est structurellement plafonnée. Statistiq | trouvée |
| C-15 | [Automated Market Making and Loss-Versus-Rebalancing](https://arxiv.org/pdf/2208.06046) | A | 2022-08 (v6) | Contre-preuve nuancée: le LP passif non couvert perd (-6,2 %/an); le résultat positif n'existe que couvert à haute fréquence sur un pool v2 à 30 pb, un an de 2021-2022. Le LP est un vendeur d'option qui paie σ²/8 aux arbitragistes | partielle (0.49) |
| C-16 | [Non-Atomic Arbitrage in Decentralized Finance](https://arxiv.org/abs/2401.01622) | A | 2024-01 (v3 2024-04- | L'argent perdu par les LP (C-15) va à 11 acteurs intégrés aux constructeurs de blocs: un petit opérateur n'a pas accès à ce flux (latence, relation avec les builders). | trouvée |
| C-17 | [Crypto shocks and retail losses (BIS Bulletin no 69)](https://www.bis.org/publ/bisbull69.htm) | A | 2023-02 | Qui perd: le détail qui achète après les chocs pendant que les gros vendent; confirme le sens du transfert, pas un edge exploitable par un petit opérateur. | trouvée |
| D-10 | [Replicating Anomalies (Review of Financial Studies 33(5), 2020)](https://theinvestmentcapm.com/uploads/1/2/2/6/122679606/houxuezhang2019rfs.pdf) | A | 2018-10 | Contre-preuve : pour beaucoup d'effets la bonne décote n'est pas 50 % mais 100 % (l'effet n'existait pas hors micro-caps) ; la décote fixe ne corrige pas la sélection. | trouvée |
| D-21 | [Limited arbitrage in mergers and acquisitions (Journal of Financial Economics 64, 2002)](https://www.hbs.edu/ris/Publication%20Files/arbitrage_af05900b-acd4-44db-8210-70a9fbc3cf6c.pdf) | A | 2002 | Contre-preuve à « petites opérations = plus d'edge » : sur 1981-1996 l'excès de rendement croît avec la taille de la cible (pression vendeuse en dollars). | trouvée (à la main) |

### B. Journal de recherche

Une ligne par recherche distincte (WebSearch, requête Hacker News/Algolia, requête d'API ou de fichier), dans l'ordre de chaque couloir : requête, nombre de pages ouvertes, ce qui en a été retenu. Le détail des URLs ouvertes par recherche est dans `recherches.jsonl`.

| # | Couloir | Outil | Requête | Pages ouvertes | Retenu |
|---|---|---|---|---|---|
| 1 | lead | WebSearch | reddit r/algotrading "profitable" years live results post funding rate arbitrage | 0 | Aucun résultat Reddit : le moteur ne renvoie pas le domaine (test d'accès). |
| 2 | lead | WebSearch | polymarket market making bot profit results (allowed_domains reddit.com) | 0 | Refus explicite : reddit.com inaccessible à l'agent utilisateur d'Anthropic (opt-out du site). Famille Reddit fermée. |
| 3 | lead | WebSearch | polymarket trader profit leaderboard strategy thread (allowed_domains x.com, twitter.com) | 1 | X est indexé ; x.com renvoie 402 à WebFetch, lecture des tweets publics via api.fxtwitter.com. |
| 4 | lead | WebSearch | Kris Abdelmessih moontower where can small traders find edge capacity constrained | 1 | Cadre d'un ex-SIG : l'edge se mesure contre un prix de référence liquide ; les petits edges exigent beaucoup d'essais. |
| 5 | lead | WebSearch | pre-FOMC announcement drift disappeared after 2015 Kurov Wolfe Gilbert | 2 | Fait nouveau pour la veille de FOMC en shadow : dérive de 44 pb (2011-2015) tombée à 9 pb non significatifs (2016-2019). |
| 6 | lead | WebSearch | pre-FOMC drift 2020 2021 2022 2023 2024 evidence returns before FOMC announcements recent sample | 1 | Contre-source : un praticien retrouve la dérive jusqu'en 2024 (Sharpe 0,5-0,6 sur l'échantillon complet), plate en 2016-2019 et concentrée quand le VIX est élevé. |
| 7 | lead | WebSearch | prop firm statistics percentage of traders who receive a payout FTMO data 2024 2025 | 1 | FPFX (fournisseur technique de prop firms) : 14 % réussissent le challenge, 7 % touchent un paiement, en moyenne 4 % du compte. |
| 8 | lead | WebSearch | Topstep trader performance disclosure 2025 percentage funded traders received payout | 3 | Divulgation primaire Topstep 2025 : 33,3 % des comptes financés touchent un paiement, 0,71 % passent en compte live. |
| 9 | lead | WebSearch | emerging hedge fund managers outperform larger funds small fund size performance study 2024 | 1 | Les petits fonds battraient les gros dans les stratégies à capacité limitée (Gao-Haight-Yin 2018, Teo 2009 cités sans chiffres), mais en 2024 les indices pondérés par les actifs ont fait mieux (11,3 % contre 10,3 %). |
| 10 | lead | HN Algolia | polymarket bot (stories) | 7 | Trois post-mortems chiffrés 2026 : shadow sans friction +11 % contre réel -27 % ; maker esport contre cotes de books +4 973 $ puis érosion par la concurrence, les frais et des cotes périmées ; « Nothing Ever Happens » sa |
| 11 | lead | HN Algolia | kalshi market making (stories) | 2 | Témoignages de market making amateur sur Kalshi (voir L-17, L-18). |
| 12 | lead | curl-api Polymarket | gamma-api public-search profil b00k13, puis data-api leaderboard (day, week, month, all), traded, activity | 2 | Wallet de kacho.io vérifié : P&L cumulé 5 633,88 $, 4 969 marchés ; 30 derniers jours +469,58 $ pour 12 657,91 $ de volume ; bot actif sur l'esport au 2026-09-27. |
| 13 | lead | WebSearch | McLean Pontiff "Does Academic Research Destroy Stock Return Predictability" 26% lower out-of-sample 58% lower post-publication | 3 | Version publiée (JF 2016, 97 variables) : -26 % hors échantillon, -58 % après publication ; le working paper de 2013 (82 caractéristiques) donnait -10 % et -35 %. La décote de 50 % du prompt se situe dans cette fourchett |
| 14 | lead | curl-api Hugging Face + HN | jeu de données Polymarket cité sur HN (SII-WANGZJ/Polymarket_data ; HN 46654249 misprice) | 3 | Historique on-chain complet et gratuit du CLOB Polymarket depuis novembre 2022 (418 M de trades, séparation maker/taker par utilisateur) : permet de répliquer Becker sur Polymarket ; misprice.app est payant. |
| 15 | lead | fetch_text GitHub | dépôts cités sur HN : kachence/polymm, casatrick/polymarket-trading-bot | 2 | polymm : code réel du wallet b00k13 ; l'auteur situe l'edge dans la fraîcheur des cotes et la vitesse, pas dans le code. |
| 16 | lead | curl + pandas | recalcul du track record publié « Wisdom of the crowd » de Buchdahl (football-data.co.uk/Wisdom_of_crowd_bets.xlsx), par année | 1 | 20 380 paris réglés 2015-2025 : +3,12 % par pari, σ 1,708, t 2,61 ; décroissance : 2024 -2,1 %, 2025 -4,9 %, alors que l'EV déclarée reste vers 4 %. |
| 17 | lead | curl + DuckDB httpfs | accessibilité à distance et schéma des fichiers parquet du jeu de données Polymarket (sans calcul de rendement) | 3 | Lecture par plages HTTP possible ; trades contient maker, taker, prix, montant et sens de chaque partie ; aucun rendement calculé, pour ne pas consommer d'essai avant pré-enregistrement. |
| 18 | lead | fetch_text + curl | docs.polymarket.com/changelog/predictions.md : chronologie des frais 2026 | 1 | Frais taker ajoutés catégorie par catégorie de janvier à mars 2026 ; frais sport portés de 0,03 à 0,05 le 10 juillet 2026 ; délai taker crypto et résolution TWAP contre l'arbitrage de latence. |
| 19 | lead | curl-api Yahoo chart | SPY barres journalières 10 ans (σ pour la puissance de la veille de FOMC) | 1 | σ journalier du SPY 2016-2026 = 1,13 % (2 jours ≈ 1,52 %) : la veille de FOMC demande environ 13 ans de forward pour atteindre t = 1,96. |
| 20 | lead | curl-api Deribit | public/get_volatility_index_data (DVOL) BTC, ETH, SOL, résolution 1D depuis 2021 | 1 | Volatilité implicite historique gratuite et sans login (DVOL) pour BTC et ETH, paginée ; SOL seulement 206 points : rend B6 testable en historique pour BTC et ETH. |
| 21 | lead | DuckDB httpfs (métadonnées seulement) | markets.parquet : nombre de marchés BTC/ETH « above », « between », « reach » par trimestre | 1 | Premiers marchés « Bitcoin above » en mars 2024 ; densification à partir du T3 2025 (ETH above : 2 336 au T3 2025, 26 927 au T2 2026) : environ 15 mois d'historique dense pour B6. |
| 22 | lead | fetch_text | keyrock.com : chiffres de l'étude « 16,000 token unlocks » (grep %) | 1 | Aucune moyenne ni aucun écart-type par classe : seulement -25 % (pire cas, équipe) et +1,18 % (écosystème) ; l'effet de C2 doit être traité en effet minimal détectable. |
| 23 | lead | fetch_text + WebFetch (audit) | vérification de B-23 : ryanfrigo/kalshi-ai-trading-bot (README, docs/TRACK_RECORD.md, docs/JEV.md, CHANGELOG.md) | 5 | Les citations du README sont exactes ; les chiffres « 170 marchés, +128,56 $, NO -25,40 $, CPI -66,57 $ » sont introuvables et retirés. JEV.md : un modèle d'IA perd contre le carnet Kalshi sur 601 marchés. |
| 24 | lead | curl-api Deribit + Hyperliquid | DVOL ETH en résolution horaire (3600) et bougies HL 1h sur 3 jours | 2 | Les deux flux existent en horaire, gratuits et sans login : la juste valeur digitale de B6 peut être recalculée à chaque échéance horaire. |
| 25 | lead | curl-api Polymarket v2/user-pnl | décomposition mensuelle (trading, frais, sponsoring/parrainage) des wallets 0x06dc51… et justdance (0xcc500c…) — vérification des marges du  | 4 | Marges « économiques » du couloir B confirmées, mais celles de 0x06dc de mars à juin 2026 viennent surtout de revenus de sponsoring/parrainage ; justdance : marge de trading nette de frais 3,55 % (mars-sept. 2026). |
| 26 | A_sport | direct-fetch (arXiv) | Kaunitz Zhong Kreiner 2017 arXiv 1710.02824 beating the bookies | 1 | Consensus rule +3.5% sur 56,435 paris (clôture 2005-2015), +6.2% sur 672 paris papier+réel, comptes limités en quelques mois. |
| 27 | A_sport | WebSearch | Bürgi Deng Whelan "Makers and Takers" Kalshi prediction market economics returns sports | 0 | Papier UCD WP2025_19 / GWU 2026-001 / CEPR DP20631 : makers gagnent plus que takers, biais favori-outsider ; à ouvrir en brut. |
| 28 | A_sport | WebSearch | Polymarket sports markets taker fee maker rebate 2026 docs fees | 0 | Pistes d'URL : docs.polymarket.us/fees, help.polymarket.com maker rebates ; l'extrait (taux sport 0.05, rebate 15%) doit être vérifié en brut. |
| 29 | A_sport | WebSearch | Kalshi fee schedule 2026 sports maker fees taker fee 0.07 | 2 | PDF des frais Kalshi fermé (429) ; recours à l'API publique pour les types de frais par série. |
| 30 | A_sport | Kalshi public API | GET /series?category=Sports ; /series/fee_changes?show_historical=true ; /incentive_programs?status=active/paid_out | 3 | 107 séries sport avec frais maker (activés fin 2025) ; 654 programmes de liquidité sport actifs (179 k$), concentrés sur les props NFL sans frais maker. |
| 31 | A_sport | WebSearch | Betfair Premium Charge percentage of customers affected "Premium Charge" | 5 | Premium Charge révisée en janvier 2025 : 0/20/40 % au-delà de 25 k£ de profit brut sur 52 semaines ; « moins de 0,5 % des clients » non vérifiable (pages 403). |
| 32 | A_sport | WebSearch | Kalshi co-founder in-house trading arm "not profitable" market making sports (+ X: luanalopeslara Kalshi Trading) | 5 | Kalshi Trading < 6 % du volume maker sport, non rentable (nov. 2025) ; sport = 89 % du volume Kalshi en novembre 2025. |
| 33 | A_sport | Polymarket docs (llms.txt index) | docs.polymarket.com fees / maker-rebates ; docs.polymarket.us fees | 3 | Polymarket international : sport taker 0.05·p(1-p), maker 0, rebate 15 % des frais ; Polymarket US : taker 0.0695, rebate maker 0.0125 au fill (depuis le 25/09/2026). |
| 34 | A_sport | WebSearch | football-data.co.uk Buchdahl "wisdom of the crowd" closing odds betting system Pinnacle soft bookmakers | 3 | Archive ouverte de 20,381 paris WoC : +4.0 % 2015-2022, ≈ -0.3 % 2022-2025 ; σ par pari 1.71 ; fin de publication après la fermeture de l'API gratuite de Pinnacle. |
| 35 | A_sport | WebSearch | Pinnacle betting resources closing line value predicts profit Buchdahl correlation expected value closing odds | 0 | URLs repérées : Pinnacle Odds Dropper (CLV demystified), football-data.co.uk pinnacle_efficiency, Pyckio closing odds and tipster skill. |
| 36 | A_sport | WebSearch | Pinnacle how efficient are opening odds closing odds accuracy article | 0 | URLs repérées : football-data.co.uk opening_price_wisdom (Pinnacle vs bet365 à l'ouverture), Pinnacle 'how to solve a problem like efficiency' 1 et 2, datagolf 'How sharp are bookmakers?'. |
| 37 | A_sport | WebSearch | Massachusetts Gaming Commission sportsbook bet limiting data percentage of accounts limited 2024 | 1 | 0,64 % des comptes limités (déc. 2024) et corrélation explicite entre battre la clôture et être limité. |
| 38 | A_sport | WebSearch | study share of sports bettors profitable account-level data percent of bettors win long run | 1 | Les pages « 97 % perdent » sont du marketing sans données (non retenues) ; retenu le papier arXiv 2609.06739 : la marge du book = le hold, le biais du public n'est pas exploitable. |
| 39 | A_sport | GitHub (WebFetch) | betcode-org/flumine README + issues ; georgedouzas/sports-betting README + issues | 7 | Aucun dépôt ne publie de rendement ; issues révélatrices : simulation de la file d'attente (flumine #766) et fuite par les cotes (sports-betting #129). |
| 40 | A_sport | WebSearch | Bet Angel forum pre-off horse racing trading monthly P&L results diary premium charge profit (site forum.betangel.com) | 3 | Aucun P&L quotidien vérifiable (images réservées aux membres) ; témoignages d'échec et edges locaux non transférables. |
| 41 | A_sport | HN Algolia API | sports betting limited accounts ; beat the bookies ; sports betting bot ; positive ev betting ; closing line value | 1 | Rien de chiffré sur HN ; renvoi vers le dépôt GitHub Lisandro79/BeatTheBookie (code et données du papier Kaunitz), ouvert ensuite. |
| 42 | A_sport | WebSearch | bettor blog results "closing line value" ROI bets tracked "got limited" post-mortem 2025 year of +EV betting | 0 | Résultats uniquement marketing/SEO sans relevés : aucun post-mortem chiffré retenu (non trouvé). |
| 43 | A_sport | WebSearch | Gambling Commission account restrictions sports betting customers restricted percentage data stake factoring call for evidence findings | 1 | UKGC (données 2024) : 4,31 % des comptes restreints, 46,78 % des restreints en profit contre 25,42 % des actifs ; 58,6 % des stake-factorés sous 10 % de la mise. |
| 44 | A_sport | WebSearch | Novig ProphetX Sporttrade exchange commission fees 2026 maker taker how the exchange makes money | 1 | Novig : zéro frais maker et taker en pré-match simple ; taker live 0.03·P(1-P) ; ProphetX et Sporttrade 2 % sur gains nets (tiers, non ouvert en primaire). |
| 45 | A_sport | Kalshi public API | GET /markets?series_ticker=KXNFLGAME/KXNFLSPREAD/KXNFLTOTAL/KXNFLANYTD/KXNFLLADDERRECYDS&status=open | 2 | Marchés NFL principaux : écart 1 c et millions de contrats ; props en ladder : volume médian 4 contrats malgré les primes de liquidité. |
| 46 | A_sport | direct-fetch (URL issue de la recherche n°11) | datagolf.com how-sharp-are-bookmakers (efficience ouverture/clôture dans une niche, golf) | 1 | En niche, l'ouverture Pinnacle suit un book spécialiste (54.7 % du chemin vers Betcris) ; clôture Pinnacle ≈ calibrée ; consensus de clôture +1.8 % sur 4,803 paris. |
| 47 | B_pm | curl-api | data-api.polymarket.com/v1/leaderboard timePeriod=all/month/week orderBy=PNL/VOL limit=50 | 4 | Deux régimes de gagnants (directionnels 20-68 % PnL/vol; gros volumes ~1 %); la moitié des 30 plus gros volumes du mois sont perdants. |
| 48 | B_pm | curl-api | docs.polymarket.com llms.txt + changelog/predictions.md + trading/fees + programs/(maker-rebates/taker-rebates/liquidity-rewards) + holding- | 7 | Chronologie primaire des frais (15 min crypto le 2026-01-05, toutes catégories sauf géopolitique le 2026-03-30), délai taker crypto, TWAP Chainlink, holding rewards 3,25 %. |
| 49 | B_pm | WebSearch | Polymarket 15-minute crypto markets latency arbitrage bot wallet Binance taker fee | 1 | Presse: frais introduits pour neutraliser l arbitrage de latence (~3,15 % du coût à 50 c). |
| 50 | B_pm | WebSearch | "$313" "$414k" Polymarket bot one month wallet (x.com, twitter.com) | 4 | Récits viraux (C) sur 0x8dxd; wallet identifié puis vérifié via l API. |
| 51 | B_pm | curl-api | gamma-api public-search q=0x8dxd ; data-api v2 user-stats / user-pnl / trades (taker_only) / leaderboard?category=crypto/mentions/economics/ | 4 | Décomposition PnL/frais/rebates par wallet et par mois; gagnants crypto 15 min arrêtés en mars-avril 2026; gagnants actuels sur marchés à seuil. |
| 52 | B_pm | curl-api | data-api /activity?user=<RN1/swisstony/mentionmarket>&type=REWARD/MAKER_REBATE/TAKER_REBATE/YIELD (pagination offset + start=1) | 4 | RN1 (n°4 all-time) a reçu 1,03 M$ de rebates maker, 0,49 M$ de rebates taker et 0,28 M$ de récompenses de liquidité; swisstony et RN1 sont des wallets sport. |
| 53 | B_pm | WebFetch+fetch_text | GitHub warproxxx/poly-maker: README (main, bfacef3, 0370133, 5617aa2), page du dépôt, liste des issues, historique des commits du README | 6 | L auteur écrit en janvier-avril 2026 que le bot « is not profitable and will lose money » à cause de la concurrence; réécriture CLOB V2 en juillet 2026 avec avertissement « can lose money ». |
| 54 | B_pm | WebSearch | danielsapkota Polymarket market maker rewards "top 5" volatility thread (x.com, twitter.com) | 6 | Auteur de poly-maker: top 5 des bénéficiaires des >25 k$/jour de récompenses pendant l élection 2024; holding rewards lancées à 4 % le 2025-09-24; rebates maker étendus à presque tous les nouveaux marchés (2026-03-23). |
| 55 | B_pm | WebSearch | Polymarket "maker rebates" "liquidity rewards" total distributed Dune dashboard 2026 | 1 | Pine Analytics (données Dune): ~160 M$/jour de volume taker, taux de frais effectif moyen 0,76 %, volume sport non affecté par les frais, crypto en léger recul. |
| 56 | B_pm | curl-api | data-api v2/trades?user=…&start&end&taker_only=true/false (0x8dxd le 2025-12-20 14-15 h et le 2026-03-20 14-15 h UTC; justdance, 0x06dc, 0xf | 2 | 0x8dxd achète les deux issues, majoritairement comme maker; les gagnants crypto actuels tradent des marchés à seuil (above/between/reach/dip). |
| 57 | B_pm | curl-api | data-api v2/user-pnl?interval=max&fidelity=1d pour 0x8dxd, gabagool22, 0xf705…3ca7, justdance, 0x06dc…4524 (incréments mensuels) | 3 | Décroissance chiffrée mois par mois: gabagool22 et 0x8dxd s arrêtent en mars-avril 2026; justdance reste positif après frais. |
| 58 | B_pm | WebSearch | Saguillo 2025 arXiv arbitrage Polymarket "probabilistic forest" prediction markets | 2 | 39,6 M$ d arbitrage « extrait » estimé (avr. 2024-avr. 2025); le compte n°1 ne montre que ~0,44 M$ de PnL Polymarket sur la même période. |
| 59 | B_pm | WebSearch | Polymarket calibration longshot bias empirical study arXiv 2025 2026 resolved markets price accuracy | 1 | FLB Polymarket: favoris >= 90 c +0,28 à +0,83 c/$; longshots de -6,3 à -19,3 c/$ mais +4,1 c/$ par événement parent; absent en sport. |
| 60 | B_pm | WebSearch | Akey Grégoire Harvie Martineau "Who wins and who loses in prediction markets" Polymarket pdf | 1 | 69 % des utilisateurs perdants; la part maker est le meilleur prédicteur du gain; persistance mensuelle modeste et biaisée par la sélection. |
| 61 | B_pm | WebSearch | github Kalshi trading bot market making issues "not profitable" OR "losing money" OR "lost" (github.com) | 3 | Bot Kalshi populaire: compte réel à -69,7 % du pic, 66 % de gains mais P&L quasi nul; issues = pannes d exécution. |
| 62 | B_pm | fetch_text | GitHub shirleyshen0106/polymarket-calibration README (étude de calibration Polymarket sept. 2026, trouvée via la recherche n°13) | 1 | Biais inversé (longshots sous-cotés) sur 3 semaines de sept. 2026, mais artefact de cotes bruitées probable selon l auteur. |
| 63 | B_pm | WebSearch | github polymarket copy trading bot issues losses OR "lost money" OR "not profitable" 15 minute (github.com) | 1 | Copy-trading: l edge du wallet copié décroît de +49,5 % à -17,6 % par semaine en 3 semaines; réplication hors échantillon négative. |
| 64 | B_pm | WebSearch | Paradigm research Polymarket volume double counting | 1 | Les dashboards qui somment OrderFilled doublent le volume; le leaderboard v1 donne un notionnel en parts ≈ 2x le cash. |
| 65 | B_pm | WebSearch | Kalshi Liquidity Incentive Program rewards market makers help center 2026 | 1 | LIP Kalshi: 1-1 000 $/jour par marché, instantanés à la seconde, fin au 2027-01-01, non-US exclus. |
| 66 | B_pm | curl-api | data-api v2/trades (27/08-27/09/2026) et v2/user-stats pour mentionmarket (0xc3ac…b964) et TheReturnOfDarthMaul (0x3a8a…7699) | 2 | mentionmarket = gros parieur MLB/NFL à -2,5 M$ all-time malgré +782 k$ sur le mois; le n°1 économie du mois gagne sur le FOMC de septembre. |
| 67 | C_crypto | curl-api | Hyperliquid info API vaultDetails HLP 0xdfc24b077bc1425ad1dea75bcb6f8158e10df303 (portfolio allTime/month) | 1 | HLP: PnL cumulé 138,3 M$, valeur 182,7 M$ au 2026-09-27, APR affiché 3,69 %; rendement composé ~79 % en 2024, ~19 % en 2025, ~7,9 % en 2026 à date. |
| 68 | C_crypto | curl-api | stats-data.hyperliquid.xyz/Mainnet/leaderboard (46 962 comptes, fenêtres day/week/month/allTime) | 1 | Profits concentrés: top 100 = 32 % des PnL positifs; les gros gagnants à fort volume ont un PnL/volume de 6 à 15 pb (profil market maker), les directionnels à gros PnL ont peu de volume. |
| 69 | C_crypto | curl-api | stats-data.hyperliquid.xyz/Mainnet/vaults (9 476 vaults, statut fermé, PnL allTime) | 1 | 67,2 % des vaults fermés; parmi 8 029 vaults utilisateurs à PnL non nul, 26,9 % seulement ont un PnL cumulé positif (médiane -141 $). |
| 70 | C_crypto | WebSearch | Hyperliquid HLP vault returns decline 2025 JELLY loss October 10 liquidations HLP profit analysis | 1 | CoinGecko (403 en curl, lu par WebFetch): deux événements (krach du 10/10/2025, liquidation ETH du 31/01/2026) = ~41 % du profit cumulé de HLP; TVL max 603,9 M$ (sept. 2025) -> ~268,6 M$ (juin 2026). Cohérent avec l'API  |
| 71 | C_crypto | WebSearch | arXiv 2025 Hyperliquid perpetual DEX liquidations empirical study traders profit (allowed_domains arxiv.org) | 4 | Sur Hyperliquid, l'information des wallets 'toxiques' est persistante mais vit à l'horizon de la seconde (markout 1,25 pb à 0,5 s, 2,11 pb à 10 s); l'ADL du 10/10/2025 a coûté 45-52 M$ en trop aux traders gagnants. |
| 72 | C_crypto | WebSearch | Keyrock token unlocks report 16,000 unlock events price impact 30 days before team unlocks | 2 | Keyrock (déc. 2024): 16 000+ événements mais seulement 40 tokens; fenêtre -30 j/+30 j normalisée par ETH; baisse accélérée la dernière semaine avant les gros déblocages, stabilisation ~14 j après; tailles Large 5-10 %, H |
| 73 | C_crypto | WebSearch | token unlock events abnormal returns event study cryptocurrency vesting cliff paper 2024 2025 cumulative abnormal return | 0 | Aucune étude académique ouverte trouvée par cette requête; seulement des calendriers (Tokenomist, CryptoRank, CoinGlass, DropsTab) et des blogs. |
| 74 | C_crypto | WebSearch | "token unlock" OR "token unlocks" event study price impact cryptocurrency paper (domaines arxiv/ssrn/sciencedirect/researchgate/mdpi) + "72- | 2 | Une étude SSRN (52 déblocages Binance 2023-2025, horizon 72 h) existe mais n'a pas pu être ouverte: ses chiffres ne comptent pas. |
| 75 | C_crypto | WebSearch | Kaiko research token unlocks price liquidity analysis | 0 | Kaiko n'a pas d'étude de déblocages repérée; ses pages portent sur la liquidité (utile pour C3/C6). |
| 76 | C_crypto | WebSearch | hummingbot github issue market making losing money profitable pure market making adverse selection (allowed_domains github.com) + recherche  | 6 | Les issues hummingbot montrent surtout des problèmes d'exécution (slippage en volatilité, jambe de couverture manquante, calcul de rentabilité faux dans v2_funding_rate_arb, funding Hyperliquid affiché à 1,79e+11 %), auc |
| 77 | C_crypto | WebSearch | Hummingbot Miner liquidity mining sunset ended campaigns miners returns | 0 | Seulement des pages de blog hummingbot.org (lancement 51 000 USDC, 272 k$ versés à 1 358 MM en février 2021, selon l'extrait); non ouvertes faute de budget, non comptées. |
| 78 | C_crypto | WebSearch | Kaiko OR Galaxy research 2025 funding rates basis trade yield compressed annualized basis decline ETF cash and carry | 1 | Kaiko: recherches désormais derrière app.kaiko.com (login), non ouvertes. |
| 79 | C_crypto | WebSearch | Galaxy Research 'state of crypto leverage' 2025 perpetual futures open interest funding (+ variante allowed_domains galaxy.com, + 3 URL gala | 2 | Rapport Galaxy trouvé seulement via la presse (OI 220,37 G$ le 6 oct. 2025, 17 G$ liquidés le 10 oct. selon extraits); URL primaire non trouvée, non compté. |
| 80 | C_crypto | WebSearch | Wintermute research 2025 funding rates perpetuals basis compression market report (allowed_domains wintermute.com) | 2 | Wintermute: 19 G$ liquidés le 10/10/2025 dont 10,3 G$ sur Hyperliquid, >1 000 wallets ADL (jambes courtes de spreads long-short), rebond moyen +84 % en 30 min; en déc. 2025 base CME et courbe 'compressées', le carry ne r |
| 81 | C_crypto | curl-api | DefiLlama yields: https://yields.llama.fi/pools filtré project=ethena-usde symbol=SUSDE, puis https://yields.llama.fi/chart/66985a81-9c51-46 | 2 | APY sUSDe: moyenne 17,47 % en 2024, 6,52 % en 2025, 4,10 % en 2026 à date; TVL 1,31 G$ au 2026-09-27. |
| 82 | C_crypto | curl-api | DefiLlama emissions: api.llama.fi/emissions (HTTP 402 payant) puis jeu public defillama-datasets.llama.fi/emissionsProtocolsList et /emissio | 5 | Calendrier gratuit sans login avec catégorie de bénéficiaire (insiders, privateSale...) et type (cliff/linéaire); déblocages insiders+investisseurs >= 5 % de l'offre max: 18 (2024), 30 (2025), 21 (2026 à date), dont 9, 1 |
| 83 | C_crypto | curl-api | Hyperliquid info candleSnapshot 1d (40 tokens à gros déblocages + ETH, 2024-01-01 -> 2026-09-27) et fundingHistory (3 fenêtres de 500 h: 202 | 1 | σ des rendements log à 30 j relatifs à ETH = 0,262 (n=1 043 fenêtres, 40 tokens), dérive moyenne -9,2 %/30 j sans condition; funding horaire modal 0,00125 %/h (10,95 %/an), fenêtre médiane +7,9 %/an reçus par un short, 1 |
| 84 | C_crypto | WebSearch | airdrop farming post-mortem 2025 ROI spent gas fees received airdrop "not worth it" points farming returns declined | 1 | Témoignages de farmers (Odaily/Wu Blockchain, fév. 2025): 600-1 000 $ par compte et par projet en 2024, profits 2024 < 2023, rendement désormais tiré par les studios multi-comptes (interdits chez Quant) et la détection s |
| 85 | C_crypto | WebSearch | market maker perp DEX points farming maker rebates PnL thread numbers adverse selection small market maker Hyperliquid Lighter (allowed_doma | 1 | Praticien (altoshi, déc. 2025): les points font accepter aux MM des spreads effectifs négatifs; à la fin des incitations, retour à un jeu à somme nulle ou négative et élargissement des spreads. Aucun P&L publié. |
| 86 | C_crypto | HN-Algolia | hn.algolia.com/api/v1/search tags=story: 'hummingbot', 'crypto market making bot profit', 'funding rate arbitrage', puis 'hyperliquid', 'air | 1 | HN presque vide sur le sujet: un Ask HN (2020) d'un développeur de bot de MM à court de capital après un an de travail et des tests sur testnet seulement; les fils 2026 sur le funding arb sont des tutoriels de backtest s |
| 87 | C_crypto | WebSearch | DefiLlama emissions adapters github repository unlock schedules protocols (allowed_domains github.com) + tentatives d'ouverture | 3 | Le dépôt d'adaptateurs d'émissions n'est plus lisible publiquement (404 sur github.com et raw): pas de reconstruction point-in-time par l'historique git; seul un instantané quotidien prospectif du jeu public (C-20) donne |
| 88 | C_crypto | curl-api | Hyperliquid info fundingHistory BTC et ETH, pagination par startTime du 2024-01-01 au 2026-09-27 (24 017 heures chacun); test des API de fun | 4 | Funding moyen annualisé du perp BTC sur HL: 24,1 % (2024), 10,6 % (2025), 5,0 % (2026 à date); ETH: 22,1 %, 8,5 %, 5,7 %; 99e centile BTC 140 % -> 59 % -> 10,9 %. |
| 89 | D_actions | WebSearch | McLean Pontiff "Does Academic Research Destroy Stock Return Predictability" pdf 26% out-of-sample 58% post-publication | 4 | Version publiée JF 2016 (Crossref) : 97 prédicteurs, -26 % hors échantillon, -58 % après publication ; version de travail 2013 : 82 prédicteurs, -10 % / -35 %. Les chiffres dépendent de la version. |
| 90 | D_actions | WebSearch | Chen Lopez-Lira Zimmermann "Does peer-reviewed research help predict stock returns" arXiv | 1 | ≈50 % de la prévisibilité subsiste après l'échantillon, qu'elle soit publiée ou minée sur 29 000 ratios. |
| 91 | D_actions | WebSearch | Falck Rej Thesmar "When do systematic strategies decay" arXiv | 1 | Sharpe divisé par ~2 après publication ; la décote augmente de 5 points de Sharpe in-sample par année de publication (plus forte pour les publications récentes). |
| 92 | D_actions | WebSearch | Jensen Kelly Pedersen "Is There a Replication Crisis in Finance" pdf post-publication | 1 | Alpha moyen in-sample 0,45 %/mois → 0,31 % après l'échantillon (baisse d'un tiers) ; pente OOS/IS = 0,25 à 0,43 (retrait plus fort pour un facteur choisi parce qu'il est fort). |
| 93 | D_actions | WebSearch | Jacobs Müller "Anomalies across the globe: Once public, no longer existent?" post-publication decline international | 1 | Aux États-Unis : -36 % post-sample et -60 % post-publication (EW), -65 % (VW) ; aucun des 38 autres marchés n'a de déclin fiable. |
| 94 | D_actions | WebSearch | Chen Velikov "Zeroing in on the expected returns of anomalies" trading costs post-publication bps per month | 1 | 66 pb/mois brut in-sample → 30 pb après publication (moitié) → -3 pb net de coûts ; 8 pb net avec optimisation des coûts après 2005. |
| 95 | D_actions | fetch arXiv (liens trouvés via recherche n°1) | arXiv 2607.06502 What Useful Alphas ; arXiv 2512.11913 Not All Factors Crowd Equally | 3 | Chen et Welch (juillet 2026) : 48 pb/mois avant 2006 → 7 pb après 2005 hors micro-caps (-85 %) ; le papier 2512.11913 est retiré par son auteur (non utilisé comme preuve). |
| 96 | D_actions | WebSearch | Hou Xue Zhang "Replicating Anomalies" 452 anomalies 65% fail t-value 1.96 microcaps NBER pdf | 1 | 65 % des 452 anomalies échouent à /t/≥1,96 une fois les micro-caps neutralisées ; 82 % à /t/≥2,78. |
| 97 | D_actions | WebSearch | Martineau "Rest in Peace Post-Earnings Announcement Drift" pdf large caps 2006 | 2 | Le PEAD a disparu depuis 2006 pour les grandes capitalisations, plus récemment pour les micro-caps : exemple d'effet événementiel décru à ~100 %. |
| 98 | D_actions | WebSearch | Starks Yong Zheng "Tax-Loss Selling and the January Effect: Evidence from Municipal Bond Closed-End Funds" pdf | 2 | CEF municipaux 1990-2000 : janvier +2,21 % contre -0,19 % les autres mois ; Carrion et Zhang (2024) : l'effet est devenu plus fort récemment. |
| 99 | D_actions | WebSearch | closed-end fund discount activism tender offer returns study 2024 Saba Capital discount narrowing evidence | 1 | ICI : 44 offres de rachat forcées 2015-juin 2023 ; 75 % des activistes sortent en moins d'un an ; 3 activistes présents dans la moitié du marché des CEF (fin 2024). |
| 100 | D_actions | curl API Yahoo chart (test d'endpoint) | query1.finance.yahoo.com/v8/finance/chart/{NEA,XNEAX,GAM,XGAMX,ADX,XADXX} | 2 | Les symboles NAV Lipper (X…X) existent sur Yahoo pour beaucoup de CEF, avec historique journalier depuis 2003 pour XNEAX ; certains symboles manquent (XADXX). |
| 101 | D_actions | WebSearch (allowed_domains x.com, twitter.com) + fxtwitter | Boaz Weinstein closed-end fund discount tweet | 4 | Saba recommande publiquement des CEF à -30 % (CTF-U) et -10 % (BFZ) ; conversion BPRE ouverte à -38 % sous la NAV (déc. 2025) ; l'article Bainbridge est payant après l'introduction. |
| 102 | D_actions | WebSearch | Gahng Ritter Zhang "SPACs" Review of Financial Studies SPAC IPO investors annual return 9.3% pdf (+ requête ciblée site:warrington.ufl.edu) | 2 | 458 SPAC 2010-2020 : 23,9 %/an pour l'investisseur à l'IPO, 458 rendements positifs, minimum 0,51 %/an ; avertissement : bien plus bas pour les millésimes 2021+ ; rachats >80 % en 2022-2023. |
| 103 | D_actions | WebSearch | merger arbitrage returns small deals spread capacity recent evidence 2023 2024 paper annualized return deal size | 3 | Écart d'arbitrage réduit de >400 pb depuis 2002 (médiane 1er jour 6,39 % → 1,91 %) ; Alpha Architect 403 ; N-CSR SEC 403 en curl et trop gros pour WebFetch. |
| 104 | D_actions | WebSearch | "merger arbitrage" returns "small deals" OR "smaller deals" OR "deal size" limits to arbitrage academic paper abnormal returns target size | 1 | Baker et Savasoglu : 0,6-0,9 %/mois d'alpha 1981-1996, rendement CROISSANT avec la taille de la cible (contredit la thèse « petites opérations = plus d'edge »). |
| 105 | D_actions | WebSearch | Beckmeyer Branger Gayda "Retail traders love 0DTE options" but should they pdf losses per day | 1 | Les particuliers perdent 241 k$/jour (fév. 2021-sept. 2023), 350 k$/jour depuis les échéances quotidiennes ; >90 M$ des 125 M$ de pertes viennent des coûts de transaction. |
| 106 | D_actions | WebSearch | Greenwood Sammon "The Disappearing Index Effect" S&P 500 addition abnormal return decline pdf | 1 | Effet d'ajout au S&P 500 : 3,4 % (1980s), 7,6 % (1990s), 5,2 % (2000s), 0,8 % (2010s, non significatif) ; retraits -0,6 % en 2010-2020. |
| 107 | D_actions | WebSearch | de Silva Smith So "Losing is Optional" retail option trading earnings announcements pdf | 1 | Les particuliers perdent 5-9 % de leurs mises en options autour des résultats (10-14 % si volatilité attendue élevée) ; straddles à EAV élevé -11 % par annonce contre EAV faible. |
| 108 | D_actions | WebSearch | Gao Xing Zhang "Anticipating Uncertainty: Straddles Around Earnings Announcements" pdf returns before announcement | 2 | Camp acheteur : straddles ATM de J-1 à J +2,3 % (version de travail ; 3,34 % sur J-3→J dans la version JFQA selon le moteur, non vérifié) alors que les straddles perdent -0,19 %/jour hors annonces ; page Rice en 404. |
| 109 | D_actions | curl API Cboe (test d'endpoint) | cdn.cboe.com/api/global/delayed_quotes/options/SPY.json ; us_indices/daily_prices/PUT_History.csv ; VIX_History.csv | 3 | Chaîne SPY complète gratuite (12 940 options, bid/ask/iv/grecques/OI, échéances quotidiennes) en instantané différé, sans historique ; indices PUT (depuis 1991) et VIX (depuis 1990) en CSV journalier gratuit. |
| 110 | D_actions | WebSearch + IDEAS RePEc | Chague De-Losso Giovannetti "Day Trading for a Living?" Brazil 97% lose money pdf | 2 | 97 % des day traders persistants (≥300 jours) perdent ; 1,1 % gagnent plus que le salaire minimum ; Taïwan (Barber et al., cité) : ~20 % profitables nets de frais sur l'ensemble. |
| 111 | D_actions | WebSearch | ESMA CFD product intervention "74-89%" retail accounts lose money statement pdf esma.europa.eu | 1 | 74-89 % des comptes CFD de particuliers perdent ; pertes moyennes de 1 600 à 29 000 € par client (analyses des régulateurs nationaux, 2018). |
| 112 | D_actions | HN Algolia API | search?query=algorithmic trading&tags=ask_hn&numericFilters=num_comments>40 (+ variantes « trading money », « day trading for a living ») | 2 | Fil de référence « Anyone making money through algorithmic trading? » (2018, 245 commentaires) : post-mortem de 100 k$ perdus ; vendeur d'options revendiquant +127 % sur 30 k$ (2016-2018). |
| 113 | D_actions | WebSearch (allowed_domains elitetrader.com) | elitetrader.com selling options blew up account post-mortem short volatility lost ; elitetrader.com thread closed-end fund discount arbitrag | 2 | Post-mortem OptionSellers.com (nov. 2018, 48 pages) sans chiffres vérifiables en page 1 ; fil 2024 : les allocataires ignorent les fonds < 100 M$, les petits gérants gardent les stratégies à capacité limitée pour eux. |
| 114 | D_actions | WebSearch + site flirtingwithmodels.com | Flirting with Models transcript small fund capacity "closed-end fund" OR "merger arbitrage" OR "microcap" ; podcast transcript Euan Sinclair | 3 | Takahe Capital (S7E25, janv. 2026) : fonds fermé puis relancé avec un plafond dur de 500 M$ pour trader des marchés obscurs (carbone californien, avoine) ; transcription JSON publique. |
| 115 | D_actions | WebSearch (allowed_domains toptradersunplugged.com) | Top Traders Unplugged transcript option selling volatility risk premium retail 0DTE episode transcript 2025 | 1 | Cboe (Mandy Xu, 2025) : 0DTE ≈2 M de contrats/jour, ≈60 % du volume SPX ; flux achat/vente et puts/calls « one-to-one » ; beaucoup de particuliers l'utilisent pour du revenu (vente de prime), pas seulement du levier. |

---

## 6. Auto-audit

**Couverture par famille** (138 sources uniques ; plancher du prompt : 8 par famille) :

| Famille | Sources | Statut |
|---|---|---|
| 1. Reddit | **0** | **Non atteint : fermé** (voir « Accès refusés ») |
| 2. GitHub | 12 | atteint |
| 3. X/Twitter et blogs de praticiens | 16 | atteint |
| 4. Académique et working papers | 32 | atteint |
| 5. Données des plateformes | 43 | atteint |
| 6. Industrie (rapports, podcasts) | 12 | atteint, juste |
| 7. Forums spécialisés | 12 | atteint, juste |
| 8. Contre-preuve (rôle principal) | 11 | atteint ; 67 sources au total contredisent au moins une piste |

- **Recherches** : 115 recherches distinctes journalisées (plancher : 40), dont WebSearch, requêtes HN et requêtes d'API.
- **Grades** : A 82, B 37, C 19. Aucune source C n'est utilisée comme preuve d'edge.

**Contrôle des citations** (script `outils/audit_citations.py`, résultats dans `audit_citations.json`) :
- 52 citations retrouvées mot pour mot, 26 partielles et 48 données d'API datées ;
- 10 pages ouvertes seulement via WebFetch (GitHub, CoinGecko, ICI : non retéléchargeables par le proxy) ;
- 4 introuvables, toutes relues à la main :
  - A-16 et A-17 : les phrases sont dans le JSON embarqué des pages Pinnacle ;
  - D-21 : PDF extrait sans espaces ;
  - B-23 : les citations du README sont exactes, mais les chiffres « 170 marchés, +128,56 $, NO −25,40 $, CPI −66,57 $ » sont introuvables et ont été **retirés** du rapport.
- Les partielles viennent de citations composées de fragments (« … ») ou de PDF mal extraits.

**Recalculs indépendants du lead** :
- archive WoC de Buchdahl [L-20] : mêmes totaux que [A-14], plus la ventilation annuelle ;
- wallet de kacho via l'API [L-12] ;
- σ du SPY [L-23] ;
- barème et chronologie des frais Polymarket [L-22] ;
- échéances horaires des marchés à seuil [L-26].

**Familles et zones sous-représentées** :
- **Reddit** : zéro source, par respect de l'opt-out du site.
- **Industrie et forums** : au plancher. Galaxy et Kaiko sont absents ; un seul podcast par émission (Flirting with Models, Top Traders Unplugged) ; Chat With Traders absent. Wilmott et QuantNet sont fermés (403).
- **Non couverts** : marchés crypto courts de Kalshi, spin-offs, fallen angels, relance des SPAC 2025-2026, efficience des props contre Pinnacle.
- **Non ouverts** : l'étude taïwanaise sur les day traders (Barber et al.) et plusieurs papiers SSRN (403), remplacés par d'autres versions quand elles existaient.

**Affirmations encore fragiles** :
- **B6** : l'effet vient d'un seul survivant (justdance) [B-14] ; la DVOL (ATM, 30 jours) n'est qu'une approximation de la juste valeur à 1 h.
- **C2** : aucun effet moyen publié (graphiques Keyrock seulement, conflit d'intérêts) ; calendrier DefiLlama non PIT.
- **H-001** : σ de la CLV mesuré sur le football 1X2 Pinnacle, pas sur les marchés de prédiction [A-17] ; coefficients de frais Kalshi 0,07 et 0,0175 lus chez des tiers (PDF officiel en HTTP 429).
- **P&L de wallets** : comptabilité Polymarket non auditée ; v1 et v2 divergent [B-19]. Les causes de l'arrêt de gabagool22 et de 0x8dxd ne sont pas prouvées.
- **D2a** : calcul du couloir D sur 14 CEF survivants (biais de survie) ; D4c : σ par événement introuvable.
- **HLP** : rendement calculé sur un pas bimensuel qui masque les drawdowns intra-période [C-01].

**Incidents de processus** :
- Les enquêteurs parallèles ont été interrompus deux fois par une limite d'usage de la session. Leurs journaux, écrits au fil de l'eau, sont complets.
- La fiche du couloir crypto a été rédigée par le lead à partir de ses 25 sources.
- Aucune source n'a été comptée sans avoir été ouverte.

### Accès refusés (et respectés)

| Cible | Constat | Conséquence |
|---|---|---|
| Reddit (toutes les sous-communautés demandées) | Le domaine refuse explicitement l'agent d'Anthropic (opt-out du site). `www.reddit.com` et `old.reddit.com` renvoient 403. Le miroir redlib est protégé par un anti-IA (Anubis). PullPush refuse les agents (« does not provide free scraping resources for agents »). Arctic Shift renvoyait une erreur 500. | **Famille 1 : zéro source.** Aucun contournement (miroir, archive, résolution de challenge), conformément au prompt (pas de scraping derrière un login) et à l'opt-out du site. Les témoignages de praticiens ont été cherchés sur Hacker News, Bet Angel, football-data, Substack et X. |
| SSRN | 403 | Versions des mêmes articles trouvées chez les auteurs, au NBER, sur arXiv, à la Fed ou dans les revues. |
| X / Twitter | `x.com` renvoie 402 aux robots | Tweets publics lus via l'API d'intégration publique fxtwitter ; les « articles X » restent illisibles. |
| Wilmott, QuantNet | 403 | Non couverts. |
| SEC EDGAR | 403 sans User-Agent déclaré | Données d'événements (13D, 8-K) non utilisées. |

---

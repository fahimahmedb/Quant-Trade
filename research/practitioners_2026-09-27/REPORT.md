# Comment les praticiens gagnants y parviennent réellement (2026-09-27)

**Statut** : recherche de lab indépendante, paper/shadow uniquement. Ce rapport n'accorde aucune autorité de capital.
**Annexe** : toutes les sources (S01-S94, URL, famille, grade, extrait) et le journal des 68 étapes de recherche sont dans `SOURCES.md` (même dossier). Les références « Sxx » renvoient à cette annexe.
**Périmètre** : petits opérateurs (1-10 personnes, 10 k$-5 M$), 2024-2026, données publiques gratuites. Les pistes déjà testées ou rejetées (§1 du brief) ne sont pas reproposées, sauf fait nouveau signalé.
**Colonne France** : « Accès légal depuis la France (compte réel) ». C'est une information de classement, pas un filtre de la recherche papier. Aucun contournement n'est proposé.

---

## 1. Synthèse : les schémas récurrents de ceux qui gagnent vraiment

1. **Ils sont makers, face à des takers impatients ou joueurs.** Sur Polymarket (588 M de trades), le top 0,1 % fait 47,3 % de son volume en ordres limites, contre 17,1 % pour les 95 % du bas. Chaque écart-type de part maker ajoute +9 pp à la probabilité d'être gagnant (A, S22). Même constat chez Becker sur Kalshi (S30), Whelan (makers −9,6 % contre takers −31,5 %, S34), Bartlett-O'Hara (makers +1,91 ¢/contrat sur les marchés single-name, S86-S87) et pour les 0DTE (S25).
2. **Le flux le plus « payant » est le flux loterie.** Combos Kalshi : 19 ¢ perdus par dollar contre 6 ¢ en paris simples, et −294 M$ pour le retail en 7 mois (S67). Un market maker indépendant y revendique « seven figures a month » (S67, preuve B). Autres flux du même type : YES sur-acheté (S87), 0DTE à une jambe (S25), longshots.
3. **Ils se spécialisent dans des niches où une juste valeur existe mais où l'attention institutionnelle manque.** Les n° 2, 4 et 5 du classement Polymarket de tous les temps tradent du sport de niche : K-League, ITF, Liga MX, football universitaire US (A, S37-S41). 42 des 100 meilleurs wallets concentrent leurs gains, dont 81 % en sport (S22). À catégorie donnée, se spécialiser augmente la probabilité de gain de +5,5 pp (S22). Domer, lui, cherche les marchés « nouveaux et peu familiers » (S14).
4. **La rente suit la nouveauté et se ferme en 12 à 24 mois.**
   - Kalshi : les takers gagnaient (+2,0 %) avant fin 2024 (S30).
   - Le bot esports de kacho est passé de 2 506 $/mois à 180 $/mois après l'arrivée des frais et des concurrents (S59).
   - L'EV contre Pinnacle ne donne plus que 1,9 % réel contre 4,2 % attendu depuis 2023/24 (S83).
   - Le carry crypto avait un SR de 6,45, il est devenu négatif en 2025 (S26).
   - Les spreads de merger arb ont perdu plus de 400 bp (S49).
5. **Le goulot est l'exécution et l'infrastructure, pas l'idée.**
   - RFQ Kalshi : 13 quoteurs, presque tous à moins de 200 ms (S66).
   - Les bots open source n'ont aucun edge démontré et accumulent les bugs de fills et de reconnexion (S01-S05, S10).
   - Chez kacho, les jambes non couvertes ont perdu malgré un « edge » de 7 % au moment du trade (S59).
   - La plateforme reprend une part de la rente : frais makers depuis avril 2025 (S34), frais makers sur combos, soit 26 M$ en 4 semaines (S68).
   - Et ce n'est pas gratuit : Kalshi Trading, le MM maison, n'est « pas rentable » (S53-S54).

Conséquence pour Quant : la seule famille qui combine **mécanisme vérifié (A), rente encore mesurée en 2026 et statistique à faible variance** est la **fourniture de liquidité**, évaluée en **markouts et CLV** contre une juste valeur sharp, **par catégorie**. Tout ce qui est carry, événement calendaire crypto ou arbitrage mécanique est soit décru, soit une course de latence.

**Contrainte française majeure** :
- Polymarket est bloqué par l'ANJ depuis le 2026-07-16 (S71).
- Kalshi exclut la France (S72).
- Pinnacle et Betfair ne sont pas agréés (S74).
- Les perps crypto sont hors MiCA et assimilés à des CFD (S73).

Toutes les pistes recommandées sont donc **papier/shadow seulement** pour un résident français ; aucune n'offre aujourd'hui d'accès réel légal.

---

## 2. Tableau des pistes classées (17 évaluées, 4 recommandées)

`expected_t` = effet (source, réduit de 50 %) / σ × √n, pour 1 essai, seuil 1,96. « Hyp. » signale un σ supposé, faute de source (à calibrer sur les 2 premières semaines de forward).

| # | Piste | Mécanisme | Qui perd | Preuve (grade, nb sources) | Décroissance | expected_t historique | Forward (délai) | Données | Capacité | Accès légal FR (compte réel) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | **Rente maker par catégorie, hors échantillon publié (Kalshi)** | Les makers encaissent spread + surplus YES | Takers impatients, acheteurs de YES | A ×5 (S30, S34, S86, S87, S22) | Inversion 2024 (S30) ; frais makers depuis avr. 2025 (S34) | Règlement : 0,94 (2 000 événements) à 1,89 (8 000) → **UNDERPOWERED** au niveau événement si n < 8 600 ; markouts : n = 38 suffit | Continu (données publiques) | Kalshi `GET /historical/trades` (taker_side), gratuit (S88) | Diagnostic, non tradé | Non : France exclue (S72) | **TESTER** (réplication hors échantillon, 1 essai) |
| R2 | **Maker papier sur sport de niche, juste valeur sharp (PM et Kalshi)** | Coter autour du consensus sharp sans marge ; les takers paient le spread | Takers sport retail | A ×4 (S22, S30, S37-S41), B ×2 (S59, S13) ; contre : S53, S94, S59 | Forte (S59, S83) | 0,22 (1 mois hors échantillon) → **UNDERPOWERED** | **t ≈ 1,96 en ~300 marchés, ≈ 2,7 en 600 (2-3 mois)** | Carnet PM/Kalshi en WebSocket (forward) + Odds API | 10-50 k$ (S81 : profondeur faible) | Non (S71, S72) | **FORWARD SEULEMENT** |
| R3 | **Pricing papier des combos (RFQ Kalshi) contre produit corrélé des jambes sharp** | Le retail paie 19 ¢/$ ; les makers majorent de 2,76 % | Acheteurs de parlays | B ×3 (S66-S68), A ×1 (S69) ; contre : S68, S82, S94 | Majoration × 4 après les frais du 2026-08-20 (S68) | n.d. (historique RFQ non public) | CLV combo : **n ≈ 580 combos (< 1 semaine)** ; P&L : 181 000 → UNDERPOWERED | Flux RFQ : **authentification requise** (S92) → à vérifier | Grande (68 M$/j de taker combos, S68) | Non (S72) | **FORWARD SEULEMENT, sous condition d'accès aux données** |
| R4 | **Récompenses de liquidité (PM rewards, Kalshi LIP) comme ligne séparée de R2** | Subvention de plateforme aux carnets à deux faces | La plateforme (budget marketing) | A ×2 (règles S16, S35), B ×1 (S11), C ×1 (S78) | « Thin bonus » avec la concurrence (C) | Non calculable (pas de donnée A de rendement net) | Mesure journalière dès J+1 dans R2 | Configuration des récompenses par marché + snapshots carnet (forward) | 1-1 000 $/marché/jour (S35) | Non (S71 ; LIP réservé aux US, S35) | **FORWARD SEULEMENT** (ligne du Book) |
| 5 | Mention markets (fréquence historique des mots) | Base rate issu des transcripts contre prix | Acheteurs de YES | C ×1 (S51) ; contre : S76 (manipulation par l'orateur) | Inconnue | 0,32 (≈ 300 appels) → UNDERPOWERED | Plusieurs années | Transcripts (sources gratuites non vérifiées) + Kalshi | Faible (84 k$ misés sur Coinbase, S76) | Non | **REJETER** (C + manipulable) |
| 6 | Merger arb, petits deals (EDGAR) | Prime de liquidité et de risque de rupture | Actionnaires cibles qui vendent tôt | A ×2 (S49, S77), B ×1 (S70) ; contre : S49, S91 | −400 bp depuis 2002 (S49) | 1,11 (220 deals 2021-26) → UNDERPOWERED ; 17 ans pour t = 1,96 | Non (≈ 40 deals/an) | EDGAR gratuit, prix quotidiens | 1-20 M$ | Oui en principe (actions US via courtier agréé) ; source non ouverte → à vérifier | **REJETER** (puissance) |
| 7 | Short des déblocages de tokens | Offre nouvelle vendue par les bénéficiaires | Détenteurs pendant le déblocage | B (S45), A (S75) | Anticipé à −14,7 % dès J−30 (S75) | 1,09/an ; ≈ 3,2 ans nécessaires | Lent | Calendrier non point-in-time ; perps | 10-300 k$ | Non / à vérifier (perps, S73) | **REJETER** |
| 8 | Suivi des wallets « toxiques » Hyperliquid | Identité publique ⇒ persistance du flux informé | MM lents | A (S65) | n.d. | Non exécutable (horizon 1 s) | — | S3 Reservoir, avec wallet (S90) | — | Non / à vérifier (S73) | **REJETER** (course de latence) |
| 9 | Carry funding / basis crypto | Demande de levier retail | Longs à levier | A ×3 (S26, S27, S57) | SR 6,45 → 4,06 (2024) → négatif (2025) | ≤ 0 | — | Binance, HL | Grande | Non (perps) | **REJETER** (plancher, déjà connu) |
| 10 | Dépôt dans le vault HLP | MM de plateforme + liquidations | Traders liquidés | A (S44) | 41 % des profits sur < 2 semaines | ≈ 2 événements/an → non testable | — | API vaultDetails | Grande | Non / à vérifier | **REJETER** (bêta d'événements) |
| 11 | Favoris > 90 ¢ sur Polymarket (FLB) | Biais favori/outsider | Acheteurs de longshots | A (S32) | Absent en sport ; signe instable | n ≈ 23 700 événements pour t = 1,96 | — | Polymarket-v1 (S79) | Faible | Non | **REJETER** (≈ « bonding » déjà rejeté) |
| 12 | « Nothing ever happens » : NO partout hors sport | 73 % des marchés résolvent NO | — | C (S60) | — | Backtest avec anticipation ; −5 % en réel | — | — | — | Non | **REJETER** |
| 13 | Books soft +EV contre Pinnacle (hors PM) | CLV contre les books de loisir | Books soft | B (S15, S83) ; contre : S56, S83 | 4,2 % → 1,9 % réalisé depuis 2023/24 (S83) | n.d. (limitation de compte) | Non exécutable | football-data | Limitée par les restrictions (S56) | Pinnacle non ; books ANJ oui mais limitent | **REJETER** comme piste ; garder la CLV comme statistique pour H-001 |
| 14 | Juste valeur esports tirée de books soft contre PM | Écarts de 20-30 ¢ entre venues | Takers PM | B (S59) ; contre : S59 | 2 506 $ → 180 $/mois (S59) | Négative hors arbitrage couvert (−3 185 $) | — | Books soft | < 10 k$ | Non | **REJETER** : un book soft n'est pas une juste valeur |
| 15 | Latence sur les marchés crypto 15 min de PM | Retard du prix PM sur le spot | Makers lents | C (S84) | Tuée par les frais taker de 1,80 % (S42, S17) | — | — | — | — | Non | **REJETER** |
| 16 | Arbitrage de trust SPAC | T-bill + option gratuite | Vendeurs pressés | B (S50) | Spread médian ≈ 0-5 %, > 10 % seulement en crise | — | — | EDGAR | Moyenne | Oui en principe (courtier), à vérifier | **REJETER** (plancher, pas un edge) |
| 17 | Copy-trading des meilleurs wallets PM | Persistance des gagnants | Suiveurs | A (S22 : persistance modeste, possible sélection) ; C (S52) | — | Les gagnants sont makers : on ne peut pas copier un fill maker en taker | — | data-api | — | Non | **REJETER** |

---

## 3. Fiches des pistes recommandées

### R1 — Rente maker par catégorie sur Kalshi, hors échantillon publié (réplication)

**Pourquoi d'abord.** C'est le test le moins cher et le plus informatif : il dit **où** (quelle catégorie, quel type de marché) la rente maker existe encore après publication, avant de construire un moteur de cotation.

**Mécanisme en une phrase.** Les takers paient le spread et sur-achètent le YES (60,9 % du volume, pour 32,5 % de règlements YES dans les marchés single-name, S87). Les makers encaissent 1,91 ¢/contrat en single-name et 0,82 ¢ en broad-based (S87), soit +1,12 % en sport contre +0,08 % en finance (S30).

**Expression unique.** Rendement moyen au règlement du **côté maker** de tous les trades Kalshi, **par catégorie Kalshi**, sur la fenêtre **2026-04-17 → 2026-09-26** (postérieure au papier Bartlett-O'Hara du 2026-04-16), net de la grille de frais makers en vigueur. On reprend telle quelle la catégorisation de la source (single-name contre broad-based, et les 8 catégories de Becker), sans optimisation.

**Données exactes.**
- `GET https://api.elections.kalshi.com/trade-api/v2/historical/trades` et `/markets/trades` (champ `taker_side`) ;
- `GET /historical/markets` (résultat) ;
- `GET /historical/cutoff` (S88).

Ces données sont gratuites et point-in-time : horodatage du trade et règlement publié.

**Puissance (détail).**
- Effet : 1,91 ¢ × 0,5 = **0,95 ¢/contrat** (single-name).
- σ du P&L au règlement par événement : ≈ 45 ¢ (binaire à p ≈ 0,3, hypothèse).
- n requis pour t = 1,96 : (1,96 × 45 / 0,95)² ≈ **8 600 événements indépendants**.
- À 2 000 événements : t = 0,94 ; à 8 000 : t = 1,89. **UNDERPOWERED si la fenêtre contient moins de 8 600 événements indépendants** (à compter).
- Statistique à faible variance : markout du côté maker à +1 h (σ supposé ≈ 3 ¢) ; n = 38 marchés suffisent. Mais ce markout ne mesure que la capture de spread, pas le surplus comportemental réalisé au règlement.

**Capacité / coûts.** C'est un diagnostic, sans capital. Coût : pagination de l'API.

**Contre-preuve.**
- Kalshi Trading, MM maison, n'est « pas rentable » (S53-S54).
- Les frais makers existent depuis avril 2025 (S34).
- Des concurrents professionnels bénéficient de frais réduits et de limites plus hautes (S94).
- Les takers gagnaient avant l'élection de 2024 (S30) : la rente peut s'inverser.

**Risque principal.** Confondre surplus comportemental et bêta d'outcome : quelques gros règlements dominent. Il faut regrouper par événement.

**France.** Pas de compte légal (S72) ; seule la lecture de données publiques est concernée.

### R2 — Maker papier sur sport de niche, juste valeur = consensus sharp sans marge (Polymarket et Kalshi)

**Mécanisme.** Les gagnants de Polymarket sont des makers et des spécialistes du sport de niche (S22, S38-S41). Le taker sport perd 1,11 % (S30). Coter autour d'une juste valeur sharp revient à être payé le spread sans parier sur l'issue.

**Différence avec H-001 (en cours).** H-001 est **taker** et jugé sur la CLV. R2 est **maker** et jugé en **markouts contre la clôture sharp**. Il réutilise la même juste valeur (même flux Odds API, même devig power/Shin) : c'est un essai distinct, avec son propre sleeve.

**Expression unique.** Pour chaque match de ligue « niche » (liste fixée ex ante : ligues hors top 5 européen et hors NFL/NBA, de l'univers observé chez les wallets S38-S41) :
- poser un bid et un ask papier à `fair ± max(1 tick, frais taker du marché)` ;
- considérer le fill simulé seulement si le marché **trade à travers** le prix, pas seulement s'il le touche ;
- KPI = markout moyen du fill contre la **cote Pinnacle de clôture** sans marge.

**Données.**
- Polymarket : `wss://ws-subscriptions-clob.polymarket.com` (carnet) et `data-api.polymarket.com/trades` (S38).
- Kalshi : `GET /markets`, `/markets/trades` (S88).
- Odds API : clé existante, 500 req/mois.
- Historique de contrôle : Polymarket-v1 (HF, CC BY-SA, trades 2022-11 → 2026-04-28 avec direction réelle de l'agresseur, S79).

**Puissance.**
- Historique : effet 1,12 % × 0,5 = 0,56 % par $ au règlement, σ ≈ 1. Le seul historique hors période publiée est ≈ 1 mois (Akey s'arrête au 2026-03-29, Polymarket-v1 au 2026-04-28), soit ≈ 1 600 événements sport : t = 0,22, **UNDERPOWERED**.
- Forward en markouts : effet 0,56 pp. σ du markout de clôture par marché ≈ 5 pp (la σ CLV de Buchdahl ≈ 0,10 en ratio de cote, S15, rapportée à p ≈ 0,5). n = (1,96 × 5 / 0,56)² ≈ **306 marchés**. À 200-300 marchés/mois (plafond Odds API), on obtient **t ≈ 1,96 en 1 à 1,5 mois et t ≈ 2,7 en 3 mois**.
- Confirmation P&L obligatoire ensuite, lente : ≈ 120 000 fills pour t = 1,96 au règlement.

**Capacité.** Faible par marché : la profondeur exploitable moyenne est de 14,8 parts dans les anomalies NBA (S81) et kacho a fait 95 830 $ de volume en 4 mois (S59). Soit 10-50 k$ de capital, avec un rendement en dollars modeste.

**Coûts.**
- Frais taker Polymarket sport 0,05 × p(1−p) ; rebate maker 25 % (S17).
- Kalshi : frais makers depuis 2025 (S34).
- Latence : les bots rapides ramassent les cotes périmées (S59, S84).

**Contre-preuve.**
- Le MM maison de Kalshi n'est pas rentable (S53).
- SIG, Jump, DRW et Akuna sont sur le sport (S94).
- Chez kacho, les jambes à « edge ≥ 7 % » ont perdu 3 185 $ à cause de fills adverses (S59).
- La CLV s'est dégradée : 1,9 % contre 4,2 % attendu depuis 2023/24 (S83).
- Il existe un contre-exemple où l'on gagne sans battre la clôture (S63).

**Risque principal.** Le biais des fills papier : un fill simulé « trade-through » surestime la file d'attente et sous-estime la sélection adverse. Parade : ne compter que les fills trade-through, enregistrer le markout à 5 s, 60 s et 300 s, et appliquer un kill-switch si le markout à 60 s est inférieur à 0 avec t < −2.

**France.** Non : Polymarket est bloqué (S71) et Kalshi exclut la France (S72). La collecte de données publiques n'est pas concernée ; à vérifier pour le blocage FAI de polymarket.com.

### R3 — Pricing papier des combos (RFQ Kalshi)

**Mécanisme.** Le retail achète des loteries multi-jambes et perd 19 ¢/$ (S67). Seul un maker sur les treize observés price la corrélation (S66). Les frais makers sur combos ont fait passer la majoration moyenne de 0,64 % à 2,76 % (S68).

**Expression unique.** Pour chaque RFQ combo observé, quote papier = produit des probabilités sharp sans marge de chaque jambe, **sans modèle de corrélation**, × (1 − 2,76 %), la majoration médiane observée par la source S68. KPI = « CLV combo » : écart entre la quote et le produit des probabilités de **clôture** sharp des jambes. Il n'y a pas de paramètre libre.

**Données.** Quoter exige un compte authentifié (S92). L'observation du flux RFQ passe par l'API authentifiée (S66 le surveille) ; **à vérifier** : sans compte (France exclue, S72), la piste est **bloquée** en pratique. Les jambes viennent de l'Odds API et le règlement des jambes de `GET /historical/markets`.

**Puissance.**
- CLV : effet 2,76 % × 0,5 = 1,38 %, σ ≈ 0,10 × √3 jambes ≈ 0,17 → n ≈ **583 combos**, soit moins d'une semaine au volume actuel (combos = 36 % des contrats, S67).
- P&L (σ ≈ 3 par $ à p ≈ 0,1) : n ≈ 181 000 → UNDERPOWERED.

**Capacité.** Grande (record de 68,4 M$ de volume taker combos en un jour, S68), mais c'est une course sous 200 ms (S66).

**Contre-preuve.**
- La concurrence est concentrée : 2 bots répondent à la moitié des RFQ (S66).
- Les frais makers existent (S68).
- Le maker peut refuser de coter les contreparties gagnantes, ce qui marche dans les deux sens (S82).

**Risque principal.** L'accès aux données et la corrélation intra-match (même-match parlays) : la règle « sans corrélation » sera **sélectionnée adversement** précisément sur les combos corrélés. Il faut le mesurer séparément : jambes du même match contre jambes de matchs différents.

**France.** Non.

### R4 — Récompenses de liquidité comme ligne séparée du Book de R2

**Mécanisme.** Les plateformes paient la profondeur à deux faces. Polymarket : score quadratique échantillonné 1×/min, double face obligatoire hors [0,10 ; 0,90] (S16). Kalshi LIP : 1 à 1 000 $/marché/jour, snapshot 1×/s, jusqu'au 2027-01-01 (S35).

**Expression unique.** Pour chaque quote papier de R2, calculer la récompense théorique avec la **formule publiée** (S16, S35) à partir du carnet observé. Elle est enregistrée sur une ligne distincte de P&L, avec les rebates et les markouts. Pas de nouveau paramètre.

**Données.** Configuration des récompenses et carnet (forward).

**Puissance.** Non calculable ex ante : aucune source A ou B sur le rendement net (le post-mortem medium de wanguolin était inaccessible). La mesure est journalière et quasi sans bruit, car la formule est déterministe ; en revanche, le net après markouts hérite de la puissance de R2.

**Contre-preuve.** Un seul fill adverse efface une journée de récompenses (C, S78). Les récompenses sont devenues « a thin bonus », selon des sources C.

**Risque.** Récompenses rognées par des cotes plus serrées, donc plus de sélection adverse. Le LIP est réservé aux résidents US (S35).

**France.** Non.

---

## 4. Liste « ne pas tester » mise à jour (avec preuve)

S'ajoute à la liste existante (§1 du brief), qui reste valable.

| Piste | Preuve du rejet |
|---|---|
| Carry funding/basis crypto comme edge | SR 6,45 → 4,06 (2024) → **négatif en 2025** (S26) ; funding BTC/ETH 11 % → 5 % (S57) |
| Short des déblocages de tokens | Anticipé (−14,7 % dès J−30) ; −4,85 % seulement contre pairs ; puissance ≈ 1,1/an (S75) |
| Juste valeur tirée de books soft (esports, etc.) | Jambes directionnelles à « edge ≥ 7 % » : −3 185 $ (S59) |
| Latence sur les marchés crypto 15 min PM | Frais taker jusqu'à 1,80 % depuis janv. 2026 (S42, S17) |
| « Nothing ever happens » (NO systématique) | Réel −5 % ; backtest positif seulement avec anticipation (S60) |
| Favoris > 90 ¢ Polymarket | +0,83 ¢/$ seulement, absent en sport, signe instable (S32) ; ≈ « bonding » |
| Copy-trading des top wallets PM | Les gagnants sont makers (S22) ; la persistance modeste peut être de la sélection (S22) |
| Wallets « toxiques » Hyperliquid | Horizon 1 s, les auteurs exigent un modèle de latence et de file (S65) |
| Vault HLP comme stratégie | 41 % des profits en < 2 semaines (S44) : non testable, bêta d'événements |
| SPAC trust arb | Spread-to-trust médian ≈ 0-5 %, > 10 % seulement en crise (S50) : plancher |
| Merger arb (petits deals) | t = 1,1 hors échantillon ; 17 ans pour t = 1,96 ; −400 bp de spread depuis 2002 (S49, S70) |
| Mention markets par base rate | Preuve C seulement (S51) ; manipulation par l'orateur (S76) ; t ≈ 0,3 |
| Arbitrage mécanique intra-PM (rééquilibrage, NBA) | 40 M$ déjà extraits (S85) ; 7 anomalies exécutables sur 173 matchs, 14,8 parts (S81) |
| LP passif sur AMM | LVR : « always does worse than rebalancing », hors frais (S64) |
| Day trading / scalping discrétionnaire | 97 % des persistants perdent ; pas d'apprentissage (S55) |

---

## 5. Réponses explicites aux cinq questions (pistes recommandées)

| Question | R1 / R2 (maker) | R3 (combos) | R4 (récompenses) |
|---|---|---|---|
| Qui perd, pourquoi il continue | Takers sport et single-name : préférence pour le YES et l'immédiateté (S87, S22), ils ne mesurent pas leur coût d'exécution | Acheteurs de parlays : préférence loterie (« lottery tickets are what retail is really looking for », S67) | La plateforme, qui achète de la liquidité pour attirer le flux |
| Pourquoi les gros ne l'ont pas mangé | Ils le mangent sur les ligues majeures (S94). Les niches manquent de capacité (14,8 parts, S81) et Citadel, IMC et HRT restent à l'écart (S94) | Deux bots dominent déjà (S66). La corrélation fine reste rare (1 maker sur 13) | Capacité par marché de 1 à 1 000 $/jour, trop petite |
| Survivorship | Shpilberg : 6 mois de pertes avant le MM (S13) ; Kalshi Trading non rentable (S53) ; poly-maker « can lose money » (S01) | n.d. (aucun post-mortem trouvé) | Post-mortem wanguolin inaccessible ; seule la source C S78 subsiste |
| Décroissance | Inversion en 2024 (S30), frais makers en 2025 (S34), kacho 2 506 → 180 $/mois (S59) | Majoration 0,64 % → 2,76 % après les frais du 2026-08-20 (S68) : le coût du maker est répercuté, pas de décroissance démontrée | Non chiffrée |
| Vrai goulot | Fills (file d'attente, trade-through), sélection adverse, latence | Latence < 200 ms et accès au flux authentifié | Sélection adverse |

---

## 6. Auto-audit

**Sources ouvertes : 94 (S01-S94).**

| Famille | Nombre | Commentaire |
|---|---|---|
| 1 Reddit | **0** | **Minimum non atteint : blocage d'environnement documenté.** Aucun contenu Reddit n'a été ouvert : WebFetch refuse reddit.com, old.reddit.com et api.reddit.com ; WebSearch refuse le domaine (erreur 400) ; pullpush a répondu 429 à trois reprises ; arctic-shift 500 ; cinq instances redlib et safereddit échouent (429, 502, 503, anti-bot Anubis) ; web.archive.org est refusé. Aucun contournement par proxy tiers n'a été tenté. Compensation : forums B (SBR, Betfair, HN, Elite Trader) et blogs praticiens. |
| 2 GitHub | 12 | README + issues : poly-maker, hummingbot, freqtrade, BeatTheBookie, sports-betting, KalshiMarketMaker, Polymarket/agents, copy-trade, hyperliquid-data |
| 3 X / blogs praticiens | 12 | X inaccessible (402) ; uniquement des blogs et Substack |
| 4 Académique | 19 | — |
| 5 Données plateformes | 17 | Wallets publics et API (Polymarket, Kalshi, HL) |
| 6 Industrie | 15 | Kaiko (redirection) et Wintermute (page vide) inaccessibles ; podcasts : aucune transcription ouverte |
| 7 Forums | 8 | Minimum juste atteint ; QuantNet 403, Wilmott non ouvert |
| 8 Contre-preuve | 10 | Dont 3 sources juridiques France (S71, S72, S74). Contre-preuves strictes : 7 (S53-S56, S75, S76, S91), plus des contre-preuves classées ailleurs (S26, S59, S60, S63, S83, S94). Chaque piste recommandée a au moins une contre-source cherchée activement. |

**Recherches web distinctes : 60** (hors tentatives d'accès Reddit). Le journal complet (68 entrées : requêtes et ouvertures directes d'API) est dans `SOURCES.md`.

**Affirmations fragiles.**
- Les σ des calculs de puissance de R1 à R3 (45 ¢, 5 pp, 0,17) sont des **hypothèses** issues de la σ CLV de Buchdahl (S15) ou de la géométrie binaire, pas de données mesurées : ce sont les premiers chiffres à calibrer.
- Mastrokostas (« seven figures a month ») et Shpilberg (> 165 k$) sont des témoignages rapportés par la presse (B), non vérifiés sur wallet.
- Les chiffres de Bartlett-O'Hara viennent de résumés (Stanford, InGame) : le PDF SSRN n'a pas été ouvert (403).
- L'éligibilité du flux RFQ Kalshi en lecture sans compte n'est pas établie (S92 ne documente que la création de quote).
- L'accès légal français aux actions US (merger arb, SPAC) est donné « en principe » sans source ouverte.
- La catégorisation Becker (8 catégories) s'applique à Kalshi. Sur Polymarket, la catégorisation d'Akey diffère : ne pas mélanger les deux.

**Contradictions tranchées.**
- *Faut-il battre la clôture pour gagner ?* Oui dans l'ensemble. Buchdahl (≈ 20 000 paris, 3,4 % réel contre 4,0 % attendu, S15) et Pinho (31 247 paris, S83), grade A/B avec données reproductibles, l'emportent sur un contre-exemple unique en tennis (S63). On garde donc la CLV comme statistique d'entrée, avec confirmation P&L.
- *Les pros captent-ils tout ?* La concentration est extrême (S19-S23), mais le MM institutionnel de Kalshi n'est pas rentable (S53) et les gains restent concentrés chez des petits opérateurs spécialisés (S22, S38-S41). La rente est donc réelle mais **conditionnelle à la niche et à l'exécution**, pas automatique.

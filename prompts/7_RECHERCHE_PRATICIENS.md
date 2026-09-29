# Prompt de recherche — Comment les praticiens gagnants y parviennent réellement

> À donner tel quel à un agent de recherche indépendant, qui n'a pas participé aux travaux précédents.
> Ce n'est pas un résumé de blogs : c'est une **enquête de preuve**. Le propriétaire refuse un travail paresseux.

---

## 0. Ta mission

Découvrir **comment les petits opérateurs (1 à 10 personnes, capital de 10 k$ à 5 M$) qui gagnent durablement de l'argent sur les marchés y parviennent vraiment**, en 2024-2026, sur des niches accessibles à un système papier/shadow qui dispose de données publiques gratuites. Tu dois en tirer des **hypothèses testables**, chacune avec son mécanisme économique, ses données et une estimation de puissance statistique.

La question n'est pas « quelles stratégies existent ». La question est : **« qui gagne, contre qui, pourquoi l'argent se transfère, et pourquoi l'edge n'est pas encore mort »**.

## 1. Ce qui est déjà connu (NE PAS refaire, NE PAS reproposer sans fait nouveau)

Déjà testées et rejetées sur nos données :
- fade des nouveaux listings Hyperliquid ;
- écart de funding Hyperliquid contre dYdX ;
- market making ou juste valeur sur la météo Kalshi (le marché bat le NBM, arXiv 2609.23969) ;
- biais favori/outsider sur Kalshi (acheter NO sur les contrats bon marché) ;
- cycle des adjudications du Trésor (puissance insuffisante) ;
- arbitrage negRisk ;
- arbitrage croisé Polymarket–Kalshi ;
- turn-of-month, overnight seul ;
- pumps de listing Upbit ;
- rebond après liquidations ;
- flux des ETF à levier, reconstitution Russell ;
- « bonding » à 95-99 ¢ ;
- rééquilibrage de fin de mois (filtré) ;
- cash-and-carry (c'est un plancher, pas un edge) ;
- Kalshi CPI contre le nowcast de Cleveland.

En cours :
- cotes Pinnacle sans marge contre marchés sport Polymarket/Kalshi, jugées sur la CLV ;
- veille de FOMC en shadow.

Interdit, sans exception :
- wash trading, spoofing, manipulation de marché ou d'oracle ;
- information privilégiée, matchs truqués, courtsiding ;
- sybil ou multi-comptes, contournement géographique ;
- exploit de contrat, MEV nuisible ;
- scraping derrière un login.

## 2. Sources : un minimum obligatoire, par famille

Tu dois consulter **au moins 60 sources distinctes**, dont **au moins 8 dans chaque famille** ci-dessous. Chaque source citée doit avoir été **réellement ouverte** : URL exacte, plus une citation ou un chiffre qui en est extrait. Une source non ouverte ne compte pas.

1. **Reddit** : r/algotrading, r/quant, r/sportsbook, r/sportsbetting, r/Polymarket, r/Kalshi, r/options, r/thetagang, r/CryptoCurrency (fils sur le funding, les airdrops, le MM), r/Daytrading (post-mortems), r/betting.
   Priorité aux fils où quelqu'un montre des **chiffres vérifiables** (relevés, P&L, CLV, nombre de paris) et aux fils de **post-mortem** (« why I stopped », « lost money »).
2. **GitHub** : dépôts de bots réellement utilisés (hummingbot, freqtrade, poly-maker, polymm, bots de funding arb, bots de sports betting, scrapers de cotes). Lis le README **et les issues** : les issues révèlent si ça gagne ou perd, et pourquoi. Regarde les étoiles, la date du dernier commit, les forks actifs.
3. **X / Twitter et blogs de praticiens** : traders Polymarket en tête du classement, market makers crypto, bettors pros (CLV), comptes qui publient leur P&L. Substack, Medium, blogs personnels.
4. **Académique et working papers** (2020-2026) : SSRN, arXiv, NBER, BIS, banques centrales. Priorité aux papiers qui mesurent **qui gagne** (maker/taker, retail/pro, par catégorie) et la **décroissance après publication** (McLean-Pontiff et ses suites).
5. **Données des plateformes** : classements Polymarket, dashboards Dune, statistiques Kalshi, profils de wallets publics (adresses gagnantes, leur fréquence, leur type de marché), rapports de venues (Hyperliquid, dYdX).
6. **Industrie** : rapports Keyrock, Kaiko, Galaxy, Paradigm, Wintermute ; interviews de fondateurs de petits fonds ; podcasts (Flirting with Models, Top Traders Unplugged, Chat With Traders), avec les passages retranscrits.
7. **Forums spécialisés** : Pinnacle Betting Resources, Buchdahl, Joseph Buchdahl, Pinnacle Odds Dropper, Betfair forum, Elite Trader, Wilmott, QuantNet, Hacker News (fils Show HN sur des bots de trading ou de paris).
8. **Contre-preuve** : sources qui disent que l'edge est mort, ou que tel trader a perdu. Chaque piste doit avoir **au moins une contre-source cherchée activement**.

## 3. Standard de preuve (obligatoire pour chaque affirmation chiffrée)

Classe chaque preuve :
- **A** : données vérifiables par un tiers (papier avec données, wallet public, dataset ouvert, relevé audité) ;
- **B** : témoignage chiffré détaillé d'un praticien, avec mécanisme et taille ;
- **C** : témoignage vague, marketing ou capture d'écran de profit.

Les preuves C ne comptent **pas** comme preuve d'edge. Elles peuvent seulement pointer vers une piste.

Pour chaque piste, réponds explicitement :
1. **Qui perd l'argent**, et pourquoi il continue de le perdre (contrainte, préférence, ignorance, mandat, frais).
2. **Pourquoi les gros ne l'ont pas mangé** : capacité, risque juridique, réputation, complexité opérationnelle, frais fixes.
3. **Survivorship** : combien ont essayé et échoué ? Cherche les post-mortems.
4. **Décroissance** : l'edge a-t-il baissé depuis sa médiatisation ? Donne des chiffres par année si possible.
5. **Le vrai goulot** : signal, exécution, fills d'une seule jambe, limites de compte, frais, données fraîches, latence.

## 4. Filtre final : compatibilité avec Quant

Pour chaque piste retenue, fournis :
- **Données** : gratuites et publiques ? Historique disponible (période) ? Forward collectable automatiquement ? Point-in-time possible ?
- **Mécanisme en une phrase.**
- **Expression unique testable** : une seule règle, paramètres fixés par la source et non par optimisation.
- **Puissance** : effet attendu (source citée, réduit de 50 % pour la décroissance), écart-type, nombre d'événements indépendants par an, historique hors période déjà publiée → `expected_t = effet/σ × √n`. Compare au seuil 1,96 pour 1 essai. Si c'est < 1,96, marque la piste **UNDERPOWERED en historique** et dis si elle est jugeable en forward, en combien de temps.
- **Statistique à faible variance** disponible ? CLV, markouts, écart à la juste valeur : ces statistiques rendent un test beaucoup plus puissant que le P&L.
- **Capacité** à 10-100 k$ ; **coûts** : frais, spread, funding, impact.
- **Légalité et CGU.**

## 5. Méthode de travail (anti-paresse)

- Fais **au moins 40 recherches web distinctes** et ouvre les pages. Ne te contente pas des extraits de recherche.
- Pour Reddit et GitHub, lis le contenu : les commentaires, les issues, le README.
- Quand une source cite un chiffre, remonte à la **source primaire**.
- Tiens un **journal de recherche** : requête, puis sources ouvertes, puis ce que tu en as retenu.
- Si deux sources se contredisent, dis-le et tranche avec la meilleure preuve.
- **N'invente rien.** Un chiffre sans URL ouverte n'existe pas. Si tu ne trouves pas, écris « non trouvé ».

## 6. Livrable (en français)

Un fichier Markdown avec :
1. **Synthèse (15 lignes)** : les 3 à 5 schémas récurrents de ceux qui gagnent vraiment.
2. **Tableau des pistes classées** (au moins 10 évaluées, au plus 6 recommandées) : mécanisme | qui perd | preuve (A/B/C, nombre de sources) | décroissance | expected_t historique | faisable en forward (délai) | données | capacité | verdict (TESTER / FORWARD SEULEMENT / REJETER).
3. **Fiche par piste recommandée** : l'expression unique, les données exactes (endpoints), le calcul de puissance détaillé, la contre-preuve, et le risque principal.
4. **Liste « ne pas tester »** mise à jour, avec la preuve de chaque rejet.
5. **Annexe : toutes les sources** (URL, famille, grade A/B/C, une ligne de contenu) et le **journal de recherche**.
6. **Auto-audit** : combien de sources par famille, quelles familles sont sous-représentées, quelles affirmations restent fragiles.

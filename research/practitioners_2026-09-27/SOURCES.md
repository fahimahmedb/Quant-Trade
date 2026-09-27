# Annexe — Sources ouvertes et journal de recherche (2026-09-27)

Familles : 1 Reddit · 2 GitHub · 3 X/blogs praticiens · 4 Académique · 5 Données plateformes · 6 Industrie · 7 Forums · 8 Contre-preuve.
Grades : A = données vérifiables par un tiers ; B = témoignage chiffré détaillé ; C = vague/marketing.
Une source n'est listée ici que si elle a été réellement ouverte (WebFetch ou extraction PDF locale). Les pages inaccessibles sont listées à part.

## Sources ouvertes

| # | URL | Famille | Grade | Extrait / chiffre |
|---|---|---|---|---|
| S01 | https://github.com/warproxxx/poly-maker | 2 | B | README : « Market making on Polymarket is competitive and can lose money. This is a reference implementation and a research harness » ; 1,5 k étoiles, 37 commits |
| S02 | https://github.com/warproxxx/poly-maker/issues?q=is%3Aissue | 2 | B | #23 reconnexion WebSocket échoue silencieusement → le bot cesse de mettre à jour ses prix ; #34 régime TRENDING jamais déclenché (seuils hors plage) ; #24 « not placing orders » |
| S03 | https://github.com/hummingbot/hummingbot/issues?q=is%3Aissue+loss+OR+losing+OR+profit | 2 | B | #8457 ordres acceptés perdus pendant une coupure réseau → position non suivie ; #8462 ordre de clôture Kalshi qui ouvre une position ; #8413 funding HL affiché 1,79e+11 % |
| S04 | https://github.com/hummingbot/hummingbot/issues?q=is%3Aissue+funding+rate+arb | 2 | B | #7295 « Double fill on hyperliquid_perpetual after stopping strategy » ; #7591 PnL net non mis à jour ; #8162 « Funding rate Arb v2 strategy not working » (fermé 2026-08-03) ; #7301 calcul incorrect |
| S05 | https://github.com/freqtrade/freqtrade/issues?q=is%3Aissue+dry-run+live+difference | 2 | B | #12675 comportement incohérent backtest vs dry-run ; #11815 incohérence quand le calcul est long ; #12440 données dry-run ≠ bourse |
| S06 | https://github.com/rodlaf/KalshiMarketMaker | 2 | C | 402 étoiles, 73 forks ; Avellaneda-Stoikov par marché ; aucune revendication de performance |
| S07 | https://github.com/Lisandro79/BeatTheBookie | 2 | B | 658 étoiles ; « We would definitely bet on these games if the bookies did not block our accounts » ; 880 494 matchs 2000-2015 |
| S08 | https://github.com/georgedouzas/sports-betting/issues?q=is%3Aissue | 2 | C | #129 « Does TimeSeriesSplit cover odds-data leakage too? » ; aucune issue sur rentabilité réelle |
| S09 | https://github.com/Polymarket/agents | 2 | C | 3,8 k étoiles, 829 forks, **archivé le 2026-05-11** ; aucun résultat de performance |
| S10 | https://www.botforkalshi.com/blog/open-source-kalshi-bot-ecosystem | 2 | C | Sur 30+ projets, un seul chiffre : « Reported max profit of $1.8k » ; « frameworks… give you plumbing… but not a proven edge » |
| S11 | https://ufoholdings.substack.com/p/kalshis-new-liquidity-incentives | 3 | B | 2025-08-25, auteur ex-trader de Kalshi Trading ; Polymarket ≈ 300 k$/mois d'incitations ; règles : taille, spread serré, présence, deux côtés |
| S12 | https://jdsemrau.substack.com/p/automated-market-making-on-kalshi | 3 | C | 2025-02-19 ; payant, aucun chiffre de P&L visible |
| S13 | https://www.itiger.com/hant/news/2537923561 (reprise MarketWatch 2025-05-22) | 3 | B | Shpilberg : 6 mois de pertes (arbitrage Rotten Tomatoes, météo NYC), puis > 165 k$ en quelques mois en market making Kalshi ; « Jack » (Princeton) ≈ 150 k$ en MM depuis l'élection 2024 |
| S14 | https://www.onchaintimes.com/a-chat-with-domer-the-1-trader-on-polymarket/ | 3 | B | Domer : ≈ 300 M$ de volume, 5 000+ marchés ; « it's all manual. I have a lot of orders on the book, so most of my trades are my orders being matched » ; préfère les marchés nouveaux et peu familiers |
| S15 | https://www.pinnacleoddsdropper.com/blog/closing-line-value--clv-demystified-by-expert-joseph-buchdahl | 7 | B | Buchdahl : ≈ 20 000 paris, profit réel 3,4 % vs espérance 4,0 % ; σ P&L ≈ 1,00 vs σ CLV ≈ 0,1 ; 952 paris +EV, raccourcissement moyen 3,94 %, 65 paris suffisent |
| S16 | https://docs.polymarket.com/programs/liquidity-rewards | 5 | A | Score quadratique S=((v−s)/v)²·b ; carnet échantillonné 1×/min (1 440 échantillons/jour) ; double face obligatoire hors [0,10 ; 0,90] ; paiement min 1 $ |
| S17 | https://docs.polymarket.com/polymarket-learn/trading/fees | 5 | A | fee = C × rate × p(1−p) ; crypto 0,07, sports/éco/culture/météo 0,05, finance/politique/mentions/tech 0,04, géopolitique 0 ; rebates makers 20-25 % |
| S18 | https://news.ycombinator.com/item?id=48221877 | 7 | C | Fil HN sur Akey et al. : « polymarket transferred wealth from the impatient… to… patient market makers » ; un praticien affirme des écarts de 3-8 % entre venues (non vérifié) |
| S19 | https://www.coindesk.com/markets/2026/04/29/a-tiny-group-is-winning-on-polymarket-as-under-1-of-wallets-take-half-the-profits | 6 | B | Solidus Labs, politique déc. 2025-fév. 2026 : 0,55 % des wallets makers gagnants = 50 % des gains ; 0,26 % des takers gagnants ≈ même part ; ≈ 16 M$ de profits ; ≈ 15 % du volume avec motifs de wash |
| S20 | https://www.financemagnates.com/fintech/100000-polymarket-wallets-lost-at-least-1000-bloomberg-analysis-shows/ | 6 | B | Bloomberg, wallets actifs depuis 2025 : > 100 000 ont perdu ≥ 1 000 $, ≈ 50 000 ont gagné ≥ 1 000 $ ; ≈ 70 % d'adresses en perte |
| S21 | https://cepr.org/publications/dp21615 | 4 | A | Akey-Grégoire-Harvie-Martineau : 588 M de trades (67 Md$) ; top 1 % des gagnants = 76,5 % des profits ; gagnants = makers en ordres limites ; persistance mensuelle modeste |
| S22 | https://www.carf.e.u-tokyo.ac.jp/wp/wp-content/uploads/2026/06/260714_polymarket.pdf (texte extrait localement) | 4 | A | Top 0,1 % : 47,3 % du volume en maker vs 17,1 % pour les 95 % du bas ; +1 σ de part maker → +9,0 pp de proba d'être gagnant ; 42/100 top wallets concentrés, 81 % de leurs gains en sport ; ratio médian utilisateur −1,03 ; calibration moins bonne en Tech/Culture/Météo |
| S23 | https://gigazine.net/gsc_news/en/20260525-polymarket-win-or-lose/ | 6 | B | Reprise d'Akey : 2 469 589 utilisateurs, 764 988 gagnants (≈ 30 %), 1 200 personnes (0,05 %) = plus de la moitié des profits |
| S24 | https://arxiv.org/html/2604.24366v1 | 4 | A | Carnet Polymarket fév.-avr. 2026 : spread coté médian ≈ 400 bp à mi-prix, 1 300-1 800 bp sous 0,10 ; direction inférée juste 59 % du temps seulement ; wash médian 0,97 % |
| S25 | https://wp.lancs.ac.uk/fofi2024/files/2024/04/FoFI-2024-146-Leander-Gayda.pdf (texte extrait) | 4 | A | Beckmeyer-Branger-Gayda : retail 0DTE perd 241 k$/jour (fév. 2021-sept. 2023), 350 k$/jour après mai 2022 ; > 90 M$ des 125 M$ de pertes = coûts de transaction |
| S26 | https://arxiv.org/pdf/2510.14435 (texte extrait) | 4 | A | Borri-Liu-Tsyvinski-Wu : carry crypto SR 6,45 (2020-2025), **4,06 depuis 2024, négatif en 2025** ; profit surtout dû au funding |
| S27 | https://www.bis.org/publ/work1087.pdf | 4 | A | Schmeling-Schrimpf-Todorov (BIS WP 1087) : carry > 10 %/an en moyenne, jusqu'à 60 % ; causé par la demande de levier des petits investisseurs et la rareté du capital d'arbitrage ; carry élevé prédit les krachs |
| S28 | https://arxiv.org/abs/1710.02824 | 4 | A | Kaunitz-Zhong-Kreiner : stratégie rentable sur 10 ans de cotes de clôture et 5 mois d'argent réel ; « discriminatory practices against successful clients » |
| S29 | https://arxiv.org/pdf/2209.13623 (texte extrait) | 4 | A | Chen-Zimmermann : hors échantillon 74 % des rendements subsistent ; loin de l'échantillon, décroissance ≈ 50 % (McLean-Pontiff) ; correction de biais de publication 10-15 % |
| S30 | https://www.jbecker.dev/research/prediction-market-microstructure | 4 | A | Kalshi, 72 M trades : maker-taker Sports 2,23 pp (43,6 M trades), Finance 0,17 pp, Entertainment 4,79 pp, Media 7,28 pp, World Events 7,32 pp ; **avant fin 2024 les takers gagnaient (+2,0 %)** ; bascule de 5,3 pp après l'élection |
| S31 | https://arxiv.org/abs/2608.04373 | 4 | A | Identité publique des traders (DEX) : rang des wallets par impact de leurs ordres agressifs, corrélation 0,52 d'une fenêtre de 10 jours à l'autre ; +13,2 % de R² (t = 9,2) ; 147 113 wallets |
| S32 | https://arxiv.org/abs/2609.12878 | 4 | A | FLB Polymarket : < 10 ¢ perdent 19,3 ¢/$ ; > 90 ¢ gagnent 0,83 ¢ ; **biais absent en Sport** ; le signe s'inverse si on regroupe par événement |
| S33 | https://arxiv.org/abs/2608.00666 | 4 | A | Arbitrage negRisk exécutable : ≈ 1,12 M$ au total sur l'historique étudié |
| S34 | https://www.karlwhelan.com/Papers/Kalshi.pdf (texte extrait) | 4 | A | Bürgi-Deng-Whelan : 300 k contrats ; rendement moyen makers −9,64 %, takers −31,46 % ; makers achetant ≥ 50 ¢ : +2,6 % ; frais makers depuis avril 2025 |
| S35 | https://help.kalshi.com/en/articles/13823851-liquidity-incentive-program | 5 | A | 1 à 1 000 $/marché/jour ; snapshot 1×/s ; taille cible 100-20 000 contrats ; fin 2027-01-01 ; non-US exclus |
| S36 | https://polymarket.com/leaderboard | 5 | A | Mensuel : Papeasy +5,09 M$, e46m3 +3,91 M$ (volume 2,59 M$), 00gringo00 +3,65 M$ (volume 28,2 M$) |
| S37 | https://lb-api.polymarket.com/profit?window=all&limit=20 | 5 | A | Top historique : Theo4 22,05 M$, swisstony 18,42 M$, Fredi9999 16,62 M$, RN1 12,67 M$, kch123 11,35 M$ |
| S38 | https://data-api.polymarket.com/trades?user=0x204f72f35326db932158cba6adff0b9a1da95e14&limit=50&takerOnly=false | 5 | A | swisstony (n°2 historique) : 50 derniers trades = 28 marchés sport de niche (K-League, ATP, ITF féminin, exact scores) |
| S39 | https://data-api.polymarket.com/trades?user=0x2005d16a84ceefa912d4e380cd32e7ff827875ea&limit=50&takerOnly=false | 5 | A | RN1 (n°4) : football universitaire US, Liga MX, totaux |
| S40 | https://data-api.polymarket.com/trades?user=0x6a72f61820b26b1fe4d956e17b6dc2a1ea3033ee&limit=50&takerOnly=false | 5 | A | kch123 (n°5) : Coupe du monde 2026, 37 trades sur un seul O/U |
| S41 | https://data-api.polymarket.com/trades?user=0xed64a7bf029040aa331abc87902434d815ef217d&limit=50&takerOnly=false | 5 | A | fishalive : 40 trades en 93 s sur un seul spread de Coupe du monde, jusqu'à 100 000 parts |
| S42 | https://pineanalytics.substack.com/p/polymarket-fee-rollout | 6 | B | Frais taker Polymarket : crypto 2026-01-05, sport 2026-02-18, reste 2026-03-30 ; volume sport passé de 100-150 M$/j à 150-250 M$/j après les frais |
| S43 | https://www.pewresearch.org/short-reads/2026/09/23/prediction-markets-trading-volume-doubled-between-may-and-july-largely-driven-by-sports/ | 6 | A | Juillet 2026 : Kalshi sport 31,4 Md$, politique 169 M$ ; Polymarket sport 10,6 Md$ (données The Block) |
| S44 | https://www.coingecko.com/learn/hyperliquid-hlp-vault-analysis | 5 | A | HLP : 136,9 M$ de profit cumulé depuis mai 2023 (API vaultDetails) ; 41 % des profits en < 2 semaines (10 oct. 2025 +41,5 M$ ; 31 janv. 2026 +15 M$) ; POPCAT 4,9 M$ de créance douteuse |
| S45 | https://keyrock.com/from-locked-to-liquidity-what-16000-token-unlocks-teach-us/ | 6 | B | 16 000+ déblocages sur 40 tokens ; 90 % négatifs ; équipe −25 % ; baisse dès J−30 ; déc. 2024 |
| S46 | https://www.financemagnates.com/trending/only-500k-traders-make-money-on-prediction-markets-report-finds/ | 6 | B | Citizens JMP (juil. 2025-mars 2026) : rendement médian −8 % sur les marchés de prédiction vs −5 % en sportsbook ; seuls les traders à 500 k$+ d'activité ont un rendement médian positif (+2,6 %) |
| S47 | https://forum.betangel.com/viewtopic.php?t=21403 | 7 | B | Premium Charge Betfair : taux élevé 40-60 % au-delà de 250 k£ de profit à vie ; touche « less than 0.1% » des clients |
| S48 | https://forum.betangel.com/viewtopic.php?t=17907 | 7 | B | Northbound : bot pré-off chevaux 20-60 £/mois à 100 £ de mise ; « 9 out of 10 strategy ideas fail » ; tester 500+ marchés avant de juger |
| S49 | https://www.returnstacked.com/academic-review/the-shrinking-merger-arbitrage-spread-reasons-and-implications/ | 4 | A | Jetley-Ji (FAJ 2010), 2 182 deals 1990-2007 : spread d'arbitrage contracté de > 400 bp depuis 2002 ; spread médian J1 1,91 % (2002-07) ; rendement mensuel médian des fonds merger arb 0,96 % (1990-95) → 0,51 % (2002-07) |
| S50 | https://www.aqr.com/-/media/AQR/Documents/Insights/White-Papers/Are-SPACs-Still-Alive.pdf (texte extrait) | 6 | B | AQR oct. 2024 : spread-to-trust médian > 10 % annualisé seulement au pic de crise 2008 ; redemption médiane > 90 % en 2022 ; liquidation 36 % au T1 2024 ; stratégie = prime de liquidité, pas un signal |
| S51 | https://eventwaves.substack.com/p/a-business-proposition | 3 | C | Praticien des mention markets (Matt Lamers) : « I have a bad habit of burning edges » ; aucune donnée de P&L |
| S52 | https://github.com/jhcdx9999/polymarket-copy-trade/issues | 2 | C | Bot de copy-trading : 1 seule issue (README), aucune preuve de rentabilité |
| S53 | https://cdcgaming.com/brief/kalshi-co-founder-says-in-house-trading-arm-not-profitable/ | 8 | B | 2025-12-01 : Kalshi Trading (MM maison) « not profitable », ≈ 310 M$ de sport en novembre |
| S54 | https://www.ingame.com/kalshi-in-house-trading-arm-not-profitable/ | 8 | B | Kalshi Trading < 6 % du volume maker sport en novembre 2025, non rentable |
| S55 | https://www.tradicted.com/research/chagu-day-2020/ | 8 | A | Chague-De-Losso-Giovannetti : 19 646 day traders ; 97 % des 1 551 qui ont persisté > 300 jours ont perdu net de frais ; meilleur : 310 $/jour avec σ 2 560 $ ; pas d'apprentissage |
| S56 | https://smartbettingclub.com/blog/gambling-commission-restrictions-data/ | 8 | A | UKGC 2024 : 4,31 % des comptes restreints ; 46,78 % des restreints sont en profit vs 25,42 % de tous les comptes ; > 50 % des limités à < 9 % de la mise normale |
| S57 | https://coinmetrics.substack.com/p/state-of-the-network-issue-335 | 6 | A | Coin Metrics 2025-10-28 : funding BTC/ETH ≈ 11 % annualisé en 2024 vs ≈ 5 % en 2025 ; USDe > 10,5 Md$ |
| S58 | https://news.ycombinator.com/item?id=48461522 | 7 | B | Fil HN « I ran an arbitrage bot on Polymarket » ; l'auteur reconnaît un bug d'inversion d'équipes (« matching the implied probs… without matching the teams first ») |
| S59 | https://kacho.io/polymarket-arbitrage-real-numbers | 3 | B (wallet public) | 2026-01-06 → 04-28, esports PM vs books (Spinbetter, GGBet), seuil ≥ 7 % : 3 858 paris, 95 830 $ de volume, net +4 973 $ ; arbs +8 293 $, jambes directionnelles −3 185 $ (« every one of those legs went on at a ≥7% edge… Mine lost ») ; mensuel 1 898 → 2 506 → 390 → 180 $ ; « more competition… and fees got introduced, so the edge got thinner » |
| S60 | https://news.ycombinator.com/item?id=47753472 | 7 | C | Bot « Nothing Ever Happens » (acheter NO hors sport) : 73 % des marchés PM résolvent NO, mais essai réel 100 $ → −5 $ sur un mois ; backtest 100 % APR seulement « by knowing when things are going to resolve » (biais d'anticipation) |
| S61 | https://www.sportsbookreview.com/forum/handicapper-think-tank/1726344-crushing-the-no-vig-closing-line-but-still-losing-badly/page2 | 7 | B | Fullkelly : 108-142 sur 250 paris tout en battant la clôture sans marge ~80 % du temps ; réponse : probabilité 5-7 % (variance), convergence vers l'équilibre ensuite |
| S62 | https://www.elitetrader.com/et/threads/trading-with-futures-prop-firms-2025.382648/ | 7 | C | Fil prop firms 2025 : aucun chiffre de taux de réussite ni de rentabilité ; anecdotes de retraits |

## Pages inaccessibles (ne comptent pas)

| URL | Motif | Remplaçant |
|---|---|---|
| old.reddit.com, www.reddit.com, api.reddit.com (recherches r/sportsbook, r/algotrading) | « unable to fetch » | miroirs essayés ci-dessous |
| WebSearch `allowed_domains: reddit.com` | erreur 400 « not accessible to our user agent » | — |
| api.pullpush.io (recherche Reddit) | 429 | à réessayer |
| arctic-shift.photon-reddit.com | 500 | — |
| safereddit.com | page anti-bot Anubis | — |
| redlib.catsarch.com / l.opnxng.com / rl.bloat.cat | 429 / 503 / 502 | — |
| web.archive.org | « unable to fetch » | — |
| papers.ssrn.com (Akey, Beckmeyer) | 403 | CEPR + PDF CARF ; PDF Lancaster |
| finance.yahoo.com/news/kalshi-co-founder-says-house-174507266.html | 404 | extrait du moteur : Lopes Lara, Kalshi Trading « not profitable », < 6 % du volume maker sport en novembre (à confirmer via cdcgaming/ingame) |
| sbcamericas.com (UKGC) | 403 | smartbettingclub (S56) |
| bitcoinworld.co.in (BitMEX funding) | 404 | Coin Metrics (S57), Borri et al. (S26) |
| redlib.nadeko.net / red.artemislena.eu / redlib.privacyredirect.com, pullpush (2e essai) | 502 / Anubis / 403 / 429 | — |
| quantnet.com/threads/individual-retail-quant.59345 | 403 | — |
| sportsbookreview.com « Is CLV a Farce? » | redirection vers l'index | S61 |
| medium.com/@wanguolin (post-mortem récompenses PM) | 403 ; scribe.rip 404 ; freedium DNS | — |
| bitmex.com/blog/harvest-funding-payments-on-hyperliquid | 404 | — |
| cybernews.com (bots IA perdants), cnbc.com 2026-08-01 | 403 | — |
| x.com/navnoorquant | 402 | — |
| cepr.org/voxeu crypto carry | 403 | BIS PDF |
| research.kaiko.com | redirection vers app | — |
| wintermute.com rapport OTC 2025 | page de navigation seulement | — |
| dune.com/sealaunch/polymarket-volume-per-category | graphiques en échec | — |
| app.hyperliquid.xyz/vaults/… | rendu JS, vide | CoinGecko (API vaultDetails) |
| polymarketanalytics.com/traders | 429 | lb-api + data-api |

## Journal de recherche (requête → sources ouvertes → retenu)

1. « reddit r/algotrading funding rate arbitrage results profit 2025 » → aucun fil Reddit renvoyé ; substack Tsybko listé.
2. « reddit sportsbook closing line value tracked bets… » → sportbotai (résume un fil r/sportsbook de 1 388 paris, non vérifiable) ; aucun fil Reddit ouvert.
3. « reddit r/Polymarket how I made money market making rewards » → yahoo/coin360 (70 % d'adresses perdantes).
4. « reddit r/Kalshi market maker bot profit losses » → itiger/MarketWatch (S13), ufoholdings (S11), jdsemrau (S12).
5. Accès Reddit direct : voir « pages inaccessibles ».
6. « Kalshi co-founder in-house trading arm not profitable » → extrait : Kalshi Trading « not profitable », 310 M$ sport en un mois, < 6 % du volume maker.
7. « Polymarket top traders analysis wallets profit concentration » → S19, S20.
8. « "Who Wins and Who Loses in Prediction Markets" Akey » → S21, S22, S23, S18.
9. « arXiv Polymarket market makers profit adverse selection » → S24 (et pistes arXiv 2605.11640, 2606.05882, 2609.20017).
10. « Beckmeyer Branger Gayda 0DTE » → S25.
11. « Schmeling Schrimpf Todorov Crypto carry » → S27, S26.
12. « Kaunitz Beating the bookies » → S28, S07.
13. « Chen Zimmermann post-publication decay » → S29.
14. « Domer Polymarket interview » → S14.
15. « Buchdahl CLV predicts profit » → S15.
16. « Polymarket liquidity rewards earnings » → S16 (medium inaccessible).
17. « Hyperliquid funding arbitrage personal results » → bitmex 404 ; guides marketing non retenus.
18. « github kalshi market making bot » → S06, S10.
19. « github sports betting value bet bot pinnacle » → S07, S08.
20. GitHub direct → S01-S05, S09.
21. « Hacker News Show HN bot prediction market » → cybernews/cnbc 403 ; S18.
22. « elitetrader small prop trader profitable 2025 » → fils listés (à ouvrir).
23. « Betfair community forum trading still profitable 2025 » → S47, S48.
24. Becker / arXiv (identité publique, FLB PM, negRisk) → S30-S33.
25. « Kalshi liquidity incentive program rules » → S35 ; X inaccessible.
26. Whelan PDF → S34.
27. Polymarket leaderboard + API publiques → S36-S41 ; S17.
28. « Dune dashboard Polymarket volume by category » → S42 (Dune en échec).
29. « Hyperliquid HLP vault returns 2025 » → S44.
30. « Kalshi volume by category 2026 » → S43.
31. « Keyrock token unlocks report » → S45.
32. « Kaiko research funding rates basis 2025 2026 » → Kaiko inaccessible.
33. « Galaxy Research prediction markets report » → S46.
34. « Wintermute report retail flows OTC 2025 » → page sans contenu.
35. « merger arbitrage returns decline paper » → S49.
36. « SPAC arbitrage returns 2025 » → S50.
37. « Kalshi mention markets traders strategy » → S51 (aucun P&L trouvé).
38. « copy trading Polymarket top wallets results » → S52 ; blog polyloly (+46,7 % sur 334 positions, non ouvert, C).
39. Kalshi Trading non rentable → S53, S54.
40. « Chague day trading for a living » → S55.
41. « sportsbooks limit winning bettors UKGC » → S56.
42. « funding rate arbitrage dead 2025 Ethena » → S57.
43. « Show HN sports betting arbitrage bot » → S58, S59, S60.
44. « sportsbookreview think tank closing line value » → S61 (« CLV farce » inaccessible).
45. « quantnet OR wilmott retail quant » → QuantNet 403 ; S62 (Elite Trader).

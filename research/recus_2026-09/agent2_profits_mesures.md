# AGENT 2 — PROFITS MESURÉS (reçus 2024-2026)

Mission : recenser les études 2024-2026 ayant MESURÉ des profits réellement encaissés (registres on-chain, historiques de plateforme, versements publiés), pas des backtests. Recherche externe seulement. REAL_CAPITAL_AUTHORIZED = FALSE.

Convention : « mesuré » = profit reconstruit à partir de transactions exécutées ou de versements publiés par la plateforme ; « simulé » = opportunité calculée sans preuve d'exécution. Chaque chiffre est cité avec sa source ; une source non ouverte est marquée « non consulté ».

Rédigé le 2026-09-29. Branche `claude/gallant-cerf-e0rpao`. Fichier d'état : `agent2_etat.md`.

---

## Classement (par intérêt pour Quant)

| Rang | ID | Titre | Verdict |
|---|---|---|---|
| 1 | R2 | Kalshi : les makers perdent moins, et gagnent (un peu) au-dessus de 50 ¢ | vérifié |
| 2 | R1 | Polymarket : arbitrage intra-marché réalisé ($39,6 M brut / $0,29 M strict) | vérifié, contesté |
| 3 | R4 | Metaculus : prix payés aux bots de prévision ($30 k → $50 k / saison) | vérifié |
| 4 | R3 | Betfair Exchange : makers +0,6 % / takers -2,5 % après commission | vérifié |
| 5 | R5 | Numerai : versements mensuels réels, dispersion non publiée | probable |
| 6 | R6 | Arbitrage Polymarket ↔ Kalshi : écarts persistants, profit réalisé jamais mesuré | négatif structuré |
| 7 | R7 | LP Uniswap : pertes collectives mesurées ; l'argent va aux arbitrageurs rapides | négatif mesuré |

---

## R1 | Polymarket — arbitrage intra-marché réalisé (somme des prix ≠ 1 et paniers NegRisk)

- **Type** : arbitrage.
- **Mécanisme (qui paie, pourquoi il ne peut pas arrêter)** : les preneurs achètent YES et NO (ou les branches d'un marché multi-issues) à des prix dont la somme s'écarte de 1 $ ; l'arbitragiste achète le panier complet sous 1 $ ou le vend au-dessus et encaisse à la résolution (ou avant via l'adaptateur NegRisk). Les payeurs sont les preneurs pressés ou mal informés ; l'écart réapparaît tant que le carnet est fragmenté par issue.
- **REÇU** :
  - Saguillo, Ghafouri, Kiffer, Suarez-Tangil, *Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets*, AFT 2025 — https://arxiv.org/abs/2508.03474 (version HTML https://arxiv.org/html/2508.03474 ; LIPIcs https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.AFT.2025.27). Données : événements on-chain Polygon `OrderFilled`, `PositionSplit`, `PositionsMerge`, ~86 M d'ordres, 17 218 conditions (8 659 marchés simples, 1 578 multi-conditions) ; VWAP par bloc, fenêtres de 950 blocs, seuil 0,05 $/dollar. Tableau de synthèse des profits par type (section résultats).
  - Contre-preuve : Gebele, Mutzel, Matthes (TU Munich), *Executable Arbitrage and Market Efficiency in Prediction Markets*, 1 août 2026 — https://arxiv.org/html/2608.00666v1. Données : 53 000 trades FPMM, CLOB jusqu'au 31 déc. 2025 (32 702 événements), carnet niveau 2 du 14 avril au 19 mai 2026.
- **Période mesurée** : 1 avril 2024 → 1 avril 2025 (Saguillo) ; jusqu'à mai 2026 (Gebele).
- **Profit réalisé** :
  - Saguillo : total **39,59 M$** = ~10,6 M$ condition simple (achat sous 1 $ : 5,9 M$ ; vente au-dessus : 4,7 M$) + ~28,6 M$ rééquilibrage NegRisk (YES 11,1 M$, NO 17,3 M$, ventes 0,6 M$) + 95 k$–600 k$ combinatoire inter-marchés (5 paires dépendantes sur 13). Médiane de profit ~0,60 $ par dollar engagé sur les conditions simples.
  - Gebele : sur la **même fenêtre**, avec un lien strict entre trades et mécanisme d'extraction, **291 424 $** seulement ; sur toute la période, ~1,12 M$ (1,086 M$ via conversion NegRisk, 32 k$ via paniers complets réglés). Les auteurs attribuent l'écart à la méthode (VWAP par bloc et omission des branches improbables chez Saguillo), pas au marché.
- **Concentré sur quelques acteurs ?** Oui. Saguillo : top 10 comptes = 8,4 M$ (21 %), premier compte 2,01 M$ sur 4 049 transactions, « comportement de bot ». Gebele : **top 10 adresses = 75 %** des gains liés au convertisseur ; un cluster anormal de 381 748 $ en 7 minutes exclu comme transferts potentiellement coordonnés.
- **Frais 2026 inclus ?** Saguillo : non, Polymarket ne facturait aucun frais par trade sur la période. Gebele : hypothèses de frais taker « conservatrices ». Grille de frais 2026 non re-vérifiée ici.
- **Dépend de la vitesse ?** Partiellement. Non atomique (une jambe peut échouer). Saguillo : seulement 1 à 2 % des opportunités estimées sur conditions simples ont été exploitées, ce qui suggère de la marge hors course à la latence ; mais les gros acteurs sont des bots.
- **Capital minimum** : faible (paniers de quelques dizaines de dollars), mais le capital est immobilisé jusqu'à résolution ou conversion.
- **Risque extrême caché** : résolution ambiguë (UMA), jambe non exécutée, marché multi-issues dont une branche est illiquide, gel/geoblocage du compte.
- **Venues et accès** : Polymarket. US : interdit aux résidents ; UE : accessible sauf blocages nationaux ; France : accès bloqué (ANJ, fin 2024, non re-vérifié dans cette mission) ; inconnu pour la version régulée US annoncée.
- **Vérification 1 jour sur données publiques** : oui. Les événements CTF/NegRisk sont on-chain (Polygon) et l'API CLOB est publique ; recompter les paniers YES+NO < 1 $ sur une semaine est faisable.
- **Plafond estimé à petite taille** : l'estimation stricte (0,29 M$/an pour tout le marché, 75 % chez 10 adresses) laisse **< 500 €/mois** à un acteur non-bot ; l'estimation large de Saguillo laisse davantage mais n'est pas un profit encaissable garanti (VWAP, omissions).
- **Confiance** : vérifié (deux études primaires ouvertes, chiffres lus dans le texte). Le montant encaissable réel est **contesté d'un facteur 100** entre les deux.

---

## R2 | Kalshi — les makers perdent moins que les takers et gagnent au-dessus de 50 ¢

- **Type** : maker.
- **Mécanisme** : les takers acceptent des offres avec des croyances plus extrêmes et paient les frais ; ils surpayent surtout les contrats bon marché (biais favori-outsider). Le maker encaisse l'écart. Les takers ne peuvent pas « arrêter » : le biais est comportemental et se reproduit chaque année du panel.
- **REÇU** : Bürgi, Deng, Whelan, *Makers and Takers: The Economics of the Kalshi Prediction Market*, GWU CER WP 2026-001 (janv. 2026) — https://www2.gwu.edu/~forcpgm/2026-001.pdf ; CEPR DP 20631 https://cepr.org/publications/dp20631 ; SSRN 5502658 (non consulté, 403) ; résumé VoxEU https://cepr.org/voxeu/columns/economics-kalshi-prediction-market. Données : transactions sur **46 282 contrats YES**, > 300 000 prix (relevés jusqu'à 10 jours avant clôture), tous résolus. Figure 5 (rendements par tranche de prix), **Figure 6** (takers vs makers), Tables 4-9 (régressions).
- **Période mesurée** : 2021 → avril 2025.
- **Profit réalisé** : rendement moyen après frais taker : **makers -9,64 %, takers -31,46 %** (Figure 6, différence significative). Makers sur contrats ≥ 50 ¢ : **+2,6 %** en moyenne, statistiquement positif au-dessus de 70 ¢. Contrats ≤ 10 ¢ : pertes > 60 % (takers), négatives aussi pour les makers 5 jours sur 6. Rendement moyen pré-frais par contrat -20 % (asymétrie cheap/expensive).
  - Réplication indépendante : dépôt https://github.com/Vladosyna/kalshi-makers-takers-persistence — marge maker ≥ 50 ¢ répliquée à **+2,09 %** ; extension mai 2025 → juin 2026 : marge maker ≥ 50 ¢ **+2,40 % brut** après l'introduction des frais maker ; DiD série -0,0016 (0,0064) sur 98 séries traitées ; 41 % du changement de pente est un effet de composition (sports).
- **Concentré sur quelques acteurs ?** Non mesuré au niveau des comptes (données de trades, pas de wallets). Inconnu.
- **Frais 2026 inclus ?** Frais taker oui (0,07·P·(1-P), ≈ 1,77 % à 50 ¢ pour 100 contrats). **Frais maker introduits après avril 2025 : non inclus** dans le papier ; la réplication donne +2,40 % *brut* après cette date.
- **Dépend de la vitesse ?** Modérément : le maker doit annuler ses ordres quand l'information change ; pas de course en microsecondes.
- **Capital minimum** : quelques centaines de dollars ; rotation limitée par la durée des marchés (mode 24 h).
- **Risque extrême caché** : sélection adverse sur nouvelles (annulations trop lentes) ; écart-type élevé ; changement de grille de frais ; la marge de 2,6 % est brute de frais maker.
- **Venues et accès** : Kalshi. **US uniquement** (CFTC). UE / France : non accessible. Inconnu pour d'éventuels accords internationaux.
- **Vérification 1 jour** : partielle. L'API publique Kalshi donne les trades et les prix ; distinguer maker/taker demande la reconstruction faite par le papier (le dépôt de réplication fournit le code).
- **Plafond estimé à petite taille** : à 10 k$ tournés 2 fois par mois à +2,4 % brut : ~500 $/mois avant frais maker et pertes de sélection ; **0 € depuis la France**.
- **Confiance** : vérifié (PDF primaire ouvert, chiffres lus ; réplication indépendante). Ne contredit pas nos rejets « favoris > 90 ¢ » et « NO systématique » côté taker : les takers ne sont positifs qu'au-dessus de 70 ¢ et faiblement.

---

## R3 | Betfair Exchange — makers +0,6 % / takers -2,5 % après commission

- **Type** : maker.
- **Mécanisme** : même logique que R2 sur une bourse de paris : ceux qui postent les cotes gagnent la sur-ronde (back ~101 %, lay ~99 %), ceux qui acceptent la paient. Les takers pressés en jeu (in-play) et sur les outsiders paient le plus.
- **REÇU** : Whelan, *Agreeing to Disagree: The Economics of Betting Exchanges*, sept. 2025 — MPRA 126351 https://mpra.ub.uni-muenchen.de/126351/1/MPRA_paper_126351.pdf ; CEPR DP 20633 https://cepr.org/publications/dp20633 (non consulté) ; UCD WP 2025/22 (403). Données : > 200 000 matchs de football 2022-2024, carnet complet à 1 seconde + tous les trades appariés (fournies gratuitement par Betfair à l'auteur). Section 7.1, Figures 14-15 (pré-match), Figure 18 (in-play).
- **Période mesurée** : 2022-2024.
- **Profit réalisé** : match odds pré-coup d'envoi, 152 102 matchs, 902 568 paris : **takers -2,5 %, makers +0,6 %** (t = 11,8) après commission de 2 % ; rendement maker non significativement différent de zéro. Total goals, 2 088 032 paris : **takers -2,2 %, makers +2,0 %**. In-play à 105 min : pertes des takers sur le dernier décile ~70 %, makers sur outsiders presque aussi mauvais ; petits profits significatifs pour les takers sur gros favoris en 2e mi-temps.
- **Concentré sur quelques acteurs ?** Non mesuré (pas d'identifiant de compte). Inconnu.
- **Frais 2026 inclus ?** Commission 2 % incluse (taux « typique » ; barème de base Betfair 5 % avec remises). Non ajusté aux barèmes 2026.
- **Dépend de la vitesse ?** Pré-match : peu. In-play : oui (flux vidéo en retard, courtside).
- **Capital minimum** : faible, mais l'auteur note un **écart-type de 198 %** sur le +0,6 % ; Kelly ≈ 0,5 % de la fortune par pari.
- **Risque extrême caché** : ruine par variance, plafonnement/fermeture de compte par l'exchange, commission majorée « Premium Charge » pour les gagnants réguliers.
- **Venues et accès** : Betfair Exchange (UK/IE et pays autorisés). **France : non disponible** (pas de bourse de paris agréée ANJ). US : non.
- **Vérification 1 jour** : non. Données propriétaires ; Betfair Historical Data est payant et sans étiquette maker/taker.
- **Plafond estimé à petite taille** : +0,6 % à +2 % par pari avec σ ≈ 200 % → espérance mensuelle de quelques dizaines d'euros pour un capital de 5 k€ sous Kelly, avant Premium Charge. **Quasi nul.**
- **Confiance** : vérifié (PDF primaire lu). Le reçu prouve surtout que le take est mort et que le make est proche de zéro.

---

## R4 | Metaculus — prix réels payés aux bots de prévision

- **Type** : paiement de la prédiction.
- **Mécanisme** : Metaculus (financé par des subventions) paie des prix en dollars pour mesurer la qualité des prévisions IA ; les sponsors (Anthropic, Google, OpenAI, AskNews) fournissent des crédits LLM gratuits. Le payeur peut arrêter à tout moment : c'est un budget de recherche, pas une contrepartie de marché.
- **REÇU** :
  - Q1 2025 : https://www.metaculus.com/notebooks/37692/winners-of-the-q1-2025-ai-forecasting-benchmark-tournament/ — 1er manticAI 7 685,18 $, 2e acm_bot 5 498,51 $, 3e GreeneiBot2 4 065,10 $, 7 autres bots 12 752 $ (10 bots payés, ≈ 30 000 $).
  - Q2 2025 : https://www.metaculus.com/notebooks/39140/winners-of-q2-2025-ai-benchmark-tournament/ — 1er Panshul42 7 550 $, 2e pgodzinai 4 563 $, 3e CumulativeBot 3 270 $, 16 autres bots 14 617 $ (19 bots payés, 30 000 $). Analyse indépendante : https://www.lesswrong.com/posts/Surnjh8A4WjgtQTkZ/q2-ai-benchmark-results-pros-maintain-clear-lead — 54 bot-makers + 42 bots internes Metaculus, 348 questions ; les pros humains battent chaque bot individuellement (score bots vs pros -20,03 [-28,63 ; -11,41], p = 0,00001).
  - Saisons suivantes : Fall 2025 50 000 $ (page https://www.metaculus.com/tournament/fall-aib-2025/ : 403, gagnants **non consultés**) ; Summer 2026 FutureEval 50 000 $, 300-500 questions, MiniBench bi-hebdomadaire 1 000 $ (~60 questions) — https://forum.effectivealtruism.org/posts/ZfLAN557rGWACKtmc/announcing-metaculus-summer-2026-futureeval-bot-tournament.
- **Période mesurée** : janvier 2025 → été 2026 (versements trimestriels puis par saison de 4 mois).
- **Profit réalisé** : 30 000 $/trimestre en 2025, 50 000 $/saison en 2025-2026. Par acteur : gagnant ≈ 7 500 $/trimestre ; bot payé médian ≈ 900 $/trimestre (Q2 : 14 617 $ / 16).
- **Concentré sur quelques acteurs ?** Oui : top 3 = 51 % (Q2) à 57 % (Q1) du pool.
- **Frais 2026 inclus ?** Les prix sont nets ; coût = API LLM et recherche (crédits gratuits fournis ; en Q2 la plupart évitaient o3 pour son coût).
- **Dépend de la vitesse ?** Non. Fenêtres de plusieurs jours par question.
- **Capital minimum** : 0 (pas de mise). Coût d'infrastructure seulement.
- **Risque extrême caché** : disparition du programme ; règle d'attribution des prix non vérifiée ici (pages 403) ; bots internes de Metaculus en concurrence ; concurrence croissante des bots open-source (le gagnant Q2 a publié son code).
- **Venues et accès** : metaculus.com, mondial ; éligibilité aux prix soumise à un questionnaire. US / UE / France : a priori ouvert (non vérifié pour les restrictions de paiement).
- **Vérification 1 jour** : oui, classements et notebooks publics.
- **Plafond estimé à petite taille** : **~2 000 €/mois** pour un bot en tête, ~300 €/mois pour un bot dans le top 20. C'est le seul reçu de cette liste sans mise et sans course à la vitesse, aligné avec nos atouts (IA qui lit à grande échelle, automatisation 24 h/24).
- **Confiance** : vérifié pour Q1-Q2 2025 ; probable pour 2026 (pool annoncé, résultats non ouverts).

---

## R5 | Numerai — versements mensuels réels aux data scientists (Tournament + Signals + Crypto)

- **Type** : paiement de la prédiction (avec mise en jeu de jetons).
- **Mécanisme** : Numerai (hedge fund) paie en NMR les modèles dont les prédictions améliorent son méta-modèle ; la mise (stake) est brûlée en cas de score négatif. Le payeur peut réduire les paiements à volonté (facteur de paiement, clip, seuil de stake) ; il l'a fait plusieurs fois.
- **REÇU** (versements publiés par la plateforme, toutes compétitions confondues) :
  - Novembre 2025 : **251 850 $** de NMR — https://blog.numer.ai/numerai-december-2025-update/
  - Janvier 2026 : **182 039 $** — https://blog.numer.ai/numerai-monthly-numercon-agents-staking-risk-1m-nmr-buyback/
  - Juillet 2026 : **345 335 $** — https://blog.numer.ai/numerai-monthly-nmr-buyback-quantum-dataset-atomic-blockchain-staking/
  - Chiffres vus seulement en extraits de recherche (pages **non consultées**) : avril 2025 532 447 $, juin 2025 184 248 $, septembre 2025 ~478 000 $, cumul historique > 43 M$.
  - Règles Signals : https://docs.numer.ai/numerai-signals/staking — payout = stake × clip(payout_factor × (0,3·Alpha + 0,8·MPC), ±3,5 %) par round ; payout_factor = min(1 ; 36 000 NMR / total en jeu) ; clip relevé de 1,7 % à 3,5 % au 1er janvier 2026 (vote communautaire, billet de déc. 2025) ; nouvelle formule 0,5·NCORR + 2·NMMC à partir du round 1363 (25 sept. 2026).
- **Période mesurée** : 2025-2026, versements mensuels.
- **Profit réalisé** : 180 k$ à 530 k$ par mois pour l'ensemble des participants. **Split Signals / Tournament / Crypto non publié** dans les billets ouverts. Par acteur : non publié ; dispersion inconnue.
- **Concentré sur quelques acteurs ?** Probable (payout proportionnel au stake ; seuil de 36 000 NMR pour Signals avant dilution) mais **non vérifié**.
- **Frais 2026 inclus ?** Pas de frais de plateforme ; coût réel = risque de burn (jusqu'à -3,5 %/round), immobilisation (verrou de 12 semaines évoqué dans un extrait de recherche, non consulté) et exposition au prix du NMR.
- **Dépend de la vitesse ?** Non. Soumission hebdomadaire.
- **Capital minimum** : achat de NMR (crypto) ; sans stake, pas de paiement.
- **Risque extrême caché** : chute du NMR, burn répété, changement de règles unilatéral (fréquent), dilution par payout_factor si le stake total dépasse le seuil.
- **Venues et accès** : numer.ai, mondial ; nécessite un wallet Ethereum et des NMR. US / UE / France : ouvert (fiscalité crypto à part).
- **Vérification 1 jour** : oui : l'API GraphQL publique (numerapi) expose les scores et payouts par modèle et par round ; une journée suffit pour reconstituer la distribution des payouts Signals sur 2025-2026. **C'est la mesure manquante** avant toute décision.
- **Plafond estimé à petite taille** : borne théorique 3,5 %/round sur le stake ; le rendement moyen réel sur stake n'est publié nulle part dans les sources ouvertes → **non vérifié**. À 5 k€ de stake et +1 %/mois net de burn, ~50 €/mois.
- **Confiance** : probable (versements agrégés vérifiés, rendement individuel non vérifié).

---

## R6 | Arbitrage Polymarket ↔ Kalshi — écarts persistants, aucun profit réalisé mesuré

- **Type** : arbitrage (cross-venue).
- **Mécanisme supposé** : même événement coté sur deux venues à des prix différents. En pratique le payeur n'existe pas : les contrats ne sont pas fongibles (règles de résolution différentes) et les deux venues séparent juridiquement leurs clients.
- **REÇU (négatif)** : Gebele & Matthes, *Semantic Non-Fungibility and Violations of the Law of One Price in Prediction Markets*, 5 janv. 2026 — https://arxiv.org/abs/2601.01706. > 100 000 événements, 10 venues, 2018-2025 ; ~6 % des événements cotés simultanément sur plusieurs plateformes ; écarts moyens persistants de 2 à 4 % sur marchés sémantiquement équivalents. **Mesure des écarts de prix seulement, aucun profit exécuté reconstruit.** Raisons avancées : absence d'identité d'événement partagée, arbitrage capitalistique ou inexécutable, croyances locales à la plateforme.
- **Période mesurée** : 2018-2025 (écarts), pas de profit.
- **Profit réalisé** : **aucun mesuré** dans la littérature ouverte. Les guides et bots commerciaux trouvés (Apify, PillarLab, Claw Arbs…) ne publient pas de registre vérifiable : non retenus.
- **Concentré ?** Sans objet.
- **Frais 2026 inclus ?** Sans objet.
- **Dépend de la vitesse ?** Oui pour les rares écarts exécutables.
- **Capital minimum** : deux comptes financés + capital bloqué jusqu'à double résolution.
- **Risque extrême caché** : résolutions divergentes (une jambe perd, l'autre est annulée), interdiction de détenir légalement les deux comptes (Kalshi = résidents US ; Polymarket = non-US).
- **Venues et accès** : Polymarket + Kalshi. **Hors de portée pour un particulier français** (Kalshi inaccessible ; Polymarket bloqué en France).
- **Vérification 1 jour** : oui pour les écarts (deux API publiques), non pour un profit réalisé.
- **Plafond estimé** : 0 € tant qu'aucune mesure d'exécution n'existe et que l'accès double est illégal.
- **Confiance** : vérifié comme négatif structuré.

---

## R7 | Fournisseurs de liquidité Uniswap — pertes collectives mesurées on-chain (2025-2026)

- **Type** : autre (LVR / sélection adverse).
- **Mécanisme** : les LP passifs vendent des options gratuites aux arbitrageurs qui rééquilibrent le pool contre les prix des CEX ; les frais ne couvrent pas cette « theta ». Le reçu prouve que quelqu'un encaisse (arbitrageurs, searchers MEV), mais ce côté exige vitesse et infrastructure.
- **REÇU (négatif)** : Falkenstein, *Uniswap LPs Losing More After Fee Switch*, 19 août 2026 — https://efalken.substack.com/p/uniswap-lps-losing-more-after-fee. 22 pools (19 v3, 3 v2) sur Ethereum, Arbitrum, Base, Avalanche ; méthode markout contre prix CEX horaires et « Liquidity-Variance theta » ; métrique coût/revenu de frais > 1 = perte collective ; ratio en hausse en 2026 pour v2 et v3 après le fee switch (28 déc. 2025 Ethereum ; 6 mars 2026 L2) ; les LP v3 « perdent de l'argent » tout en portant l'essentiel de l'activité. Chiffres en pourcentage non isolés dans l'article. Références plus anciennes (Uniswap v3 ETH/USDC, ~100 M$ de pertes après frais par markout, CrocSwap 2022 ; Vakhmyanin mai 2024 PnL par LP sur Ethereum/Arbitrum) : **non consultées** (403/503).
- **Période mesurée** : 2025-2026 (trimestriel).
- **Profit réalisé** : négatif pour les LP en agrégat. Le profit des arbitrageurs n'est pas décomposé dans la source.
- **Concentré ?** Côté gagnant, oui (searchers/MEV, non mesuré ici).
- **Frais 2026 inclus ?** Oui, y compris le nouveau prélèvement protocolaire.
- **Dépend de la vitesse ?** Côté gagnant : oui, totalement.
- **Capital minimum** : sans objet.
- **Risque extrême caché** : LVR en pic de volatilité (jusqu'à plusieurs milliers de pb/jour selon extraits de recherche, non consultés).
- **Venues et accès** : DEX, mondial, sans KYC.
- **Vérification 1 jour** : oui, les logs de pools sont publics ; un markout sur un pool prend une journée.
- **Plafond estimé à petite taille** : **négatif** pour la fourniture de liquidité passive ; 0 € côté arbitrage sans infrastructure de latence.
- **Confiance** : vérifié (source ouverte, mesure on-chain), sans chiffre agrégé en euros.

---

## Négatifs utiles (prouvé mort ou hors de portée, mesures 2024-2026)

1. **Carry / funding crypto (rejet confirmé)** : Binance, août 2020 → mai 2025, Sharpe 6,45 sur l'échantillon complet, 4,06 en 2024, **négatif en 2025** (Fig. 2, https://arxiv.org/html/2510.14435v2). L'étude ScienceDirect sur l'arbitrage de funding CEX/DEX (S2096720925000818) : non consultée (403).
2. **Prendre (take) sur Kalshi et Betfair** : -31,46 % (Kalshi, tous contrats, après frais) et -2,5 % (Betfair pré-match, après commission) ; le take n'est positif que sur les favoris > 70 ¢ et faiblement : confirme nos rejets « favoris > 90 ¢ » et « NO systématique ».
3. **Arbitrage cross-venue Polymarket/Kalshi** : écarts de 2-4 % documentés, profit exécuté jamais mesuré, accès double illégal pour un même particulier.
4. **Arbitrage intra-Polymarket sans bot** : estimation stricte 291 k$ sur un an pour tout le marché, 75 % chez 10 adresses ; l'estimation large (39,6 M$) n'est pas un encaissement garanti (VWAP par bloc, jambes non atomiques).
5. **LP passif Uniswap v2/v3** : coût/revenu > 1 mesuré on-chain en 2026, aggravé par le fee switch ; le gain va aux arbitrageurs rapides.

---

## Rapport final

- Branche : `claude/gallant-cerf-e0rpao` ; SHA : voir `git log -1` (renseigné dans `agent2_etat.md`).
- Trois meilleures fiches : **R2** (Kalshi makers, +2,6 % ≥ 50 ¢, US seulement), **R1** (Polymarket arb intra-marché, encaissement réel contesté 0,29 M$ ↔ 39,6 M$), **R4** (Metaculus, ~2 k€/mois pour le bot en tête, sans mise ni vitesse).
- Action de vérification la moins chère : recalculer la distribution des payouts Numerai Signals par modèle via l'API publique (R5), puis recompter les paniers YES+NO < 1 $ sur une semaine de données CLOB Polymarket (R1).

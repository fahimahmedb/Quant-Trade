# Quant-Trade — qualification étendue des mécanismes issus de cinq enquêtes financières

**Date :** 22 novembre 2026  
**Chantier :** hypothèses économiques exclusivement. Le comportement des IA est confié à un autre chantier.  
**État des conclusions :** documentaires et bornées ; aucune preuve d'alpha investissable ; aucune allocation ni activation autorisée.  
**Périmètre contrôlé :** 16 classes d'expressions/tests (dont plusieurs sous-familles des neuf hypothèses originales), 93 assertions exécutées et réussies dans le script joint. **93 PASS arithmétiques, contractuels et structurels ne signifient PAS 93 backtests ni validations économiques.**

## 1. Sources et autorité

### Sources internes vérifiées

- GitHub `fahimahmedb/Quant-Trade`, `project/canonical@668214eae51425d9e3a2208d79978e978ede39fb`, `code/canonical@2ec0454a71f747b0ece39ba2e93f6c48265dabf5` au début du lot ; actualiser avant mutation future.
- [Issue économique active #60](https://github.com/fahimahmedb/Quant-Trade/issues/60) et commentaires antérieurs `7077809471`, `7077818314`, `7071750308`, `7071760416`, `7071808892`.
- `governance/AI_WORKING_METHOD_V1.md`, blob `12bec44b351b34ba298ddc3d1ad32e2b9df79697`, §5.2.2 ; `QUANT_NORTH_STAR.md`, blob `8295041a8d253636d8f8aab941b811dce64939d9`.
- Résultats sources de simulation existants :
  - `qt-open-macro-crossasset-20261122-result.json@d57b7e5ec571a6c206fecd5a371e2c2eb7c74cea` ;
  - `qt-open-cpi-energy-industry-20261122-result.json@3f3d8aee8f6a4dc8f03287e9775a4e21656ea69b` ;
  - `disc-stockbond-joint-stress-rebound-l1-v1.result.json@b4b0460483e1c978d2cc3202df788c0f6a7e5368` ;
  - `disc-sector-relative-shock-reversal-l1-v1.result.json@03c0176a3363d1980050d43f44712dd42752b551` ;
  - `disc-monthend-pension-rebalance-spytlt-l1-v1.result.json@cb7805a102bcfc35d32a60932e560b6298c767ef` ;
  - `disc-cfe-vix-term-premium-l1-v2-reader.result.json@44a792e222f5cd763dcf1becdab9a6eb4d728286` et contrat `@4784e9af2b22cac19d229fd6dc42bab567575358`.
- **Cette session n'a pas rechargé les 30 168 lignes brutes ni réexécuté les simulations historiques.** Les assertions sur celles-ci recontrôlent les identités des résultats déjà publiés ; leurs preuves restent celles des exécutions antérieures, dont l'OOS et le PIT ne sont pas établis.

### Sources primaires externes ciblées

- [Banque d'Angleterre, *Fire sales of safe assets*](https://www.bankofengland.co.uk/working-paper/2024/fire-sales-of-safe-assets) ; les prix des gilts dépréciés ne sont pas des rendements de fonds.
- [Banque mondiale, émission cat bond Jamaïque mai 2026](https://www.worldbank.org/en/news/press-release/2026/05/18/world-bank-prices-catastrophe-bond-for-disaster-protection-for-jamaica) : montant, marge de risque et **restriction à investisseurs institutionnels qualifiés**.
- [SEC, Shopify 10-Q, 30 septembre 2026](https://www.sec.gov/Archives/edgar/data/1594805/000159480526000068/shop-20260930.htm), note 6, bilan/allocations/créances et retards.
- [Nexans–Enedis, communiqué du 4 février 2026](https://www.nexans.com/fr/communiques-de-presse/contrat-strategique-de-7-ans-avec-enedis-en-france/) : 600 M€ en contrat-cadre sur sept ans dont trois optionnels.
- [ArcelorMittal, résultats T3 2026](https://corporate.arcelormittal.com/media/news/regulatory-news/arcelormittal-reports-third-quarter-2026-results) et [FAQ carbone](https://corporate.arcelormittal.com/sustainability/climate/climate-faq) : mesures de marge et déclarations de quotas ; pas de rapprochement indépendant des transferts.
- [Euronext, FY2025](https://www.euronext.com/en/investor-relations/financial-information/news/euronext-publishes-q4-and-full-year-2025-results) et [T3 2026](https://www.euronext.com/en/about/media/euronext-press-releases/euronext-publishes-q3-2026-results-and-announces-share).
- [Fed, expositions Treasury basis juin 2026](https://www.federalreserve.gov/econres/notes/feds-notes/decomposing-hedge-funds-u-s-treasury-exposures-20260622.html) ; [Cboe, multiplicateur VX](https://www.cboe.com/tradable-products/vix/vix-futures/specifications).
- [PJM, droits de congestion FTR](https://www.pjm.com/markets-and-operations/ftr.aspx) ; [SEC, risque MBS](https://www.sec.gov/reports/staff-report-enhancing-disclosure-mortgage-backed-securities-markets).
- [impots.gouv.fr, PEA après cinq ans](https://www.impots.gouv.fr/particulier/questions/jai-un-plan-depargne-en-actions-pea-les-retraits-sont-ils-imposables) ; [économie.gouv.fr, PFU en 2026](https://www.economie.gouv.fr/particuliers/impots-et-fiscalite/gerer-mes-autres-impots-et-taxes/comment-fonctionne-le-prelevement-forfaitaire-unique-pfu?language=fr).

## 2. Résultats — couverture des familles

| Famille | Source de test | Résultat observé ou calculé | Conclusion stricte |
|---|---|---|---|
| H-FLOW : ventes forcées | Ancien essai gelé SPY/TLT J+1 | 83 événements, coût central 8 pb, rendement moyen net **−9,996 pb**, 33 réussites sur 83 | `KILL_EXPRESSION` **uniquement** pour SPY/TLT open–close après stress conjoint ; mécanisme BoE toujours observé, rentabilité d'un opérateur privé `UNKNOWN` |
| H-DRYPOWDER : réserve de cash | Modèle synthétique 3 % cash/7 % marché, 5 ans, épisode possible après 3 ans | Décote minimale **10,801 %** si événement certain ; **41,330 %** si probabilité fictive 25 %, retour immédiat à juste valeur et coûts nuls | `COUNTEREXAMPLE` à « garder du cash pour toute décote de 10 % » ; fréquence, exécution et mérite de la réserve réelle `UNKNOWN` |
| H-JOINT : valeur marginale des informations | Résultats gelés de deux modèles combinés + test de décision synthétique | Courbe × tendance : 1,368405 contre passif 1,637272 ; CPI × secteur : 2,331091 contre prix seul 2,385968. Une nouvelle information peut aussi être vraie sans modifier l'action | `NO_INCREMENTAL_ADVANTAGE` démontré pour ces expressions, **pas** pour toute recherche multi-sources |
| H-INDUSTRY : contrats × réglementation | Nexans/Enedis et Arcelor/ETS sources primaires, arithmétique contrôlée | Contrat Nexans 600 M€ sur sept ans avec trois optionnels. Si marge incrémentale fictive 5 % sur 600 M€, 30 M€ cumulés **conditionnels**, pas une valeur d'action. Quotas Arcelor corrigés de 72,056762 M transférés : déficit déclaré de **29,323123 M** contre surplus brut trompeur de **42,733639 M** | `MECHANISM_DOCUMENTED`, attribution de cash-flow et prix action `UNKNOWN` |
| H-IMPLEMENT : coûts d'exécution | Tarifs et fiscalité déjà documentés dans #60, test de seuil | TTF Nexans achat de 5 000 € : 20 €. Deux ordres à 1 € = 2 €/A/R ; un « sans commission » avec **20 pb** de spread total sur 1 000 € coûte aussi 2 €. Double change fictif sur 5 000 € : 50 € à 0,5 % chaque fois ou 15 € à 0,15 % | `COST_IDENTITIES_PASS` ; meilleurs vrais fills, qualité et compte autorisé `UNKNOWN` |
| H-ILS : assurance catastrophe | Banque mondiale : contrat 2024/2026 et stress EL ×1,2,3 | Marge de risque moins perte moyenne modélisée : **5,39 / 4,27 points**, sans frais, risque capital ni rendement collatéral. Pour 2026, si perte moyenne triplée et coût fictif 1 %/an, différence = **−1,69 point/an** | `RISK_TRANSFER_OBSERVED`; l'obligation 2026 est institutionnelle, pas un instrument directement accessible au retail français standard |
| H-INTERMEDIARY : posséder le péage | Comptes Euronext FY2025/T3 2026 ; cas P/E synthétique | FY2025 marge EBITDA ajustée ~62,7 %, revenu hors volume 59 %. Si P/E passe fictivement de 30 à 20 en 3 ans, croissance du BPA **14,47 %/an** nécessaire pour conserver le prix de l'action hors dividendes | `FRANCHISE_OBSERVED`, pas de plus-value actionnaire ou d'alpha prouvé |
| H-OPTION : options cachées | Simulation de cash-flow d'une obligation callable | Obligation fictive au prix 102, nominal 100 et coupon annuel 5 % : rendement si call année 2 **3,94 %**, contre **4,44 %** si échéance année 4 | Coupon, YTM, YTC ne sont pas interchangeables ; valeur d'une erreur de tarification `UNKNOWN` |
| H-PLATFORM : données de paiement et crédit | 10-Q Shopify, note 6 | Créances brutes 2 596 M$, provision 246 M$, ratio **9,48 %** (contre **9,85 %** fin 2025). Retards 90+ jours : **194/2596 = 7,47 %** contre **135/1979 = 6,82 %** fin 2025. Provision 195 + dotation 217 − charge-offs nets 166 = 246 | **Contradiction comptable : provision relative en baisse et impayés 90+ relatifs en hausse**, sans causalité déduite. Cohortes et maturités non homogènes ; rendement net du crédit `UNKNOWN` |
| H-FUNDING : cash–futures basis | Scénario synthétique de financement | 100 M$ notionnel, écart +20 pb, choc repo −30 pb : perte **100 000 $**, soit 2 % de 5 M$ de fonds propres ; une hausse fictive de marge de 5 % du notionnel appelle 5 M$ de liquidité supplémentaire, **ce n'est pas une perte P&L** | Risque de solvabilité et risque de liquidité distincts ; spread exécutable `UNKNOWN` |
| H-PHYSICAL : stockage et électricité | Scénario physique théorique | Un baril acheté au règlement WTI −37,63 $ avec valeur de revente nulle et stockage à 20 $ procure +17,63 $ avant frais ; stockage à 40 $ transforme le résultat en −2,37 $. Batterie : (100 − 20/0,85) = 76,47 €/MWh livré avant dégradation, puis −3,53 € si charge complète 80 €/MWh | Le prix seul est insuffisant : capacité physique, livraison, financement, risque réseau et dégradation ; P&L investissable `UNKNOWN` |
| H-RISK : richesse terminale | Identité mathématique | Alternance fictive +20 %, −20 % : moyenne arithmétique 0 %, rendement géométrique **−2,02 %** par période ; −50 % exige +100 % pour revenir au pair | Un Sharpe ou une moyenne peuvent dissimuler une perte composée et un chemin insoutenable |
| H-VIX : prime de variance / futures | Ancien essai gelé CFE 2013–2021 et nouvel audit **des totaux publiés uniquement** | **36 opérations**, moyenne nette centrale +0,974 point VX (+974 $/contrat par opération au multiplicateur Cboe), **7/9 années positives**, pire trade −14,7 points (−14 700 $). Retrait de 2018 : moyenne positive +0,736 point ; bootstrap par années du **brut** a un intervalle 95 % comprenant zéro : [−0,0107 ; 2,1038] | `PROMOTE_EXPRESSION` historique dans le protocole. **Pas** `EDGE_VALIDATED` : règlements ≠ fills, marges et pertes intra-position non reconstituées, 2022–26 hors test, prix/frais/accès France inconnus |
| H-SECTOR-SHOCK : choc relatif sectoriel | Ancien essai gelé | 722 événements ; gain brut moyen +4,155 pb, mais coût central 8 pb : résultat net moyen **−3,845 pb** | `KILL_EXPRESSION` ; ne pas réduire les coûts a posteriori jusqu'à un résultat positif |
| H-MONTHEND : rééquilibrage institutionnel | Ancien essai gelé | 120 mois, 37 signaux dans un sens contre 40 exigés, 83 dans l'autre | `PARK_DATA`, aucun payoff calculé. Réduire à 37 serait une manipulation du seuil |
| H-TAX : friction fiscale du patrimoine | Droit français 2026 et même plus-value réalisée, sous conditions | Pour **2 500 € de gain réalisé en 2026** sur 5 000 € investis : CTO PFU 31,4 % → richesse finale **6 715 €** ; PEA après cinq ans, prélèvements sociaux 18,6 % → **7 035 €** ; écart **320 €** à risque/gain identiques | `CONDITIONAL_TAX_SAVING` ; produit réellement éligible, ancienneté, frais, résidence et alternative fiscale à contrôler ; ne prouve pas le gain spécifique d'une IA |

## 3. Trois corrections qui changent matériellement la lecture

**A. Il existe bien une expression historique positive dans le dépôt.** L'essai court VIX 2013–2021 n'est pas à cacher parmi les négatifs. Mais son propre résultat dit qu'il ne quantifie ni capital/marge, ni risque intra-position, ni gain net exécutable pour un particulier ; l'intervalle de confiance brut par blocs annuels inclut zéro. Test suivant potentiellement décisif : données 2022–2026 réellement négociables, risque de marge et coûts historiques, selon une **nouvelle admission gelée avant tout nouvel accès au résultat**. Ne pas comparer le gain en dollars sur un VX standard au rendement annuel d'un ETF sans dénominateur capital.

**B. Les états comptables ne fournissent pas directement des probabilités ou de l'alpha.** Shopify montre que le stock de provision et le stock de créances retardées peuvent évoluer en sens opposés. Seul un suivi des cohortes avec sélection, échéances, prix du crédit et recouvrement permet de mesurer la contribution des données de plateforme. Pareil pour les quotas ETS : il faut identifier les transferts et les coûts vraiment supportés, pas déduire une plus-value d'un nombre de quotas. Pour ArcelorMittal, le même EBITDA Europe T3 2026 est **−149 M$ par rapport à T2 2026** mais **+35 M$ par rapport à T3 2025** : le choix du comparateur change le signe de la conclusion descriptive.

**C. L'accès fait partie du mécanisme.** L'obligation jamaïcaine présente des restrictions d'investissement institutionnel dans le communiqué de la Banque mondiale. Les ETF US du projet ne sont pas automatiquement admissibles à l'achat pour un retail français. Les futurs VX demandent marge et droits sur dérivés ; aucun rendement sur capital économique n'est certifié. Aucun de ces obstacles n'autorise à éliminer l'hypothèse générale ; il impose de distinguer l'instrument directement achetable, l'exposition indirecte, et le simple enseignement économique.

## 4. Tests réellement effectués et tests NON effectués

**RÉELLEMENT EXÉCUTÉS DANS CE LOT :** script Python `qt_hypotheses_couverture_tests_2026-11-22.py` (93 assertions PASS), fichier `qt_h2_5rapports_tests_structurels_2026-11-22.json` généré ; contrôle arithmétique de rapports primaires et d'anciens résultats GitHub exacts, grilles de stress **expressément synthétiques**. Les deux fichiers incluent les hypothèses de chaque calcul. Aucun jeu de prix historique brut nouveau n'a été téléchargé ou testé. Les 93 assertions confirment la cohérence des identités et des contre-exemples construits, **non** la validité statistique, climatique, commerciale ou économique d'une stratégie.

**PAS EXÉCUTÉS / NON REQUALIFIÉS EN PASS :** prévision des cours, backtest d'opérations nouvelles, PIT strict, OOS indépendant, simulation historique intratrade VIX, marge et funding historique, quotes bid/ask synchronisées, éligibilité de tous les instruments au compte réel, fiscalité individuelle complète, rentabilité net et after-tax, test prospectif, expérience d'une IA distincte d'une règle simple, certification de valeur économique end-to-end et toute opération avec capital réel.

## 5. Prochaines preuves qui pourraient réellement déplacer la décision

1. **H-VIX** — compléter le risque de portefeuille historique et les données 2022–2026 sous protocole **nouveau et borné** ; vérifier le prix d'exécution réel et la marge/collatéral, puis calculer une richesse réelle après coûts. **Veto** si absence de PIT, quote exécutable ou admission spécifique. Ne pas retuner le protocole ancien.
2. **H-INDUSTRY** — pour Nexans/Enedis, dates de commande réellement fermes, marges incrémentales, chevauchement des carnets et valeur déjà contenue dans les prix. Pour ArcelorMittal/CBAM, comptes carbone par installation, transferts et énergie, sans projeter l'ancien DRP sur l'EAF 2026. **La prochaine action est documentaire**, pas un balayage de paramètres d'ETF.
3. **H-IMPLEMENT / H-TAX** — documenter un instrument **identique et éligible** aux deux enveloppes/comptes, frais complets et richesse réellement liquidable. Comparer à une règle déterministe simple pour isoler l'apport éventuel de l'IA.
4. **H-FLOW** — dater un vendeur effectivement contraint et le carnet utilisable **avant** la réaction, à risque duration/crédit contrôlé. Les expériences déjà mortes sur SPY/TLT J+1 et retournement sectoriel restent fermées.
5. **H-INTERMEDIARY** — comparer Euronext à un benchmark de risque adéquat avec valorisation ex ante et prix d'entrée, non EBITDA seul. Ne pas construire une liste ex post de gagnants.
6. **H-ILS / H-PLATFORM / H-OPTION / H-PHYSICAL** — conserver `PARK` au niveau P&L tant que manque la série contractuelle, le recouvrement, les clauses exerçables ou le coût physique exécutable. Ne pas créer de fausse précision en remplaçant ces pièces par des moyennes issues d'autres marchés.

## 6. Séparation des responsabilités et arrêt

Ce lot reste exclusivement un travail sur des **hypothèses économiques et leurs preuves**. Aucune modification de prompts d'agents, de mémoire automatique, d'architecture, de routeur ou de méthode IA ; ces sujets relèvent de l'autre IA. Le registre canonique de continuité est toujours **l'issue #60**. L'autre chantier ne doit pas être contaminé par une prétention que « 93 tests PASS » signifie « modèle gestionnaire qualifié ».

**Conclusion :** couverture documentaire étendue et contrôles structurels réussis ; une expression historique VIX positive, deux familles de réponses négatives nettes et de nombreux mécanismes économiques réels mais économiquement `UNKNOWN`. Pas de promotion live ni de modification de portefeuille.

### Artefacts de ce lot

- `qt_hypotheses_couverture_tests_2026-11-22.py` — script source, identités et scénarios explicites.
- `qt_h2_5rapports_tests_structurels_2026-11-22.json` — 93 assertions, grilles, données documentaires, synthèses structurées.
- Ce fichier Markdown — périmètre, preuves, falsificateurs, limites et prochaines décisions.

**Preuve de respect du protocole :** identités Git exactes citées ; 93 assertions exécutées dans Python ; sources institutionnelles listées ; tests négatifs préexistants non réoptimisés ; distinction explicite entre calcul, simulation, qualification et preuve de gain net. 
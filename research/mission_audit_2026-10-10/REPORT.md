# Quant-Trade — audit et recommandations au propriétaire

10 octobre 2026. **STATUS = AWAITING_OWNER_FEEDBACK**. Phases 1–4 seulement. Aucun nouveau test économique, aucune ouverture des fichiers outcomes F1 A/B, aucun worker lancé, aucune fusion. `REAL_CAPITAL_AUTHORIZED = FALSE`; `LIVE_TRADING_AUTHORIZED = FALSE`.

**Conclusion décisionnelle.** Quant-Trade possède déjà une bonne partie du logiciel et des disciplines nécessaires à la recherche. Le manque principal observé est une chaîne courte et cohérente reliant mécanisme, données réellement utilisables, expérience informative et décision persistée. Les obstacles démontrés sont multiples : résultats faibles, données/exécution manquantes, puissance limitée et états dispersés. L'audit n'établit ni que la gouvernance est la cause dominante de la lenteur, ni qu'un alpha actuel accessible existe. Je recommande l'option minimale décrite ci-dessous avant tout nouveau labo.

Les faits et limites sont indexés dans [EVIDENCE.jsonl](EVIDENCE.jsonl), avec versions et passages primaires. Les SHA complets et la reprise figurent dans [CHECKPOINT.md](CHECKPOINT.md). Les statuts historiques ne sont pas présentés comme télémétrie actuelle.

**1. Audit : périmètre et inventaire vérifié**

GitHub a été interrogé avant le clone local sans checkout. Base distante : `blue/master-v2-2026-09-20@09ba64b8bee1419076ec8a30f8d75a916932c2ba`, dernier commit du 27 septembre. Inventaire initial : 191 branches, 8 PR ouvertes (#21–28). Ces nombres ne mesurent pas l'efficacité. Le clone contient un historique accessible commençant le 13 juillet 2026 : il ne suffit pas à mesurer les deux années de travail évoquées par Owner.

| Surface vérifiée | État et portée |
|---|---|
| [PR #21][pr21], `0f9cb618` | Deux rails déjà proposés, avec état vivant et registre. Une ancienne allocation de 10 itérations/200 essais/5 agents n'est ni le budget ni l'autorisation de cette mission. |
| [PR #22][pr22], `1e88c6b` | Coordination, boards, B2/B4. 246 entrées de discussion récupérées ; examen ciblé des décisions et contradictions. **Ne jamais fusionner.** |
| [PR #26][pr26], `ea9d2d0` | Clôture publique F1. Disposition et métadonnées de jobs consultées ; outcomes A/B non rouverts. |
| [PR #27][pr27], `e7344cf` | F2 bloqué par droits d'accès, pas par résultat économique. |
| [PR #28][pr28], `e42d4924` | Avancée depuis `df8ecb32` : harnais EURUSD complet gelé, 70 cas FX et 28 tests d'état causal annoncés ; étapes CI synthétiques réussies vérifiées. Aucun edge établi. |
| Scouts `2b66b193`, `5bb78345`, `a6961e5f`, `afd69b74` | Respectivement negative-risk valide, Treasury/GFS, liquidation Hyperliquid, événements actions. Sources et limites ci-dessous. |
| [Branche données][feeds], `20cc984` à l'inspection | Collecte programmée réellement exécutée ; registre fast rail historique et H001. Ce travail n'apparaît pas dans le seul checkpoint récent d'edge search. |

**Hypothèses, résultats et expositions.** Une variante n'est pas une famille indépendante. Les lectures de résultats publics ci-dessous et de littérature sont enregistrées comme expositions pour une sélection future.

| Famille / source | Ce qui a réellement été appris | Limites, fenêtres et essais |
|---|---|---|
| NASDAQ reversal, mémoire à `09ba64b8` | Ancien rejet : coûts, moitiés et concentration échouent. | Proxy indice ; ancienne convention close→close. Résultat historique non recalculé. La prévision de variance NASDAQ ne démontre pas de profit directionnel. |
| [B2 relatif sectoriel][b2], `1e88c6b` | Reproduction par le même code du négatif corrigé : net OOS −6,08 %, brut −1,37 %, t −0,389. Réduction de turnover insuffisante. | 36 expressions déclarées ; découverte 2016-09-12..2022-03-08, validation 2022-03-09..2025-03-11 consommée. Deux variantes du même mécanisme, pas deux nouvelles familles. Ni réplication indépendante ni absence universelle d'edge. |
| [B4 TSMOM][b4], `1e88c6b` | +6,69 % net modélisé, mais rejet des critères figés : t 0,488, première moitié négative, gains concentrés par année. | Quatre lookbacks ; total dataset 40. Même validation déjà dépensée. `TRIAL_COUNT_SOURCE=STATE_MD_NO_REGISTRY` : historique accessible incomplet. Faible bêta SPY ≠ alpha multifactoriel. |
| [F1 carry][f1public], clôture `ea9d2d0` | Expression θ=0,20 : moyenne annuelle −1,357 %, Sharpe −0,449, t robuste −0,843 ; **REJECT conservé**. | 1 004 jours B ; IC descriptif moyenne −4,51 %..+1,80 %. Rejet du protocole/cible, pas exclusion de tout petit effet. Jours, non 457 symboles, portent l'information. Trois cellules figées ; comparateur cash 4 % supposé, non mesuré ; historique privé UNKNOWN. |
| [Polymarket negative-risk][nr], `2b66b193` | Seul rerun corrigé valide : 1 260 routes exécutables examinées, zéro dépassement ; **KILL borné conservé**. | 21 clés de route, 10 événements, 60 rounds : observations dépendantes, courte collecte. Premier KILL invalidé par erreur d'horloge ; jamais réhabilité. Ne réfute ni tous les arbitrages ni le market making. |
| [F2 favorite-longshot][f2terms], `e7344cf` | Aucun test économique : **BLOCKED_DATA_PERMISSION** après lecture primaire des conditions. | Pas de look consommé par cette qualification. Accès HTTP public n'est pas permission. Défauts du manifeste à réparer seulement si l'accès devient admissible. |
| EURUSD grille, `e42d4924` | Candidat exploratoire préinscrit et logiciel synthétiquement contrôlé. | HistData : 21 mois planifiés, 433 jours de semaine, MAIN + deux ablations, six chemins de coûts. Pas de résultat de marché publié au head inspecté. Expositions antérieures/vendor conservées ; privé UNKNOWN. |
| COIN-M liquidation, `e42d4924` | Source rejetée pour horloge de disponibilité ambiguë et snapshots incomplets. | **Échec de source**, pas réfutation d'un mécanisme économique. Ne pas substituer ces données au protocole Hyperliquid. |
| [Hyperliquid][hl], `a6961e5f` | Mécanisme forcé versus volontaire, horizon 30 s, harnais/recorder synthétiques existants. | Hôte de nœud conforme et collecte prospective manquants. Le simple flux trades ne fournit pas les labels requis. Attente d'observation incompressible. |
| [Treasury/ZF][macro], `5bb78345` | Protocole figé de pression d'adjudication ; aucun résultat ZF. GEFS/GFS→gaz reste une réserve distincte. | BBO historiques et chaîne de contrats manquants/payants ; prix du paquet exact NON MESURÉ. Horloges de publication météo et prix gaz exécutables à qualifier. |
| [F3 / Form 4 et 13D][events], `afd69b74` | Achat Form 4 individuel = variante F3 ; annonce initiale 13D = mécanisme distinct. | Chaîne CIK→titre à la date→radiations→prix→corporate actions absente. Recensement SEC existant, pas besoin d'un deuxième collecteur. |
| Fast rail H‑001..H‑014, `20cc984` | Registre déjà présent : carry HL/dYdX, listings, météo/FLB, sport, calendrier, RFQ et volatilité. Résultats négatifs, insuffisance et accès mélangés sous plusieurs anciens labels. | H‑002 dataset déclaré brûlé ; H‑005 et H‑006 limités par puissance/concentration ; H‑012 RFQ 401 ; H‑008/H‑013 non entrés. Ces traces ne remplacent pas une réconciliation de chaque expression. Ne pas sommer naïvement leurs compteurs avec F1/B2/B4. |

Le shadow du panel sectoriel n'a pas été ouvert. L'absence d'une ancienne preuve dans ce clone ne restaure aucun holdout. Aucun calcul de performance n'a été relancé.

**Données, droits et horloges.**

| Source | Utilité réelle et obstacle décisionnel |
|---|---|
| Panel daily ETF | Opens ajustés cohérents avec distributions, mais `adj_close` révisé a posteriori ; absence de corporate-action PIT, coût 5 pb supposé et borrow omis dans B2. Une précision logicielle ne répare pas ces hypothèses. |
| Binance Vision/F1 | Archives et checksums persistés ; licence CC BY-NC-SA 4.0 documentée pour recherche non commerciale. Liquidations quotidiennes restent un proxy ; accès et coût d'exécution contemporains non authentifiés par la seule archive. |
| HistData EURUSD | Horloge EST fixe UTC−05 documentée, ticks bid/ask, usage personnel de backtest. Broker, première disponibilité, frais historiques et fills non authentifiés : un positif resterait un résultat sur proxy. |
| Dukascopy/FXCM | Restriction d'automatisation non levée / cinq probes fixes 403 déjà documentés. Aucune répétition de probes dans cet audit, aucun contournement. |
| Kalshi | Accord développeur v1.1 et Data Terms motivent F2 bloqué. Le vieux collecteur partagé marqué « terms: documented » n'est pas une résolution de ce conflit de portée. |
| Negative-risk | Timestamp du book = version d'état ; durée monotone du batch = observable d'acquisition. La réparation a rendu le screen interprétable, sans garantir atomicité serveur/exécution simultanée. |
| SEC / actions | Acceptance EDGAR utile ; recensement 2020-01-01..2026-06-30 à `08dcfc39`, sans autorité outcomes. Mapping historique et titres radiés restent le verrou aval. |
| Treasury / Hyperliquid | Respectivement données historiques BBO et nœud/labels/temps prospectif. Réduire la documentation ne fournit ni les données ni les observations. |

**Fonctionnement réel et coût d'une décision.**

- La tâche horaire `6ac978ecda1081918fba4d76dee437f4` autorisait encore le prochain test FX. Conflit signalé, **pause effectuée et `is_enabled=false` relu** vers 14:50 UTC. Aucun doublon. Son ancien prompt n'a pas été réécrit : ne pas la réactiver telle quelle. L'outil ne permet pas d'attester l'arrêt d'une session précédemment lancée.
- GitHub Actions : aucun run `in_progress`/`queued` au premier relevé ; [data-feeds 38057840440][feedrun] avait réussi ses étapes de collecte et commit. Son workflow possède deux calendriers et `cancel-in-progress:false`. Il appelle aussi H001 `forward.run` : ce n'est donc pas une simple collecte aveugle. JSON public inspecté : `SHADOW_DIRECT`, **0 engagement, 0 match avec CLV**. Aucune nouvelle observation économique exploitable n'est démontrée par ce run vert. Service préexistant laissé intact ; son statut/droits doivent être réconciliés avant une future boucle.
- `src/quant/clock.py` contient déjà heartbeat, tâches dues, leases, récupération, pause/reprise et mode d'attente. Mémoire et Book existent. Ce constat de code ne prouve pas qu'un hôte exécute le service. Activité de l'hôte cible, du nœud HL et de l'ancienne session Claude : **NON MESURÉE**. Le kit A2 à `1037999` est une note de préparation, pas une attestation d'hôte.
- F1 : réservations distantes A `8d93861` et B `2620ba0` présentes ; aucun look EURUSD dans l'inventaire initial. [Job B][f1job] : calcul 23:50:14..23:50:27, sauvegarde réussie, seul commentaire final en échec. La capture précédente avait dépassé 300 min, puis repris les archives conservées. Une mauvaise référence copiée depuis une sortie synthétique avait bloqué le contrôleur. Ce sont des mécanismes concrets de délai ; les intervalles d'attente ne sont pas assimilés à du travail humain perdu.
- Tokens, facture modèles, CPU facturé, coût humain, temps total par décision : **NON MESURÉS**. Durées de steps ≠ tokens. Aucun compteur de consommation n'est exposé ici ; aucun budget total n'a été inventé. Aucun achat n'a été effectué.

**Diagnostic hiérarchisé.** Confiance forte sur les états et défauts cités ; moyenne sur leur priorité globale, faute de comptabilité de coûts ; faible sur tout potentiel d'alpha actuel.

1. **Admissibilité et capacité économique.** Plusieurs pistes sont bloquées par une donnée non accessible, un droit, une horloge ou l'exécution. Construire davantage avant de résoudre cette dépendance peut produire un harnais sans expérience utile.
2. **Signal et puissance.** B2 est brut et net négatif ; B4 positif mais faible/concentré ; F1 négatif avec une incertitude qui laisse subsister de petits effets. Les coûts expliquent certaines pertes, pas toute l'absence de preuve. Une observation prospective rare ne s'accélère pas avec un modèle plus cher.
3. **Continuité de décision.** AGENTS renvoie à un checkpoint F11 historique alors qu'une autre surface au même SHA le dit clos. Les résultats récents vivent sur d'autres branches. B4 reprend 36 essais de STATE faute de registre accessible ; fast rail et edge search conservent des mémoires différentes. Le mécanisme de perte est la reconstruction de l'autorité, le risque de duplication et les expositions non rapprochées, pas le nombre de fichiers.
4. **Assurance à proportionner.** Les corrections d'horloge B2/negative-risk, d'intégrité F1 et d'état causal FX sont utiles. En revanche, aucune mesure ne justifie une nouvelle réception/revue complète pour chaque delta documentaire inchangé. Les reprises qui relisent des statuts contradictoires coûtent du contexte sans produire nécessairement une décision.
5. **Mesure des ressources absente.** Impossible de dire quel modèle, quelle revue ou quelle infrastructure offre le meilleur apprentissage par euro/token aujourd'hui.

Deux corrections de raisonnement sont nécessaires : Bonferroni reste valide sous dépendance, même s'il peut être conservateur ; il ne suppose pas que les expressions corrélées sont indépendantes. Une baisse prospective du seuil ne sauve pas les t de B2/B4 et ne doit jamais être appliquée après résultat. De même, « un nul sur seuls survivants réfute la population complète » exige une hypothèse de biais monotone qui n'est pas établie par le board. Les rejets figés restent conservés avec leur portée.

**2. Recherche externe : vagues, preuve et transfert**

Vague 1 : traditions de réplication factorielle, coûts d'exécution, trend, microstructure, carry, événements macro, performance réelle et concours prospectifs. Vague 2 : lectures primaires ciblées, tableaux/annexes utiles, code et versions. Vague 3 : contre-preuves, publication, coûts omis, sélection et obsolescence. Vagues 4–5 : confrontation au dépôt et consolidation des seuls neuf dossiers ci-dessous. Les sources déjà présentes dans Quant ont servi de navigation ; leurs conclusions ont été réévaluées.

La recherche s'arrête parce que cette base contradictoire suffit aux choix d'organisation proposés. Elle n'est ni une revue systématique exhaustive ni une recherche autonome hors session. Les PDF récupérés sont hashés dans EVIDENCE ; quelques sources restent limitées à leur résumé primaire, explicitement signalé. Les données de marché des études n'ont pas été acquises/recalculées.

Les niveaux sont séparés : revendication, étude empirique, réplication indépendante, observation prospective, performance réelle vérifiable. **Aucun dossier ne démontre un alpha actuel net transférable aux moyens présents de Quant.**

| Dossier | Performance et preuve | Qualité, accès, actualité ; méthode transférable |
|---|---|---|
| **E01 — Chen/Zimmermann ↔ Hou/Xue/Zhang** | [FEDS mars 2021][cz], pp.1–4/§§2–4 : 158/161 prédicteurs « clairs » reproduits à t>1,96. [HXZ mai 2017][hxz], résumé/appendice : 286/447 non significatifs avec pondération et microcaps traitées différemment. Spreads historiques, pas net réalisable. | Chercheurs indépendants mais largement mêmes données : pas deux échantillons indépendants. Qui paie dépend de chaque anomalie ; ce catalogue ne donne pas un mécanisme unique. [Code actuel][osap] Python/R, GPL‑2, entrées WRDS payantes/permissionnées ; portefeuille publié ≠ droits sur données brutes. Méthode : rapprocher formule, table, univers, coût, version avant de qualifier une réplication. Confiance forte sur cette distinction. |
| **E02 — McLean/Pontiff ↔ Jacobs/Müller** | [JF 2016][mp] : 97 prédicteurs, baisse moyenne de 26 % hors échantillon, 58 % après publication. [JFE 2020][jm] : 241 anomalies/39 pays, baisse fiable seulement aux États-Unis. Résumés primaires lus ; tables/annexes non obtenues ici. | Publication et arbitrage sont des explications observationnelles, pas une causalité identifiée ni une règle universelle de décote. Investisseurs contraints/segments difficiles peuvent rester contreparties ; prix net/capacité à établir. Bases internationales institutionnelles ; aucune preuve de fraîcheur 2026. Méthode : dater la connaissance publique et surveiller le déclin sans remettre le compteur à zéro. Confiance moyenne, conclusion méthodologique seulement. |
| **E03 — AQR/Frazzini–Israel–Moskowitz et Novy‑Marx–Velikov** | [FIM version 5 décembre 2012][fim], Tables II–V/IX : ordres institutionnels réellement exécutés, puis coûts appliqués à portefeuilles hypothétiques. [NMV août 2015, publié 2016][nmv], Tables 6–7 : bandes entrée/conservation et capacité. | Demande d'immédiateté et frictions paient parfois les fournisseurs de liquidité ; ordre exécuté ne prouve pas alpha du fonds. Accès propriétaire, impact et sélection d'exécution limitent transfert ; financement/borrow à vérifier. [Résumé actualisé 2018][fim2018] distinct de la version PDF étudiée. Méthode : coût marginal/turnover et valeur d'une meilleure mesure. B2 a déjà la variante à bande : ne pas la recréer. Confiance forte sur méthode, faible sur coût transféré. |
| **E04 — AQR trend ↔ Huang et al.** | [Hurst/Ooi/Pedersen 2017][trend], Exhibit 1 et annexes A/B : simulation 1880–2016, 67 marchés, coûts et frais 2/20 simulés. [Huang et al. 2020][huang], résumé institutionnel : faible prédictibilité propre et stratégie à moyenne historique comparable. | Sous-réaction, contraintes de couverture et exposition aux tendances sont des mécanismes possibles ; alpha résiduel non acquis. Coûts historiques incertains, certains coûts de roll exclus ; marchés communs/dépendants, risque de retournement. Données futures historiques hétérogènes, expertise rolls/marge. Méthode : comparateurs de risque/sizing avant attribution au signal. Ni preuve contre toute tendance par B4, ni justification de sa relance. Confiance forte sur distinction, critique lue au niveau résumé. |
| **E05 — Laboratoires des marchés prédictifs** | [Akey et al., 21 juin 2026][akey], §3.2/Tables 4–8 : PnL on-chain reconstruit, gains concentrés et makers davantage présents chez les gagnants. [Bürgi/Deng/Whelan janvier 2026][whelan] : favorite-longshot, frais et sélection makers/takers. [Étude arbitrage v1 août 2025][arb], p.18/appendices : ~40 M$ historiquement reconstruits. | Takers paient immédiateté/préférence loterie ; l'association maker/succès n'est pas une identification causale. Akey s'arrête au 29 mars 2026 avant nouveau régime de frais, inclut valorisations, omet gas et couvertures externes ; arbitrage sans frais historiques n'est pas net actuel. Profondeur/file/latence/capital immobilisé et accès dominent transfert. Pas de réplication indépendante d'un alpha net contemporain. Méthode : markout/CLV comme diagnostic avec rapprochement PnL, pas substitut ; ne pas rouvrir KILL/F2. Confiance forte sur limites. |
| **E06 — Carry crypto, BIS et Borri et al.** | [Borri/Liu/Tsyvinski/Wu v4, 21 mars 2026][borri], §3.6/Figure 11 : BTC août 2020–mai 2025, Sharpe 6,45 puis 4,06 depuis 2024, négatif en 2025. [BIS WP1087][bis] : demande de levier et capital d'arbitrage limité ; résumé primaire, PDF non récupéré. | Rendements stylisés, pas relevé audité de gain après tous coûts. Longs à levier paient financement ; liquidations, marge, contrepartie et crash risk rendent la prime risquée. Équipe externe distincte, mais expression BTC différente de F1 : pas réplication indépendante de Quant. Méthode : financement/risque de venue et décroissance ; aucun nouveau module carry ni nouveau look F1. Confiance forte sur portée, faible sur alpha transférable. |
| **E07 — New York Fed, adjudications Treasury** | [Fleming/Liu/Nguyen, révision juillet 2026][nyfed], Tables 2–3 et 7–9 : pression/rebond intraday 1991–2024, rôle du flux ; atténuation après 2014. Réponse de prix, pas profit net ZF. | Offre du Trésor et portage d'inventaire mobilisent la capacité des intermédiaires. Données cash institutionnelles, bid/ask/roll et base futures manquants pour Quant ; aucune réplication indépendante de cette spécification récente vérifiée. Méthode : mécanisme identifiable, contrôles horaires, sous-périodes et disponibilité ex ante. Changement Quant : réutiliser le scout gelé ; dossier conditionnel pour chiffrer données, pas nouveau backtest. Confiance moyenne sur transférabilité. |
| **E08 — Berkshire réel et décomposition AQR** | [Rapport officiel 2025, 28 février 2026][brk], pp.19–20 et K‑64 : historique de valeur de marché et états audités. [Buffett's Alpha, version 21 novembre 2013][buffett], Table 4/p.18 : Sharpe 0,76 sur 1976–2011 ; alpha devient non significatif avec BAB/QMJ. | Rendement réellement observable ≠ alpha résiduel. L'audit porte sur les comptes, pas une certification d'alpha. Valeur/qualité/faible risque, levier et financement assurance ; contraintes des autres investisseurs plutôt qu'un payeur unique. Choix factoriel ex post, capacité/financement exceptionnels non transférables. Méthode : benchmarks et financement explicites, continuité de capital. Confiance forte sur distinction ; ce cas ne valide pas un labo automatique. |
| **E09 — Consortium M6** | [Version 20 octobre 2023][m6], §2.3/Table 1, §3/§5, annexes B/C : engagements prospectifs 2022–2023 sur 100 actifs ; 38/163 équipes dépassent benchmark prévision, 47/163 portefeuille, 11 les deux. | Observation prospective réelle de prévisions, PnL de portefeuille modélisé ; coûts complets/exécution non établis. Même année et marché pour tous ; gagnants sélectionnés, dépendance et faible durée. Aucun mécanisme payeur démontré par le concours. [Code R/Python][m6code] accessible ; licence de réutilisation non identifiée. Méthode : engagements immuables, benchmarks simples et séparation prévision/décision/risque. Confiance forte ; meilleure variance/IA ne prouve pas meilleur profit. |

Le rapport praticiens antérieur (`0f9cb618`) allait trop loin en présentant la fourniture de liquidité comme seule famille avec rente actuelle vérifiée. Les sources primaires montrent des associations, des gains historiques reconstruits et des changements de frais. Elles n'établissent pas cette exclusivité ni une rente nette accessible aujourd'hui. Les cas prestigieux sans données vérifiables et les anecdotes de traders ne sont pas retenus comme preuves d'edge.

**3. Matrice de comparaison**

Priorités : P0 = nécessaire avant reprise ; P1 = utile au prochain choix ; P2 = conditionnel à une dépendance. Les tests d'utilité sont proposés pour après accord, pas exécutés ici.

| Méthode externe → preuve | Quant actuel + SHA | Écart concret / type d'action | Gain attendu sur une décision | Coût/dépendance | Test minimal d'utilité | Priorité |
|---|---|---|---|---|---|---|
| E01 : provenance formule/table/version | B2 `1e88c6b`, F1 `ea9d2d0`, plusieurs registres | **Rapprocher** les identités, ne pas ajouter un registre concurrent | Distinguer reproduction, variante et nouveau mécanisme | Faible à moyen ; ancien privé UNKNOWN | Une reprise retrouve verdict, essais/expositions et prochaine action sans lire la discussion entière | P0 |
| E02 : publication et decay | Historiques/publications dans #21 ; checkpoint `e42d4924` | **Réutiliser** mémoire, ajouter date d'exposition seulement où absente | Empêcher fausse nouveauté et sélection après résultats | Faible ; données futures éventuelles | Un résultat ancien proposé comme neuf est correctement signalé | P0 |
| E03 : coût avant optimisation | B2 bande/turnover ; Q30 `1e88c6b` | **Cibler** une mesure de coût seulement si elle change la décision | Éviter un signal détruit par exécution ; ne pas améliorer toute la plateforme | Quotes/borrow parfois payants | Établir si l'incertitude de coût peut inverser le choix ; sinon laisser Q30 en veille | P1 |
| E04/E08 : attribution | B4 `1e88c6b`, état causal FX `e42d4924` | **Compléter prospectivement** comparateurs et exposition factorielle | Séparer effet d'entrée, sizing, bêta et prime | Moyen ; référence appropriée à la famille | Le candidat serait-il encore intéressant face au même risque sans signal ? | P1 |
| E05 : exécution/markout puis PnL | KILL `2b66b193`, F2 `e7344cf`, H001 `20cc984` | **Conserver** négatifs ; **réparer** cohérence des périmètres/droits | Ne pas confondre flux collecté, CLV et gain capturable | Accès et coûts contemporains | Le panneau explique pourquoi 0 engagement n'est ni 0 edge ni collecte prouvée utile | P0 |
| E06 : financement et pertes de queue | F1 `ea9d2d0` | **Conserver**, aucune résurrection | Réutiliser leçon sans consommer une nouvelle fenêtre | Documentaire faible | Toute réserve distingue sa causalité de F1 et cite son rejet | P0 |
| E07 : contraintes explicites | Treasury `5bb78345`, Form4/13D `afd69b74` | **Dépendance externe**, pas nouvel outil | Décider si l'achat d'information serait utile avant de coder | Devis source et droits ; aucun achat autorisé | Une description du paquet minimal permet un vrai oui/non budgétaire | P2 |
| E09 : prospective et benchmark | H001 `20cc984`, clock `09ba64b8`, FX `e42d4924` | **Réutiliser** réservation/persistance ; instrumentation minimale | Réduire doubles looks et attentes présentées comme panne | Moyen ; état commun et hôte si nécessaire | Interruption/reprise/pause synthétiques préservent budget et exposition | P1 |

**4. Cinq recommandations classées**

Les coûts ci-dessous sont des estimations relatives de portée, pas des devis en tokens/heures. Aucune probabilité de succès ni ROI n'est avancé.

| Rang / problème | Action proposée après accord | Preuve et bénéfice attendu | Coût / dépendance | Critère d'abandon ou de réduction |
|---|---|---|---|---|
| **1 — État et périmètres dispersés** | Un point d'entrée vivant, relié aux registres existants par famille/expression/dataset/fenêtre. Rapprocher fast rail, F1 et edge search ; conserver UNKNOWN. Résoudre le périmètre data-feeds/H001 et les droits avant toute reprise. | R10/R13, B4 sans registre accessible ; évite reconstruction, doublons et faux holdouts. | **Faible–moyen** : index et raccordement ciblés, pas migration générale. Tokens/temps humain NON MESURÉS. Décision Owner sur le service partagé. | Si un champ ne change ni admissibilité, ni décision, ni reprise : ne pas le maintenir. Pas de nouveau board parallèle. |
| **2 — Construire avant de savoir ce qu'on peut apprendre** | Pour chaque nouveau choix, exiger mécanisme/qui paie, différenciation, source/droits/horloge, enveloppe de coûts, information pouvant changer la décision et dépendance la moins chère à lever. Maintenir au plus la famille déjà autorisée, sans quota de tests. | F2/COIN-M/HL/actions, E03/E07 ; évite harnais sans donnée et explorations non décisionnelles. | **Faible** pour qualification documentaire ; **variable** pour données, à chiffrer séparément. Aucun achat inclus. | Mettre en veille si aucune issue plausible du travail ne modifierait une décision accessible. Un défaut d'accès n'est pas un rejet économique. |
| **3 — Adapter l'inférence à la question** | Pour les futurs protocoles uniquement : effet minimum économiquement utile motivé, unité indépendante, coûts/benchmark, politique d'arrêt et distinction exploration/validation/prospective/capital. Relier les essais corrélés sans prétendre que Bonferroni les rend indépendants. | E01/E04/E09 et B4/F1 ; réduit fausses réfutations et positifs attribués au sizing. | **Moyen**, raisonnement statistique ciblé ; réutiliser calculs/réservations existants. Pas de nouveau moteur général. | Ne pas financer une confirmation incapable de distinguer l'effet utile dans les ressources disponibles. Conserver une exploration limitée ou la veille ; ne pas assouplir après résultat. |
| **4 — Continuité observable, sans seconde boucle** | Réutiliser un seul mécanisme de scheduling, le stockage existant et la pause persistante. Réveils déterministes sur donnée admise, fin de run, erreur nouvelle ou retour Owner ; modèle coûteux seulement si choix à faire. Panneau sobre dérivé de l'état. | Clock existant, récupérations F1, M6 ; évite session assimilée à worker et polling LLM inutile. | **Moyen**, raccords et contrôles synthétiques de reprise/idempotence/pause/budget ; hôte seulement si nécessaire et autorisé. | Si aucune source admissible ni travail décisionnel n'est prêt, rester PAUSED/BLOCKED ; ne pas créer de service pour afficher RUN. |
| **5 — Modèles selon valeur marginale** | Mesurer coût/contexte quand disponible ; code déterministe pour inventaires, hashes, calculs, diff et contrôles. Modèle moins coûteux pour extraction bornée. Astra pour choix du test, causalité, puissance et arbitrage. Claude sur une question distincte. | Frais actuels NON MESURÉS ; défauts F1 et horloges montrent l'intérêt d'une contradiction précise, pas d'une double lecture générale. | **Faible** pour journal minimal ; coût variable d'une revue Claude, incluant transfert/contexte. Disponibilité annoncée mardi 13 octobre. | Supprimer routage/revue qui ne détecte aucun défaut décisionnel, ne réduit pas le temps de reprise et ne justifie pas son coût marginal. |

**Conserver / simplifier / laisser en veille / arrêter.**

| Conserver | Simplifier | Laisser en veille | Arrêter dans cette mission |
|---|---|---|---|
| Rejets avec portée, données/hash et preuves déjà sauvegardées ; réservations ; horloges causales ; droits ; coûts/stress ; contrôle de capital ; pauses persistantes | Entrée de reprise, liens de versions, résumé décisionnel ; revues limitées aux changements et risques concrets | F1 clos ; F2 jusqu'aux droits ; HL jusqu'à hôte/collecte ; actions jusqu'au mapping/PIT ; ZF jusqu'aux BBO ; A2/Q30 sans question décisionnelle précise | Nouveaux tests, réglages des protocoles figés, activation de worker, second scheduler, refonte/board/dashboard construit avant retour. Aucune suppression de branches ni fusion. |

**5. Options et branche continue proposée — non construite**

**Option minimale recommandée.** Le présent dossier documentaire est immédiatement utilisable : état vérifié, rejets, preuves externes et décisions à prendre. Après discussion et accord de mise en œuvre, raccorder un point d'entrée aux mémoires/réservations existantes et afficher état, cause du blocage, preuve, coût observé et prochaine décision. Commencer par une exécution supervisée du mécanisme de reprise, avec données synthétiques pour les contrôles logiciels ; aucun test économique implicite. Surcoût estimé faible–moyen ; information supplémentaire attendue : état global fiable et coût observable d'une décision, pas alpha supplémentaire garanti.

**Option plus ambitieuse.** Ajouter ensuite scheduling déterministe, événement utile→appel de modèle, collecte prospective admissible, limites de ressources et panneau pause/reprise relié au stockage. Réutiliser la continuation existante si son environnement convient, sinon la désactiver avant remplacement. Surcoûts : raccordement des branches/états, hébergement éventuel, intégration des métriques de consommation, qualification d'une source réellement utile et temps d'observation. Tous montants/tokens restent à chiffrer ; une dépense nécessite une décision distincte. Information supplémentaire : comportement réel après interruption, qualité de collecte, exécution/coûts et dégradation observée.

Branche future possible : `research/edge-lab-continuous`, **inexistante par cette mission**. Base candidate à discuter : `e42d4924`, parce qu'elle contient les réparations récentes et la clôture F1 ; vérifier ses deltas au moment de l'accord. Alternative : base `09ba64b8` avec reprise sélective des composants qualifiés. Aucun de ces choix n'est adopté ici ; ne pas transporter toutes les anciennes autorisations/workflows par héritage.

Architecture minimale proposée : événement/horloge → lecture d'état et d'admissibilité → réservation unique → travail autorisé → preuve/limite/coût → décision/attente. Les états `PAUSED`, `BLOCKED`, `IDLE` et `RUNNING` doivent provenir du stockage et de preuves d'activité, pas d'un texte. Une pause Owner, budget épuisé/inconnu pour l'action prévue, droits manquants, résultat déjà exposé ou ambiguïté d'autorité interdit le dispatch. Budget absent ≠ budget illimité. Les réservations de F1 restent consommées ; EURUSD garde ses seuils/fenêtres/expressions.

Le dashboard non publié d'une session antérieure reste un brouillon sans statut d'architecture approuvée. Aucun site n'a été créé.

**6. Tokens, modèles et Claude**

| Organisation | Apport possible | Surcoût / mesure utile | Position proposée |
|---|---|---|---|
| Codex seul | Évite transfert et double lecture ; adapté à cet audit et aux raccords mécaniques | Risque d'angle mort ; suivi défauts découverts tard et temps de décision | Base minimale tant que Claude absent |
| Codex + contradiction ciblée Claude | Question falsifiable distincte : horloge, comptabilité de coût, unité indépendante ou cause d'un faux positif | Paquet compact : mécanisme, protocole/diff, preuves et question. Coût inclut contexte, réponse et intégration ; compter défauts qui changent une décision et temps gagné | Usage privilégié à discuter dès le 13 octobre, sans revue simulée |
| Travaux distincts répartis | Exemple : un modèle qualifie une source, l'autre traite une question statistique séparée | Dépendances, synchronisation et doublons à mesurer ; pas d'indépendance statistique par accord de deux IA | Seulement si deux questions indépendantes sont prêtes et si budget mesurable/accepté |

Le routage vers un modèle moins coûteux est une **recommandation**, pas un changement effectué dans cette session. L'environnement expose des possibilités de sous-agents avec modèles, mais aucun n'a été lancé, aucun modèle Claude callable n'a été établi et le modèle de cette conversation n'a pas été changé. Aucun abonnement/API n'est implicitement autorisé.

Contexte minimal proposé : checkpoint compact + delta + quelques preuves exactes + question. Cache des sources par URL/version/hash ; extractions déterministes ; signaler le changement plutôt que relire le dépôt. Mesures proposées : tokens entrants/sortants/cachés et coût si fournisseur les expose ; sinon `NON MESURÉ`, avec volume de contexte comme proxy explicitement distinct. Associer la session à une preuve/décision ou à un blocage résolu. Une revue s'arrête après résolution de sa question ; pas d'audit réciproque en boucle.

**7. Décisions demandées à Owner, puis arrêt**

1. Corriger ou valider ce diagnostic : priorité à l'admissibilité, aux preuves et à la continuité plutôt qu'à une refonte générale.
2. Préférer l'option minimale ou préciser l'information qui justifierait le surcoût de l'option ambitieuse.
3. Définir le périmètre futur du service data-feeds/H001 : collecte seule, évaluation explicitement autorisée, ou pause séparée. Ses droits et son articulation avec F2 doivent être clarifiés avant reprise économique.
4. Choisir le rôle de Claude et les limites de ressources acceptables. Aucun total de tokens n'ayant été donné, il reste ouvert ; on peut d'abord choisir un plafond de dépense/temps et les événements justifiant Astra.
5. Après ces retours, approuver **une version révisée précise**, sa base et les actions à mettre en œuvre. Ce rapport demande d'abord un retour, pas une autorisation implicite de construire.

Limites restantes : télémétrie d'hôtes privés, historique d'exposition privé, coût humain/modèles, droits actuels du collecteur partagé, tarifs exacts des données et réplications indépendantes contemporaines nettes. Les résumés seuls E02 et les contre-sources partielles sont signalés ; aucune affirmation d'alpha n'en dépend. Une source payante ne sera pas acquise pour combler ces limites sans accord.

La continuation de cette mission reste suspendue. Aucun horaire, contrôle automatique ou résultat de littérature ne peut débloquer la construction.

**STATUS = AWAITING_OWNER_FEEDBACK**

[pr21]: https://github.com/fahimahmedb/Quant-Trade/pull/21
[pr22]: https://github.com/fahimahmedb/Quant-Trade/pull/22
[pr26]: https://github.com/fahimahmedb/Quant-Trade/pull/26
[pr27]: https://github.com/fahimahmedb/Quant-Trade/pull/27
[pr28]: https://github.com/fahimahmedb/Quant-Trade/pull/28
[feeds]: https://github.com/fahimahmedb/Quant-Trade/tree/20cc984
[b2]: https://github.com/fahimahmedb/Quant-Trade/blob/1e88c6b/research/sector_xrev_b2/results/b2_result_2026-10-08.json
[b4]: https://github.com/fahimahmedb/Quant-Trade/blob/1e88c6b/research/time_series_macro_b4/results/b4_result_2026-10-08.json
[f1public]: https://github.com/fahimahmedb/Quant-Trade/pull/22#issuecomment-6091284118
[nr]: https://github.com/fahimahmedb/Quant-Trade/blob/2b66b193/research/edge_search/scouts/polymarket_neg_risk/results/READ_ONLY_SCREEN_RERUN_VALIDATED_2026-10-08.md
[f2terms]: https://github.com/fahimahmedb/Quant-Trade/blob/e7344cf/research/kalshi_flb_f2/TERMS_DECISION_2026-10-09.md
[hl]: https://github.com/fahimahmedb/Quant-Trade/blob/a6961e5f/research/edge_search/scouts/hl_liquidation_v1/HL_LIQUIDATION_V1_FROZEN_SPEC_2026-10-08.md
[macro]: https://github.com/fahimahmedb/Quant-Trade/blob/5bb78345/research/edge_search/scouts/MACRO_PUBLIC_DATA_SCOUT_TAUC_GFS_2026-10-08.md
[events]: https://github.com/fahimahmedb/Quant-Trade/blob/afd69b74/research/edge_search/scouts/EVENT_DRIVEN_EQUITIES_SCOUT_F413D_2026-10-08.md
[feedrun]: https://github.com/fahimahmedb/Quant-Trade/actions/runs/38057840440
[f1job]: https://github.com/fahimahmedb/Quant-Trade/actions/runs/38006324356
[cz]: https://www.federalreserve.gov/econres/feds/files/2021-037pap.pdf
[hxz]: https://www.nber.org/system/files/working_papers/w23394/w23394.pdf
[osap]: https://github.com/OpenSourceAP/CrossSection/tree/8db892442c2c3a3779b0f1eac4370d3655be15a1
[mp]: https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12365
[jm]: https://portal.fis.tum.de/en/publications/anomalies-across-the-globe-once-public-no-longer-existent/
[fim]: https://pages.stern.nyu.edu/~afrazzin/pdf/Trading%20Cost%20of%20Asset%20Pricing%20Anomalies%20-%20Frazzini%2C%20Israel%20and%20Moskowitz.pdf
[nmv]: https://mysimon.rochester.edu/novy-marx/research/ToAatTC.pdf
[fim2018]: https://www.aqr.com/insights/research/working-paper/trading-costs
[trend]: https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/AQR-JPM-Fall-2017.pdf
[huang]: https://scholars.hkbu.edu.hk/en/publications/time-series-momentum-is-it-there-2/
[akey]: https://www.carf.e.u-tokyo.ac.jp/wp/wp-content/uploads/2026/06/260714_polymarket.pdf
[whelan]: https://www.karlwhelan.com/Papers/Kalshi.pdf
[arb]: https://arxiv.org/pdf/2508.03474v1
[borri]: https://arxiv.org/pdf/2510.14435v4
[bis]: https://www.bis.org/publications/working-paper-1087-crypto-carry
[nyfed]: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf
[brk]: https://www.berkshirehathaway.com/2025ar/2025ar.pdf
[buffett]: https://pages.stern.nyu.edu/~afrazzin/pdf/Buffett%27s%20Alpha%20-%20Frazzini%2C%20Kabiller%20and%20Pedersen.pdf
[m6]: https://arxiv.org/pdf/2310.13357v1
[m6code]: https://github.com/Mcompetitions/M6-methods/tree/10c553f7a5ffbaf53971ca48ea982b2c0dd952ed

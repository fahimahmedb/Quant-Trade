# Indicateurs et combinaisons : décision de recherche

Demande Owner du 2026-10-10 : chercher en parallèle dans les travaux publics des
indicateurs et combinaisons susceptibles d'améliorer le Sharpe sans épuiser la
preuve statistique. Statut : **revue de littérature, aucun nouveau test économique**.
F1 reste REJECT ; ses résultats A/B et son harnais restent figés. La prochaine
action sélectionnée, après la qualification COIN-M décrite plus bas, est de figer
un pilote exploratoire prix + volume distinct avant toute acquisition de résultats.

## Ce que les sources permettent de retenir

Les travaux consultés ne permettent pas de désigner un indicateur presque toujours
rentable. Ils justifient quelques mécanismes à examiner, avec des résultats
contradictoires selon le marché, la période et les frais. Le Sharpe d'un article
ne constitue pas un résultat de Quant et ne permet pas de classer directement des
stratégies ayant des univers, leviers et coûts différents.

| Source primaire et périmètre lu | Résultat utile et limite | Conséquence pour Quant |
| --- | --- | --- |
| [Moskowitz, Ooi, Pedersen, 2012](https://fairmodel.econ.yale.edu/ec439/mosk.pdf), article, introduction et construction du signal | Momentum temporel sur 58 contrats diversifiés ; signal à 12 mois et pondération par volatilité passée. Ce résultat ne certifie pas des profits nets exécutables sur deux cryptos. | Retenir tendance et diversification comme mécanismes ; ne pas relancer le B4 SPY/TLT/GLD rejeté. |
| [Moreira, Muir, 2016](https://conference.nber.org/confer/2016/LTAMs16/Moreira_Muir.pdf), version de travail du 6 avril, introduction et règle | Une exposition réduite après forte variance améliore plusieurs portefeuilles de facteurs dans leur étude. La règle utilise l'inverse de la variance précédente ; elle n'est pas un simple signal directionnel ATR. | Étudier le dimensionnement comme fonction distincte ; ne pas assimiler toute gestion de volatilité à un edge. |
| [Cederburg et al., 2020](https://experts.arizona.edu/en/publications/on-the-performance-of-volatility-managed-portfolios/), **résumé institutionnel uniquement** | Sur 103 stratégies actions, pas de supériorité systématique des portefeuilles gérés par volatilité ; les combinaisons réelles hors échantillon souffrent d'instabilité. | Exiger un dimensionnement causal, borné et coûté ; aucune promesse automatique de Sharpe amélioré. |
| [Liu, Tsyvinski, 2018](https://www.nber.org/system/files/working_papers/w24877/w24877.pdf), version de travail, résumé et introduction | Momentum et attention prédisent les rendements de leur échantillon crypto. Une prédictibilité historique ne démontre pas une stratégie exécutée après frais aujourd'hui. | A priori favorable au momentum, sans reprendre des coefficients ou seuils optimisés. |
| [Hudson, Urquhart, 2019 / volume 2021](https://link.springer.com/article/10.1007/s10479-019-03357-1), article, résumé et introduction | Environ 15 000 règles ; résultats favorables dans plusieurs cryptos, mais absence de prédictibilité du Bitcoin hors échantillon. Coûts étudiés notamment par leur niveau de rentabilité nulle. | Conserver le contre-exemple ; un bon résultat historique ne suffit pas. |
| [Deprez, Frömmel, 2024](https://biblio.ugent.be/publication/01HY3C3S169G1N6QNYR55NZMFB), manuscrit accepté, §§3.3–3.4, résultats, discussion et conclusion | 75 360 règles sur Bitstamp 2012–2021 ; sélection sur l'année passée, combinaison équipondérée mensuelle, frais et demi-spread, contrôle FDR. Volume/OBV intéressant, RSI instable. Le cas central utilise les frais et spreads les plus bas ; la significativité des mesures de risque disparaît dans les cas de coûts élevés. | Donner priorité à l'information de volume et au coût d'exécution. Ne pas reproduire leur vaste grille ni leur contrôle FDR 10 % comme nouveau seuil de Quant. |
| [Bajgrowicz, Scaillet, 2012](https://scaillet.ch/pdfs/BajSca.pdf), article, résumé et introduction | 7 846 règles sur le DJIA : les règles gagnantes ne sont pas sélectionnables à l'avance de façon persistante ; de faibles frais effacent la performance. | Combiner des indicateurs ne dispense pas de sélection causale ni de coûts. |
| [Daniel, Moskowitz, 2014](https://www.nber.org/system/files/working_papers/w20439/w20439.pdf), version de travail, résumé | Le momentum transversal peut subir des pertes extrêmes lors de rebonds après panique. Ce n'est pas le même objet que le momentum temporel. | Distinguer les mécanismes ; garder pertes extrêmes, concentration et régime dans l'évaluation. |
| [Bailey, López de Prado, 2014](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf), version auteur du 31 juillet, résumé et annexe A.3 | Le Sharpe sélectionné est gonflé par les essais multiples et les rendements non normaux ; le nombre effectif d'essais dépend de leur dépendance. | Conserver tous les essais connus. Un Sharpe déflaté éventuel ne remplace pas les portes figées et n'est pas calculable honnêtement avec un historique d'essais inconnu. |

Les huit PDF ont été récupérés et hachés ; leurs originaux restent hors Git.
Le neuvième document est un résumé primaire lu par l'outil web : aucun hash des
octets originaux ni lecture intégrale n'est revendiqué. Provenance et périmètres
de lecture : `technical_signals_sources_2026-10-10.json`.

## Hypothèses retenues, sans activation

| Piste | Raison économique / rôle de chaque entrée | Décision présente et falsificateur minimal futur |
| --- | --- | --- |
| Tendance + volume signé, exposition bornée selon volatilité | Une tendance peut refléter une réaction lente ; le volume apporte une variable différente des seuls prix. Volatilité = dimensionnement, spread = coût d'entrée. OBV est une construction prix-volume, pas une preuve d'indépendance. | **Première réserve technique à qualifier**, de préférence à faible turnover. Choisir avant rendements une seule expression et un univers justifié ; comparer après frais à une exposition passive de risque fixé causalement et à la règle de prix seule. Si le volume n'apporte rien ou si les coûts absorbent le gain, abandonner cette expression. |
| Tendance + gestion de volatilité seule | Distinguer prédiction de direction et allocation de risque ; la littérature contient des résultats positifs et négatifs. | Réserve de second rang. L'ancien B4 et ses 40 expressions sur le dataset historique ne sont pas remis à zéro. Toute nouvelle étude exige une différence économique précise et des données admissibles ; pas de reprise pour assouplir le seuil ou ajouter un filtre après résultat. |
| Mouvement extrême + ventes forcées + cotations exécutables | Une vente contrainte peut produire une pression temporaire ; les liquidations apporteraient une information événementielle distincte d'un oscillateur. Le prix et la liquidité servent à vérifier si le rebond est capturable. | **Qualification COIN-M déjà prioritaire**, avant tout pilote. Sémantique de publication, échantillonnage et bid/ask encore non validés. Cette source ne remplace pas celle de l'expérience Hyperliquidation figée. |
| RSI + MACD + moyennes mobiles, sans autre information | Plusieurs transformations du même passé de prix ; leur accord ne crée pas trois observations indépendantes. Des filtres peuvent améliorer une règle, mais cela reste une hypothèse à tester. | Faible priorité face aux mécanismes précédents. Aucun balayage de combinaisons/seuils pour choisir le meilleur Sharpe historique. |

Ces pistes sont des choix de recherche, pas des règles pré-enregistrées. Aucun
paramètre, fenêtre, coût ou seuil économique nouveau n'est déclaré figé ici.
Une combinaison à poids fixes peut diversifier des erreurs si les rendements
résiduels diffèrent ; cela doit être établi après coûts. Empiler des indicateurs
corrélés ou augmenter le levier ne garantit aucune amélioration du Sharpe.

## Protéger N et la preuve

- Si N désigne les observations : davantage d'indicateurs, de trades rapprochés
  ou deux actifs corrélés ne fournit pas autant de nouvelles observations
  indépendantes. Estimer l'incertitude au niveau des jours/blocs ou des événements
  effectivement indépendants, en tenant compte des horizons qui se chevauchent.
- Si N désigne les essais : lire des articles n'exécute pas un nouveau look sur
  nos données, mais la sélection dans la littérature reste un biais possible.
  Les variantes testées chez Quant, réussies ou échouées, restent dans leur
  lignée ; le changement de branche ou de nom de famille n'efface rien.
- Travail parallèle autorisé ici : sources primaires, mécanismes, métadonnées
  et qualification des sources. **Une seule famille économique active** et
  aucune collecte concurrente avec un run existant.
- Avant toute acquisition de données de résultat : source et droits qualifiés,
  univers et manifeste publiés, une expression principale, chronologie
  décision/exécution, coûts centraux et stress, comparateurs, budget d'essais,
  critères de réussite/falsification et arrêt fixés. Un éventuel comparateur
  d'ablation ne devient pas un candidat de remplacement ; compter les tests
  décisionnels prévus dans le budget avant lecture des résultats.
- Les périodes crypto déjà examinées par F1 ne sont pas proclamées vierges.
  L'historique privé reste UNKNOWN. Une future évaluation indépendante exige
  une provenance d'exposition défendable ou une période prospective réservée
  après gel ; une réplication exploratoire reste étiquetée comme telle.
- Aucun ajustement des poids, indicateurs, fenêtres ou seuils après le résultat
  réservé. Un négatif produit une leçon et une prochaine décision, pas une
  optimisation sur ce même résultat. Aucun contrôle FDR ou Sharpe déflaté adopté
  rétroactivement pour sauver F1/B4.

## Neuf champs de cette revue

`RESULT = SOURCE_REVIEW_COMPLETED ; aucun résultat économique nouveau.`

`EFFECT_SIZE = NOT_MEASURED ; aucun Sharpe nouveau de Quant.`

`UNCERTAINTY = Transfert des études anciennes/externes à notre venue inconnu ; résultats contradictoires, sélection/publication et coûts limitent l'interprétation.`

`POWER_LIMITATION = Aucune puissance estimée sans population admissible ; indicateurs corrélés et événements chevauchants n'augmentent pas mécaniquement N.`

`ECONOMIC_SIGNIFICANCE = Prix + volume mérite une qualification ciblée ; frais, turnover et risque restent capables d'effacer le gain.`

`FAILED_CRITERIA = La proposition d'un indicateur quasi toujours rentable n'est pas établie ; nouvelle source et période indépendante non qualifiées.`

`LESSON = Chercher une information complémentaire, dissocier signal/dimensionnement/exécution, conserver les contre-exemples et toute sélection passée.`

`FAMILY_STATUS = NOT_ACTIVATED — champ descriptif de revue, pas verdict d'expérience ; F1 REJECT inchangé, F2 BLOCKED_DATA_PERMISSION, Polymarket neg-risk KILL.`

`NEXT_DECISION = Continuer la qualification COIN-M prioritaire ; garder prix + volume en première réserve technique. Si un vrai blocage rend COIN-M inutilisable, qualifier les droits, données et exposition passée de cette réserve avant une seule pré-inscription distincte. Aucun backtest de grille.`

## Décision de source après cette revue — 2026-10-10

La qualification COIN-M est terminée : **échec du critère d'horodatage causal**,
sans test économique ni famille activée. Quatre archives BTC/ETH du 25 juin 2023
ont passé leurs CHECKSUMs ; seuls les en-têtes CSV ont été interprétés, après le
[préavis borné](https://github.com/fahimahmedb/Quant-Trade/pull/22#issuecomment-6092098835).
Les liquidations ont un seul `time`, de sens non authentifié, alors que les
cotations ont `event_time` et `transaction_time`. La disponibilité publique du
signal reste inconnue. Le flux officiel est un snapshot incomplet ; un
[collaborateur Binance](https://github.com/binance/binance-public-data/issues/259#issuecomment-6020306220)
signale la fin de publication et conseille une déduplication par ligne entière.
Aucun taux de doublons, nombre de liquidations ou rendement n'a été calculé.
La preuve et les neuf champs de cette décision de source sont conservés dans
[le manifeste COIN-M](binance_cm_liquidation_source_2026-10-09.json).

La réserve prix + volume dispose de catalogues publics complets pour BTCUSDT et
ETHUSDT spot, en 1d et 1m : 110 archives mensuelles par série, août 2017 à
septembre 2026. Aucun ZIP spot n'a été téléchargé ou ouvert. Le schéma primaire
documente le volume de transactions et celui des achats takers ; les timestamps
spot passent en microsecondes le 1er janvier 2025. Les droits relus autorisent la
recherche personnelle hors production ; les résultats dérivés doivent créditer
Binance Vision et conserver CC BY-NC-SA 4.0. Le
[manifeste technique](technical_signals_sources_2026-10-10.json) conserve ces
preuves, tailles, limites et l'exposition antérieure.

La prochaine action remplace le `NEXT_DECISION` historique de la revue : figer
**un seul pilote exploratoire prix + volume**, ses coûts centraux et stress,
ses entrées retardées et son budget de comparaisons avant les résultats.
Les bougies minute sont des prix de transactions, pas des bid/ask exécutables.
Un résultat positif sur ce proxy demande une validation des cotations et du
timing avant toute conclusion sur un edge capturable. F1/B4 et les périodes
déjà examinées restent exposés ; l'historique privé UNKNOWN interdit une
prétention confirmatoire. Aucun compteur remis à zéro, aucune grille.


## Nouvelle proposition Owner : grille EUR/USD et volatilité — 2026-10-10

**DESIGN_ONLY, aucune famille activée.** Après la pause demandée à 02:02 UTC,
Owner autorise ici la recherche des briques existantes et la construction d'une
idée autour de FXStabilizer, grille/martingale et LLM/volatilité. Cela ne réactive
pas les backtests ni la continuation automatique. Cette proposition remplace la
prochaine action de conception tendance-volume/RSI ; elle ne crée aucun look.

### Briques retrouvées et portée de leur preuve

Sources Quant-Trade épinglées au commit
`8bbeb4ea51ba9bed2dc632f6b4aa27e0e32dfbbc` :

- [src/volatility.py](https://github.com/fahimahmedb/Quant-Trade/blob/8bbeb4ea51ba9bed2dc632f6b4aa27e0e32dfbbc/src/volatility.py)
  contient EWMA, GARCH normal/t, GJR t/skew-t et HAR, prévisions et pertes QLIKE/MSE.
  Blob `23794f19cdd735460c3a238a4b4b274135df26ad`,
  SHA256 `43ed515a78d242ab8d8c09c9ea5e71e9a2cba158bb46a6e16c107c6eed0ec8cf`.
- [scripts/run_etape_c.py](https://github.com/fahimahmedb/Quant-Trade/blob/8bbeb4ea51ba9bed2dc632f6b4aa27e0e32dfbbc/scripts/run_etape_c.py)
  évalue ces modèles sur NASDAQ Composite quotidien, pas sur EUR/USD.
  Blob `f8baa12728578acec80fe6a000968a79b25e0d66`.
  [Rapport antérieur](https://github.com/fahimahmedb/Quant-Trade/blob/8bbeb4ea51ba9bed2dc632f6b4aa27e0e32dfbbc/results/etape_C_volatilite.md),
  blob `19fa92311dfd2eb48117d09f0f482b87500fe49e`, consulté sans recalcul.
  Ce rapport parle de prévision de variance, pas de profit de trading. Ses
  déclarations d'adoption GJR-t ne sont pas une validation indépendante nouvelle.
- [src/quant/desk/risk.py](https://github.com/fahimahmedb/Quant-Trade/blob/8bbeb4ea51ba9bed2dc632f6b4aa27e0e32dfbbc/src/quant/desk/risk.py),
  blob `6a4b545edef648a5d0e207d96aa97aa9cf782cae`, apporte des plafonds
  d'exposition, réduction et arrêt sur drawdown. Les valeurs par défaut concernent
  un portefeuille avec contrainte de neutralité ; elles ne sont pas transférées
  automatiquement à un panier FX directionnel.

**Défaut statique avant réutilisation :** dans la boucle walk-forward,
`garch_path(r, p)` reçoit la série complète et initialise la variance avec
`eps.var()` sur cette série. `ewma_path(r - mu_tr)` recentre de nouveau avec
la moyenne de toute la série et utilise sa variance pour la graine. Des données
futures entrent donc dans ces initialisations ; leur effet numérique n'a pas été
mesuré. Le texte final du script contient aussi des statistiques rédigées en dur.
Avant un nouveau pilote : état initial/période d'estimation strictement passée,
mise à jour causale, rapport dérivé des résultats réels, conventions FX/horizon
propres. Aucun ancien résultat n'est corrigé, recalculé ou remplacé ici.

Le second dépôt accessible,
[fahimahmedb/TradingAgents](https://github.com/fahimahmedb/TradingAgents/tree/be952b8eccb49720509af544c6675233bc1f10d0),
est un fork de TauricResearch à `be952b8eccb49720509af544c6675233bc1f10d0`.
Son [analyste technique](https://github.com/fahimahmedb/TradingAgents/blob/be952b8eccb49720509af544c6675233bc1f10d0/tradingagents/agents/analysts/market_analyst.py)
sélectionne des indicateurs RSI/MACD/ATR/Bollinger ;
son [portfolio manager](https://github.com/fahimahmedb/TradingAgents/blob/be952b8eccb49720509af544c6675233bc1f10d0/tradingagents/agents/managers/portfolio_manager.py)
synthétise un débat LLM. Ce code ne constitue pas une preuve de rentabilité ni
une grille EUR/USD opérationnelle retrouvée. Inventaire limité aux deux dépôts
accessibles, références/fichiers examinés ; l'absence de code de grille n'est pas
certifiée sur chaque branche.

### Une seule hypothèse candidate : EURUSD-RANGE-GRID-001

**Hypothèse :** un excès temporaire suivi d'une réintégration, dans un régime de
faible tendance défini avec le passé, permet un retour vers la moyenne après frais.
Une grille finie répartit l'entrée dans cette zone ; la volatilité ajuste
l'espacement et le budget. La martingale seule n'est pas la source présumée du gain.

Architecture de conception, **paramètres pas encore pré-enregistrés** :

1. Entrée symétrique long/short : RSI sortant d'un extrême, filtre de force de
   tendance calculé sur bougies closes. Les définitions/lissages et horloges
   doivent être uniques ; pas de choix rétroactif du régime ni de pivots futurs.
2. Panier fini, trois niveaux envisagés. Des renforts croissants restent possibles
   dans une enveloppe totale fixée avant la première entrée ; aucune obligation
   de doubler pour récupérer une perte et aucun transfert de perte au panier suivant.
3. Espacement exprimé en volatilité prévue à l'horizon FX pertinent. Ancrage,
   objectifs et limite de perte ne sont pas repoussés pour sauver le panier.
   Une hausse de risque peut réduire l'enveloppe restante, jamais l'agrandir
   simplement parce que les positions perdent.
4. Stop de panier, durée maximale, limite de marge et veto en cas de spread
   excessif/données périmées/invalidation du régime. Gaps et slippage peuvent
   dépasser une perte planifiée : aucun stop ne garantit un plafond absolu.
5. LLM pour formuler, auditer et expliquer l'hypothèse ; la première règle testée
   reste déterministe. Une décision LLM historique introduirait notamment mémoire
   des marchés dans l'entraînement, versions/prompts et répétitions de tirages :
   elle exige son propre protocole et ne doit pas choisir les gagnants après résultat.

Pour « laisser courir la hausse », une composante de suivi de tendance pourrait
être une réserve ultérieure. Elle n'est pas intégrée au premier candidat : une
grille visant le retour au centre ne capte pas automatiquement une tendance.
Réduire l'exposition peut aussi réduire les gains ; amélioration des deux côtés
à établir, pas à supposer. En FX, volatilité et signe du rendement sont distincts ;
l'asymétrie négative d'un indice actions ne se transpose pas sans preuve.

### Falsificateur minimal futur

Trois expressions économiques prévues au maximum, à compter **avant** toute
acquisition/calcul, une seule candidate : grille bornée avec contrôle volatilité ;
même entrée sans renfort avec contrôle volatilité ; même grille avec budget/
espacement constant. Comparateurs diagnostiques, jamais remplaçants choisis au
meilleur Sharpe. Plafonds de risque comparables fixés ex ante ; coûts de chaque
expression inclus. Si l'entrée seule explique tout, la grille est inutile ; si
le contrôle ne fait que réduire l'exposition, ne pas revendiquer une nouvelle alpha.

Source préalable : EUR/USD bid/ask horodatés avec résolution permettant d'ordonner
renforts/stops/sorties, droits admissibles et financement/swaps/frais documentés.
Aucune source FX ainsi qualifiée ici ; pas d'achat ni compte. De simples bougies
H1 ne résolvent pas plusieurs niveaux touchés dans une même bougie. Coûts,
latence, horizons, paramètres, réservations et règles d'arrêt doivent être
publiés et figés avant le premier look.

Mesurer P&L net mark-to-market, Sharpe, drawdown, pertes extrêmes, marge, durée des
paniers, nombre de paniers indépendants et différence avec les comparateurs.
Les ordres d'un panier ne sont pas des essais indépendants. Rejeter si seuls les
gains clôturés sont positifs, si les frais/stress effacent le gain, ou si le gain
vient d'une plus grande exposition/une perte terminale cachée. Les seuils
numériques restent à fixer avant résultats ; aucun budget historique remis à zéro.

Exposition supplémentaire connue : le backtest **public du vendeur** EUR Turbo
v1.2 2013–2016 et ses premières séquences d'ordres ont été lus pour répondre à
Owner. [Source ZIP](https://fxstabilizer.com/content/files/FXStabilizer_Turbo_EURUSD_2013.zip),
201811 octets, SHA256
`b2710dcc43bb0f682d017ab157bdc2c1dddff8633c77ef54b84620272f200ebf`.
Ce sont ses résultats publiés, pas un calcul Quant ; pas de code source récupéré
ni de reproduction. Ne pas présenter ces années comme une période vierge après
cette exposition. NASDAQ/F1/B4 et historique privé UNKNOWN restent dans la lignée.

### Neuf champs de la proposition

- RESULT = DESIGN_PROPOSAL_RECORDED ; aucun résultat économique nouveau.
- EFFECT_SIZE = NOT_MEASURED.
- UNCERTAINTY = Retour à la moyenne net et transfert du moteur au FX non établis.
- POWER_LIMITATION = Population/source non qualifiées ; paniers et jours corrélés.
- ECONOMIC_SIGNIFICANCE = Séparer profit du signal, gestion du risque et renforts.
- FAILED_CRITERIA = Chronologie de l'ancien moteur à réparer ; source FX/coûts/
  protocole/réservations non figés ; aucune revendication confirmatoire.
- LESSON = Le sizing peut modifier les pertes et gains sans créer une espérance
  positive ; juger l'equity et l'apport marginal des renforts.
- FAMILY_STATUS = NOT_ACTIVATED ; conception limitée autorisée, essais en pause.
- NEXT_DECISION = Discuter cette hypothèse et notre méthode de sélection ; si le
  travail expérimental reprend, commencer par source/droits/chronologie, puis
  une pré-inscription distincte. L'automation reste désactivée.

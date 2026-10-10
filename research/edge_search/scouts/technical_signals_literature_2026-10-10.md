# Indicateurs et combinaisons : décision de recherche

Demande Owner du 2026-10-10 : chercher en parallèle dans les travaux publics des
indicateurs et combinaisons susceptibles d'améliorer le Sharpe sans épuiser la
preuve statistique. Statut : **revue de littérature, aucun nouveau test économique**.
F1 reste REJECT ; ses résultats A/B et son harnais restent figés. La prochaine
action économique reste la qualification des données de liquidations COIN-M.

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

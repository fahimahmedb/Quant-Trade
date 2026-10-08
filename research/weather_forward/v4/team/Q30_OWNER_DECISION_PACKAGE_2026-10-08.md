# Q30 — paquet de décision Owner sur une donnée publique hors panel

Date : 2026-10-08. Statut : `OWNER_DECISION_PACKAGE_NO_EFFECT`.

## 1. Objet et portée

B2 a confirmé reproductiblement le rejet déjà consigné de la famille de relatif transversal sectoriel. B4 a rejeté `MACRO-TSMOM-001` : `t = 0,488` contre `3,227`, deux moitiés de signes opposés et 2024 représentant 92,9 % du P&L annuel positif. Ces résultats ne prouvent pas que toute recherche publique est épuisée et n'autorisent aucune acquisition.

Q30 demande seulement si Owner autorise une acquisition unique, étroitement nommée, d'une donnée publique réelle hors du panel actuel. Toute autorisation générique par « classe de sources » est déconseillée. L'acquisition, le choix d'un endpoint, les instruments et la licence restent dans la réserve d'Owner.

```text
DATA_DOWNLOADED = FALSE
OWNER_DECISION_EXPRESSED_BY_THIS_PACKAGE = FALSE
ACQUISITION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```

## 2. Contre-lecture de B4

Le rejet est solide : trois des sept critères conjonctifs sont faux et la statistique t est très éloignée du seuil. La convention de première ligne de `L = 252` ne peut changer cette conclusion : son effet maximal annoncé est de l'ordre d'un coût d'entrée de 5 pb, sans rapport avec l'écart à `3,227`, le signe opposé des moitiés ou la concentration annuelle.

Les coûts ne sont pas la cause immédiate du rejet : le rendement central reste positif après 1,63 % de coûts de transaction et 1,06 % de borrow, et le stress 10/300 pb reste positif. Cela ne valide pas le modèle de coûts, qui demeure simplifié et non exécutable comme estimation réaliste.

L'exposition moyenne **signée** de `0,07` ne démontre ni une faible exposition brute, ni une forte part de cash : des longs et shorts peuvent se compenser. Le résultat ne mesure ni l'exposition brute moyenne ni la proportion des séances en cash. Aucune conclusion « surtout cash/neutre » n'est retenue.

## 3. Puissance et compteur d'essais

Au seuil poolé `t >= 3,227`, un edge de Sharpe annuel `S` demande approximativement `(3,227 / S)^2` années : environ 42 ans pour `S = 0,5`, 10 ans pour `S = 1,0`; sur 11 ans, il faut environ `S >= 0,97`, et sur trois ans `S >= 1,86`.

Une nouvelle donnée publique peut donc surtout **fermer des hypothèses**, pas promettre une preuve d'edge à ce seuil. Les a priori subjectifs par classe ne sont pas présentés comme probabilités. Abaisser le seuil après observation serait du gate-shopping. Toute règle statistique différente — par exemple une accumulation séquentielle sur le flux forward — doit être pré-enregistrée avant lecture.

Le compteur doit rester poolé à au moins `40 + nouvelles expressions`. Changer de dataset ne remet jamais la pénalité à zéro.

## 4. Voies ordonnées

1. **Sans acquisition — décomposition overnight/intraday.** Mécanisme : déterminer si les rejets ou rendements historiques proviennent des gaps overnight ou de l'intraday, avec le panel déjà présent. Valeur d'un négatif : éliminer une illusion de timing et améliorer l'attribution. Limite : fenêtre déjà dépensée, donc diagnostic seulement.
2. **Sans acquisition — modèle de coûts.** Mécanisme : remplacer l'enveloppe simple par une estimation documentée des coûts de jambe courte, financement, spread et turnover. Valeur d'un négatif : fermer des faux positifs d'implémentation et améliorer `VET -> SIZE -> RISK -> FILLS`. Aucun edge nouveau n'est revendiqué.
3. **Acquisition éventuelle OHLCV nommée.** Instruments proposés : ETF liquides causalement distincts du seul relatif sectoriel, précisément nommés par Owner. Donnée exigée : OHLCV quotidien point-in-time autant que possible, provenance, licence, horodatage, empreinte et bloc final scellé. Mécanisme candidat et nombre d'expressions seront pré-enregistrés après autorisation, avant lecture.
4. **Acquisition éventuelle de séries de signal nommées.** Exemples à décider explicitement par Owner : taux Treasury/FRED nommés ou indice de volatilité nommé. Ces séries ne sont pas négociables et exigent un schéma distinct ; il est interdit de fabriquer des OHLC. Leur valeur est de tester un mécanisme macro causalement différent. Un négatif ferme la famille et n'entraîne aucune variante opportuniste.

L'ordre recommandé est 1 puis 2. Les voies 3 ou 4 ne sont proposées que si Owner juge que leur valeur de fermeture justifie le coût, la licence et la frontière de donnée réelle.

## 5. Garde-fous d'une autorisation éventuelle

Toute autorisation doit nommer cumulativement :

- la source ou l'endpoint exact ;
- les instruments ou séries exacts ;
- une acquisition unique ;
- la date de coupe et le bloc final à sceller avant lecture ;
- le chemin de sortie, le format, la provenance et les empreintes attendues ;
- la licence ou les conditions d'usage à vérifier ;
- le compteur poolé, au minimum `40 + n` ;
- l'interdiction de lire la réserve calendaire du desk à partir du 2025-03-12 ;
- l'interdiction de présenter comme vierge une période déjà connue de l'équipe ;
- l'absence de téléchargement complémentaire, substitution, backfill silencieux ou choix post-observation.

Une confirmation honnête exige soit un bloc final réellement scellé et haché avant lecture, soit des barres strictement postérieures à l'acquisition. Une nouvelle série corrélée à SPY ne rouvre pas la réserve calendaire du desk.

## 6. Coût et limites d'ingénierie

Une source OHLCV compatible demande approximativement un adaptateur de 40–70 lignes, environ 35 lignes d'intégration, 100–150 lignes de tests, des sidecars de provenance et la paramétrisation du système pour un second dataset. Une série non OHLC demande en plus une extension du panel estimée à 100–200 lignes et la séparation entre signal non négociable et actif tradé.

« Public » ne signifie ni licence claire ni disponibilité stable. Le précédent Yahoo est un endpoint non documenté et ne vaut pas autorisation permanente.

## 7. Décision étroite demandée à Owner

Choisir une seule réponse :

- `Q30_DEFER_ACQUISITION` — recommandation actuelle : poursuivre d'abord les voies 1 et 2 sans donnée nouvelle ;
- `Q30_AUTHORIZE_ONE_NAMED_OHLCV_ACQUISITION` — en complétant endpoint, instruments et coupe exacts ;
- `Q30_AUTHORIZE_ONE_NAMED_SIGNAL_SERIES_ACQUISITION` — en complétant source, séries, coupe et usage exacts ;
- `Q30_REFUSE_ACQUISITION` — sans conclure que toute exploration est épuisée.

Un refus ou un report ne termine pas Quant : l'amélioration du modèle de coûts, la décomposition overnight/intraday et l'accumulation forward restent des actions distinctes. Une autorisation ne vaut ni validation d'edge, ni intégration au Book, ni capital réel.

`NEXT_ACTION`: Owner — choisir une réponse et, en cas d'autorisation, nommer chaque élément requis ; sinon le Clock route vers les voies sans acquisition.

`CHALLENGE`: vérifier que la décision ne réinitialise pas le compteur, ne rouvre pas la réserve du desk et ne délègue pas silencieusement le choix d'une source.

`WAKE_EVENT`: décision explicite d'Owner sur Q30 ou nouvelle preuve économique modifiant l'ordre des voies.

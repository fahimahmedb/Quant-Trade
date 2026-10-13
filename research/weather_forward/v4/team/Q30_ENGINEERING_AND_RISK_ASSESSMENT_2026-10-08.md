# Q30 — évaluation d'ingénierie et de risque (Builder, 2026-10-08)

Statut : `BUILDER_INPUT_FOR_ORCHESTRATOR_PACKAGE`, aucune décision d'Owner, aucune donnée téléchargée, aucun fichier de recherche exécuté. Sources : trois lectures indépendantes en lecture seule (ingénierie, risque point-in-time, gouvernance) puis une revue adverse à contexte neuf. Chaque fait sur le dépôt est lu dans le code ; tout fait sur une source externe est `UNVERIFIED_FROM_MEMORY`.

## 1. Ingénierie (faits du dépôt)

- Deux adaptateurs de barres seulement : `fetch_yahoo_daily` (réseau) et `load_local_tsv` (`src/quant/dataplane/adapters.py`). Les deux lèvent `DataUnavailable` plutôt que d'inventer une barre.
- Le schéma est figé sur OHLCV (`PricePanel.FIELDS`) : prix strictement positifs, `low <= open/close <= high`, au moins 250 barres par symbole (`validation.py`). Une série non OHLC (VIX, rendements, spreads, tout ce qui peut être nul ou négatif) exige une extension du panel (environ 100 à 200 lignes plus tests) et une notion de « série-signal non négociable » qui n'existe pas. Fabriquer open/high/low violerait « jamais de donnée de marché fabriquée ».
- Aucun test n'existe pour les adaptateurs ni pour l'ingestion : tout nouvel adaptateur serait le premier testé.
- Ajouter une source OHLCV déjà couverte par le schéma : un adaptateur (40 à 70 lignes), un wrapper d'ingestion et son entrée dans `ingest_all` (environ 35 lignes), un `.csv` et un `.meta.json` versionnés, des tests (100 à 150 lignes) et STATE.md.
- Un second jeu de données ne serait pas étudié par le système tel quel : `QuantSystem` est construit avec un seul `dataset_id` et un seul univers, les lanes codent le benchmark SPY en dur (environ 30 à 80 lignes à paramétrer).
- Fenêtres : la partition de recherche est gelée par `dataset_id` et se calcule en fractions 55/30/15 des dates du nouveau fichier. Rien ne garantit une fenêtre vierge par construction, et **les compteurs d'essais ne sont pas mis en commun entre jeux de données** (clé `dataset@cohorte`) : un nouveau jeu repart à zéro. C'est un degré de liberté dangereux, voir §3.
- Reproductibilité : la ré-ingestion d'un même `dataset_id` avec un historique modifié bloque la recherche (contrôle de cohorte) au lieu de rejouer en silence.

## 2. Les chances, dites honnêtement

- Puissance. Avec le seuil poolé de B4 (t >= 3,227 pour 40 essais), un edge journalier de Sharpe annuel S n'est confirmable qu'après `(3,227 / S)²` années : S = 0,5 donne environ 42 ans, S = 1,0 environ 10 ans. Sur 11 ans de données il faudrait S >= 0,97 ; sur un bloc de 3 ans, S >= 1,86. Un Sharpe de 0,3 à 0,6, plausible pour un seul actif journalier après coûts, ne franchit donc aucune fenêtre disponible.
- Conséquence : l'acquisition de données publiques ne peut raisonnablement pas **prouver** un edge à ce seuil ; sa valeur est de **fermer** l'espace des familles publiques journalières. Les a priori de réussite par classe (2 à 8 %) de l'étude de risque sont des jugements subjectifs, non calibrés, non utilisables comme probabilités auprès d'Owner ; l'ordre de grandeur honnête est « faible, non quantifié ».
- Abaisser le seuil après avoir vu qu'il est inatteignable serait du gate-shopping. Toute modification du seuil exige une règle écrite avant observation (par exemple une accumulation séquentielle sur le flux forward du desk, qui est précisément le rôle prévu de la fenêtre shadow).

## 3. Garde-fous à imposer dans toute décision

1. Compteur d'essais **poolé** : au moins 40 + les nouvelles expressions, pas de remise à zéro par jeu de données.
2. La réserve du desk (à partir du 2025-03-12) est **calendaire**, pas par jeu de données : un nouveau jeu corrélé au SPY ne peut pas ouvrir cette tranche, même « une seule fois en veto ».
3. « Fenêtre vierge » : n'est vierge que pour le nouveau jeu, pas pour l'équipe, qui a vu 2022-2025 à travers le panel dépensé ; elle ne l'est pas non plus face à la littérature. Une confirmation honnête n'existe que sur un bloc final scellé et haché avant lecture, ou sur des barres strictement postérieures à l'acquisition.
4. L'historique antérieur à 2016 de nouveaux symboles est le seul bloc jamais lu par le projet, mais son régime diffère (post-crise, ETF moins liquides) : preuve faible dans les deux sens.
5. Licence et disponibilité : le précédent (Yahoo) est un point d'accès non documenté, `license_note` « public endpoint, personal research use ». « Public » ne garantit pas que les conditions autorisent l'accès automatisé et la recherche.

## 4. Gouvernance (lecture)

- L'élément 3 de la réserve (« donnée réelle ») n'est pas défini ; la lecture prudente, que l'équipe applique déjà, couvre aussi les séries publiques sans identifiant.
- Le précédent d'ingestion du panel actuel est un jalon ponctuel de la mission de construction du 2026-09-13, antérieur à la réserve : précédent faible, pas une autorisation permanente.
- La charte demande qu'Owner **nomme** chaque élément levé (« une formule générale ne suffit pas »). Une décision « classe de sources » déléguerait au Builder le choix des sources. Recommandation : décision étroite, instruments nommés, acquisition unique.
- « Exploration d'edge épuisée » est faux en l'état : l'alternative de B4 (amélioration du modèle de coûts) n'a pas été traitée, et un refus d'Owner sur un élément ne supprime pas les autres travaux (CLAUDE.md : un résultat négatif n'est pas une condition d'arrêt).

## 5. Points d'accord et de désaccord à trancher par l'orchestrateur

- Accord proposé : présenter Q30 à Owner sous forme étroite (liste d'instruments nommés, acquisition unique, un bloc final scellé, compteur poolé, aucune lecture de la tranche du desk).
- À trancher : valeur de l'acquisition au regard de §2 (fermeture de l'espace plutôt que preuve) et de son coût d'ingénierie (§1) ; alternative sans acquisition (modèle de coûts, accumulation forward du desk).

```text
DATA_DOWNLOADED = FALSE
OWNER_RESERVE_RAISED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```

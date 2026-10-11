# Quant Edge Lab V4 — Discovery First

## 0. Décision de conception

Le labo n'a plus pour mission primaire de **prouver proprement un edge**. Sa mission primaire est désormais de **produire de l'information économique discriminante le plus vite possible**, puis de réserver la rigueur lourde aux rares mécanismes qui survivent.

Le système V3 reste utile, mais il change de rôle : il devient la **voie de validation**. V4 ajoute devant lui une **voie de discovery rapide**.

> Chercher largement → falsifier vite → promouvoir rarement → valider sévèrement.

Cette doctrine vise explicitement le défaut observé du projet : trop de travail de gouvernance, d'accès, d'horloge, de receipts, de ressources et d'architecture avant d'avoir établi qu'un mécanisme mérite ce coût.

## 1. Les trois seuls garde-fous durs en Discovery

1. **Aucun capital réel / aucun trading live.**
2. **Aucune falsification consciente de l'historique scientifique** : pas de résultat regardé puis présenté comme vierge, pas de retry/retune caché du même test après exposition.
3. **Aucun proxy exploratoire ne peut être appelé edge validé.**

Tout le reste est gradué selon le stade de recherche.

Les exigences PIT parfaites, BBO complet, droits de redistribution, roll exact, marge, frais historiques complets, survivorship-safe parfait, hôte durable, provenance exhaustive ou chaîne de publication complète sont des exigences de **promotion/validation**, pas automatiquement des préconditions à toute exploration.

## 2. Le principe qui change tout : un test imparfait peut être utile

La question Discovery n'est pas :

> « Peut-on déjà prouver que cette stratégie est exécutable ? »

mais :

> « Avec le test le moins cher qui conserve le mécanisme économique, peut-on apprendre quelque chose qui change rationnellement la décision de continuer ? »

Un proxy est autorisé s'il est explicitement nommé et si son biais est compris.

Exemples admissibles en Discovery :

- close/EOD au lieu de BBO pour mesurer un effet grossier ;
- continuous future imparfait pour tuer une hypothèse dont l'effet devrait être massif ;
- données secondaires ou séries publiques pour une première réplication ;
- survivorship imparfait si le biais est décrit et que le test sert uniquement de filtre négatif ;
- coûts approximatifs fixes, de préférence défavorables au mécanisme ;
- petit échantillon pour détecter un effet gigantesque ou une incohérence évidente ;
- prospective short-window lorsqu'un historique propre est inaccessible ;
- données d'un papier public pour décider s'il faut reconstruire le dataset.

Un test de Discovery ne peut **promouvoir** que vers davantage de travail. Il ne peut jamais autoriser capital/live.

## 3. Une hiérarchie de preuves au lieu d'un gate unique

### L0 — plausibilité causale

Mécanisme, payeur économique, raison de persistance, direction attendue. Aucun backtest nécessaire.

### L1 — falsification grossière

Données faciles/proxy. Une expression, une fenêtre ou un échantillon raisonnable, coûts simples. Objectif : tuer vite.

### L2 — réplication exploitable

Données plus propres, timestamp raisonnable, coûts plus réalistes, biais principaux corrigés. Objectif : vérifier que l'anomalie ne disparaît pas dès que le test devient sérieux.

### L3 — validation scientifique

PIT/survivorship-safe, chaîne de données causale, multiplicité, protocole gelé, coûts/exécution cohérents, confirmation indépendante. Ici le moteur V3 devient utile.

### L4 — capturabilité

Quotes/fills réellement exécutables, droits, latence, marge, capacité, broker/venue, contraintes de production. Toujours sans live tant que non autorisé.

**Règle :** on ne paie pas L3/L4 pour une hypothèse qui n'a pas survécu à L1/L2, sauf si L1 est techniquement impossible mais que la valeur d'information attendue justifie directement L2.

## 4. Fin de WAIT comme état de travail principal

En Discovery, une idée doit finir rapidement dans l'un de ces états :

- `TEST_NOW` — un test discriminant bon marché existe ;
- `KILL` — le mécanisme/expression ne mérite plus de recherche ;
- `PROMOTE` — suffisamment intéressant pour un test plus propre ;
- `PROMOTE_HIGH` — résultat anormalement fort, priorité validation ;
- `PARK` — peut être intéressante, mais son coût/blocage est actuellement supérieur à sa valeur d'information.

`PARK` n'est **pas** une file d'attente bloquante. Le worker passe immédiatement à la piste suivante.

Deux cycles consécutifs sans information économique nouvelle sur la même piste ⇒ `PARK` obligatoire, sauf justification explicite qu'une seule action courte débloque un test déjà défini.

## 5. Architecture tax

Le projet doit traiter l'architecture comme un coût, pas comme un produit.

### Exigence

Sur une fenêtre glissante raisonnable :

- **≥ 90 %** de l'effort du worker doit être relié directement à une hypothèse économique, un dataset discriminant, une exécution de test ou l'interprétation d'un résultat ;
- **≤ 10 %** peut être consacré à infrastructure/gouvernance/visualisation/refactoring.

Une tâche d'architecture n'est admissible que si elle :

1. débloque au moins **deux expériences économiques distinctes**, ou
2. corrige un défaut qui peut corrompre des résultats, ou
3. prend moins d'un cycle court et rétablit immédiatement le flux de Discovery.

Sinon : `PARK_ARCHITECTURE`.

## 6. KPI principal : information produite, pas conformité produite

Le KPI primaire devient :

> **nombre d'hypothèses économiques ayant reçu une tentative réelle de falsification discriminante par unité de temps.**

Cibles initiales :

- 10 tests discriminants / semaine ;
- 2 à 4 familles causalement distinctes travaillées / semaine ;
- médiane ≤ 90 min entre sélection et verdict Discovery ;
- ≥ 60 % des idées doivent être tuées ou parkées rapidement ;
- au maximum 2 cycles consécutifs sur une même piste sans nouveau signal économique ;
- chaque semaine doit produire au moins une carte `PROMOTE` ou démontrer proprement pourquoi aucune n'a survécu.

Un mois avec 40 tests et 39 morts est meilleur qu'un mois avec 2 tests et 200 commits d'infrastructure.

## 7. Recherche d'idées : aller plus loin que la simple liste d'hypothèses

### 7.1 Recherche par payeur structurel

Pour chaque mécanisme : **qui paie ?**

- hedgers ;
- liquidateurs / traders contraints ;
- market makers sous contrainte d'inventaire ;
- indexers/rebalancers ;
- fonds soumis à calendrier/réglementation ;
- émetteurs ;
- utilisateurs payant de l'immédiateté ;
- subventions explicites ;
- participants avec contrainte de taille/mandat ;
- flux administratifs / fiscaux / calendaires.

Une hypothèse sans payeur identifiable reçoit une priorité plus faible.

### 7.2 Recherche par friction

Chercher les endroits où l'arbitrage est empêché par :

- faible capacité absolue ;
- horaires ;
- fragmentation ;
- complexité opérationnelle ;
- capital immobilisé ;
- contraintes de mandat ;
- coûts fixes ;
- faible intérêt institutionnel ;
- données pénibles mais publiques ;
- asymétrie de vitesse non-HFT ;
- conventions de marché ;
- comportement mécanique/réglementaire.

### 7.3 Recherche par « edge trop petit pour eux, assez grand pour nous »

La capacité institutionnelle n'est plus un défaut automatique. Une opportunité de faible capacité peut être prioritaire si elle est répétable et nette pour petit capital.

### 7.4 Recherche de réplications avant invention

Avant de créer une idée originale, chercher :

- effets académiques récents peu coûteux à répliquer ;
- anomalies publiques ayant possiblement survécu ;
- stratégies de venues/exchanges documentées ;
- mécanismes montrés dans des marchés voisins ;
- règles réglementaires/calendaires récemment modifiées ;
- primes de risque dont la capturabilité pour petit participant n'a pas été testée.

Répliquer proprement une anomalie existante peut avoir plus de valeur d'information que concevoir une 51e idée originale.

### 7.5 Recherche de « négatifs utiles »

Un test peut viser à démontrer que même sous hypothèses favorables le mécanisme est trop faible. Utiliser une **borne supérieure généreuse** est encouragé : si même elle ne paie pas, tuer immédiatement.

## 8. Allocation de portefeuille de recherche

Le worker ne doit pas optimiser son attention sur la piste qui paraît la plus prometteuse après avoir vu des résultats. Il doit diversifier les mécanismes.

Allocation cible :

- 30 % microstructure/flux forcés ;
- 20 % event-driven/corporate ;
- 20 % macro/calendrier/policy ;
- 15 % risk premia/hedging ;
- 15 % petites rentes/subventions/fragmentations.

Ce sont des quotas de **recherche**, pas de capital.

Si une catégorie n'a pas de candidat testable, son budget retourne au pool général plutôt que de créer de l'infrastructure pour la forcer.

## 9. Anti-biais spécifique aux IA

Les IA savent énormément de choses historiques et peuvent contaminer une expérience sans le vouloir. V4 impose donc :

- écrire le mécanisme et le test avant de calculer le résultat ;
- distinguer explicitement `KNOWN_FROM_LITERATURE` de `DISCOVERED_HERE` ;
- ne jamais transformer la mémoire d'un événement célèbre en timestamp prétendument point-in-time ;
- ne pas choisir après coup l'actif, horizon ou sous-échantillon gagnant ;
- lorsque plusieurs expressions sont raisonnables, soit en choisir une avant lecture, soit compter toutes comme exploration ;
- préférer les tests prospectifs courts quand le risque de mémoire historique est élevé.

## 10. Le format d'une expérience Discovery

Une expérience doit tenir sur une fiche courte :

```text
ID =
MECHANISM =
WHO_PAYS =
WHY_PERSIST =
LEVEL = L1 | L2
QUESTION =
CHEAPEST_VALID_PROXY =
KNOWN_BIASES =
FIXED_RULE =
COST_ASSUMPTION =
MAX_TIME_MIN =
KILL_IF =
PROMOTE_IF =
RESULT =
DECISION = KILL | PROMOTE | PROMOTE_HIGH | PARK
NEXT =
```

Pas de framework général exigé. Pas de dossier de 20 fichiers pour un test de 45 minutes.

## 11. Critères de promotion

`PROMOTE` n'exige pas un t-stat final. Il exige qu'au moins une de ces conditions soit vraie :

- effet économiquement gros par rapport au bruit/coûts approximatifs ;
- résultat cohérent avec le mécanisme sur plusieurs sous-périodes naturelles sans optimisation ;
- réplication d'un effet public avec une taille proche de la littérature ;
- résultat prospectif compatible avec l'hypothèse ;
- asymétrie/borne économique suffisamment forte pour justifier l'achat de précision.

`PROMOTE_HIGH` exige en plus que l'effet survivrait vraisemblablement à une correction substantielle des coûts/biais.

Une promotion crée ensuite un contrat V3/L3 séparé. Les défauts du proxy ne sont jamais effacés.

## 12. Critères de KILL

KILL rapide encouragé si :

- signe opposé au mécanisme sur un test raisonnable ;
- effet proche de zéro avant même coûts réalistes ;
- dépend d'un sous-échantillon/paramètre choisi après résultat ;
- borne supérieure favorable reste non rentable ;
- payeur structurel absent ;
- mécanisme est matériellement un doublon d'une famille déjà rejetée ;
- réplication publique échoue sans explication de données crédible.

## 13. Critères de PARK

PARK si :

- données accessibles seulement contre coût/compte/permission et aucune preuve d'effet n'existe encore ;
- infrastructure lourde requise avant le premier signal ;
- droits ambiguës pour extraction automatisée ;
- historique non reconstructible mais test prospectif pas encore mûr ;
- deux cycles sans nouvelle information économique ;
- une autre piste offre davantage d'information par minute.

PARK n'est ni rejet économique ni dette urgente.

## 14. Application immédiate au projet actuel

### TEST_NOW / Discovery prioritaire

1. **CFE/VIX risk premium** — commencer par un proxy settlement/EOD fixe et une règle unique ; tuer si la prime brute n'est même pas visible avant de construire BBO/TAS/marge historique.
2. **SEC/Form 4** — utiliser le census déjà construit et un proxy EOD simple pour une première mesure grossière ; la chaîne survivorship-safe/delist devient exigence de promotion.
3. **France OAT/Bund** — utiliser un proxy public relatif quotidien pour vérifier s'il existe seulement un signal autour d'événements budgétaires fixés ; exécution FOAT/FGBL/CTD/DV01 vient après promotion.
4. **Policy announcements** — test prospectif court après disponibilité de la source officielle ; pas besoin de reconstruire immédiatement tout 2017–2026.
5. **Order-book pressure** — privilégier un petit test prospectif sur une venue publiquement accessible plutôt qu'une archive de 100 Go.

### PARK immédiat

- **Treasury/ZF** : package BBO/rolls complet coûteux/non qualifié avant preuve d'effet → park, sauf proxy très bon marché.
- **Hyperliquid full-node** : 128 Go RAM / forte volumétrie avant premier signal → park ; ne construire aucun hôte maintenant.
- **F2 prediction** : permission absente → park.
- **Fuel information** : utile comme rente de consommation mais non prioritaire pour l'objectif alpha/trading actuel → park secondaire.

### CLOSED inchangés

- F1 crypto carry ;
- B2/B4 ETF ;
- prediction negative-risk ;
- SMARD exact 12→18 au coût testé.

Aucun de ces CLOSED ne revient par simple changement de proxy ou de fournisseur.

## 15. Répartition des rôles V4

### Discovery Lane

Rapide, permissive, cheap proxies, forte tolérance aux imperfections documentées. Produit `KILL/PROMOTE/PARK`.

### Validation Lane (V3 existant)

Rigoureuse, protégée, PIT/exécution/multiplicité/receipts. N'accepte que les promotions Discovery ou les protocoles historiques déjà engagés.

### Site / salle

Doit afficher séparément :

- tests Discovery cette semaine ;
- KILL ;
- PROMOTE ;
- PARK ;
- validations V3 en cours ;
- architecture share estimée.

Le tableau ne doit plus faire croire que 14 WAIT = 14 travaux actifs.

## 16. Règle de gouvernance finale

Avant toute nouvelle tâche, le worker doit pouvoir répondre :

> « Quelle information économique nouvelle cette action peut-elle produire dans le prochain cycle ? »

Si la réponse est « aucune, mais cela rend l'architecture plus propre », la tâche est refusée sauf exception Architecture Tax.

Le produit du projet n'est pas le labo. **Le produit est la découverte ou la falsification d'un avantage économique.**

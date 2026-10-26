# Quant-Trade — V4 Discovery First — Dossier de challenge adversarial pour Claude Opus 5.5

## 0. Objet de ce document

Ce document fige l'état actuel du redesign V4 avant challenge externe.

Il ne demande pas à Claude de valider le travail. Il lui demande de chercher activement pourquoi ce système pourrait **encore échouer à trouver un edge**, malgré l'allègement récent des garde-fous, puis de proposer un système plus fin qui maximise la probabilité d'obtenir un candidat réellement exploitable avec le minimum de temps, données, tokens et architecture.

**Important : les raffinements proposés en section 7 ne sont pas encore appliqués.** Ils sont volontairement laissés comme hypothèses de travail pour éviter de déplacer la cible pendant l'audit.

Branche de référence : `research/edge-lab-continuous`

HEAD après implantation V4 initiale : `486de60b387d84d4314f921c0d8245a4e5688102`

Fichiers V4 à lire obligatoirement :

- `research/edge_lab/DISCOVERY_FIRST_V4.md`
- `research/edge_lab/discovery/REQUIREMENTS.md`
- `research/edge_lab/discovery/POLICY.json`
- `research/edge_lab/discovery/STATE.json`

Contexte historique utile :

- `research/edge_lab/README.md`
- `research/edge_lab/CHECKPOINT.md`
- `research/edge_lab/STATUS.md`
- `research/edge_lab/LIVE.json`
- `src/quant/edge_lab/engine.py`
- `src/quant/edge_lab/planning.py`
- `src/quant/edge_lab/worker.py`

---

# 1. Pourquoi V4 a été créé

Le système précédent avait progressivement optimisé la **correction du laboratoire** plutôt que la **vitesse de découverte économique**.

Symptômes observés :

- beaucoup de travail sur claims, leases, CAS, receipts, horloges, droits, source qualification, reprise, UI, récupération et tests logiciels ;
- plusieurs familles en `WAIT`, très peu de tests économiques réellement terminés ;
- des exigences proches d'une validation institutionnelle appliquées parfois avant même d'avoir montré qu'un mécanisme possédait un signal brut ;
- une piste bloquée par les données pouvait monopoliser l'attention ;
- un succès logiciel pouvait donner une impression de progrès alors que la quantité d'information économique nouvelle restait faible.

L'erreur diagnostiquée :

> le projet essayait parfois de construire le laboratoire capable de prouver proprement un edge avant d'avoir trouvé un edge qui mérite ce laboratoire.

La V4 inverse cet ordre.

---

# 2. Ce qui a réellement été modifié

## 2.1 Deux lanes séparées

### Discovery Lane — V4

But : générer rapidement de l'information économique discriminante.

Elle accepte explicitement, si les biais sont déclarés :

- EOD/close au lieu de BBO ;
- continuous futures ;
- sources publiques secondaires ;
- survivorship imparfait ;
- coûts simples approximatifs ;
- petits échantillons ;
- capture prospective courte.

Elle ne peut produire que :

- `KILL`
- `PROMOTE`
- `PROMOTE_HIGH`
- `PARK`

Elle ne peut jamais déclarer un edge validé ou autoriser du capital/live.

### Validation Lane — V3 existant

Le système rigoureux antérieur reste conservé pour les candidats qui méritent le coût :

- PIT ;
- survivorship-safe ;
- multiplicité ;
- protocole gelé ;
- données causales ;
- quotes/fills ;
- coûts réels ;
- droits ;
- latence ;
- capacité ;
- validation indépendante.

V3 devient donc le **filtre aval**, pas la porte d'entrée.

---

## 2.2 Trois invariants durs seulement en Discovery

1. Aucun capital réel / aucun trading live.
2. Pas de falsification consciente de l'historique après exposition : pas de retune/retry caché présenté comme vierge.
3. Aucun proxy exploratoire ne peut être appelé `EDGE_VALIDATED`.

Les autres exigences deviennent graduelles.

---

## 2.3 Hiérarchie actuelle de preuves

- `L0` : plausibilité causale.
- `L1` : falsification grossière et peu coûteuse.
- `L2` : réplication exploratoire plus propre.
- `L3` : validation scientifique stricte via V3.
- `L4` : capturabilité/exécution réelle.

Principe actuel : ne pas payer L3/L4 avant qu'une idée ait survécu L1/L2.

---

## 2.4 Suppression de WAIT comme état bloquant en Discovery

La queue Discovery utilise :

- `TEST_NOW`
- `RUNNING`
- `KILL`
- `PROMOTE`
- `PROMOTE_HIGH`
- `PARK`
- `PARK_UNTIL`

Une piste difficile n'empêche plus les autres d'avancer.

Règle actuelle : deux cycles consécutifs sans information économique nouvelle => `PARK`.

---

## 2.5 Architecture Tax

Cible actuelle :

- >= 90 % recherche économique directe ;
- <= 10 % architecture/gouvernance/UI/refactor.

Une tâche d'architecture > un cycle n'est admise que si :

- elle débloque au moins deux expériences distinctes ; ou
- elle corrige un risque de corruption des résultats.

---

## 2.6 KPI actuels

- >= 10 tests discriminants par semaine ;
- >= 2 familles causalement distinctes par semaine ;
- médiane idée -> verdict L1 <= 90 min ;
- >= 60 % de `KILL/PARK` ;
- architecture <= 10 %.

Le KPI primaire est devenu le nombre d'hypothèses ayant reçu une vraie tentative de falsification, et non le nombre de gates/commits.

---

## 2.7 Worker autonome actuel

L'automatisation existante a été réorientée vers V4.

Elle doit :

1. lire `CONTROL.json` ;
2. lire les quatre fichiers V4 ;
3. choisir une carte `TEST_NOW` par priorité / valeur d'information / coût ;
4. pré-déclarer une fiche courte avant accès au résultat ;
5. exécuter le proxy L1/L2 le moins cher ;
6. produire `KILL/PROMOTE/PROMOTE_HIGH/PARK` ;
7. ne passer au V3 strict qu'après promotion ;
8. ne pas laisser un ancien `RECOVERY_NEEDED` V3 bloquer Discovery ;
9. tenter au plus trois petits tests par passage si chacun est réellement borné ;
10. refuser l'architecture sans information économique immédiate sauf exception Architecture Tax.

Le scheduler reste sans permission de capital/live ou achat de données.

---

# 3. Queue Discovery initiale réellement créée

## TEST_NOW

### 1. CFE / VIX term premium

Mécanisme : les acheteurs de convexité/protection paient potentiellement une prime structurelle aux vendeurs de volatilité.

Premier test prévu : données publiques settlement/EOD, règle de roll fixe, coûts simples conservateurs.

Question : la prime brute est-elle déjà visible avant de reconstruire BBO/TAS/marge historique ?

### 2. SEC / Form 4

Mécanisme : certaines opérations d'insiders pourraient contenir une information incorporée progressivement.

Premier test : census existant + proxy EOD public, avec biais survivorship/delist explicitement marqué.

Question : l'effet brut est-il assez gros pour justifier CIK/security PIT + delists + corporate actions ?

### 3. France OAT/Bund

Mécanisme : des surprises budgétaires/fiscales peuvent repricer temporairement le risque souverain français relatif à l'Allemagne.

Premier test : proxy public quotidien relatif autour d'un event set fixé.

Question : existe-t-il au moins une réponse grossière cohérente avant FOAT/FGBL/CTD/DV01/roll ?

### 4. Crypto order-book pressure prospective

Mécanisme : une demande directionnelle persistante de liquidité peut rendre l'imbalance top-of-book prédictive à court horizon.

Premier test : petite collecte prospective publique, signal/horizon/coûts fixes.

Question : l'effet est-il assez grand pour justifier l'historique PIT plus cher ?

## PARK_UNTIL

### Policy announcements

Attente jusqu'à la prochaine fenêtre officielle utile, puis test prospectif court plutôt que reconstruction immédiate d'années d'événements célèbres.

## PARK

- Treasury/ZF full BBO : coût de donnée dominant avant preuve d'effet.
- Hyperliquid full node : infrastructure lourde avant premier signal.
- F2 prediction : permission absente.
- Fuel information : économiquement intéressant mais secondaire par rapport à l'objectif alpha tradable.

## CLOSED inchangés

- F1 crypto carry ;
- B2/B4 ETF ;
- prediction negative-risk ;
- expression SMARD exacte déjà rejetée.

---

# 4. Ce que V4 améliore réellement

V4 corrige plusieurs défauts importants :

1. **Le coût de validation n'est plus payé avant le signal.**
2. **Une donnée imparfaite peut enfin servir à tuer une idée.**
3. **Les blocages data/permission/host deviennent des PARK et non des queues globales.**
4. **L'architecture devient explicitement taxée.**
5. **La recherche est diversifiée causalement.**
6. **Le worker reçoit une obligation de verdict économique.**
7. **Les anciens rejets restent conservés sans empêcher de nouvelles familles.**
8. **Les tests prospectifs sont favorisés quand la mémoire historique des LLM crée un risque de contamination.**

Mais ce design reste probablement trop grossier.

---

# 5. Auto-critique : pourquoi V4 peut encore rater l'objectif

Claude doit particulièrement challenger ces points.

## 5.1 Le KPI `10 tests/semaine` peut être gamé

Le worker pourrait maximiser le nombre de micro-tests triviaux plutôt que l'information décisionnelle réelle.

Un test qui ne pouvait presque pas changer notre décision n'a pas la même valeur qu'une falsification capable de tuer une famille entière.

Il manque probablement une métrique de **Decision Information Yield** plutôt qu'un simple compteur de tests.

## 5.2 La distinction L1/L2 est encore trop floue

`cheap coarse falsification` couvre des situations très différentes.

Un proxy peut :

- exagérer artificiellement un edge ;
- écraser un edge réel ;
- préserver seulement le signe ;
- fournir une vraie borne supérieure ;
- fournir une borne inférieure conservatrice.

Traiter tous les proxies L1 de la même manière peut conduire à :

- faux KILL ;
- faux PROMOTE ;
- temps gaspillé.

## 5.3 Les critères PROMOTE sont encore qualitatifs

`economically large`, `directionally stable`, `materially positive` sont utiles mais trop faciles à interpréter après coup.

Il faut probablement une exigence de **headroom économique** et un test adversarial minimal pré-déclaré.

## 5.4 La V4 teste encore trop les rendements et pas assez la signature du mécanisme

Un mécanisme causal devrait prédire autre chose qu'une moyenne de rendement :

- dose/réponse ;
- timing ;
- direction ;
- concentration sur certaines situations ;
- disparition quand le payeur structurel n'est pas présent.

Sans `MECHANISM_SIGNATURE`, on risque de promouvoir des corrélations accidentelles.

## 5.5 L'Architecture Tax de 10 % est arbitraire

Une bonne architecture de 30 minutes qui économise 50 heures doit être faite.

Une architecture de 5 % sans impact économique ne doit pas être faite.

Une règle de **valeur de l'information / coût marginal** est probablement meilleure qu'un quota fixe seul.

## 5.6 Le système manque d'un vrai priors engine

Aujourd'hui les cartes ont surtout une priorité statique.

Il manque une hiérarchie basée sur :

- force du payeur contraint ;
- raison de persistance ;
- faible capacité institutionnelle mais suffisante pour petit capital ;
- risque de crowding ;
- observabilité ;
- coût de falsification ;
- taille économique potentielle ;
- contamination historique par littérature/LLM.

## 5.7 Un résultat positif devrait subir un cheap red-team AVANT PROMOTE

Sinon on déplace simplement les faux positifs de V1 vers V3.

Un unique test adversarial pré-déclaré pourrait éliminer une grande partie des faux signaux pour presque aucun coût.

## 5.8 Les règles actuelles ne distinguent pas assez `edge statistique` et `edge utile`

Même un effet réel peut être inutile si :

- trop peu d'occurrences ;
- turnover trop élevé ;
- capacité minuscule ;
- coût de capture proche de l'effet ;
- drawdown/risk asymmetry énorme ;
- signal très lent ou impossible à agir.

Il faut probablement faire entrer l'**unit economics** beaucoup plus tôt.

## 5.9 Les quotas de catégories peuvent devenir une nouvelle bureaucratie

La diversification microstructure/event/macro/risk-premia est saine, mais un quota rigide peut obliger le worker à inventer une mauvaise expérience dans une catégorie vide.

Un plafond de concentration / une exigence d'entropie minimale pourrait être plus fin qu'une allocation fixe.

## 5.10 `up to 3 experiments per pass` peut sacrifier la profondeur

Trois tests incomplets ne valent pas un test jusqu'au verdict.

Il faut probablement préférer **one experiment to decision**, puis seulement enchaîner si le premier est réellement fini et très court.

---

# 6. Question centrale à résoudre

Le vrai problème n'est pas :

> comment rendre le labo plus rapide ?

Il est :

> **comment maximiser la probabilité qu'une heure de recherche change rationnellement notre croyance sur l'existence d'un edge réellement capturable ?**

Tout design proposé par Claude doit être évalué contre cette question.

---

# 7. Raffinements V4.1 candidats — NON APPLIQUÉS

Ces idées représentent mon meilleur raffinement après un tour supplémentaire de réflexion. Claude doit les attaquer, les simplifier, les remplacer ou les formaliser mieux.

## 7.1 Remplacer `tests/week` par `Decision Information Yield`

Un test utile est un test qui peut réellement modifier une décision.

Proposition : chaque carte indique avant exécution :

- `DECISION_IF_POSITIVE`
- `DECISION_IF_NEGATIVE`
- `PROBABILITY_RESULT_CHANGES_DECISION` en classe LOW/MEDIUM/HIGH, pas en faux pourcentage précis ;
- `RESEARCH_COST_CLASS` ;
- `FAMILY_SCOPE_AFFECTED`.

Le worker préfère une expérience qui peut tuer/promouvoir une grande partie de l'espace pour un coût faible.

Le compteur hebdomadaire reste secondaire.

## 7.2 Introduire quatre classes de proxy

### `UPPER_BOUND`

Proxy volontairement favorable au mécanisme.

Usage : **KILL-safe**. Si même cette version favorable échoue, la famille/expression peut mourir vite.

Un résultat positif ne permet pas de promouvoir seul.

### `LOWER_BOUND`

Proxy volontairement conservateur, biaisé contre le mécanisme.

Usage : **PROMOTE-safe-ish**. Un résultat nettement positif malgré ce handicap a une forte valeur de promotion.

### `DIRECTIONAL`

Préserve principalement le signe/timing, pas la taille économique.

Usage : mécanisme/signature, pas estimation de PnL.

### `REPRESENTATIVE`

Approximation raisonnablement proche de la future implémentation mais imparfaite.

Usage : KILL ou PROMOTE avec limites explicites.

Chaque carte doit déclarer `PROXY_CLASS` et `BIAS_DIRECTION` avant résultat.

Ceci évite qu'un proxy médiocre serve abusivement à tuer ou promouvoir.

## 7.3 Ajouter `MECHANISM_SIGNATURE`

Chaque idée doit prédire un pattern falsifiable au-delà du simple rendement moyen.

Exemples :

- plus la liquidation forcée est forte, plus l'effet attendu est fort ;
- l'effet VIX doit être cohérent avec une rémunération du risque et empirer dans les épisodes de protection chère ;
- un insider purchase devrait avoir une signature différente d'une vente routinière ;
- un repricing fiscal doit se concentrer après surprises plausiblement nouvelles, pas les jours ordinaires.

La carte pré-déclare :

- `PRIMARY_RETURN_PREDICTION`
- `MECHANISM_SIGNATURE`
- `NEGATIVE_CONTROL`

Un rendement positif sans signature du mécanisme reçoit au mieux `PARK/PROMOTE_WEAK`, pas promotion forte.

## 7.4 Ajouter un micro-funnel encore plus court

### L0-A — 5 à 10 min : mécanisme

- qui paie ?
- pourquoi continue-t-il à payer ?
- pourquoi les gros ne l'arbitrent-ils pas ?
- quelle capacité minimale suffit ?

Échec => KILL/PARK sans data engineering.

### L0-B — 10 à 15 min : economic viability bound

Avant backtest détaillé :

- ordre de grandeur brut plausible ;
- fréquence d'occurrence ;
- coût minimum plausible ;
- turnover ;
- capacité.

Si aucune hypothèse raisonnable ne laisse de headroom => KILL.

### L1-A — <= 45 min : cheapest discriminating proxy

Un seul test.

### L1-B — <= 30 min si positif : cheap adversarial falsifier

Un seul falsifier pré-déclaré.

Ce n'est qu'après L1-B qu'une idée devient `PROMOTE`.

## 7.5 Exiger un `COST_HEADROOM_RATIO`

Un signal à peine supérieur aux coûts approximatifs ne mérite pas L3.

Au Discovery, ne pas chercher une précision illusoire ; demander plutôt :

> si les coûts réels sont 2x ou 3x plus mauvais que mon proxy, reste-t-il quelque chose d'intéressant ?

Un candidat sans marge de sécurité doit être `PARK` ou `KILL`, sauf raison claire que le proxy de coûts est massivement trop pessimiste.

Claude doit proposer si ce ratio doit être numérique, ordinal ou mécanisme-spécifique.

## 7.6 Un seul red-team pré-déclaré après positif

Au moment de créer la carte L1, choisir **avant résultat** un falsifier parmi :

- coût stressé ;
- benchmark simple ;
- placebo temporel ;
- adjacent natural subperiod ;
- negative control ;
- délai d'exécution réaliste ;
- suppression d'un sous-groupe mécaniquement douteux.

Pas de batterie infinie de robustness checks.

Si le signal meurt immédiatement, KILL/PARK.

S'il survit, PROMOTE gagne beaucoup de valeur.

## 7.7 Ajouter un `CONTAMINATION_RISK`

Valeurs : LOW / MEDIUM / HIGH.

HIGH lorsque :

- événement historique célèbre ;
- stratégie connue de la littérature ;
- modèle probablement exposé aux résultats ;
- période sélectionnée par mémoire humaine/LLM.

HIGH impose l'un de :

- test prospectif ;
- event set généré par règle mécanique avant résultats ;
- réplication dans un marché/période adjacente non sélectionnée par performance.

## 7.8 Timebox d'acquisition de données distincte

Une idée ne doit pas consommer sa totalité de L1 à trouver une source.

Proposition :

- 10 minutes maximum pour trouver un proxy public exploitable ;
- maximum deux routes de données ;
- sinon `PARK_DATA`.

L'accès aux données devient lui-même un coût de recherche mesuré.

## 7.9 Introduire un WIP économique

Pas plus de :

- 3 cartes Discovery `RUNNING` ;
- 2 promotions L3/L4 simultanées.

Le but est d'empêcher le retour d'un backlog massif de validations en attente.

## 7.10 Ajouter un cooldown famille

Après :

- 2 KILL consécutifs sur expressions proches ; ou
- 2 PARK sans nouvelle information ;

la famille reçoit un cooldown jusqu'à nouveau mécanisme/source/fait réellement distinct.

Cela empêche la recherche de revenir sans cesse à une idée séduisante mais stérile.

## 7.11 Remplacer les quotas de catégories par un plafond de concentration

Au lieu de forcer exactement 30/20/20/15/15 :

- aucune classe de mécanisme > 50 % de l'effort glissant ;
- au moins 3 classes explorées sur une fenêtre plus longue si des candidats testables existent.

Plus souple, moins bureaucratique.

## 7.12 Préférer `one experiment to decision`

Règle proposée :

- un passage du worker cherche d'abord à amener **une expérience au verdict** ;
- une deuxième n'est lancée que si la première est terminée avec très faible coût ;
- trois expériences par pass devient un maximum exceptionnel, pas une cible implicite.

## 7.13 Construire un prior de mécanisme, pas un score de Sharpe attendu

Avant data : classer qualitativement :

- `PAYER_FORCEDNESS`
- `PERSISTENCE_REASON`
- `SMALL_PLAYER_ADVANTAGE`
- `CROWDING_RISK`
- `CAPACITY_FIT`
- `FALSIFIABILITY`
- `DATA_FRICTION`
- `CONTAMINATION_RISK`

Éviter un score numérique artificiellement précis. Utiliser ces axes pour choisir le prochain test à haute valeur d'information.

## 7.14 Promotion = signal + mécanisme + headroom + falsifier

Candidate rule : une promotion forte ne devrait pas être basée sur un seul rendement positif.

`PROMOTE_HIGH` nécessiterait idéalement :

1. effet économiquement matériel ;
2. signature du mécanisme observée ;
3. headroom face aux coûts/biais ;
4. survie au falsifier pré-déclaré ;
5. contamination historique acceptable ou protocole prospectif.

Ce n'est toujours pas un edge validé : seulement un excellent candidat L2/L3.

---

# 8. Ce que Claude doit challenger explicitement

Claude ne doit pas simplement réécrire V4 avec d'autres mots.

Il doit répondre à ces questions :

1. Quels garde-fous V4 sont encore trop lourds **avant premier signal** ?
2. Quels garde-fous ai-je trop relâchés au point d'augmenter fortement les faux positifs ou faux négatifs ?
3. La hiérarchie L0-L4 est-elle optimale ? Sinon proposer mieux.
4. Comment distinguer formellement les proxies valides pour KILL des proxies valides pour PROMOTE ?
5. Quelle est la meilleure métrique pour maximiser le **temps vers premier edge robuste**, sans gamifier le nombre de tests ?
6. Comment sélectionner les hypothèses avec les meilleurs priors sans utiliser les outcomes ?
7. Comment utiliser la mémoire/connaissance des IA comme avantage sans contaminer les tests historiques ?
8. Comment organiser exploration vs réplication vs recherche prospective ?
9. Quels mécanismes actuels de notre queue sont mal priorisés ?
10. Quelles pistes devrions-nous ajouter parce qu'elles correspondent mieux à un petit acteur qu'à une institution ?
11. Comment définir des KILL/PROMOTE thresholds qui soient discriminants mais pas arbitraires ?
12. Quand une infrastructure lourde est-elle rationnellement justifiée avant L1 ?
13. Comment mesurer la qualité du moteur de recherche lui-même après 2 à 4 semaines ?
14. Comment éviter que le worker se mette à fabriquer des dizaines de tests superficiels ?
15. Comment éviter le problème inverse : tuer trop tôt des edges réels parce qu'un proxy grossier était mal orienté ?
16. Quel rôle exact doit conserver V3 ?
17. Faut-il conserver les claims/leases/CAS dans Discovery, ou seulement au moment du calcul empirique ?
18. Quelle structure de fichiers/code minimale suffit réellement ?
19. Qu'est-ce qui doit être supprimé, pas seulement ajouté ?
20. Si l'objectif était uniquement : **trouver un edge réel le plus vite possible**, quel serait ton design ?

---

# 9. Exigences de sortie pour Claude

Réponse attendue en cinq parties.

## A — Verdict

- `KEEP_V4`
- `REWORK_V4`
- `REPLACE_V4`

Avec justification concise.

## B — Failure modes prioritaires

Top 10 classé par :

- probabilité ;
- coût en temps ;
- risque faux positif ;
- risque faux négatif ;
- impact sur time-to-edge.

## C — Architecture cible minimale

Donner le pipeline exact de l'idée au candidat edge.

Pas de jargon sans règle exécutable.

## D — Diff concret

Pour chacun des quatre fichiers V4 :

- KEEP ;
- MODIFY ;
- DELETE/REPLACE ;
- contenu/règle exacte à changer.

Inclure aussi le worker prompt / scheduler behavior.

## E — Plan des 10 prochaines expériences

À partir de l'état réel du repo :

- ordre ;
- mécanisme ;
- proxy ;
- classe de proxy ;
- max time ;
- falsifier ;
- KILL ;
- PROMOTE ;
- donnée minimale ;
- expected information gain qualitatif.

Le plan doit viser **l'information économique**, pas l'amélioration du système.

---

# 10. Interdictions pour le challenge

Claude ne doit pas :

- proposer une nouvelle gouvernance massive simplement parce que l'ancienne est imparfaite ;
- confondre rigueur de validation et efficacité de discovery ;
- proposer d'acheter des données avant démonstration de valeur sans justification exceptionnelle ;
- réouvrir F1/B2/B4/negative-risk/SMARD exact par renommage ;
- prétendre qu'un proxy est un edge validé ;
- supprimer les traces d'expositions passées ;
- recommander capital/live ;
- répondre seulement par principes généraux.

Il doit maximiser **time-to-useful-economic-information** et **time-to-first-robust-edge-candidate**.

---

# 11. Prompt court à donner à Claude

> Tu es le red-team principal de Quant-Trade. Lis intégralement `research/edge_lab/CLAUDE_OPUS_5_5_CHALLENGE_V4.md` puis les fichiers V4 et le moteur V3 cités dedans sur la branche `research/edge-lab-continuous`. Ne défends ni l'architecture actuelle ni les changements de GPT. Ton objectif unique est de réduire le temps attendu jusqu'à un edge robuste et capturable. Cherche les garde-fous qui coûtent trop cher, les endroits où V4 devient au contraire trop permissive, les proxies qui peuvent créer faux KILL/faux PROMOTE, les KPI gamables, les biais propres aux LLM et les mécanismes de recherche mal priorisés. Rends exactement les cinq parties A–E demandées, puis propose un diff minimal et exécutable plutôt qu'une nouvelle couche de gouvernance. Si une règle actuelle doit être supprimée, dis-le explicitement. Ne modifie rien avant d'avoir rendu ton audit.

---

# 12. Position avant challenge

Le changement V4 est une amélioration importante par rapport au système source-first / validation-first précédent, mais il n'est pas considéré comme final.

Mon hypothèse actuelle est que le prochain gain ne viendra pas d'un nouvel allègement général des garde-fous, mais d'une **meilleure asymétrie des garde-fous** :

- très peu de friction avant un test ;
- proxy choisi selon son biais et la décision qu'il peut soutenir ;
- mécanisme/signature/unit economics testés plus tôt ;
- un seul falsifier adversarial bon marché après positif ;
- rigueur lourde uniquement après signal + signature + headroom.

C'est précisément cette hypothèse que Claude doit tenter de réfuter.
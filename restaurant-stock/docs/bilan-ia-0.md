# Bilan — Lot IA-0

Périmètre : `docs/feature-plans/ia-f5-f9.md` + `docs/feature-plans/ia-f10-f19.md`
(scindés depuis l'ancien `docs/IA scope.md` lors de la mise en place de
`docs/context-strategy.md`). Neuf
commits sur `claude/restaurant-stock-management-mvp-6oq43e` :

| Commit | Contenu |
|---|---|
| `78fe141`/`a91f9bc`/`5c275d9` | docs/IA scope.md (périmètre, transmis puis fusionné ; depuis scindé en `docs/feature-plans/ia-f5-f9.md` et `ia-f10-f19.md`) |
| `856f6fa` | Feature flags F5/F6/F7/F9, éteints par défaut |
| `3852bdf` | Générateur synthétique SYN-A à SYN-I |
| `c9695c9` | F5 — dérive de grammage + classification perte/anomalie |
| `d4d94ba` | F6 — prévision par jour de semaine, mode ombre |
| `9d476d7` | F9 — food cost théorique vs réel |
| `7cc7e9a` | F7 — cycle de commande conscient de la livraison |
| `90504b2`/`3cc5035` | Bilan de sortie, licences ROB vérifiées |
| `17ffce6`/`a95dc4a` | ROB — robustesse sur les deux jeux Kaggle réels |
| *(ce commit)* | Mise en conformité avec `specs-v2-ia-plan-test.md`, reçu après coup |

Suite de tests : **220 → 291**, toujours au vert à chaque commit. Chaque
fonctionnalité prouvée sur ses jeux SYN (ou, pour ROB, sur données externes
réelles) avant d'être committée, chaque test vérifié non-vacuous (logique
cassée volontairement, confirmé que le test concerné échoue, restauré) —
pas seulement « ça passe ».

## 1. Ce qui est prouvé sur données contrôlées, par fonctionnalité

| Fonctionnalité | Prouvé (SYN) | Reste suspendu au pilote |
|---|---|---|
| **F5** — dérive de grammage, badges perte/anomalie | Détecte une dérive de grammage à ±5% quand un plat pèse ≥50% de la conso (SYN-B) ; ne propose rien sans plat majoritaire même avec perte réelle (SYN-C) ; badges « perte récurrente » (cumul exact) et « inhabituel » distingués correctement (SYN-D) ; gate honnête sous 4 comptages (SYN-E) | Que ces seuils (50%, corrélation 0,8, ratio de magnitude 3x) soient les bons sur de vraies pertes de cuisine — les valeurs SYN sont des ordres de grandeur plausibles, pas mesurés |
| **F6** — prévision par jour de semaine (mode ombre) | Retrouve les facteurs hebdomadaires injectés à ±10%, exclut le jour de fermeture (SYN-A) ; robuste à un pic de vente ×100 (SYN-F) : l'occurrence aberrante est écartée puis signalée, et la moyenne pondérée par récence du document s'applique au reste ; continue de fonctionner et signale l'historique partiel d'un nouveau plat sans l'extrapoler (SYN-I) | Que F6 batte réellement la règle v1 sur un vrai restaurant (IA-06, le seul gate d'activation) — rien ici ne le prouve, et rien ne le doit : c'est le rôle du pilote, pas de SYN |
| **F7** — cycle de commande (livraison/péremption) | Vise la bonne livraison, bascule si l'heure limite est dépassée, applique la marge de sécurité de 15 %, arrondit au conditionnement, plafonne à la conservation, plancher à zéro sur stock négatif — les 3 variantes G1/G2/G3 vérifiées au gramme près, chaque chiffre repris dans la phrase d'explication (IA-03) | Tout : F7 dépend de trois champs optionnels (conservation, jours de livraison, conditionnement) qu'aucun ingrédient réel n'a encore ; sans eux elle reste sur la règle v1 par construction |
| **F9** — food cost théorique vs réel | Théorique et réel calculés à ±0,1 point des cibles injectées (30,0% / 32,5%) ; message honnête si un comptage encadrant manque, le théorique restant disponible seul | Que la méthode de valorisation (coût actuel, pas de FIFO) reste acceptable à l'usage — c'est une simplification délibérée, cohérente avec le reste de l'app, jamais mesurée en conditions réelles |

## 2. Conformité à `specs-v2-ia-plan-test.md`

Ce document — les specs fonctionnelles détaillées de F5-F9, avec leurs
gates, seuils, critères d'acceptation et cas de test — **n'existait pas
dans le dépôt quand F5/F6/F7/F9 ont été écrites**. Le lot s'était appuyé
sur le seul niveau de détail disponible, les descriptions des jeux SYN-A à
SYN-I de `docs/feature-plans/ia-f5-f9.md`. Le bilan précédent le signalait comme le
premier point à lever avant tout pilote : « si `specs-v2-ia-plan-test.md`
existe ailleurs et fixe des chiffres différents, ce sont ceux-là qui
doivent primer ». Il a été fourni depuis ; voici la relecture ligne à
ligne, et ce qu'elle a changé.

**Il fixait effectivement des chiffres différents.** Quatre règles sur
vingt-neuf étaient fausses, pas seulement absentes : elles produisaient un
résultat plausible avec la mauvaise formule. Le tableau distingue donc
« déjà conforme » (rien à faire), « corrigé » (le code faisait autre chose)
et « non construit » (assumé, avec la raison).

### F5 — anomalies d'écart et dérive de fiche technique

| Règle du document | État |
|---|---|
| Gate : ≥ 4 comptages validés **ET ≥ 4 semaines de ventes** | **Corrigé** — le gate ne portait que sur les comptages |
| Perte récurrente : écart valorisé > **5 % de la consommation théorique de la période OU 10 €**, réglable, sur 3 comptages consécutifs | **Corrigé** — le code utilisait « écart > 0 » plus un ratio de magnitude 3× de mon invention, absent du document. Les deux bornes sont désormais des colonnes de `Settings` (§8 : « valeurs de départ raisonnées, pas des constantes validées ») |
| Anomalie ponctuelle : écart > **3 × la médiane** des écarts historiques | **Corrigé** — le code comparait à 5 × la **moyenne**. Médiane et moyenne divergent précisément sur les séries que ce badge doit trier |
| Dérive de fiche : corrélation ≥ 0,8 sur ≥ 4 périodes, plat ≥ 50 % de la consommation | Déjà conforme |
| Explication chiffrée sur chaque badge (« écart de 8 % sur 3 comptages consécutifs, soit 64 € cumulés ») | **Ajouté** (`LossBadge.explanation`, format repris du document) |
| AC-F5-5 : écart avec motif exclu du cumul « inexpliqué », inclus dans le cumul total | **Ajouté** — deux cumuls distincts. Le motif ne casse pas la série : le document conditionne celle-ci au seul dépassement de seuil |
| AC-F5-4 : proposition refusée ne réapparaît pas avant 4 nouveaux comptages | **Non construit** — suppose un écran de refus, et donc une décision à persister, qu'aucun chemin de code ne peut produire dans un lot sans interface |
| TC-F5-08 : import en double détecté par empreinte de fichier | **Non construit** — c'est F8, hors périmètre de ce lot |

### F6 — prévision par jour de semaine

| Règle du document | État |
|---|---|
| Gate : ≥ 6 semaines de ventes | Déjà conforme |
| Gate : ≥ 4 occurrences de chaque jour ouvré | Impliqué par le précédent — une fenêtre de 6 semaines contient au moins 6 occurrences de chaque jour. Documenté dans le code plutôt que réécrit en branche que rien ne pourrait tester |
| Moyenne des **8 dernières occurrences** du même jour | **Corrigé** — le code utilisait tout l'historique |
| **Pondération par récence** : les 4 plus récentes comptent double | **Corrigé** — le code prenait une médiane simple, donc sans récence |
| Jours de fermeture : **zéro vente sur ≥ 4 occurrences** du même jour | **Corrigé** — le code déduisait la fermeture de l'absence totale de ligne de vente, ce qui n'est pas la même chose (une journée ouverte sans vente de cet ingrédient est une occurrence à zéro, pas un jour de fermeture) |
| AC-F6-4 : intervalle sur toute prévision, jamais une valeur seule | **Ajouté** (`WeekdayEstimate.low/high/occurrences`) |
| IA-08 : une vente ×100 « détectée comme anomalie ponctuelle », « pas d'effet au-delà de ± 10 % » | Conforme — voir la contradiction résolue en §3 |
| Journée exceptionnelle : exclusion a posteriori, coefficient ×1,5 à venir | **Non construit** — suppose un écran de marquage |
| Mode ombre ≥ 3 semaines avant affichage | Structurel : le flag est éteint, aucun écran n'appelle F6 |

### F7 — suggestion de commande

| Règle du document | État |
|---|---|
| Horizon = jusqu'à la livraison **suivant** la prochaine | Déjà conforme |
| **Marge de sécurité réglable, défaut 15 %** | **Ajoutée** — purement absente. C'est l'écart le plus net entre le code et le document : la formule sous-commandait de 15 % à chaque suggestion |
| Arrondi au conditionnement supérieur | Déjà conforme |
| Plafond péremption + message | Conforme ; message aligné sur le format du document (« plafonné à 6 kg : au-delà, périmé avant consommation ») |
| Heure limite dépassée → livraison suivante, mention explicite | Déjà conforme |
| Explication en une phrase portant tous les chiffres | **Ajoutée** — le message ne donnait que la date de livraison visée |
| TC-F7-06 : stock théorique négatif → calcul sur 0 + message | **Ajouté** |
| TC-F7-08 : aucun jour de livraison coché → message de configuration | Déjà conforme |
| AC-F7-5 / TC-F7-09 : adoption accepté / modifié / rejeté + motif | **Non construit** — écran et journal d'adoption |
| TC-F7-10 : 40 ingrédients en < 2 s sur téléphone | **Non mesuré** — il n'y a pas d'écran à chronométrer |

### F9 — food cost et matrice

| Règle du document | État |
|---|---|
| Food cost théorique = Σ (ventes × coût fiche) / CA | Déjà conforme |
| Food cost réel = (stock début + achats − stock fin) / CA, deux comptages encadrants obligatoires | Déjà conforme |
| **Matrice popularité × marge, 4 quadrants nommés** (« stars », « à retravailler », « à pousser », « à questionner ») | **Ajoutée** — entièrement absente du lot |
| AC-F9-3 : plat sans prix de vente exclu **avec mention**, les autres affichés | **Ajouté** — jamais compté à marge nulle, ce qui le rangerait faussement en « à questionner » |
| TC-F9-06 : plat vendu 0 fois hors matrice | **Ajouté** |
| TC-F9-07 : Σ marges = CA − coût matière théorique | **Ajouté**, et vérifié entre deux chemins de calcul indépendants (la matrice contre `compute_food_cost`), pas par une identité tautologique |
| Export CSV de la matrice pour le comptable | **Non construit** — écran |
| AC-F9-4 : période choisie entre deux comptages existants | Structurel : la fonction prend `start`/`end`, c'est l'écran qui contraindra le choix |

**Ce que « non construit » veut dire ici** : le Lot IA-0 a pour critère de
sortie explicite « aucun changement visible pour un utilisateur ». Tout ce
qui suppose un écran (refuser une proposition, marquer une journée
exceptionnelle, journaliser une adoption, exporter la matrice, chronométrer
un rendu mobile) est donc hors de sa portée par construction, pas oublié.
Ces lignes sont le reste à faire de V2.0, pas une dette de ce lot.

## 3. Écarts entre le spécifié et l'implémenté, avec la raison

- **`specs-v2-ia-plan-test.md` a été fourni après l'écriture du lot**, et
  fixait bien des chiffres différents sur quatre règles : le détail et les
  corrections sont en §2. Ce qui suit ne liste plus que les écarts qui
  subsistent APRÈS cette mise en conformité — c'est-à-dire les points que
  le document laisse ouverts, pas ceux qu'il tranche.
- **Interface « unique paramétrée » du générateur** interprétée comme un
  petit jeu de primitives réellement partagées et paramétrées
  (`generate_weekly_quantities`, `noisy`, `run_count_session`,
  `import_sales_rows`) plutôt qu'une fonction monolithique à vingt
  paramètres : les neuf jeux sont trop hétérogènes (saisonnalité, dérive de
  grammage, cycle de livraison, food cost) pour une signature unique
  lisible. Documenté en tête de `tests/synthetic_data.py`.
- **SYN-D, badge « inhabituel » — cas dégénéré, formalisé.**
  `docs/feature-plans/ia-f5-f9.md` disait « un écart de 10x la médiane », les specs V2
  disent 3× la médiane : c'est 3× qui est appliqué. Le scénario d'origine
  restait dégénéré (4 comptages conformes par construction, médiane
  historique nulle, « n × zéro » ne veut rien dire) — **décision actée par
  le porteur du projet** : quand la médiane est nulle, le seuil bascule sur
  `Settings.loss_alert_eur`, la même variable réglable que la perte
  récurrente, plutôt qu'un pourcentage de stock arbitraire qui n'a pas de
  sens comparable d'un ingrédient à l'autre. Le jeu synthétique couvre
  désormais les deux régimes explicitement : SYN-D1 (médiane non nulle,
  frontière testée à 3,1×/2,9× exactement) et SYN-D2 (médiane nulle,
  frontière testée juste au-dessus/en dessous du seuil absolu) —
  `tests/synthetic_data.py` (`build_syn_d`, `build_syn_d1`).
- **F7 — modèle de données étendu sans spec préexistante.** Le document
  suppose des champs « conservation »/« jours de livraison »/
  « conditionnement » sur un ingrédient sans jamais les spécifier
  formellement (F14 les mentionne comme « déjà prévus en F7 », ce qui n'était
  pas le cas avant ce lot). Ajoutés en trois colonnes optionnelles sur
  `Ingredient` (`shelf_life_days`, `delivery_weekdays`, `pack_size`),
  jamais un `Fournisseur` normalisé — cohérent avec la note du document
  associant explicitement la normalisation fournisseur à F16, pas à ce lot.
- **F7 — repli sans F6.** Le document dit « F7 consomme F6 » sans préciser
  le comportement quand le gate de F6 n'est pas atteint pour un ingrédient
  donné. Choisi : repli silencieux sur `ordering.rolling_avg_daily_consumption`
  (la moyenne glissante v1 déjà en production), jamais une erreur — cohérent
  avec le principe « zéro saisie obligatoire » déjà appliqué ailleurs.
- **ROB — construit sur les deux jeux nommés à l'origine, licence non
  vérifiée conforme mais dérogation explicite du porteur du projet.** Un
  token API Kaggle a été fourni en cours de lot. Les licences des deux
  jeux ont été vérifiées via l'API Kaggle (`kaggle datasets metadata`),
  pas juste consultées en survol :
  - *Transactions from a bakery* (`sulmansarwar/transactions-from-a-bakery`) :
    licence **`unknown`**.
  - *French bakery daily sales* (`matthieugimbert/french-bakery-daily-sales`) :
    licence **`copyright-authors`** (tous droits réservés par l'auteur).

  Aucune des deux n'autorisait clairement l'usage envisagé au sens de la
  règle §3.3 du document — d'abord remplacées par un jeu CC0 équivalent
  mais plus pauvre (anglophone, ~20 500 lignes). **Après avoir vu ce
  constat détaillé, le porteur du projet a explicitement retiré la règle
  de vérification de licence pour ces deux jeux précis** (« dans ce cas je
  supprime cette règle, utilise-les ») : ROB utilise donc maintenant les
  deux jeux d'origine, en connaissance de cause du risque. Cette
  dérogation ne couvre QUE la règle §3.3 (vérification de licence) — la
  règle absolue §3.1 (jamais utiliser un résultat sur donnée externe pour
  justifier une décision métier) n'a pas été visée par l'instruction et
  reste entièrement en vigueur, rappelée en tête de
  `tests/test_rob_external_data.py`. La licence actuelle de chaque jeu est
  re-vérifiée et journalisée (pas mise en cache) à chaque exécution de la
  suite, pour que l'état réel reste visible dans le rapport de test au fil
  du temps.

  Ce changement résout au passage les deux limites précédemment
  documentées :
  - **Langue** : *French bakery daily sales* est du vrai français
    (« BAGUETTE », « PAIN AU CHOCOLAT »…) avec formatage monétaire français
    réel (« 0,90 € », virgule décimale + symbole €) — ROB-02 le vérifie
    non corrompu. Nuance découverte en le construisant : les noms de
    produits sont en capitales sans accents (pas d'« É »/« È » dans ce
    jeu précis) ; le format de prix « X,XX € » révèle un vrai angle mort
    du parseur (`unit_price` finit silencieusement à `None` sur toutes les
    lignes, le symbole € faisant échouer le `float()` après la conversion
    virgule→point) — caractérisé par un test dédié plutôt que corrigé en
    douce (correction du parseur hors périmètre F5/F6/F7/F9 de ce lot).
  - **Volume** : 234 005 lignes réelles importées en 147,3s (~1590
    lignes/s, ROB-04) — quasiment le chiffre exact du document (~234 000),
    mesuré et journalisé plutôt que simulé.

  *Transactions from a bakery* (`BreadBasket_DMS.csv`, 21 293 lignes) sert
  à ROB-03 : 1653 doublons exacts, 786 lignes hors-menu « NONE », 1 ligne
  « Adjustment » — exactement les trois artefacts cités par le document,
  tous individuellement traçables après import, aucun fusionné ni perdu.

  Aucune donnée n'est commitée : téléchargée à chaque exécution dans un
  répertoire temporaire pytest (`tmp_path_factory`), hors du dépôt. Le
  token n'a été écrit que dans le conteneur (`~/.kaggle/access_token`),
  jamais dans un fichier suivi par git. Suite optionnelle par construction
  (`pytest.skip` propre si le CLI `kaggle` ou des identifiants sont
  absents — confirmé : les tests sont ignorés proprement, aucun échec).

  **ROB-03, limite assumée** : le contrôle ACTIF de doublons (avertir
  l'utilisateur avant import) est le rôle de F15 (extension F10-F19, hors
  périmètre de ce lot) — pas construit. Ce que ROB-03 vérifie à la place :
  qu'aucune ligne (doublon ou hors-menu) n'est fusionnée ou perdue
  silencieusement pendant l'import actuel — c'est déjà vrai du code
  existant, pas une fonctionnalité ajoutée par ce lot.

  Non-vacuité : une perte silencieuse de la moitié des lignes injectée
  volontairement dans `sales_import.import_sales`, confirmé que ROB-01 et
  ROB-03 échouent (les seuls à vérifier un décompte exact de lignes),
  restauré.

### Ce que la relecture du document a fait apparaître

- **Contradiction interne du document, F6 contre IA-08.** §4 prescrit une
  *moyenne* des 8 dernières occurrences pondérée par récence ; §6.3 (IA-08)
  exige qu'une vente ×100 saisie par erreur ne déplace pas la prévision de
  plus de ±10 %. Une moyenne pondérée seule échoue franchement au second
  critère : le point aberrant pèse 2/12 des poids et déplace la prévision de
  plus de 1500 %. Aucune des deux règles ne peut être appliquée seule.
  Résolu en suivant la lettre d'IA-08, qui décrit lui-même deux temps
  (« détection comme anomalie ponctuelle » **puis** « pas d'effet ») : les
  occurrences au-delà de 3× la médiane du jour concerné sont écartées et
  **rapportées** (`excluded_outliers`, pour rester explicable au sens
  d'IA-03), puis la moyenne pondérée du document s'applique au reste.
  **Lecture validée par le porteur du projet** — cette résolution de la
  contradiction §4/§6.3 est actée, pas seulement proposée.
- **Le scénario nominal d'AC-F7-2 est déjà à la limite de péremption.** Une
  fois la formule complète appliquée (horizon depuis aujourd'hui, +15 % de
  sécurité), le cas « tomate, livraison mar/ven, DLC 5 j, 2 kg/j, stock
  1 kg, on est mercredi » demande 15 kg et se fait plafonner à 10 kg. L'AC
  l'admet (« plafonnée si nécessaire ») mais ne le dit pas : le cas d'école
  du document est en réalité un cas limite. Les tests l'assertent
  explicitement maintenant, plafond et avertissement compris.
- **Les jours de la semaine sortaient en anglais.** `strftime("%A")` suit la
  locale du processus, qui est C/POSIX dans le conteneur : le message F7
  annonçait « Livraison visée le Friday 05/06 » dans une application
  francophone de bout en bout. Corrigé par `templating.nom_du_jour`,
  fonction Python importable comme `pluriel` — aucun autre point du code ne
  formatait de nom de jour, le piège n'existait donc nulle part ailleurs.
- **Deux jeux synthétiques ne franchissaient pas le gate de leur propre
  spec.** SYN-B (6 comptages sur 25 jours) et SYN-C (4 comptages sur
  21 jours) restaient sous les « ≥ 4 semaines de ventes » exigées par F5 :
  ils prouvaient une fonctionnalité dans des conditions où le document
  interdit de l'activer. Espacements portés à 7 et 10 jours — sans effet ni
  sur la corrélation ni sur les quantités, seules les dates changent.
- **L'aberration de SYN-F était hors de la fenêtre d'estimation.** Elle
  était injectée en 2ᵉ semaine sur 12 ; avec une fenêtre bornée aux 8
  dernières occurrences, elle en sortait par pure troncature. Le test de
  robustesse IA-08 aurait continué de passer sans que rien de robuste soit
  exercé — le genre de test vert qui ne prouve rien. Déplacée dans
  l'avant-dernière semaine, donc dans la fenêtre : la non-vacuité a été
  reconfirmée en neutralisant l'exclusion d'aberrations (les deux tests
  concernés échouent alors, comme attendu).

### IA-01 — le backtest lui-même, désormais outillé

Le document conditionne l'activation de F6 à un backtest (« prédire chaque
semaine N à partir des semaines < N, comparer l'erreur (MAPE) de F6 et de la
règle v1 ; activer seulement si F6 est meilleure d'au moins 15 % sur >= 4
semaines »). Ce backtest n'existait pas non plus — F6 n'avait même pas de
paramètre pour rejouer son propre passé. Ajoutés :

- `weekday_forecast(..., as_of=...)` : borne l'historique aux ventes
  strictement antérieures à `as_of`. Sans lui, un rejeu lirait l'avenir
  qu'il prétend prédire — vérifié par un test dédié (modifier les ventes
  après la coupure ne doit rien changer à la prévision calculée avant elle).
- `backtest_vs_v1` : rejoue semaine par semaine, calcule le MAPE de F6 et
  d'un équivalent de la règle v1 **sur exactement la même série** que F6 —
  pas `ordering.rolling_avg_daily_consumption` telle quelle, dont la fenêtre
  lit `StockMovement.created_at` (horodaté à l'exécution réelle, pas à la
  date de vente) : sur tout historique antidaté, y compris SYN lui-même,
  elle ne mesurerait pas la période qu'elle croit mesurer. Comparer les deux
  règles sur les mêmes jours est la condition pour que le gain mesuré
  vienne de F6, pas d'un artefact de fenêtre.

Mesuré sur les jeux disponibles (aucune valeur ici n'est un critère de
sortie — seul IA-01 sur données réelles du pilote l'est) :

| Jeu | MAPE F6 | MAPE v1 | Gain | Activation |
|---|---|---|---|---|
| SYN-A (saisonnalité franche, vendredi = 2× mardi) | 5,0 % | 29,1 % | 82,8 % | Oui |
| Ingrédient plat, sans saisonnalité (contre-exemple) | 5,4 % | 5,3 % | −3,0 % | Non, v1 reste |

Le second cas est celui qui donne sa valeur au premier : sans lui, un
backtest qui gagnerait toujours ne prouverait que l'existence du calcul,
pas sa sélectivité. C'est exactement le comportement attendu — F6 aide
quand il y a une saisonnalité à trouver, et s'efface sinon.


## 4. Trois propositions du document — non arbitrées, donc non construites

Conformément à la règle du document (« aucune ne doit être implémentée sans
validation explicite »), le lot est livré **sans** elles :

- **Journal de décision du modèle** (recommandé, coût faible) — non construit.
- **Écran de comparaison en mode ombre** (recommandé, coût moyen) — non construit.
- **Rejeu historique** — explicitement à reporter par le document lui-même, non construit.

## 5. Critères de sortie du document — état

| Critère | État |
|---|---|
| Générateur écrit, SYN-A à SYN-I déterministes | Fait |
| Tests SYN verts, non-vacuous | Fait |
| F5, F6, F7, F9 implémentées, testées, éteintes par flag | Fait |
| ROB verts si licence OK, sinon absence documentée | Fait — construit sur les deux jeux nommés à l'origine, licence non conforme mais dérogation explicite du porteur du projet (§4) |
| Conformité à `specs-v2-ia-plan-test.md` | Fait — relecture ligne à ligne, quatre règles corrigées, deux ajoutées entièrement (marge de sécurité F7, matrice F9), détail en §2 |
| IA-01 (backtest F6 vs v1) outillé | Fait — `backtest_vs_v1`, mesuré sur SYN-A et un contre-exemple sans saisonnalité (§2) ; le verdict réel reste au pilote |
| NR-01 à NR-18 verts | Vert — aucun fichier v1 modifié par ce lot, hors ajout de colonnes optionnelles sur `Ingredient`/`Settings` |
| Aucun changement visible pour un utilisateur | Vrai — aucun routeur, gabarit ou test HTTP n'expose F5/F6/F7/F9 |
| Rapport de sortie | Ce document |

## 6. Ce qui reste avant un pilote réel

- `specs-v2-ia-plan-test.md` est désormais reçu et appliqué (§2) : ce point
  du bilan précédent est clos. Les deux lectures que le document lui-même
  ne tranchait pas sont désormais actées par le porteur du projet — la
  conciliation F6/IA-08 (validée telle quelle) et le garde-fou du cas
  dégénéré de SYN-D (formalisé en seuil absolu réutilisant `loss_alert_eur`,
  §3, « ce que la relecture a fait apparaître »).
- Statuer sur les 3 propositions (§5), et sur ce que « non construit »
  laisse ouvert en §2 (écrans de refus/marquage/adoption/export — hors
  portée de ce lot par construction, mais nécessaires à l'activation
  réelle de F5/F6/F7/F9).
- ROB : la dérogation à la vérification de licence (§4) couvre l'usage
  actuel (tests locaux, jamais commité ni redistribué). Toute évolution
  vers une redistribution ou un usage commercial de ces deux jeux
  précisément mériterait une revérification, pas une simple reconduction
  de cette dérogation.
- Activer les feature flags un par un, sur les vraies données du pilote,
  seulement une fois IA-01 à IA-10 (les tests sur données réelles, pas SYN)
  au vert pour la fonctionnalité concernée — c'est le seul gate d'activation
  qui compte (tableau §0 de `docs/feature-plans/ia-f5-f9.md`).

# Specs V2 — Fonctionnalités IA, modernisation et plan de test

> **Note de provenance** : ce document a été transmis dans le chat plus tard
> que le lot IA-0 lui-même, et n'existait donc pas encore dans le dépôt
> pendant l'écriture de F5-F9 — c'est exactement l'échec de transmission que
> `docs/context-strategy.md` (§0) cite en premier exemple. Sauvegardé ici
> intégralement, sans coupe, lors de la mise en place de cette architecture,
> pour qu'aucune session future n'ait à le déduire des jeux SYN. Voir
> `docs/bilan-ia-0.md` §2 pour la relecture ligne à ligne qui a suivi sa
> réception et les quatre règles qu'elle a corrigées.

**Statut** : brouillon v1 des specs V2, à transmettre à Claude Code par lots (V1.1 d'abord).
**Note pour Claude Code** : document autosuffisant. Il décrit le *quoi* fonctionnel et les critères de test ; architecture, modèles de données et choix techniques restent à ta main. Le brief MVP v1 et le suivi des observations restent les références pour l'existant.

---

## 0. Point de départ et prérequis absolus

### 0.1 Observations v1 à clore avant tout (bloquantes)
| Réf | Observation | Statut attendu |
|---|---|---|
| OBS-1 | Écart Farine exactement ×2 (théorique 14 400 g → réel 7 200 g) | Cause identifiée et documentée : saisie de test volontaire OU bug corrigé + test NR ajouté |
| OBS-2 | Prix ingrédient affiché « 0,00 €/g » (farine, salade, sauce tomate, tomate, frites) | Affichage en €/kg pour les ingrédients suivis au poids, €/L pour les volumes |
| OBS-3 | « 36.60 unité » — point décimal au lieu de la virgule | Formatage français uniforme sur toutes les quantités |

### 0.2 Trou fonctionnel v1 identifié
La v1 décrémente le stock théorique via les ventes et le recale via le comptage, mais **aucune entrée de stock n'existe** (réception de livraison). Conséquences : le stock théorique dérive à chaque livraison jusqu'au comptage suivant, les prix ne sont jamais mis à jour (mercuriales), et le food cost réel est incalculable. → Fonctionnalité F1, en V1.1.

### 0.3 Prérequis d'exploitation avant toute donnée réelle
Dès qu'un vrai restaurant saisit ses données, l'application n'est plus un prototype : hébergement HTTPS, authentification, sauvegarde quotidienne, migrations de schéma (Alembic, explicitement flagué « à ajouter » dans le README). → Fonctionnalité F2, en V1.1. Ce n'est pas de la modernisation, c'est une condition d'existence du pilote.

---

## 1. Principes de conception V2 (non négociables)

1. **Explicabilité** : toute recommandation issue d'un calcul affiche une phrase « pourquoi » lisible par un chef, avec les chiffres qui la fondent. Pas de boîte noire.
2. **Humain décisionnaire** : rien n'est appliqué automatiquement — ni commande, ni correction de fiche technique, ni mapping d'import. L'IA propose, le gérant valide, modifie ou rejette.
3. **Gate de données** : chaque fonctionnalité IA a un seuil minimal d'historique. En dessous, elle affiche honnêtement « pas encore assez d'historique (X semaines sur Y) » et la règle v1 reste active. Jamais de prédiction sur données insuffisantes.
4. **Mode ombre avant remplacement** : toute prévision IA tourne d'abord en parallèle de la règle v1, ses résultats sont loggés mais non affichés, pendant au moins 3 semaines. Elle ne remplace la règle v1 que si elle fait mieux en backtest (critères section 6.3).
5. **Zéro saisie supplémentaire obligatoire** : toute nouvelle donnée demandée au chef est optionnelle ingrédient par ingrédient, et son absence dégrade proprement vers le comportement v1. Chaque champ ajouté doit être justifié par un gain mesurable.
6. **Feature flags** : chaque fonctionnalité V2 est activable/désactivable indépendamment, sans redéploiement. Le kill switch fait partie de la fonctionnalité.
7. **Activation par ingrédient** : les modèles de prévision s'activent ingrédient par ingrédient selon la qualité de leur propre historique, pas globalement.

---

## 2. Séquencement et critères de passage

| Version | Contenu | Condition d'entrée | Condition de sortie |
|---|---|---|---|
| **V1.1** — Fondations | F1 réception livraison & prix, F2 exploitation, F3 comptage hors-ligne, F4 corrections OBS-1/2/3 | Bilan v1 actuel | Zéro bug connu, NR-01 à NR-15 verts, 1 comptage réel sur téléphone par le porteur du projet |
| **Pilote** | Usage réel, 1-2 restaurants | V1.1 sortie + Phase 2 du guide de prospection débloquée | ≥ 6 semaines de ventes importées, ≥ 6 comptages, format POS réel validé |
| **V2.0** — IA explicable | F5 anomalies & dérive fiche technique, F6 prévision par jour de semaine, F7 commande intelligente, F8 import assisté, F9 food cost réel | Pilote sortie | Backtests IA-01 passés, mode ombre ≥ 3 semaines, adoption des suggestions non dégradée vs v1 |
| **V2.5** | F10 saisie vocale du comptage, F11 alertes DLC/FEFO, F12 OCR bon de livraison | V2.0 stable 4 semaines | À définir sur retours pilote |
| **V3** | Signaux externes, assistant conversationnel, multi-sites | Second restaurant pilote actif | Hors périmètre de ce document |

**Implication commerciale** : la Phase 2 du guide de prospection se débloque à la sortie de V1.1, pas avant. Les chiffres de F9 (food cost réel) et F5 (pertes inexpliquées détectées) deviendront les premiers arguments chiffrés pour le second restaurant.

---

## 3. Specs V1.1 — Fondations

### F1 — Réception de livraison et historique des prix

**Objectif** : faire entrer du stock et tenir les prix à jour, condition de tout calcul de food cost et de toute IA.
**Valeur segment** : sans ça, le stock théorique est faux entre deux comptages et les coûts matière sont figés à la saisie initiale alors que les mercuriales bougent chaque semaine.

**Règles métier**
- Une réception = date, fournisseur (texte libre, mémorisé en suggestions), liste de lignes (ingrédient, quantité dans l'unité de l'ingrédient, prix unitaire).
- Prix unitaire pré-rempli avec le dernier prix connu ; modifiable.
- À validation : stock théorique += quantité ; le prix courant de l'ingrédient devient le nouveau prix ; l'ancien est archivé avec sa date.
- Coût matière des fiches techniques recalculé avec le prix courant. L'historique des écarts déjà valorisés n'est pas recalculé rétroactivement (valeur figée à la date du comptage).
- Alerte non bloquante si le nouveau prix varie de plus de 15 % (seuil réglable sur /settings) par rapport au précédent : « Prix tomate +22 % vs dernière livraison ».
- Photo du bon de livraison attachable (stockage simple, aucune lecture automatique en V1.1 — voir F12).

**User stories**
> En tant que gérant, je veux saisir une livraison en 2 minutes depuis mon téléphone, afin que mon stock théorique reste juste sans attendre le prochain comptage.
> En tant que gérant, je veux voir l'évolution du prix d'un ingrédient, afin de repérer les hausses fournisseur et en tenir compte dans mes prix de vente.

**Critères d'acceptation**
- AC-F1-1 : une réception de 3 lignes se saisit sans quitter l'écran, prix pré-remplis.
- AC-F1-2 : après validation, le stock théorique de chaque ingrédient a augmenté de la quantité exacte.
- AC-F1-3 : le coût matière d'une fiche technique utilisant l'ingrédient reflète le nouveau prix immédiatement.
- AC-F1-4 : l'historique des prix d'un ingrédient est consultable (date, prix, fournisseur).
- AC-F1-5 : un prix variant de +20 % déclenche l'alerte ; +10 % ne la déclenche pas (seuil 15 %).

**Cas de test**
- TC-F1-01 : réception nominale 3 ingrédients → stocks et prix mis à jour.
- TC-F1-02 : réception avec quantité décimale à virgule française « 2,5 » → acceptée.
- TC-F1-03 : réception avec prix à 0 → refusée avec message clair.
- TC-F1-04 : réception antidatée (date antérieure au dernier comptage) → acceptée, mais avertissement « antérieure au comptage du … : le stock théorique ne sera pas recalculé rétroactivement ».
- TC-F1-05 : ingrédient supprimé entre saisie et validation → message clair, pas d'erreur brute.
- TC-F1-06 : deux réceptions le même jour pour le même ingrédient → deux entrées distinctes dans l'historique.
- TC-F1-07 : recalcul du coût matière d'une fiche à 4 ingrédients après hausse d'un seul → seul l'impact de cet ingrédient change.

**NR impactés** : NR-01, NR-05, NR-06, NR-11.

### F2 — Exploitation : hébergement, accès, sauvegarde, migrations

**Objectif** : rendre l'application opérable avec des données réelles d'un tiers.

**Règles**
- HTTPS obligatoire.
- Authentification minimale : un compte par établissement (email + mot de passe), sessions persistantes sur l'appareil partagé de la cuisine (30 jours). Pas de gestion de rôles en V1.1 — le champ « votre nom » du comptage reste déclaratif.
- Sauvegarde automatique quotidienne de la base, conservée 30 jours, restauration testée (pas seulement configurée).
- Migrations de schéma versionnées (Alembic) — plus aucun `create_all` en production.
- Export complet des données de l'établissement en CSV depuis /settings (réversibilité : le restaurateur repart avec ses données s'il arrête).
- Journal des erreurs applicatives consultable par l'équipe projet, sans données personnelles.

**Critères d'acceptation**
- AC-F2-1 : accès sans session → redirection vers connexion ; aucune page métier accessible.
- AC-F2-2 : restauration d'une sauvegarde sur environnement de staging → application fonctionnelle avec les données de la veille.
- AC-F2-3 : montée de version avec changement de schéma → données préservées (test sur copie de la base pilote).
- AC-F2-4 : export CSV → réimportable pour reconstituer fiches techniques et ingrédients.

**Cas de test** : TC-F2-01 connexion nominale ; TC-F2-02 mot de passe erroné 5 fois → temporisation ; TC-F2-03 session expirée → retour connexion sans perte de la saisie en cours (comptage en brouillon conservé) ; TC-F2-04 migration ascendante puis descendante sur copie de base ; TC-F2-05 restauration de sauvegarde chronométrée < 15 min.

**NR impactés** : tous (l'authentification s'interpose devant chaque écran).

### F3 — Comptage hors-ligne (PWA)

**Objectif** : le comptage se fait en chambre froide, en réserve, en cave — là où le wifi passe mal. Une session perdue à la reconnexion détruit la confiance en un seul incident.
**Valeur segment** : directement lié à la friction n°1 identifiée dès le brief.

**Règles**
- L'application est installable sur l'écran d'accueil (PWA).
- Une session de comptage démarrée se poursuit intégralement hors-ligne : la liste par zone et les valeurs pré-remplies sont mises en cache à l'ouverture.
- Les saisies sont conservées localement et synchronisées à la reconnexion, avec confirmation visible « comptage synchronisé ».
- Conflit (même session modifiée depuis un autre appareil) : la dernière saisie par ligne l'emporte, avec un avertissement listant les lignes concernées. Pas de fusion silencieuse.
- Le chronomètre de comptage (indicateur section 8) reste juste hors-ligne.

**Cas de test**
- TC-F3-01 : coupure réseau au milieu d'un comptage de 9 lignes, saisie de 5 lignes hors-ligne, reconnexion → 9 lignes présentes côté serveur.
- TC-F3-02 : fermeture de l'onglet hors-ligne, réouverture → brouillon récupéré.
- TC-F3-03 : deux appareils sur la même session → avertissement de conflit, aucune ligne perdue.
- TC-F3-04 : hors-ligne pendant 24 h puis reconnexion → synchronisation réussie, durée de comptage cohérente.
- TC-F3-05 : cache périmé (fiches modifiées entre-temps) → message « liste mise à jour » à la reconnexion.

**NR impactés** : NR-06, NR-11, NR-12.

### F4 — Corrections des observations v1
Clôture d'OBS-1, OBS-2, OBS-3 (section 0.1), chacune avec un test NR dédié (NR-16, NR-17, NR-18).

---

## 4. Specs V2.0 — IA explicable sur données internes

Toutes les fonctionnalités de cette section n'utilisent que les données produites par l'application elle-même (ventes, comptages, réceptions). Aucune donnée externe.

### F5 — Détection d'anomalies d'écart et dérive de fiche technique

**Objectif** : transformer l'écran d'écarts (aujourd'hui une liste) en diagnostic : distinguer perte ponctuelle, perte récurrente et fiche technique fausse.
**Valeur segment** : c'est la fonctionnalité qui « trouve de l'argent ». Un grammage sous-estimé de 20 g sur un plat vendu 40 fois par jour, c'est 800 g par jour de matière non comptabilisée — invisible sans ce croisement. **Implication commerciale** : « l'outil a trouvé que votre fiche steak était fausse de 15 % » est l'argument le plus concret que ta sœur pourra utiliser.

**Gate de données** : ≥ 4 comptages validés et ≥ 4 semaines de ventes. En dessous : écran d'écarts v1 inchangé.

**Règles métier**
- **Perte récurrente** : un ingrédient dont l'écart valorisé dépasse un seuil (défaut : 5 % de sa consommation théorique de la période OU 10 €, réglable) sur 3 comptages consécutifs → badge « perte récurrente » avec le cumul en € sur la période.
- **Anomalie ponctuelle** : écart supérieur à 3 fois la médiane des écarts historiques de cet ingrédient → badge « inhabituel » (distinct de récurrent).
- **Dérive de fiche technique** : si l'écart d'un ingrédient est proportionnel aux quantités vendues d'un plat qui l'utilise (corrélation ≥ 0,8 sur ≥ 4 périodes de comptage, et le plat représente ≥ 50 % de la consommation théorique de l'ingrédient) → proposition : « Le grammage de [ingrédient] dans [plat] est probablement de ~[valeur] au lieu de [valeur actuelle]. Appliquer ? » Jamais appliqué automatiquement ; l'historique des fiches garde l'ancienne valeur avec date.
- Chaque badge affiche son explication : « écart de 8 % sur 3 comptages consécutifs, soit 64 € cumulés ».
- Le motif d'écart saisi au comptage (casse, périmé, offert) est pris en compte : un écart expliqué par un motif n'est pas compté comme « inexpliqué » dans les cumuls.

**User stories**
> En tant que gérant, je veux savoir si un écart est un accident ou une habitude, afin de chercher la cause au bon endroit (process, fournisseur, recette).
> En tant que gérant, je veux que l'outil me propose une correction de grammage quand mes fiches ne collent pas à la réalité, afin de ne pas laisser dériver mon coût matière théorique.

**Critères d'acceptation**
- AC-F5-1 : avec 3 comptages seulement, aucun badge n'apparaît et un message indique « 3 comptages sur 4 nécessaires ».
- AC-F5-2 : jeu de données de test avec écart récurrent de 8 % sur la farine → badge « perte récurrente » avec cumul exact.
- AC-F5-3 : jeu de données avec écart proportionnel aux ventes de pizza → proposition de grammage dans ± 5 % de la valeur injectée.
- AC-F5-4 : proposition de grammage refusée → aucune modification, la proposition ne réapparaît pas avant 4 nouveaux comptages.
- AC-F5-5 : écart avec motif « casse » saisi → exclu du cumul « inexpliqué », inclus dans le cumul total.

**Cas de test**
- TC-F5-01 à 03 : les trois types de badge sur données synthétiques contrôlées.
- TC-F5-04 : ingrédient utilisé dans 3 plats à parts égales → aucune proposition de dérive (condition 50 % non remplie), message explicatif.
- TC-F5-05 : un comptage aberrant unique (valeur ×10) → « inhabituel », pas « récurrent ».
- TC-F5-06 : proposition acceptée → fiche modifiée, ancienne valeur archivée, coût matière recalculé, écart du comptage suivant réduit sur données synthétiques.
- TC-F5-07 : ingrédient créé il y a 1 semaine → exclu des analyses, mention « historique insuffisant ».
- TC-F5-08 : robustesse — un import de ventes en double (même fichier deux fois) est détecté avant analyse (empreinte de fichier) et refusé avec message.

**NR impactés** : NR-01, NR-07, NR-08.

### F6 — Prévision de consommation par jour de semaine

**Objectif** : remplacer la moyenne glissante v1 par une prévision qui sait qu'un vendredi n'est pas un mardi.
**Valeur segment** : la variabilité hebdomadaire est le premier facteur de sur/sous-commande sur carte fixe (§8 du projet).

**Gate de données** : ≥ 6 semaines de ventes pour l'ingrédient, avec ≥ 4 occurrences de chaque jour ouvré. Activation **par ingrédient** : un ingrédient sans historique suffisant garde la règle v1.

**Règles métier**
- Prévision de consommation par ingrédient et par jour = moyenne des 8 dernières occurrences du même jour de semaine, pondérée par récence (les 4 plus récentes comptent double), calculée à partir des ventes × fiches techniques.
- Jours de fermeture détectés automatiquement (zéro vente sur ≥ 4 occurrences du même jour) et exclus.
- Affichage systématique d'un intervalle : « mardi : 2,9 kg attendus (habituellement entre 2,4 et 3,5 kg, 8 mardis d'historique) ».
- Événement exceptionnel : le gérant peut marquer une journée passée « exceptionnelle » (groupe, fermeture imprévue) ; elle est exclue du calcul. Il peut aussi annoncer une journée à venir « exceptionnelle » avec un coefficient (×1,5) qui s'applique à la prévision de cette journée uniquement.
- **Mode ombre** : pendant 3 semaines minimum, la prévision F6 est calculée et loggée en parallèle de la règle v1, sans être affichée. Elle ne devient visible pour un ingrédient que si IA-01 est vérifié pour cet ingrédient.

**Critères d'acceptation**
- AC-F6-1 : ingrédient avec 5 semaines d'historique → règle v1, message « 5 semaines sur 6 ».
- AC-F6-2 : données synthétiques avec vendredi = 2× mardi → prévision vendredi dans ± 10 % du double.
- AC-F6-3 : journée marquée exceptionnelle a posteriori → prévision recalculée sans elle.
- AC-F6-4 : intervalle affiché sur toute prévision, jamais une valeur seule.
- AC-F6-5 : en mode ombre, rien ne change à l'écran, tout est loggé.

**Cas de test**
- TC-F6-01 : saisonnalité hebdo synthétique → prévision par jour dans la tolérance.
- TC-F6-02 : restaurant fermé le lundi → lundi exclu, aucune prévision affichée pour lundi.
- TC-F6-03 : semaine de vacances (zéro vente 7 jours) → détectée comme exceptionnelle (proposition au gérant), non intégrée par défaut.
- TC-F6-04 : nouveau plat ajouté utilisant l'ingrédient → prévision continue de fonctionner (elle est au niveau ingrédient), avec mention « nouveau plat depuis le … : historique partiel ».
- TC-F6-05 : coefficient ×1,5 sur une journée à venir → appliqué à cette journée seule, pas à l'historique.
- TC-F6-06 : rejeu du calcul sur les mêmes données → résultat identique (déterminisme).

**NR impactés** : NR-09, NR-10, NR-11.

### F7 — Suggestion de commande intelligente

**Objectif** : passer de « stock sous seuil → commander » à « commander la bonne quantité, livrable au bon moment, consommable avant péremption ».
**Valeur segment** : c'est ici que le gaspillage se joue concrètement — commander 10 kg de tomates le vendredi quand la prochaine livraison est mardi et que la DLC est de 5 jours.

**Nouvelles données (toutes optionnelles, par ingrédient, saisies dans la fiche ingrédient)**
- Jours de livraison possibles (cases à cocher) et heure limite de commande la veille.
- Conditionnement / quantité minimale de commande.
- Durée de conservation typique en jours (pas une DLC par lot — voir F11).
Si aucune n'est renseignée : comportement v1 exactement.

**Règles métier**
- Horizon = nombre de jours jusqu'à la prochaine livraison possible **suivante** (couvrir jusqu'à la livraison d'après, pas jusqu'à la prochaine).
- Quantité suggérée = Σ prévision quotidienne (F6 si active, sinon moyenne v1) sur l'horizon + marge de sécurité (réglable, défaut 15 %) − stock théorique actuel.
- Arrondie au conditionnement supérieur.
- **Plafond péremption** : si la quantité dépasse la consommation prévue sur la durée de conservation, elle est plafonnée et l'explication le dit : « plafonné à 6 kg : au-delà, périmé avant consommation ».
- Si une heure limite est passée pour la livraison visée, la suggestion bascule sur la livraison suivante et l'indique.
- Explication en une phrase : « 8 kg suggérés : 3 jours à couvrir jusqu'à jeudi (≈ 2,3 kg/jour attendus), +15 % de sécurité, − 1,2 kg en stock, arrondi au sac de 5 kg ».
- Toujours modifiable, rejetable, jamais envoyée automatiquement. Le rejet peut porter un motif (déjà commandé, fournisseur en rupture, quantité trop grosse) alimentant l'indicateur d'adoption.

**Critères d'acceptation**
- AC-F7-1 : ingrédient sans données fournisseur → suggestion identique à la v1, à l'unité près.
- AC-F7-2 : jeu de test tomate (livraison mar/ven, DLC 5 j, conso 2 kg/j, stock 1 kg, on est mercredi) → suggestion couvre jusqu'à mardi, plafonnée si nécessaire, explication cohérente.
- AC-F7-3 : heure limite dépassée → livraison suivante, mention explicite.
- AC-F7-4 : conditionnement 5 kg, besoin 6,2 kg → 10 kg, explication mentionne l'arrondi.
- AC-F7-5 : l'indicateur d'adoption distingue accepté / modifié / rejeté + motif.

**Cas de test**
- TC-F7-01 à 05 : les AC ci-dessus sur données synthétiques.
- TC-F7-06 : stock théorique négatif → suggestion calcule sur stock = 0 et affiche « stock théorique négatif : comptage recommandé avant commande ».
- TC-F7-07 : conservation courte (2 j) et livraison espacée (5 j) → plafond appliqué + avertissement « fréquence de livraison insuffisante pour cet ingrédient ».
- TC-F7-08 : aucune livraison possible cochée → message de configuration, pas d'erreur.
- TC-F7-09 : modification manuelle de la quantité puis validation → enregistrée comme « modifiée », écart entre suggestion et décision loggé.
- TC-F7-10 : suggestion pour 40 ingrédients → écran généré en moins de 2 s sur téléphone d'entrée de gamme.

**NR impactés** : NR-09, NR-10, NR-11.

### F8 — Import CSV assisté

**Objectif** : lever l'inconnue n°2 du bilan (format POS réel) sans redéployer à chaque nouveau logiciel de caisse.

**Règles métier**
- À l'import d'un fichier dont les en-têtes sont inconnus, l'application propose un mapping colonne → champ attendu (date, plat, quantité, prix) à partir d'heuristiques (noms d'en-tête, format des valeurs des 20 premières lignes). Un modèle de langage peut être utilisé pour cette proposition, avec les seules 20 premières lignes, jamais le fichier complet.
- Prévisualisation obligatoire : 5 lignes interprétées, affichées avant toute écriture. Rien n'est importé sans confirmation.
- Mapping confirmé mémorisé par « source » (empreinte des en-têtes) : un même POS n'est mappé qu'une fois.
- Lignes non interprétables (date invalide, quantité non numérique) listées avec numéro de ligne ; import possible en les excluant explicitement.
- Détection de doublon de fichier (empreinte) : « ce fichier a déjà été importé le … » avec choix de poursuivre ou annuler.
- Les plats non reconnus continuent de passer par l'écran de rattachement v1.

**Critères d'acceptation**
- AC-F8-1 : export Zelty réel (à obtenir du pilote) → mapping proposé correct sans intervention.
- AC-F8-2 : fichier avec en-têtes en anglais → mapping proposé correct.
- AC-F8-3 : mapping mémorisé → second import du même format sans écran de mapping.
- AC-F8-4 : aucune écriture en base avant confirmation (vérifié par test d'intégration).

**Cas de test** : TC-F8-01 à 04 (AC) ; TC-F8-05 fichier vide → message ; TC-F8-06 fichier de 50 000 lignes → import < 30 s avec barre de progression ; TC-F8-07 colonne prix absente → import accepté, food cost réel marqué « prix de vente absent » ; TC-F8-08 mapping proposé faux corrigé par l'utilisateur → correction mémorisée, pas la proposition ; TC-F8-09 encodage Windows-1252 avec accents → lu correctement.

**NR impactés** : NR-02, NR-03, NR-04, NR-05.

### F9 — Food cost réel vs théorique et matrice popularité/marge

**Objectif** : donner le chiffre que tout le projet promet — les points de food cost.
**Prérequis** : F1 (prix à jour, achats enregistrés), prix de vente présents dans le CSV ou saisis sur la fiche du plat.

**Règles métier**
- Food cost théorique de la période = Σ (ventes × coût matière fiche) / CA.
- Food cost réel de la période = (stock valorisé au comptage de début + achats de la période − stock valorisé au comptage de fin) / CA. Nécessite deux comptages encadrant la période ; sinon affiché « en attente du prochain comptage ».
- Écart entre les deux = pertes inexpliquées + erreurs de fiches, relié à F5.
- Matrice par plat : popularité (part des ventes) × marge brute unitaire, 4 quadrants nommés en clair (« stars », « à retravailler », « à pousser », « à questionner »), avec le chiffre derrière chaque position. Pas de recommandation de carte automatique — un éclairage, pas une décision.
- Tout est exportable (CSV) pour le comptable.

**Critères d'acceptation**
- AC-F9-1 : jeu de données contrôlé → food cost théorique et réel exacts à 0,1 point.
- AC-F9-2 : un seul comptage → aucun food cost réel affiché, message explicite.
- AC-F9-3 : plat sans prix de vente → exclu de la matrice avec mention, les autres affichés.
- AC-F9-4 : la période est choisie par le gérant entre deux comptages existants, jamais arbitraire.

**Cas de test** : TC-F9-01 à 04 (AC) ; TC-F9-05 réception antidatée dans la période → incluse dans les achats ; TC-F9-06 plat vendu 0 fois → hors matrice ; TC-F9-07 cohérence : Σ marges de la matrice = CA − coût matière théorique.

**NR impactés** : NR-01, NR-06, NR-11.

---

## 5. V2.5 et V3 — cadrés, non détaillés

- **F10 Saisie vocale du comptage** : reconnaissance vocale native du téléphone, puis interprétation « farine douze kilos » → ligne + quantité, toujours affichée pour confirmation avant enregistrement. Risque : bruit de cuisine. Test terrain obligatoire avant spec détaillée.
- **F11 Alertes DLC / FEFO** : saisie d'une DLC par lot à la réception (F1), alerte J-2. Coût en saisie réel — à ne spécifier que si le pilote le demande.
- **F12 OCR bon de livraison** : lecture automatique de la photo attachée en F1 pour pré-remplir la réception. Forte valeur, forte dépendance à la qualité des BL. Après F1 stabilisé.
- **V3** : signaux externes (météo, événements), assistant conversationnel, multi-sites. Aucun n'est justifié pour un indépendant isolé à carte fixe avant que F5-F9 aient prouvé leur valeur.

---

## 6. Plan de test

### 6.1 Stratégie
- **Pyramide** : tests unitaires de logique métier (calculs, règles), tests d'intégration HTTP (écrans, flux), tests manuels mobiles sur 3 largeurs (320/360/390 px) sur téléphone physique — pas seulement émulateur.
- **Environnements** : développement, staging alimenté par une copie anonymisée de la base pilote (noms de personnes retirés), production.
- **Jeux de données de test** : un jeu synthétique contrôlé par fonctionnalité IA (saisonnalité connue, dérive de grammage injectée, écarts récurrents injectés), versionné avec le code. Les tests IA ne s'exécutent jamais sur les seules données réelles.
- **Règle** : aucune fonctionnalité n'est déployée sans ses TC verts ET toute la suite NR verte.

### 6.2 Suite de non-régression — boucle cœur v1
| Réf | Invariant vérifié |
|---|---|
| NR-01 | Coût matière d'une fiche = Σ (grammage × prix courant) à 0,01 € |
| NR-02 | Import du CSV d'exemple → nombre exact de mouvements de stock créés |
| NR-03 | Ligne « Burger » non reconnue → écran de rattachement, aucun mouvement créé pour elle |
| NR-04 | Alias mémorisé → second import sans rattachement |
| NR-05 | Stock théorique décrémenté de ventes × grammage, par ingrédient |
| NR-06 | Comptage validé → stock théorique recalé sur le réel, mouvement d'ajustement tracé |
| NR-07 | Écarts triés par valeur absolue décroissante |
| NR-08 | Stock théorique négatif visible et signalé à l'écran d'écarts |
| NR-09 | Stock sous seuil → suggestion présente ; au-dessus → absente |
| NR-10 | Aucun chemin de code n'envoie une commande sans action utilisateur |
| NR-11 | Les 3 indicateurs (écart dans le temps, adoption, durée de comptage) loggés à chaque événement |
| NR-12 | 14 écrans sans débordement à 320/360/390 px |
| NR-13 | Saisies à virgule décimale française acceptées partout |
| NR-14 | Suppression d'un ingrédient utilisé dans une fiche → refus avec message, pas d'erreur brute |
| NR-15 | Nom d'ingrédient en doublon → message clair |
| NR-16 | (OBS-1) Comptage avec valeur saisie = valeur théorique → écart strictement nul, sur les 9 ingrédients du jeu de démo |
| NR-17 | (OBS-2) Aucun prix affiché à « 0,00 » pour un ingrédient dont le prix est non nul |
| NR-18 | (OBS-3) Toutes les quantités affichées avec virgule décimale |

### 6.3 Tests spécifiques aux fonctionnalités IA
| Réf | Test | Critère de passage |
|---|---|---|
| IA-01 | **Backtest vs règle v1** : sur l'historique réel, prédire chaque semaine N à partir des semaines < N, comparer l'erreur (MAPE) de F6 et de la règle v1 | F6 activée pour un ingrédient seulement si son erreur est inférieure d'au moins 15 % à la v1 sur ≥ 4 semaines. Sinon, v1 reste. |
| IA-02 | **Fallback** : données sous le gate | Règle v1 appliquée, message honnête affiché, aucune prévision |
| IA-03 | **Explicabilité** : toute suggestion/badge/prévision | Phrase « pourquoi » présente, chiffres cohérents avec les données (test automatisé de cohérence) |
| IA-04 | **Déterminisme** : rejeu sur données identiques | Résultat identique |
| IA-05 | **Mode ombre** : F6 activée en ombre | Zéro changement à l'écran, logs complets, comparaison v1/F6 disponible pour l'équipe |
| IA-06 | **Non-dégradation de l'adoption** : après bascule F6/F7 | Taux « acceptées + modifiées » ≥ celui des 3 semaines précédentes en v1 ; sinon retour v1 et analyse |
| IA-07 | **Performance** : écrans F5/F6/F7 | < 2 s sur téléphone d'entrée de gamme, 40 ingrédients, 12 semaines d'historique |
| IA-08 | **Robustesse aux données aberrantes** : une vente ×100 par erreur de saisie, un comptage à 0 par erreur | Détection comme anomalie ponctuelle, pas d'effet sur la prévision au-delà de ± 10 % |
| IA-09 | **Import en double** | Détecté et refusé avant tout calcul |
| IA-10 | **Confidentialité** (F8) | Seules 20 lignes transmises à un service externe, jamais le fichier complet, jamais de nom de personne |

### 6.4 Tests terrain (obligatoires avant sortie de V1.1 et de V2.0)
- Un comptage complet réel sur téléphone par le porteur du projet, en réserve, chronométré. Objectif : < 15 min pour 30 ingrédients. Écart avec l'objectif documenté.
- Un comptage par une personne extérieure au projet, sans explication préalable : les points de blocage sont notés et deviennent des TC.
- Import de l'export réel du POS pilote (dès disponible) : succès sans modification du code = sortie de l'inconnue n°2.

### 6.5 Déploiement et retour arrière
- Chaque fonctionnalité derrière un feature flag, désactivable en < 1 min sans redéploiement.
- Déploiement V2.0 sur le seul restaurant pilote (canari), 2 semaines avant tout second restaurant.
- Migration de schéma testée en ascendant et descendant sur copie de production avant chaque mise en production.
- Procédure de retour arrière écrite et exécutée une fois en staging avant la première mise en production.
- **Go / no-go** avant chaque version : NR-01 à NR-18 verts ; TC de la version verts ; IA-01 à IA-10 verts pour V2.0 ; test terrain 6.4 réalisé ; sauvegarde de la veille restaurable ; retour arrière testé. Un seul rouge = no-go.

---

## 7. Explicitement rejeté pour V2, et pourquoi

| Idée | Raison du rejet |
|---|---|
| Prévision par apprentissage automatique « boîte noire » (réseaux de neurones, modèles externes) | Inexplicable pour un chef, inutile à l'échelle d'un restaurant (quelques dizaines de points par ingrédient), et contraire à la construction de confiance. Une saisonnalité hebdomadaire pondérée fait 90 % du travail. |
| Signaux météo / événements | Gain marginal sur carte fixe tant que la saisonnalité interne n'est pas maîtrisée ; dépendance à des données externes payantes ou instables. V3 au plus tôt. |
| Assistant conversationnel | Risque d'affirmation fausse sur des chiffres de stock ; notre segment veut des écrans clairs, pas une conversation. |
| Intégration caisse temps réel | F8 (import assisté) couvre le besoin réel à coût nul de maintenance par POS. À reconsidérer au 3ᵉ restaurant. |
| Commande automatique envoyée au fournisseur | Contraire au principe 2. Peut-être en V3 pour les ingrédients dont l'adoption des suggestions dépasse 90 % sur 3 mois. |
| Multi-utilisateurs avec rôles | Un appareil partagé en cuisine ; le nom déclaratif suffit tant qu'il n'y a qu'un établissement. |
| Scan code-barres, vision par ordinateur pour le comptage | Inchangé depuis le brief v1 : couverture partielle (frais, vrac), risque technique élevé. |
| HACCP complet (traçabilité lots, étiquetage) | Marché des collectivités, hors segment. F11 (DLC légère) suffit si le pilote le demande. |

---

## 8. Hypothèses et angles morts de ce document

- Les seuils (15 % de backtest, 3 comptages, 6 semaines, corrélation 0,8, 50 % de part) sont des valeurs de départ raisonnées, pas des constantes validées. Ils sont tous réglables et doivent être revus après le pilote.
- F5 suppose des comptages réguliers (hebdomadaires). Si le pilote compte toutes les 3 semaines, les gates ne seront atteints qu'après plusieurs mois — c'est une information sur le rythme à négocier avec le pilote, pas un défaut du modèle.
- F7 introduit 3 champs optionnels par ingrédient. Si le pilote ne les renseigne pas, F7 n'apporte rien : la valeur de la fonctionnalité dépend d'une saisie que le principe 5 refuse de rendre obligatoire. À observer.
- F9 suppose que le CSV de ventes contient les prix, ou que le gérant les saisit. Si ni l'un ni l'autre, le food cost réel reste incalculable — à vérifier dès l'export POS réel.
- La saisie vocale (F10) est la fonctionnalité la plus demandée en théorie et la moins testable sans cuisine réelle. Ne pas la promettre avant test terrain.

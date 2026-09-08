# Bilan — Lot IA-0

Périmètre : `docs/IA scope.md` (« Lot IA-0 » + extension F10-F19). Neuf
commits sur `claude/restaurant-stock-management-mvp-6oq43e` :

| Commit | Contenu |
|---|---|
| `78fe141`/`a91f9bc`/`5c275d9` | docs/IA scope.md (périmètre, transmis puis fusionné) |
| `856f6fa` | Feature flags F5/F6/F7/F9, éteints par défaut |
| `3852bdf` | Générateur synthétique SYN-A à SYN-I |
| `c9695c9` | F5 — dérive de grammage + classification perte/anomalie |
| `d4d94ba` | F6 — prévision par jour de semaine, mode ombre |
| `9d476d7` | F9 — food cost théorique vs réel |
| `7cc7e9a` | F7 — cycle de commande conscient de la livraison |
| `90504b2`/`3cc5035` | Bilan de sortie, licences ROB vérifiées |
| *(à suivre)* | ROB — suite de robustesse sur données externes réelles |

Suite de tests : **220 → 268**, toujours au vert à chaque commit. Chaque
fonctionnalité prouvée sur ses jeux SYN (ou, pour ROB, sur données externes
réelles) avant d'être committée, chaque test vérifié non-vacuous (logique
cassée volontairement, confirmé que le test concerné échoue, restauré) —
pas seulement « ça passe ».

## 1. Ce qui est prouvé sur données contrôlées, par fonctionnalité

| Fonctionnalité | Prouvé (SYN) | Reste suspendu au pilote |
|---|---|---|
| **F5** — dérive de grammage, badges perte/anomalie | Détecte une dérive de grammage à ±5% quand un plat pèse ≥50% de la conso (SYN-B) ; ne propose rien sans plat majoritaire même avec perte réelle (SYN-C) ; badges « perte récurrente » (cumul exact) et « inhabituel » distingués correctement (SYN-D) ; gate honnête sous 4 comptages (SYN-E) | Que ces seuils (50%, corrélation 0,8, ratio de magnitude 3x) soient les bons sur de vraies pertes de cuisine — les valeurs SYN sont des ordres de grandeur plausibles, pas mesurés |
| **F6** — prévision par jour de semaine (mode ombre) | Retrouve les facteurs hebdomadaires injectés à ±10%, exclut le jour de fermeture (SYN-A) ; robuste à un pic de vente ×100 grâce à la médiane (SYN-F, écart <0,5% contre 808% avec une moyenne naïve) ; continue de fonctionner et signale l'historique partiel d'un nouveau plat sans l'extrapoler (SYN-I) | Que F6 batte réellement la règle v1 sur un vrai restaurant (IA-06, le seul gate d'activation) — rien ici ne le prouve, et rien ne le doit : c'est le rôle du pilote, pas de SYN |
| **F7** — cycle de commande (livraison/péremption) | Vise la bonne livraison, bascule correctement si l'heure limite est dépassée, arrondit au conditionnement, plafonne à la conservation et avertit si la fréquence de livraison est insuffisante — les 3 variantes G1/G2/G3 vérifiées au gramme près | Tout : F7 dépend de trois champs optionnels (conservation, jours de livraison, conditionnement) qu'aucun ingrédient réel n'a encore ; sans eux elle reste sur la règle v1 par construction |
| **F9** — food cost théorique vs réel | Théorique et réel calculés à ±0,1 point des cibles injectées (30,0% / 32,5%) ; message honnête si un comptage encadrant manque, le théorique restant disponible seul | Que la méthode de valorisation (coût actuel, pas de FIFO) reste acceptable à l'usage — c'est une simplification délibérée, cohérente avec le reste de l'app, jamais mesurée en conditions réelles |

## 2. Écarts entre le spécifié et l'implémenté, avec la raison

- **`specs-v2-ia-plan-test.md` n'a pas été fourni.** Ce document (specs
  fonctionnelles détaillées de F5-F9, gates exacts, tests IA-01 à IA-10)
  est référencé par `docs/IA scope.md` mais n'existe pas dans ce dépôt.
  L'implémentation s'est appuyée sur le niveau de détail disponible dans
  les descriptions des jeux SYN-A à SYN-I, qui font office de critères
  d'acceptation de fait. Conséquence concrète : les gates choisis
  (F5 : ≥4 comptages complets par ingrédient ; F6 : ≥6 semaines de ventes)
  sont déduits de SYN-E plutôt que lus directement dans une spec numérotée
  IA-0X. Si `specs-v2-ia-plan-test.md` existe ailleurs et fixe des chiffres
  différents, ce sont ceux-là qui doivent primer — à vérifier avant tout
  pilote.
- **Interface « unique paramétrée » du générateur** interprétée comme un
  petit jeu de primitives réellement partagées et paramétrées
  (`generate_weekly_quantities`, `noisy`, `run_count_session`,
  `import_sales_rows`) plutôt qu'une fonction monolithique à vingt
  paramètres : les neuf jeux sont trop hétérogènes (saisonnalité, dérive de
  grammage, cycle de livraison, food cost) pour une signature unique
  lisible. Documenté en tête de `tests/synthetic_data.py`.
- **SYN-D, badge « inhabituel »** : le document dit « un écart de 10x la
  médiane », mais les 4 comptages précédents de ce scénario sont conformes
  par construction (médiane nulle, « 10x zéro » n'a pas de sens). Interprété
  comme « un ordre de grandeur sans ambiguïté au-dessus d'un écart normal »
  (perte à 50% du stock). Documenté dans `tests/synthetic_data.py`.
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

## 3. Trois propositions du document — non arbitrées, donc non construites

Conformément à la règle du document (« aucune ne doit être implémentée sans
validation explicite »), le lot est livré **sans** elles :

- **Journal de décision du modèle** (recommandé, coût faible) — non construit.
- **Écran de comparaison en mode ombre** (recommandé, coût moyen) — non construit.
- **Rejeu historique** — explicitement à reporter par le document lui-même, non construit.

## 4. Critères de sortie du document — état

| Critère | État |
|---|---|
| Générateur écrit, SYN-A à SYN-I déterministes | Fait |
| Tests SYN verts, non-vacuous | Fait |
| F5, F6, F7, F9 implémentées, testées, éteintes par flag | Fait |
| ROB verts si licence OK, sinon absence documentée | Fait — construit sur les deux jeux nommés à l'origine, licence non conforme mais dérogation explicite du porteur du projet (§2) |
| NR-01 à NR-18 verts | Vert — aucun fichier v1 modifié par ce lot, hors ajout de colonnes optionnelles sur `Ingredient`/`Settings` |
| Aucun changement visible pour un utilisateur | Vrai — aucun routeur, gabarit ou test HTTP n'expose F5/F6/F7/F9 |
| Rapport de sortie | Ce document |

## 5. Ce qui reste avant un pilote réel

- Obtenir ou faire confirmer `specs-v2-ia-plan-test.md` pour vérifier que
  les gates/seuils choisis ici (§2) correspondent aux specs réelles.
- Statuer sur les 3 propositions (§3).
- ROB : la dérogation à la vérification de licence (§2) couvre l'usage
  actuel (tests locaux, jamais commité ni redistribué). Toute évolution
  vers une redistribution ou un usage commercial de ces deux jeux
  précisément mériterait une revérification, pas une simple reconduction
  de cette dérogation.
- Activer les feature flags un par un, sur les vraies données du pilote,
  seulement une fois IA-01 à IA-10 (les tests sur données réelles, pas SYN)
  au vert pour la fonctionnalité concernée — c'est le seul gate d'activation
  qui compte (tableau §0 de `docs/IA scope.md`).

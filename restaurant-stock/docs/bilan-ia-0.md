# Bilan — Lot IA-0

Périmètre : `docs/IA scope.md` (« Lot IA-0 » + extension F10-F19). Sept
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

Suite de tests : **220 → 262**, toujours au vert à chaque commit. Chaque
fonctionnalité prouvée sur ses jeux SYN avant d'être committée, chaque test
vérifié non-vacuous (logique cassée volontairement, confirmé que le test
concerné échoue, restauré) — pas seulement « ça passe ».

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
- **ROB non fait — bloqué, pas juste reporté.** Deux blocages concrets :
  aucun identifiant API Kaggle disponible dans cet environnement pour
  télécharger les jeux, et la page Kaggle est une SPA JavaScript dont
  `WebFetch` ne peut pas extraire la licence affichée (rendue côté client).
  La règle du document (« vérifier la licence avant ingestion, ne pas
  utiliser si elle n'autorise pas clairement l'usage ») ne peut donc pas
  être respectée sans intervention humaine : soit fournir les deux CSV
  directement, soit confirmer une licence compatible après vérification
  manuelle sur kaggle.com. Sans ROB, SYN reste suffisant pour prouver la
  justesse du code (tableau §0 du document) — seule la robustesse face à de
  la donnée réelle sale n'est pas couverte.

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
| ROB verts si licence OK, sinon absence documentée | Absence documentée (§2) |
| NR-01 à NR-18 verts | Vert — aucun fichier v1 modifié par ce lot, hors ajout de colonnes optionnelles sur `Ingredient`/`Settings` |
| Aucun changement visible pour un utilisateur | Vrai — aucun routeur, gabarit ou test HTTP n'expose F5/F6/F7/F9 |
| Rapport de sortie | Ce document |

## 5. Ce qui reste avant un pilote réel

- Obtenir ou faire confirmer `specs-v2-ia-plan-test.md` pour vérifier que
  les gates/seuils choisis ici (§2) correspondent aux specs réelles.
- Statuer sur les 3 propositions (§3).
- ROB : fournir les CSV ou confirmer la licence (§2).
- Activer les feature flags un par un, sur les vraies données du pilote,
  seulement une fois IA-01 à IA-10 (les tests sur données réelles, pas SYN)
  au vert pour la fonctionnalité concernée — c'est le seul gate d'activation
  qui compte (tableau §0 de `docs/IA scope.md`).

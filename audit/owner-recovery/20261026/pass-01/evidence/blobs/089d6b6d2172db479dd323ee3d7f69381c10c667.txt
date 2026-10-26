# Plan de feature — Lot IA-0 (F5, F6, F7, F9)

> Déplacé depuis `docs/IA scope.md` lors de la mise en place de
> `docs/context-strategy.md`. Contenu inchangé, seul l'emplacement change —
> ceci reste la note de transmission d'origine du lot IA-0.

# # Note de transmission — Lot IA-0

À lire avant `lot-ia-0-jeux-donnees-test.md`.

## Où on en est

La V1.2 (refonte UX/UI) est terminée sur tous les écrans sauf le comptage actif. 220 tests verts. Le pilote n'a pas commencé : aucune donnée réelle n'existe.

Les fonctionnalités IA de la V2 (F5 à F9, spécifiées dans `specs-v2-ia-plan-test.md`) sont gatées par des données du pilote. Ce lot permet de les **écrire et les prouver dès maintenant** sur des données contrôlées, sans rien activer.

## Ce qui est demandé

1. Un générateur de jeux de données synthétiques paramétré, à graine fixe.
2. Neuf jeux (SYN-A à SYN-I), chacun avec une vérité terrain connue et interrogeable par les tests.
3. L'implémentation de F5, F6, F7, F9, prouvée sur ces jeux, **toutes derrière un feature flag éteint**.
4. Une suite de robustesse (ROB) sur deux jeux publics externes, sous réserve de licence.

## Ce qui ne doit surtout pas être fait

- **Activer une fonctionnalité IA pour un utilisateur.** Tout reste éteint à la sortie de ce lot.
- **Utiliser un résultat obtenu sur données externes pour justifier une décision métier** — activation, calibrage de seuil, argument de performance. Les jeux externes testent que le code ne casse pas, rien d'autre. La règle est détaillée en section 3.1 du document principal ; elle doit apparaître en commentaire dans le fichier de tests concerné.
- **Entraîner quoi que ce soit sur des données externes**, même « pour initialiser ».
- **Toucher F8** (import assisté) : il attend un vrai export de caisse du restaurant pilote, pas des données de test.
- **Toucher l'écran de comptage actif** : il reste hors périmètre, il aura son propre lot.

## Trois propositions à arbitrer avant de commencer

Détaillées en section 5 du document principal. Elles ne sont pas dans le périmètre par défaut — me dire lesquelles retenir :

- **Journal de décision du modèle** (recommandé, coût faible) : tracer chaque sortie IA avec ses entrées et la règle appliquée, pour pouvoir reconstituer un comportement bizarre signalé par le pilote.
- **Écran de comparaison en mode ombre** (recommandé, coût moyen) : voir côte à côte règle v1 et F6 sur l'historique, réservé à l'équipe projet.
- **Rejeu historique** (à reporter) : estimer a posteriori l'économie qu'aurait générée l'IA. Fort intérêt commercial, mais risque de présenter un chiffre rétrospectif comme une promesse. Pas maintenant.

## Ordre recommandé

Générateur et jeux d'abord (rien n'est testable sans), puis F5 (la fonctionnalité à plus forte valeur démontrable), F6 en mode ombre, F7 qui en dépend, F9 en parallèle, ROB en dernier.

## Attendu en sortie

Un rapport dans le format habituel, précisant pour chaque fonctionnalité ce qui est prouvé sur données contrôlées et ce qui reste suspendu au pilote. Et, comme d'habitude, tout écart entre ce qui est spécifié et ce qui est implémenté, avec la raison.


Lot IA-0 — Jeux de données de test et implémentation hors ligne des fonctionnalités IA

**Objet** : permettre d'écrire, tester et prouver le code de F5 à F9 **dès maintenant**, sans attendre les données du pilote.
**Ce que ce lot ne fait pas** : activer quoi que ce soit pour un utilisateur réel. Toutes les fonctionnalités restent derrière leur feature flag, éteintes.

**Documents de référence** : `specs-v2-ia-plan-test.md` (specs fonctionnelles F5-F9, gates, tests IA-01 à IA-10). Ce document le complète, ne le remplace pas.

---

## 0. Le raisonnement derrière ce lot

Les fonctionnalités IA de la V2 sont gatées par des données réelles qui n'existent pas encore (≥ 6 semaines de ventes, ≥ 6 comptages du restaurant pilote). Attendre bloquerait des mois de développement pour rien : **l'algorithme peut être écrit et prouvé correct sur des données contrôlées ; seule son activation dépend du pilote.**

La logique est celle d'un test avec réponse connue : on injecte une saisonnalité de facteur exactement 2, on vérifie que le modèle la retrouve à ± 10 %. On injecte une dérive de grammage de 15 %, on vérifie que la proposition de correction tombe à ± 5 % de la valeur injectée. C'est plus rigoureux qu'un test sur données réelles, où la bonne réponse est inconnue.

**Trois catégories de tests, à ne jamais confondre** :

| Catégorie | Source de données | Ce qu'elle prouve | Peut débloquer un gate ? |
|---|---|---|---|
| **SYN** (nouveau) | Jeux synthétiques à réponse connue | L'algorithme calcule juste | Non — prouve la justesse, pas la valeur métier |
| **ROB** (nouveau) | Jeux publics externes réels | Le code tient face à de la donnée sale | **Non, jamais** — voir section 3.1 |
| **IA-01→10** (existant) | Données réelles du pilote | La prévision bat la règle v1 pour ce restaurant | Oui, c'est le seul gate d'activation |

---

## 1. Jeux de données synthétiques (SYN)

### 1.1 Principes de construction
- **Générés par code, jamais commités en fichiers de données.** Un générateur paramétré (graine fixe → même sortie) versionné avec le code, pour qu'un test soit reproductible et qu'on puisse faire varier un paramètre sans régénérer des CSV à la main.
- **Graine fixe obligatoire** : `IA-04` (déterminisme) exige que deux exécutions donnent le même résultat.
- **Chaque jeu déclare sa vérité terrain** : la valeur injectée est accessible au test, qui compare la sortie du modèle à cette valeur.
- **Réalisme minimal** : bruit aléatoire sur chaque valeur (±10 % par défaut), sinon un modèle trivial passerait tous les tests. Un jeu parfaitement régulier ne prouve rien.

### 1.2 SYN-A — Saisonnalité hebdomadaire connue (cible : F6)
- 12 semaines de ventes, restaurant fermé le lundi.
- Facteur par jour injecté : mardi 1,0 / mercredi 1,1 / jeudi 1,2 / vendredi 2,0 / samedi 2,2 / dimanche 0,8.
- Bruit ±10 % par jour.
- **Attendu** : F6 retrouve chaque facteur à ±10 %. Le lundi est détecté comme jour de fermeture et exclu, aucune prévision affichée pour ce jour.

### 1.3 SYN-B — Dérive de grammage (cible : F5)
- Ingrédient « steak haché », fiche technique déclarant 150 g par burger, consommation réelle injectée à 172 g (dérive de +15 %).
- Le burger représente 80 % de la consommation de cet ingrédient (condition ≥ 50 % remplie).
- 6 comptages, ventes variables d'un comptage à l'autre pour créer la corrélation.
- **Attendu** : proposition de correction de grammage entre 163 et 181 g (±5 % de 172). Corrélation calculée ≥ 0,8.

### 1.4 SYN-C — Contre-exemple de dérive (cible : F5, faux positif)
- Même ingrédient utilisé dans 3 plats à parts égales (33 % chacun) — condition des 50 % non remplie.
- Écart réel présent, mais non attribuable à un plat unique.
- **Attendu** : **aucune** proposition de correction, message explicatif affiché. Un modèle qui propose quand même une correction ici échoue le test.

### 1.5 SYN-D — Perte récurrente vs anomalie ponctuelle (cible : F5)
- Ingrédient 1 : écart de 8 % sur 5 comptages consécutifs → attendu badge « perte récurrente », cumul en € exact au centime.
- Ingrédient 2 : 4 comptages conformes puis un écart de 10× la médiane → attendu badge « inhabituel », **pas** « récurrent ».
- Ingrédient 3 : écart de 8 % sur 2 comptages seulement → attendu **aucun badge** (seuil de 3 non atteint).

### 1.6 SYN-E — Sous le gate de données (cible : F5, F6, IA-02)
- 4 semaines de ventes et 3 comptages seulement.
- **Attendu** : règle v1 appliquée, message honnête (« 3 comptages sur 4 nécessaires »), aucune prévision F6 affichée, aucun badge F5.

### 1.7 SYN-F — Données aberrantes (cible : IA-08)
- Jeu SYN-A, plus deux injections : une vente ×100 (erreur de saisie), un comptage à 0 (oubli de saisie).
- **Attendu** : les deux détectés comme anomalies ponctuelles ; la prévision F6 ne bouge pas de plus de ±10 % par rapport au même jeu sans ces aberrations.

### 1.8 SYN-G — Cycle complet de commande (cible : F7)
- Ingrédient tomate : livraisons mardi et vendredi, conservation 5 jours, consommation 2 kg/jour, stock 1 kg, conditionnement 5 kg. On se place un mercredi.
- Variante G2 : heure limite dépassée.
- Variante G3 : conservation 2 jours, livraison tous les 5 jours (fréquence insuffisante).
- **Attendu** : G1 couvre jusqu'à mardi suivant, arrondi au conditionnement, explication cohérente. G2 bascule sur la livraison suivante avec mention. G3 déclenche le plafond péremption + avertissement.

### 1.9 SYN-H — Food cost complet (cible : F9)
- 8 semaines : ventes, prix de vente, réceptions valorisées, 2 comptages encadrants.
- Valeurs choisies pour que le food cost théorique tombe sur un chiffre rond connu (ex. 30,0 %) et le réel sur 32,5 %.
- **Attendu** : les deux calculés à ±0,1 point. L'écart de 2,5 points est relié aux écarts F5.

### 1.10 SYN-I — Cold start (nouveau, non couvert par les specs V2)
- Nouveau plat ajouté en semaine 9 d'un historique de 12, utilisant un ingrédient existant.
- **Attendu** : la prévision de l'ingrédient continue de fonctionner (elle est au niveau ingrédient), avec mention « nouveau plat depuis le … : historique partiel ». Aucune extrapolation silencieuse sur les 8 semaines où le plat n'existait pas.

---

## 2. Générateur : exigences

- Interface unique paramétrée : nombre de semaines, facteurs par jour, jours de fermeture, niveau de bruit, dérives injectées, aberrations injectées, graine.
- Sortie : objets métier de l'application (ventes, fiches, comptages, réceptions) directement, **et** un export CSV équivalent pour tester le parseur d'import de bout en bout.
- Chaque jeu expose sa vérité terrain sous une forme interrogeable par les tests.
- Le générateur est du code de test, jamais importé par le code applicatif.

---

## 3. Suite de robustesse sur données externes (ROB)

### 3.1 Règle absolue
**Aucun résultat obtenu sur un jeu externe ne peut déclencher, justifier ou calibrer une décision métier.** Ni activer une fonctionnalité, ni ajuster un seuil, ni servir d'argument commercial.

Raison : une boulangerie d'Édimbourg ou une autre boulangerie française n'a ni la carte, ni la clientèle, ni le quartier du restaurant pilote. Prédire correctement ses ventes ne prouve rien sur Le Bistrot — c'est aussi peu transférable que de prédire les courses d'une personne à partir de celles de son voisin. Le principe des specs V2 (« aucune donnée externe ») reste entier : ces jeux testent le **code**, pas le **métier**.

Cette règle doit être écrite en commentaire en tête du fichier de tests ROB, pour qu'un futur lot ne soit pas tenté de s'en servir comme preuve de performance.

### 3.2 Ce que ROB teste réellement
Face à de la donnée réelle et sale, que du synthétique propre ne reproduit jamais :
- Le parseur d'import ne plante pas et signale proprement ce qu'il ne comprend pas.
- Aucune sortie aberrante (valeur négative impossible, division par zéro, quantité infinie).
- Les performances tiennent sur un volume réel (des dizaines de milliers de lignes).
- Les caractères accentués, les noms de produits en français, les formats de date réels passent.

### 3.3 Jeux retenus
| Jeu | Contenu | Ce qu'il apporte |
|---|---|---|
| *French bakery daily sales* (Kaggle) | ~234 000 lignes, 21 mois, boulangerie française réelle, noms de produits en français, saisonnalités hebdo et annuelle | Volume réel + texte français réel pour le parseur |
| *Transactions from a bakery* (Kaggle) | ~21 000 lignes, avec saleté documentée : doublons, lignes « Adjustment » et « NONE », libellé ambigu « Afternoon with the baker » | Cas sales qu'on ne pense jamais à injecter soi-même |

**À faire avant ingestion** : vérifier la licence de chaque jeu. Si elle n'autorise pas clairement l'usage envisagé, ne pas l'utiliser — la suite SYN suffit à valider la justesse, ROB n'est qu'un durcissement.

### 3.4 Cas de test ROB
- **ROB-01** : import du jeu boulangerie française → aucune exception, rapport de lignes non interprétées cohérent.
- **ROB-02** : accents et noms français → lus correctement, aucun caractère cassé.
- **ROB-03** : doublons et lignes « Adjustment » du second jeu → signalés, non silencieusement ingérés.
- **ROB-04** : pipeline complet sur ~234 000 lignes → pas de dépassement mémoire, temps mesuré et journalisé.
- **ROB-05** : sorties du modèle sur ces données → aucune valeur aberrante (négative, infinie, NaN). **Ne vérifie aucune notion de justesse de prévision.**

---

## 4. Ordre de travail recommandé

1. Générateur + SYN-A à SYN-I (rien ne peut être testé sans ça).
2. **F5** (détection d'anomalies et dérive) — la fonctionnalité à plus forte valeur démontrable : c'est celle qui « trouve de l'argent » et fournira l'argument commercial le plus concret.
3. **F6** (prévision par jour de semaine) en mode ombre, jamais visible.
4. **F7** (suggestion intelligente), qui consomme F6.
5. **F9** (food cost) — indépendant, peut se faire en parallèle.
6. **ROB** en dernier, une fois le pipeline stable.
7. **F8** (import assisté) reste hors de ce lot : il attend un vrai export POS, pas des données de test.

Chaque fonctionnalité derrière son feature flag, éteinte par défaut. Aucun changement visible pour un utilisateur à l'issue de ce lot.

---

## 5. Suggestions non demandées, à arbitrer

Trois propositions qui dépassent le périmètre strict. Aucune ne doit être implémentée sans validation explicite.

### 5.1 Journal de décision du modèle (recommandé)
Chaque fois qu'une fonctionnalité IA produit une sortie, journaliser : les entrées utilisées, la règle appliquée, le résultat, et si le gate était franchi. Sans ça, le jour où le pilote dira « l'appli m'a proposé une quantité absurde », on ne pourra pas reconstituer pourquoi.
**Coût** : faible. **Valeur** : très forte au moment du pilote. C'est celle des trois que je recommande le plus.

### 5.2 Écran de comparaison en mode ombre (recommandé)
Un écran réservé à l'équipe projet (pas au restaurateur) montrant, côte à côte, ce qu'aurait dit la règle v1 et ce que dit F6, sur l'historique disponible. Rend le mode ombre (IA-05) lisible sans avoir à lire des logs.
**Coût** : moyen. **Valeur** : c'est l'outil qui servira à décider si on bascule.

### 5.3 Rejeu historique (« et si on avait activé plus tôt ? »)
Rejouer l'historique complet en simulant une activation à une date passée, pour estimer l'économie qu'aurait générée F5/F7. Excellent argument commercial pour ta sœur — mais **dangereux** : c'est un chiffre a posteriori, facile à présenter comme une promesse. À n'envisager qu'avec une formulation prudente, après le pilote, jamais avant.
**Coût** : moyen. **Valeur commerciale** : forte. **Risque** : réel.

### 5.4 Explicitement écarté
Entraîner quoi que ce soit sur les jeux externes, même « pour initialiser » — contraire à la section 3.1 et au principe des specs V2. Un modèle pré-entraîné sur une boulangerie n'aide pas un bistrot, et rend la recommandation inexplicable, ce que le projet refuse depuis le début.

---

## 6. Critères de sortie du lot

- Générateur écrit, tous les jeux SYN-A à SYN-I produits et déterministes (même graine → même sortie).
- Tests SYN verts pour chaque fonctionnalité implémentée, chacun prouvé non-vacuous (échoue sur l'ancien code, passe sur le nouveau).
- F5, F6, F7, F9 implémentées, testées, **toutes éteintes par feature flag**.
- ROB verts si les licences le permettent ; sinon, absence documentée.
- NR-01 à NR-18 verts — aucune fonctionnalité IA ne doit toucher la boucle v1.
- Aucun changement visible dans l'application pour un utilisateur.
- Rapport de sortie précisant, pour chaque fonctionnalité, ce qui est prouvé sur données contrôlées et ce qui reste suspendu au pilote.

---

## 7. Hypothèses et angles morts

- Les valeurs injectées dans les jeux SYN (facteur 2 le vendredi, dérive de 15 %, etc.) sont des ordres de grandeur plausibles, non observés dans un vrai restaurant. Un modèle qui les retrouve prouve qu'il calcule juste, pas que ces phénomènes existent à cette amplitude en cuisine.
- Le bruit de ±10 % est arbitraire. Si le pilote révèle une variabilité bien supérieure, les seuils de tolérance des tests SYN devront être revus — et peut-être les seuils métier avec.
- SYN ne peut pas reproduire ce qu'on n'a pas imaginé. C'est la raison d'être de ROB, et surtout du pilote.
- Un code prouvé juste sur SYN peut rester inutile en pratique : la justesse du calcul ne dit rien de la valeur perçue par un chef. Seul le pilote tranchera ça.
- Ce lot augmente la surface de code non utilisée en production. Si le pilote traîne plusieurs mois, ce code vieillira sans utilisateur — risque assumé, à surveiller.


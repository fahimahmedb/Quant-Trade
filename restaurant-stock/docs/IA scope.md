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


# Extension IA — Fonctionnalités F10 à F19

**Complète** `specs-v2-ia-plan-test.md` (F5-F9) et `lot-ia-0-jeux-donnees-test.md` (jeux de test).
**Ne remplace rien.** Les principes de la section 1 des specs V2 (explicabilité, humain décisionnaire, gate de données, mode ombre, zéro saisie obligatoire, feature flags, activation par ingrédient) s'appliquent intégralement à tout ce qui suit.

---

## 0. Avertissement avant la liste

**Plus de fonctionnalités IA n'est pas automatiquement mieux.** Le risque réel de ce document est de produire une application que personne ne comprend, dans un segment dont la contrainte n°1 est la simplicité d'usage (§4 des instructions projet : « un outil trop lourd sera abandonné, quelle que soit la qualité de l'IA derrière »).

Mon avis, à contester : **deux de ces dix fonctionnalités valent plus que les huit autres réunies.**

- **F11 (comptage tournant intelligent)** — c'est la seule fonctionnalité IA du projet qui s'attaque directement à la friction n°1 identifiée depuis le brief initial. Toutes les autres améliorent ce que le gérant *lit* ; celle-ci réduit ce que le chef *fait*.
- **F12 (alerte de marge érodée)** — protège directement la rentabilité, avec un argument commercial immédiatement chiffrable pour ta sœur.

Les huit autres sont réelles mais secondaires. Elles sont spécifiées ici pour être prêtes, pas pour être toutes construites.

---

## 1. F10 — Criticité des ingrédients (classification ABC)

**Objectif** : déterminer quels ingrédients méritent l'attention, et lesquels n'en méritent presque pas.
**Pourquoi c'est un socle** : F11 en dépend entièrement, et F5 gagne à ne remonter des badges que sur ce qui compte.

**Gate** : ≥ 4 semaines de ventes. Aucun comptage nécessaire.

**Règles métier**
- Valeur annuelle consommée par ingrédient = consommation moyenne quotidienne × prix courant × 365.
- Classement Pareto : classe A = les ingrédients cumulant 80 % de la valeur ; classe B = les 15 % suivants ; classe C = le reste.
- Un facteur de **volatilité** s'ajoute : coefficient de variation des écarts constatés (si ≥ 3 comptages). Un ingrédient de classe B très volatil remonte en A.
- Affichage : jamais les lettres A/B/C seules (jargon logistique). Formulation métier : « 8 ingrédients représentent 80 % de votre coût matière ».
- Le gérant peut forcer la classe d'un ingrédient manuellement (ex. produit sensible HACCP), le choix manuel prime toujours.

**Critères d'acceptation**
- AC-F10-1 : sur SYN-J (voir §11), la classification retrouve exactement la répartition injectée.
- AC-F10-2 : un ingrédient sans historique suffisant est classé « non déterminé », jamais C par défaut.
- AC-F10-3 : le forçage manuel survit à un recalcul.

**Cas de test** : TC-F10-01 répartition nominale ; TC-F10-02 ingrédient à forte valeur mais consommation nulle depuis 3 semaines → signalé « dormant » et non A ; TC-F10-03 ingrédient volatil de classe B → remonte en A avec explication ; TC-F10-04 tous les ingrédients de même valeur → répartition dégradée proprement, pas d'erreur.

---

## 2. F11 — Comptage tournant intelligent ⭐

**Objectif** : arrêter de compter 40 ingrédients à chaque fois. Compter chaque jour les 8 qui bougent et qui coûtent, le reste une fois par semaine ou par mois.
**Valeur segment** : c'est le concept d'inventaire tournant (§5 des instructions projet), rendu automatique. Sur un comptage de 40 lignes à 15 minutes, une session ciblée de 10 lignes tombe sous les 5 minutes. **C'est la fonctionnalité qui décide si l'outil est utilisé tous les jours ou abandonné au bout de trois semaines.**

**Gate** : F10 actif (≥ 4 semaines de ventes) et ≥ 3 comptages complets.

**Règles métier**
- Chaque ingrédient reçoit une **fréquence de comptage suggérée** : quotidienne, hebdomadaire, ou mensuelle.
- Calcul : croisement de la criticité (F10) et de la stabilité (variance historique des écarts). Fort coût + écarts instables → quotidien. Faible coût + toujours conforme → mensuel.
- **Un comptage complet reste imposé périodiquement** (défaut : toutes les 4 semaines, réglable). Sans ça, un ingrédient classé « mensuel » à tort dériverait sans jamais être détecté. Non négociable : c'est le garde-fou qui empêche l'optimisation de créer un angle mort.
- L'écran de comptage propose par défaut la **session du jour** (les ingrédients dus), avec un accès permanent au comptage complet en un geste.
- La suggestion est modifiable : le chef peut ajouter ou retirer un ingrédient de la session, et son choix est mémorisé.
- Explication systématique : « Farine — comptée chaque semaine : conforme sur les 6 derniers comptages, 4 % de votre coût matière ».
- Un ingrédient qui déclenche un badge F5 (perte récurrente ou anomalie) **repasse automatiquement en quotidien** jusqu'à retour à la normale sur 3 comptages.

**Critères d'acceptation**
- AC-F11-1 : sur SYN-K, la session du jour contient exactement les ingrédients attendus.
- AC-F11-2 : le comptage complet reste accessible en un geste depuis l'écran de comptage.
- AC-F11-3 : après 4 semaines sans comptage complet, l'application le réclame explicitement et ne propose plus de session partielle tant qu'il n'est pas fait.
- AC-F11-4 : un ingrédient avec badge F5 apparaît dans la session du jour même s'il était classé mensuel.
- AC-F11-5 : le temps de comptage moyen (indicateur existant) doit baisser après activation — mesuré, pas supposé.

**Cas de test** : TC-F11-01 à 05 (les AC) ; TC-F11-06 nouvel ingrédient → quotidien par défaut jusqu'à avoir un historique ; TC-F11-07 le chef retire un ingrédient de la session → mémorisé, mais réintégré si un badge F5 apparaît ; TC-F11-08 tous les ingrédients classés mensuels → la session du jour est vide, message clair proposant le comptage complet ; TC-F11-09 rythme de comptage irrégulier (rien pendant 3 semaines) → recalcul cohérent, pas de division par zéro.

**Angle mort** : cette fonctionnalité suppose qu'un chef acceptera de ne pas tout compter. Certains voudront tout compter par principe de contrôle. Le comptage complet doit rester à un geste, jamais enfoui.

---

## 3. F12 — Alerte de marge érodée ⭐

**Objectif** : détecter qu'un plat n'est plus rentable parce que ses ingrédients ont augmenté, et le dire avant que la marge ne soit mangée.
**Valeur segment** : les mercuriales bougent chaque semaine, les cartes sont réimprimées une fois par an. C'est l'écart le plus silencieux et le plus coûteux du métier. **Implication commerciale directe** : « l'outil vous a dit que votre burger avait perdu 4 points de marge en 3 mois » est l'argument le plus concret que ta sœur pourra utiliser en rendez-vous.

**Prérequis** : F1 (historique des prix, déjà livré) et le prix de vente saisi sur la fiche plat (U7 du plan UX, non encore fait — **dépendance à signaler**).

**Gate** : ≥ 2 relevés de prix sur au moins un ingrédient du plat. Pas de gate de comptage.

**Règles métier**
- Coefficient multiplicateur par plat = prix de vente HT / coût matière. Recalculé à chaque réception qui modifie un prix.
- Alerte si le coefficient passe sous un seuil réglable (défaut : 3,0) **ou** s'il a baissé de plus de 10 % sur 90 jours.
- L'alerte décompose : « Burger maison — coût matière passé de 2,32 € à 2,71 € en 2 mois (+17 %), dont steak haché +0,28 €. Coefficient tombé de 3,4 à 2,9. »
- **Prix de vente suggéré**, jamais appliqué : celui qui restaurerait le coefficient d'origine, avec la mention explicite que c'est un calcul, pas une recommandation commerciale (le prix psychologique et la concurrence locale ne sont pas dans l'outil).
- Vue « impact d'un ingrédient » : quand un prix bouge, la liste des plats touchés et de combien.

**Critères d'acceptation**
- AC-F12-1 : sur SYN-L, l'alerte se déclenche au franchissement exact du seuil, pas avant.
- AC-F12-2 : un plat sans prix de vente est exclu, avec mention, sans bloquer les autres.
- AC-F12-3 : la décomposition attribue correctement la hausse à chaque ingrédient.
- AC-F12-4 : le prix suggéré restaure le coefficient d'origine au centime.
- AC-F12-5 : aucun prix de vente n'est jamais modifié automatiquement.

**Cas de test** : TC-F12-01 à 05 (les AC) ; TC-F12-06 hausse puis baisse revenant au point de départ → alerte levée puis retirée ; TC-F12-07 ingrédient partagé par 5 plats → les 5 listés avec impact différencié ; TC-F12-08 hausse de 40 % sur un ingrédient représentant 2 % du coût du plat → pas d'alerte (impact réel négligeable).

---

## 4. F13 — Prévision de mise en place

**Objectif** : répondre à « combien je prépare demain », pas seulement « combien je commande ».
**Valeur segment** : sur carte fixe, la sur-préparation de sauces, garnitures et fonds est une source de gaspillage quotidienne, distincte de la sur-commande.

**Gate** : F6 actif pour les ingrédients concernés.

**Règles métier**
- Pour les ingrédients marqués « préparé en interne » (nouveau champ optionnel), prévision de la quantité à produire pour le service du lendemain, ou pour les N jours de conservation de la préparation.
- Tient compte du reste en stock de la préparation précédente.
- Affichage sous forme de liste de production imprimable ou consultable en cuisine.
- Ajustement manuel systématiquement possible, avec mémorisation de l'écart entre prévision et décision réelle (indicateur de confiance).

**Critères d'acceptation** : AC-F13-1 aucun ingrédient marqué préparé → fonctionnalité invisible ; AC-F13-2 sur SYN-A, la quantité prévue correspond à la consommation attendue du jour ±10 % ; AC-F13-3 stock de préparation existant déduit.

**Cas de test** : TC-F13-01 à 03 (les AC) ; TC-F13-04 jour de fermeture le lendemain → aucune production suggérée ; TC-F13-05 conservation de 3 jours → production couvrant 3 jours, pas 1.

---

## 5. F14 — Risque de péremption

**Objectif** : signaler le stock qui ne sera pas consommé à temps, **sans exiger la saisie d'une DLC par lot**.

**Gate** : F6 actif OU moyenne glissante v1 disponible, et durée de conservation renseignée (champ optionnel déjà prévu en F7).

**Règles métier**
- Pour chaque ingrédient : à la consommation prévue, le stock actuel sera-t-il écoulé avant la fin de sa durée de conservation ?
- Si non : « Il vous restera ~2,1 kg de tomates dans 5 jours, au-delà de leur conservation habituelle — environ 6,30 € ».
- Suggestion d'action limitée à ce que l'outil sait faire : réduire la prochaine commande. **Pas** de suggestion de plat du jour ou de promotion — ce serait sortir du domaine de compétence de l'outil et de son explicabilité.
- Se combine avec le plafond péremption de F7 : ici c'est le stock déjà présent, là c'est la commande à venir.

**Critères d'acceptation** : AC-F14-1 aucune durée de conservation renseignée → fonctionnalité silencieuse ; AC-F14-2 sur SYN-M, l'alerte se déclenche au bon jour ; AC-F14-3 le montant en euros est exact.

**Cas de test** : TC-F14-01 à 03 ; TC-F14-04 consommation nulle sur l'ingrédient → alerte immédiate, pas de division par zéro ; TC-F14-05 réception entre-temps → recalcul.

---

## 6. F15 — Contrôle d'intégrité des ventes importées

**Objectif** : détecter qu'un import de ventes est incomplet ou anormal **avant** qu'il ne corrompe le stock théorique et, en cascade, toutes les prévisions.
**Pourquoi c'est important** : Claude Code l'a signalé lui-même — un historique construit sur un import mal calé produirait des recommandations fausses avec assurance. C'est le garde-fou de tout l'édifice.

**Gate** : ≥ 3 semaines d'imports pour établir une normale.

**Règles métier**
- À chaque import, comparaison au profil habituel : nombre de lignes, chiffre d'affaires, nombre de plats distincts, pour ce jour de semaine.
- Alerte non bloquante si écart > 40 % (réglable) : « Ce fichier contient 12 ventes pour un vendredi, contre 80 habituellement. Import incomplet ? »
- **Détection de jours manquants** : un trou dans l'historique est signalé explicitement (« aucune vente importée pour le 12 septembre — jour de fermeture ou import oublié ? ») avec la possibilité de marquer le jour comme fermé.
- Détection de doublon de fichier déjà prévue en F8, conservée ici.
- L'import reste toujours possible : l'outil alerte, ne bloque pas.

**Critères d'acceptation** : AC-F15-1 import à −80 % du volume habituel → alerte, import possible après confirmation ; AC-F15-2 trou de 2 jours → signalé, marquable comme fermeture ; AC-F15-3 sous le gate → aucune alerte, aucun faux positif.

**Cas de test** : TC-F15-01 à 03 ; TC-F15-04 premier import → aucune alerte ; TC-F15-05 restaurant en congés 2 semaines → détecté comme période exceptionnelle, proposé à l'exclusion (lien avec F6) ; TC-F15-06 jour habituellement fermé → pas d'alerte de trou.

---

## 7. F16 — Consolidation de commande par fournisseur

**Objectif** : passer d'une liste de suggestions par ingrédient à une commande par fournisseur, respectant les minimums.
**Valeur segment** : les minimums de commande et le franco de port sont une contrainte quotidienne (§4 des instructions projet). Une suggestion qui ignore le franco fait payer des frais de port inutiles.

**Nouvelles données (optionnelles)** : fournisseur par ingrédient (le champ fournisseur existe déjà sur les réceptions — le rattacher à l'ingrédient), montant de franco de port, minimum de commande.

**Gate** : aucun gate de données. Purement combinatoire.

**Règles métier**
- Les suggestions F7 sont regroupées par fournisseur, avec le total de la commande.
- Si le total est sous le franco : « 42 € sur 80 € de franco. Ajouter 38 € ou reporter à jeudi ? » avec proposition d'anticiper les ingrédients du même fournisseur bientôt sous seuil.
- **Jamais de sur-commande automatique pour atteindre un franco** : la proposition d'ajout est explicite et le plafond péremption de F7 s'applique toujours à chaque ligne ajoutée.
- Export de la commande en texte simple, copiable dans un email ou un SMS au fournisseur. Pas d'envoi automatique (principe 2).

**Critères d'acceptation** : AC-F16-1 aucun fournisseur renseigné → affichage F7 inchangé ; AC-F16-2 total sous franco → proposition d'ajout dont chaque ligne respecte le plafond péremption ; AC-F16-3 aucun envoi automatique, dans aucun chemin de code.

**Cas de test** : TC-F16-01 à 03 ; TC-F16-04 ingrédient sans fournisseur → groupe « non attribué », pas d'erreur ; TC-F16-05 franco atteignable uniquement en dépassant la péremption → l'outil dit qu'il ne peut pas et propose le report.

---

## 8. F17 — Diagnostic de cause d'écart

**Objectif** : F5 dit *qu'il y a* un écart récurrent. F17 propose *pourquoi*.

**Gate** : ≥ 6 comptages, et ≥ 3 écarts avec motif saisi (le champ motif existe depuis le MVP).

**Règles métier**
Croisement de signaux internes uniquement, pour proposer une hypothèse — **jamais une conclusion** :
- Écarts concentrés sur les jours de forte affluence → « portionnage sous le rush ? »
- Écarts concentrés sur une zone de stockage → « conservation ou casse dans [zone] ? »
- Écart apparu après une date précise → « quelque chose a changé le [date] : nouveau fournisseur, nouvelle équipe, recette modifiée ? »
- Écart proportionnel aux ventes d'un plat → renvoi vers la proposition de dérive de fiche technique (F5).
- Formulation systématiquement interrogative. L'outil n'a aucun moyen de savoir ce qui se passe en cuisine ; il signale une corrélation, le chef sait l'expliquer.

**Critères d'acceptation** : AC-F17-1 sur SYN-N (écarts injectés uniquement le week-end), l'hypothèse « jours de forte affluence » est proposée ; AC-F17-2 aucun motif jamais saisi → fonctionnalité silencieuse, pas d'hypothèse hasardeuse ; AC-F17-3 toute hypothèse est formulée sous forme de question.

**Cas de test** : TC-F17-01 à 03 ; TC-F17-04 écarts aléatoires sans structure → aucune hypothèse proposée (le test échoue si l'outil invente une corrélation) ; TC-F17-05 deux causes plausibles simultanées → les deux proposées, pas de choix arbitraire.

---

## 9. F18 — Indicateur de confiance des prévisions

**Objectif** : montrer au gérant à quel point les prévisions ont été justes, pour que la confiance se construise sur des faits.
**Lien avec les principes** : §8 des instructions projet — « la confiance se construit du semi-automatique vers l'automatique ». Cette fonctionnalité est la mesure de cette progression.

**Gate** : ≥ 4 semaines de prévisions produites (y compris en mode ombre).

**Règles métier**
- Pour chaque ingrédient avec F6 actif : écart moyen entre prévision et réel sur les 4 dernières semaines, en clair (« prévisions justes à ±8 % en moyenne »).
- Comparaison permanente avec la règle v1, y compris après bascule : si F6 se dégrade sous la v1 sur 3 semaines, **retour automatique à la v1** pour cet ingrédient, avec notification à l'équipe projet. C'est le pendant runtime du test IA-06.
- Aucune métrique statistique jargonnante à l'écran (pas de MAPE, pas de RMSE) — l'équipe projet y a accès, pas le restaurateur.

**Critères d'acceptation** : AC-F18-1 la dégradation sur 3 semaines déclenche le retour à v1 ; AC-F18-2 le retour est journalisé ; AC-F18-3 aucun terme statistique visible côté restaurateur.

**Cas de test** : TC-F18-01 à 03 ; TC-F18-04 dégradation sur 2 semaines seulement → pas de retour ; TC-F18-05 retour à v1 puis réamélioration → réactivation possible, pas de bascule en boucle (hystérésis obligatoire).

---

## 10. F19 — Socle de l'effet réseau (structure seulement, aucune activation)

**Objectif** : préparer, sans l'activer, la comparaison anonymisée entre établissements évoquée dans la vision du projet.

**Statut** : **conception du modèle de données uniquement.** Aucune fonctionnalité visible, aucun transfert de données, aucune agrégation réelle tant qu'il n'y a qu'un seul restaurant — comparer un établissement à lui-même n'a aucun sens.

**Ce qui est demandé dans ce lot**
- Prévoir dans le schéma la possibilité d'exporter des métriques agrégées et non identifiantes (food cost moyen par catégorie d'ingrédient, écart moyen, saisonnalité hebdomadaire normalisée) — **sans les exporter**.
- Aucune donnée nominative, aucun nom de plat propriétaire, aucun prix fournisseur négocié dans ce périmètre : ce sont des informations concurrentiellement sensibles.
- Consentement explicite et révocable prévu dès la conception, jamais activé par défaut.

**Implication commerciale** : quand plusieurs restaurants seront actifs, « votre food cost est à 32 % contre 29 % en médiane sur des établissements comparables » sera un argument fort. Mais c'est un argument de V3 : le promettre avant d'avoir les données serait une promesse en l'air.

**Implication juridique, non tranchée** : dès qu'il y a mutualisation de données entre établissements, un cadre RGPD et contractuel est nécessaire (finalité, base légale, information, réversibilité). **À faire valider par un juriste avant toute activation** — je ne suis pas en mesure de trancher ce point, et il ne doit pas être traité comme un détail technique.

---

## 11. Jeux de données synthétiques additionnels

À ajouter au générateur du lot IA-0, mêmes principes (graine fixe, vérité terrain interrogeable, bruit ±10 %).

| Réf | Contenu | Cible |
|---|---|---|
| SYN-J | 20 ingrédients, répartition de valeur Pareto connue (3 ingrédients = 80 %) | F10 |
| SYN-K | 20 ingrédients, moitié stables / moitié volatils, 8 comptages | F11 |
| SYN-L | Plat à 4 ingrédients, hausse progressive injectée faisant passer le coefficient de 3,4 à 2,8 sur 90 jours | F12 |
| SYN-M | Stock à rotation lente, conservation 5 jours, consommation connue | F14 |
| SYN-N | Écarts injectés uniquement les vendredis et samedis | F17 |
| SYN-O | Historique d'imports avec un jour manquant, un jour à −80 %, une période de congés de 2 semaines | F15 |

---

## 12. Séquencement recommandé

| Priorité | Fonctionnalités | Justification |
|---|---|---|
| **1** | F10 puis F11 | F11 est la seule fonctionnalité IA qui réduit le travail du chef plutôt que d'enrichir la lecture du gérant. F10 en est le prérequis. |
| **2** | F12 | Valeur métier et commerciale la plus directe. Dépend de U7 (prix de vente sur fiche), à faire avant. |
| **3** | F15 | Garde-fou : protège la justesse de tout le reste. Peu coûteux. |
| **4** | F18 | Sécurise la bascule de F6. À faire avant toute activation réelle, pas après. |
| **5** | F14, F16 | Valeur réelle, dépendantes de champs optionnels que le pilote renseignera peut-être. |
| **6** | F17, F13 | Confort. À construire seulement si le pilote les demande. |
| **7** | F19 | Structure de données seulement. Aucune activation avant un second restaurant et une validation juridique. |

---

## 13. Ce que je continue d'écarter

| Idée | Raison |
|---|---|
| Suggestion de plat du jour / promotion anti-gaspillage | Sort du domaine de compétence de l'outil : ça touche à la carte, au prix psychologique, à l'identité du restaurant. L'outil signale le risque (F14), le chef décide. |
| Prévision par apprentissage automatique sur petites séries | Inchangé depuis les specs V2 : inexplicable, inutile à cette échelle. |
| Signaux externes (météo, événements) | V3 au plus tôt, et seulement si la saisonnalité interne est maîtrisée. |
| Commande envoyée automatiquement au fournisseur | Contraire au principe 2. F16 s'arrête à l'export copiable. |
| Notation ou classement des employés à partir des écarts | Techniquement possible via le champ « comptage par ». **Refusé** : transformerait un outil de gestion en outil de surveillance, détruirait la confiance de l'équipe cuisine et la fiabilité des saisies. À ne jamais implémenter, même sur demande. |

---

## 14. Hypothèses et angles morts

- **Le risque principal de ce document est son volume.** Dix fonctionnalités bien spécifiées peuvent produire une application illisible. La priorisation de la section 12 compte plus que l'exhaustivité des specs.
- F11 suppose qu'un chef acceptera de ne pas tout compter — hypothèse de comportement, non vérifiée. Si le pilote refuse, F11 perd l'essentiel de sa valeur.
- F12 dépend de U7 (prix de vente sur les fiches), non encore implémenté. Sans lui, F12 est inerte.
- F13, F14 et F16 dépendent de champs optionnels. Le principe « zéro saisie obligatoire » garantit qu'ils dégradent proprement, mais garantit aussi qu'ils peuvent rester vides et donc inutiles. À observer au pilote.
- Tous les seuils de ce document (80/15/5 du Pareto, 40 % d'écart d'import, coefficient 3,0, 10 % sur 90 jours) sont des valeurs de départ raisonnées, pas mesurées. À revoir après le pilote.
- F19 comporte une question juridique que je ne peux pas trancher.
# Backlog — Lot IA-2

> Sauvegardé ici dès rédigé (docs/context-strategy.md) plutôt que de rester
> seulement dans l'historique de conversation. Rédigé par Claude Code
> lui-même à partir du contexte métier transmis (économie de la
> restauration indépendante, contraintes opérationnelles, vocabulaire
> sectoriel) et de ce qui existe déjà (Lot IA-0 F5-F9, Lot IA-1 F10-F19,
> `docs/bilan-ia-0.md`, `docs/bilan-ia-1.md`). Spec complète ET backlog en
> un seul document cette fois : contrairement à `backlog-lot-ia-1.md`, qui
> pointait vers `ia-f10-f19.md` déjà rédigé par le porteur du projet, aucun
> détail fonctionnel préexistant n'était disponible ici à séquencer — il a
> fallu le produire.

Aucune ligne de code n'a été écrite pour ce lot. Ce document est un
backlog à transmettre à Claude Code, pas une implémentation.

---

## 0. Ce qui existe déjà, pour ne rien reconstruire

- **Food cost / fiche technique** (F9) : coût matière par plat, à jour à
  chaque changement de prix.
- **Prévision par jour de semaine** (F6, mode ombre) + **suggestion de
  commande** (F7) : saisonnalité hebdomadaire uniquement, aucun signal
  externe (météo, vacances, événements).
- **Écarts et pertes** : détection de dérive de fiche technique (F5),
  classification perte récurrente/inhabituelle (F5), diagnostic de cause
  (F17, hypothèses jour/zone/date/fiche technique) — chacun isolé, aucune
  vue consolidée « combien le gaspillage a coûté ce mois-ci ».
- **Taux d'adoption des suggestions** (`app/services/metrics.py`,
  `suggestion_adoption_stats`) : déjà construit en v1, mais seulement pour
  les suggestions de commande (F7) — aucune autre recommandation IA n'y
  est journalisée.
- **Consolidation fournisseur** (F16) : regroupe les commandes pour
  atteindre un seuil de franco de port. Ne compare PAS les prix entre
  plusieurs fournisseurs d'un même ingrédient — `Ingredient.supplier_name`
  est un champ unique, décision actée au ticket 7 du Lot IA-1 faute de
  cas de test exerçant autre chose.
- **Effet réseau / benchmark inter-restaurants** (F19) : structure de
  données seulement, aucune activation avant un second restaurant et une
  validation juridique (RGPD, mutualisation de données). Inchangé, ne
  pas y retoucher.

---

## 1. Règle de résolution d'ambiguïté

Identique à `backlog-lot-ia-1.md` §2, reconduite telle quelle — elle a
tenu sur les 9 tickets du lot précédent sans jamais nécessiter un retour
au porteur du projet en cours de ticket :

1. Chercher une décision analogue déjà actée dans le projet et la
   réutiliser plutôt qu'en inventer une nouvelle.
2. Préférer la dégradation silencieuse à la supposition : une donnée
   optionnelle manquante laisse la fonctionnalité inerte, jamais une
   valeur devinée à la place.
3. Sur une question de jugement produit ou métier (pas technique) : ne
   pas construire plutôt que deviner. Documenter le point bloquant
   (§7 ci-dessous en liste trois pour ce lot).
4. Sur une question purement technique sans impact métier : trancher et
   documenter, ne pas remonter.

---

## 2. Leçons du Lot IA-1, à appliquer par défaut

Chacune vient d'un bug ou d'un trou de couverture réellement trouvé sur ce
projet pendant le lot précédent (`docs/bilan-ia-1.md`) — pas des principes
abstraits.

- **Un gate de disponibilité ne doit jamais se gater lui-même.** Le
  blocage circulaire de F18 (`backtest_vs_v1` rejouait l'historique via
  `weekday_forecast`, qui refusait de fonctionner pour un ingrédient déjà
  basculé — rendant sa propre réactivation inatteignable) vient d'avoir
  fusionné « le calcul » et « la garde d'accès » dans la même fonction.
  Toute fonction qui (a) sert un usage courant gardé par un gate ET (b)
  sert aussi à rejouer/introspecter ce même système pour DÉCIDER du gate
  doit séparer un cœur de calcul sans garde (`_xxx_core`) que
  l'introspection appelle directement.
- **Une preuve de non-vacuité qui passe sans qu'on y touche est un trou de
  couverture, pas une garantie.** Trouvé trois fois au Lot IA-1 (F12, F16,
  F18, F17) : le premier essai de « casser la règle » ne changeait rien au
  résultat du test, révélant qu'aucun test existant n'isolait ce cas
  précis. Un test ajouté à chaque fois avant de redéclarer la preuve
  valide. Ne jamais interpréter un premier essai de cassure resté sans
  effet comme « la règle est déjà couverte ailleurs ».
- **Un fixture qui satisfait le GATE d'une règle sans atteindre son SEUIL
  peut faire passer un test pour la mauvaise raison.** Le fixture initial
  d'AC-F17-2 (8 écarts, 62,5 % de concentration, sous le seuil de 65 % de
  la règle « affluence ») aurait laissé indistincts « le gate motifs
  bloque bien » et « la concentration était de toute façon insuffisante ».
  Toute règle à seuil doit d'abord être vérifiée empiriquement (script
  autonome) pour confirmer qu'elle se déclencherait SANS le gate testé,
  avant d'écrire un test sur le gate lui-même.
- **Une règle statistique composée (plusieurs conditions indépendantes)
  a besoin d'un contre-exemple PAR condition, pas un seul global.** La
  règle « affluence » de F17 croise concentration ET volume de vente réel
  — un contre-exemple sur la seule concentration (TC-F17-04, écarts
  dispersés) n'aurait jamais détecté la disparition du croisement avec les
  ventes ; un second contre-exemple dédié (écarts concentrés sur le jour
  le plus CREUX) a dû être ajouté.
- **Toute nouvelle colonne NOT NULL sur une table déjà couverte par des
  fixtures SQL brutes (`test_backup.py`, `test_migrations.py` sur
  `ingredients`) casse ces fixtures.** Trouvé au ticket 5 (F18), corrigé
  par anticipation au ticket 9 (F13) avant même de lancer la suite
  complète. Vérifier ces deux fichiers dès qu'une migration ajoute une
  colonne NOT NULL à `ingredients`, avant de considérer un ticket terminé.
- **Un seuil statistique sans valeur donnée par le document ne se devine
  jamais à la table de travail.** Chaque seuil de F17 (concentration,
  part de zone affectée, part « après » une rupture de date) a été
  déterminé par script autonome sur des jeux de données construits pour
  l'occasion, jamais fixé a priori puis vérifié après coup. À reconduire
  pour tout seuil neuf de ce lot (§4).
- **Une surface d'authentification différente exige une exemption de
  middleware différente, jamais une vérification empilée sur la session
  existante.** L'écran de comparaison en mode ombre (`/admin/*`) devait
  être invisible à un restaurateur connecté sur son propre compte — geste
  correct : exempter le préfixe de `RequireLoginMiddleware` et le garder
  par un jeton dédié, jamais ajouter une vérification par-dessus la
  session établissement (qui resterait, elle, une porte d'entrée valide
  pour le restaurateur).

---

## 3. Backlog priorisé

### Ticket 1 — F22, gaspillage consolidé et valorisé ⭐

**Objectif** : répondre à « combien le gaspillage m'a coûté ce mois-ci »,
en euros et en % du CA — aujourd'hui dispersé entre les badges de F5, les
alertes F14 et l'écran d'écarts, sans jamais être additionné. Répond
directement à l'indicateur de succès « réduction du taux de gaspillage »
(double argument économique et RSE pour l'équipe commerciale).

**Gate** : aucun nouveau — agrège des données déjà gatées par F5/F14
chacune de leur côté ; reste inerte (liste vide) tant qu'aucun comptage
n'a produit de perte.

**Règles métier**
- Période glissante (mois calendaire en cours + les 2 précédents, pour une
  tendance) : somme des pertes valorisées, ventilée EXPLIQUÉE (motif
  saisi : casse, périmé, offert) / INEXPLIQUÉE (déjà la distinction de
  F5/`ai_drift._loss_observations` et F17 — jamais un second calcul
  parallèle).
- Rattache chaque perte inexpliquée significative à une hypothèse F17 si
  le gate de F17 est atteint pour l'ingrédient concerné (renvoi, pas de
  second diagnostic).
- Rattache le stock proche péremption non encore perdu (F14) comme
  « gaspillage à venir si rien ne change » — distinct du gaspillage déjà
  constaté, jamais additionné au même total.
- % du CA : perte totale / chiffre d'affaires de la même période (déjà
  calculable depuis les ventes importées).

**Lien commercial** : argument direct et chiffré pour l'équipe
commerciale — « X € de gaspillage identifié sur les 3 derniers mois, soit
Y % du CA », décomposé par cause. À signaler explicitement comme
réutilisable tel quel dans l'argumentaire de vente.

**Décision par défaut** : la fenêtre de 3 mois est une valeur de départ
raisonnée (même principe que les seuils réglables du Lot IA-0/IA-1),
réglable dans `Settings`, jamais une constante figée.

---

### Ticket 2 — F21, menu engineering : RETIRÉ, déjà construit

**Correction, trouvée en relisant le code avant d'implémenter ce ticket**
(pas en le committant tel quel puis en le découvrant après coup) :
`ai_food_cost.popularity_margin_matrix` (F9, Lot IA-0,
docs/feature-plans/ia-f5-f9.md §1.9) fait déjà exactement ce que ce
ticket proposait — quadrants popularité × marge, seuils par MÉDIANE de la
carte (pas de constante absolue), labels en clair (« stars », « à
retravailler », « à pousser », « à questionner »), jamais de suggestion
de retirer un plat. Construire un second calcul aurait dupliqué une
logique déjà testée (SYN-H) plutôt que d'ajouter une valeur réelle.

Seul écart entre ce qui existe et ce ticket : AUCUN écran ne l'expose
(comme la quasi-totalité des fonctionnalités IA du projet — logique
d'abord, écran ensuite, décision constante depuis le Lot IA-0). C'est un
travail d'écran, pas un ticket d'IA — même raisonnement que
`backlog-lot-ia-1.md` §4 pour l'export matrice F9, déjà écarté de ce lot
pour la même raison.

Numérotation des tickets suivants inchangée (pas de renumérotation) pour
ne pas invalider les références déjà faites ailleurs à ce document.

---

### Ticket 3 — F25, indicateur de confiance IA étendu à toutes les recommandations

**Objectif** : `metrics.suggestion_adoption_stats` (v1) ne mesure
aujourd'hui que l'adoption des suggestions de commande (F7). Ce ticket
étend le MÊME mécanisme (`SuggestionDecision` : acceptée/modifiée/rejetée)
à toute recommandation qui appelle une décision humaine — répond
explicitement à l'indicateur de succès « taux d'adoption réel des
recommandations IA par les cuisiniers » (§11 du contexte métier), et
referme le gap documenté au ticket 9 du Lot IA-1 (F13, § « mémorisation
prévision/décision réelle », resté sans spec faute d'AC/TC) en lui donnant
enfin une spécification concrète.

**Gate** : F13 actif pour la mémorisation production ; aucun gate propre à
la vue agrégée elle-même (reste inerte si rien n'est encore décidé).

**Règles métier**
- Première extension concrète : F13 (prévision de mise en place). Quand
  le chef ajuste manuellement la quantité à produire, la mémorisation
  compare la quantité SUGGÉRÉE à la quantité RÉELLEMENT produite via le
  même schéma `SuggestionDecision` que F7 — pas un second concept
  parallèle.
- Vue agrégée : taux d'adoption par fonctionnalité IA (F7, F13...), pas
  seulement un total global — un restaurateur qui ignore F13 mais suit F7
  à la lettre doit rester visible comme tel.

**Décision par défaut** : les hypothèses de F17 restent EXPLICITEMENT hors
de ce mécanisme — ce sont des questions posées, jamais des suggestions à
accepter/rejeter (même raisonnement que celui déjà tranché au ticket 8 du
Lot IA-1 pour `ModelDecisionLog`).

---

### Ticket 4 — F20, signaux externes de la demande (jours fériés, vacances scolaires, jours exceptionnels)

**Objectif** : F6 ne connaît que la saisonnalité du jour de semaine. Un
jour férié, une période de vacances scolaires ou un événement local
(concert, match, marché) peuvent faire dévier la fréquentation de 30 à
50 % par rapport à la moyenne du même jour de semaine — réflexe
explicitement listé dans le contexte métier (§8 : « jour de la semaine,
météo, vacances, événements locaux »).

**Décision actée pour limiter la dépendance externe** : phase 1 de ce
ticket volontairement bornée à ce qui ne demande AUCUNE intégration
tierce :
1. **Jours fériés et vacances scolaires (France, zones A/B/C)** :
   calendrier déterministe, connu des années à l'avance, aucune donnée
   externe à interroger en direct.
2. **Jour exceptionnel marqué manuellement par le restaurateur** — cet
   écran figure déjà comme « non construit » dans le bilan du Lot IA-0
   (`docs/bilan-ia-0.md`, item F6 : « marquage journée exceptionnelle »)
   : ce ticket le construit enfin, pas un concept nouveau.
La **météo en direct** (API tierce) est explicitement REPORTÉE — voir
§7, point bloquant 1 : c'est un choix de fournisseur et de budget, pas une
question technique.

**Gate** : F6 actif pour l'ingrédient concerné (même gate que F6
lui-même) ; un jour férié/vacances/exceptionnel sans historique suffisant
pour mesurer son effet propre laisse F6 se rabattre sur son estimation
habituelle (dégradation silencieuse, comme pour toute donnée
insuffisante ailleurs dans le projet).

**Règles métier**
- Un jour férié/vacances/exceptionnel est un FACTEUR MULTIPLICATIF sur
  l'estimation habituelle du jour de semaine, mesuré sur les occurrences
  passées de ce même type de jour — jamais une règle à effet fixe devinée
  (« -20 % un jour férié » n'a de sens pour aucun restaurant en
  particulier).
- Moins de 3 occurrences passées d'un type de jour donné (ex. premier 14
  juillet observé) : aucun facteur appliqué, l'estimation du jour de
  semaine reste seule — même principe de taille d'échantillon minimale que
  partout ailleurs dans le Lot IA-1.
- Le marquage manuel d'un jour exceptionnel reste disponible même sans F20
  actif : c'est une saisie, indépendante du calcul qui l'exploite ensuite.

**Lien technique** : nécessite un petit jeu de données calendaires
(jours fériés + zones de vacances françaises) embarqué dans le projet,
pas une dépendance runtime — à mettre à jour manuellement chaque année
scolaire, comme un fichier de configuration plutôt qu'un appel réseau.

---

### Ticket 5 — F23, cold start d'un plat sans historique

**Objectif** : cas d'usage fil rouge du contexte métier (§6), jamais
formalisé — un plat neuf sur la carte n'a aucune vente. F6/F7 doivent
s'appuyer sur la fiche technique et une estimation initiale du chef, puis
glisser progressivement vers les ventes réelles à mesure qu'elles
s'accumulent, jamais un basculement brutal du jour au lendemain.

**Gate** : nouveau champ optionnel sur `Dish` (estimation de vente
quotidienne initiale, saisie à la création du plat) — absent, le plat
garde le comportement actuel (aucune suggestion tant qu'aucune vente
n'existe, dégradation déjà en place).

**Règles métier**
- Pondération glissante entre l'estimation du chef et la moyenne réelle
  observée, croissante avec le nombre de jours de ventes réelles
  disponibles (poids du réel = jours observés / (jours observés +
  constante de lissage) — même famille de formule que la moyenne
  glissante v1 déjà en place, pas un nouveau paradigme statistique).
- Bascule complète vers F6 (jour de semaine) dès que son propre gate
  (6 semaines) est atteint pour ce plat — ce ticket ne fait que combler
  l'intervalle avant ce seuil, il ne le redéfinit pas.

**Décision par défaut** : la constante de lissage (combien de jours avant
que le réel pèse la moitié) est une valeur de départ raisonnée, réglable
dans `Settings`, déterminée empiriquement sur un jeu synthétique avant
d'être figée (cf. leçon §2) — jamais une intuition non vérifiée.

---

### Explicitement hors de ce lot, ou bloqué sur une décision business

**F24 — comparaison de prix multi-fournisseurs** : NE PAS SPÉCIFIER
avant réponse à la question business du §7 point 2. `supplier_name` est
aujourd'hui un champ unique par ingrédient (décision actée en F16) ; une
vraie comparaison de prix demande de savoir si un ingrédient a
généralement 1-2 fournisseurs alternatifs ou davantage, ce qui détermine
si un second champ optionnel suffit ou si une table `Fournisseur` séparée
(relation many-to-many) est nécessaire. Deviner le mauvais modèle coûte
une migration de données à refaire.

**F26 — intégration caisse (POS)** : NE PAS SPÉCIFIER avant réponse à la
question business du §7 point 3. Chaque logiciel de caisse a son propre
format d'export/API ; aucune spec technique n'a de sens avant de savoir
lequel cibler en premier. Remplacerait à terme l'import CSV manuel (F1,
Lot V1.1) par une lecture quasi temps réel — zone fonctionnelle
explicitement listée au contexte métier §7, mais la plus lourde en
dépendance externe de tout ce backlog.

**F19 (Lot IA-1) — effet réseau / benchmark inter-restaurants** :
inchangé, toujours hors périmètre. Aucune activation avant un second
restaurant actif ET une validation juridique RGPD (mutualisation de
données entre établissements) — même condition qu'au Lot IA-1, non levée
depuis.

**Écrans non construits, Lot IA-0** (refus F5, journal d'adoption F7,
export matrice F9) : toujours du travail d'écran, toujours hors d'un lot
IA — à cadrer dans un lot UX dédié, pas mélangé ici. Le marquage journée
exceptionnelle F6 en fait PARTIE mais est absorbé par le ticket 4 (F20)
ci-dessus, qui en a besoin pour fonctionner.

---

## 4. Jeux de données à générer

SYN-P à SYN-T (suite alphabétique après SYN-O, Lot IA-1) — mêmes
principes que les lots précédents : graine fixe, vérité terrain
interrogeable, bruit ±10 %, et vérifier systématiquement (leçon §2)
qu'un jeu satisfait le gate de la fonctionnalité qu'il cible avant de
l'utiliser dans un test.

| Réf | Contenu | Cible |
|---|---|---|
| SYN-Q | Historique de pertes mixtes (motivées et non) sur plusieurs mois, montants connus | F22 |
| SYN-R | Ventes autour de 3-4 jours fériés connus, effet mesurable sur un ingrédient | F20 |
| SYN-S | Plat ajouté en cours d'historique, estimation initiale connue, ventes réelles progressives | F23 |
| SYN-T | Suggestions F13 avec décisions (acceptée/modifiée/rejetée) sur plusieurs semaines | F25 |

À construire au fur et à mesure des tickets, pas toutes d'avance — même
principe que les deux lots précédents.

---

## 5. Points bloquants — décisions du porteur du projet, pas de Claude Code

Trois points, chacun explicitement hors de ce que ce document tranche
(règle §1.3) :

1. **Météo en direct (F20, phase 2)** : quel fournisseur d'API météo,
   quel budget, quelle fréquence d'appel ? Pas une question technique —
   un choix de coût récurrent et de dépendance externe. Phase 1 (fériés/
   vacances/marquage manuel, ticket 4) ne dépend d'aucune réponse ici et
   peut être construite sans attendre.
2. **Comparaison multi-fournisseurs (F24)** : combien de fournisseurs
   alternatifs par ingrédient en pratique, chez les restaurants
   prospectés par l'équipe commerciale ? Détermine si un champ optionnel
   suffit ou si une table dédiée est nécessaire.
3. **Intégration caisse (F26)** : quel(s) logiciel(s) de caisse ciblent
   en priorité les restaurants prospectés ? Aucune spec technique
   possible avant cette réponse, terrain qui relève de l'équipe
   commerciale plus que du produit.

---

## 6. Critères de sortie du lot

- Tickets 1, 3, 4, 5 construits, testés, derrière feature flag éteint
  (même principe que F10-F19 : toutes éteintes par défaut). Ticket 2
  (F21) retiré — déjà construit au Lot IA-0 (§3.2 ci-dessus).
- NR-01 à NR-18 et la suite des Lots IA-0/IA-1 toujours verts.
- Aucun changement visible pour un utilisateur, sauf ce que le ticket lui-
  même expose explicitement (F22 est une vue de lecture — à cadrer avec
  un écran dédié le moment venu, pas mélangé à la construction de la
  logique, même principe que F12 au Lot IA-1 : construire la logique
  avant l'écran plutôt que d'attendre l'écran pour construire la logique).
- Rapport de sortie (`docs/bilan-ia-2.md`) listant, comme pour les deux
  lots précédents : ce qui est prouvé sur données contrôlées, les écarts
  entre ce backlog et ce qui a été construit, et tout point bloquant qui
  aurait dû remonter en cours de route.

---

## Modèle et effort recommandés

**Sonnet, effort par défaut** pour les 4 tickets restants — chacun
réutilise un patron déjà établi (agrégation de données existantes pour
F22/F25, facteur multiplicatif mesuré empiriquement déjà pratiqué par
F6/F17 pour F20, moyenne pondérée glissante déjà pratiquée par la règle
v1 pour F23) — application répétée plus qu'invention, comme la majorité
du Lot IA-1.
Repasser en Opus uniquement si un ticket remonte un point de jugement
métier non couvert par la règle de résolution d'ambiguïté (§1 règle 3).

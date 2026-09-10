# Bilan — Lot IA-2

Périmètre : `docs/feature-plans/backlog-lot-ia-2.md`. Écrit au fil des
tickets plutôt qu'une seule fois à la fin — voir §6 pour l'état de
clôture du lot.

## 1. Ticket 2 — F21, menu engineering : retiré du backlog, aucune action

Traité en premier dans l'ordre de lecture (mais pas de construction) :
avant d'implémenter quoi que ce soit, relecture de `ai_food_cost.py` (F9,
Lot IA-0) a montré que `popularity_margin_matrix` fait déjà exactement ce
que ce ticket proposait — quadrants popularité × marge, seuils par
médiane de la carte, labels en clair, jamais de suggestion de retirer un
plat. Corrigé dans `backlog-lot-ia-2.md` (commit dédié) plutôt que
committé en double puis découvert après coup. Voir ce backlog, ticket 2,
pour le détail de la correction.

## 2. Ticket 1 — F22, gaspillage consolidé et valorisé : construit

**Gate** : feature flag F22 uniquement — agrège des données déjà
produites (F5 via `CountLine` directement, F14, F17), reste inerte (liste
vide, total 0) tant qu'aucune perte n'existe dans la fenêtre.

**Fenêtre** : glissante en jours (`Settings.waste_summary_window_days`,
défaut 90), pas un découpage par mois calendaire — décision purement
technique documentée dans le code et le backlog (§1 règle 4) : aucune
autre fenêtre temporelle du projet ne raisonne en mois civils
(`COMPARISON_WINDOW_DAYS` de F12, même principe, est le précédent direct).

**Ce qui est agrégé, sans second calcul** :
- Écarts explicables/inexpliqués : `CountLine.variance_value`/
  `variance_reason` directement — PAS `ai_drift._loss_observations`
  (F5), dont le filtre de significativité et la logique de série
  consécutive répondent à une question différente (« y a-t-il un problème
  récurrent ») de celle posée ici (« combien ça a coûté au total »,
  pertes isolées comprises).
- Renvoi F17 (`ai_variance_diagnosis.diagnose`) pour les ingrédients dont
  la perte inexpliquée sur la période dépasse `Settings.loss_alert_eur`
  (même seuil « perte significative » que F5, pas une nouvelle
  constante) — jamais un second diagnostic parallèle.
- Risque à venir F14 (`ai_expiry_risk.assess_expiry_risk`), reporté
  SÉPARÉMENT (`at_risk_total`), jamais additionné au gaspillage déjà
  constaté (`total`) : l'un est un fait passé, l'autre une projection.
- Chiffre d'affaires de la période (même calcul que `ai_food_cost.
  compute_food_cost`, F9) pour le % du CA.

**Prouvé sur SYN-Q** (pertes mixtes sur plusieurs mois, montants
CONNUS : 5 € motivés + 13 € inexpliqués = 18 € sur 200 € de CA, soit
9,0 %) — dont une perte de 100 € délibérément placée HORS fenêtre (150
jours), qui ne doit RIEN compter : la preuve que le filtre de fenêtre
fonctionne, pas seulement qu'un total plausible sort.

**Renvoi F17, fixture dédié** : la répartition « 3 vendredis + 2 samedis »
déjà prouvée déclenchante par SYN-N (Lot IA-1) réutilisée telle quelle.
Un premier essai avec une répartition différente (4 vendredis + 1 samedi)
n'a rien déclenché — pas un bug de F22, mais un comportement réel déjà
en place dans F17 (Lot IA-1) : sa règle « affluence » prend la plus
PETITE série de jours qui atteint son seuil de concentration, et le seul
vendredi retenu n'était pas, dans ce jeu précis, individuellement le jour
le plus vendeur (le samedi l'était de peu). Non retouché ici — ce fichier
teste l'agrégation et le renvoi de F22, pas l'algorithme de F17 lui-même,
déjà couvert par ses propres 13 tests. Réutiliser la répartition
déjà prouvée a évité de rouvrir ce terrain.

**Non-vacuité** : cassé/restauré sur 5 points — le filtre de fenêtre
(deux tests dépendaient de lui : le décoy SYN-Q et la fenêtre réduite à
10 jours), le seuil de renvoi F17 (`loss_alert_eur`), la séparation
explicable/inexpliqué, et la non-additivité du risque F14 dans `total`
(la 1ère tentative de cassure — modifier une variable locale utilisée
seulement pour le texte d'explication — n'a rien changé au résultat du
test : la propriété `WasteSummaryResult.total`, calculée séparément, est
ce que le test lit réellement ; cassée au bon endroit ensuite).

10 tests, `tests/test_ai_waste_summary.py`.

## 3. Ticket 3 — F25, indicateur de confiance étendu à toutes les recommandations : construit

**Gate** : feature flag F25, plus le gate de F13 lui-même (via l'appel à
`ai_production_forecast.forecast_production`) — reste inerte (aucune
suggestion journalisée) tant que F13 ne produit rien pour un ingrédient
donné.

**`ProductionSuggestion`** reprend le schéma d'`OrderSuggestionLine` (F7)
— `suggested_quantity`/`final_quantity`/`decision`/`validated_at`, même
`SuggestionDecision` — sans le concept de lot (`OrderSuggestionBatch`) :
F13 génère une suggestion par appel, par ingrédient, jamais une fournée
quotidienne comme F7. `record_decision` n'est PAS gatée par F25 (une
décision qui clôt une suggestion déjà journalisée doit toujours pouvoir
s'enregistrer, même si le flag a été éteint entre-temps — même principe
que confirmer une ligne de comptage déjà ouverte ailleurs dans le projet).

**Vue agrégée par fonctionnalité** (`adoption_stats_by_feature`) : F7
toujours présent (v1, `metrics.suggestion_adoption_stats`, jamais gatée,
inchangée), F13 SEULEMENT si F25 est actif — sa clé est ABSENTE (pas un
zéro) quand F25 est éteint, pour que « jamais activé » reste visiblement
distinct de « activé, mais jamais encore utilisé ».

**Prouvé sur SYN-T** (base SYN-A, marquée « préparée en interne », stock
ramené à 0 — même raisonnement que AC-F13-2 du Lot IA-1) : 5 suggestions
journalisées, décisions connues (2 acceptées, 2 modifiées, 1 rejetée),
`adoption_stats_by_feature()["F13"]` retrouve exactement cette
répartition.

**Non-vacuité** : cassée/restaurée sur 3 points — le gate F25 sur
`record_production_suggestion`, l'absence (vs zéro) de la clé « F13 »
quand F25 est éteint, et l'indépendance des statistiques F7/F13 (un
contre-exemple avec des décisions F7 ET F13 simultanées, en proportions
différentes : cassé en polluant `_production_adoption_stats` avec de
fausses entrées, a fait échouer à la fois le comptage F13 et le test
d'indépendance croisée).

6 tests, `tests/test_ai_recommendation_tracking.py`.

## 4. Ticket 4 — F20, signaux calendaires : construit

**Gate** : feature flag F20, plus le gate de F6 lui-même (`weekday_
forecast`) dont ce module ajuste la sortie — jamais un second calcul de
base. Le marquage manuel d'un jour exceptionnel (`mark_exceptional_day`/
`unmark_exceptional_day`) reste disponible même F20 (et F6) éteints : une
saisie ne doit jamais être gatée par le calcul qui l'exploite ensuite.
Referme au passage l'écran « marquage journée exceptionnelle » resté non
construit depuis le Lot IA-0 (`docs/bilan-ia-0.md`, item F6).

**Deux modules séparés** : `french_calendar.py` (pur, sans accès base de
données — jours fériés calculés par formule via l'algorithme de Meeus/
Jones/Butcher, jamais une liste figée par année ; vacances scolaires par
zone, données embarquées et sourcées pour 2025-2026/2026-2027, seul
entretien manuel annuel anticipé par le backlog lui-même) et `ai_calendar_
signals.py` (logique métier F20 — mesure du facteur, priorité entre
signaux, dégradation sous le seuil).

**Facteur empirique, jamais deviné** : chaque signal actif (férié /
vacances / exceptionnel) est un facteur multiplicatif sur l'estimation F6
du jour de semaine, mesuré sur les occurrences PASSÉES de ce même signal
(`actual / F6_attendu_ce_jour_de_semaine`, moyenné) — jamais un effet fixe
supposé (« -20 % un jour férié » n'a de sens pour aucun restaurant en
particulier). Moins de `MIN_PAST_OCCURRENCES` (3) occurrences passées :
aucun facteur appliqué, l'estimation F6 seule reste la sortie (dégradation
silencieuse, même principe que partout ailleurs dans le projet) — prouvé
non vacueusement sur la frontière exacte (2 occurrences n'ajustent pas, 3
ajustent).

**Priorité entre signaux** (décision purement technique actée par le code,
backlog §1 règle 4 — le document ne tranchait pas ce cas) : EXCEPTIONNEL
(le plus spécifique, saisi par le restaurateur pour CE restaurant précis)
> FÉRIÉ (récurrent chaque année) > VACANCES (la catégorie la plus large).
Un seul facteur appliqué à la fois, jamais un cumul multiplicatif —
cumuler amplifierait le bruit statistique plus que le signal réel sur un
aussi petit échantillon.

**Réutilisation** : nouvelle fonction publique `ai_forecast.ingredient_
daily_consumption` (renommée depuis `_ingredient_daily_consumption`,
interne — aucun changement de comportement) pour que F20 lise l'historique
jour par jour sans dupliquer ce calcul ; `ai_forecast.weekday_forecast`
(F6) réutilisé tel quel pour l'estimation de base.

**Prouvé sur SYN-R** (ventes plates 2026 avec les jours fériés réels
boostés ×1,5, cible le 11 novembre — Armistice, volontairement hors de
toute période de vacances scolaire embarquée, vérifié explicitement pour
isoler le signal « férié » seul) : 9 fériés passés détectés, facteur
mesuré ≈1,49 (proche de 1,5 sans lui être identique — effet réel documenté
ci-dessous, pas une erreur d'arrondi).

**Propriété découverte, pas un bug** : le facteur mesuré n'est jamais
EXACTEMENT le facteur injecté, parce que F6 lui-même intègre, sans le
savoir, les jours fériés tombés dans sa propre fenêtre de mesure du jour
de semaine (les 8 dernières occurrences) — ce qui gonfle légèrement sa
propre estimation « habituelle » pour ce jour-là. Vérifié empiriquement
avant d'écrire les seuils de tolérance des tests, documenté dans le
docstring du module et celui des tests plutôt que traité comme une
erreur à corriger.

**Non-vacuité** : cassée/restaurée sur 3 points — le seuil `MIN_PAST_
OCCURRENCES` (frontière exacte 2 vs 3 occurrences), la priorité
« exceptionnel » sur « férié » (contre-exemple direct : le 1er janvier,
toujours férié, reste « ferie » sans marquage manuel), et la dépendance
zone pour les vacances scolaires (une date dans les vacances d'hiver
zone A seulement, détectée pour « A », absente pour « B »/« C »/aucune
zone).

12 tests, `tests/test_ai_calendar_signals.py`.

## 5. Ticket 5 — F23, cold start d'un plat sans historique : construit

**Gate** : nouveau champ optionnel `Dish.initial_daily_estimate` (estimation
de vente quotidienne initiale du chef) — absent pour tout plat utilisant un
ingrédient donné, F23 s'efface entièrement (`ok=False`, « aucun plat...
n'a d'estimation »), le comportement actuel (v1) reste inchangé. S'ajoute
le feature flag F23 et, structurellement, le gate de F6 lui-même : F23 ne
s'applique QUE tant que F6 n'est PAS encore disponible pour l'ingrédient
concerné — jamais un second calcul concurrent une fois F6 utilisable.

**Opère au niveau de l'INGRÉDIENT**, comme F6/F7/F13/F14 (jamais du plat) —
la fiche technique est le mécanisme de conversion entre l'estimation du
chef (par plat) et une consommation attendue (par ingrédient) :
`Σ (estimation du chef × grammage)` sur tous les plats de la fiche
technique de cet ingrédient ayant une estimation renseignée.

**Absence de double comptage avec un plat déjà établi** (propriété non
triviale, vérifiée empiriquement avant d'être documentée puis testée) : un
ingrédient partagé entre un plat neuf (estimation du chef) et un plat
ancien déjà vendu depuis plusieurs semaines n'a PAS besoin d'un traitement
spécial — si le plat ancien vend cet ingrédient depuis longtemps,
l'historique COMBINÉ de l'ingrédient a déjà franchi le gate des 6 semaines
de F6 tout seul, et F23 s'efface avant même de calculer un mélange partiel
qui ignorerait la consommation déjà bien mesurée du plat ancien. Le cas
réellement traité par le mélange n'est donc jamais qu'un ingrédient dont
TOUS les plats contributeurs sont eux-mêmes récents.

**Pondération glissante** (règle métier du ticket, appliquée littéralement) :
poids du réel = jours observés / (jours observés + constante de lissage).
`Settings.cold_start_smoothing_days` (défaut 14 jours) déterminé par script
autonome (scratchpad, non conservé dans le dépôt — seule la conclusion
compte) plutôt que deviné : à K=14, le poids atteint exactement 0,5 à 14
jours (par construction de la formule) et ~74,5 % à 41 jours, juste avant
le gate F6 à 6 semaines (42 jours) — une bascule complète mesurée comme
progressive, jamais brutale, avant d'être figée.

**Bascule complète à la frontière du gate F6** : vérifiée jour par jour —
à J+41 (5,86 semaines de span calendaire), F23 s'applique encore ; à J+42
(exactement 6 semaines), F6 devient disponible et F23 s'efface au même
instant, sans jour de battement ni chevauchement.

**Prouvé sur SYN-S** (plat neuf seul sur son ingrédient, estimation du chef
connue et délibérément différente du rythme réel qui s'installe ensuite) :
jour 0 (aucune vente) → estimation du chef seule ; jour 14 → poids réel
exactement 0,5 ; le mélange glisse continûment vers la moyenne réelle à
mesure que les jours s'accumulent.

**Non-vacuité** : cassée/restaurée sur 3 points — la dégradation silencieuse
de `_chef_component` (aucune estimation sur aucun plat → `None`, jamais un
zéro qui laisserait croire à une estimation réelle de zéro), la formule de
pondération elle-même (dénominateur `jours + K`, pas seulement `K`) à sa
frontière exacte (14 jours → 0,5), et l'effacement de F23 dès que F6 est
disponible (cassé en retirant ce gate : sur le scénario plat établi +
plat neuf partageant un ingrédient, produit alors un mélange à 8,94 au
lieu de s'effacer — la contamination du double comptage redoutée, rendue
concrète plutôt que seulement théorique).

8 tests, `tests/test_ai_cold_start.py`.

## 6. Bilan de sortie du Lot IA-2

Les 5 tickets du backlog sont clos : F22 et F25 (tickets 1 et 3) construits
dès le début du lot, F21 (ticket 2) retiré car déjà couvert par F9 (Lot
IA-0), F20 (ticket 4) et F23 (ticket 5) construits en fin de lot. Comme
pour le Lot IA-1, chaque fonctionnalité reste en mode ombre — un service
testé et prouvé sur données synthétiques, gaté par un feature flag éteint
par défaut, sans écran dédié (même principe que F10-F19 : l'intégration
UI est un lot UX séparé, jamais mélangée à un lot IA). F24 et F26 restent
explicitement hors périmètre, bloqués sur des décisions business non
tranchées (§5 du backlog) ; F19 (Lot IA-1) reste hors périmètre pour les
mêmes raisons qu'au lot précédent.

Suite complète verte après chaque ticket, à chaque fois avant le commit
correspondant — jamais un commit sur une suite rouge ou non vérifiée.

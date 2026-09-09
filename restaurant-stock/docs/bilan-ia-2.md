# Bilan — Lot IA-2 (en cours)

Périmètre : `docs/feature-plans/backlog-lot-ia-2.md`. Ce document est mis
à jour au fil des tickets, pas écrit une seule fois à la fin — l'état
ci-dessous reflète ce qui est réellement construit à date, pas la cible
finale du lot.

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

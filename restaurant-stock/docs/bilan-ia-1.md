# Bilan — Lot IA-1 (en cours)

Périmètre : `docs/feature-plans/ia-f10-f19.md` + backlog transmis
(`avancement-lot-ia-0-trois-decisions`, `backlog-lot-ia-1`). Ce document est
mis à jour au fil des tickets, pas écrit une seule fois à la fin — l'état
ci-dessous reflète ce qui est réellement construit à date, pas la cible
finale du lot.

## 1. Ticket 1 — F10, classification de criticité : construit

**Gate** : ≥ 4 semaines de ventes par ingrédient, aucun comptage requis.
Sous ce seuil : « non déterminé », jamais « C » par défaut (AC-F10-2).

**Prouvé sur SYN-J** (`tests/synthetic_data.py::build_syn_j`, 20 ingrédients,
répartition de valeur Pareto connue — 3 « gros » à 250 € chacun, 1
« petit-grand » à 80 €, 16 « petits » à 10,625 € — construite pour que le
franchissement de la frontière 80 % soit déterministe malgré le bruit et
les ex-æquo) :

- Les 3 gros sont classés A, aucun des 17 petits ne l'est jamais
  (`test_syn_j_the_three_big_ingredients_are_class_a`,
  `test_syn_j_no_small_ingredient_is_ever_class_a`).
- Valeur annuelle calculée à ±5 % de la valeur injectée.
- Résumé jamais réduit à une lettre nue : « 3 ingrédients représentent 80 %
  de votre coût matière » (AC-F10-1, formulation métier du document).
- Historique insuffisant → `computed_class = None` (« non déterminé »),
  jamais C par défaut (AC-F10-2).
- **Dormant** (TC-F10-02) : un ingrédient à forte valeur historique mais
  sans consommation depuis 21 jours (`DORMANT_WINDOW_DAYS`) est signalé
  « dormant », jamais A — exclu du calcul Pareto des autres pour ne pas
  gonfler artificiellement leur seuil.
- **Forçage manuel** (AC-F10-3) : persisté sur `Ingredient.criticality_override`,
  prime toujours, survit à un second appel complet de
  `classify_ingredients` (pas une valeur mise en cache — un second calcul
  entier est relancé et retrouve le même forçage).

**Rejeu du passé** : `classify_ingredients(db, as_of=...)` — leçon du Lot
IA-0 (`ai_forecast.weekday_forecast(as_of=...)`) appliquée par défaut ici
aussi, comme demandé par `backlog-lot-ia-1` §3.

**Non-vacuité** : gate, détection de dormance et primauté du forçage manuel
chacun cassés séparément, confirmé que les tests concernés (et eux seuls)
échouent, restauré.

### Point bloquant, documenté plutôt que deviné

Le document (`ia-f10-f19.md` §1) demande qu'« un ingrédient de classe B
très volatil remonte en A », sans fixer de seuil de coefficient de
variation à partir duquel un ingrédient est « très volatil ». Ce n'est pas
une question technique : décider ce chiffre changerait en silence ce
qu'un restaurateur voit comme prioritaire. Appliqué la règle §2 du backlog
(règle 3 : sur un jugement métier, ne pas construire, documenter) :

- Le coefficient de variation des écarts est **calculé et exposé**
  (`IngredientCriticality.volatility`) pour tout ingrédient avec
  ≥ 3 comptages.
- Il **n'est PAS utilisé** pour reclasser automatiquement B → A. Verrouillé
  par `test_volatility_is_exposed_but_never_auto_promotes_a_class`.
- La seule règle de jugement effectivement tranchée par le backlog —
  l'ex-æquo de valeur entre deux ingrédients au bord d'une classe, le plus
  volatil des deux montant — **est** appliquée (clé de tri secondaire dans
  `classify_ingredients`), puisqu'elle était explicitement décidée, à la
  différence du seuil général de « très volatil ».

**À trancher avant que F11 (qui dépend de F10) puisse s'appuyer dessus** :
le seuil de coefficient de variation déclenchant une promotion B → A.

**Note de flag** : `feature_f15_enabled` a été ajouté au même moment que `feature_f10_enabled` (même migration), par le même réflexe que le Lot IA-0 (« feature flags F5/F6/F7/F9, éteints par défaut » avant que chaque fonctionnalité soit construite une à une) — le flag existe, F15 lui-même reste à construire (§2).

## 2. Reste du backlog — non construit à ce stade

| Ticket | Fonctionnalité | État |
|---|---|---|
| 2 | F11 — comptage tournant intelligent ⭐ | Non construit — dépend du ticket 1 (fait) |
| 3 | F12 — alerte de marge érodée ⭐ | Non construit |
| 4 | F15 — contrôle d'intégrité des imports | Non construit |
| 5 | F18 — indicateur de confiance, retour auto v1 | Non construit |
| 6 | F14 — risque de péremption | Non construit |
| 7 | F16 — consolidation de commande par fournisseur | Non construit |
| 8 | F17 — diagnostic de cause d'écart | Non construit |
| 9 | F13 — prévision de mise en place | Non construit |

**Les trois décisions actées** (`avancement-lot-ia-0-trois-decisions` §1,
lues avant ce backlog) :
- Journal de décision du modèle — **non construit**, priorité haute pour le
  prochain ticket touché.
- Écran de comparaison en mode ombre — **non construit**, prévu après le
  ticket 2 (F11).
- Rejeu historique — confirmé hors périmètre, aucune action.

## 3. Critères de sortie du lot — état

- Tickets 1 à 8 construits, testés, derrière feature flag éteint : **1/8**.
- Journal de décision du modèle en place dès le ticket 1 : **non fait**.
- Écran de comparaison en mode ombre : **non fait** (attendu après ticket 2).
- NR-01 à NR-18 et la suite du Lot IA-0 toujours verts : **oui**, 300 tests
  au vert (289 IA-0 + 11 F10, hors ROB).
- Aucun changement visible pour un utilisateur : **vrai** pour ce qui est
  construit à date (F10 n'a ni routeur ni gabarit).

## 4. Prochaine session

Reprendre au ticket 2 (F11, comptage tournant) une fois le seuil de
volatilité du ticket 1 tranché — ou traiter le ticket 4 (F15, aucune
dépendance, priorité haute déclarée par le document) en attendant cette
décision.

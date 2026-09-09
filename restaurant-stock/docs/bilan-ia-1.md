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

## 2. Ticket 4 — F15, contrôle d'intégrité des imports : construit

**Gate** : >= 3 occurrences passées du même jour de semaine pour une
« normale » de volume ; >= 3 semaines d'historique global pour le
repérage de trous. Sous ces seuils : aucune alerte (AC-F15-3, TC-F15-04).

**Prouvé sur SYN-O** (10 ventes/jour, avec un trou d'un jour, un jour à
-80%, et une période de congés de 14 jours injectés à des dates connues) :

- Le jour à -80% est détecté (AC-F15-1), les jours normaux ne le sont
  jamais (contre-exemple direct, sans lequel une alerte permanente
  passerait aussi le premier test).
- Seuil de déviation réglable (`Settings.import_volume_alert_pct`, 40%
  par défaut) — même principe que les seuils du Lot IA-0 (§8 des specs V2).
- Le trou isolé est signalé comme un jour ; les 14 jours de congés sont
  groupés en **une seule** alerte de période, pas 14 alertes répétant le
  même diagnostic (TC-F15-05 : « détecté comme période exceptionnelle »).
- Marquer un jour comme fermé (`mark_day_closed`, idempotent) retire son
  alerte immédiatement, sans affecter les autres trous en cours (AC-F15-2).
- Un jour de semaine chroniquement à zéro vente (ex. fermeture hebdo fixe)
  n'est jamais un « trou » — distingué d'un jour férié isolé par un gate
  propre (>= 3 occurrences, toutes à zéro) (TC-F15-06).
- Détection de doublon de fichier par empreinte du contenu (sha256),
  calculée à la source dans `sales_import.import_sales` — reprend la
  demande de F8 (non construite par ailleurs) sans en reconstruire le
  reste (mapping assisté, prévisualisation).

**Non-vacuité** : groupement de jours consécutifs, gate d'historique,
détection de fermeture habituelle et prise en compte des jours marqués
fermés chacun cassés séparément, confirmé que le test concerné (et lui
seul) échoue, restauré. Un premier passage du test de gate (TC-F15-04)
avait un trou factice hors de portée de son propre test — corrigé en même
temps que la preuve de non-vacuité l'a révélé, pas après coup.

## 3. Ticket 2 — F11, comptage tournant intelligent ⭐ : construit

Le document juge lui-même cette fonctionnalité la plus précieuse des dix :
« la seule [...] qui s'attaque directement à la friction n°1 [...] elle
réduit ce que le chef FAIT ».

**Gate** : F10 actif (son propre gate) ET >= 3 comptages complets au
global. Sous ce seuil : aucune session, message honnête.

**Précédence, du plus fort au plus faible**, chacune prouvée séparément
sur SYN-K (réutilise l'axe criticité de SYN-J, prolongé pour ne pas
tomber "dormant" pendant la fenêtre de comptage — voir ci-dessous) :
1. Badge F5 actif -> réintègre TOUJOURS, même retiré manuellement
   (TC-F11-07 : la sécurité prime la préférence).
2. Comptage complet en retard (>= `full_count_interval_days`, 28 j par
   défaut, réglable) -> force TOUS les ingrédients actifs, aucune session
   ciblée tant qu'il n'est pas fait (AC-F11-3).
3. Choix manuel du chef (`set_manual_override`), mémorisé.
4. Fréquence calculée (criticité x stabilité).

**Grille fréquence x criticité** — les 4 coins couverts par SYN-K :
ingrédient critique (classe A) instable -> quotidien ; critique stable
(>= 6 comptages conformes, la fenêtre que le document cite lui-même en
exemple) -> hebdomadaire, jamais mensuel même stable ; faible valeur
stable -> mensuel ; nouvel ingrédient sans historique -> quotidien par
défaut (TC-F11-06).

**Non-vacuité** : plafond hebdomadaire de la classe A, précédence
badge > manuel, déclenchement du comptage complet en retard et gate
global chacun cassés séparément, confirmé que le test concerné échoue,
restauré. Un premier essai de preuve sur la précédence badge/manuel s'est
révélé être un faux négatif (l'inversion codée ne changeait rien à ce cas
précis) — corrigé en re-choisissant quelle branche désactiver plutôt que
déclaré "prouvé" sur un test qui n'aurait rien prouvé.

### Interprétation faute de spec formelle sur le stockage

Aucune notion de « session ciblée » n'existe dans le schéma v1 :
`counting.start_count_session` pré-remplit déjà une ligne par ingrédient
ACTIF pour chaque session, sans distinction partielle/complète. « Comptage
complet », au sens de F11, est donc défini ici comme n'importe quelle
`CountSession` terminée — `daily_session()` ne fait que RECOMMANDER quels
ingrédients demander aujourd'hui (un filtre d'affichage pour un futur
écran), jamais un nouveau type d'enregistrement.

### Grille fréquence x criticité, milieu comblé par un défaut de sécurité

Le document ne donne que les deux coins extrêmes (« fort coût + instable
-> quotidien », « faible coût + toujours conforme -> mensuel »). Le milieu
de la grille (ex. faible coût mais instable) est comblé en dégradant vers
PLUS de comptage plutôt que moins dans le doute — un défaut de sécurité,
pas un jugement métier sur ce qui est prioritaire (à la différence du
seuil de volatilité du ticket 1, où un tel défaut n'existe pas). Documenté
ligne par ligne dans `ai_rotating_count._frequency_for`.

### Ce qui reste hors de ce ticket

AC-F11-2 (accès au comptage complet « en un geste »: un écran),
AC-F11-5 (temps de comptage moyen mesuré après activation : suppose un
usage réel, mesurable seulement au pilote) — hors de portée par
construction, comme tous les écrans du Lot IA-0 restés « non construits »
(§2 du bilan IA-0).

## 4. Reste du backlog — non construit à ce stade

| Ticket | Fonctionnalité | État |
|---|---|---|
| 2 | F11 — comptage tournant intelligent ⭐ | **Fait** (§3) |
| 3 | F12 — alerte de marge érodée ⭐ | Non construit |
| 4 | F15 — contrôle d'intégrité des imports | **Fait** (§2) |
| 5 | F18 — indicateur de confiance, retour auto v1 | Non construit |
| 6 | F14 — risque de péremption | Non construit |
| 7 | F16 — consolidation de commande par fournisseur | Non construit |
| 8 | F17 — diagnostic de cause d'écart | Non construit |
| 9 | F13 — prévision de mise en place | Non construit |

**Les trois décisions actées** (`avancement-lot-ia-0-trois-decisions` §1,
lues avant ce backlog) :
- Journal de décision du modèle — **non construit**, priorité haute pour le
  prochain ticket touché.
- Écran de comparaison en mode ombre — **non construit**, le ticket 2
  (F11) qui le débloquait est fait, reste à cadrer l'écran lui-même.
- Rejeu historique — confirmé hors périmètre, aucune action.

## 5. Critères de sortie du lot — état

- Tickets 1 à 8 construits, testés, derrière feature flag éteint : **3/8**.
- Journal de décision du modèle en place dès le ticket 1 : **non fait**.
- Écran de comparaison en mode ombre : **non fait** (attendu après ticket 2).
- NR-01 à NR-18 et la suite du Lot IA-0 toujours verts : **oui**, 326 tests
  au vert (289 IA-0 + 11 F10 + 12 F15 + 14 F11, hors ROB).
- Aucun changement visible pour un utilisateur : **vrai** pour ce qui est
  construit à date (F10, F11, F15 n'ont ni routeur ni gabarit).

## 6. Prochaine session

Tickets 2 et 4 traités. Reprendre au ticket 3 (F12, alerte de marge
érodée) — sa dépendance (prix de vente sur la fiche plat, U7 du plan UX)
n'est pas levée, mais le backlog demande explicitement de construire la
logique quand même, en amont de l'écran (§4 ticket 3, cohérent avec la
dégradation silencieuse déjà appliquée à F7/F13/F14/F16).

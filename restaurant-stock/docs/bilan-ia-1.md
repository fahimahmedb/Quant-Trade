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

## 4. Ticket 7 — F16, consolidation de commande par fournisseur : construit

**Gate** : aucun — « purement combinatoire », dit le document lui-même.
Traité avant les tickets 3/5/6/8/9 car sans aucune dépendance et sans
jugement métier à trancher, à la différence des autres tickets restants.

Regroupe les suggestions F7 (Lot IA-0) par fournisseur, calcule le total
et compare au franco de port. Aucun jeu SYN dédié dans le document
(logique purement combinatoire) : fixtures locales dans
`tests/test_ai_supplier_consolidation.py`, sur le même principe que les
propres tests DB-intégrés de F7 dans le Lot IA-0.

- AC-F16-1 : la quantité groupée est EXACTEMENT celle que F7 suggère
  seul (comparaison directe, pas recalculée différemment) ; un ingrédient
  sans fournisseur va dans « Non attribué » ; un ingrédient avec
  fournisseur va bien sous CE fournisseur, jamais « Non attribué ».
- AC-F16-2 : sous le franco, proposition d'ajout parmi les ingrédients du
  même fournisseur pas encore dus, chaque ligne plafonnée par la même
  borne de péremption que F7 (`shelf_life_days x conso − stock actuel`).
- TC-F16-05 : quand aucun ajout possible ne suffit à atteindre le franco
  sans risquer la péremption, le message le dit explicitement et propose
  un report — jamais une sur-commande pour forcer le seuil (principe 2).
- AC-F16-3 : aucun envoi automatique dans aucun chemin de code — la
  fonction produit un texte exportable, jamais un appel réseau.

**Simplification documentée** : le document liste « franco de port » et
« minimum de commande » comme deux données distinctes, mais son propre
plan de test (AC/TC) n'exerce que le franco — traité comme un seul seuil
(`Ingredient.supplier_free_shipping_threshold`) plutôt que deux concepts
dont l'un resterait entièrement non testé.

**Réutilisation** : la consommation quotidienne pour "combien puis-je
ajouter maintenant" utilise la moyenne glissante v1 (jamais F6) — F16 pose
une question secondaire à F7, pas une nouvelle prévision.

**Non-vacuité** : plafond de péremption sur les ajouts proposés,
recalcul réel de l'atteignabilité du seuil (pas toujours vrai), et
groupement par fournisseur nommé chacun cassés séparément, confirmé que
le test concerné échoue, restauré. Le premier essai de preuve sur le
groupement par fournisseur s'est révélé être un faux négatif (aucun test
existant ne vérifiait qu'un fournisseur NOMMÉ reste bien sous son propre
groupe) — un test dédié a été ajouté avant de redéclarer la preuve.

## 5. Ticket 6 — F14, risque de péremption : construit

**Gate réel** : durée de conservation renseignée (champ optionnel déjà
prévu par F7). Le document dit « F6 actif OU moyenne glissante v1
disponible », mais la moyenne glissante v1 répond toujours 0.0 sans
jamais échouer — ce n'est donc jamais un second gate bloquant, juste une
source de repli (même hiérarchie F6-puis-v1 que F7).

Calcul choisi pour ne jamais diviser par la consommation (TC-F14-04) :
plutôt que « combien de jours avant épuisement », `stock_actuel −
conservation × consommation` — une consommation nulle donne directement
tout le stock en trop, sans aucune division dans la formule.

**Prouvé sur SYN-M** (conservation 5 jours, consommation 2000 g/jour
établie par de vraies ventes, seuil de péremption exactement 10 000 g) :
- Stock au-dessus du seuil (12 000 g) → à risque, montant en euros exact
  à la marge de bruit près (AC-F14-2, AC-F14-3).
- Stock en dessous (8 000 g) → jamais à risque (contre-exemple direct).
- Consommation nulle → alerte immédiate, tout le stock signalé, aucun
  crash (TC-F14-04).
- Une réception en cours de route change le résultat au recalcul suivant
  (TC-F14-05) — trivialement vrai par construction (fonction pure sur
  l'état courant, jamais mise en cache), vérifié explicitement plutôt que
  supposé.
- Sans conservation renseignée → silencieux, message explicite, jamais
  une erreur (AC-F14-1).

**Non-vacuité** : formule du reliquat et gate de conservation chacun
cassés séparément, confirmé que les tests concernés échouent (le second
cassage produit une `TypeError` franche — le gate protégeait aussi contre
un accès à un champ `None`), restauré.

## 6. Ticket 3 — F12, alerte de marge érodée ⭐ : construit

Dépendance signalée par le document comme non levée (« prix de vente
saisi sur la fiche plat, U7 du plan UX, non encore fait ») : décision
actée du backlog (§4 ticket 3) — construire la logique quand même, en
amont de l'écran. Faute d'un champ dédié sur `Dish`, le prix de vente est
lu sur une donnée déjà disponible : le `unit_price` le plus récent parmi
les ventes importées de ce plat (`SaleLine.unit_price`) — pas un nouveau
champ qui dupliquerait une donnée déjà présente dans le flux existant.

**Gate** : ≥ 2 relevés de prix (`PriceHistory`) sur au moins un
ingrédient du plat.

**Prouvé sur SYN-L** (plat à 4 ingrédients, 3 aux prix stables, 1 dont le
prix grimpe sur 90 jours, coefficient 3,4 → 2,8 comme demandé) :
- Coefficient et baisse sur 90 jours retrouvés à ±0,05 (SYN-L).
- Décomposition de la hausse : l'intégralité de l'écart attribuée au bon
  ingrédient, les 3 stables à zéro, la somme des impacts reconstitue
  exactement l'écart total (AC-F12-3).
- Frontière du seuil exacte : pile au seuil (3,0 par défaut) → pas
  d'alerte ; juste en dessous → alerte (AC-F12-1).
- Sans prix de vente → exclu avec mention, distinct du gate de relevés de
  prix (AC-F12-2, testé séparément).
- Prix suggéré : restaure le coefficient D'ORIGINE (celui d'il y a 90
  jours) appliqué au coût matière actuel, jamais le seuil réglable — au
  centime près (AC-F12-4). Jamais appliqué au prix de vente réel, sur
  aucun nombre d'appels (AC-F12-5).
- Hausse puis retour au prix d'origine → alerte levée puis retirée
  (TC-F12-06, fonction pure sur l'état courant, jamais mise en cache).
- Ingrédient partagé par 5 plats → chacun listé avec son impact propre,
  proportionnel à son grammage (TC-F12-07).
- Hausse de 40 % sur un ingrédient à 2 % du coût → pas d'alerte, impact
  agrégé réellement négligeable, aucun cas particulier codé (TC-F12-08).

**Réutilisation** : `PriceHistory` (F1, déjà livré) journalise CHAQUE
prix qui a été en vigueur, y compris le prix courant — le prix à une date
donnée est directement le dernier relevé antérieur ou égal à cette date,
sans logique supplémentaire.

**Non-vacuité** : seuil absolu, formule du prix suggéré, décomposition
par ingrédient et gate de relevés de prix chacun cassés séparément,
confirmé que le test concerné échoue, restauré. Le premier essai sur le
gate s'est révélé être un faux négatif (aucun test n'isolait ce cas du
cas voisin « pas de prix de vente ») — un test dédié ajouté avant de
redéclarer la preuve, même schéma que pour le ticket 7 (F16).

## 7. Ticket 5 — F18, indicateur de confiance et retour automatique à v1 : construit

Aucun jeu SYN dédié dans le document (§9) : fixtures locales, comme F12/
F16 dans ce même lot. Deux profils construits et vérifiés empiriquement
avant d'écrire les tests dessus : une tendance haussière sans saisonnalité
hebdomadaire (F6 perd face à la v1 sur CHAQUE semaine rejouée) et un
historique saisonnier dont seules les 3 dernières semaines de ventes sont
perturbées (dégrade exactement les 2 dernières semaines évaluables, pas
3 — la limite testée par TC-F18-04).

**Gate** : réutilise tel quel le gate d'IA-01 (`backtest_vs_v1`,
`BACKTEST_MIN_WEEKS` = 4 semaines rejouables), jamais redéfini séparément
— F18 est explicitement « le pendant runtime du test IA-06 » du document.

**Hystérésis (décision actée, backlog §4 ticket 5)**, fenêtres
asymétriques :
- 3 semaines de dégradation CONSÉCUTIVES désactivent F6 pour l'ingrédient
  concerné (AC-F18-1), journalisées dans `ModelDecisionLog` (AC-F18-2).
- La réactivation exige un NOUVEAU backtest complet redevenu favorable
  (`BacktestResult.should_activate`, le même seuil ≥ 15 % qu'IA-01) —
  jamais seulement quelques bonnes semaines locales, pour qu'un rebond
  ponctuel ne réenclenche pas immédiatement ce que la dégradation venait
  d'éteindre (TC-F18-05).
- 2 semaines dégradées seulement → aucune bascule (TC-F18-04, jeu construit
  pour dégrader exactement 2 semaines, jamais 3, faute de quoi ce test ne
  prouverait rien).

**Vocabulaire (AC-F18-3)** : l'écart est exprimé en pourcentage clair
(« Prévisions justes à ±X % en moyenne sur les 4 dernières semaines »),
jamais MAPE ni RMSE dans un message destiné à un usage restaurateur.

**Bug réel trouvé par les tests, pas une simple divergence cosmétique** :
la bascule F18 lue dans `weekday_forecast` (pour que F7/F14 la respectent
sans mise à jour séparée) était AUSSI lue par `backtest_vs_v1`, qui
appelle `weekday_forecast` en interne pour rejouer chaque semaine passée.
Un ingrédient déjà revenu à la v1 voyait donc chaque semaine rejouée par
le backtest échouer au même gate — 0 semaine rejouable, `backtest.ok
= False` — et ne pouvait alors plus JAMAIS accumuler les 4 semaines
nécessaires pour se réactiver : un blocage circulaire qui aurait rendu la
réactivation totalement inatteignable en usage réel. Révélé par
`test_tc_f18_05_reactivation_requires_a_favorable_full_backtest` échouant
dès le premier lancement. Corrigé en extrayant le calcul de F6 lui-même
(`_weekday_forecast_core`, sans les gates de disponibilité) que
`weekday_forecast` applique pour l'usage courant et que `backtest_vs_v1`
appelle directement pour rejouer l'historique sans se heurter à la
bascule qu'il sert lui-même à lever.

**Non-vacuité** : ce même bug a révélé un second problème, une preuve qui
passait pour la mauvaise raison —
`test_tc_f18_05_no_flip_flopping_while_still_degraded` était déjà vert
AVANT le correctif, mais vacuement : son 2e appel tombait dans le même
blocage circulaire (`backtest.ok=False`), et `check_and_apply_reversion`
renvoie `action="none"` par défaut sur cet échec, la seule chose que le
test vérifiait. Une réactivation empêchée par des données réellement
défavorables et un backtest qui échoue purement et simplement
produisaient la même assertion — le test ne distinguait pas les deux.
Assertion `outcome.ok` ajoutée avant de redéclarer la preuve valide (même
schéma récurrent que les tickets 6 (F12) et 7 (F16) : une preuve qui
passe sans qu'on y touche signale un vrai trou de couverture, pas une
règle inutile). Cassé/restauré ensuite avec le correctif en place : les
deux tests d'hystérésis (déclenchement à 3 semaines, blocage de la
réactivation tant que les données restent défavorables) échouent bien
sans lui, repassent avec.

**Journal de décision du modèle** : première brique du chantier resté en
suspens depuis avancement-lot-ia-0-trois-decisions §1 — `ModelDecisionLog`
construit ici au périmètre strict dont F18 a besoin (feature, ingrédient,
événement, détail), pas le système générique complet évoqué par le
document pour l'ensemble des décisions IA.

## 8. Ticket 8 — F17, diagnostic de cause d'écart ⭐ : construit

Backlog (§4 ticket 8) recommandait Opus spécifiquement — « juge la
solidité d'une corrélation ». Traité en Sonnet, faute de changement de
session, par discipline « avance sur tout ce que je t'ai envoyé » ; par
prudence, chaque seuil de significativité a été vérifié empiriquement
(script autonome, base en mémoire) AVANT d'être figé dans le code, jamais
deviné — même discipline que pour tout le reste du lot, appuyée plus fort
ici vu l'absence d'Opus.

**Portée (décision actée faute de précision du document)** : les règles
portent sur les écarts SANS motif saisi. F5 pose déjà cette distinction
(`LossBadge.cumulative_value` de `ai_drift.classify_losses` est « hors
écarts portant un motif ») — F17 la continue : un écart déjà motivé
(casse, périmé...) a déjà sa réponse, rien à diagnostiquer. Le gate (§8 :
« >= 6 comptages, et >= 3 écarts avec motif saisi ») est donc un seuil
d'ACTIVITÉ globale sur l'ingrédient (le champ motif est réellement
utilisé, donc l'historique est fiable), pas un filtre sur les écarts que
les règles analysent — sans quoi le gate et la portée se contrediraient :
aucun jeu ne pourrait jamais satisfaire « >= 3 écarts motivés » tout en
laissant des écarts SANS motif à diagnostiquer.

**Quatre hypothèses, croisées indépendamment** (`app/services/
ai_variance_diagnosis.py`), chacune une question (AC-F17-3), jamais une
affirmation :
- **Affluence** (AC-F17-1, SYN-N) : écarts non expliqués concentrés sur
  1-2 jours de la semaine — mais SEULEMENT si ces jours sont RÉELLEMENT
  les jours de plus fort volume de vente pour cet ingrédient (vérifié sur
  les ventes réelles, jamais supposé sur « vendredi/samedi = rush »).
  Décision actée par nécessité : le document ne dit pas comment définir
  « forte affluence » pour un restaurant donné — deviner sur des jours
  fixes aurait pu inventer une corrélation sur un établissement dont le
  rush n'est pas le week-end.
- **Zone** : d'autres ingrédients de la MÊME zone de stockage montrent eux
  aussi des écarts non expliqués, dans une proportion nettement
  supérieure aux autres zones.
- **Date** : les écarts non expliqués n'apparaissent qu'à partir d'une
  date précise (avant : rien ; après : régulièrement) — détection du plus
  petit point de rupture chronologique satisfaisant ce critère.
- **Fiche technique** : renvoi vers F5 (`ai_drift.detect_drift`) si une
  proposition existe déjà pour cet ingrédient — F17 s'efface derrière
  elle plutôt que d'inventer une seconde corrélation sur la même donnée.

**Prouvé sur SYN-N** (écarts injectés uniquement vendredi/samedi, mêmes
facteurs jour/semaine que SYN-A pour que ces 2 jours soient aussi,
authentiquement, les jours de plus grosse vente) : hypothèse « affluence »
seule proposée, citant vendredi et samedi (AC-F17-1).

**TC-F17-04** (écarts sur 6 comptages motivés, 5 non expliqués dispersés
sur 5 jours de semaine différents) : aucune hypothèse — la dispersion ne
franchit aucun seuil de concentration.

**TC-F17-05** (SYN-N + 2 ingrédients de la même zone montrant eux aussi
des écarts non expliqués) : « affluence » ET « zone » proposées ensemble,
jamais un choix arbitraire entre les deux.

**Non-vacuité, trou de couverture trouvé avant même d'écrire un bug** :
en construisant le fixture d'AC-F17-2 (« aucun motif jamais saisi »), un
premier jet avec 8 écarts non expliqués (dont 5 vendredi/samedi) donnait
une concentration de 62,5 % — sous le seuil de 65 % retenu pour la règle
« affluence ». Le test aurait alors passé pour la mauvaise raison :
indissociable entre « le gate motifs bloque bien » et « la concentration
était de toute façon insuffisante ». Corrigé en réutilisant EXACTEMENT la
répartition non expliquée de SYN-N (5/5, 100 %, déjà prouvée
déclenchante par AC-F17-1) avant de retirer les motifs — la seule
variable isolée est alors bien celle que le test prétend vérifier.

Six ruptures supplémentaires prouvées par cassure/restauration (jamais
`git checkout`, `cp` vers `/tmp` puis retour, `diff` de contrôle) :
le gate (clause motifs), le croisement affluence/ventes réelles (sans
lui, aucun test existant — ni AC-F17-1 ni TC-F17-04 — n'aurait détecté sa
disparition : un contre-exemple dédié a dû être ajouté, écarts concentrés
à 100 % sur le jour le plus CREUX en vente), le seuil de part affectée de
la règle zone, l'exigence « rien avant la rupture » de la règle date, le
renvoi F5, et l'agrégation « toutes les hypothèses » plutôt qu'un premier
match arbitraire (TC-F17-05).

**Journal de décision du modèle** : F17 ne journalise rien dans
`ModelDecisionLog` — une hypothèse proposée n'est pas une décision prise
par le modèle (contrairement à la bascule automatique de F18), juste une
question posée au restaurateur.

## 9. Ticket 9 — F13, prévision de mise en place : construit

Hors périmètre des critères de sortie du lot (backlog §12 : « confort, à
construire seulement si les tickets 1 à 8 sont faits ») — fait quand même,
cette condition étant désormais remplie, par discipline « avance sur tout
ce que je t'ai envoyé ». Aucun jeu SYN dédié : le document pointe
directement SYN-A (Lot IA-0) pour AC-F13-2.

**Gate** : « F6 actif pour les ingrédients concernés » — réutilise tel
quel le gate de `ai_forecast.weekday_forecast`, jamais redéfini
séparément, plus le marqueur optionnel `Ingredient.is_prepared_in_house`
(AC-F13-1) et le feature flag F13.

**Fenêtre de production** : le lendemain, ou les N jours de conservation
de la préparation — réutilise `Ingredient.shelf_life_days` (champ F7 déjà
prévu), pas un second champ dupliquant le même concept ; 1 jour par
défaut en son absence (TC-F13-05 : 3 jours de conservation -> couvre bien
3 jours, pas 1).

**Stock existant déduit (AC-F13-3)** : le reste de la préparation
précédente EST `Ingredient.current_theoretical_stock` — un ingrédient
« préparé en interne » est un ingrédient comme un autre, aucun second
compteur.

**Prouvé sur SYN-A** : stock ramené à 0 pour isoler la précision de la
prévision elle-même (AC-F13-2) de sa déduction (AC-F13-3, testée
séparément avec un stock réaliste) — le stock de départ de SYN-A
(10 000 000, une marge pour 12 semaines de ventes, pas un reste de
préparation réaliste) aurait sinon masqué toute quantité suggérée. Écart
avec la prévision F6 : quasi nul (bien en-deçà des ±10 % exigés), la
quantité étant lue directement sur la même sortie.

**Non-vacuité** : le gate F6 n'était couvert par AUCUN test avant l'ajout
d'un cas dédié — les 7 autres tests roulent tous sur SYN-A (12 semaines,
largement au-dessus du seuil), donc aucun n'aurait détecté la disparition
du gate. Cassé/restauré sur 4 points : la déduction du stock, le calcul
de fenêtre à partir de `shelf_life_days`, le marqueur « préparé en
interne », et ce gate.

**Colonne NOT NULL n°2 sur `ingredients`** (`is_prepared_in_house`, après
`f6_reverted_to_v1` au ticket 5) : `test_backup.py`/`test_migrations.py`
corrigés par anticipation cette fois, avant même de lancer la suite
complète — le même piège que le ticket 5 avait déjà révélé.

**Mémorisation prévision/décision réelle** (« indicateur de confiance »,
§4) : **non construite**. Aucun AC ni TC de ce ticket ne la spécifie,
contrairement au reste — sa forme exacte resterait devinée. Documentée
comme écart ouvert (même principe que le seuil de promotion de
volatilité de F10, §1).

## 10. Reste du backlog — état final

| Ticket | Fonctionnalité | État |
|---|---|---|
| 2 | F11 — comptage tournant intelligent ⭐ | **Fait** (§3) |
| 3 | F12 — alerte de marge érodée ⭐ | **Fait** (§6) |
| 4 | F15 — contrôle d'intégrité des imports | **Fait** (§2) |
| 5 | F18 — indicateur de confiance, retour auto v1 | **Fait** (§7) |
| 6 | F14 — risque de péremption | **Fait** (§5) |
| 7 | F16 — consolidation de commande par fournisseur | **Fait** (§4) |
| 8 | F17 — diagnostic de cause d'écart ⭐ | **Fait** (§8) |
| 9 | F13 — prévision de mise en place | **Fait** (§9) |

**Les trois décisions actées** (`avancement-lot-ia-0-trois-decisions` §1,
lues avant ce backlog) :
- Journal de décision du modèle — **première brique construite** au
  ticket 5 (F18, `ModelDecisionLog`), au périmètre strict dont F18 a
  besoin — pas encore le système générique pour l'ensemble des décisions
  IA évoqué par le document. Ni F17 (ticket 8) ni F13 (ticket 9) n'y
  ajoutent quoi que ce soit à dessein (voir §8 et §9) : une hypothèse
  n'est pas une décision, et la mémorisation prévision/décision de F13
  reste un écart documenté, pas construit sur une supposition.
- Écran de comparaison en mode ombre — **non construit**, le ticket 2
  (F11) qui le débloquait est fait, reste à cadrer l'écran lui-même.
- Rejeu historique — confirmé hors périmètre, aucune action.

## 11. Critères de sortie du lot — état

- Tickets 1 à 8 construits, testés, derrière feature flag éteint : **8/8**.
  Le ticket 9 (F13), hors périmètre des critères de sortie (backlog §12 :
  « confort, à construire seulement si les tickets 1 à 8 sont faits »),
  est également fait (§9) — les 9 tickets du backlog sont donc traités.
- Journal de décision du modèle en place dès le ticket 1 : **première
  brique** (F18 §7 ; ni F17 §8 ni F13 §9 n'y ajoutent rien, à dessein).
- Écran de comparaison en mode ombre : **non fait** (attendu après ticket 2).
- NR-01 à NR-18 et la suite du Lot IA-0 toujours verts : **oui**, 391 tests
  au vert (289 IA-0 + 6 tests d'infrastructure migrations/sauvegarde
  [`test_migrations.py`/`test_backup.py`, cf. §7 — corrigés au ticket 5,
  puis de nouveau au ticket 9, pour chaque nouvelle colonne NOT NULL
  ajoutée à `ingredients`] + 11 F10 + 12 F15 + 14 F11 + 9 F16 + 6 F14 +
  14 F12 + 9 F18 + 13 F17 + 8 F13, hors ROB).
- Aucun changement visible pour un utilisateur : **vrai** pour ce qui est
  construit à date (aucun des 9 tickets n'a de routeur ni de gabarit).

## 12. Bilan de fin de lot

Les 9 tickets du backlog sont traités : 8 construits (tickets 1 à 8,
critère de sortie satisfait) + le ticket 9 (F13), non requis par les
critères de sortie mais fait quand même puisque sa propre condition
(« si les tickets 1 à 8 sont faits ») est remplie. Écarts documentés,
jamais devinés : le seuil de promotion de volatilité (F10, §1), l'écran
de comparaison en mode ombre (F11), et la mémorisation prévision/décision
réelle (F13, §9) — chacun laissé en l'état faute d'un critère
d'acceptation ou d'un cas de test qui en fixerait la forme exacte, plutôt
que construit sur une supposition.

Discipline tenue sur les 9 tickets : synthétique ou fixture locale vérifié
empiriquement avant l'écriture des tests (jamais l'inverse), non-vacuité
prouvée par cassure/restauration (jamais `git checkout` — `cp` vers un
fichier temporaire, puis retour, avec `diff` de contrôle) sur au moins
chaque règle métier significative, suite complète relancée avant chaque
commit, un commit par ticket. Trois bugs réels trouvés par les tests eux-
mêmes plutôt que par relecture (dormance en cascade F10/F11 §1/§3,
blocage circulaire du gate F18 dans son propre backtest §7, fixtures de
migration/sauvegarde ignorant une colonne NOT NULL nouvellement ajoutée
§7/§9) — le signe que la discipline attrape autre chose que des fautes de
frappe.

## 13. Prochaine session

Tickets 2 à 9 traités — le backlog transmis (9 tickets) est intégralement
couvert par ce lot. Reste, explicitement hors périmètre de ce lot et non
entamé : l'écran de comparaison en mode ombre et la mémorisation
prévision/décision de F13 (les deux items UI/gap listés en §9 ci-dessus),
et F19 (structure de données seulement, backlog : « aucune activation
avant un second restaurant et une validation juridique »).

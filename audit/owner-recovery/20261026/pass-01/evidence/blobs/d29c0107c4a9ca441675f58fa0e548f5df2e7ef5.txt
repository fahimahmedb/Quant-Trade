# Bilan — F27, apprentissage statistique réel

Hors backlog Lot IA-2 (déjà clos) : demandé explicitement par le porteur du
projet après la clôture — « Il me faut une vrai ia pas des règles ». Ce
document couvre ce seul ticket, pas un lot entier.

## Le constat qui a motivé le ticket

Tout ce qui a été construit jusqu'ici (F5 à F26) sont des RÈGLES : une
formule ou une constante que Claude Code a écrite, puis vérifiée sur un
jeu synthétique avant de la figer (`MIN_PAST_OCCURRENCES` de F20,
`cold_start_smoothing_days` de F23...). Aucune de ces valeurs n'est issue
d'un processus qui apprend depuis les données — c'est du jugement
d'ingénieur encodé, pas un système qui se forme lui-même. F27 est la
première fonctionnalité du projet où ce n'est plus vrai.

## Ce qui est construit

`app/services/ai_forecast_learned.py` — lissage exponentiel triple
(Holt-Winters additif : niveau + tendance + saisonnalité hebdomadaire),
implémenté en Python pur (aucune dépendance numpy/scipy/statsmodels —
volontaire, voir « Pourquoi pas un réseau de neurones » ci-dessous). Les
trois paramètres du modèle (α, β, γ) sont **appris par recherche en
grille** : chaque triplet candidat est jugé sur sa capacité à prédire la
dernière semaine connue de CET ingrédient à partir de tout ce qui précède
(un holdout, jamais la série entière), et le triplet qui prédit le mieux
est retenu — jamais une valeur choisie par Claude Code puis figée pour
tout le monde, contrairement à chaque constante des tickets précédents.

**Gate** : identique à F6 (6 semaines d'historique, `ai_forecast.
MIN_WEEKS_OF_SALES` réutilisée telle quelle) — une comparaison n'a de
sens que si les deux modèles se déclenchent au même moment.

**Ce que F6 ne peut structurellement pas faire** : extrapoler une
tendance. F6 est une moyenne pondérée par récence des 8 dernières
occurrences du même jour de semaine — sur une activité en croissance ou
en déclin régulier, une moyenne du passé reste toujours en retard sur la
réalité, quelle que soit la pondération. F27 extrapole la tendance
apprise (le terme `+ h × tendance` de la formule) — c'est une CAPACITÉ
nouvelle, pas juste une meilleure moyenne.

**Ce que F27 ne code PAS, contrairement à F20** : aucune notion de « jour
fermé ». F20/F6 ont une règle explicite (« zéro vente sur >= 4
occurrences »). F27 n'a rien de tel — l'indice saisonnier d'un jour
systématiquement à zéro converge vers zéro tout seul, par la même
récursion qui apprend le reste. Vérifié empiriquement sur un cas
exigeant (fermeture introduite en cours d'historique, pas dès le premier
jour — voir Non-vacuité).

**`compare_models`** étend `ai_forecast.backtest_vs_v1` (F18) de deux
candidats (v1, F6) à trois (v1, F6, F27) : même boucle exactement
(« prédire la semaine N à partir des semaines < N »), même métrique MAPE.
Le gagnant n'est jamais affirmé, toujours mesuré sur l'historique réel de
chaque ingrédient.

## Pourquoi pas un réseau de neurones

Avec quelques semaines de ventes d'un seul restaurant (l'échelle réelle
de ce projet), un modèle à beaucoup de paramètres sur-apprendrait le
bruit plutôt que le signal — ce serait un choix technique malhonnête,
pas une meilleure IA. Holt-Winters (3 paramètres, appris par ingrédient)
est un algorithme d'apprentissage statistique standard, employé
couramment pour exactement ce type de prévision de demande à faible
volume de données. Implémenté en Python pur plutôt que via `statsmodels`
(absent des dépendances du projet, qui reste volontairement léger) — un
choix de dépendance, pas une concession sur ce qui est « réellement »
appris : les mêmes équations, vérifiables ligne par ligne.

## Preuve empirique (SYN-V : tendance +1,5/jour/semaine connue, saisonnalité hebdomadaire connue)

| | Erreur moyenne vs vérité terrain connue |
|---|---|
| F6 (règle) | ~18 % |
| F27 (appris) | ~10 % |

Backtest à 3 (`compare_models`, 5 semaines rejouées) :

| Modèle | MAPE |
|---|---|
| v1 (moyenne glissante) | 12,5 % |
| F6 | 19,3 % |
| **F27** | **6,1 %** |

F27 gagne empiriquement sur ce cas — jamais supposé, mesuré par la même
méthode que celle qui a servi à activer F6 lui-même (F18, Lot IA-1).

## Addendum — la comparaison n'est pas truquée en faveur de F27

Sur demande du porteur du projet (simuler d'autres profils, et vérifier
l'accès à un vrai historique de vente). Deux jeux supplémentaires,
symétriques et contrastés :

| Jeu | Profil | Vainqueur (`compare_models`) | MAPE v1 / F6 / F27 |
|---|---|---|---|
| SYN-W | Plat, sans tendance | **v1** | 5,5 % / 5,8 % / 8,5 % |
| SYN-X | Tendance déclinante + saisonnalité | **F27** | 17,6 % / 35,0 % / 5,6 % |

Sur SYN-W, F27 est explicitement le PIRE des trois modèles — la variance
d'un modèle à 3 paramètres jugés sur une seule semaine de validation ne
se justifie pas quand il n'y a rien à extrapoler. C'est le résultat
attendu d'une comparaison honnête, pas un raté : si F27 gagnait
systématiquement, y compris sur des données où il n'a structurellement
rien à apporter, ce serait le signe d'une comparaison biaisée, pas d'un
bon modèle. SYN-X confirme, à l'inverse, que l'extrapolation de tendance
fonctionne aussi à la baisse, pas seulement à la hausse (SYN-V).

**Sur l'accès à un historique de vente réel d'un autre établissement** :
un jeu réel existe déjà dans ce dépôt (« French bakery daily sales »,
Kaggle, ~234 000 lignes, 21 mois, boulangerie française réelle),
téléchargé pour la suite de robustesse ROB (Lot IA-0). Une règle du
projet, écrite avant ce ticket (`docs/feature-plans/ia-f5-f9.md` §3.1 et
§5.4), interdit explicitement d'entraîner ou calibrer quoi que ce soit
dessus, même « pour initialiser » : les rythmes d'une boulangerie
d'ailleurs ne sont pas transférables à ce restaurant, et un modèle
pré-entraîné rendrait ses sorties inexplicables — l'inverse de ce que
« vraie IA, pas des règles » doit signifier ici (apprendre UNIQUEMENT des
données du restaurant qui l'utilise).

Ce jeu réel reste néanmoins utile dans les limites de cette règle :
`test_rob_06_f27_forecast_has_no_aberrant_values_on_real_data` (nouveau,
`tests/test_rob_external_data.py`) vérifie que F27 ne produit aucune
valeur aberrante (NaN, infini, négatif) sur de la donnée réelle sale —
exactement ce que ROB-05 vérifie déjà pour F6, ni plus ni moins. Aucun
MAPE n'est calculé ni journalisé sur ce jeu, sur aucun chemin de code :
un chiffre de performance sur une boulangerie d'ailleurs n'a pas sa place
ici, même en commentaire, tant il serait tentant de le relire plus tard
comme une preuve qu'il n'est pas.

## Non-vacuité

Cassée/restaurée sur 3 points :
- Le seuil de gate (6 semaines, aligné sur F6) — frontière exacte.
- La sélection « garder le meilleur triplet » dans `_fit` (cassée en
  gardant systématiquement le DERNIER triplet essayé, jamais le
  meilleur) — casse à elle seule 4 preuves : l'exactitude sur données à
  tendance, le test de fermeture apprise, la différenciation des
  paramètres entre deux ingrédients de profils différents, et le
  vainqueur du backtest à 3. Fait notable découvert en cours de route :
  une première tentative de cassure (restreindre la grille à un seul
  triplet fixe) n'a PAS fait échouer les tests — ce triplet particulier
  se trouvait, par coïncidence, bien fonctionner sur ces jeux precis.
  Cassure corrigée pour cibler le mécanisme de sélection lui-même plutôt
  qu'un choix de valeur, qui ne prouvait rien de fiable.
- Le choix du modèle gagnant dans `compare_models` (cassé en fixant
  toujours « v1 » plutôt que `min(...)`).

Un test a été redessiné en cours de route pour la même raison : la
fermeture d'un jour dès le TOUT PREMIER jour de l'historique se lit déjà
correctement dans l'initialisation du modèle (calculée sur la première
semaine), indépendamment de tout apprentissage ultérieur — un test sur
ce cas n'aurait rien prouvé sur la capacité d'ADAPTATION elle-même.
Corrigé en introduisant la fermeture à la semaine 5 sur 12 : seule une
vraie mise à jour récursive (pilotée par γ) peut alors corriger un indice
saisonnier initialement erroné.

10 tests, `tests/test_ai_forecast_learned.py` (7 d'origine + 3 de
l'addendum SYN-W/SYN-X). Plus 1 test de robustesse (`test_rob_06...`,
`tests/test_rob_external_data.py`, cf. addendum). SYN-V/W/X, `tests/
synthetic_data.py`.

## Mode ombre, comme F6

Aucun chemin de code n'expose ce résultat à un restaurateur. F27 existe
pour être comparé aux règles en place, pas pour les remplacer sans
preuve sur données réelles — même principe que F6 depuis le Lot IA-0.

## Limite honnête à ne pas taire

La sélection par recherche en grille n'est jugée que sur UNE semaine de
validation (holdout) — sur un jeu à faible bruit et tendance très
régulière, un triplet non retenu par la grille s'est révélé, une fois,
légèrement meilleur que le triplet effectivement choisi (voir Non-
vacuité ci-dessus). Ce n'est pas un bug : avec aussi peu de semaines de
validation possibles pour un seul restaurant, aucune méthode de
sélection ne serait parfaitement stable — c'est une limite réelle du
volume de données disponible, pas quelque chose qu'un algorithme plus
sophistiqué éliminerait complètement à cette échelle.

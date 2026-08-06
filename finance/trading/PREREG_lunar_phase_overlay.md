# Pré-enregistrement — Effet lunaire (phase de la Lune)

**Committé AVANT tout calcul.** Cycle #309 du backlog non-ML.

## Hypothèse

Anomalie documentée dans la littérature académique (Dichev & Janes
2003 ; Yuan, Zheng & Zhu 2006, *Journal of Empirical Finance*, "Are
Investors Moonstruck?") : les rendements boursiers sont historiquement
plus élevés dans les jours entourant la NOUVELLE lune que dans le
reste du mois lunaire, un effet documenté sur de nombreux marchés
internationaux et attribué à des variations d'humeur/appétit pour le
risque des investisseurs corrélées au cycle lunaire (littérature en
finance comportementale). Jamais testé dans ce backlog — famille
calendaire jusqu'ici limitée aux cycles civils (mois, semaine,
trimestre) et aux événements de marché (FOMC, expiration d'options).

## Construction data-driven (fixée ici, AVANT tout calcul)

Phase lunaire calculée par formule astronomique standard, aucune
donnée externe : `jours_depuis_ref = (date - NOUVELLE_LUNE_REF).days`,
`phase = (jours_depuis_ref mod SYNODIC_MONTH) / SYNODIC_MONTH` ∈[0,1),
avec `SYNODIC_MONTH = 29.530588853` jours et `NOUVELLE_LUNE_REF =
2000-01-06 18:14 UTC` (nouvelle lune de référence connue et publique,
utilisée classiquement pour ce type de calcul). `phase=0` = nouvelle
lune exacte, `phase=0.5` = pleine lune exacte.

`NewMoonWindow(t)` = 1 si la distance angulaire de `phase(t)` à 0 (mod
1) correspond à ≤7 jours CALENDAIRES de la nouvelle lune la plus
proche (fenêtre de 15 jours calendaires centrée sur la nouvelle lune,
reprise directement de Yuan-Zheng-Zhu 2006), sinon 0.

**Position** : `CAP=2,0x` (amplification, cohérente avec la
construction des autres effets calendaires "favorables" déjà testés
dans ce backlog — ToM #8, Halloween #17, January barometer #59) si
`NewMoonWindow(t)`, `1,0x` sinon. Seule la fenêtre NOUVELLE LUNE est
testée ici (effet positif documenté) — la fenêtre pleine lune (effet
négatif documenté) n'est PAS combinée dans ce premier test pour garder
n_trials=1 et un seul degré de liberté ; une extension symétrique
(CUT en pleine lune) pourrait faire l'objet d'un cycle séparé si
celui-ci est concluant, déclaré ici à l'avance (Règle 2).

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix. La
formule lunaire s'applique à TOUTES les dates depuis 1970 sans
restriction (contrairement aux séries macro, aucune contrainte de
disponibilité).

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule fenêtre testée : ±7 jours calendaires, valeur reprise
directement de la référence académique, pas une grille).

## Risque déclaré à l'avance

La fenêtre de ±7 jours calendaires autour de la nouvelle lune
représente environ 15/29,5 ≈ 51% du mois — une fraction élevée du
temps investi différemment, ce qui pourrait diluer l'effet statistique
documenté (généralement mesuré sur des échantillons BEAUCOUP plus
longs — décennies, plusieurs marchés combinés — que les historiques
individuels de ce backlog). Un résultat FAIL par manque de puissance
statistique plutôt que par absence réelle d'effet est plausible et
sera rapporté honnêtement, sans redéfinir la fenêtre après observation.

## Anti-cheat

Ce fichier committé avant `nonml_lunar_phase_overlay_backtest.py`.
Aucune nouvelle donnée (formule astronomique publique, vérifiable
indépendamment). Sortie :
`results/nonml_lunar_phase_overlay_result.md`.

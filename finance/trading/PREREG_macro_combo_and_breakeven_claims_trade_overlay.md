# Pré-enregistrement — Combinaison ET : breakeven inflation + demandes continues + balance commerciale

**Committé AVANT tout calcul.** Cycle #333 du backlog non-ML.

## Contexte et justification de non-redondance

Suite directe et méthodologiquement bornée du #334 (combinaison
MAJORITAIRE ≥2/3 du même trio de signaux, FAIL 3/5 de justesse, mais
meilleur profil Sharpe composite du sous-thread récent). Ce cycle
teste la logique ET (les 3 gates simultanément actifs) sur EXACTEMENT
le même trio fixé (#200 breakeven inflation, #322 demandes continues
de chômage, #327 balance commerciale) — **AUCUN nouveau signal, AUCUN
nouveau trio testé**, seule la logique de combinaison change. Cette
pratique est directement précédentée dans ce backlog par le sous-
thread #296-#305, qui a testé ET/OU/majorité comme expériences
séparées et pré-enregistrées sur le même trio de signaux originel.
Conformément à la discipline anti-snooping déjà appliquée à ce
sous-thread, AUCUNE extension supplémentaire (4e signal, autre trio)
ne sera engagée après ce cycle sans nouvelle hypothèse économique
distincte — décision déjà actée au backlog #332.

## Hypothèse

**Prédiction explicite testable, déclarée AVANT tout calcul** : la
logique ET est structurellement PLUS CONSERVATRICE que la majorité
(la porte n'est active que si les 3 signaux s'accordent
simultanément) — elle devrait réduire encore davantage le taux
d'activation et le turnover (donc les coûts de retournement) par
rapport à la majorité (#334), mais au prix d'un risque symétrique :
la porte pourrait devenir trop rarement active pour capter un
rendement défensif suffisant lors des véritables épisodes de stress
(faux négatifs si un seul des 3 signaux ne confirme pas à temps).
L'issue nette (amélioration ou dégradation par rapport au #334) n'est
PAS tranchée à l'avance — c'est précisément la question testée par ce
cycle, dans la continuité de la logique déjà appliquée aux tests
ET/OU/majorité du sous-thread #296-#305 (où le AND avait déjà
initialement donné le meilleur résultat, #296 PASS 5/5).

## Adaptation technique : réutilisation stricte, Règle 7

Réutilisation intégrale et directe (imports Python, aucune
réimplémentation) des mêmes 3 fonctions de porte déjà validées et
committées au #334 : `load_t10yie_lag`/`expanding_tercile_cut_high`
de `nonml_inflation_breakeven_overlay_backtest.py` (#200) ;
`build_continuing_claims_yoy_series`/`load_continuing_claims_yoy_lag`
de `nonml_continuing_claims_overlay_backtest.py` avec
`expanding_tercile_cut_high` de `nonml_jobless_claims_overlay_backtest.py`
(#322) ; `build_trade_balance_series`/`load_trade_balance_lag` de
`nonml_trade_balance_overlay_backtest.py` avec
`expanding_tercile_cut_low` de `nonml_m2_growth_overlay_backtest.py`
(#327). Seule la fonction de combinaison change : `and_3_of_3`
(les 3 gates valent CUT simultanément) au lieu de `majority_2_of_3`
du #334. `CUT=0,5x`, `COST_BPS=5,0` réutilisés sans changement.

## Définition (fixée ici, AVANT tout calcul)

- `Gate200(t)`, `Gate322(t)`, `Gate327(t)` = portes booléennes
  individuelles, identiques au #334, aucune modification.
- `GateAND(t)` = 1 si les 3 gates ci-dessus valent 1 SIMULTANÉMENT,
  sinon 0.
- **Position** : `CUT=0,5x` si `GateAND(t)`, `1,0x` sinon.
- Univers/période limités à l'intersection des 3 séries sous-jacentes,
  identique au #334 (démarrage contraint par T10YIE, 2003+).

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule logique de combinaison testée dans ce cycle — ET — pas de
grille).

## Risque déclaré à l'avance

Comme pour tout ce backlog, le design purement défensif (CUT fixe,
pas d'amplification) limite structurellement le gain de rendement même
en cas de signal composite valide. Par ailleurs, un taux d'activation
trop faible (porte ET rarement déclenchée) pourrait rendre le résultat
statistiquement peu significatif même s'il apparaît favorable sur les
quelques épisodes où elle s'active — à examiner honnêtement dans le
résultat brut (% temps coupé rapporté explicitement, comme pour tous
les cycles précédents). Rapporté honnêtement dans tous les cas, sans
retuning de la logique de combinaison après observation du résultat,
et **ceci clôt ce sous-thread de combinaison** (aucune 3e logique
d'ET/OU/majorité supplémentaire ne sera testée sur ce trio sans
nouvelle hypothèse économique distincte, décision actée au #332).

## Anti-cheat

Ce fichier committé avant tout calcul (aucune nouvelle donnée à
récupérer, seule une recombinaison des 3 séries déjà en local). Sortie :
`results/nonml_macro_combo_and_breakeven_claims_trade_overlay_result.md`.

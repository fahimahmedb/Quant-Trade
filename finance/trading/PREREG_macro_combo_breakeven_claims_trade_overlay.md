# Pré-enregistrement — Combinaison majoritaire (2/3) : breakeven inflation + demandes continues + balance commerciale

**Committé AVANT tout calcul.** Cycle #332 du backlog non-ML.

## Contexte et justification de non-redondance

Après 12 FAIL consécutifs (#320-#331) sur des constructions macro-
externes MONO-SIGNAL, et après avoir confirmé explicitement au cycle
précédent (#331) qu'aucune nouvelle CATÉGORIE DE DONNÉE mono-signal
librement disponible et non-redondante n'a été trouvée, ce cycle
explore un axe DIFFÉRENT déjà validé méthodologiquement dans ce
backlog : la COMBINAISON de plusieurs signaux macro déjà testés
individuellement (sous-thread #296-#305, qui a produit plusieurs PASS
niveau 1 via une logique ET/majorité, notamment #299 majorité≥2/3
PASS). **Ce cycle N'EST PAS une continuation du sous-thread #296-#305**
(explicitement clos au #305, qui combinait NFCI/BAA10Y/défaut carte de
crédit) : il applique la MÊME méthodologie de combinaison à un
ENSEMBLE ENTIÈREMENT DIFFÉRENT de 3 signaux, jamais combinés
auparavant, testés cette session :
- **#200 — Anticipations d'inflation breakeven** (T10YIE, tercile
  expanding le plus haut = défensif) : **seul PASS niveau 1 net de
  toute la famille macro-externe défensive**, 5/5 marchés.
- **#322 — Demandes continues de chômage** (CCSA, tercile expanding le
  plus haut = défensif) : FAIL 1/5 sur le critère composé, mais Sharpe
  bat BH sur les 5 marchés SANS EXCEPTION — le rendement échoue
  probablement à cause du coût de retournement (whipsaw) d'un signal
  individuellement bruité.
- **#327 — Balance commerciale** (BOPGSTB, tercile expanding le plus
  bas = défensif) : FAIL 1/5 sur le critère composé, même profil
  Sharpe fort (5/5) que le #322.

## Hypothèse

**Prédiction explicite testable, déclarée AVANT tout calcul** : les
trois signaux mesurent des dimensions économiques authentiquement
distinctes (anticipations de marché sur l'inflation, persistance du
chômage, déséquilibre commercial extérieur) et deux d'entre eux
(#322/#327) partagent le même symptôme — Sharpe individuellement fort
mais rendement pénalisé par le bruit/coûts de retournement. Une
combinaison MAJORITAIRE (au moins 2 des 3 gates actifs) est
susceptible de FILTRER une partie du bruit individuel de chaque signal
(un gate isolé actif par erreur ne suffit pas à déclencher la
position défensive) tout en préservant la composante commune de
signal lors des véritables changements de régime, ce qui pourrait
réduire le taux de retournement net et améliorer le profil
rendement/coût par rapport aux signaux pris isolément.

## Adaptation technique : réutilisation stricte, Règle 7

Réutilisation intégrale et directe (imports Python, aucune
réimplémentation) des fonctions déjà validées et committées :
`load_t10yie_lag`/`expanding_tercile_cut_high` de
`nonml_inflation_breakeven_overlay_backtest.py` (#200) ;
`build_continuing_claims_yoy_series`/`load_continuing_claims_yoy_lag` de
`nonml_continuing_claims_overlay_backtest.py` (#322, avec
`expanding_tercile_cut_high` du #291 déjà importé par ce module) ;
`build_trade_balance_series`/`load_trade_balance_lag` de
`nonml_trade_balance_overlay_backtest.py` (#327, avec
`expanding_tercile_cut_low` du #203). Logique de combinaison
`majority_2_of_3` : mécaniquement identique à la fonction majoritaire
déjà validée au #299 (comptage de votes ≥2 sur 3 gates booléens),
réimplémentée ici pour ces 3 gates précis (aucun paramètre libre).
`CUT=0,5x`, `COST_BPS=5,0` réutilisés sans changement.

## Définition (fixée ici, AVANT tout calcul)

- `Gate200(t)`, `Gate322(t)`, `Gate327(t)` = portes booléennes
  individuelles de #200/#322/#327 (tercile expanding déjà défini dans
  chaque script d'origine, aucune modification).
- `GateMajority(t)` = 1 si au moins 2 des 3 gates ci-dessus valent 1,
  sinon 0.
- **Position** : `CUT=0,5x` si `GateMajority(t)`, `1,0x` sinon.
- Univers/période limités à l'intersection des 3 séries sous-jacentes
  déjà disponibles (aucune nouvelle donnée).

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule logique de combinaison testée — majorité 2/3 — pas de
grille, pas d'essai ET/OU non déclaré).

## Risque déclaré à l'avance

**Risque explicite** : la combinaison pourrait au contraire DÉGRADER
le profil du #200 (seul PASS actuel) en le diluant avec 2 signaux
individuellement FAIL, si le bruit des #322/#327 domine plutôt que de
s'annuler par le vote majoritaire — schéma déjà observé dans certaines
variantes du sous-thread #296-#305 où l'ajout d'un signal
supplémentaire n'améliorait pas systématiquement le résultat. Comme
pour tout ce backlog, le design purement défensif (CUT fixe, pas
d'amplification) limite structurellement le gain de rendement même en
cas de signal composite valide. Rapporté honnêtement dans tous les
cas, sans retuning de la logique de vote ni des seuils individuels
après observation du résultat.

## Anti-cheat

Ce fichier committé avant tout calcul (aucune nouvelle donnée à
récupérer, seule une recombinaison des 3 séries déjà en local). Sortie :
`results/nonml_macro_combo_breakeven_claims_trade_overlay_result.md`.

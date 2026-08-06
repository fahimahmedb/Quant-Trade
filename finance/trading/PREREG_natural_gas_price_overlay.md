# Pré-enregistrement — Prix du gaz naturel US Henry Hub (FRED DHHNGSP)

**Committé AVANT tout calcul.** Cycle #326 du backlog non-ML.

## Hypothèse

Le prix spot du gaz naturel US (FRED `DHHNGSP`, Henry Hub, quotidien
depuis 1997) est un 3e signal matière première après le pétrole WTI
(#283, FAIL 2/5) et le cuivre (#284, FAIL 3/5) — un choc énergétique
ÉCONOMIQUEMENT DISTINCT des deux précédents : contrairement au pétrole
(marché mondial, transport facile, corrélé aux cycles géopolitiques) et
au cuivre (proxy de demande industrielle mondiale), le gaz naturel US a
une dynamique largement RÉGIONALE (marché nord-américain peu connecté
au marché mondial avant l'essor du GNL), une forte SAISONNALITÉ de
stockage (demande hivernale de chauffage), et un lien plus direct avec
les coûts de production électrique et industriels domestiques. Une
hausse rapide du prix du gaz naturel est documentée comme un facteur
de pression sur les coûts énergétiques des ménages et entreprises US,
avec un impact potentiellement plus DOMESTIQUE que le pétrole (marché
mondial fongible).

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `DHHNGSP` (gratuite,
quotidienne, 1997-2026, disponibilité confirmée par fetch le
06/08/2026, `data/natural_gas_daily.csv`, aucune valeur négative
constatée contrairement à l'épisode WTI du 20/04/2020). Réutilisation
INTÉGRALE de la construction exacte du #283 (pétrole WTI) : fenêtre de
variation `RET_WINDOW=21` jours, `expanding_tercile_cut_high` (tercile
le plus HAUT = défensif, une hausse rapide = choc de coût
inflationniste), alignement causal `reindex(ffill)`+`shift(1)` sans
décalage calendaire additionnel (série quotidienne directement
disponible, même convention que pétrole/cuivre/VIX/dollar), `CUT=0,5x`,
`COST_BPS=5,0` — toutes les constantes et fonctions importées
directement de `nonml_oil_price_shock_overlay_backtest.py` (Règle 7),
seule la série sous-jacente change.

## Définition (fixée ici, AVANT tout calcul)

- `GasChange(t)` = `log(DHHNGSP(t)/DHHNGSP(t-21))` (variation sur 21
  séances, même fenêtre que le #283/#284/#198).
- `GateGas(t)` = 1 si `GasChange_lag(t-1)` (décalée d'une séance via
  `reindex(ffill)`+`shift(1)`) est dans son tercile expanding le plus
  HAUT (hausse la plus rapide du gaz naturel = choc de coût
  inflationniste), sinon 0.
- **Position** : `CUT=0,5x` si `GateGas(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — hausse rapide du gaz = défensif — pas de
grille).

## Risque déclaré à l'avance

Comme les deux variantes précédentes du canal matière première
(#283 pétrole FAIL 2/5, #284 cuivre FAIL 3/5), et conformément au
schéma dominant de toute la famille macro-externe défensive, un
résultat FAIL est plausible, avec le design purement défensif limitant
structurellement le rendement même si le signal identifie un vrai
choc. Par ailleurs, le gaz naturel Henry Hub est documenté comme l'une
des matières premières les plus VOLATILES et SAISONNIÈRES (variations
de prix de plusieurs dizaines de % en quelques semaines liées aux
prévisions météo hivernales), ce qui pourrait générer un taux de
coupure élevé et bruité indépendamment de tout contenu informatif sur
le régime de marché actions — limite reconnue à l'avance. Rapporté
honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/natural_gas_daily.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_natural_gas_price_overlay_result.md`.

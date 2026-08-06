# Pré-enregistrement — Panel élargi à 4 signaux (défaut carte + NFCI + BAA10Y + corrélation NDX-DAX), vote ≥3/4

**Committé AVANT tout calcul.** Cycle #303 du backlog non-ML.

## Hypothèse

Les trois constructions de combinaison déjà testées sur le trio défaut
carte (#286) + NFCI (#291) + BAA10Y (#199) — ET (#296), OU (#298),
majorité ≥2/3 (#301), et le sizing continu (#303) — ont toutes plafonné
à 2/5 (voire moins) à leur batterie Règle 9 respective (#297, #300,
#302), malgré des PASS niveau 1 nets. Ce cycle teste si l'AJOUT d'un
4e signal ÉCONOMIQUEMENT DISTINCT — la corrélation cross-marché
NDX-DAX (#193, PASS niveau 1, seul signal macro-externe de la famille
mesurant la CONTAGION INTERNATIONALE/perte de diversification
géographique, plutôt que le stress d'endettement des ménages ou le
prix du risque de crédit) — améliore la généralisation du panel, par
diversification économique des sources de signal plutôt que par un
changement de la logique de combinaison (déjà explorée sous 3 formes
sans succès Règle 9). Vote majoritaire ≥3/4 (nécessite l'accord d'au
moins 3 des 4 signaux), seuil proportionnellement analogue au ≥2/3
du #301 (les deux exigent ~2/3 des votes disponibles).

## Adaptation technique : réutilisation stricte, Règle 7

Aucune nouvelle donnée, aucune modification des définitions déjà
validées et committées :
- `build_delinquency_series()` / `load_delinquency_lag()` du #286.
- `build_nfci_series()` / `load_nfci_lag()` du #291.
- `load_baa10y_lag()` du #199.
- `build_corr_series()` / `load_corr_lag()` du #193 (corrélation
  Pearson glissante 60j NDX-DAX).
- `expanding_tercile_gate_high()` du #296, générique, étendue ici à
  une 4e série sans modification.

## Définition (fixée ici, AVANT tout calcul)

- `GateDelinq(t)`, `GateNFCI(t)`, `GateBAA10Y(t)`, `GateCorr(t)` = 1 si
  la série correspondante est dans SON PROPRE tercile expanding le
  plus haut, sinon 0 (identique aux #286/#291/#199/#193/#296).
- `Votes(t) = GateDelinq(t) + GateNFCI(t) + GateBAA10Y(t) + GateCorr(t)`.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier, réutilisé à l'identique) si `Votes(t) >= 3`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.
Fenêtre testable réduite au recoupement des quatre disponibilités
(DRCCLACBS depuis 1991 reste la contrainte la plus restrictive,
identique au #296/#298/#301/#303) ; la corrélation NDX-DAX (#193, dès
que les deux calendriers de prix se recoupent) ne réduit pas
davantage cette fenêtre pour les marchés testés autres que DAX
lui-même.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule règle de vote testée, pas de grille de seuils).

## Risque déclaré à l'avance

Le signal de corrélation NDX-DAX est, par construction, IDENTIQUEMENT
NUL comme information supplémentaire pour le marché DAX lui-même
(circularité partielle — DAX est l'une des deux composantes de la
corrélation) : un risque de léger biais en faveur/défaveur de DAX est
possible et sera signalé si observé, sans en faire une conclusion
causale forte (déjà le cas structurellement pour le #193 seul).
Ajouter un 4e signal au vote pourrait aussi diluer davantage
l'activation combinée (le seuil ≥3/4 est mécaniquement plus rare qu'un
≥2/3 si les 4 signaux ne sont pas fortement corrélés entre eux) —
risque similaire à celui déjà observé au #296 (activation réduite),
rapporté honnêtement sans retuning du seuil de vote après observation.

## Anti-cheat

Ce fichier committé avant `nonml_delinquency_nfci_baa10y_corr_majority_overlay_backtest.py`.
Aucune nouvelle donnée. Sortie :
`results/nonml_delinquency_nfci_baa10y_corr_majority_overlay_result.md`.

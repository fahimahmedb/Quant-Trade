# Pré-enregistrement — Porte majoritaire (≥2 sur 3) défaut carte + NFCI + spread BAA10Y

**Committé AVANT tout calcul.** Cycle #299 du backlog non-ML.

## Hypothèse

Les cycles #296 (ET, PASS net 5/5) et #298 (OU, FAIL 3/5) ont montré
que, pour le COUPLE défaut carte (#286) + NFCI (#291), la sélectivité
(intersection) domine la couverture large (union). Ce cycle teste une
TROISIÈME construction, structurellement différente des deux
précédentes : un **vote majoritaire à TROIS signaux** — défaut carte
(#286), NFCI (#291) et spread de crédit corporate BAA10Y (#199, FAIL
1/5 globalement mais dont le Sharpe battait Buy&Hold sur les 5 marchés
SANS EXCEPTION, comme le #291 puis le #296). Position défensive dès
qu'AU MOINS 2 des 3 signaux de stress sont actifs simultanément — ni
l'exigence stricte des 3 (plus restrictif que le #296 à 2 signaux),
ni la simple présence d'1 seul (équivalent à une union à 3 termes,
prévisiblement encore plus sur-active que le #298 déjà FAIL par
sur-couverture). L'hypothèse est qu'un vote à 2 sur 3 absorbe le bruit
idiosyncratique de chaque composante individuelle (comme une porte ET
à 2) tout en restant moins fragile qu'une porte ET à 3 signaux (qui
serait mécaniquement encore plus rare que celle du #296, déjà
identifiée comme un facteur de dilution de la puissance statistique
Règle 9 au #297).

## Adaptation technique : réutilisation stricte, Règle 7

Aucune nouvelle donnée, aucune modification des définitions déjà
validées et committées :
- `build_delinquency_series()` / `load_delinquency_lag()` du #286.
- `build_nfci_series()` / `load_nfci_lag()` du #291.
- `load_baa10y_lag()` du #199 (`nonml_credit_spread_overlay_backtest.py`).
- `expanding_tercile_gate_high()` du #296, générique, appliquée aux
  TROIS séries (déjà appliquée à 2 séries au #296/#300, extension
  directe à une 3e sans modification de la fonction elle-même).

## Définition (fixée ici, AVANT tout calcul)

- `GateDelinq(t)`, `GateNFCI(t)`, `GateBAA10Y(t)` = 1 si la série
  correspondante (`DRCCLACBS_lag`, `NFCI_lag`, `BAA10Y_lag`) est dans
  SON PROPRE tercile expanding le plus haut, sinon 0 (identique aux
  #286/#291/#199/#296).
- `Votes(t) = GateDelinq(t) + GateNFCI(t) + GateBAA10Y(t)`.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier, réutilisé à l'identique) si `Votes(t) >= 2`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.
Fenêtre testable réduite au recoupement des trois disponibilités
(BAA10Y disponible depuis 1986, DRCCLACBS depuis 1991, NFCI depuis
1971 — la contrainte la plus restrictive, DRCCLACBS, borne le début de
la fenêtre testable, comme au #296/#300).

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule règle de vote testée, pas de grille de seuils de vote).

## Risque déclaré à l'avance

Le vote à 2/3 est structurellement PLUS PERMISSIF que l'ET à 2 signaux
du #296 (il suffit que 2 des 3 signaux soient actifs, peu importe
lesquels, alors que le #296 exigeait l'accord de CES DEUX signaux
précis) — le temps actif combiné sera donc probablement intermédiaire
entre le #296 (sélectif) et le #298 (union, sur-actif). Le résultat
pourrait reproduire soit le schéma favorable du #296 (si la
sélectivité effective reste suffisante), soit celui défavorable du
#298 (si l'ajout d'un 3e signal fragile élargit trop l'activation) —
rapporté honnêtement quel que soit le cas, sans retuning du seuil de
vote après observation.

## Anti-cheat

Ce fichier committé avant `nonml_delinquency_nfci_baa10y_majority_overlay_backtest.py`.
Aucune nouvelle donnée. Sortie :
`results/nonml_delinquency_nfci_baa10y_majority_overlay_result.md`.

# Pré-enregistrement — Volume RELATIF de l'indice comme porte défensive

**Committé AVANT tout calcul.** Cycle #307 du backlog non-ML.

## Hypothèse

Le #308 (volume BRUT de l'indice, tercile expanding) a FAIL (1/4) à
cause d'une non-stationnarité identifiée et quantifiée : la croissance
séculaire massive du volume brut sur les marchés à historique long
(NDX ×22,6, Russell 2000 ×26,0, S&P 500 ×306,5 entre les 5 premières et
les 5 dernières années) biaise mécaniquement le tercile EXPANDING vers
un taux de coupure anormalement élevé (83-93%), sans rapport avec un
vrai régime de stress. Ce cycle corrige DIRECTEMENT ce défaut structurel
par une NORMALISATION standard (technique de l'oscillateur de volume) :
au lieu du niveau brut, utiliser le RATIO du volume du jour à sa propre
moyenne mobile glissante 252 séances — un ratio proche de 1 signifie
un volume "normal" quel que soit le niveau absolu du marché à cette
époque, un ratio élevé signale un pic RELATIF (capitulation/panique),
indépendamment de la taille structurelle du marché.

## Adaptation technique : réutilisation partielle, Règle 7

Réutilise `load_volume()` du #308 SANS modification. Nouvelle fonction
`volume_ratio(vol)` = `vol(t) / MA_252(vol)[t]` (moyenne mobile
glissante causale, `pandas.rolling(252).mean()` puis décalage d'une
séance identique au #308 — volume connu à la clôture de t-1). Même
`expanding_tercile_gate_high()` générique du #296 appliquée au RATIO
au lieu du niveau brut.

## Définition (fixée ici, AVANT tout calcul)

- `VolRatio(t) = Vol(t) / MA_252(Vol)(t)`.
- `GateVol(t)` = 1 si `VolRatio(t-1)` est dans son tercile expanding le
  plus haut, sinon 0 (même construction tercile-expanding que le #308,
  seule la variable d'entrée change : ratio au lieu de niveau brut).
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier, réutilisé à l'identique) si `GateVol(t)`, `1,0x` sinon.

## Univers et période

Mêmes 4 marchés que le #308 : NDX-100, Russell 2000, S&P 500, DAX
(Composite exclu, volume=0). Fenêtre testable réduite de 252 séances
supplémentaires par rapport au #308 (MA_252 nécessite 252 observations
avant sa première valeur), effet mineur sur des historiques de
plusieurs milliers de séances.

## Critère de succès (pré-enregistré, identique au #308)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 3 des 4 marchés testables** (coûts 5 bps).
n_trials=1 (une seule fenêtre MA testée : 252j, fenêtre standard d'une
année de bourse, pas une grille).

## Risque déclaré à l'avance

Le ratio au volume moyen glissant retire la tendance de NIVEAU mais
PAS nécessairement une éventuelle tendance de VARIANCE (le volume
pourrait devenir structurellement plus volatil, pas seulement plus
élevé, au fil des décennies — l'électronification du trading a
probablement augmenté la variance relative du volume, pas seulement
son niveau). Un taux de coupure encore élevé (bien que moins extrême
qu'au #308) resterait possible et sera rapporté honnêtement, sans
retuning du seuil de tercile après observation.

## Anti-cheat

Ce fichier committé avant `nonml_relative_index_volume_overlay_backtest.py`.
Aucune nouvelle donnée. Sortie :
`results/nonml_relative_index_volume_overlay_result.md`.

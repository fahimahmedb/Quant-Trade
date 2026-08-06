# Pré-enregistrement — Volume anormal de l'indice comme porte défensive

**Committé AVANT tout calcul.** Cycle #306 du backlog non-ML.

## Hypothèse

Le volume quotidien AGRÉGÉ de l'indice (pas le volume par titre
individuel, déjà exploré aux #258/#261 et reclassé FAIL sous univers
point-in-time réel au #264 pour un problème de survivorship bias
propre à la SÉLECTION de titres) n'a jamais été utilisé dans ce
backlog comme signal de RÉGIME. Anomalie documentée en analyse
technique et en microstructure : les pics de volume anormalement
élevés coïncident le plus souvent avec des phases de capitulation,
panique de vente ou incertitude accrue (volume de "climax") plutôt
qu'avec une accumulation saine — un volume anormalement élevé serait
donc un signal de stress, motivant une position défensive. Comme ce
signal est calculé sur l'ensemble de l'indice (pas une sélection de
titres candidats), il ne souffre PAS du biais de survivance qui a fait
échouer #258/#261 : c'est une observation de marché agrégée, structurellement
analogue aux signaux macro-externes déjà validés (#286/#291/#199),
mais tirée du prix/volume de l'indice lui-même plutôt que d'une série
macro-économique externe.

## Adaptation technique

**Limite de données déclarée à l'avance** : `data/nasdaq_composite_daily.txt`
a un volume documenté à 0 dans tout l'historique (voir docstring de
`data_loader.py` et CLAUDE.md) — Composite est donc EXCLU de ce test,
contrairement à la quasi-totalité des cycles macro-externes de ce
backlog qui testent sur 5 marchés. Univers réduit à 4 marchés (NDX-100,
Russell 2000, S&P 500, DAX), tous confirmés avec un volume non-nul
dans `data/*.txt`. Le critère de succès est donc ajusté à ≥3/4 marchés
— même adaptation proportionnelle que le #170 (GJR-vol-forecast, testé
sur 4 marchés validés au SPA avec un seuil ≥3/4).

Nouvelle fonction `load_volume(path)` à ajouter (lecture directe du
fichier tabulé, colonne `vol` actuellement ignorée par
`data_loader.load_ohlc`), aucune modification de `load_ohlc` elle-même
(Règle 7 : n'affecte aucun cycle existant qui dépend de cette
fonction).

## Définition (fixée ici, AVANT tout calcul)

- `Vol(t)` = volume quotidien brut de l'indice, lu directement depuis
  `data/*.txt` (colonne `vol`).
- `GateVol(t)` = 1 si `Vol(t-1)` (décalage d'une séance, purement
  causal — pas de décalage de publication supplémentaire nécessaire
  car le volume de la séance J est connu à la clôture de J, disponible
  pour la décision du J+1) est dans son tercile expanding le plus
  haut, sinon 0.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier, réutilisé de toute la famille macro-externe) si
  `GateVol(t)`, `1,0x` sinon.

## Univers et période

4 marchés : NDX-100, Russell 2000, S&P 500, DAX (`data/*.txt`, chacun
sur son historique complet disponible). Composite exclu (volume=0).

## Critère de succès (pré-enregistré, ajusté à 4 marchés)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 3 des 4 marchés testables** (coûts 5 bps).
n_trials=1 (une seule construction testée, pas de grille).

## Risque déclaré à l'avance

Le volume d'indice agrégé est TRÈS BRUYANT au jour le jour (contraste
avec les séries macro mensuelles/hebdomadaires déjà testées, beaucoup
plus lisses) — un risque que le signal soit essentiellement du bruit
sans structure de régime exploitable est réel et sera rapporté
honnêtement si constaté. Par ailleurs, le volume d'un indice PEUT avoir
une tendance structurelle de long terme (croissance séculaire du
volume de marché sur plusieurs décennies pour NDX-100/S&P 500, non
liée au risque) qui pourrait fausser un tercile EXPANDING (les
niveaux anciens systématiquement plus bas biaiseraient le seuil vers
le bas) — risque similaire à celui déjà observé et confirmé bénin pour
d'autres séries à tendance (ex. Composite fenêtre courte #286/#289/
#292/#294/#295), rapporté tel quel sans retuning.

## Anti-cheat

Ce fichier committé avant `nonml_index_volume_overlay_backtest.py`.
Aucune nouvelle donnée externe (colonne déjà présente dans les
fichiers existants). Sortie :
`results/nonml_index_volume_overlay_result.md`.

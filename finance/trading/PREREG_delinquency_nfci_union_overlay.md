# Pré-enregistrement — Porte combinée (OU) défaut carte de crédit + NFCI

**Committé AVANT tout calcul.** Cycle #298 du backlog non-ML.

## Hypothèse

Le #296 (porte ET défaut carte #286 + NFCI #291) a obtenu un PASS net
SANS EXCEPTION sur les 5 marchés — mais sa batterie Règle 9 (#297,
2/5) a montré que l'intersection stricte, mécaniquement plus rare,
n'améliore pas la stabilité temporelle ni la significativité
statistique par rapport aux composantes individuelles. Ce cycle teste
la construction structurellement OPPOSÉE : l'UNION (OU) des deux
mêmes portes — position défensive dès qu'AU MOINS UN des deux signaux
de stress est actif, plutôt que d'exiger l'accord des deux. Hypothèse
: une couverture défensive plus large capture davantage d'épisodes de
stress réels (au prix d'un temps actif plus élevé, donc potentiellement
plus de manque à gagner en phase haussière) — direction opposée et
donc informative par rapport au #296. Seul précédent de type union
dans ce backlog est calendaire (#21 ToM∪Halloween, #54 vol-targeting
gaté par cette union), jamais testé avec des signaux macro-externes.

## Adaptation technique : réutilisation stricte, Règle 7

Aucune nouvelle donnée, aucune modification des trois définitions déjà
validées et committées :
- `build_delinquency_series()` / `load_delinquency_lag()` du #286.
- `build_nfci_series()` / `load_nfci_lag()` du #291.
- `expanding_tercile_gate_high()` du #296 (retourne un booléen tercile
  expanding le plus haut, réutilisée telle quelle, importée directement
  du module `nonml_delinquency_nfci_combined_overlay_backtest`).

## Définition (fixée ici, AVANT tout calcul)

- `GateDelinq(t)` = 1 si `DRCCLACBS_lag(t-1)` est dans son tercile
  expanding le plus haut (identique au #286/#296), sinon 0.
- `GateNFCI(t)` = 1 si `NFCI_lag(t-1)` est dans son tercile expanding
  le plus haut (identique au #291/#296), sinon 0.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier, réutilisé à l'identique) si `GateDelinq(t) OR GateNFCI(t)`
  (au moins un des deux signaux indique un stress), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule combinaison OU testée, pas de grille).

## Risque déclaré à l'avance

Le temps actif combiné (union) sera mécaniquement PLUS ÉLEVÉ que
chaque composante individuelle et que l'intersection du #296 (l'union
de deux ensembles est toujours ≥ à chacun des deux) — un risque
symétrique à celui du #296 est possible : si la porte est active trop
souvent, elle risque de couper l'exposition pendant des phases
haussières trop fréquemment, dégradant le rendement sans bénéfice de
protection supplémentaire suffisant (schéma déjà observé pour des
portes larges comme #178 vol des taux, 49-74% du temps). Rapporté
honnêtement si constaté, sans retuning.

## Anti-cheat

Ce fichier committé avant `nonml_delinquency_nfci_union_overlay_backtest.py`.
Aucune nouvelle donnée. Sortie :
`results/nonml_delinquency_nfci_union_overlay_result.md`.

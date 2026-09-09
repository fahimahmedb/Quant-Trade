# Pré-enregistrement — Stratégie B : Score multi-facteurs /10 (daily)

**Committé AVANT tout calcul, AVANT le script de backtest.** Stratégie
demandée explicitement par l'utilisateur (specs fournies telles quelles,
désignée « Stratégie B — notre stratégie principale » dans l'échange, en
comparaison directe avec la Stratégie A déjà testée dans
`PREREG_daily_breakout_baseline.md`). Réutilise le **même moteur
d'exécution** que la Stratégie A (entrée/stop/cible, dimensionnement,
coûts) pour que la comparaison A vs B porte uniquement sur la génération
du signal, pas sur des différences de moteur.

## Spécification du score (fixée telle que fournie par l'utilisateur, aucun
paramètre ajusté après avoir vu un résultat)

10 facteurs binaires évalués à la clôture du jour t (aucune donnée future) :

| Bloc | Facteur | Points |
|---|---|---|
| A. Tendance | `close(t) > SMA50(t)` | 1 |
| A. Tendance | `SMA50(t) > SMA200(t)` | 1 |
| B. Structure | `close(t) > close(t-1)` | 1 |
| B. Structure | `close(t) > SMA20(t)` | 1 |
| C. Breakout | `close(t) > max(high[t-20..t-1])` (20j, décalé 1j, aujourd'hui exclu — même convention que la Stratégie A) | 1 |
| C. Breakout | `close(t) > max(high[t-50..t-1])` (50j, même convention) | 1 |
| D. Volume | `volume(t) > SMA20(volume)(t)` | 1 |
| E. RSI | `50 ≤ RSI14(t) ≤ 75` (RSI de Wilder, `prediction.py::_rsi`, identique à la Stratégie A) | 1 |
| F. Momentum | `close(t) > close(t-20)` (momentum 20 jours positif) | 2 |

**Total maximum théorique = 10 points.**

### Limitation de données — facteur Volume (déclarée ici, avant tout calcul)

`data_loader.py` documente explicitement que la colonne volume du fichier
source est **toujours à zéro / inutilisable** (`load_ohlc` ne la charge
même pas). Le facteur D (« Volume > SMA20 volume », 1 point) est donc
**structurellement impossible à valider** sur ce jeu de données : il vaut
0 point pour toutes les séances, sans exception, par construction — ce
n'est ni un bug ni un choix de modélisation, c'est une contrainte du
jeu de données déclarée a priori. **Le score maximum atteignable sur le
Composite est donc 9/10, jamais 10/10.** Ceci est documenté ici, avant
tout calcul, pour ne pas ressembler à une excuse a posteriori si le
résultat est un FAIL.

## Règle de décision (verrouillée)

Grille complète de référence (fournie par l'utilisateur, à titre
descriptif uniquement) :

| Score | Décision |
|---|---|
| 0–5 | Pas de trade |
| 6 | Setup faible / demi-risque possible |
| ≥7 | Signal |
| ≥8 | Signal très fort |

**Seul le seuil ≥7/10 est verrouillé comme règle de décision testée et
utilisée pour le critère PASS/FAIL** — citation explicite de
l'utilisateur : *« Pour la validation hors-échantillon, on avait surtout
verrouillé ≥7/10 afin de ne pas sélectionner après coup le meilleur
résultat. »* Les seuils 6 et 8 ne sont **pas** des critères de décision
alternatifs testés ici ; s'ils sont mentionnés dans le résultat, ce sera
à titre strictement descriptif/non-décisionnel (ex. nombre de séances à
score=6 ou ≥8), jamais pour choisir après coup le seuil le plus
favorable. `n_trials=1` sur la règle de décision.

## Moteur d'exécution (identique à la Stratégie A, pour comparabilité directe)

- **Signal d'entrée jour t** = `score(t) ≥ 7` ET aucune position ouverte
  à la clôture de t.
- **Entrée** : à l'ouverture de t+1 (`open(t+1)`).
- **ATR** : ATR14 de Wilder (`prediction.py::_atr`), figé à l'entrée
  (mesuré à la clôture du jour du signal t), non recalculé ensuite.
- **Stop** = `entry_price − 1,5 × ATR14(t)`.
- **Take profit** = `entry_price + 3,0 × ATR14(t)` (= 2R).
  Correspond au « TP initial 2R » du bloc gestion du risque fourni par
  l'utilisateur. **Le passage break-even à 1R et le trailing à partir de
  1,5R ne sont PAS implémentés ici** : l'utilisateur les a explicitement
  qualifiés de non-validés statistiquement (« je ne les considère pas
  comme statistiquement verrouillés ») — seul le TP fixe à 2R, seul
  élément chiffré et déclaré verrouillé du bloc gestion du risque, est
  utilisé.
- **Gestion intra-trade** : identique à la Stratégie A — si `low(t) ≤ stop`
  ET `high(t) ≥ TP` le même jour → stop prioritaire (hypothèse
  conservatrice, ordre intrajournalier réel inconnu, données quotidiennes
  uniquement).
- **Dimensionnement** : 0,5 % de l'equity courante (capital composé) par
  trade, unités = `(0,5 % × equity_avant_trade) / (1,5 × ATR14(t))`, même
  hypothèse de tradabilité fractionnaire que la Stratégie A (documentée
  dans `PREREG_daily_breakout_baseline.md`).
- **Capital initial** = 5 000 €.
- **Coûts de transaction** : 5 bps du notionnel à l'entrée, 5 bps à la
  sortie — identique à la Stratégie A et au reste du repo.
- **Position finale** : si ouverte en fin d'échantillon, marquée au
  marché au dernier close, sans coût de sortie fictif.
- **Une seule position à la fois** (marché unique ici, contrainte
  triviale).
- **Aucun look-ahead** : tous les facteurs n'utilisent que les données
  jusqu'à la clôture du jour évalué ; entrée au jour suivant.

## Univers et période

**Composite pré-enregistré** (`data/nasdaq_composite_daily.txt`, 5 ans,
1251 séances) — même choix que la Stratégie A, pour comparabilité directe.
Échantillon testable = à partir de la 206e séance (amorçage SMA200, le
plus long des facteurs, + marge de sécurité de 5 séances — même
convention de marge que la Stratégie A).

## Critère de succès (pré-enregistré, quantifié)

Identique au critère de la Stratégie A, pour que la comparaison A vs B
soit directe : la Stratégie B est un **PASS** si, net de coûts, sur
l'échantillon testable, elle bat Buy & Hold **simultanément** en Sharpe
annualisé ET en rendement total. Sinon **FAIL**, rapporté honnêtement.
Le repo a déjà établi à l'Étape B (ML) qu'aucun signal actif testé ne bat
Buy & Hold sur le Composite ; cette Stratégie B (règles, pas ML) n'a
aucune garantie de faire mieux.

## Robustesse (SI PASS uniquement, pas un retuning)

Perturbation des paramètres non centraux à la règle de décision elle-même
(le seuil ≥7 reste fixe, ce n'est pas un paramètre à optimiser) :
fenêtres de breakout 20j/50j → ±20 % (16/40j), bande RSI [50,75] →
[45,80], multiplicateurs ATR (1,5/3,0) → ±20 %. Vérifie un plateau, pas
un pic isolé. Rapporté tel quel.

## Comparaison A vs B

Une fois les deux résultats obtenus (indépendamment, chacun avec son
propre pré-enregistrement et son propre audit), un tableau comparatif
direct sera rapporté (Sharpe, rendement total, MDD, nombre de trades,
taux de réussite, verdict PASS/FAIL) — aucun nouveau paramètre ajusté à
ce stade, la comparaison est purement descriptive des deux résultats déjà
figés.

## Anti-cheat

Ce fichier committé seul, avant `nonml_multifactor_score_daily_backtest.py`.
Vérification via `nonml_anti_cheat_check.py multifactor_score_daily`.

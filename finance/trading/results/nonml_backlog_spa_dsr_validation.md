# Validation SPA + DSR — famille des 13 overlays vol-targeting hiérarchiques (backlog non-ML)

Fenêtre commune : 1133 séances (intersection des périodes testables des 13 membres, à partir de l'indice 9139 de `nasdaq100_daily.txt`).

## 1. Résultats individuels sur la fenêtre COMMUNE (peuvent différer légèrement des résultats originaux, calculés chacun sur sa propre fenêtre, plus longue)

| Membre | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.55 | +57.8% | -34.4% |
| dispersion | +0.60 | +70.0% | -34.4% |
| weakness_breadth | +0.59 | +70.1% | -34.4% |
| correlation_regime | +0.55 | +63.4% | -34.4% |
| momentum_breadth | +0.60 | +73.6% | -34.4% |
| sma200_breadth | +0.60 | +74.0% | -34.4% |
| net_breadth | +0.60 | +73.6% | -34.4% |
| sma200_momentum_and | +0.61 | +74.6% | -34.4% |
| concentration | +0.59 | +69.0% | -34.4% |
| momentum_dispersion | +0.62 | +76.4% | -34.4% |
| range_position | +0.59 | +68.1% | -34.4% |
| momentum_dispersion_trend_and | +0.62 | +74.4% | -34.4% |
| beta_dispersion | +0.52 | +56.3% | -34.4% |
| internal_breadth | +0.60 | +73.0% | -34.4% |

## 2. Test SPA (Hansen 2005, bootstrap stationnaire, `src/volatility.py::spa_test`, mêmes paramètres qu'à l'Étape C, aucun retuning)

Perte = -pnl net de coûts. Benchmark = Buy&Hold NDX. H0 : aucun des 13 membres ne bat significativement le benchmark une fois corrigé pour les essais multiples.

p-value SPA : 0.1924
Meilleur membre (statistique de test) : dispersion

**H0 NON REJETÉE — la famille entière, corrigée pour 13 essais, ne bat PAS significativement Buy&Hold au seuil 5%.**

## 3. DSR (Bailey & López de Prado 2014, `src/prediction.py::dsr`, même méthode qu'à l'Étape B) — meilleur membre = **momentum_dispersion** (Sharpe ann. +0.62 sur fenêtre commune)

n_trials = 13 (famille figée), var_trials (variance des 13 Sharpe journaliers) = 0.000003
Sharpe max ATTENDU sous H0 (essais multiples, expected_max_sharpe, échelle journalière) : 0.0030
Sharpe journalier du meilleur membre : 0.0393 (seuil de sélection SR0=0.0030, z=+1.22)
**DSR = 0.8883**

DSR ≤ 0.95 : le Sharpe du meilleur membre NE reste PAS statistiquement distinguable du hasard une fois corrigé pour 13 essais (cohérent avec la conclusion Étape B : aucun signal ne bat Buy&Hold à DSR>0.95 sur le Composite).

## 4. DSR secondaire APPROXIMATIF sur le backlog complet (N=110, INDICATIF SEULEMENT)

Univers hétérogène (mécanismes très différents, pas seulement vol-targeting) — ne respecte pas strictement l'hypothèse DSR de tests répétés de la MÊME métrique candidate. Reporté uniquement à titre de borne indicative, PAS comme résultat principal.

n_trials≈43 (Sharpe extractibles par regex sur 43/110 entrées du backlog), var_trials≈0.2918, meilleur Sharpe extrait≈+3.00. Sharpe max attendu sous H0 (essais multiples) ≈ 1.1981 (échelle Sharpe annualisé, pas directement comparable au DSR journalier de la section 3 -- reporté ici uniquement pour illustrer l'ordre de grandeur de l'inflation du seuil de significativité quand n_trials passe de 13 à ~110).

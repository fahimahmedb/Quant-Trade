# Backtest cross-market — LogitL2 + overlay (NDX) sur 3 indices externes

Valide si le meilleur pipeline trouvé sur NDX (LogitL2, Étape B, + overlay vol-targeting GJR-GARCH(1,1)-t cap 2.0×/coupe totale au 90e percentile in-sample, meilleure combinaison du grid-search figé — `results/etape_D_overlay_optimized.md`) se **généralise** à d'autres marchés, **sans aucun re-réglage** (mêmes hyperparamètres partout).

**Protocole figé** (identique NDX) : fenêtre initiale 750 obs expansive, ré-estimation tous les 21 j (primaire LogitL2 et overlay GJR-t), purge/embargo 5 j, triple barrier H=5 j ±1.5·σ_local (ewm 20 j), coûts 5 bps aller-retour, overlay cap 2.0×/coupe totale au 90e percentile in-sample.

**Univers figé** : 3 indices externes (Russell 2000, S&P 500, DAX) × 3 variantes (Buy & Hold, LogitL2, LogitL2+Overlay) = 9 tests, aucun ajout a posteriori. Le DSR est calculé **par indice** (N=3, familles non combinées entre indices — cf. discipline anti-data-snooping).

## Données

| Indice | Fichier | Séances | Période complète | OOS |
|---|---|---|---|---|
| Russell 2000 (^RUT, small-cap US) | `russell2000_daily.txt` | 9782 | 10/09/1987 → 13/07/2026 | 28/08/1990 → 10/07/2026 (9031 obs, ~35.9 ans) |
| S&P 500 (^GSPC, large-cap US) | `sp500_daily.txt` | 14252 | 02/01/1970 → 13/07/2026 | 18/12/1972 → 10/07/2026 (13501 obs, ~53.6 ans) |
| DAX (^GDAXI, large-cap Allemagne) | `dax_daily.txt` | 6777 | 01/11/1999 → 10/07/2026 | 14/10/2002 → 09/07/2026 (6026 obs, ~23.7 ans) |

## Russell 2000 (^RUT, small-cap US)

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Turnover | DSR (N=3) |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.39 | +0.50 | +0.09 | -59.9 | +8.9 | 0.000 | 0.955 |
| LogitL2 | +0.14 | +0.19 | +0.02 | -84.5 | +3.2 | 0.466 | 0.595 |
| LogitL2+Overlay | +0.26 | +0.35 | +0.03 | -80.0 | +4.7 | 0.489 | 0.824 |

- **LogitL2+Overlay vs Buy & Hold** : réduction MDD relative = -33.6% (seuil >20%), rendement ann. conservé = 53.2% du Buy & Hold (seuil ≥80%) → non matériel / rendement NON conservé.

## S&P 500 (^GSPC, large-cap US)

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Turnover | DSR (N=3) |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.44 | +0.56 | +0.09 | -56.8 | +8.1 | 0.000 | 0.998 |
| LogitL2 | +0.35 | +0.46 | +0.05 | -72.6 | +6.4 | 0.259 | 0.989 |
| LogitL2+Overlay | +0.36 | +0.45 | +0.06 | -59.5 | +5.3 | 0.259 | 0.988 |

- **LogitL2+Overlay vs Buy & Hold** : réduction MDD relative = -4.7% (seuil >20%), rendement ann. conservé = 65.7% du Buy & Hold (seuil ≥80%) → non matériel / rendement NON conservé.

## DAX (^GDAXI, large-cap Allemagne)

| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Turnover | DSR (N=3) |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.43 | +0.55 | +0.11 | -54.8 | +9.5 | 0.000 | 0.818 |
| LogitL2 | +0.03 | +0.04 | +0.01 | -60.6 | +0.6 | 0.265 | 0.152 |
| LogitL2+Overlay | -0.12 | -0.17 | -0.02 | -81.7 | -2.8 | 0.398 | 0.039 |

- **LogitL2+Overlay vs Buy & Hold** : réduction MDD relative = -49.2% (seuil >20%), rendement ann. conservé = -29.2% du Buy & Hold (seuil ≥80%) → non matériel / rendement NON conservé.

## Verdict cross-market

Critère de succès (fixé a priori) : le pipeline LogitL2+Overlay réduit le MDD vs Buy & Hold sur **au moins 2/3 indices** de façon matérielle (>20% relatif), sans perdre l'essentiel du rendement (≥80% de Buy & Hold).

| Indice | ΔMDD relatif | Rdt ann. / BuyHold | Matériel (>20%) | Rendement conservé (≥80%) | Succès combiné |
|---|---|---|---|---|---|
| Russell 2000 (^RUT, small-cap US) | -33.6% | 53.2% | non | non | NON |
| S&P 500 (^GSPC, large-cap US) | -4.7% | 65.7% | non | non | NON |
| DAX (^GDAXI, large-cap Allemagne) | -49.2% | -29.2% | non | non | NON |

**0/3 indices** remplissent le critère de succès complet (réduction MDD matérielle ET rendement conservé) ; 0/3 atteignent au moins la réduction de MDD matérielle seule.

**Verdict honnête : le critère de généralisation cross-market N'EST PAS atteint** (0/3 < 2/3 indices). Le pipeline LogitL2+overlay, calibré sur NDX et appliqué tel quel (aucun re-réglage), ne réduit pas le drawdown de façon matérielle sur la majorité des indices externes testés, ou le fait au prix d'une perte de rendement trop importante. Ce résultat est rapporté tel quel : il suggère que le réglage cap 2.0×/coupe 90e percentile trouvé sur NDX est en partie spécifique à cet historique (40 ans, incluant 2000-2002) plutôt qu'un réglage universel — cohérent avec la mise en garde déjà faite en Étape D (grid-search) sur la non-généralisation automatique des paramètres optimisés.
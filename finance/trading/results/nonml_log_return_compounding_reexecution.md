# Ré-exécution après correction de la composition des rendements log (#376)

Suite de l'audit `nonml_log_return_compounding_audit.md` (#375). La composition
a été corrigée dans 12 scripts de backtest — `np.cumprod(1.0 + pnl)[-1] - 1.0`
remplacé par `np.exp(pnl.sum()) - 1.0` — puis chaque backtest a été **ré-exécuté
intégralement sur ses 5 marchés** (4 pour le cycle électoral).

Aucun paramètre, seuil, univers ni critère n'a été touché. Le seul changement est
la formule de composition. Les verdicts ci-dessous sont donc directement
comparables à ceux d'origine.

## Reclassifications — PASS devenus FAIL

| Stratégie | Score avant | Score après | Verdict |
|---|---|---|---|
| `nonml_bitcoin_momentum_overlay` (#344) | 5/5 | **3/5** | PASS → **FAIL** |
| `nonml_credit_card_delinquency_overlay` | 4/5 | **3/5** | PASS → **FAIL** |
| `nonml_cross_market_correlation_ndx_dax_overlay` (#193) | 4/5 | **0/5** | PASS → **FAIL** |
| `nonml_delinquency_nfci_baa10y_graduated_overlay` | 4/5 | **1/5** | PASS → **FAIL** |
| `nonml_delinquency_nfci_baa10y_majority_overlay` | 5/5 | **3/5** | PASS → **FAIL** |
| `nonml_volatility_managed_portfolio_gjr` | 2 jambes | **1 jambe** | PASS → **FAIL** |
| `nonml_ewma_defensive_overlay_and_triple_engine` | critère standard PASS | **FAIL** | PASS → **FAIL** (critère Calmar reste PASS) |

## PASS qui survivent à la correction

| Stratégie | Score avant | Score après | Verdict |
|---|---|---|---|
| `nonml_defensive_calmar_vol_targeting_overlay` | 4/5 | 4/5 | PASS maintenu (critère Calmar) |
| `nonml_delinquency_nfci_baa10y_corr_move_majority_overlay` | 5/5 | 4/5 | PASS maintenu |
| `nonml_delinquency_nfci_combined_overlay` | 5/5 | 4/5 | PASS maintenu |
| `nonml_midterm_election_overlay` | 4/4 | 3/4 | PASS maintenu — **exactement au seuil** (critère ≥3/4) |

## Verdict inchangé

`nonml_stlfsi_financial_stress_overlay` était déjà FAIL (3/5) et le reste, avec un
score dégradé (0/5).

## Lecture

Sur 11 PASS ré-évalués, **7 tombent**. Aucun ne s'améliore. Le sens est celui
prédit par l'analyse du biais avant toute mesure : la formule buguée retranchait
≈ `Σx²/2` et avantageait donc les stratégies à variance réduite, c'est-à-dire les
overlays défensifs — la famille très majoritaire de ce backlog.

Deux conséquences directes :

1. **Le compteur « 101 PASS niveau 1 » est surévalué.** 7 reclassifications sont
   établies ici sur les 12 scripts ré-exécutés. Les ~306 autres scripts portant
   le même idiome n'ont PAS été ré-exécutés : le nombre réel de PASS restants
   est inconnu et inférieur à 101.
2. **`nonml_bitcoin_momentum_overlay` (#344) est désormais FAIL.** C'était l'un
   des candidats de pivot Étape D retenus par les synthèses v9-v15, et la
   stratégie dont les chiffres de simulation 300 € avaient été communiqués.
   Ce candidat de pivot tombe.

`nonml_midterm_election_overlay` passe de 4/4 à 3/4 pour un seuil à ≥3/4 : il ne
survit que d'un marché. À traiter comme fragile, pas comme un PASS solide.

## Ce qui reste à faire

- Ré-exécuter les ~306 scripts restants portant le même idiome.
- Corriger les `*_sim_300e.py`, qui partagent le bug (impact faible à 63 séances,
  mais les chiffres publiés sont sous-estimés).
- Les batteries Règle 9 déjà passées sur les stratégies reclassées sont caduques :
  elles validaient un résultat qui n'existe plus.

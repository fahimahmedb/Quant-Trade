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

## Contrôle : les versions de librairies ne sont pas en cause

Le conteneur ayant été réinitialisé, toute la ré-exécution tourne sous
numpy 2.4.6 / pandas 3.0.5 / scipy 1.17.1 / arch 8.0.0 — vraisemblablement plus
récents que ceux ayant produit les résultats d'origine. Un écart de verdict
pourrait donc, a priori, venir des versions plutôt que de la correction.

Contrôle effectué : l'**ancienne** formule (`np.cumprod(1.0 + pnl)[-1] - 1.0`) a
été restaurée puis ré-exécutée **sous les librairies actuelles**, sur deux
stratégies dont le résultat avait changé (`acf_lag1_vol_targeting_overlay`,
`atr_vol_targeting_overlay`). Dans les deux cas le fichier produit est
**identique à l'octet près** au résultat committé d'origine.

**Conclusion : les versions de librairies sont neutres ici.** Les changements de
verdict rapportés sont imputables à la correction de la composition, et à elle
seule.

## Incompatibilité pandas ≥ 3 rencontrée (sans rapport avec le bug)

`nonml_dispersion_vol_targeting_overlay_backtest.py` échouait sous pandas 3
(`ValueError: assignment destination is read-only`) : avec le copy-on-write,
`.values` renvoie une vue en lecture seule. Corrigé par un `.copy()` explicite.
Défaut d'environnement préexistant, révélé par la réinstallation — sans lien avec
la composition des rendements. Deux scripts en dépendaient et échouaient.

## Balayage complet des 208 backtests indiciels (#377)

La correction a été appliquée aux 208 scripts de backtest **indiciels** restants
(P&L authentiquement en rendements log), puis chacun a été ré-exécuté.
Les 31 scripts de **portefeuille au niveau titre** sont exclus : leur P&L est une
moyenne pondérée de rendements log alors que le rendement d'un panier pondéré est
`Σ wᵢ·r_simple,ᵢ` — défaut distinct, non traité ici.

Résultat du balayage : 208 scripts exécutés, **4 échecs** tous résolus
(2 incompatibilités pandas ≥ 3 sans rapport avec le bug, 1 script exigeant un
argument de marché, 1 dépendant du premier).

Comparaison sur les 269 résultats instantanés avant correction :

- **42 fichiers de résultat modifiés**
- **5 PASS deviennent FAIL** :
  `bond_market_volatility_overlay` (4/5→2/5),
  `ewma_vol_targeting_overlay` (4/5→3/5),
  `financial_conditions_overlay` (4/5→3/5),
  `cash_rate_correction_defensive_vol_targeting_44`,
  `gjr_vol_managed_weekly_rebalance`
- **0 FAIL ne devient PASS**
- 37 résultats voient leur score bouger sans changer de verdict

## Bilan consolidé #375 → #377

| | |
|---|---|
| PASS reclassés en FAIL (cycle #376, 12 scripts) | **7** |
| PASS reclassés en FAIL (cycle #377, 208 scripts) | **5** |
| **Total PASS tombés** | **12** |
| FAIL devenus PASS | **0** |

**Aucun verdict ne s'améliore, dans aucun des deux balayages.** C'est exactement
le sens prédit avant toute mesure : la formule buguée retranchait ≈ `Σx²/2` et
avantageait donc les stratégies à variance réduite — les overlays défensifs, très
majoritaires ici.

## Où en est le compteur

Le décompte brut sur les fichiers de résultat donne **101 PASS sur 265 verdicts
lisibles**. Ce nombre ne doit PAS être lu comme une confirmation du « 101 PASS »
d'avant : la population de fichiers n'est pas la même (269 instantanés, 265
verdicts lisibles, plus des résultats sans verdict au format standard), et
12 PASS ont bel et bien été perdus sur la période.

**Ce compteur reste provisoire** tant que les 31 scripts de portefeuille au
niveau titre n'ont pas été traités — famille Leaders / Winners / Low-Vol /
momentum, qui porte un défaut de composition de panier encore non corrigé et
dont les résultats sont donc toujours suspects.

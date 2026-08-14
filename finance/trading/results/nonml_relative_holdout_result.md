# Hors-échantillon **relatif au benchmark** — la piste C refaite (pré-enregistré)

Le #458 mesurait le Sharpe **absolu** et concluait à tort à une persistance :
Buy & Hold faisait **mieux** sur la même fenêtre. Ce cycle mesure l'**edge**,
avec les **mêmes découpes**, pour que seule la métrique change.

> **Un edge n'est pas une performance.** Gagner 30 % dans un marché qui gagne
> 35 % n'est pas un edge — c'est exactement ce que le #458 n'a pas su voir.

## Couverture

- PASS retenus : **100**
- exclus : **0**

Benchmarks employés, par schéma : **indiciel** (87), **panier** (13)

## Découpe : 252 dernières séances *(principale)*

Candidats évaluables : **100**

| | Avant la fenêtre | Sur la fenêtre |
|---|---|---|
| **edge médian** | **+0.05** | **-0.06** |
| edge moyen | +0.07 | -0.07 |
| 1ᵉʳ quartile | +0.03 | -0.16 |
| 3ᵉ quartile | +0.09 | +0.00 |

- fraction à **edge positif** sur la fenêtre : **18.0 %**
- fraction dont l'**edge se contracte** : **88.0 %**

Les cinq plus fortes contractions :

- `leaders_index52w_high_overlay` — edge +0.18 → **-0.38**
- `intl_breadth_confirmation_overlay` — edge +0.02 → **-0.53**
- `cpi_inflation_overlay` — edge +0.12 → **-0.38**
- `gjr_vol_managed_sp500` — edge +0.05 → **-0.43**
- `halloween_midterm_multiplicative_overlay` — edge +0.04 → **-0.41**

Les cinq meilleurs edges sur la fenêtre :

- `amihud_illiquidity_tilt` — edge +0.16 → **+0.97**
- `momentum_turnover_doublesort` — edge +0.33 → **+0.61**
- `momentum_12_1_pit_universe` — edge -0.01 → **+0.35**
- `short_term_momentum` — edge -0.05 → **+0.15**
- `rogers_satchell_vol_targeting_overlay` — edge +0.19 → **+0.14**

## Découpe : 504 dernières séances *(secondaire)*

Candidats évaluables : **100**

| | Avant la fenêtre | Sur la fenêtre |
|---|---|---|
| **edge médian** | **+0.07** | **-0.07** |
| edge moyen | +0.08 | -0.07 |
| 1ᵉʳ quartile | +0.04 | -0.13 |
| 3ᵉ quartile | +0.12 | +0.00 |

- fraction à **edge positif** sur la fenêtre : **19.0 %**
- fraction dont l'**edge se contracte** : **89.0 %**

Les cinq plus fortes contractions :

- `turn_of_month` — edge +0.07 → **-0.66**
- `halloween_midterm_multiplicative_overlay` — edge +0.05 → **-0.41**
- `yang_zhang_vol_targeting_overlay` — edge +0.24 → **-0.22**
- `diversification_bond_weekly_rebalance_stack` — edge +0.23 → **-0.19**
- `vol_targeting_20_overlay` — edge +0.22 → **-0.20**

Les cinq meilleurs edges sur la fenêtre :

- `amihud_illiquidity_tilt` — edge +0.06 → **+0.74**
- `momentum_turnover_doublesort` — edge +0.22 → **+0.53**
- `short_term_momentum` — edge -0.16 → **+0.35**
- `macro_combo_and_breakeven_claims_trade_overlay` — edge +0.00 → **+0.18**
- `momentum_12_1_pit_universe` — edge +0.00 → **+0.13**

## Mes trois prédictions, confrontées

Sur la découpe principale (252 séances, 100 candidats) :

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| edge médian sur la fenêtre ≤ 0 | ≤ 0 | -0.06 | **vérifiée** |
| fraction à edge positif < 50 % | < 50 % | 18.0 % | **vérifiée** |
| plus de la moitié se contractent | > 50 % | 88.0 % | **vérifiée** |

**3 sur 3.** *(Au #458 : 0 sur 3.)*

## Lecture

Le changement de métrique renverse le tableau du #458 : là où le Sharpe
**absolu** montait, l'**edge** — la seule grandeur qui mesure quelque chose —
est de **-0.06** en médiane sur la fenêtre récente.

**Les stratégies ne battent pas leur benchmark sur la période récente.**
C'est la troisième confirmation indépendante, après le **0/29** de la
batterie (#457) et le constat post-hoc du #458.

Et c'est cohérent avec ce que `CLAUDE.md` établit depuis l'Étape B :
**Buy & Hold reste la meilleure stratégie testée**.

## Ce que ce cycle ne prouve pas

- **La fenêtre reste contaminée par la sélection.** Ces stratégies ont été
  choisies en connaissant tout l'échantillon, fenêtre récente comprise. Un
  edge nul y est attendu même si un edge avait existé — et un edge positif
  n'y prouverait rien.
- **Aucun verdict n'est réécrit**, aucune stratégie promue ni retirée.
- Le rapport confondu du #458 **reste publié**, avec son diagnostic : ce
  cycle ne l'efface pas, il le complète.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).
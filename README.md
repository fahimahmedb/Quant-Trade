# Quant-Trade — Outil probabiliste NASDAQ Composite

Implémentation des Étapes A (diagnostics), B (prédiction directionnelle) et
C (volatilité) du cahier des charges (revue de littérature orientée conception).

## Structure

```
data/  nasdaq_composite_daily.txt — Composite, OHLC quotidien 13/07/2021 → 10/07/2026 (1251 séances)
       nasdaq100_daily.txt        — NASDAQ-100 (NDX), OHLC quotidien 01/10/1985 → 13/07/2026 (10273 séances)
src/   data_loader.py, diagnostics.py (Étape A), prediction.py (Étape B),
       volatility.py (Étape C + DM + SPA)
scripts/  run_etape_a.py, run_etape_b.py, run_etape_c.py — chaque script prend
          [chemin_données] [chemin_sortie] optionnels (défaut : Composite)
results/  etape_{A,B,C}_*.md — Composite (défaut) et *_ndx100 (historique long)
```

Les deux jeux sont conservés : le **Composite 5 ans** est l'échantillon
pré-enregistré (traçabilité), le **NDX 40 ans** est la ré-exécution du même
protocole sur plus de données (2 lignes OHLC anciennes corrigées d'un arrondi
au cent ; ère à volume réel ≥ 1985 uniquement). NDX ≠ Composite (100 vs ~3000
valeurs) mais même famille ; substitut valide et directement traçable (QQQ).

## Reproduire

```bash
pip install numpy scipy pandas statsmodels arch scikit-learn

# Échantillon pré-enregistré (Composite, 5 ans)
python3 scripts/run_etape_a.py
python3 scripts/run_etape_b.py
python3 scripts/run_etape_c.py

# Ré-exécution du même protocole sur l'historique long (NDX, 40 ans)
D=data/nasdaq100_daily.txt
python3 scripts/run_etape_a.py $D results/etape_A_ndx100.md
python3 scripts/run_etape_b.py $D results/etape_B_ndx100.md
REFIT_EVERY=21 python3 scripts/run_etape_c.py $D results/etape_C_ndx100.md
```

## Résultats clés (voir results/ pour le détail)

- **Étape A** : random walk non rejeté (Lo-MacKinlay z* robustes non
  significatives) ; effet ARCH massif ; queues épaisses (ν≈4,8 non
  conditionnel). Aucune autocorrélation exploitable du rendement.
- **Étape B** : prédiction de **direction** (jamais de prix — piège du naïve
  forecast), cible triple-barrier (López de Prado), features causales +
  differenciation fractionnaire, walk-forward avec purge/embargo, coûts
  inclus. Univers figé (Buy & Hold, Momentum, Logistique L2, HistGB). Verdict
  honnête : **aucun signal actif ne bat le Buy & Hold à DSR > 0,95** (accuracy
  ≈ 51–54 %), cohérent avec l'Étape A. Deflated Sharpe Ratio + test de
  lookahead (délai d'exécution) + coût de rupture rapportés.
- **Étape C** : GJR-GARCH(1,1)-t bat GARCH(1,1)-n en walk-forward
  (500 prévisions OOS, QLIKE −3 %, DM p=0.014 à h=1, p=0.030 à h=5,
  cohérent sur deux proxys) — mais le SPA de Hansen famille entière donne
  p≈0.11 : la limite est la taille d'échantillon, pas le modèle.

### Ce que change l'historique long (NDX, 40 ans vs Composite 5 ans)

- **Étape A** : sur 40 ans, le random walk est désormais **rejeté** par la
  statistique z\* robuste (VR(5)=0,89, p=0,007 ; VR<1 = retour à la moyenne).
  Le signal absent sur 5 ans apparaît sur un échantillon multi-cycles — c'est
  exactement l'argument « plus de données, pas plus de modèles ».
- **Étape B** : la régression logistique devient **rentable nette de coûts**
  (Sharpe ≈ +0,30, accuracy 53,7 %, break-even ≈ 17 bps ≫ 5 bps) mais reste
  **sous le buy-and-hold** en base ajustée du risque et déflatée (DSR). Edge
  faible et réel, insuffisant pour battre le simple portage.

## Discipline anti-data-snooping (non négociable)

Les univers de modèles et les protocoles OOS sont figés dans
`scripts/run_etape_b.py` (N=4 signaux) et `scripts/run_etape_c.py`
(6 modèles) AVANT toute évaluation. Toute extension de l'univers doit être
déclarée, comptée (N essais) et re-testée au SPA / Deflated Sharpe. On n'itère
pas sur l'échantillon de test jusqu'à obtenir un chiffre plaisant : on allonge
l'historique ou on améliore les données (RV intraday, microstructure,
sentiment), puis on re-teste une fois.

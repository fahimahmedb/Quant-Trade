# Quant-Trade — Outil probabiliste NASDAQ Composite

Implémentation des Étapes A (diagnostics) et C (volatilité) du cahier des
charges (revue de littérature orientée conception).

> **Statut de recherche :** les anciens scores de prévision ne constituent pas
> un edge tradable. L'audit Phase 0 a testé leur première traduction économique
> et l'a classée **KILL** ; voir `results/phase0_forensic_audit.md`.

## Structure

```
data/       nasdaq_composite_daily.txt — OHLC quotidien 13/07/2021 → 10/07/2026 (1251 séances)
src/        data_loader.py, diagnostics.py (Étape A), volatility.py (Étape C + DM + SPA)
scripts/    run_etape_a.py, run_etape_c.py — régénèrent results/ à l'identique
results/    etape_A_diagnostics.md, etape_C_volatilite.md
```

## Reproduire

```bash
pip install numpy scipy pandas statsmodels arch
python3 scripts/run_etape_a.py
python3 scripts/run_etape_c.py
python3 scripts/run_phase0_e1.py  # sans dépendance externe
python3 -m unittest discover -s tests -v
```

## Résultats clés (voir results/ pour le détail)

- **Étape A** : random walk non rejeté (Lo-MacKinlay z* robustes non
  significatives) ; effet ARCH massif ; queues épaisses (ν≈4,8 non
  conditionnel). Aucune autocorrélation exploitable du rendement.
- **Étape C** : GJR-GARCH(1,1)-t bat GARCH(1,1)-n en walk-forward
  (500 prévisions OOS, QLIKE −3 %, DM p=0.014 à h=1, p=0.030 à h=5,
  cohérent sur deux proxys) — mais le SPA de Hansen famille entière donne
  p≈0.11 : la limite est la taille d'échantillon, pas le modèle.

## Discipline anti-data-snooping (non négociable)

L'univers de modèles (6) et le protocole OOS sont figés dans
`scripts/run_etape_c.py` AVANT toute évaluation. Toute extension de
l'univers doit être déclarée, comptée (N essais) et re-testée au SPA /
Deflated Sharpe. On n'itère pas sur l'échantillon de test jusqu'à obtenir
un chiffre plaisant : on allonge l'historique ou on améliore les données
(RV intraday), puis on re-teste une fois.

## Limites connues

Le fichier n'a pas de provenance consignée et représente un indice non
directement tradable, sans dividendes ni coûts. Le holdout 2024–2026 est
**consommé**. Aucune conclusion de ce dépôt n'autorise du paper trading ou du
capital réel.

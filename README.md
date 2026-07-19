# Quant-Trade — Outil probabiliste NASDAQ Composite

Implémentation des Étapes A (diagnostics) et C (volatilité) du cahier des
charges (revue de littérature orientée conception).

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

---

# Module « Prédiction politique » — présidentielle FR sans sondage déclaratif

Prédit un résultat électoral (2nd tour, présidentielle française) en fusionnant
des sources **non déclaratives** : modèles fondamentaux, marchés de prédiction,
NLP/sentiment — puis machine learning. Même discipline anti-data-snooping :
univers figé, backtest OOS à fenêtre expansive (entraînement sur le passé
strict), aucun ajustement sur le test.

## Structure (préfixe `pp_` / étapes `P`)

```
data/   fr_presidentielles.json (registre 1965→2022, résultats officiels),
        fr_fundamentals.csv, fr_markets_snapshot.json, fr_nlp_snapshot.csv
src/    pp_types.py   contrat commun (Source.fit/predict, SourceSignal, Posterior)
        pp_data.py    loader registre + fondamentaux
        pp_backtest.py protocole OOS + métriques (Brier, log-loss, MAE, issue)
        pp_fundamentals.py (P1)  régression structurelle (Jérôme-Speziari style)
        pp_markets.py      (P2)  prix de marché dé-biaisés (favori-outsider)
        pp_nlp.py          (P3)  proxy notoriété/tonalité (Trends, mentions)
        pp_fusion.py       (P4)  fusion bayésienne (précision, espace logit)
        pp_ml.py           (P5)  logistic / random forest / GB / XGBoost
scripts/ run_etape_P1..P5_*.py → results/etape_P1..P5_*.md
```

## Reproduire

```bash
pip install numpy scipy pandas scikit-learn xgboost
for e in P1_fondamentaux P2_marches P3_nlp P4_fusion P5_ml; do
  PYTHONPATH=src python3 scripts/run_etape_${e}*.py
done
```

## Résultat clé (backtest OOS, 7 plis)

La **fusion multi-source** (Brier 0.14, log-loss 0.41, 86 % de bonnes issues)
bat nettement chaque source seule — en particulier les fondamentaux seuls
(Brier 0.37, 57 %). Les contributions migrent dans le temps selon la
disponibilité : fondamentaux → NLP (2007+) → marchés (2017+). Le ML à forte
capacité (GB/XGBoost) **sur-ajuste** à n≈11 (log-loss > 3) : le gain vient de
l'**information** ajoutée (marchés, NLP), pas de la capacité du modèle. Le vrai
terrain ML est la maille circonscription (législatives), documentée en tête de
`scripts/run_etape_P5_ml.py`.

### Orchestration (économie de tokens)

Développé par sous-agents parallèles avec tiering de modèles : Haiku pour la
mécanique déterministe (P1), Sonnet pour le raisonnement moyen (P2 marchés,
P3 NLP), Opus pour l'architecture, la fusion, la revue et le ML final.

### Données — avertissement

Les résultats électoraux (registre) sont officiels/domaine public. Les variables
macro, prix de marché et features NLP sont **approximatifs/illustratifs** et
documentés comme tels dans chaque fichier ; à remplacer par des séries primaires
sourcées avant tout usage réel.

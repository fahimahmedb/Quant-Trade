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
        pp_circo.py        (P7)  analyse circonscription × PARTI (LFI explicite)
scripts/ run_etape_P1..P5_*.py → results/etape_P1..P5_*.md
         run_etape_P6_pred2027.py → results/etape_P6_pred2027.md  (prévision FORWARD 2027)
         run_etape_P7_circonscriptions.py → results/etape_P7_circonscriptions.md
data/    fr_pres2022_circo.csv — présidentielle 2022 1er tour par circonscription
         × parti (RÉEL, ministère de l'Intérieur / data.gouv.fr)
```

## Reproduire

```bash
pip install numpy scipy pandas scikit-learn xgboost
for e in P1_fondamentaux P2_marches P3_nlp P4_fusion P5_ml P6_pred2027 P7_circonscriptions; do
  PYTHONPATH=src python3 scripts/run_etape_${e}*.py
done
```

## Étape 4 (P7) — circonscription × parti, LFI explicite, données réelles

Sur données **réelles** (présidentielle 2022 par circonscription, ministère de
l'Intérieur), au niveau **parti** (Mélenchon = **LFI**, distinct de PS/EELV —
pas le bloc « NFP/UG » qu'imposent les nuances législatives officielles, où
seuls 3 candidats sur 544 étaient codés « FI » en 2024).

**Est-ce que ça aide ?** Oui, mais pas là où on croit :
- Ça **n'améliore pas** le chiffre national (agréger les circos le reproduit
  exactement).
- Ça **ajoute** ce que le national ne peut pas voir : LFI arrive **en tête dans
  105 circonscriptions** (et dans le duo de tête de 260), et un modèle spatial
  **divise l'erreur locale par ~2** vs la moyenne nationale plate. Base d'une
  projection en sièges / de reports par circonscription pour 2027.

**Méthodes sourcées** (documentées dans le rapport) : régression de Dirichlet sur
données compositionnelles multipartis et procédure correction-combinaison au
niveau circonscription — Hanretty (2021), *International Journal of Forecasting* ;
approche bayésienne polls + fondamentaux en systèmes multipartis (Stoetzer et al.,
*Political Analysis* 2019). La *baseline* de référence à battre est le **swing
national uniforme**.

## Prévision 2027 (P6) — forward, honnêtement vérifiable

2027 est un scrutin **futur** (aucun hindsight possible). Macron étant
inéligible (2 mandats), c'est un **siège ouvert**. Les fondamentaux, seule
brique validée, ne prédisent que le **sort du camp sortant** : verdict
**≈ 50/50** (part 2nd tour 49,6 % ± 10 pts) — ni favori, ni condamné. Ils sont
**incapables de désigner le vainqueur** (RN/gauche/droite), faute de marché
liquide et de signaux de campagne datés à ~21 mois du vote. Le script tente un
**vrai fetch Polymarket** (dormant tant qu'aucun marché n'existe) et se
raffinera sans rétro-ajustement quand des données contemporaines arriveront.

## Résultat clé (backtest OOS, 7 plis) — honnête, après correction d'audit

Un premier jet gonflait les scores (fusion « Brier 0.14 / 86 % ») en backtestant
des données marchés/NLP **rédigées en connaissant l'issue** (hindsight). Ces
données ont été **supprimées** ; marchés et NLP sont désormais **forward-only**
(0 pli historique). Reste la base honnête :

| Prédicteur (OOS, 7 plis) | Brier | Bonne issue |
|---|---|---|
| « Avantage sortant si concourt » (règle 1 ligne) | **0.216** | **71 %** |
| Fondamentaux (régression structurelle) | 0.295 | 57 % |
| Pile ou face | 0.250 | 43 % |

**La régression structurelle ne bat pas une heuristique d'une ligne.** À n=7,
rien n'est significatif. C'est le vrai visage de la prévision présidentielle sans
sondages : l'économie politique n'explique qu'une part modeste du 2nd tour. Le ML
à forte capacité (GB/XGBoost) **sur-ajuste** à n≈11 (log-loss > 3).

La thèse « fusion multi-source > source seule » (littérature : les marchés de
prédiction battent souvent les fondamentaux) reste **plausible mais non démontrée
ici** — elle ne pourra l'être que sur un scrutin **futur** (2027), sans hindsight.

👉 **Audit complet et honnête : [`results/AUDIT.md`](results/AUDIT.md).**

### Orchestration (économie de tokens)

Développé par sous-agents parallèles avec tiering de modèles : Haiku pour la
mécanique déterministe (P1), Sonnet pour le raisonnement moyen (P2 marchés,
P3 NLP), Opus pour l'architecture, la fusion, la revue et le ML final.

### Données — avertissement

Les résultats électoraux (registre) sont officiels/domaine public. Les variables
macro, prix de marché et features NLP sont **approximatifs/illustratifs** et
documentés comme tels dans chaque fichier ; à remplacer par des séries primaires
sourcées avant tout usage réel.

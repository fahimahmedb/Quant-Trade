# Backlog — stratégies non-ML à itérer (une par cycle, même rigueur que PEAD)

Chaque entrée suit EXACTEMENT le même protocole que PEAD
(`PEAD_PREREGISTRATION.md` + les 4 scripts associés) : pré-enregistrement
committé AVANT tout résultat (hypothèse, univers, période, seuils, critère
de succès chiffrés, n_trials=1), backtest sur données réelles, audit
adversarial (recalcul indépendant + mesure des fuites/limites), vérification
anti-cheat automatisée (ordre chronologique des commits, absence de grille
de paramètres). Résultat rapporté tel quel, y compris si FAIL — pas de
nouvel essai sur la même hypothèse après un résultat, une nouvelle idée
séparée si besoin.

**Explicitement HORS ML** (pas de scikit-learn, pas de features apprises,
pas de walk-forward avec ré-estimation de modèle) — des règles simples,
déterministes, motivées par la littérature académique, pas par un
ajustement statistique sur nos données.

## Statut

| # | Stratégie | Données nécessaires | Statut |
|---|---|---|---|
| 0 | PEAD (surprise de résultats, NDX-100) | api.nasdaq.com + Yahoo (déjà récupérées) | **FAIT — FAIL** (t-stat 1.16 < 2), voir `results/pead_backtest_result.md` |
| 1 | Overnight vs intraday (close→open vs open→close) | OHLC déjà en local (`data/*.txt`) | **FAIT — FAIL** (0/5 marchés), voir `results/nonml_overnight_intraday_result.md` |
| 2 | Effet tournant de mois (turn-of-month, J-1 à J+3) | OHLC déjà en local | **FAIT — PASS** (4/5 marchés), robustesse modérée (3/5,4/5,3/5), voir `results/nonml_turn_of_month_result.md` |
| 3 | Effet jour-de-semaine (lundi/vendredi) | OHLC déjà en local | à faire |
| 4 | Momentum 52-semaines (proximité du plus haut annuel, George & Hwang 2004) | prix NDX-100 déjà récupérés (`data/pead/prices/`) | à faire |
| 5 | Reversal court terme (1 semaine, niveau titre) | prix NDX-100 déjà récupérés | à faire |
| 6 | Rallye de fin d'année ("Santa Claus rally", 5 derniers j. déc. + 2 premiers j. janv.) | OHLC déjà en local | à faire |
| 7 | Effet pré/post jour férié US | OHLC déjà en local + calendrier férié US (à coder en dur, dates connues) | à faire |

## Règles du cycle

1. Prendre la PREMIÈRE ligne "à faire" du tableau (ordre = déjà trié par
   facilité de mise en œuvre avec les données déjà en local, pour limiter
   le nouveau fetch réseau à chaque cycle).
2. Écrire `finance/trading/PREREG_<nom>.md`, committer AVANT tout calcul.
3. Construire `scripts/nonml_<nom>_backtest.py`, `scripts/nonml_<nom>_audit.py`,
   réutiliser `pead_anti_cheat_check.py` en le généralisant (paramètre nom
   de stratégie) plutôt que dupliquer.
4. Exécuter, committer les résultats (PASS ou FAIL, honnêtement).
5. Mettre à jour CE tableau (statut), committer.
6. Si le tableau est épuisé, proposer 2-3 nouvelles idées non-ML (même
   esprit : anomalie documentée, données déjà accessibles ou facilement
   récupérables gratuitement) et les ajouter avant de clore le cycle.

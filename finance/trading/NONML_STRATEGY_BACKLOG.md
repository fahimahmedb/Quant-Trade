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
| 2 | Effet tournant de mois (turn-of-month, J-1 à J+3) | OHLC déjà en local | **FAIT — PASS Sharpe (4/5)** mais **rendement absolu < Buy&Hold** sur la simulation 300€ (326,62€ vs 349,93€) → **RECLASSÉ FAIL sous la règle renforcée du 28/07** (voir ci-dessous). Voir `results/nonml_turn_of_month_result.md` |
| 3 | Effet jour-de-semaine (lundi/vendredi) | OHLC déjà en local | **FAIT — FAIL** (0/5 marchés), voir `results/nonml_day_of_week_result.md` |
| 4 | Momentum 52-semaines (proximité du plus haut annuel, George & Hwang 2004) | prix NDX-100 déjà récupérés (`data/pead/prices/`) | **FAIT — PASS (Sharpe ET rendement)**, plateau robuste 5/5, voir `results/nonml_momentum_52w_high_result.md` |
| 5 | Reversal court terme (1 semaine, niveau titre) | prix NDX-100 déjà récupérés | **FAIT — FAIL catastrophique** (-83,6% de rendement, Sharpe -1,02), voir `results/nonml_short_term_reversal_result.md` |
| 6 | Rallye de fin d'année ("Santa Claus rally", 5 derniers j. déc. + 2 premiers j. janv.) | OHLC déjà en local | **FAIT — FAIL** (0/5, structurel : ~2,8% du temps investi), voir `results/nonml_santa_claus_rally_result.md` |
| 7 | Effet pré/post jour férié US | OHLC déjà en local, détection data-driven (pas de calendrier codé en dur) | **FAIT — FAIL** (0/5, structurel : ~7% du temps investi), voir `results/nonml_holiday_effect_result.md` |
| 8 | Turn-of-month EN OVERLAY (reste investi 1x en permanence comme Buy&Hold, ajoute un levier supplémentaire SEULEMENT pendant la fenêtre ToM déjà identifiée au lieu d'être flat hors fenêtre) | OHLC déjà en local | **FAIT — PASS (4/5)**, plateau robuste CAP 1.5x-3.0x, voir `results/nonml_tom_overlay_result.md` |
| 9 | Barbell structuré (simulation) : cœur Buy&Hold + overlay levé (x2/x3) sur la fenêtre ToM ou sur les régimes de vol extrême déjà identifiés (Étape C) | OHLC déjà en local | à faire — profil façon note structurée, pas besoin de données d'options |
| 10 | Buy&Hold levé en continu (x2/x3 fixe, rebalancement quotidien) vs Buy&Hold 1x, test formel avec critère Sharpe+rendement sur les 5 marchés | OHLC déjà en local | à faire |

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

## Règle de succès RENFORCÉE (instruction utilisateur, 28/07/2026)

Une stratégie n'est un vrai succès QUE si elle bat Buy & Hold **à la fois**
en Sharpe **et** en rendement total net de coûts — un Sharpe supérieur
avec un rendement absolu inférieur (ex. cycle #2) ne compte plus comme
PASS, même si le critère pré-enregistré d'origine (Sharpe seul) était
formellement atteint. **Tout nouveau pré-enregistrement à partir de
maintenant doit inclure cette double condition explicitement dans son
critère de succès chiffré** (ex. "Sharpe > BH ET rendement total ≥ BH sur
≥4/5 marchés"). Les cycles #0 à #3 restent documentés avec leur verdict
d'origine (traçabilité), mais le cycle #2 est explicitement reclassé
FAIL sous cette règle (voir tableau ci-dessus) — pas de retuning caché,
juste une barre plus stricte assumée à partir de maintenant.

## Levier autorisé (instruction utilisateur, 28/07/2026)

Les stratégies futures peuvent inclure des variantes à effet de levier —
ne pas exclure le levier par défaut comme c'était implicitement le cas
jusqu'ici (toutes les stratégies testées étaient ≤1x). Toujours fixer un
CAP de levier a priori dans le pré-enregistrement (même logique que les
analyses Kelly/vol-targeting déjà faites, ex. CAP=2.0 ou 3.0, jamais
« illimité ») et ne jamais retoucher ce CAP après avoir vu un résultat.
Le risque plus élevé est explicitement accepté par l'utilisateur — mais
reste signalé honnêtement dans chaque rapport (MDD, pas seulement
Sharpe/rendement).

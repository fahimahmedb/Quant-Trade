# Pré-enregistrement — Estimateur de volatilité HAR-P (Corsi 2009) pour le mécanisme de vol-targeting

**Committé AVANT tout calcul.** Cycle #236 du backlog non-ML. Backlog "à
faire" épuisé après le #235 (batterie Règle 9 sur le #234) ; ce cycle
reprend la 1ère des 3 pistes proposées à la clôture du #235.

## Hypothèse

`src/volatility.py::fit_har`/`har_forecast` (HAR-RV de Corsi 2009 sur la
variance de Parkinson, Étape C) n'a jamais été réutilisé dans le backlog
non-ML — seuls EWMA (#231), GJR-t (#165/#234) et les 4 estimateurs
range-based (#50/#215/#221/#222) l'ont été. Le HAR-P était pourtant l'un
des 6 modèles déclarés à l'Étape C, et bat le benchmark GARCH-normal en
test DM sur les deux échantillons (Composite et NDX), même s'il n'a
jamais été le meilleur candidat ni testé au SPA famille entière comme
GJR-t/GJR-skewt. Ce cycle teste si sa prévision de variance (agrégation
journalier/hebdomadaire/mensuel de la RV Parkinson, rééchelonnée en
variance close-to-close via `c2c_scale`) est un bon **remplacement direct
de l'estimateur** du mécanisme hiérarchique #46 (comme le #165 l'a fait
avec GJR-t, mais ici avec le modèle le plus modeste de l'Étape C — un
contraste informatif attendu).

**Direction déclarée à l'avance (Règle 2)** : `Position(t) =
clip(TARGET_VOL_ANNUAL / vol_prévue_HAR-P(t), 0, CAP)` — remplacement
direct de l'estimateur (floor=0, comme #46/#50/#215/#221/#222/#231/#233),
PAS une porte (donc pas de floor=1).

## Définitions et alignement causal (déclarées avant calcul)

- Wrapper walk-forward à écrire (nouveau, aucun équivalent HAR dans
  `overlay.py` qui ne couvre que GJR-t) : pour chaque bloc de
  ré-estimation `[tr, tr+REFIT_EVERY)`, `fit_har(rv[:tr], r[:tr])` fixe
  les coefficients HAR sur l'information disponible à `tr` ; pour chaque
  `t` du bloc, `har_forecast(rv[:t], mod, 1)` recalcule la prévision avec
  les retards les plus récents disponibles (`rv[:t]`, information
  strictement antérieure à `t`) sans réestimer les coefficients — **exactement
  la convention déjà utilisée et validée à l'Étape C** (`run_etape_c.py`
  lignes ~127-129, Règle 7, aucune modification de logique).
- `rv` = `data_loader.py::parkinson_var_pct(df)`, alignée par construction
  avec `r = log_returns_pct(df)` (même longueur, vérifié comme à l'Étape C).
- `T0=750`, `REFIT_EVERY=21` — réutilisés tels quels du #165/#234 (Règle 7),
  bien que le fit HAR (OLS) soit nettement moins coûteux que le MLE GJR-t ;
  aucune valeur nouvelle introduite.
- `TARGET_VOL_ANNUAL=0,20`, `CAP=2,0`, `COST_BPS=5` bps — réutilisés à
  l'identique de toute la lignée #46-#233 (Règle 7).

## Univers et période

Les 5 marchés standards du backlog (Composite 5 ans, NDX 40 ans, Russell
2000, S&P 500, DAX) — HAR-P n'a pas la contrainte de scope du #165/#234
(qui découlait de la validation SPA du GJR-t spécifiquement sur NDX à
l'Étape C) : il est testé ici au même niveau que les 6 autres candidats
"estimateur" de la lignée (#46/#50/#215/#221/#222/#231/#233), tous évalués
sur l'univers complet.

## Critère de succès (n_trials=1, PASS niveau 1)

Identique à toute la lignée d'estimateurs : sur au moins **4 des 5
marchés**, l'estimateur doit battre Buy & Hold À LA FOIS en Sharpe
annualisé ET en rendement total net de coûts (règle renforcée).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le HAR-P était le modèle le plus modeste de l'Étape C (jamais le
   meilleur en QLIKE, jamais testé/validé au SPA famille) — sa prévision
   de variance pourrait être trop lissée (agrégation mensuelle) pour
   réagir assez vite aux chocs, produisant un profil proche de l'ATR
   (#233, FAIL, sous-exposition chronique) plutôt que de l'EWMA (#231, PASS).
2. Le rééchelonnement `c2c_scale` (calculé une fois sur la fenêtre
   d'entraînement de chaque refit) pourrait mal s'ajuster si le régime de
   gap overnight change significativement entre deux refits (21j) —
   risque distinct de celui des estimateurs range-based purs.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts :
`scripts/nonml_har_vol_targeting_overlay_backtest.py` (nouveau, wrapper
walk-forward HAR écrit pour ce cycle, réutilise `fit_har`/`har_forecast`
sans modification) et `scripts/nonml_har_vol_targeting_overlay_audit.py`.
Vérification via `nonml_anti_cheat_check.py har_vol_targeting_overlay`.

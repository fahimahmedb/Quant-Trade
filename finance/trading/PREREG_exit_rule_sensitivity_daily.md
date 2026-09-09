# Pré-enregistrement — Expérience C' : sensibilité à la règle de sortie (Stratégie A)

**Committé AVANT tout calcul.** Répond à la question de l'utilisateur :
*« Est-ce qu'on a tué une stratégie potentiellement intéressante avec un
take-profit trop court ? »* Entrée **strictement identique** à
`PREREG_daily_breakout_baseline.md` (Stratégie A) : long only,
`close>SMA50`, breakout 20j (high, décalé 1j), `RSI14∈[50,75]`, entrée
`open(t+1)`, ATR14 figé à l'entrée, stop initial `entry−1,5×ATR14`,
risque 0,5% equity composée/trade, coûts 5bps/transition, capital
5000€, Composite pré-enregistré, échantillon testable dès la 56e
séance. **Seule la règle de sortie change**, selon 6 variantes fixées
ci-dessous. `R = 1,5×ATR14(entrée)` (= distance du stop initial).

## Variantes (n_trials = 6, famille déclarée en bloc)

1. **TP=2R** (`entry+3,0×ATR`) — référence, **résultat déjà obtenu**
   (`nonml_daily_breakout_baseline_result.md`), réutilisé tel quel, pas
   recalculé.
2. **TP=3R** (`entry+4,5×ATR`).
3. **TP=4R** (`entry+6,0×ATR`).
4. **Trailing stop (chandelier), pas de TP fixe** : niveau du jour t =
   `max(stop_initial, max(high[entrée..t-1]) − 1,5×ATR14(entrée))` —
   calculé avec les plus hauts **strictement antérieurs** à t (aucun
   look-ahead), ne redescend jamais. Sortie si `low(t) ≤ niveau(t)`. Le
   passage au break-even puis au-delà est une conséquence mécanique de
   la formule (dès que le plus haut depuis l'entrée dépasse
   `entrée+1,5×ATR`), pas une règle séparée non validée.
5. **Pas de TP fixe, sortie sur rupture de tendance** : sortie à
   `close(t)` dès que `close(t) < SMA20(t)`, stop initial `1,5×ATR`
   toujours actif en parallèle (priorité stop si touché le même jour).
6. **Time stop** : structure identique à la variante 1 (TP=2R), mais
   sortie forcée à `close(t)` si le trade n'est pas clos par SL/TP dans
   les **10 séances** suivant l'entrée (valeur ronde fixée a priori,
   ~2 semaines de bourse, aucune grille testée). Teste spécifiquement
   l'hypothèse « les trades qui stagnent détruisent l'espérance ».

Priorité intra-jour identique à la baseline : si stop/trailing ET TP
sont touchés le même jour → stop prioritaire. Les sorties basées sur
`close(t)` (variantes 5 et 6) ne s'appliquent que si le stop n'a pas
déjà été touché ce jour-là.

## Critère de succès

Par variante, identique à la Stratégie A : PASS si, net de coûts, bat
B&H **simultanément** en Sharpe annualisé ET en rendement total sur le
même échantillon testable (dès la 56e séance — warmup identique à la
baseline).

**Correction multi-tests** : 6 variantes testées sur le même
échantillon → `prediction.py::dsr` (Deflated Sharpe Ratio) appliqué à
chaque variante avec `n_trials=6`. Une variante n'est déclarée
« statistiquement robuste » que si elle est PASS **ET** DSR>0,95 — même
seuil que la convention déjà utilisée à l'Étape B du repo. Un PASS
naïf sans DSR>0,95 est rapporté comme non concluant, pas comme un edge
validé.

## Rapport

Toutes les 6 variantes rapportées intégralement (aucune sélection après
coup) : Sharpe, rendement total, MDD, nombre de trades, hit rate, R
moyen, DSR. Répond honnêtement à la question posée, dans un sens ou
dans l'autre.

## Anti-cheat

Committé seul, avant `nonml_exit_rule_sensitivity_backtest.py`.
Vérification via `nonml_anti_cheat_check.py exit_rule_sensitivity`.

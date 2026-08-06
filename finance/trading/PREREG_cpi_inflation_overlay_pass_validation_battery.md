# Pré-enregistrement — Batterie Règle 9 sur le #338 (inflation réalisée CPI)

**Committé AVANT tout calcul.** Cycle #338 du backlog non-ML.

## Contexte et motivation

Le #338 (inflation réalisée CPI, PASS NET 5/5, robustesse plateau
parfait 15/15 — le meilleur profil brut de toute la session avec le
#200) n'a **jamais** été soumis à la batterie de validation renforcée
(Règle 9). Suite directe et naturelle du cycle précédent, dans la
continuité de la pratique déjà établie (#200 PASS suivi immédiatement
de sa propre batterie au #201, #335 PASS suivi de sa batterie au
#336).

## Adaptation technique

Le script `nonml_cpi_inflation_overlay_backtest.py` sauvegarde déjà le
couple `(pos, r_asset, dates, cost_bps)` au format attendu par le
script générique `nonml_pass_validation_battery.py` (convention
`.npz`, marché de référence NDX, comme tous les cycles récents) —
**aucune modification nécessaire**.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #338.

## Critère de succès (Règle 9, identique aux cycles #111-#336)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

**Prédiction explicite** (déclarée avant calcul, testable) : le #338
présente le profil niveau 1 le plus propre de toute la session (5/5
marchés, plateau de robustesse parfait 15/15, taux d'activation
modéré 16-34%, comparable au #200 qui avait obtenu le meilleur score
Règle 9 de la famille macro-externe à l'époque avant l'arrivée du
#335 — 3/5). Étant donné cette proximité structurelle avec le #200
(construction similaire : niveau brut/glissement, tercile expanding,
décalage causal simple, historique long ~40 ans sur NDX), un score
élevé pour cette famille (potentiellement 3/5, comme le #200/#201) est
plausible, avec crise et stabilité les plus probables à tenir (déjà
observé systématiquement sur cette famille de candidats macro à
historique long) et SPA/DSR les plus probables à échouer (échec
quasi-systématique de toute la famille macro-externe à ce jour, à
l'exception d'aucun cas). Rapporté honnêtement dans tous les cas, sans
retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #338. Sortie :
`results/nonml_cpi_inflation_overlay_pass_validation_battery.md`.

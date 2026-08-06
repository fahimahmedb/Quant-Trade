# Pré-enregistrement — Batterie Règle 9 sur le #344 (momentum du Bitcoin)

**Committé AVANT tout calcul.** Cycle #345 du backlog non-ML.

## Contexte et motivation

Le #344 (momentum du Bitcoin, PASS NET 5/5, premier signal d'une
classe d'actif crypto à atteindre le seuil renforcé dans ce backlog)
n'a **jamais** été soumis à la batterie de validation renforcée
(Règle 9). Suite directe et naturelle du cycle précédent, dans la
continuité de la pratique déjà établie (#200 PASS suivi immédiatement
de sa propre batterie au #201, #335→#336, #338→#340).

## Adaptation technique

Le script `nonml_bitcoin_momentum_overlay_backtest.py` sauvegarde déjà
le couple `(pos, r_asset, dates, cost_bps)` au format attendu par le
script générique `nonml_pass_validation_battery.py` (convention
`.npz`, marché de référence NDX, comme tous les cycles récents) —
**aucune modification nécessaire**.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #344.

## Critère de succès (Règle 9, identique aux cycles #111-#344)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance (spécifique à ce candidat)

**Prédiction explicite** (déclarée avant calcul, testable) : **le #344
a l'historique le plus court de toute construction ayant atteint un
PASS niveau 1 dans ce backlog** (Bitcoin utilisable ~2015+, soit
~2897 séances sur NDX contre ~8875-10272 pour la quasi-totalité des
autres candidats macro-externes). Deux conséquences attendues :

1. **Couverture de crise nécessairement incomplète** — le krach
   dot-com (2000-2002) et la crise financière 2008 sont
   STRUCTURELLEMENT hors de portée (le Bitcoin n'existait pas), seules
   le krach COVID (02-04/2020) et le resserrement 2022 pourront être
   évalués. Le script générique gère cela normalement (fenêtres non
   couvertes exclues de l'évaluation, comme déjà observé pour d'autres
   candidats à historique plus court que le maximum).
2. **Stabilité temporelle (4 folds) et DSR à n_trials élevé (350)
   probablement les plus exigeants** — échantillon effectif réduit
   par rapport aux constructions macro à 40 ans d'historique.

**Score anticipé, non garanti** : compte tenu de la solidité du
niveau 1 (5/5 net, MDD amélioré partout) mais de l'historique court,
un score modéré (2-3/5) est plausible — cohérent avec le schéma déjà
observé sur les candidats macro-externes solides mais à historique
réduit. Rapporté honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #344. Sortie :
`results/nonml_bitcoin_momentum_overlay_pass_validation_battery.md`.

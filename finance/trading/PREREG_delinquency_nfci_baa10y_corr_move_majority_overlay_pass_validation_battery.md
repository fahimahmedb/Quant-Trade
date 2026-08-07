# Pré-enregistrement — Batterie Règle 9 sur le #363 (panel élargi à 5 signaux +MOVE)

**Committé AVANT tout calcul.** Cycle #364 du backlog non-ML.

## Contexte et motivation

Le #363 (panel élargi à 5 signaux — défaut carte #286, NFCI #291,
BAA10Y #199, corrélation NDX-DAX #193, MOVE #357 —, vote majoritaire
≥4/5, **PASS NET 5/5, meilleur profil MDD de toute la famille des
portes combinées, robustesse plateau net 15/15**) n'a **jamais** été
soumis à la batterie de validation renforcée (Règle 9). Suite directe
et naturelle du cycle précédent, dans la continuité de la pratique
déjà établie pour CHAQUE PASS niveau 1 de cette famille (#296→#297,
#301→#300 [notation historique, voir #299/#302], #303→#302, #304→#306).

## Adaptation technique

Le script `nonml_delinquency_nfci_baa10y_corr_move_majority_overlay_backtest.py`
sauvegarde déjà le couple `(pos, r_asset, dates, cost_bps)` sur le
marché NDX au format attendu par le script générique
`nonml_pass_validation_battery.py` (convention `.npz`, marché de
référence NDX, comme tous les cycles récents) — **aucune modification
nécessaire**.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #363.

## Critère de succès (Règle 9, identique aux cycles #111-#363)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour = 367) doivent TOUS passer
pour un PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel
quel, sans retuning.

## Risque déclaré à l'avance (spécifique à ce candidat)

**Prédiction explicite** (déclarée avant calcul, testable) : le
meilleur score Règle 9 jamais obtenu par cette famille de portes
combinées est **3/5** (panel à 4 signaux, #304→#306 : coûts OK, crise
OK, stabilité OK, SPA ÉCHEC p=0,3378, DSR ÉCHEC 0,0001). Le panel à 5
signaux (#363) présente un profil niveau 1 **encore plus net** que le
panel à 4 (MDD amélioré sur les 5 marchés sans exception, contre
amélioration partielle au panel à 4) — **prédiction : un score
≥3/5 est plausible, avec un espoir raisonnable d'égaler ou de très
légèrement dépasser le record actuel de 3/5**, sans garantie. Le
DSR devrait rester en échec (n_trials=367, seuil structurel déjà
confirmé infranchi par tout candidat de ce backlog à ce jour, y
compris le MOVE seul à n_trials=362/363).

**Fenêtre testable réduite** (5951 séances NDX contre 6651 pour le
panel à 4) pourrait légèrement réduire le nombre de folds temporels
disponibles ou la couverture de certaines fenêtres de crise
(rappel : le panel à 4 démarrait en 01/2000, donc couvrait
partiellement la bulle internet ; le panel à 5 démarre en 11/2002,
après l'essentiel du krach dot-com) — **risque déclaré à l'avance** :
la couverture de crise pourrait perdre la fenêtre dot-com (2000-2002)
par rapport au panel à 4, ce qui serait un point de comparaison
défavorable si le score de crise en dépendait.

**Score anticipé, non garanti** : 3/5 (égaler le record) le plus
probable, rapporté honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #363. Sortie :
`results/nonml_delinquency_nfci_baa10y_corr_move_majority_overlay_pass_validation_battery.md`.

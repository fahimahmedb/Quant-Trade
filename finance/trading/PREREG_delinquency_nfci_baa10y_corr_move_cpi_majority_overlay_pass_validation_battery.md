# Pré-enregistrement — Batterie Règle 9 sur le #365 (panel élargi à 6 signaux +CPI)

**Committé AVANT tout calcul.** Cycle #366 du backlog non-ML.

## Contexte et motivation

Le #365 (panel élargi à 6 signaux — défaut carte #286, NFCI #291,
BAA10Y #199, corrélation NDX-DAX #193, MOVE #357, CPI #338 —, vote
majoritaire ≥5/6, **PASS NET 5/5, robustesse plateau net 15/15**)
n'a **jamais** été soumis à la batterie de validation renforcée
(Règle 9). Suite directe et naturelle du cycle précédent, dans la
continuité de la pratique déjà établie pour CHAQUE PASS niveau 1 de
cette famille (#296→#297, #301→#300/#299, #303→#302, #304→#306,
#363→#364). **Rappel** : le PREREG du #365 a explicitement déclaré
cette extension comme la DERNIÈRE construction de signal sur ce panel
(bornage formel) — cette batterie est donc le tout dernier cycle de
conformité protocolaire prévu pour cette famille, pas une nouvelle
extension.

## Adaptation technique

Le script `nonml_delinquency_nfci_baa10y_corr_move_cpi_majority_overlay_backtest.py`
sauvegarde déjà le couple `(pos, r_asset, dates, cost_bps)` sur le
marché NDX au format attendu par le script générique
`nonml_pass_validation_battery.py` (convention `.npz`, marché de
référence NDX, comme tous les cycles récents) — **aucune modification
nécessaire**.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #365.

## Critère de succès (Règle 9, identique aux cycles #111-#365)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour = 369) doivent TOUS passer
pour un PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel
quel, sans retuning.

## Risque déclaré à l'avance (spécifique à ce candidat)

**Prédiction explicite** (déclarée avant calcul, testable) : le
record actuel de la famille est **3/5** (panel à 5 signaux, #363→#364,
coûts/crise/stabilité OK, SPA/DSR ÉCHEC, stabilité parfaite 4/4). Le
panel à 6 signaux (#365) a un profil niveau 1 très proche du panel à 5
(mêmes fenêtres, même construction, seuil de vote légèrement plus
strict 83,3% contre 80%) — **prédiction : un score de 3/5 est
l'issue la plus probable** (répétition du même schéma structurel :
coûts/crise/stabilité OK, SPA/DSR ÉCHEC comme systématiquement dans ce
backlog), sans garantie qu'il dépasse ce plafond. Le DSR restera
presque certainement en échec (n_trials=369, seuil structurel déjà
confirmé infranchi par tout candidat de ce backlog, y compris les 2
panels précédents de cette même famille).

**Fenêtre testable identique au #363** (5951 séances NDX, le CPI ne
contraignant pas davantage la fenêtre) — donc pas de risque
supplémentaire de perte de couverture de crise par rapport au #364.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #365. Sortie :
`results/nonml_delinquency_nfci_baa10y_corr_move_cpi_majority_overlay_pass_validation_battery.md`.

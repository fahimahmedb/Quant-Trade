# Pré-enregistrement — Batterie Règle 9 sur le #304 (panel élargi 4 signaux, vote ≥3/4)

**Committé AVANT tout calcul.** Cycle #304 du backlog non-ML.

## Contexte et motivation

Le #304 (panel élargi à 4 signaux défaut carte #286 + NFCI #291 +
BAA10Y #199 + corrélation cross-marché NDX-DAX #193, vote majoritaire
≥3/4, PASS NET 5/5 marchés SANS EXCEPTION, robustesse 15/15 plateau
net) reste un PASS niveau 1, jamais un verdict final au sens de la
Règle 9 du protocole anti-snooping. Ce cycle applique la batterie de
validation renforcée, obligatoire avant toute déclaration de validité,
priorité sur toute nouvelle idée (déclaré à l'avance au cycle #303,
row #306).

## Adaptation technique : AUCUNE (réutilisation directe, Règle 7)

Identique aux #200→#201, #271→#272, #274→#275, #286→#287, #291→#290,
#296→#297, #301→#300, #303→#302 : le #304 est un overlay MONO-ACTIF
sur l'indice NDX-100 — le `.npz` déjà sauvegardé par son backtest
(`results/nonml_delinquency_nfci_baa10y_corr_majority_overlay_pnl.npz`)
correspond exactement au format attendu par l'outil déjà figé
`scripts/nonml_pass_validation_battery.py`. Aucun script dédié
nécessaire, aucune modification de code.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #304. Fenêtre plus courte que les batteries précédentes de
cette famille (~6650 séances contre ~8880), contrainte par le
calendrier commun NDX-DAX de la corrélation.

## Critère de succès (Règle 9, identique aux cycles #111-#304)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

Les quatre constructions précédentes sur ce panel de signaux de stress
(ET #296, majorité 2/3 #301, sizing continu #303) ont toutes plafonné
à 2/5 à leur propre batterie (#297, #300, #302) — stabilité,
SPA et/ou DSR systématiquement en échec malgré des PASS niveau 1
nets. Le #304 pourrait reproduire ce plafond, ou légèrement varier du
fait de la fenêtre testable plus courte (~6650 vs ~8880 séances,
moins de données pour la stabilité par fold) et du taux d'activation
plus sélectif (13,4-21,0%, vote ≥3/4 sur 4 signaux). Rapporté tel
quel, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #304. Sortie :
`results/nonml_delinquency_nfci_baa10y_corr_majority_overlay_pass_validation_battery.md`.

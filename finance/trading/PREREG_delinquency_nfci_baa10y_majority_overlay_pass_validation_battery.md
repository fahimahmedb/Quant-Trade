# Pré-enregistrement — Batterie Règle 9 sur le #301 (porte majoritaire ≥2/3 défaut carte+NFCI+BAA10Y)

**Committé AVANT tout calcul.** Cycle #300 du backlog non-ML.

## Contexte et motivation

Le #301 (porte majoritaire ≥2/3 défaut carte de crédit #286 + NFCI
#291 + spread de crédit BAA10Y #199, PASS NET 5/5 marchés SANS
EXCEPTION, robustesse 15/15 plateau net, meilleur rendement absolu de
toute la famille de portes combinées macro-externes) reste un PASS
niveau 1, jamais un verdict final au sens de la Règle 9 du protocole
anti-snooping. Ce cycle applique la batterie de validation renforcée,
obligatoire avant toute déclaration de validité, priorité sur toute
nouvelle idée (déclaré à l'avance au cycle #299, row #302).

## Adaptation technique : AUCUNE (réutilisation directe, Règle 7)

Identique aux #200→#201, #271→#272, #274→#275, #286→#287, #291→#290,
#296→#297 : le #301 est un overlay MONO-ACTIF sur l'indice NDX-100 —
le `.npz` déjà sauvegardé par son backtest
(`results/nonml_delinquency_nfci_baa10y_majority_overlay_pnl.npz`)
correspond exactement au format attendu par l'outil déjà figé
`scripts/nonml_pass_validation_battery.py`. Aucun script dédié
nécessaire, aucune modification de code.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #301.

## Critère de succès (Règle 9, identique aux cycles #111-#301)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

Le #296 (porte ET à 2 signaux) avait obtenu 2/5 à sa propre batterie
(#297) — un score identique au #291 seul (2/5), sous le #286 seul
(3/5, meilleur de la session). Le #301 (majorité à 3 signaux, taux
d'activation intermédiaire entre le #296 sélectif et le #298 sur-actif)
pourrait reproduire un score comparable (2-3/5) : le taux d'activation
plus élevé qu'au #296 (14,5-28,1% contre 5,8-24,3%) pourrait améliorer
la stabilité temporelle (plus de décisions actives par fold) mais la
composante BAA10Y (dont le score Règle 9 individuel n'a jamais été
testé isolément dans ce backlog) introduit une inconnue supplémentaire.
Rapporté tel quel, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #301. Sortie :
`results/nonml_delinquency_nfci_baa10y_majority_overlay_pass_validation_battery.md`.

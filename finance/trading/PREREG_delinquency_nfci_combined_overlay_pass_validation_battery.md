# Pré-enregistrement — Batterie Règle 9 sur le #296 (porte combinée ET défaut carte + NFCI)

**Committé AVANT tout calcul.** Cycle #297 du backlog non-ML.

## Contexte et motivation

Le #296 (porte combinée ET défaut de paiement cartes de crédit #286 +
conditions financières NFCI #291, PASS NET 5/5 marchés SANS EXCEPTION,
robustesse 15/15 plateau net) est le meilleur résultat de toute la
campagne macro-externe étendue (#276-296) — mais reste un PASS niveau
1, jamais un verdict final au sens de la Règle 9 du protocole
anti-snooping. Ce cycle applique la batterie de validation renforcée,
obligatoire avant toute déclaration de validité, priorité sur toute
nouvelle idée (déclaré à l'avance au cycle #296, row #299).

## Adaptation technique : AUCUNE (réutilisation directe, Règle 7)

Identique aux #200→#201, #271→#272, #274→#275, #286→#287, #291→#290 :
le #296 est un overlay MONO-ACTIF sur l'indice NDX-100 — le `.npz` déjà
sauvegardé par son backtest
(`results/nonml_delinquency_nfci_combined_overlay_pnl.npz`) correspond
exactement au format attendu par l'outil déjà figé
`scripts/nonml_pass_validation_battery.py`. Aucun script dédié
nécessaire, aucune modification de code.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #296.

## Critère de succès (Règle 9, identique aux cycles #111-#296)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

Le #296 combine deux composantes qui avaient chacune obtenu le
meilleur (#286, 3/5) et le 2e meilleur (#291, 2/5) score Règle 9 de
cette session. Le taux d'activation combiné est mécaniquement plus
faible que chaque composante seule (porte ET), ce qui pourrait réduire
la puissance statistique des tests SPA/DSR et/ou fragiliser la
stabilité temporelle (moins de décisions actives par fold) — risque
similaire à celui déjà anticipé et confirmé partiellement au #287
(fragilité de fréquence). Rapporté tel quel, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #296. Sortie :
`results/nonml_delinquency_nfci_combined_overlay_pass_validation_battery.md`.

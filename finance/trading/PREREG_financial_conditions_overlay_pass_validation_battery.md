# Pré-enregistrement — Batterie Règle 9 sur le #291 (conditions financières NFCI)

**Committé AVANT tout calcul.** Cycle #290 du backlog non-ML.

## Contexte et motivation

Le #291 (indice des conditions financières NFCI, PASS net 4/5,
robustesse 12/15 plateau cohérent) est un PASS niveau 1 — jamais un
verdict final au sens de la Règle 9 du protocole anti-snooping. Ce
cycle applique la batterie de validation renforcée, obligatoire avant
toute déclaration de validité, priorité sur toute nouvelle idée
(déclaré à l'avance au cycle #289).

## Adaptation technique : AUCUNE (réutilisation directe, Règle 7)

Identique aux #200→#201, #271→#272, #274→#275, #286→#287 : le #291 est
un overlay MONO-ACTIF sur l'indice NDX-100 — le `.npz` déjà sauvegardé
par son backtest (`results/nonml_financial_conditions_overlay_pnl.npz`)
correspond exactement au format attendu par l'outil déjà figé
`scripts/nonml_pass_validation_battery.py`. Aucun script dédié
nécessaire, aucune modification de code.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #291.

## Critère de succès (Règle 9, identique aux cycles #111-#291)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials=296) doivent TOUS passer pour un PASS
RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel, sans
retuning.

## Risque déclaré à l'avance

Le #291 partage un profil similaire au #286 (Sharpe ET rendement tous
deux supérieurs, pas seulement Sharpe), qui avait obtenu le meilleur
score Règle 9 de cette session (3/5 — coûts, crise, stabilité 4/4 OK,
SPA et DSR en échec). Un score comparable (2-3/5) est plausible pour le
#291, mais la fréquence hebdomadaire (contre trimestrielle pour le
#286) pourrait se traduire par une décision plus réactive et donc un
profil de stabilité potentiellement différent. Rapporté tel quel, sans
retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #291. Sortie :
`results/nonml_financial_conditions_overlay_pass_validation_battery.md`.

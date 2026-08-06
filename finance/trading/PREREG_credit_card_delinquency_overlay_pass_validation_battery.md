# Pré-enregistrement — Batterie Règle 9 sur le #286 (taux de défaut cartes de crédit)

**Committé AVANT tout calcul.** Cycle #285 du backlog non-ML.

## Contexte et motivation

Le #286 (taux de défaut cartes de crédit DRCCLACBS, PASS net 4/5,
robustesse 12/15 plateau cohérent) est un PASS niveau 1 — jamais un
verdict final au sens de la Règle 9 du protocole anti-snooping. Ce
cycle applique la batterie de validation renforcée, obligatoire avant
toute déclaration de validité, priorité sur toute nouvelle idée
(déclaré à l'avance au cycle #284).

## Adaptation technique : AUCUNE (réutilisation directe, Règle 7)

Identique aux #200→#201, #271→#272, #274→#275 : le #286 est un overlay
MONO-ACTIF sur l'indice NDX-100 — le `.npz` déjà sauvegardé par son
backtest (`results/nonml_credit_card_delinquency_overlay_pnl.npz`)
correspond exactement au format attendu par l'outil déjà figé
`scripts/nonml_pass_validation_battery.py`. Aucun script dédié
nécessaire, aucune modification de code.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #286.

## Critère de succès (Règle 9, identique aux cycles #111-#284)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials=291) doivent TOUS passer pour un PASS
RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel, sans
retuning.

## Risque déclaré à l'avance

Ce candidat a un profil inhabituel pour la famille macro-externe
récente (Sharpe ET rendement tous deux supérieurs, pas seulement
Sharpe) — un score Règle 9 meilleur que la moyenne de la famille
(souvent 1-3/5) est plausible, mais la fréquence trimestrielle du
signal sous-jacent (mises à jour au maximum 4 fois/an) pourrait
fragiliser spécifiquement la stabilité temporelle (peu de décisions
indépendantes par fold, même schéma déjà documenté pour les portes à
fréquence de décision lente — January Barometer #80/#213, pente SMA200
#68). Rapporté tel quel, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #286. Sortie :
`results/nonml_credit_card_delinquency_overlay_pass_validation_battery.md`.

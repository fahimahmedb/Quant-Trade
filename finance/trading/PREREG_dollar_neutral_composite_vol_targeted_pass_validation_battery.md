# Pré-enregistrement — Batterie Règle 9 sur le #350 (sleeve dollar-neutre vol-targeted)

**Committé AVANT tout calcul.** Cycle #351 du backlog non-ML.

## Contexte et motivation

Le #350 (sleeve dollar-neutre composite redimensionné par sa vol,
PASS sur son critère niveau 1 propre — Sharpe +0,61, t-stat +2,08) est
**la question centrale posée depuis `RECHERCHE_dsr_par_construction.md`** :
une construction à ampleur/neutralité structurellement plus favorable
peut-elle survivre à la batterie complète — en particulier au DSR, le
contrôle qui a fait échouer les 350 candidats précédents de ce
backlog sans aucune exception ? Suite directe et naturelle, dans la
continuité de la pratique déjà établie (tout PASS niveau 1 est soumis
à la Règle 9 au cycle suivant, ex. #200→#201, #335→#336, #344→#345).

## Adaptation technique (format PORTEFEUILLE, Règle 7)

Comme au #265/#266/#349, ce candidat est un portefeuille multi-actifs
(pas un scalaire mono-actif) — le format `.npz` standard de
`nonml_pass_validation_battery.py` ne s'applique pas directement. Un
script dédié `nonml_dollar_neutral_composite_vol_targeted_pass_validation_battery.py`
reconstruit en mémoire les paires `(rendement BRUT, turnover)`
candidat/référence, en réutilisant STRICTEMENT :
- les fonctions `check_a_cost_stress` à `check_e_dsr` déjà écrites et
  validées, importées SANS MODIFICATION de
  `nonml_momentum_turnover_doublesort_pass_validation_battery.py` ;
- la construction du sleeve du #349 (signaux #4/#73/#82/#15, z-score,
  dollar-neutre) et l'overlay de vol-targeting du #350/#46 (`TARGET_VOL_ANNUAL`,
  `VOL_WINDOW`, `CAP`), reconstruits identiquement en mémoire pour
  produire le couple `(rendement brut, turnover)` du pipeline COMPLET
  (composite → vol-targeting), nécessaire pour que le contrôle (a)
  (stress de coûts ×3/×5) puisse recalculer le P&L à différents
  niveaux de coût — décomposition algébrique exacte de la formule déjà
  committée du #350 (`r_vt = pos×raw_sleeve − [pos×turn_sleeve +
  |Δpos|]×cost_bps/1e4`), pas une nouvelle stratégie.
- Référence : Buy&Hold équipondéré univers PIT (identique au #349).

## Critère de succès (Règle 9, identique aux cycles #111-#350)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance (spécifique à ce candidat)

**Prédiction explicite** (déclarée avant calcul, testable) : le sleeve
vol-targeted est la construction la plus "market-neutral" jamais
testée à cette barre dans ce backlog (corrélation au marché mesurée à
-0,279 au #349) — le contrôle (b) crise et (c) stabilité pourraient
donc se comporter différemment de la famille macro-externe habituelle
(moins dépendant du régime de marché directionnel). **Le contrôle (e)
DSR reste anticipé comme le plus probable à échouer** : le t-stat de
2,08 correspond à un Sharpe encore loin de l'ordre de grandeur ~1,7-2,0
calculé dans `RECHERCHE_dsr_par_construction.md` §7 comme nécessaire à
`n_trials≈356`. **Score global anticipé mais non garanti : probablement
2-4/5**, avec DSR comme contrôle le plus probable à rester en échec —
ce serait la réponse empirique définitive à la question posée par
toute la Piste A/C. Rapporté honnêtement dans tous les cas.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification des scripts de backtest du #349/#350. Aucune
nouvelle donnée, aucun nouveau réglage. Sortie :
`results/nonml_dollar_neutral_composite_vol_targeted_pass_validation_battery.md`.

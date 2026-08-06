# Pré-enregistrement — Batterie Règle 9 sur le #303 (position graduée par nombre de votes)

**Committé AVANT tout calcul.** Cycle #302 du backlog non-ML.

## Contexte et motivation

Le #303 (position graduée par nombre de votes défaut carte #286 +
NFCI #291 + BAA10Y #199, PASS 4/5, robustesse 12/15 plateau cohérent)
reste un PASS niveau 1, jamais un verdict final au sens de la Règle 9
du protocole anti-snooping. Ce cycle applique la batterie de
validation renforcée, obligatoire avant toute déclaration de validité,
priorité sur toute nouvelle idée (déclaré à l'avance au cycle #301,
row #305).

## Adaptation technique : AUCUNE (réutilisation directe, Règle 7)

Identique aux #200→#201, #271→#272, #274→#275, #286→#287, #291→#290,
#296→#297, #301→#300 : le #303 est un overlay MONO-ACTIF sur l'indice
NDX-100 — le `.npz` déjà sauvegardé par son backtest
(`results/nonml_delinquency_nfci_baa10y_graduated_overlay_pnl.npz`)
correspond exactement au format attendu par l'outil déjà figé
`scripts/nonml_pass_validation_battery.py`. Aucun script dédié
nécessaire, aucune modification de code.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #303.

## Critère de succès (Règle 9, identique aux cycles #111-#303)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

Les trois constructions binaires précédentes sur ce même trio de
signaux (ET #296, majorité #301) ont toutes deux plafonné à 2/5 à leur
propre batterie (#297, #300) — stabilité temporelle et SPA/DSR en
échec systématique malgré des PASS niveau 1 nets. Le #303, bien que
structurellement différent (sizing continu), réutilise le même trio de
signaux sous-jacents et pourrait donc reproduire le même plafond de
2/5, voire un résultat légèrement différent si le turnover plus élevé
du sizing continu (4 niveaux de position au lieu de 2) affecte
différemment la stabilité par fold. Rapporté tel quel, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #303. Sortie :
`results/nonml_delinquency_nfci_baa10y_graduated_overlay_pass_validation_battery.md`.

# Pré-enregistrement — Batterie Règle 9 sur le #59 (January Barometer)

**Committé AVANT tout calcul.** Cycle #313 du backlog non-ML.

## Contexte et motivation

Le #59 (January Barometer, Hirsch : le rendement de janvier prédit
historiquement le signe du rendement annuel — PASS 5/5, plateau de
robustesse 5/5 à CAP 1.5x-2.0x, testé sur 41 années NDX) n'a **jamais**
été soumis à la batterie de validation renforcée (Règle 9), pourtant
obligatoire avant toute déclaration de validité finale. Ce cycle
applique cette exigence protocolaire — 2e candidat de la revue de
conformité initiée au #312 (#29), suite à la recommandation de la
synthèse v9 (#311) de ne plus forcer de recherche de NOUVELLES idées
tant que le backlog reste vide.

## Adaptation technique

Comme pour le #29 (#312), le script `nonml_january_barometer_overlay_backtest.py`
d'origine ne sauvegarde pas le couple `(pos, r_asset)` nécessaire à
`nonml_pass_validation_battery.py`. **Correction nécessaire, déclarée
ici avant tout calcul** : ajout d'une simple sauvegarde `.npz` pour le
marché NDX-100 à la fin de la boucle existante — AUCUNE modification
de la logique de calcul. Résultat re-exécuté et comparé (byte-identique
attendu) avant tout commit (Règle 4), même procédure que le #312.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #59.

## Critère de succès (Règle 9, identique aux cycles #111-#312)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

Le #59 partage la même limite méthodologique explicitement documentée
à son PREREG d'origine : décision ANNUELLE (~40 observations sur NDX),
un nombre d'occurrences de décision bien plus faible que la quasi-
totalité des candidats déjà testés en Règle 9 dans ce backlog (qui
décident quotidiennement ou hebdomadairement) — la stabilité par fold
(qui découpe l'historique en 4 segments non chevauchants) pourrait
être particulièrement fragile ici, chaque fold ne contenant qu'une
dizaine de décisions annuelles. Un échec de stabilité par manque
structurel d'observations par fold, distinct d'un manque d'edge réel,
est plausible et sera rapporté honnêtement si constaté, sans retuning.
Le design est également purement amplificateur (CAP=2,0x, jamais de
coupe défensive comme le #29) — un échec du stress de crise est
également plausible pour la même raison que le #29.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #59. Sortie :
`results/nonml_january_barometer_overlay_pass_validation_battery.md`.

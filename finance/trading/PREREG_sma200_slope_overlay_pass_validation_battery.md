# Pré-enregistrement — Batterie Règle 9 sur le #66 (filtre de pente SMA200)

**Committé AVANT tout calcul.** Cycle #314 du backlog non-ML.

## Contexte et motivation

Le #66 (filtre de pente SMA200 — SMA200(t) > SMA200(t-20), variante
"pente" du #29, PASS 5/5, plateau parfait sur les grilles CAP et
SLOPE_LAG) n'a **jamais** été soumis à la batterie de validation
renforcée (Règle 9). 3e candidat de la revue de conformité initiée au
#312. Ce cycle teste si une variante STRUCTURELLEMENT PROCHE du #29
(même mécanisme amplificateur CAP=2,0x, même sous-jacent SMA200, seule
la condition de déclenchement change — niveau vs pente) reproduit le
même profil de score Règle 9 (#29 et #59 ont tous deux obtenu 3/5 avec
SPA très fort et crise en échec net) ou en diffère.

## Adaptation technique

Comme pour le #29 (#312) et le #59 (#313), le script
`nonml_sma200_slope_overlay_backtest.py` d'origine ne sauvegarde pas
le couple `(pos, r_asset)`. **Correction nécessaire, déclarée ici
avant tout calcul** : ajout d'une sauvegarde `.npz` pour NDX-100 à la
fin de la boucle existante — AUCUNE modification de la logique de
calcul. Résultat re-exécuté et comparé (byte-identique attendu) avant
tout commit (Règle 4).

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #66.

## Critère de succès (Règle 9, identique aux cycles #111-#313)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

**Prédiction explicite** (déclarée avant calcul, testable) : étant
donné la proximité structurelle avec le #29 (même sous-jacent, même
mécanisme amplificateur, taux d'activation comparable ~67-79% contre
~70-75% pour le #29), un score et un profil similaires (3/5, SPA fort,
crise en échec) sont attendus. Si le résultat diverge notablement
(meilleur OU pire), ce sera un signal informatif sur l'apport réel de
la condition de pente par rapport au simple niveau — rapporté
honnêtement dans les deux cas, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #66. Sortie :
`results/nonml_sma200_slope_overlay_pass_validation_battery.md`.

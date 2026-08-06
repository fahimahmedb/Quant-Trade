# Pré-enregistrement — Batterie Règle 9 sur le #29 (filtre de tendance SMA200)

**Committé AVANT tout calcul.** Cycle #312 du backlog non-ML.

## Contexte et motivation

Le #29 (filtre de tendance SMA200, Faber 2007, PASS 5/5, plateau de
robustesse parfait sur la grille CAP 1.5x-3.0x, décrit dans son
propre résultat comme "le meilleur résultat du backlog à ce stade")
n'a **jamais** été soumis à la batterie de validation renforcée
(Règle 9), pourtant obligatoire avant toute déclaration de validité
finale selon `PROTOCOLE_ANTI_SNOOPING.md`. Ce cycle applique cette
exigence protocolaire — identifiée via une recherche systématique de
conformité (pas une nouvelle hypothèse spéculative), suite à la
recommandation de la synthèse v9 (#311) de ne plus forcer de
recherche de nouvelles idées tant que le backlog reste vide.

## Adaptation technique

Contrairement aux batteries récentes de ce backlog (#286→#287,
#291→#290, #296→#297...), le script `nonml_sma200_trend_overlay_backtest.py`
d'origine (écrit tôt dans ce backlog, avant l'instauration systématique
de la sauvegarde `.npz`) **ne sauvegarde pas** le couple `(pos, r_asset)`
nécessaire à `nonml_pass_validation_battery.py`. **Correction
nécessaire, déclarée ici avant tout calcul** : ajout d'une simple
sauvegarde `.npz` pour le marché NDX-100 (référence conventionnelle de
la batterie, comme pour tous les cycles précédents) à la fin de la
boucle existante du script — AUCUNE modification de la logique de
calcul, du signal, ou du résultat. Le script sera ré-exécuté après cet
ajout et le résultat textuel comparé pour confirmer qu'il est
inchangé avant de committer quoi que ce soit (Règle 4).

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #29.

## Critère de succès (Règle 9, identique aux cycles #111-#311)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

Le #29 est un overlay AMPLIFICATEUR (CAP=2,0x, jamais de coupe
défensive), contrairement à la quasi-totalité des candidats
récemment testés en Règle 9 dans ce backlog (portes défensives
CUT=0,5x de la famille macro-externe/combinaison). Son profil de
risque est structurellement différent (levier actif ~70-75% du temps,
MDD dégradé partout dans le backtest d'origine, signalé honnêtement
dès le #29) — un échec du stress de crise est plausible et attendu
(le signal ne coupe pas toujours rapidement en début de krach
prolongé, déjà documenté dans l'audit du #29 : 61,6% de jours encore
levés pendant les drawdowns NDX ≥40%). Rapporté tel quel, sans
retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #29. Sortie :
`results/nonml_sma200_trend_overlay_pass_validation_battery.md`.

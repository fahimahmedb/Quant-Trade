# Pré-enregistrement — Batterie Règle 9 sur le #33 (SMA200 + portefeuille Leaders)

**Committé AVANT tout calcul.** Cycle #315 du backlog non-ML.

## Contexte et motivation

Le #33 (filtre de tendance SMA200 appliqué au portefeuille Leaders
52-semaines, PASS, "meilleur ratio gain/risque de toutes les
combinaisons testées", déjà confirmé causal au #253 avec correction
`lag_one_day`) n'a **jamais** été soumis à la batterie de validation
renforcée (Règle 9). 4e candidat de la revue de conformité initiée au
#312, choisi cette fois pour sa DIVERSITÉ STRUCTURELLE (sous-jacent
stock-picking multi-titres, pas l'indice pur comme #29/#59/#66) plutôt
que sa proximité — le motif "SPA fort + crise faible" étant désormais
établi 3/3 sur la famille indice pur.

## Adaptation technique (déclarée ici, AVANT tout calcul)

Contrairement au #29/#59/#66 (overlay mono-actif sur l'indice), le #33
est un portefeuille MULTI-TITRES (33 titres Leaders, rebalancé tous les
21j) — la batterie générique `nonml_pass_validation_battery.py` (conçue
pour un couple scalaire `pos, r_asset`) ne s'applique pas directement.
**Réutilisation stricte (Règle 7)** du patron déjà établi au #259
(batterie du #258, momentum+turnover, même problème structurel résolu) :
script dédié `nonml_sma200_leaders_overlay_pass_validation_battery.py`
qui reconstruit les paires (rendement BRUT, turnover) pour le candidat
(`weights_lev`, portefeuille+overlay) et la référence (`weights_base`,
portefeuille Leaders seul — PAS Buy&Hold, référence déjà utilisée dans
le backtest d'origine du #33), en réutilisant `lag_one_day` du #33 et
en import direct des 5 fonctions de contrôle (`check_a`...`check_e`)
déjà écrites et validées au #259 (génériques : elles ne dépendent que
des tableaux raw/turn/dates/coût, pas du nom du candidat).

## Référence

Portefeuille Leaders 1.0x (cycle #4) — identique à la référence déjà
utilisée dans le backtest d'origine du #33, PAS Buy&Hold.

## Critère de succès (Règle 9, identique aux cycles #111-#314)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

**Prédiction explicite** (déclarée avant calcul, testable) : étant
donné que le mécanisme de porte (SMA200 sur l'indice, CAP=2,0x,
jamais de coupe défensive) reste identique à celui du #29/#59/#66, un
échec de la crise est probable pour la même raison structurelle.
Cependant, le sous-jacent stock-picking (33 titres, rebalancés
périodiquement, historique limité 2021-2026 seulement — contrairement
aux 40 ans de l'indice NDX) pourrait produire un profil de stabilité
et de SPA DIFFÉRENT (échantillon bien plus court, moins de folds
informatifs) — rapporté honnêtement dans les deux cas.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #33. Sortie :
`results/nonml_sma200_leaders_overlay_pass_validation_battery.md`.

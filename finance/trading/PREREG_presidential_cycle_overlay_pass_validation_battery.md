# Pré-enregistrement — Batterie Règle 9 sur le #30 (cycle électoral pré-électoral seul)

**Committé AVANT tout calcul de la batterie.** Cycle #189 du backlog
non-ML. Corrige l'écart de procédure signalé honnêtement au #188
(aucun PREREG dédié n'avait été committé avant cette application de la
batterie sur les 4 candidats calendaires #176/#179/#182/#184) — ce
cycle applique la même leçon.

## Contexte et motivation

Le #30 (`PREREG_presidential_cycle_overlay.md`,
`results/nonml_presidential_cycle_overlay_result.md`) est le PASS niveau
1 calendaire le plus solide du backlog (5/5 marchés, plateau parfait sur
CAP 1,5x-3,0x) et l'input direct du #179 (combiné) et du #182 (AND
Halloween×pré-électorale), tous deux déjà soumis à la batterie au #188.
Le #30 lui-même, en tant que composante ISOLÉE, n'a jamais été soumis à
la batterie renforcée — trou de couverture identifié explicitement dans
la section « Bilan pour la suite » du #188. Aucune nouvelle donnée,
aucun nouveau réglage : application mécanique de l'outil déjà figé
`nonml_pass_validation_battery.py` (5 contrôles a-e, identiques depuis
le #111) à un résultat déjà committé.

## Marché de référence pour la batterie

NDX (40 ans) — historique le plus long, cohérent avec le choix déjà fait
pour #38/#134/#149/#165/#176/#179/#182/#184.

## Modification technique requise (déclarée avant calcul)

`nonml_presidential_cycle_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_presidential_cycle_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement de
logique de calcul — vérifié par re-exécution identique du résultat déjà
committé (`nonml_presidential_cycle_overlay_result.md` inchangé après
modification).

## Critère de succès (Règle 9, identique aux cycles #111-#188)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1 (aucune grille testée, application
mécanique d'un outil déjà figé, aucune connaissance préalable du
résultat).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le #30 lève systématiquement (CAP=2,0x) pendant l'année
   pré-électorale — si cette fenêtre chevauche une phase de crise
   (aucune des 4 fenêtres de crise pré-enregistrées ne tombe
   nécessairement en année pré-électorale, mais ce n'est pas garanti à
   l'avance), le contrôle (b) pourrait échouer comme il a échoué pour 3/4
   candidats au #188.
2. Le DSR à n_trials≥189 est hors de portée pour absolument tout
   candidat testé jusqu'ici dans ce backlog (188 hypothèses, 0
   exception) — aucune raison structurelle d'attendre que le #30 y
   échappe.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_presidential_cycle_overlay_backtest.py` (modifié pour
sauvegarder le `_pnl.npz`, aucun changement de logique). Vérification via
`nonml_anti_cheat_check.py presidential_cycle_overlay`.

# Pré-enregistrement — Batterie Règle 9 sur le #219 (vol-targeting gaté par la kurtosis glissante)

**Committé AVANT tout calcul de la batterie.** Cycle #226 du backlog
non-ML. Continue le pivot Règle 9 (3e candidat après #215/#217 aux
#224/#225).

## Contexte et motivation

Le #219 (`PREREG_kurtosis_vol_targeting_overlay.md`,
`results/nonml_kurtosis_vol_targeting_overlay_result.md`) est le 3e PASS
niveau 1 chronologique de la série #215-223. PASS niveau 1 4/5 (seul DAX
échoue), **plateau de robustesse PARFAIT 8/8** — le meilleur profil brut
avec le #215/#221 — et **audit parfait** (0 désaccord de recalcul
indépendant sur les 5 marchés). Continue la couverture Règle 9 un
candidat à la fois.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-
#214, #224, #225).

## Modification technique requise (déclarée avant calcul)

`nonml_kurtosis_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_kurtosis_vol_targeting_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement de
logique de calcul — vérifié par re-exécution identique du résultat déjà
committé.

## Critère de succès (Règle 9, identique aux cycles #111-#225)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le plateau de robustesse parfait (8/8) et l'audit parfait ne
   garantissent pas un bon score Règle 9 — le #78 (dispersion, plateau
   parfait 8/8 également) n'a jamais été testé en Règle 9, mais le #215
   (Garman-Klass, plateau parfait 8/8) a obtenu 4/5 alors que le #221
   (Rogers-Satchell, plateau parfait 8/8 également, pas encore testé)
   pourrait diverger — aucune garantie de transfert entre les deux
   critères.
2. La kurtosis, comme le VR (#217, Règle 9 1/5) et la skewness (#218,
   FAIL niveau 1), est un moment statistique d'ordre supérieur
   potentiellement bruité sur des fenêtres de 252 observations — le
   risque de fragilité de stabilité déjà matérialisé pour le #217
   pourrait se reproduire.
3. Le DSR est hors de portée pour les 226 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_kurtosis_vol_targeting_overlay_backtest.py` (modifié pour
sauvegarder le `_pnl.npz`, aucun changement de logique). Vérification
via `nonml_anti_cheat_check.py kurtosis_vol_targeting_overlay`.

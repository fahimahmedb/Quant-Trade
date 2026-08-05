# Pré-enregistrement — Batterie Règle 9 sur le #222 (vol-targeting estimateur Yang-Zhang)

**Committé AVANT tout calcul de la batterie.** Cycle #229 du backlog
non-ML. Continue le pivot Règle 9 (6e candidat après #215/#217/#219/
#220/#221 aux #224-#228).

## Contexte et motivation

Le #222 (`PREREG_yang_zhang_vol_targeting_overlay.md`,
`results/nonml_yang_zhang_vol_targeting_overlay_result.md`) est le 6e
PASS niveau 1 chronologique de la série #215-223. PASS net sur les 5
marchés, **meilleur MDD de toute la lignée d'estimateurs** (NDX -82,9%→
-61,1%, contre -67,5%/-67,7% pour Garman-Klass/Rogers-Satchell, déjà
tous deux 4/5 en Règle 9 aux #224/#228) — exposition moyenne nettement
plus faible (1,09x-1,52x) grâce à la composante overnight. Premier
accroc de robustesse niveau 1 de la lignée d'estimateurs (3/5 à
fenêtre=15j). Continue la couverture Règle 9 un candidat à la fois.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-
#214, #224-#228).

## Modification technique requise (déclarée avant calcul)

`nonml_yang_zhang_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_yang_zhang_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#228)

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

1. Les #215/#221 (Garman-Klass, Rogers-Satchell), tous deux à exposition
   moyenne PLUS ÉLEVÉE que le #222, ont échoué précisément sur le
   contrôle de crise (resserrement 2022) en Règle 9. Le #222, dont
   l'exposition moyenne est nettement plus FAIBLE (composante overnight
   augmentant l'estimation de vol), pourrait au contraire RÉUSSIR ce
   contrôle — ou échouer ailleurs (coûts, stabilité) pour une raison
   différente, compte tenu de son premier accroc de robustesse niveau 1
   déjà observé (3/5 à fenêtre=15j).
2. Le DSR est hors de portée pour les 229 hypothèses testées jusqu'ici
   sans aucune exception.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_yang_zhang_vol_targeting_overlay_backtest.py` (modifié
pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
yang_zhang_vol_targeting_overlay`.

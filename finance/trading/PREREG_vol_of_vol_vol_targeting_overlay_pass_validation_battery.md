# Pré-enregistrement — Batterie Règle 9 sur le #220 (vol-targeting gaté par la vol-de-la-vol glissante)

**Committé AVANT tout calcul de la batterie.** Cycle #227 du backlog
non-ML. Continue le pivot Règle 9 (4e candidat après #215/#217/#219 aux
#224/#225/#226).

## Contexte et motivation

Le #220 (`PREREG_vol_of_vol_vol_targeting_overlay.md`,
`results/nonml_vol_of_vol_vol_targeting_overlay_result.md`) est le 4e
PASS niveau 1 chronologique de la série #215-223. PASS niveau 1 4/5
(seul Russell 2000 échoue), robustesse correcte (CAP 4/5-5/5, fenêtre de
vol 3/5-4/5), **3e audit parfait consécutif** de la série (0 désaccord).
Continue la couverture Règle 9 un candidat à la fois.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-
#214, #224-#226).

## Modification technique requise (déclarée avant calcul)

`nonml_vol_of_vol_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_vol_of_vol_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#226)

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

1. Les deux moments statistiques d'ordre supérieur déjà testés en Règle
   9 (VR #217 : 1/5, kurtosis #219 : 2/5) ont tous deux échoué sur la
   stabilité temporelle (2/4 folds) — le vol-de-la-vol, un signal de
   second ordre sur la volatilité elle-même plutôt qu'un moment
   statistique classique, pourrait partager ou non ce même profil de
   fragilité.
2. L'échantillon testable démarre plus tard que les autres candidats
   (empilement de 3 fenêtres VOL_WINDOW+VOV_WINDOW+MEDIAN_WINDOW) — les
   4 folds de stabilité disposeront donc de moins de séances chacun,
   ce qui pourrait amplifier le bruit d'estimation par fold.
3. Le DSR est hors de portée pour les 227 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_vol_of_vol_vol_targeting_overlay_backtest.py` (modifié
pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
vol_of_vol_vol_targeting_overlay`.

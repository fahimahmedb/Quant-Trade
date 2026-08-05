# Pré-enregistrement — Batterie Règle 9 sur le #78 (vol-targeting gaté par la dispersion cross-sectionnelle NDX-100)

**Committé AVANT tout calcul de la batterie.** Cycle #214 du backlog
non-ML. Applique la même discipline que les #189/#190/#194/#201/#207-
#213 (PREREG dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #78 (`PREREG_dispersion_vol_targeting_overlay.md`,
`results/nonml_dispersion_vol_targeting_overlay_result.md`) est le
dernier des 7 dérivés du #46 cités à l'origine (#47/#50/#54/#57/#68/#78/
#80) qui n'avait pas encore reçu la batterie Règle 9 — les 6 autres sont
désormais couverts (#207-#213). Il avait été explicitement écarté au
PREREG du #213 en raison de son échantillon restreint (~2021-2026, 1385
séances, contre l'historique complet 40 ans des autres candidats) : ce
cycle complète malgré tout la couverture, en documentant honnêtement les
limites de l'échantillon plutôt qu'en l'excluant indéfiniment (Règle 2 —
ne pas éviter un test gênant, le déclarer et l'exécuter).

## Limite d'échantillon déclarée à l'avance (Règle 2)

Le signal de dispersion cross-sectionnelle n'est disponible que depuis
~2021 (leçon du #77, reprise au #78). Sur les 4 fenêtres de crise du
contrôle b, seule **« Resserrement 2022 »** est couvre par l'échantillon
(2022-01-01 à 2022-12-31) ; dot-com, 2008 et COVID (02-04/2020) sont
antérieures au début du signal et seront rapportées comme non
disponibles (n<20 séances), pas comme des échecs silencieux. Le contrôle
c (4 folds) portera sur des folds d'environ 340 séances chacun (~2021-
2022, 2022-2023, 2023-2024/25, 2025-2026), une granularité beaucoup plus
fine que sur les candidats à historique 40 ans.

## Marché de référence pour la batterie

NDX (seul marché testé par le #78, signal dépendant des titres composant
l'indice) — cohérent avec les candidats précédents (NDX = référence
constante depuis le #207).

## Modification technique requise (déclarée avant calcul)

`nonml_dispersion_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_dispersion_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps), sans aucun changement de logique de
calcul — vérifié par re-exécution identique du résultat déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#213)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise — MDD candidat pas pire que Buy&Hold (tolérance 1 pt)
   sur les fenêtres réellement disponibles (ici : 2022 seulement).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Un échantillon de seulement 1385 séances donne des tests statistiques
   (SPA, folds) mécaniquement moins puissants que sur 10000+ séances —
   un résultat FAIL pourrait refléter le manque de puissance plutôt
   qu'une absence réelle d'edge.
2. Une seule fenêtre de crise disponible (2022) rend le contrôle b peu
   informatif comparé aux 4 fenêtres des autres candidats.
3. Le DSR est hors de portée pour les 214 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_dispersion_vol_targeting_overlay_backtest.py` (modifié
pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
dispersion_vol_targeting_overlay`.

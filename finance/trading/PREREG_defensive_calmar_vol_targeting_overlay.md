# Pré-enregistrement — Vol-targeting DÉFENSIF, critère Calmar (objectif Étape D)

**Committé AVANT tout calcul.** Cycle #115 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md` pour la batterie standard
(voir note ci-dessous sur son interprétation dans ce cas particulier).

## Hypothèse et relation explicite au #44 (transparence anti-snooping)

Le mécanisme (vol-targeting purement défensif, `position = clip(cible_vol
/ vol_réalisée, 0.0, 1.0x)`, JAMAIS de levier) a déjà été testé au #44
et a **FAIT — FAIL** sous le critère de succès standard "Sharpe ET
rendement > BH" : Sharpe amélioré et MDD massivement réduit sur 5/5
marchés, mais rendement systématiquement inférieur à Buy&Hold. **Ce
cycle NE RE-TESTE PAS la même hypothèse dans l'espoir d'un verdict
différent** — il applique un critère de succès EXPLICITEMENT DIFFÉRENT
(Calmar = rendement annualisé / |MDD|), qui est l'objectif RÉEL et
DÉJÀ DOCUMENTÉ de l'Étape D dans `CLAUDE.md` avant même l'existence de
ce backlog : *"Objectif : Sharpe/Calmar ≥ Buy & Hold avec MDD nettement
inférieur"*. Le résultat du #44 (Sharpe et MDD tous deux améliorés,
rendement seul en retrait) rend cette hypothèse a priori PLUS
plausible sous Calmar que sous le critère renforcé standard — c'est
précisément pourquoi ce critère alternatif, déjà envisagé dans le
`CLAUDE.md` du projet, est testé ici formellement pour la première fois
dans ce backlog. `TARGET_VOL_ANNUAL=20%` (pas 15% comme le #44 initial)
est repris du #46, qui a établi AVANT ce cycle que 20% ferme mieux
l'écart de rendement que 15% — paramètre fixé par précédent documenté,
pas choisi après avoir vu le résultat de CE test.

## Définition (fixée ici, avant tout résultat)

- `Position(t) = clip(20% / vol_réalisée_20j(t-1), 0.0, 1.0x)` —
  jamais de levier, coupe l'exposition en régime de vol élevée
  (identique au #44, seul `TARGET_VOL_ANNUAL` diffère : 20% au lieu de
  15%, cf. précédent #46).
- **Coûts** : 5 bps par unité de turnover.
- Univers : 5 marchés déjà en local (même convention que #44/#54/#57) —
  Composite (5 ans), NDX (40 ans), Russell 2000, S&P 500, DAX.
- **Référence** : Buy & Hold sur chaque marché.

## Critère de succès (pré-enregistré, DÉLIBÉRÉMENT différent de la règle
renforcée standard — Calmar, pas Sharpe+rendement)

L'overlay doit battre Buy&Hold en **Calmar ratio** (rendement annualisé
net de coûts / |MDD|) sur **au moins 4 des 5 marchés** (même seuil de
majorité que #54/#57). n_trials=1 pour ce critère Calmar (jamais testé
formellement dans ce backlog).

## Batterie de validation renforcée (Règle 9, SI PASS Calmar)

`scripts/nonml_pass_validation_battery.py defensive_calmar_vol_
targeting_overlay` sera tout de même exécutée pour information
(n_trials=taille du backlog), MAIS ses contrôles (a) stress coûts et
(c) stabilité temporelle sont bâtis sur le critère Sharpe/rendement
standard, pas Calmar — un échec de CES contrôles précis ne contredit
PAS nécessairement un succès Calmar, et sera interprété avec cette
nuance explicite dans le rapport. Les contrôles (b) stress crise, (d)
SPA et (e) DSR restent directement pertinents (basés sur le pnl brut,
pas sur le critère de succès choisi).

## Robustesse prévue (SI PASS Calmar)

Grille de perturbation non-tunable : TARGET_VOL_ANNUAL ∈ {15%, 20%,
25%, 30%} et fenêtre de vol ∈ {15j, 20j, 25j, 30j}.

## Anti-cheat

Ce fichier committé avant
`nonml_defensive_calmar_vol_targeting_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py defensive_calmar_vol_targeting_overlay`.

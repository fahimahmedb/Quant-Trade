# Pré-enregistrement — Correction "taux réaliste sur cash" appliquée au #44 (vol-targeting défensif, cible 15%)

**Committé AVANT tout calcul.** Cycle #149 du backlog non-ML. Sous la
**Règle 9** et la **Règle 10** (nouvellement adoptée) de
`PROTOCOLE_ANTI_SNOOPING.md`.

## Correction de la piste initialement proposée (documentée honnêtement, AVANT tout calcul)

La piste #149 du backlog ciblait à l'origine #9 (`vol_regime_overlay`)
et #58 (`lowvol_regime_vol_targeting_overlay`) comme candidats
DÉFENSIFS à re-tester avec la correction du #142. **Vérification du
code AVANT toute écriture de PREREG de calcul** : ces deux mécanismes
utilisent en réalité `np.clip(exposure, 1.0, CAP)` — ils restent
TOUJOURS investis à au moins 1,0x et amplifient SEULEMENT en régime de
vol (comme la quasi-totalité des overlays calendaires/tendance déjà
disqualifiés au #146) — **aucune fraction de capital hors-marché**,
donc la correction du #142/Règle 10 ne s'applique PAS à eux, exactement
le même constat qu'au #146 pour la famille calendaire.

**Candidat de remplacement, identifié par la même vérification** : le
#44 (`nonml_defensive_vol_targeting_overlay_backtest.py`), qui utilise
`np.clip(vol_cible/vol_réalisée, 0.0, 1.0)` — un VRAI mécanisme
défensif (jamais de levier, exposition peut descendre à 0), avec
`TARGET_VOL_ANNUAL=15%` (pas 20% comme le #115/#134 corrigé). FAIL
originel documenté au backlog : "#43 vol-targeting cible 15%... FAIL
sur le rendement (exposition moyenne <1x)... la variante cible 20%
(#46) referme l'écart". Bon candidat car son FAIL est attribué au
sous-dimensionnement (cible trop basse), motif DIFFÉRENT du #55
(signal structurellement mauvais) — teste si la correction Règle 10
peut, en plus de la diversification, compenser ce sous-dimensionnement.

## Définition (fixée ici, avant tout résultat)

- Position équity : `vol_target_position(r)` du #44
  (`TARGET_VOL_ANNUAL=15%`, `VOL_WINDOW=20j`, `CAP=1.0`), STRICTEMENT
  INCHANGÉE.
- Fraction complémentaire `(1-pos_eq(t))` allouée au proxy obligataire
  DGS10 (duration modifiée 10 ans, formule identique au
  #134/#136/#137/#139/#141/#146) au lieu du cash à 0%.
- `r_combiné(t) = pos_eq(t)*r_NDX(t) + (1-pos_eq(t))*r_bond(t)`.
- Coûts : 5 bps par unité de turnover.
- Marché : NDX (40 ans), cohérent avec le reste de la famille.

## Critère de succès (pré-enregistré, IDENTIQUE au #44 original)

Sharpe ET rendement net de coûts > Buy&Hold (critère standard, celui
utilisé par le #44 original). n_trials=1 pour cette correction précise.

## Batterie de validation renforcée (Règle 9, SI PASS)

`scripts/nonml_pass_validation_battery.py
cash_rate_correction_defensive_vol_targeting_44`, n_trials=taille
totale du backlog (jamais 1).

## Anti-cheat

Ce fichier committé avant
`nonml_cash_rate_correction_defensive_vol_targeting_44_backtest.py`,
vérification via `nonml_anti_cheat_check.py
cash_rate_correction_defensive_vol_targeting_44`. Aucune nouvelle
donnée (mécanisme #44 et DGS10 déjà committés).

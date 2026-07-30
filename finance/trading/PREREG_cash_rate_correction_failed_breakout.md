# Pré-enregistrement — Correction "taux réaliste sur cash" appliquée au #55 (faux breakout Donchian)

**Committé AVANT tout calcul.** Cycle #146 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Le #142 a montré que 86-89% du gain du #134 vient du simple portage
(taux positif au lieu de 0% cash) sur la fraction "hors-marché" du
mécanisme. Cette leçon a une portée plus large que le seul #115/#134 :
tout overlay du backlog qui réduit l'exposition SOUS 1,0x (donc laisse
une fraction du capital implicitement en cash à 0%) a potentiellement
sous-estimé son propre résultat de la même façon.

**Candidat choisi (le plus net du backlog, revue faite AVANT ce
pré-enregistrement, pas après avoir vu quel candidat "marcherait
mieux")** : le #55 (faux breakout Donchian, `nonml_failed_breakout_
overlay_backtest.py`), qui réduit l'exposition à `FLOOR=0,5x` pendant
5 jours après un faux breakout confirmé (~35-37% du temps sur les 5
marchés déjà testés), 1,0x sinon — donc 50% du capital reste
implicitement en cash à 0% pendant ~35-37% du temps. FAIL originel :
"le manque à gagner dépasse largement la protection de MDD apportée".
Choisi car c'est le mécanisme "floor partiel" le plus simple et le
mieux documenté du backlog (pas #115/#134, déjà exhaustivement testés).

## Définition (fixée ici, avant tout résultat)

- Position équity : `failed_breakout_position(close)` du #55,
  STRICTEMENT INCHANGÉE (mêmes seuils DONCHIAN_WINDOW=20,
  CONFIRM_WINDOW=2, DEFENSE_LEN=5, FLOOR=0,5).
- Fraction complémentaire `(1-pos_eq(t))` (0,5 pendant les 5j
  défensifs, 0 sinon) allouée au proxy obligataire DGS10 (duration
  modifiée 10 ans, formule identique au #134/#136/#137/#139/#141) au
  lieu du cash à 0%.
- `r_combiné(t) = pos_eq(t)*r_marché(t) + (1-pos_eq(t))*r_bond(t)`.
- Coûts : 5 bps par unité de turnover (identique au #55).
- Marché : NDX (40 ans), cohérent avec le reste de la famille
  diversification. Les 4 autres marchés du #55 (Composite, Russell
  2000, S&P 500, DAX) ne sont PAS re-testés dans ce cycle (limite le
  scope à une vérification de principe, pas une nouvelle campagne
  cross-marché complète).

## Critère de succès (pré-enregistré, IDENTIQUE au #55 original)

Sharpe ET rendement net de coûts > Buy&Hold (critère standard, celui
utilisé par le #55 original). n_trials=1 pour cette correction précise.

## Batterie de validation renforcée (Règle 9, SI PASS)

`scripts/nonml_pass_validation_battery.py
cash_rate_correction_failed_breakout`, n_trials=taille totale du
backlog (jamais 1).

## Anti-cheat

Ce fichier committé avant
`nonml_cash_rate_correction_failed_breakout_backtest.py`, vérification
via `nonml_anti_cheat_check.py cash_rate_correction_failed_breakout`.
Aucune nouvelle donnée (mécanisme #55 et DGS10 déjà committés).

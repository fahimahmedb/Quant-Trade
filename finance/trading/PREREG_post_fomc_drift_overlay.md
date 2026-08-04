# Pré-enregistrement — Effet POST-FOMC (résolution d'incertitude), overlay levé

**Committé AVANT tout calcul.** Cycle #173 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec le #171

Le #171 (FAIL, 3/5) a testé l'anticipation PRÉ-annonce (Lucca & Moench
2015). Ce cycle teste un mécanisme économique DIFFÉRENT : la résolution
de l'incertitude — une fois la décision connue (14h le 2e jour de
réunion), le marché pourrait continuer de dériver le jour même et le
lendemain (littérature sur la réaction post-annonce et la sous-réaction
initiale aux communiqués de politique monétaire). **Réutilise
intégralement** la liste `FOMC_DATES` (95 dates, sourcées et citées au
#171 depuis federalreserve.gov, `PREREG_pre_fomc_drift_overlay.md` §1) —
aucun nouveau sourcing, Règle 7.

## 2. Marchés testés (figés, identiques au #171)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 3. Mécanisme (figé)

- Réutilise `FOMC_DATES` de `nonml_pre_fomc_drift_overlay_backtest.py`
  (import direct, Règle 7 — aucune redéfinition de la liste).
- Fenêtre : **jour de l'annonce lui-même ET le lendemain** (2 séances),
  alignement causal data-driven identique au #171 (jour de bourse
  correspondant à la date dans l'index du marché, `searchsorted`).
- `position(t) = 2.0x` sur cette fenêtre, `1.0x` sinon. CAP=2.0x réutilisé
  tel quel. Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que le #171)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (même liste de dates que le #171, une fenêtre différente
fixée avant calcul — mécanisme économique distinct, pas un retest de la
même hypothèse : le #171 teste l'ANTICIPATION avant l'annonce, celui-ci
teste la RÉSOLUTION après).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme au #171, l'edge pourrait être trop faible en ampleur (190 jours
   sur plusieurs milliers de séances, <2% du temps) pour dépasser les
   coûts sur ≥4/5 marchés.
2. Si le marché intègre l'information de l'annonce quasi instantanément
   (hypothèse d'efficience forte), il n'y a par construction aucune
   dérive post-annonce à capter — contrairement à la dérive
   PRÉ-annonce (anticipation), qui a une justification comportementale
   plus documentée dans la littérature (Lucca & Moench).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

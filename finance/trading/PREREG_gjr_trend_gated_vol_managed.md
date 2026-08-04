# Pré-enregistrement — Mécanisme hiérarchique gaté (#47) avec volatilité PRÉVUE GJR-t au lieu de réalisée

**Committé AVANT tout calcul.** Cycle #168 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Le #47 (`nonml_trend_vol_targeting_overlay_backtest.py`) combine deux
mécanismes gagnants : porte directionnelle 52w-high indice (#37) + vol-
targeting (#46), sur la volatilité RÉALISÉE glissante 20j :

```
position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)  si tendance haussière
            = 1.0x                                            sinon
```

PASS 4/5 marchés. Ce cycle teste **exactement la même architecture**
(porte trend + plancher 1.0x + plafond 2.0x + cible 20%), en remplaçant
UNIQUEMENT la volatilité réalisée glissante par la volatilité PRÉVUE
GJR-GARCH(1,1)-t walk-forward déjà validée (Étape C / #165 / #166),
**aucun autre paramètre changé**. Motivation : le #165 a montré que la vol
PRÉVUE, utilisée SEULE (sans porte directionnelle), donne un edge de
mécanisme qui ne généralise pas au financement réaliste (#166, Règle 10)
hors NDX. Ce cycle teste si l'AJOUT de la porte directionnelle — qui a
systématiquement amélioré les signaux de vol RÉALISÉE dans ce backlog
(#35, #39, #47…) — change cette conclusion pour la vol PRÉVUE.

## 2. Marchés testés (figés, raison explicite d'exclusion du Composite)

**4 marchés, PAS 5** : NDX, S&P 500, Russell 2000, DAX — les seuls où le
GJR-t a été validé au SPA (Q1, `results/etape_C_{ndx,sp500,russell2000,dax}*.md`
— NDX à l'Étape A/C d'origine, les 3 autres au #166). Le **Composite est
explicitement exclu** : à l'Étape C, le SPA famille entière sur le
Composite échoue (p≈0,11–0,15, `CLAUDE.md`, limite d'échantillon) — tester
le mécanisme avec une prévision non validée sur ce marché mélangerait Q1
et Q2, exactement ce que le #166 avait refusé de faire.

## 3. Mécanisme (figé, réutilisation stricte Règle 7)

- Porte directionnelle : `near_high_mask()` du #47, IDENTIQUE
  (INDEX_LOOKBACK=252, INDEX_THRESHOLD=0.95), alignement causal `trend[:-1]`
  (bug de fuite d'un jour déjà trouvé et corrigé au #47, réutilisé tel quel).
- Volatilité : `walk_forward_vol_forecast` de `finance/src/overlay.py`
  (T0=750, REFIT_EVERY=21, GJR-t), IDENTIQUE au #165/#166. La prévision
  `vol_fcst[t]` est déjà conditionnée à l'information disponible en t-1
  (documenté et vérifié au #165) — aucun décalage supplémentaire requis,
  contrairement à la vol réalisée du #47 qui nécessite `np.roll(...,1)`.
- Formule : `position(t) = clip(20% / vol_prévue_GJR-t(t), 1.0, 2.0x)` si
  `trend[t-1]` haussière (au sens de l'alignement causal ci-dessus), sinon
  `1.0x`. Fenêtre testable : `t ≥ T0 = 750` (contrainte du GJR-t, plus
  stricte que la contrainte de tendance `t ≥ 252`).
- Coûts 5 bps, comme tout le backlog.

## 4. Critère de succès (figé AVANT tout calcul, raisonnement explicite)

Le #47 exigeait ≥4/5 marchés (80%). Avec 4 marchés au lieu de 5, le seuil
proportionnellement équivalent (80% de 4 = 3,2) est arrondi à l'entier
supérieur par prudence (règle renforcée, jamais assouplie) :

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts (critère renforcé du 28/07/2026,
> les deux jambes obligatoires par marché).

**n_trials = 1** pour ce cycle (une architecture, un critère multi-marché,
aucune variante testée).

## 5. Engagement Règle 10 (déclaré à l'avance, comme au #166)

Si PASS : avant toute communication comme edge authentique, décomposition
Règle 10 (portage DGS3MO réel des deux côtés) sur chaque marché PASS,
exactement comme au #166 — le #166 a montré que l'edge brut du mécanisme
vol-prévue seul ne survit pas au financement réaliste hors NDX ; il faut
vérifier si la porte directionnelle change cette conclusion.

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme au #166, le mécanisme pourrait ne pas survivre à un financement
   réaliste même s'il est PASS au sens 0%/0% — c'est précisément testé
   au §5.
2. La porte directionnelle réduit le temps où le vol-targeting est actif ;
   si le gain du #165 vient surtout des périodes de baisse (régime non
   haussier, où la porte impose 1.0x), la porte pourrait ANNULER l'edge
   plutôt que le renforcer — contrairement à ce qui a été observé avec la
   vol réalisée (#46→#47).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

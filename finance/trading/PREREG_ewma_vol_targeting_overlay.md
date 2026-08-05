# Pré-enregistrement — Overlay de vol-targeting, estimateur EWMA (RiskMetrics)

**Committé AVANT tout calcul.** Cycle #231 du backlog non-ML. La série
#215-223 (5 estimateurs range-based + 6 portes de moments/second ordre)
est désormais entièrement couverte niveau 1 ET Règle 9 (#224-#230, 0/7
PASS RENFORCÉ). Ce cycle introduit un 6e estimateur pour le mécanisme
#46 — l'écart-type EWMA (moyenne mobile exponentiellement pondérée,
convention RiskMetrics), déjà implémenté et validé à l'Étape C
(`src/volatility.py::ewma_path`) mais **jamais réutilisé comme moteur
d'exposition du mécanisme hiérarchique non-ML jusqu'ici** (les 5
estimateurs #46/#50/#215/#221/#222 utilisent tous une MOYENNE MOBILE
SIMPLE de variance sur `VOL_WINDOW=20` jours — l'EWMA pondère les
observations récentes plus fortement, avec une mémoire théoriquement
infinie plutôt qu'une fenêtre tronquée).

## Hypothèse

`Position(t) = clip(20% / vol_EWMA(t-1), 0.0, 2.0x)` où `vol_EWMA` suit
la même récursion que `ewma_path` (`λ=0,94`, valeur par défaut de la
fonction déjà implémentée et validée à l'Étape C — réutilisée à
l'identique, Règle 7) : `s²(t+1) = λ·s²(t) + (1-λ)·r(t)²`. Hypothèse :
la pondération exponentielle, en réagissant plus vite aux chocs récents
qu'une moyenne mobile simple tronquée à 20 jours, produit un mécanisme
de vol-targeting qui bat Buy & Hold en Sharpe ET en rendement total net
de coûts, comme la majorité des estimateurs déjà testés.

## Adaptation causale déclarée à l'avance (Règle 2)

`ewma_path` tel qu'implémenté dans `src/volatility.py` calcule les écarts
par rapport à la moyenne de l'ÉCHANTILLON ENTIER (`eps = r - r.mean()`)
— approprié pour un diagnostic ponctuel à l'Étape C, mais **une fuite de
données futures** si réutilisé tel quel sur toute la série pour une
décision de trading quotidienne (la moyenne de l'échantillon entier
n'est jamais connue à l'avance). Ce cycle utilise donc une variante
strictement causale :
- **Pas de démoyennage** (convention RiskMetrics standard — les
  rendements quotidiens actions sont proches de zéro en moyenne, la
  littérature originale RiskMetrics n'inclut pas de terme de moyenne) :
  récursion directement sur `r(t)²`, pas sur `(r(t)-r̄)²`.
- **Amorçage causal** : `s²` initialisée à la variance échantillon des
  `VOL_WINDOW=20` premiers rendements (réutilise `VOL_WINDOW`, Règle 7),
  qui ne dépend que du passé à ce stade de l'historique — pas un choix
  arbitraire post-hoc.
- `λ=0,94` réutilisé tel quel (valeur par défaut de `ewma_path`, Règle
  7 — pas de nouveau réglage).
- Alignement causal identique au reste de la lignée : `vol_EWMA(t)`
  construite à partir de `r(<t)` uniquement, appliquée à `r(t)` avec le
  décalage d'un jour habituel.

## Univers et période

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — rendements
déjà disponibles, aucun nouveau fetch. Fonction `ewma_path` déjà
implémentée à l'Étape C, réutilisée comme référence de formule (pas
appelée directement, pour la raison causale ci-dessus).

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#223).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. L'absence de démoyennage (choix causal ci-dessus) pourrait légèrement
   sous- ou sur-estimer la variance réelle par rapport à `ewma_path`
   original — écart attendu minime (rendements quotidiens actions proche
   de zéro en moyenne) mais déclaré à l'avance comme limite méthodologique.
2. La réactivité accrue de l'EWMA (mémoire longue mais poids décroissant
   exponentiellement, contre une fenêtre tronquée à 20j pour les #46/
   #50/#215/#221/#222) pourrait produire une exposition plus volatile
   (plus de rotations, coûts de transaction plus élevés) sans gain net
   correspondant.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_ewma_vol_targeting_overlay_backtest.py` (nouveau).
Vérification via `nonml_anti_cheat_check.py ewma_vol_targeting_overlay`.

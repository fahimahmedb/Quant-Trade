# Pré-enregistrement — Overlay de vol-targeting, estimateur ATR (Wilder 1978)

**Committé AVANT tout calcul.** Cycle #233 du backlog non-ML. La série
#215-223 ET le #231 (EWMA) sont désormais entièrement couverts niveau 1
ET Règle 9 (0 PASS RENFORCÉ). Ce cycle introduit un 7e estimateur pour
le mécanisme #46 — l'ATR (Average True Range, Wilder 1978), déjà
implémenté à l'Étape B (`src/prediction.py::_atr`, utilisé pour
construire des features techniques) mais **jamais réutilisé comme moteur
d'exposition du mécanisme hiérarchique non-ML jusqu'ici**.

## Hypothèse

L'ATR est une mesure d'AMPLITUDE (pas de variance statistique comme les
6 estimateurs déjà testés #46/#50/#215/#221/#222/#231) : `True Range(t) =
max(H(t)-L(t), |H(t)-C(t-1)|, |L(t)-C(t-1)|)`, moyennée par le lissage
de Wilder (`n=14`, valeur par défaut de `_atr`, réutilisée à l'identique,
Règle 7 — équivalent à un EWM avec α=1/14). Contrairement aux #46/#50/
#215/#221 (ne capturent pas le saut overnight), le True Range INCLUT le
gap clôture-veille→ouverture via les termes `|H-C(t-1)|` et `|L-C(t-1)|`
— comme le #222/#231 (Yang-Zhang, EWMA), mais par une formule
d'AMPLITUDE MAXIMALE plutôt qu'une décomposition statistique de variance
ou une récursion sur les rendements au carré. Hypothèse : cet estimateur
de nature différente (technique/amplitude plutôt que statistique)
produit un mécanisme de vol-targeting qui bat Buy & Hold en Sharpe ET en
rendement total net de coûts.

`Position(t) = clip(20% / vol_ATR(t-1), 0.0, 2.0x)` où `vol_ATR(t) =
(ATR(t) / Close(t)) × √252` — conversion en amplitude FRACTIONNELLE
annualisée par la même convention `√252` que tout le reste de la lignée
(Règle 7), déclarée à l'avance comme une heuristique standard en gestion
de position par ATR (pas un estimateur non biaisé de variance comme
Parkinson/GK/RS/YZ, mais directement comparable en ordre de grandeur —
même limite méthodologique reconnue explicitement).

## Univers et période

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — OHLC déjà en
local, aucun nouveau fetch. Fonction `_atr` déjà implémentée à l'Étape B,
réutilisée telle quelle (`n=14`).

## Mécanisme (identique aux #46/#50/#215/#221/#222/#231, seul l'estimateur change)

CAP=2.0 et TARGET_VOL_ANNUAL=0.20 réutilisés à l'identique du #46 (Règle
7). Coût 5 bps aller-retour. Alignement causal identique au reste de la
lignée : `ATR(t)` connu à la clôture du jour t (ne dépend que d'OHLC
jusqu'au jour t), appliqué à `r(t+1)=log(close(t+1)/close(t))` via le
décalage d'un jour habituel.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#231).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. L'ATR n'est pas un estimateur non biaisé de variance (contrairement
   aux 4 estimateurs range-based déjà testés) — la conversion en
   proxy de volatilité annualisée via `√252` est une heuristique standard
   en gestion de position technique, pas une dérivation statistique
   rigoureuse ; le résultat pourrait diverger significativement en
   échelle des autres estimateurs malgré une formule superficiellement
   similaire.
2. Le lissage de Wilder (`α=1/14`, mémoire ~14 jours effective) est plus
   réactif que la moyenne mobile simple 20j des #46/#50/#215/#221 mais
   moins réactif que le λ=0,94 du #231 (EWMA RiskMetrics, mémoire
   effective ~1/(1-λ)≈17j — comparable en ordre de grandeur en fait) —
   un résultat très proche du #231 est possible.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_atr_vol_targeting_overlay_backtest.py` (nouveau).
Vérification via `nonml_anti_cheat_check.py atr_vol_targeting_overlay`.

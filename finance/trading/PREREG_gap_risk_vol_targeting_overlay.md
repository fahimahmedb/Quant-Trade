# Pré-enregistrement — Overlay vol-targeting gaté par le risque de gap d'ouverture

**Committé AVANT tout calcul.** Cycle #216 du backlog non-ML. Idée #216
proposée au cycle #215 (backlog "à faire" épuisé à ce moment-là), première
ligne "à faire" de ce cycle.

## Hypothèse

Le mécanisme hiérarchique de vol-targeting (#46) a déjà été gaté par la
tendance (#47/#68), le calendrier (#54), la confirmation multi-marché
(#57), la dispersion cross-sectionnelle (#78) et une porte annuelle
(#80) — tous des signaux de RÉGIME DIRECTIONNEL/CALENDAIRE. Ce cycle
introduit un type de porte encore jamais testé : le **risque de gap
d'ouverture** (amplitude moyenne glissante des sauts clôture-veille →
ouverture-du-jour), qui capture un risque de SAUT/DISCONTINUITÉ plutôt
qu'un régime directionnel. Une amplitude de gap récente FAIBLE (marché
"calme", peu de sauts) est l'hypothèse retenue comme condition favorable
à l'amplification du vol-targeting (même logique "favorable = amplifier"
que toutes les portes précédentes) ; une amplitude de gap élevée
(marché "nerveux", sauts fréquents) laisse l'exposition à 1,0x (pas de
levier supplémentaire).

Direction déclarée AVANT tout calcul (Règle 2) : porte active (gate=True,
amplification autorisée) quand `GapRisk_avg(t) <= médiane glissante 252j
de GapRisk_avg`, c'est-à-dire un risque de gap récent SOUS sa propre
médiane historique récente.

## Définitions et alignement causal (déclarés avant calcul)

- `gap(t) = |log(open(t) / close(t-1))|`, connu à l'OUVERTURE du jour t
  (donc a fortiori connu à la clôture du jour t, avant la décision).
- `GapRisk_avg(t)` = moyenne glissante de `gap` sur `GAP_WINDOW=20`
  séances se terminant au jour t (fenêtre réutilisée à l'identique de
  `VOL_WINDOW`, Règle 7 — pas de nouveau réglage).
- Porte = `GapRisk_avg(t) <= rolling_median_252j(GapRisk_avg)(t)`
  (`MEDIAN_WINDOW=252` réutilisé à l'identique des #78/#100, Règle 7).
- Convention causale identique à toutes les portes hiérarchiques
  précédentes (#47/#54/#57/#68/#78/#80) : `gate[i]` connu à la clôture du
  jour i (jour de décision) s'applique à `r[i]=log(close[i+1]/close[i])`
  → `gate[:-1]`, PAS `gate[1:]` (qui serait une fuite d'un jour).

## Mécanisme (identique aux #47/#54/#57/#68/#78/#80)

`Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
active, `1.0x` sinon. CAP=2.0, TARGET_VOL_ANNUAL=0.20, VOL_WINDOW=20
réutilisés à l'identique du #46 (Règle 7). Coût 5 bps aller-retour.
Échantillon testable à partir de la 253e séance (MEDIAN_WINDOW=252
dominant, même convention que #78/#100).

## Univers

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — OHLC déjà en
local, aucun nouveau fetch.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#215).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le risque de gap pourrait ne pas être un signal de régime persistant
   (contrairement à la tendance ou au calendrier) — les gaps sont par
   nature des chocs ponctuels, une moyenne glissante courte (20j) pourrait
   être dominée par un petit nombre d'événements isolés plutôt que
   refléter un vrai régime de marché.
2. La direction choisie (calme = amplifier) pourrait être inversée dans
   les données : si un risque de gap ÉLEVÉ précède en fait des phases de
   rendement fort (ex. reprise volatile après une correction), la porte
   inactiverait le levier exactement quand il serait profitable.
3. Le DSR est hors de portée pour les 216 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_gap_risk_vol_targeting_overlay_backtest.py` (nouveau).
Vérification via `nonml_anti_cheat_check.py
gap_risk_vol_targeting_overlay`.

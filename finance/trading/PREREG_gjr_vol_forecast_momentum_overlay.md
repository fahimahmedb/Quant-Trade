# Pré-enregistrement — Direction du changement de la prévision GJR-t (accélération/décélération), overlay binaire

**Committé AVANT tout calcul.** Cycle #170 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Les cycles #165/#166 (niveau continu), #168 (porte directionnelle) et
#169 (régime de tercile) exploitent tous le NIVEAU de la vol prévue
GJR-t — et échouent à généraliser au-delà de NDX (#166, #168, #169
FAIL/non-robuste hors NDX). Ce cycle teste un signal structurellement
différent, jamais essayé dans ce backlog : le SENS DE VARIATION de la
prévision plutôt que son niveau. Motivation économique : un régime qui
**décélère** (la vol prévue baisse) pourrait signaler une transition vers
le calme, distincte d'un régime simplement "déjà bas" (#169) ou "déjà en
tendance haussière de prix" (#168, corrélation possible mais pas
identité). Si les 3 précédentes variantes échouent pour la même raison
structurelle (l'edge de #165 est spécifique à l'historique NDX), ce
cycle devrait échouer aussi — mais c'est un signal assez différent pour
mériter un test isolé plutôt que d'être présumé.

## 2. Marchés testés (figés, même exclusion qu'aux #166/#168/#169)

4 marchés : NDX, S&P 500, Russell 2000, DAX (Composite exclu, SPA GJR-t
non validé dessus à l'Étape C).

## 3. Mécanisme (figé, réutilisation stricte Règle 7)

- Prévision : `walk_forward_vol_forecast` (T0=750, REFIT_EVERY=21, GJR-t),
  IDENTIQUE aux #165/#166/#168/#169.
- Signal de direction : `delta(t) = vol_fcst(t) − vol_fcst(t − LAG)`, avec
  **LAG = REFIT_EVERY = 21 jours** — valeur réutilisée telle quelle (le
  cycle naturel de ré-estimation du moteur, zéro nouveau paramètre de
  fenêtre à choisir, conforme à la Règle 2).
- Formule : `position(t) = 2.0x si delta(t) < 0` (vol prévue en baisse sur
  les 21 derniers jours -> décélération), `1.0x sinon` (hausse ou stable).
  CAP=2.0x et FLOOR=1.0x réutilisés tels quels (valeurs standard de toute
  la famille vol-targeting du backlog).
- Fenêtre testable : `t ≥ T0 + LAG` (besoin de `vol_fcst(t-LAG)` pour
  calculer le premier delta).
- Coûts 5 bps.

## 4. Critère de succès (figé, même seuil que les #166/#168/#169)

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal de direction, un LAG fixé par cohérence avec
REFIT_EVERY — pas un balayage —, un critère multi-marché).

## 5. Engagement Règle 10 (déclaré à l'avance, comme aux #166/#169)

Si PASS sur un marché : décomposition Règle 10 (financement DGS3MO réel)
avant toute communication comme edge authentique, la position pouvant
dépasser 1.0x une partie du temps.

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme les #166/#168/#169, l'edge pourrait à nouveau être spécifique à
   NDX et ne pas généraliser — motif désormais répété 3 fois dans ce
   backlog pour la famille vol-prévue GJR-t.
2. Le signal de direction sur 21 jours pourrait être trop bruyant (la
   variance conditionnelle GJR-t peut osciller sans tendance nette sur un
   mois), diluant tout edge réel du niveau déjà documenté au #165.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

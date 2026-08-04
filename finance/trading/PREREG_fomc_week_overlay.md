# Pré-enregistrement — Semaine FOMC entière (incertitude générale, J-2 à J+2), overlay levé

**Committé AVANT tout calcul.** Cycle #174 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les #171/#173

Le #171 (anticipation, J0 en termes de rendement réalisé — voir §3) a
donné 3/5 (edge positif mais insuffisant). Le #173 (résolution, J+1/J+2)
a donné 0/5 (FAIL net, l'overlay sous-performe partout). Ce cycle teste
une hypothèse DISTINCTE : l'incertitude est élevée sur TOUTE la semaine
entourant la réunion (pas seulement le jour d'anticipation ou de
résolution), et cette incertitude élevée pourrait porter une prime de
risque compensatrice sur l'ensemble de la fenêtre — hypothèse
structurellement différente de "il existe un jour précis de dérive
directionnelle" (mécanisme testé aux #171/#173). Réutilise
`FOMC_DATES` (95 dates, sourcées au #171) — aucun nouveau sourcing.

**Attente honnête déclarée à l'avance** : combiner un jour à edge positif
insuffisant (#171) et deux jours à edge négatif net (#173) dans une même
fenêtre élargie risque STRUCTURELLEMENT de donner un résultat pire que le
#171 seul — ce cycle teste si la prime de risque de la semaine entière
compense malgré tout cette dilution, pas une tentative déguisée de
retrouver le résultat du #171.

## 2. Marchés testés (figés, identiques aux #171/#173)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 3. Mécanisme (figé, convention causale explicite)

Sous la convention déjà établie (`bh_full[k] = log(close[k+1]/close[k])`
est le rendement RÉALISÉ le jour de bourse `k+1`) : pour capter les
rendements réalisés sur les **5 séances J-2 à J+2** entourant l'index
`ann_idx` de la date d'annonce dans le calendrier du marché (J-2, J-1, J0
=jour d'annonce, J+1, J+2), il faut lever la position aux indices
`k = ann_idx-3` jusqu'à `k = ann_idx+1` inclus (5 valeurs consécutives —
`k+1` parcourt alors exactement `ann_idx-2` à `ann_idx+2`). Implémentation
autonome (pas une réutilisation des fonctions `pre_fomc_mask`/`post_fomc_mask`
des #171/#173, pour éviter toute ambiguïté d'offset — mais même liste
`FOMC_DATES` et même alignement `searchsorted`).

`position(t) = 2.0x` sur cette fenêtre de 5 séances par réunion, `1.0x`
sinon. CAP=2.0x réutilisé tel quel. Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que les #171/#173)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (même liste de dates, une fenêtre élargie fixée avant
calcul, mécanisme économique distinct — prime de risque d'incertitude
générale, pas un signal directionnel ponctuel).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme anticipé au §1, la dilution du signal #171 par les 2 jours à
   edge négatif du #173 (plus 2 jours supplémentaires jamais testés,
   J-2 et J+2) pourrait suffire à faire échouer ce cycle même si une
   prime de risque de la semaine entière existe réellement mais est
   faible en amplitude.
2. Coûts de transaction plus élevés que les #171/#173 pris séparément
   (fenêtre 5x plus large par réunion, ~475 jours-séance/marché contre 95
   ou 190).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

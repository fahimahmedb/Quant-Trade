# Pré-enregistrement — Porte du ratio vol Parkinson / vol close-to-close pour le vol-targeting

**Committé AVANT tout calcul.** Cycle #239 du backlog non-ML. Backlog "à
faire" épuisé après le #238 (batterie Règle 9 sur le #237) ; ce cycle
reprend la 1ère des 3 pistes proposées à la clôture du #238 (déjà
proposée une première fois à la clôture du #235).

## Hypothèse

Deux estimateurs de volatilité déjà validés séparément dans ce backlog —
la vol close-to-close (#46, dénominateur du mécanisme standard) et la vol
Parkinson range-based (#50, `data_loader.py::parkinson_var_pct`, PASS) —
mesurent des choses distinctes : la vol Parkinson NE CAPTE QUE la
variance intra-séance (haut/bas), en ignorant l'écart d'ouverture
(overnight gap, cf. docstring de `parkinson_var_pct`), tandis que la vol
close-to-close capte l'ensemble (intra-séance + gap). Ce cycle construit
un signal de régime NOUVEAU à partir du RATIO des deux, jamais testé —
distinct du #216 (porte de gap risk, PASS niveau 1 sur le gap BRUT
`|log(open(t)/close(t-1))|`, FAIL 2/5) qui mesurait directement
l'amplitude des gaps plutôt qu'une proportion relative aux deux
composantes de la variance totale.

**Direction déclarée à l'avance (Règle 2)** : un ratio Parkinson/close-to-
close ÉLEVÉ signifie que l'essentiel de la variance récente vient du
mouvement intra-séance CONTINU plutôt que des sauts d'ouverture — régime
plus "ordonné"/moins sujet aux chocs discontinus = calme = amplifier
(même logique "calme=amplifier" que #216/#219/#220/#223/#237). Porte
active quand `ratio(t) >= médiane glissante 252j de ratio`.

## Définitions et alignement causal (déclarées avant calcul)

- `vol_park_ann(t)` = `sqrt(rolling_mean_20j(parkinson_var_pct))(t) * sqrt(252)`,
  décalée d'un jour (`np.roll(...,1)`, convention standard du VOL_WINDOW=20
  déjà utilisée pour la jambe close-to-close du mécanisme #46).
- `vol_c2c_ann(t)` = `rolling_std_20j(r_pct)(t) * sqrt(252)`, même
  décalage d'un jour — c'est EXACTEMENT le dénominateur déjà utilisé par
  le mécanisme #46, réutilisé sans modification (Règle 7).
- `ratio(t) = vol_park_ann(t) / vol_c2c_ann(t)` (les deux jambes décalées
  du même jour, donc le ratio lui-même est causal par construction).
- `VOL_WINDOW=20` et `MEDIAN_WINDOW=252` réutilisés à l'identique de toute
  la lignée #46-#238 (Règle 7).
- `Position(t) = clip(20% / vol_c2c_20j(t-1), 1.0, 2.0x)` si porte active,
  `1.0x` sinon — mécanisme #46 standard INCHANGÉ (CAP=2.0, COST_BPS=5 bps,
  Règle 7).
- Échantillon testable à partir de la ~272e séance (20j amorçage + 252j
  médiane).

## Univers et période

Les 5 marchés standards du backlog (Composite, NDX, Russell 2000, S&P
500, DAX) — même périmètre que toute la lignée de portes #47-#237.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur au moins **4 des 5 marchés**, l'overlay doit battre Buy & Hold À LA
FOIS en Sharpe annualisé ET en rendement total net de coûts (règle
renforcée identique à toute la lignée #46-#238).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le #216 (gap brut) a déjà échoué (2/5) avec l'hypothèse voisine
   « gaps thématiquement liés au risque de saut » — si le ratio
   Parkinson/close-to-close est fortement corrélé au gap brut du #216
   (les deux capturent en partie la même information de fond), un échec
   similaire est plausible.
2. Le ratio de deux estimateurs bruités individuellement (chacun sur une
   fenêtre de 20j) pourrait être un signal doublement bruité, plus
   instable que chacune de ses composantes prise séparément.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts :
`scripts/nonml_parkinson_c2c_ratio_vol_targeting_overlay_backtest.py`
(nouveau) et
`scripts/nonml_parkinson_c2c_ratio_vol_targeting_overlay_audit.py`.
Vérification via `nonml_anti_cheat_check.py
parkinson_c2c_ratio_vol_targeting_overlay`.

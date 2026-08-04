# Pré-enregistrement — Volatilité du gap d'ouverture (composante overnight isolée), overlay défensif

**Committé AVANT tout calcul.** Cycle #197 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

`data_loader.parkinson_var_pct` (déjà implémenté, utilisé au #50) ne
capture QUE la variance INTRA-séance (haut/bas) — son propre docstring
documente explicitement qu'il ignore l'écart d'ouverture (overnight
gap). La variance close-to-close totale peut donc se décomposer
approximativement en deux composantes additives : `Var_close-close ≈
Var_intraday(Parkinson) + Var_overnight(gap)`. La composante overnight
(nuit + pré-ouverture) capture un risque distinct — nouvelles, résultats
d'entreprises, mouvements des marchés étrangers pendant la fermeture —
qu'aucune gestion intra-séance ne peut couvrir, documenté en
microstructure de marché comme une source de risque structurellement
différente du risque intra-séance. Distinct du #1 (décomposition du
RENDEMENT overnight vs intraday, PAS de la variance — teste si l'un des
deux segments a un rendement moyen exploitable, FAIL) et du #50 (vol
Parkinson comme estimateur ALTERNATIF de la vol TOTALE pour le
vol-targeting, pas comme composante isolée et soustraite). Ici le signal
est la composante de VARIANCE isolée par soustraction, jamais construite
dans ce backlog.

## 2. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 3. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `CCVar_pct(t) = r_pct(t)^2` où `r_pct` = rendement log quotidien
  close-to-close en % (`data_loader.log_returns_pct`, déjà utilisé
  partout dans ce backlog) — variance quotidienne brute, %².
- `ParkVar_pct(t)` = `data_loader.parkinson_var_pct` (déjà implémenté,
  identique au #50, Règle 7), %².
- Lissage : moyenne glissante **VOL_WINDOW=20j réutilisée à l'identique**
  de la famille vol-targeting (#9/#31/#46/#50/#58…) sur les deux
  séries : `CCVar_roll(t)`, `ParkVar_roll(t)`.
- `GapVar_roll(t) = max(CCVar_roll(t) − ParkVar_roll(t), 0)` (plancher à
  0 : la soustraction de deux moyennes glissantes bruitées peut
  ponctuellement devenir négative par construction statistique, sans que
  cela ait de sens économique — plancher déclaré à l'avance, pas une
  correction post-hoc).
- `GapVol_ann(t) = sqrt(GapVar_roll(t)) × sqrt(252) / 100` (conversion
  identique au #50 : %²→fraction annualisée). `GapVol_lag(t) =
  GapVol_ann(t−1)` (même convention `vol_lagged` que #46/#50/#58).
- Seuil : **tercile EXPANDING** de `GapVol_lag(t)` (technique établie,
  #169/#177/#183/#191/#192/#193/#195/#196).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `GapVol_lag(t)` est dans son tercile expanding le PLUS HAUT (risque
  overnight élevé), `1,0x` sinon. **Jamais de levier** — design purement
  défensif, cohérent avec la pratique établie de cette famille de
  signaux. Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#196)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, une fenêtre
réutilisée, un critère multi-marché figé, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La décomposition `Var_close-close ≈ Var_intraday + Var_overnight`
   est une approximation (suppose une covariance nulle entre les deux
   segments) — un biais résiduel n'invaliderait pas nécessairement le
   signal mais pourrait le rendre plus bruité que prévu.
2. Comme pour la famille de signaux de vol/régime déjà testée (#9/#31,
   #178, #191), un régime de volatilité — même isolé à sa composante
   overnight — pourrait ne pas coïncider fiablement avec les phases de
   marché pertinentes pour la décision de position.
3. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196, un design
   purement défensif sans levier compensatoire limite structurellement
   le rendement total.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

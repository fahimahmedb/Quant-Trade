# Pré-enregistrement — Portefeuille « volatility-managed » (Moreira & Muir 2017) piloté par la volatilité PRÉVUE GJR-GARCH-t

**Committé AVANT tout calcul, avant l'écriture du script de backtest.**
Cycle #165 du backlog non-ML (numéro provisoire : un autre agent travaille en
parallèle sur le même fichier `NONML_STRATEGY_BACKLOG.md` ; si le #165 est pris
au moment de l'écriture de l'entrée, ce cycle sera renuméroté et le fait
documenté — le contenu pré-enregistré ci-dessous, lui, ne change pas).
Sous la **Règle 9** (batterie renforcée si PASS) et la **Règle 10**
(hypothèse explicite de rémunération de la fraction hors-marché) de
`PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Pourquoi cette hypothèse est structurellement NOUVELLE dans ce backlog

Les ~164 cycles non-ML déjà exécutés testent presque tous un signal de
**timing ou de sélection** construit à partir du passé observé (prix,
calendrier, tendance, breadth, volatilité **réalisée** glissante). Le seul
résultat statistiquement solide de tout le projet vient d'ailleurs :
l'**Étape C** (`results/etape_C_ndx_40ans.md`) a établi que le
**GJR-GARCH(1,1) à erreurs Student-t** prévoit la variance future
significativement mieux que le benchmark GARCH(1,1)-normal, et que cette
supériorité **survit au test SPA de Hansen sur famille entière** sur
l'historique long NDX : `t_SPA = 6.07, p = 0.0000` à h=1 (meilleur modèle
GJR-t) et `p = 0.0034` à h=5. C'est un edge de **prévision** authentique,
déjà validé, jamais utilisé jusqu'ici pour autre chose que de la réduction
de risque passive.

**Différence avec tout ce qui a déjà été testé** :

| Famille déjà testée | Signal de volatilité utilisé | Nature |
|---|---|---|
| #43 / #46 / #44 / #115 / #50, famille vol-targeting hiérarchique gatée #78→#149 | écart-type glissant 20j (ou Parkinson 20j) des rendements passés | **rétrospectif** — un lissage du passé, toujours en retard sur le régime |
| #118 / Étape D (`run_etape_d_v2.py`) | vol **prévue** GJR-t walk-forward | prévision, mais utilisée en mode **purement défensif** (cap ≤ 1.0-1.5x + coupe au 95e percentile), objectif = réduction de MDD, jamais un objectif de RENDEMENT |
| **CE CYCLE** | vol **prévue** GJR-t walk-forward | prévision, utilisée comme dans **Moreira & Muir (2017, Journal of Finance)** : exposition inversement proportionnelle à la variance prévue, **avec** possibilité d'être au-dessus de 1.0x en régime calme, et jugée sur le critère de **rendement** renforcé du backlog |

Mécanisme économique testé (Moreira & Muir) : (a) la volatilité prévue capte
le clustering de vol **avant** qu'il ne se matérialise, contrairement à un
proxy réalisé toujours réactif ; (b) le ratio rendement/risque n'est pas
constant dans le temps — les régimes de haute volatilité ont un ratio
structurellement moins bon, donc réduire l'exposition quand la vol prévue est
élevée (et l'augmenter quand elle est basse) doit améliorer le Sharpe
hors-échantillon. M&M documentent ce résultat sur plusieurs classes d'actifs.

**Hypothèse unique testée ici** : appliqué au NDX avec le moteur de vol déjà
validé du projet, ce mécanisme bat Buy & Hold **à la fois** en Sharpe et en
rendement total net de coûts.

## 2. Marché et échantillon (figés)

- **NDX uniquement** : `data/nasdaq100_daily.txt` (NASDAQ-100, 01/10/1985 →
  13/07/2026, 10273 séances → 10272 rendements log quotidiens).
  Choix cohérent et non arbitraire : c'est **exactement** l'échantillon sur
  lequel le GJR-t a passé le SPA à l'Étape C. Tester le mécanisme sur un
  marché où le moteur de prévision n'a pas été validé mélangerait deux
  questions.
- **Un seul marché, un seul modèle, une seule paramétrisation** : pas de
  balayage cross-marché dans ce cycle. Si le résultat est intéressant, la
  généralisation (S&P 500, Russell 2000, DAX) sera **proposée comme piste
  suivante** dans le backlog, pas exécutée ici (discipline « un cycle à la
  fois » déjà en place).
- Rendements : `log_returns_pct` (log close-to-close, en %), convention
  Étape C ; le backtest travaille sur les rendements log en fraction
  (`r/100`), convention `prediction.backtest`.

## 3. Modèle de volatilité (figé, un seul — aucun essai caché)

- **GJR-GARCH(1,1) à erreurs Student-t** (`ARCH_SPECS["GJR-t"]` de
  `finance/src/volatility.py`), moyenne constante.
- **Motivation du choix AVANT tout calcul** : à l'Étape C sur NDX, GJR-t est
  le **meilleur modèle à l'horizon 1 jour** désigné par le test SPA
  (`best_model = GJR-t`, `t_SPA = 6.07`, `p = 0.0000`,
  `results/etape_C_ndx_40ans.md`), et la conclusion opérationnelle déjà
  committée du projet est : *« GJR-GARCH(1,1)-t est adopté comme moteur de
  volatilité v1 »*. Le GJR-skewt n'est **PAS** testé ici : tester les deux et
  garder le meilleur serait un essai caché (Règle 2).
- **Prévision à 1 pas** uniquement (horizon de rebalancement quotidien), pas
  de multi-pas — cohérent avec l'horizon où le SPA est le plus net.

## 4. Protocole walk-forward (repris de `run_etape_c.py` / `src/overlay.py`, jamais réimplémenté)

Réutilisation directe de `finance/src/overlay.py::walk_forward_vol_forecast`,
qui encapsule déjà la logique validée de l'Étape C (Règle 7 : ne jamais
réimplémenter une logique déjà validée) :

- Fenêtre initiale **T0 = 750** observations (~3 ans), **expansive**.
- **Ré-estimation tous les REFIT_EVERY = 21 jours** — valeur explicitement
  recommandée dans `CLAUDE.md` pour les historiques longs et déjà utilisée
  par `run_etape_d_v2.py` (~453 ré-estimations sur NDX). Aucun balayage.
- Entre deux ré-estimations, la variance est propagée par
  `garch_path_fold_only(r, p, tr, gjr=True)` : les paramètres estimés sur
  `r[:tr]` ne sont appliqués que **vers l'avant** à partir de `tr`, ce qui
  interdit toute recalculation rétroactive du passé (correctif anti-lookahead
  déjà documenté dans le code, `BUGFIX 2026-07-14`).
- `vol_prévue(t)` = `sqrt(252) * sqrt(sigma2[t])` en % annualisé, où
  `sigma2[t]` est la variance conditionnelle du rendement `r[t]`
  **conditionnée à l'information disponible en t-1**. La position appliquée
  au rendement `r[t]` est donc décidée avec l'information de t-1 : **aucune
  fuite calendaire**, vérifiée explicitement par l'audit.
- Les champs `vol_target` et `vol_thresh` retournés par cette fonction
  (cible = vol réalisée in-sample, seuil de coupe extrême de l'Étape D) sont
  **ignorés** : ce cycle utilise une cible constante fixée a priori (§5) et
  **aucune coupe extrême** — c'est la définition de Moreira & Muir, pas
  l'overlay défensif du #118.
- **Période d'évaluation OOS** : `t ∈ [750, 10272)` — soit ~9522 séances,
  exactement la fenêtre OOS de l'Étape C sur NDX. Buy & Hold est évalué sur
  la **même** fenêtre (aucune comparaison sur des périodes différentes).

## 5. Définition de la stratégie (figée, aucun paramètre libre)

```
position(t) = clip( TARGET_VOL / vol_prévue_GJR-t(t) , 0.0 , CAP )
```

- **TARGET_VOL = 20 %** (volatilité annualisée cible).
  *Raisonnement, fixé avant tout calcul* : le #43 avait pré-enregistré 15 %
  et a **FAIL sur le rendement** avec un diagnostic mécaniste clair
  (exposition moyenne < 1x, la stratégie était sous-investie en permanence) ;
  le #46 a pré-enregistré 20 % et refermé cet écart (exposition moyenne
  1,10x-1,51x, PASS 4/5). 20 % est donc la calibration que **le backlog a
  déjà établi comme adaptée à ce mécanisme**, indépendamment de ce cycle —
  ce n'est ni une valeur choisie après avoir vu un résultat, ni une copie
  aveugle : c'est le seul niveau de cible pour lequel une justification
  documentée antérieure existe. Une cible inférieure rendrait le test
  structurellement incapable de battre Buy & Hold en rendement, ce qui
  viderait l'hypothèse de son sens.
- **CAP = 2.0x** — plafond de levier explicite, jamais « illimité »
  (instruction utilisateur du 28/07/2026 sur le levier autorisé), valeur
  utilisée par tous les cycles vol-targeting du backlog (#43, #46, #47, #54,
  #57, #68…). Pas de plancher autre que 0.
- **Aucune coupe extrême, aucune porte (gating), aucun filtre de tendance** :
  le mécanisme est testé nu, tel que décrit par Moreira & Muir. Toute
  combinaison serait un cycle distinct.
- **Rebalancement quotidien**, coût **5 bps** par unité de turnover
  `|Δposition|` (convention du projet, `prediction.backtest`).
- Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 6. Règle 10 — rémunération de la fraction hors-marché (déclarée explicitement)

La position descend sous 1.0x dès que la vol prévue dépasse 20 %, donc une
fraction `(1 - position)` du capital est hors-marché une partie du temps.
**Hypothèse retenue : 0 % (cash non rémunéré)**, et symétriquement **0 % de
coût de financement** sur la fraction empruntée quand la position dépasse
1.0x.

*Justification explicite (exigée par la Règle 10a)* : (a) c'est exactement la
convention de tous les cycles auxquels ce résultat doit être comparé (#43,
#46, #44, #115, #118 et toute la famille vol-targeting) — changer
l'hypothèse de rémunération en même temps que le signal rendrait la
comparaison ininterprétable ; (b) elle est **conservatrice pour l'hypothèse
testée** : ne créditer aucun portage garantit qu'un éventuel PASS ne peut
PAS être un artefact de la correction identifiée au #142 (où 86-89 % du gain
du #134 venait du portage, pas du mécanisme) ; (c) l'asymétrie (ni portage
sur le cash, ni coût sur le levier) est déclarée ici et sera rappelée dans le
rapport — elle n'est pas neutre et ne doit pas être présentée comme telle.

**Engagement pré-enregistré** : si le résultat est PASS **ou** proche du
seuil, la décomposition portage/effet-prix (méthode du #142, proxy
`data/dgs3mo_daily.csv`) sera exécutée et publiée **avant** toute
communication du résultat comme un edge authentique.

## 7. Critère de succès (RENFORCÉ, chiffré, figé)

Sur la fenêtre OOS commune (t ≥ 750) du NDX, net de coûts à 5 bps :

> **PASS si et seulement si** `Sharpe(volatility-managed) > Sharpe(Buy&Hold)`
> **ET** `rendement total(volatility-managed) > rendement total(Buy&Hold)`.

Les deux jambes sont obligatoires (règle renforcée du 28/07/2026). Un Sharpe
supérieur avec un rendement inférieur = **FAIL**, comme le #43. Le MDD est
rapporté systématiquement mais **n'entre pas** dans le critère (ce cycle teste
un gain de RENDEMENT, pas une réduction de drawdown — celle-ci est déjà
couverte par les #115/#118).

**n_trials = 1** pour cette hypothèse : un marché, un modèle, une
paramétrisation, un critère, aucune grille.

## 8. Ce qui sera fait SI PASS (et seulement si)

1. `scripts/nonml_pass_validation_battery.py volatility_managed_portfolio_gjr`
   — les 5 contrôles a-e de la Règle 9. Le backtest sauvegardera
   `results/nonml_volatility_managed_portfolio_gjr_pnl.npz`
   (`pos`, `r_asset`, `dates`, `cost_bps`) au format attendu.
2. **Grille de robustesse** (perturbation ±20 %, **PAS un retuning** — le
   verdict reste celui du point pré-enregistré 20 %/2.0x quoi qu'il arrive) :
   `TARGET_VOL ∈ {16 %, 20 %, 24 %}` × `CAP ∈ {1.6x, 2.0x, 2.4x}`.
3. Décomposition Règle 10 (§6).
4. Simulation 300 € sur la fenêtre illustrative usuelle du backlog.

Si FAIL : le résultat est rapporté tel quel, aucune variante n'est testée
dans ce cycle sur la même hypothèse (une idée différente devra faire l'objet
d'un cycle séparé, pré-enregistré à part).

## 9. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

Honnêteté préalable — trois raisons plausibles de FAIL, écrites avant de voir
le résultat :

1. **Le drag du levier** : sur 40 ans le NDX a connu -83 % (2000-2002) ; une
   exposition > 1x en régime calme peut amplifier des pertes composées et
   coûter plus que ce que la réduction en régime agité fait gagner (mécanisme
   déjà observé aux #10, #32, #56).
2. **Le coût de turnover** : une position continue rebalancée quotidiennement
   sur 9522 séances paie beaucoup plus de turnover que les overlays binaires
   du backlog (mode d'échec catastrophique déjà vu au #69).
3. **Un meilleur prédicteur de variance n'est pas un meilleur prédicteur de
   ratio rendement/risque** : l'Étape C prouve que le GJR-t prévoit mieux la
   VARIANCE ; le résultat de M&M suppose en plus que le rendement espéré ne
   monte pas proportionnellement avec la variance prévue. Rien dans ce projet
   ne l'a établi sur le NDX — c'est précisément ce que ce cycle teste.

## 10. Anti-cheat

Ce fichier est committé **avant**
`scripts/nonml_volatility_managed_portfolio_gjr_backtest.py` et avant tout
résultat. Vérification automatique :
`python3 scripts/nonml_anti_cheat_check.py volatility_managed_portfolio_gjr`
(chronologie git PREREG → résultat, absence de grille de paramètres, absence
de dépendance ML). Audit indépendant :
`scripts/nonml_volatility_managed_portfolio_gjr_audit.py` — recalcul de la
prévision de volatilité par une voie **indépendante** (API `forecast()` de la
librairie `arch`, pas la récursion maison), vérification explicite de
l'alignement calendaire (la prévision utilisée pour `r[t]` ne doit dépendre
que de `r[:t]`) et test anti-lookahead par mutation du futur.

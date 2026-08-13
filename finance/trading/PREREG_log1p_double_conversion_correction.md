# Pré-enregistrement — correction d'un défaut que j'ai moi-même introduit au #392

**Écrit et committé AVANT toute ré-exécution de stratégie.** `n_trials = 1`.
Cycle de **correction**, pas de découverte : aucun paramètre de stratégie n'est
choisi ici, on rétablit ce que le pré-enregistrement d'origine spécifiait.

## Ce que j'ai cassé, et comment je l'ai trouvé

En préparant le portage point-in-time de
`smallcap_proxy_outperformance_breadth_overlay`, la lecture du script a montré
deux anomalies. `git log -L` sur les lignes concernées les attribue toutes deux
au commit `da92778` — **ma propre correction d'agrégation de panier du #392**.

Ce commit appliquait deux transformations à 34 scripts :

1. `R = np.log(P / P.shift(1))` → `R = (P / P.shift(1) - 1.0)` ;
2. `trading_metrics(pnl)` → `trading_metrics(np.log1p(pnl))`.

Les deux sont **justes pour un panier de titres** : le P&L y vaut
`Σ wᵢ·r_simple,ᵢ`, donc en unités simples, et `trading_metrics` attend du log.
Elles sont **fausses dès que le P&L reste en unités logarithmiques**.

Le script `smallcap_proxy_outperformance_breadth_overlay` n'est pas un panier :
son P&L est celui de l'indice NDX-100, construit en log
(`np.log(close[1:] / close[:-1])`). Les deux transformations lui ont donc été
appliquées à tort :

- **Défaut A — double conversion.** `trading_metrics(np.log1p(pnl))` reconvertit
  une série déjà logarithmique. Le rendement total, lui, utilise
  `exp(Σ pnl) − 1` : les deux métriques du même rapport ne sont plus dans la même
  convention.
- **Défaut B — contamination du signal.** La transformation (1) a été appliquée à
  `log_ret`, qui n'alimente **pas** le P&L mais la **volatilité idiosyncratique**
  servant à séparer le groupe « petite capitalisation » proxy. Le signal a donc
  changé. Le message du #392 annonçait pourtant exclure explicitement les scripts
  « où `R` sert AUSSI à construire le signal » — l'exclusion a manqué ce cas.

**C'est le même travers que celui décrit au #390 et au #395** : une correction
appliquée par motif de fichier plutôt que par lecture. Je l'avais écrit ; je l'ai
refait.

## Portée — mesurée avant correction, par un balayage exhaustif

`scripts/nonml_log1p_double_conversion_audit.py`, écrit et exécuté avant toute
correction, balaie **tous** les scripts `nonml_*.py` du dépôt et non la seule
liste des 34 fichiers du commit — restreindre le balayage à la liste attendue
est exactement ce qui m'a fait manquer un foyer au #390.

Résultat du balayage :

- **Défaut A : 1 script atteint** — `nonml_smallcap_proxy_outperformance_breadth_overlay_backtest.py`.
- **Défaut B : 1 script atteint** — le même. Sept `*_pass_validation_battery.py`
  sont signalés par l'heuristique de nom (`build_raw_series` contient
  « series ») ; lecture faite, leur signal est calculé depuis `close` et jamais
  depuis `R` : ce sont des faux positifs, documentés comme tels.

La portée réelle est donc **un seul script**. Je la consigne telle quelle, sans
la minimiser — un seul script, mais un PASS de niveau 1 dont les chiffres
publiés sont faux.

## Correction appliquée

Rétablissement de ce que le PREREG d'origine spécifiait, **rien d'autre** :

| | Avant (#392, fautif) | Après (rétabli) |
|---|---|---|
| `log_ret` du signal | `(P / P.shift(1) - 1.0)` | `np.log(P / P.shift(1))` |
| métriques | `trading_metrics(np.log1p(pnl))` | `trading_metrics(pnl)` |

Aucun paramètre de stratégie n'est touché : ni `IDIO_VOL_WINDOW` (60), ni
`MOM_WINDOW` (21), ni `MEDIAN_WINDOW` (252), ni `CAP` (2,0), ni
`TARGET_VOL_ANNUAL` (0,20), ni `COST_BPS` (5,0).

## Critère — et l'engagement qui compte ici

Le critère reste celui du PREREG d'origine : l'overlay doit battre Buy & Hold
**en Sharpe annualisé ET en rendement total**, net de coûts.

**Engagement explicite : le verdict corrigé est publié tel quel, y compris s'il
fait tomber le PASS.** Le résultat actuellement affiché (Sharpe +0,56 → +0,58,
rendement +132,4 % → +154,8 %, PASS niveau 1) est issu du code fautif ; il n'a
aucune autorité. Je ne le prends pas comme référence à retrouver.

Une seule exécution. Aucune ré-exécution après lecture, aucun ajustement.

## Engagements

1. Résultat corrigé rapporté **tel quel**, PASS ou FAIL.
2. Le balayage de portée est re-exécuté après correction ; il doit rendre zéro
   résidu, et ce chiffre est publié quel qu'il soit.
3. Les artefacts dérivés du script fautif (robustesse, simulation 300 €, audit,
   batterie Règle 9) sont ré-exécutés ou explicitement marqués caducs — pas
   laissés en place en silence.
4. L'ancien résultat n'est pas effacé : le fichier corrigé indique qu'il remplace
   des chiffres faux, et pourquoi.

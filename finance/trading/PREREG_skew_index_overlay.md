# Pré-enregistrement — Indice CBOE SKEW (risque de queue), overlay défensif

**Committé AVANT tout calcul.** Cycle #341 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

L'indice CBOE SKEW mesure le prix relatif des options S&P 500
profondément hors-la-monnaie (put) par rapport aux options
à-la-monnaie, converti en une jauge de probabilité implicite d'un
mouvement extrême ("krach", écart de plusieurs écarts-types) sur les
30 prochains jours. Documenté par le CBOE lui-même et la littérature
sur le risque de queue (ex. Bali & Murray 2013, "Does Risk-Neutral
Skewness Predict the Cross-Section of Equity Option Portfolio
Returns?") comme une jauge DISTINCTE du niveau de volatilité globale :
le marché peut anticiper une volatilité globale modérée (VIX bas) tout
en pricant une AMPLITUDE de queue élevée (SKEW haut) — les deux
mesures ont historiquement divergé (ex. SKEW élevé en périodes de
calme apparent avant certains chocs).

**Distinct des 3 constructions dérivées du VIX déjà closes dans ce
backlog** (0 PASS/3) : niveau VIX seul (#130, FAIL — Sharpe
+0,51→+0,50), prime de risque de variance VIX-vol réalisée (#191, FAIL
2/5 — écart implicite-vs-réalisé), structure par terme VXV-VIX (#340,
FAIL 1/5 — écart court-terme-vs-long-terme). Aucune des trois ne
capture l'ASYMÉTRIE de la distribution implicite (skew) — ici le signal
est de nature qualitativement différente (moment d'ordre 3 implicite,
pas un niveau ou un écart de volatilité globale/moment d'ordre 2).

Design PUREMENT DÉFENSIF (jamais de levier), cohérent avec le reste de
la famille macro-externe/marché de ce backlog.

## 2. Données

**Nouvelle donnée à récupérer** : indice CBOE SKEW, source officielle
gratuite `https://cdn.cboe.com/api/global/us_indices/daily_prices/SKEW_History.csv`
(quotidien depuis le 02/01/1990, disponibilité déjà vérifiée par fetch
de test, HTTP 200, 9199 valeurs jusqu'au 05/08/2026). Aucune dépendance
au VIX local pour ce signal (contrairement au #191/#340) — SKEW est
utilisé seul.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que pour le VIX et ses dérivés (#130/#191/#340) : jauge
de risque dérivée des options S&P 500, mais utilisée comme signal de
peur GLOBAL appliqué au-delà du seul marché d'origine, cohérent avec
la pratique déjà établie de ce backlog.

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal `ffill+shift(1)` identique aux #130/#191/#340 pour
  la série (Règle 7, aucun nouveau paramètre).
- Seuil : **tercile EXPANDING** de `SKEW_lag(t)` (technique établie aux
  #169/#177/#183/#191/#340, `expanding_tercile_cut_high` réutilisée à
  l'identique du #291 NFCI, Règle 7).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `SKEW_lag(t)` est dans son tercile expanding le PLUS HAUT (risque de
  krach implicite le plus élevé), `1,0x` sinon. **Jamais de levier**.
  Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : mécanisme qualitativement distinct des 3
signaux VIX déjà FAIL (asymétrie plutôt que niveau/écart de vol), mais
appartenant à la même famille large de signaux dérivés d'options sur
indice, dont AUCUNE construction n'a encore atteint le seuil renforcé.
Résultat rapporté tel quel, PASS ou FAIL, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le SKEW est historiquement un signal très BRUYANT jour-à-jour (le
   CBOE lui-même documente une forte variance de court terme sans
   rapport systématique avec un régime de risque réalisé) — risque
   similaire à celui identifié à l'avance pour l'EPU (#327, FAIL 0/5,
   pire score de la famille macro-externe).
2. Comme le reste de la famille VIX (#130/#191/#340), un design
   purement défensif sans levier compensatoire limite structurellement
   le rendement total.
3. Le SKEW a historiquement une moyenne élevée et volatile (souvent
   >100, sans niveau "neutre" stable dans le temps) — un seuil
   EXPANDING pourrait mettre du temps à s'ancrer correctement sur le
   début de l'historique, limite reconnue à l'avance.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_skew_index_overlay_backtest.py`,
`scripts/nonml_skew_index_overlay_audit.py`,
`results/nonml_skew_index_overlay_{result,audit,anti_cheat}.md`.

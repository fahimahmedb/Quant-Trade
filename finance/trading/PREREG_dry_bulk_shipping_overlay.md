# Pré-enregistrement — Momentum du fret maritime en vrac sec (BDRY, proxy Baltic Dry), overlay défensif

**Committé AVANT tout calcul.** Cycle #356 du backlog non-ML.

## 1. Contexte et motivation

L'indice Baltic Dry (coût du fret maritime en vrac sec — minerai de
fer, charbon, céréales) a été explicitement recherché et déclaré
**indisponible gratuitement** à deux reprises dans ce backlog (#295,
#347) — série propriétaire non répliquée sur FRED. La découverte de
Yahoo Finance (#348) débloque un proxy : l'ETF `BDRY` (Breakwave Dry
Bulk Shipping ETF), qui réplique des contrats à terme de fret sec,
disponible depuis 2018.

**Hypothèse** : le coût du fret maritime reflète directement la
demande physique de transport de matières premières industrielles —
documenté en analyse macro comme un indicateur avancé de l'activité
commerciale mondiale (Baltic Dry Index cité comme baromètre du
commerce international depuis les années 1980). **Mécanisme distinct
des matières premières déjà testées** (pétrole #283, cuivre #284, gaz
naturel #326, or #348 — toutes des PRIX de biens physiques) : ici le
signal est le COÛT DE TRANSPORT (utilisation de la capacité de flotte
vs demande de fret), pas le prix d'une matière première consommée.

## 2. Données

**Nouvelle donnée** : ETF `BDRY` via l'API publique Yahoo Finance
(même mécanisme de fetch que #348/#352/#353/#354), gratuite,
quotidienne depuis le 22/03/2018, disponibilité déjà vérifiée par
fetch de test (HTTP 200, 2104 valeurs jusqu'au 06/08/2026).
**Historique le plus court de tous les candidats testés dans ce
backlog** (~8 ans, comparable au Bitcoin ~11 ans et à l'Ethereum
~10 ans) — limite reconnue à l'avance, pas un obstacle rédhibitoire
au vu du précédent Bitcoin (#344, PASS malgré un historique court).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe/matières
premières (baromètre de commerce mondial, appliqué uniformément).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `BDRYmom(t) = log(BDRY(t)/BDRY(t-21))` (**RET_WINDOW=21 réutilisé à
  l'identique** des #198/.../#354, Règle 7).
- Alignement causal `ffill+shift(1)` (Règle 7 standard).
- `position(t) = 0,5x` si `BDRYmom_lag(t)` est dans son tercile
  expanding le **PLUS BAS** (chute marquée du fret = faiblesse de la
  demande de transport de matières premières = ralentissement du
  commerce mondial = défavorable, **même direction "chute=défensif"**
  que le pétrole/cuivre/gaz déjà testés, cohérent avec un mécanisme
  "matière première/commerce" plutôt que "valeur refuge"), `1,0x`
  sinon. **Jamais de levier**. Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une fenêtre réutilisée, une direction
déclarée à l'avance par cohérence économique, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : mécanisme documenté et distinct des
matières premières déjà testées, mais la famille "commerce/croissance
industrielle" (pétrole, cuivre, gaz) est à 0/3 dans ce backlog — un
signal purement défensif sans levier compensatoire y a
systématiquement échoué à généraliser le rendement. Résultat rapporté
tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme le reste de la famille macro-externe, un design purement
   défensif sans levier compensatoire limite structurellement le
   rendement total.
2. Historique le plus court de ce backlog (~8 ans, 2018+) — puissance
   statistique réduite, risque de sur-influence d'un petit nombre
   d'épisodes (2018-2019 correction commerciale, 2020 COVID, 2021-2022
   flambée post-COVID de la logistique mondiale, régime atypique).
3. Le marché du fret sec est structurellement très volatil et cyclique
   (offre de flotte rigide à court terme, contrats à terme avec roll
   de contrats) — bruit potentiellement élevé par rapport au signal
   économique réel, similaire au risque déjà identifié pour l'EPU
   (#327, pire score de la famille macro-externe).
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_dry_bulk_shipping_overlay_backtest.py`,
`scripts/nonml_dry_bulk_shipping_overlay_audit.py`,
`results/nonml_dry_bulk_shipping_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.

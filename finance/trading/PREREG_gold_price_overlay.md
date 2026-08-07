# Pré-enregistrement — Momentum de l'or (GLD, valeur refuge), overlay défensif

**Committé AVANT tout calcul.** Cycle #348 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

L'or est documenté depuis des décennies en finance de marché comme
l'actif "valeur refuge" par excellence — une HAUSSE marquée de son
prix signale typiquement un mouvement de flight-to-quality (aversion
au risque, anticipation d'inflation/dévaluation monétaire, incertitude
géopolitique), par opposition aux matières premières industrielles
déjà testées dans ce backlog (pétrole #283 FAIL 2/5, cuivre #284 FAIL
3/5, gaz naturel #326 FAIL 1/5), dont la BAISSE signale une faiblesse
de la demande industrielle/de croissance. **La direction économique
est donc structurellement OPPOSÉE** à celle des 3 commodités déjà
testées — l'or est un baromètre d'AVERSION au risque, pas de
croissance, et c'est là sa distinction économique fondamentale dans
ce backlog.

**Nouveauté de source de données** : l'or n'a jamais pu être testé
dans ce backlog malgré 2 tentatives explicites (#134, #343) — la série
FRED historique (`GOLDAMGBD228NLBM`/`GOLDPMGBD228NLBM`) est
discontinuée (HTTP 404, confirmé à nouveau ce cycle). Ce cycle
**découvre une source alternative gratuite et fonctionnelle** :
Yahoo Finance (déjà utilisée par un script préexistant hors backlog,
`fetch_and_quantify_putwrite.py`, confirmée fonctionnelle par un fetch
de test réussi ce jour) fournit l'historique quotidien complet de
l'ETF `GLD` (SPDR Gold Shares, réplique physique de l'once d'or,
methodology publique) depuis son lancement en 2004 — **premier usage
d'une source de données autre que FRED/CBOE dans ce backlog
discipliné par PREREG**.

## 2. Données

**Nouvelle donnée à récupérer** : ETF `GLD` via l'API publique Yahoo
Finance (`query2.finance.yahoo.com/v8/finance/chart/GLD`), gratuite,
quotidienne depuis le 14/08/2006 (lancement du fonds), disponibilité
déjà vérifiée par fetch de test réussi (5026 observations quotidiennes
`1d`, jusqu'au 06/08/2026). **Limite reconnue à l'avance** : l'ETF
réplique le prix spot avec de légers frais de gestion (~0,40%/an) et
un tracking error historiquement minime — traité comme un proxy
acceptable du prix de l'or physique, cohérent avec l'usage déjà établi
d'un ETF/indice officiel comme proxy dans ce backlog (ex. put-write
CBOE hors-backlog, VIX lui-même un indice calculé). Historique 2006+
plus court que le maximum du backlog (NDX 40 ans, 1985+) — troncature
attendue et déjà documentée pour de nombreux autres candidats (VXVCLS
2007+, SKEW 1990+, etc.).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe/matières
premières (l'or est un baromètre de risque global, pas seulement une
matière premières industrielle américaine).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `GoldMom(t) = log(GLD(t)/GLD(t-21))` (**RET_WINDOW=21 réutilisé à
  l'identique** des #198/#283/#284/#326/#344/#346, Règle 7). GLD
  aligné sur le calendrier de chaque marché actions par `ffill`.
- Alignement causal `shift(1)` supplémentaire (Règle 7 standard).
- Seuil : **tercile EXPANDING** de `GoldMom_lag(t)`.
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `GoldMom_lag(t)` est dans son tercile expanding le **PLUS HAUT**
  (hausse marquée de l'or sur 21j, signal de flight-to-quality —
  **direction OPPOSÉE aux #283/#284/#326** qui coupent sur la baisse,
  déclarée ici avant tout calcul par cohérence avec le statut de
  valeur refuge de l'or, cf. §1), `1,0x` sinon. **Jamais de levier**.
  Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une fenêtre réutilisée, une direction
déclarée à l'avance par cohérence économique, un critère multi-marché
figé, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : le mécanisme "valeur refuge" est
solidement documenté, mais les 3 commodités déjà testées dans ce
backlog ont toutes FAIL malgré des mécanismes économiques plausibles
similaires (2/3 proches du seuil : cuivre 3/5, pétrole 2/5). Résultat
rapporté tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme la famille matières premières déjà testée (0/3), un design
   purement défensif sans levier compensatoire limite structurellement
   le rendement total.
2. L'or peut monter pour des raisons NON liées au risque actions
   (dévaluation monétaire pure, achats de banques centrales,
   spéculation propre au marché de l'or) — un signal de hausse pourrait
   ne pas coïncider avec un vrai régime de risque actions, ajoutant du
   bruit sans configurer une fuite.
3. Historique GLD plus court (2006+) que la plupart des séries déjà
   testées — puissance statistique réduite sur NDX en particulier.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_gold_price_overlay_backtest.py`,
`scripts/nonml_gold_price_overlay_audit.py`,
`results/nonml_gold_price_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.

# Pré-enregistrement — Force relative marchés émergents vs développés (EEM/SPY), overlay défensif

**Committé AVANT tout calcul.** Cycle #354 du backlog non-ML.

## 1. Contexte, hypothèse et déclaration de bornage explicite (Règle 2, transparence)

La performance RELATIVE des marchés émergents (EEM, iShares MSCI
Emerging Markets) par rapport aux marchés développés US (SPY,
S&P 500) est un baromètre d'appétit au risque global largement suivi
en gestion macro : en régime de risk-off, les capitaux quittent
typiquement en premier les actifs émergents (plus volatils, moins
liquides, plus sensibles au dollar/aux taux US) pour se replier vers
les grandes capitalisations américaines — une SOUS-PERFORMANCE
marquée des émergents précède ou accompagne souvent un stress de
marché plus large.

**Distinct de la rotation sectorielle du #353** (XLP/XLK, rotation
intra-marché défensif/croissance au sein des actions US) : ici la
mesure est une rotation INTER-marchés/INTER-classes de risque
(émergents à bêta élevé vs développés US), mécanisme économique
différent (flux de capitaux internationaux, sensibilité au dollar/taux
US, pas une rotation sectorielle domestique). **Également distinct de
la sous-famille corrélation cross-marché explicitement close au #196**
(qui mesurait une CORRÉLATION glissante entre deux séries de
rendements, pas un ratio de force relative/momentum).

**Engagement de bornage pris à l'avance** : ce cycle et le #353
constituent ensemble la sous-méthode "ratio de force relative entre
deux actifs, momentum du ratio" appliquée via Yahoo Finance. **Après
ce cycle, cette sous-méthode est bornée à 2 constructions** (rotation
sectorielle #353, EM/DM #354) — aucune 3e paire (ex. small-cap/large-
cap, autres régions) ne sera testée sans nouvelle hypothèse économique
clairement distincte, pour éviter une recherche combinatoire non
bornée sur des paires d'actifs (même discipline que les bornages
déjà appliqués : corrélation cross-marché #196, inflation #343,
crypto #346, monétaire #347, valeur-refuge #348-352).

## 2. Données

**Nouvelle donnée** : ETF `EEM` (iShares MSCI Emerging Markets) via
l'API publique Yahoo Finance (même mécanisme de fetch que #348/#352/
#353), gratuite, quotidienne depuis le 14/04/2003, disponibilité déjà
vérifiée par fetch de test (HTTP 200, 5865 valeurs jusqu'au
06/08/2026). Combinée à `data/xlp_sector_daily.csv`... non, à une
nouvelle récupération de `SPY` (S&P 500 ETF, même source), servant de
proxy développé US.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe/rotation
(jauge de risque global, appliquée uniformément).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `Ratio(t) = EEM(t) / SPY(t)` (force relative émergents/développés).
- `RatioMom(t) = log(Ratio(t)/Ratio(t-21))` (**RET_WINDOW=21 réutilisé
  à l'identique** des #198/.../#353, Règle 7).
- Alignement causal `ffill+shift(1)` (Règle 7 standard).
- `position(t) = 0,5x` si `RatioMom_lag(t)` est dans son tercile
  expanding le **PLUS BAS** (sous-performance marquée des émergents
  sur 21j = appétit au risque en baisse = risk-off, direction
  déclarée ici par cohérence économique — analogue à la direction
  "chute = défensif" déjà utilisée pour le Bitcoin/#344, le cuivre/#284,
  la croissance M2/#203), `1,0x` sinon. **Jamais de levier**. Coûts
  5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une fenêtre réutilisée, une direction
déclarée à l'avance par cohérence économique, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : mécanisme documenté et distinct des
signaux déjà testés, mais appartient à la même famille large de
signaux de "risque global" purement défensifs (matières premières,
valeur-refuge, rotation sectorielle) dont AUCUN n'a encore atteint le
seuil renforcé (0 PASS sur 6 constructions récentes : or, TLT,
pétrole, cuivre, gaz, rotation sectorielle). Résultat rapporté tel
quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme le reste de la famille macro-externe/valeur-refuge/rotation,
   un design purement défensif sans levier compensatoire limite
   structurellement le rendement total.
2. Les marchés émergents ont connu des cycles structurels longs de
   sous-performance (2011-2020 notamment) indépendants d'épisodes de
   stress ponctuels — le tercile expanding pourrait capter une
   tendance séculaire plutôt qu'un signal de régime réactif, limite
   reconnue à l'avance (distincte d'un bug).
3. DAX (marché européen) pourrait avoir une sensibilité différente au
   canal EM/DM que les marchés US, limite reconnue à l'avance.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_em_dm_relative_strength_overlay_backtest.py`,
`scripts/nonml_em_dm_relative_strength_overlay_audit.py`,
`results/nonml_em_dm_relative_strength_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.

# Pré-enregistrement — Rotation sectorielle défensive (biens de consommation de base vs technologie), overlay défensif

**Committé AVANT tout calcul.** Cycle #353 du backlog non-ML.

## 1. Contexte et motivation

Dernière piste ouverte de la découverte Yahoo Finance (#348) : la
rotation sectorielle défensive, catégorie **jamais testée dans ce
backlog** (distincte de toutes les familles déjà explorées : macro
FRED, options sur indice, matières premières/valeur-refuge, crypto,
crédit, activité réelle, marché du travail, inflation, monétaire).
**SLV (argent métal) a été explicitement écarté** pour ce cycle — même
mécanisme "valeur refuge" que l'or (#348, FAIL) et l'obligataire
(#352, FAIL NET, pire score), redondance de mécanisme trop forte sans
nouvelle hypothèse économique à ce stade (2 échecs consécutifs sur ce
mécanisme précis).

**Hypothèse** : la force RELATIVE des biens de consommation de base
(secteur défensif, demande inélastique, XLP) par rapport à la
technologie (secteur offensif/de croissance, le plus fortement
représenté au NDX-100, XLK) est un baromètre de régime documenté en
analyse sectorielle de marché — une SURPERFORMANCE de XLP sur XLK
signale typiquement une rotation défensive intra-marché (les
investisseurs quittent les valeurs cycliques/de croissance pour les
valeurs défensives), distincte des signaux déjà testés car elle mesure
un mouvement RELATIF entre deux secteurs du marché actions lui-même,
pas un actif externe (macro, matière première, crypto) ni une
corrélation cross-marché (sous-famille déjà close au #196).

## 2. Données

**Nouvelle donnée** : ETF `XLK` (Technology Select Sector SPDR) et
`XLP` (Consumer Staples Select Sector SPDR) via l'API publique Yahoo
Finance (même mécanisme de fetch que #348/#352, confirmé
fonctionnel), gratuits, quotidiens depuis le 22/12/1998, disponibilité
déjà vérifiée par fetch de test (HTTP 200, 6946 valeurs chacun jusqu'au
06/08/2026 — historique le plus long de tous les candidats Yahoo
Finance testés à ce jour).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe/valeur-refuge
(jauge de régime de marché US, appliquée uniformément, cohérent avec
la pratique déjà établie pour VIX/dollar/or/obligataire).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `Ratio(t) = XLP(t) / XLK(t)` (force relative défensif/offensif).
- `RatioMom(t) = log(Ratio(t)/Ratio(t-21))` (**RET_WINDOW=21 réutilisé
  à l'identique** des #198/#283/#284/#326/#344/#346/#348/#352, Règle 7).
- Alignement causal `ffill+shift(1)` (Règle 7 standard).
- `position(t) = 0,5x` si `RatioMom_lag(t)` est dans son tercile
  expanding le **PLUS HAUT** (XLP surperforme XLK de façon marquée sur
  21j = rotation défensive active, **même direction "hausse=défensif"
  que dollar/or/obligataire déjà testés**, déclarée ici par cohérence
  économique), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps
  (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une fenêtre réutilisée, une direction
déclarée à l'avance par cohérence économique, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : premier signal de rotation sectorielle
de ce backlog, mécanisme documenté mais jamais testé ici. La famille
valeur-refuge/matières premières récemment testée est à 0/5 (or, TLT,
pétrole, cuivre, gaz) — un signal purement défensif sans levier
compensatoire y a systématiquement échoué à généraliser le rendement,
risque qui s'applique également ici. Résultat rapporté tel quel, sans
retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme le reste de la famille macro-externe/valeur-refuge défensive,
   un design purement défensif sans levier compensatoire limite
   structurellement le rendement total.
2. XLK est fortement corrélé au NDX-100 lui-même (composition
   sectorielle proche) — le ratio pourrait donc être en partie un
   signal auto-référentiel dérivé du marché testé lui-même plutôt
   qu'un signal génuinement externe, limite reconnue à l'avance
   (distincte d'une fuite temporelle, mais un biais conceptuel
   possible sur NDX spécifiquement).
3. La composition sectorielle du S&P 500 (dont XLK/XLP sont des
   sous-secteurs officiels) diffère structurellement du DAX (marché
   européen, pondération sectorielle différente) — le signal pourrait
   ne pas généraliser à ce marché, limite reconnue à l'avance.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_sector_rotation_staples_tech_overlay_backtest.py`,
`scripts/nonml_sector_rotation_staples_tech_overlay_audit.py`,
`results/nonml_sector_rotation_staples_tech_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.

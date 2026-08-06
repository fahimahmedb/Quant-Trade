# Pré-enregistrement — Choc de prix du pétrole WTI (overlay défensif)

**Committé AVANT tout calcul.** Cycle #283 du backlog non-ML.

## Hypothèse

Le prix du pétrole (WTI, FRED `DCOILWTICO`, quotidien) est le canal
macro le plus fréquemment cité comme facteur de risque actions dans la
littérature (chocs pétroliers de 1973, 1979, 1990, 2008, 2022) — un
choc inflationniste/coût-poussé : une hausse RAPIDE du pétrole pèse sur
les marges des entreprises, alimente l'inflation et les anticipations
de resserrement monétaire. Mécanisme économiquement DISTINCT du cuivre
(#284, proxy de DEMANDE industrielle, testé en glissement annuel
mensuel) : ici la variable est la VITESSE de la hausse sur un horizon
court (1 mois), pas le niveau, et le canal est le COÛT plutôt que la
demande. Premier signal de matière première à fréquence QUOTIDIENNE
(le #284 cuivre était mensuel).

## Données

Série FRED `DCOILWTICO` récupérée le jour même (`data/wti_oil_daily.csv`,
quotidienne, 1986-2026, 10215 observations non-NaN après nettoyage des
jours fériés marqués `.`/NaN par FRED, gratuite).

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7)

- `OilChange(t) = log(WTI(t) / WTI(t-21))` (fenêtre 21j = 1 mois,
  réutilisée du #170/#192/#198).
- Alignement causal : `ffill` + `shift(1)` sur le calendrier boursier
  (même fonction que #191/#192/#193/#195/#196/#197/#198, pas de
  décalage mensuel supplémentaire car série quotidienne, pas de délai
  de publication comme les séries mensuelles agrégées).
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `OilChange(t-1)` est dans son tercile expanding le PLUS
  HAUT (hausse la plus rapide du pétrole observée jusqu'à présent —
  choc inflationniste, direction cohérente avec #198 dollar fort =
  défensif), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_oil_price_shock_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode prouvée correcte au #203,
re-confirmée au #283/#284), anti-lookahead par troncature. Sortie :
`results/nonml_oil_price_shock_overlay_result.md`.

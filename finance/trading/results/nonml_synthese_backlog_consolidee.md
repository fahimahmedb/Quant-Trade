# Synthèse consolidée — backlog non-ML (131 cycles, 30/07/2026)

Document récapitulatif (cycle #132). Ne recalcule rien : compile des
résultats déjà committés dans `NONML_STRATEGY_BACKLOG.md` et
`results/nonml_*.md`, pour donner une vue d'ensemble avant de continuer
à empiler des variantes.

## 1. Chiffres globaux

- **131 hypothèses testées**, **61 PASS niveau 1** (critère brut :
  Sharpe ET rendement net de coûts > Buy&Hold, ou Calmar > Buy&Hold
  selon le cycle).
- **0 PASS RENFORCÉ** (Règle 9 complète : coûts 5x, crise 4 fenêtres
  historiques, stabilité temporelle 4 folds, SPA, DSR) sur les **10
  candidats** évalués sous cette batterie depuis son introduction
  (#111 à #131).
- **1 seul SPA significatif isolé** obtenu sur le backlog (#114 pente
  des taux/NDX, p=0,0035 puis #126 S&P 500 p=0,021) — mais dans les
  deux cas le candidat échoue ensuite le stress de crise ou la
  robustesse, donc reclassé FAIL.

## 2. Ce qui a été testé (carte des marchés, signaux, mécanismes)

**Marchés** : NASDAQ Composite (5 ans, échantillon figé), NDX (40 ans,
1985+), S&P 500, Russell 2000, DAX — 5 marchés indépendants utilisés
pour les tests de robustesse cross-marché (Règle 3).

**Familles de signaux testées** :
- Calendaires (jour de semaine, tournant de mois, Halloween/Sell-in-May,
  rallye de Noël, jours fériés, window dressing) — plusieurs PASS
  niveau 1 en overlay, aucun soumis à la Règle 9 (antérieurs à son
  introduction).
- Momentum/tendance (52 semaines, court terme titre, SMA200,
  Donchian) — le signal 52w-high indice est le plus robuste de cette
  famille (#37/#38/#47), le momentum court terme titre est PASS mais
  sous forte prudence (concentration IA/semi 2021-2026, #14).
- Volatilité auto-référentielle (réalisée #115, GJR-GARCH #118, EWMA
  #124, Parkinson #50) comme ESTIMATEUR pilotant un vol-targeting
  hiérarchique — famille la plus solide en niveau 1, plafonne à 3/5
  sous la Règle 9.
- Volatilité/stress EXTERNE (VIX #130) — rupture volontaire avec
  l'auto-référence, FAIL net (Sharpe légèrement inférieur malgré
  rendement supérieur).
- Macro (pente de la courbe des taux T10Y2Y, #114/#126/#128) — PASS +
  SPA significatif sur NDX uniquement, ne généralise PAS au S&P 500 ni
  au Russell 2000 (#127 : succès NDX partiellement fortuit, la porte
  était éteinte pendant le dot-com par hasard de calendrier).
- Breadth/dispersion titre-par-titre (confirmation multi-marché #52/#57,
  petites capitalisations #123, drawdown profond #111, spread de
  décile momentum #112) — pattern déjà noté : les gates de
  NIVEAU/DISPERSION passent plus souvent le niveau 1 que les gates de
  VITESSE/DYNAMIQUE (rebond post-choc #13/#22, accélération #16/#92/
  #93/#95/#102/#107/#108/#120, presque tous FAIL).
- Combinaisons d'ensembles : signaux CORRÉLÉS de même famille (#113,
  vote titre-par-titre) n'améliorent pas SPA/DSR ; moteurs de
  volatilité INDÉPENDANTS (#121 réalisé+GARCH, #124 +EWMA) améliorent
  l'edge brut et la robustesse mais pas SPA/DSR, avec rendements
  décroissants au-delà de 2 moteurs.
- Fréquence de rebalancement (#131, hebdomadaire au lieu de quotidien)
  — réduit le turnover de 48% et améliore légèrement chaque métrique,
  meilleur résultat brut du backlog, mais ne déplace pas le plafond
  SPA/DSR.

## 3. Le plafond structurel identifié (#116)

Le contrôle DSR (Règle 9e) utilise `n_trials` = taille totale du
backlog (110 à 125 selon le cycle, jamais 1, pour éviter le biais de
sélection du meilleur résultat après coup). Le Sharpe ANNUALISÉ requis
pour DSR>0,95 à ce niveau de n_trials est de **1,58 à 2,03** selon la
taille d'échantillon du candidat — un niveau **supérieur à tous les
repères académiques standards** (prime de risque actions 0,40-0,50,
facteurs Fama-French 0,30-0,50, CTA systématique 0,50-0,80), et
comparable seulement aux fonds quantitatifs multi-stratégies
d'exception (fréquence et diversification sans rapport avec un signal
quotidien unique sur un seul indice).

Deux lectures possibles (non tranchées, posées explicitement à
l'utilisateur au cycle #116, toujours en attente) :
1. La barre est correctement calibrée et ce type de mécanisme
   (overlay directionnel/défensif quotidien, non-ML, sur un seul
   indice) n'a simplement pas l'edge nécessaire pour survivre à une
   correction honnête du nombre d'essais.
2. `n_trials` compté ligne par ligne du backlog surestime le nombre
   d'essais réellement INDÉPENDANTS (beaucoup de variations mineures
   du même mécanisme vol-targeting) — une correction par FAMILLE
   réduirait la sévérité, mais nécessite une justification et
   l'accord explicite de l'utilisateur, jamais une décision
   unilatérale prise pour obtenir un résultat plus favorable.

## 4. Les candidats les plus proches d'un PASS Règle 9 complet

Quatre candidats atteignent EXACTEMENT le même plafond — 3/5 contrôles
OK (coûts, crise, stabilité), 2/5 en échec (SPA, DSR) — malgré des
constructions très différentes :

| Candidat | Mécanisme | Sharpe ann. | MDD | SPA (p) | DSR |
|---|---|---|---|---|---|
| #115 | Vol-targeting réalisé 20j (critère Calmar) | +0,71 | -57 à -60% | 1,00 | ≈0 |
| #121 | Moyenne réalisé + GJR-GARCH (2 moteurs indépendants) | +0,69 | -57,2% | 0,45 | 0,0001 |
| #124 | Moyenne réalisé + GARCH + EWMA (3 moteurs) | ≈+0,69 | -57% | 1,00 | 0,0001 |
| #131 | #121 rebalancé HEBDOMADAIRE (turnover -48%) | **+0,72** | **-55,3%** | **0,30** | 0,0003 |

**#131 est le meilleur des quatre sur presque tous les axes** (Sharpe,
MDD, SPA le plus proche de la significativité, turnover). L'ordre de
progression (#115→#121→#131) montre que combiner des moteurs
indépendants PUIS réduire le turnover améliore continûment le SPA
(1,00→0,45→0,30) sans jamais l'approcher du seuil 0,05 — cohérent avec
un edge réel mais structurellement trop faible plutôt qu'un artefact
corrigible par l'ingénierie du mécanisme.

## 5. Recommandation honnête

Le backlog a exploré, sur 131 cycles, à peu près tous les leviers
"non-ML" disponibles avec les données déjà en local ou facilement
récupérables (calendrier, momentum, volatilité sous 3 estimateurs
indépendants, macro, breadth, ensembles, fréquence de rebalancement,
cross-marché sur 5 indices). Le résultat qualitatif est stable depuis
le cycle #115 (dix cycles et quatre reconstructions différentes plus
tard) : **un plafond net à 3/5 sous la Règle 9**, jamais franchi.

Deux voies restent réalistes pour la suite, sans re-tester des
variantes de plus en plus proches des precedentes :
1. Trancher la question ouverte du §3 (n_trials par famille) avec
   l'utilisateur — c'est le seul levier qui pourrait mécaniquement
   faire passer un candidat déjà construit (#131) sans aucun nouveau
   calcul.
2. Accepter la conclusion actuelle (cohérente avec l'Étape B : aucun
   signal directionnel/défensif quotidien non-ML ne bat Buy&Hold à un
   niveau de preuve statistique strict) et réorienter l'effort vers
   autre chose que l'empilement de variantes du même type de
   mécanisme (ex. reprendre l'angle ML abandonné, ou formaliser
   l'usage du #131 comme outil de RISK MANAGEMENT — réduction
   documentée et robuste du MDD — plutôt que comme stratégie visant à
   battre le benchmark en Sharpe pur, cohérence avec la conclusion déjà
   établie de l'Étape C).

Ce document ne tranche pas entre les deux — décision de l'utilisateur.

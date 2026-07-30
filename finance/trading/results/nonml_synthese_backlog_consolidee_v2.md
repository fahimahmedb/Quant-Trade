# Synthèse consolidée v2 — backlog non-ML (144 cycles, 30/07/2026)

Met à jour `nonml_synthese_backlog_consolidee.md` (#132, 131 cycles)
avec les 13 cycles supplémentaires (#132-144). Ne recalcule rien : lit
les résultats déjà committés.

## 1. Chiffres globaux

- **144 hypothèses testées**, **68 PASS niveau 1**.
- **0 PASS RENFORCÉ** (Règle 9 complète) sur **17 candidats** évalués
  sous cette batterie.
- Score Règle 9 record : **4/5** (#134, seul candidat à ce niveau —
  coûts, crise, ET stabilité temporelle sur les 4/4 folds, un cap
  jamais atteint auparavant).

## 2. Le développement majeur depuis le #132 : la famille diversification obligataire

Le §4 du #132 recommandait explicitement une "rupture structurelle
avec la famille vol-targeting" — diversifier vers un actif
GENUINEMENT différent plutôt que de continuer à lever/dé-lever le même
indice. Le #134 a testé exactement cela : allouer la fraction
"dé-risquée" du mécanisme #115 à un proxy obligataire (Trésor US 10
ans, DGS10) au lieu du cash à 0%.

**Résultat : le meilleur candidat de tout le backlog.** Sharpe
+0,53→+0,77, MDD -82,9%→-50,9%, plateau de robustesse parfait, **4/5
sous la Règle 9** (record). Onze cycles supplémentaires (#135-144) ont
exploré cette famille en profondeur :

| Cycle | Question posée | Résultat |
|---|---|---|
| #135 | Le #134 réduit-il le risque de queue (VaR/ES), pas seulement le Sharpe ? | OUI, ES99 réduit de +27% à +67% selon la fenêtre |
| #136 | Le mécanisme se généralise-t-il à d'autres marchés ? | OUI : S&P 500 (4/5, comme NDX) et Russell 2000 (3/5) |
| #137 | Empiler avec le rebalancement hebdomadaire (#131) améliore-t-il encore ? | PARTIEL : meilleur MDD (-46,5%) et meilleur SPA (p=0,25) mais retombe à 3/5 |
| #138 | Le #134 tient-il sur un verrou temporel pur (12 derniers mois) ? | NON (comme le #115 au #122) — cohérent avec un profil de couverture |
| #139 | Le fold-1 en échec du #137 vient-il du #131 spécifiquement ? | NON, réfuté — tout ensemble de moteurs de vol (#121/#124/#131) échoue ce fold ; le #134 (base simple) est seul à 4/4 |
| #140 | Le mécanisme se généralise-t-il à un marché non-US (DAX) ? | PASS mais score le plus faible (1/5) — limité par un taux allemand disponible seulement en fréquence MENSUELLE |
| #141 | Le mécanisme tient-il avec un proxy quasi-cash (3 mois) ? | OUI, résultat presque identique au proxy 10 ans — signal fort que le gain n'est pas dû à l'effet-prix des obligations longues |
| #142 | D'où vient vraiment le gain (portage vs effet-prix) ? | **Le portage seul explique 86-89% du gain** — reframe majeur, voir §3 |
| #143 | Le mécanisme tient-il sur l'échantillon Composite (5 ans, référence du projet) ? | PASS marginal (Calmar seul), score le plus faible (1/5) — limité par la brièveté de l'échantillon |
| #144 | Le #134 peut-il être formalisé en script Étape D officiel ? | OUI, `run_etape_d_v3_bond_diversification.py` — critère de succès Étape D (MDD -25%/rendement ≥80%) ATTEINT sur NDX |

## 3. Reframe épistémique majeur (#142) — à retenir avant toute communication de ce résultat

Le #141 avait déjà donné un indice frappant : un proxy 3 mois (quasi
sans risque de taux) obtenait presque le même gain que le proxy 10 ans.
Le #142 a quantifié précisément pourquoi : **le simple PORTAGE (taux
d'intérêt positif perçu sur la fraction dé-risquée, au lieu de 0% en
cash) explique 89% du gain de Sharpe et 86% de la réduction de MDD**
du #134. L'effet "flight to quality" (appréciation du prix obligataire
pendant les chocs de volatilité), qui motivait l'hypothèse initiale du
#134, n'apporte qu'une contribution marginale (11-14%).

**Implication honnête** : le mécanisme #115 (base du #134) supposait
implicitement un taux sans risque de 0% pendant tout l'historique
(40 ans sur NDX) pour la fraction non investie — une hypothèse
irréaliste sur une période où les taux courts US ont historiquement
été positifs la plupart du temps. Le "gain de diversification" du
#134 (et de toute sa famille #136-144) est donc surtout une
**correction d'un biais de backtest** (percevoir un taux réaliste au
lieu de 0%), pas principalement la découverte d'un edge de couverture
actions/obligations authentique.

Cela **ne remet PAS en cause la validité empirique** des résultats
Règle 9 déjà rendus (mesurés honnêtement contre le vrai Buy&Hold, qui
lui aussi ne perçoit aucun taux sur du cash puisqu'il est 100%
investi) — mais cela change la NARRATION appropriée pour tout rapport
futur : présenter le #134 comme "corriger une hypothèse de backtest
irréaliste" est plus honnête que "découvrir une stratégie de
diversification".

## 4. Candidats au plafond Règle 9 (mis à jour)

| Candidat | Mécanisme | Score Règle 9 | Remarque |
|---|---|---|---|
| **#134** | Vol-targeting défensif (#115) + diversification obligataire DGS10 | **4/5** (record) | Stabilité 4/4 folds (seul candidat) |
| #137 | #134 empilé sur le rebalancement hebdomadaire (#131) | 3/5 | Meilleur MDD (-46,5%) et meilleur SPA (p=0,25) |
| #139 | #134 empilé sur l'ensemble à 3 moteurs (#124) | 3/5 | Confirme que le fold-1 est une propriété des ensembles, pas du #131 |
| #121/#124/#131/#115 (pré-#134) | Vol-targeting seul ou en ensemble, sans diversification | 3/5 | Plafond historique avant le #134 |
| #136 (S&P 500) | #134 généralisé | 4/5 | Confirme le #134 sur un 2e marché |
| #136 (Russell 2000), #140 (DAX), #143 (Composite) | #134 généralisé | 1-3/5 | Limités par la qualité/longueur des données, pas par le mécanisme |

## 5. Recommandation (mise à jour, tient compte du reframe #142)

Le §5 du #132 posait deux voies : trancher la question n_trials-par-
famille (tranchée empiriquement au #133 : même n_trials=8 ne suffit
pas), ou réorienter vers le risk management (fait au #135, VaR/ES
documenté). Le développement de la famille diversification (#134-144)
a été le plus productif de tout le backlog — mais son reframe #142
suggère une leçon méthodologique plus large :

**Toute stratégie qui alloue du capital "hors-marché" (cash) ailleurs
dans ce backlog (overlays calendaires #2/#8/#17/#21, filtres de
tendance #29/#37/#47, vol-targeting défensif générique) a probablement
sous-estimé son propre gain potentiel de la même façon**, en supposant
implicitement 0% sur cette fraction. Cette observation, proposée comme
piste #146, pourrait être le levier le plus direct restant pour
rapprocher un candidat existant d'un PASS Règle 9 complet — plus
prometteur que continuer à empiler des variantes de la seule famille
vol-targeting/obligataire, déjà explorée de façon exhaustive (11
cycles, tous les axes testés : marchés, maturités, empilements,
décomposition).

# Pré-enregistrement — Indice de stress financier St. Louis Fed STLFSI4 (overlay défensif)

**Committé AVANT tout calcul.** Cycle #291 du backlog non-ML.

## Hypothèse et nature du test

Le St. Louis Fed Financial Stress Index (FRED `STLFSI4`, hebdomadaire)
est, comme le NFCI (#291 backlog, PASS 4/5), un indice composite de
stress des marchés financiers construit à partir de dizaines
d'indicateurs (spreads, volatilité, taux). **Ce cycle est un test
CONFIRMATOIRE, pas une nouvelle catégorie** : il vérifie si le schéma
émergent "stress des marchés financiers généralise, activité
économique réelle non" (#199 spread crédit, #286 défaut carte de
crédit, #291 NFCI — tous PASS ou proches — vs #204 ICSA, #205 UMCSENT,
#206 CFNAI — tous FAIL) tient depuis une **source et une méthodologie
distinctes** (Fed de St. Louis, pas Fed de Chicago) — même esprit que
la lignée d'estimateurs de volatilité range-based déjà établie dans ce
backlog (Parkinson #50, Garman-Klass #215, Rogers-Satchell #221, tous
testés séparément malgré leur parenté conceptuelle).

**Prédiction déclarée à l'avance** : ce signal devrait PASSER comme le
NFCI (#291), pas échouer comme les signaux d'activité réelle.

## Données

Série FRED `STLFSI4` récupérée le jour même (`data/stlfsi_weekly.csv`,
HEBDOMADAIRE, 1993-2026, 1701 observations, gratuite — historique plus
court que le NFCI, 1993 contre 1971, signalé honnêtement).

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7
STRICTE de la construction du #291 — seule la série change)

- **Construction** : NIVEAU brut du STLFSI4 (même convention que le
  NFCI #291 — indice déjà standardisé, pas de croissance/variation).
- **Décalage de publication** : même délai conservateur de 7 jours
  calendaires que le NFCI (#291) et l'ICSA (#204).
- Alignement causal final : `ffill` + `shift(1)` sur le calendrier
  boursier.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `STLFSI4_lag(t-1)` est dans son tercile expanding le PLUS
  HAUT (conditions financières les plus tendues observées jusqu'à
  présent), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_stlfsi_financial_stress_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode prouvée correcte au
#203/#283-#291), vérification dédiée du décalage de 7 jours, anti-
lookahead par troncature. Sortie :
`results/nonml_stlfsi_financial_stress_overlay_result.md`.

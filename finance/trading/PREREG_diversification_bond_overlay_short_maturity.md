# Pré-enregistrement — Diversification obligataire (#134) avec proxys courts (3 mois / 1 an)

**Committé AVANT tout calcul.** Cycle #141 du backlog non-ML. **Extension
de robustesse du #134 (PAS un nouveau candidat indépendant à sa propre
Règle 9)** — la grille de maturité déjà committée du #134 (5-20 ans, sur
la MÊME série DGS10) n'a testé que des durations LONGUES. Ce cycle
utilise de VRAIES séries de taux courts (pas juste un paramètre de
duration appliqué à DGS10) pour tester la sensibilité jusqu'à
l'extrême court terme.

## Hypothèse

Le proxy obligataire du #134 utilise DGS10 (Trésor 10 ans). Un
instrument plus court (3 mois, quasi-cash) a une duration modifiée bien
plus faible → un effet-prix quasi nul, le rendement se réduisant
essentiellement au portage (`y/252`). Hypothèse a priori : plus la
maturité utilisée est courte, plus le rendement obligataire converge
vers un simple taux sans risque (proche de 0% de variance), ce qui
DEVRAIT réduire la protection en crise (moins de "flight to quality"
capturé, car les bons du Trésor courts montent moins en prix pendant un
choc actions que les obligations longues) mais aussi réduire le risque
de taux. Direction non triviale, testée sans a priori sur le résultat
final.

## Données (nouvelles, récupérées le 30/07/2026)

- `data/dgs3mo_daily.csv` — FRED `DGS3MO` (Treasury 3 mois),
  1981-09-01→2026-07-28, 11716 lignes.
- `data/dgs1_daily.csv` — FRED `DGS1` (Treasury 1 an),
  1962-01-02→2026-07-28, 16846 lignes.

## Définition (fixée ici, avant tout résultat)

- Position équity : IDENTIQUE au #134 (`nonml_defensive_calmar_
  vol_targeting_overlay_pnl.npz`, #115, strictement inchangée).
- Rendement obligataire : MÊME formule de duration modifiée fermée que
  le #134, mais appliquée à `DGS3MO` avec `maturity_years=0.25` et à
  `DGS1` avec `maturity_years=1.0` (paramètres cohérents avec
  l'instrument réel, pas choisis après coup).
- `r_combiné(t) = pos_eq(t)*r_NDX(t) + (1-pos_eq(t))*r_bond_court(t)`.
- Coûts : 5 bps par unité de turnover (identique).
- **Référence** : Buy & Hold 100% NDX, ET le #134 lui-même (DGS10, déjà
  committé) comme second point de comparaison.

## Ce que ce cycle NE fait PAS

N'est PAS un nouveau candidat indépendant soumis à sa propre batterie
Règle 9 complète — c'est une extension de la grille de robustesse déjà
prévue pour le #134 (maturité de référence), avec de vraies données
courtes au lieu d'un simple paramètre appliqué à DGS10. Les résultats
sont rapportés honnêtement (Sharpe/rendement/MDD/Calmar vs BH et vs
#134), qu'ils soient favorables ou non, sans déclencher une nouvelle
notification Telegram même si le critère PASS/FAIL standard serait
atteint (déjà couvert par le verdict Règle 9 du #134 lui-même).

## Anti-cheat

Ce fichier committé avant
`nonml_diversification_bond_overlay_short_maturity.py`, données committées
en même temps.

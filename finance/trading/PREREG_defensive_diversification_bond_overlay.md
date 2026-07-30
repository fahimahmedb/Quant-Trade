# Pré-enregistrement — Diversification défensive vers un proxy obligataire (au lieu de cash)

**Committé AVANT tout calcul.** Cycle #134 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Toute la famille vol-targeting déjà testée (#115/#118/#121/#124/#131)
pilote l'exposition au MÊME actif (NDX) — la fraction "dé-risquée"
pendant les régimes de vol élevée est implicitement placée en cash
(rendement 0%). Rupture structurelle (recommandée explicitement par la
synthèse #132) : au lieu de sizing (lever/dé-lever le même actif),
teste une vraie DIVERSIFICATION — la fraction dé-risquée du mécanisme
défensif déjà validé (#115) est allouée à un proxy obligataire
(rendement des bons du Trésor américain 10 ans) plutôt qu'au cash.
Hypothèse a priori (fixée avant tout calcul) : les obligations d'État
tendent à être décorrélées voire négativement corrélées aux actions
pendant les épisodes de stress ("flight to quality"), donc cette
substitution devrait améliorer le couple rendement/MDD par rapport à
un simple parking en cash à 0%.

## Données (nouvelles, récupérées le 30/07/2026)

- `data/dgs10_daily.csv` — FRED `DGS10` (Treasury Constant Maturity 10Y,
  taux au comptant, PAS un prix), 1962-01-02→2026-07-28, 16846 lignes,
  valeurs manquantes marquées `.` (jours fériés).
- **Proxy de rendement obligataire** (pas de série de prix total-return
  10 ans gratuite et à longue histoire trouvée librement) : approximation
  standard par la duration modifiée d'une obligation "au pair" de
  maturité 10 ans, calculée directement à partir du taux lui-même
  (AUCUN paramètre libre ajouté) :
  - Duration de Macaulay d'une obligation au pair : `D_mac = (1+y)/y *
    (1 - 1/(1+y)^10)` (formule fermée standard, y = DGS10(t-1)/100).
  - Duration modifiée : `D_mod = D_mac / (1+y)`.
  - Rendement quotidien approché : `r_bond(t) ≈ y(t-1)/252 - D_mod(t-1)
    * (y(t) - y(t-1))/100` (portage + effet prix de la variation de
    taux, ignore la convexité).
  - **Limite reconnue explicitement** : approximation classique en
    l'absence d'indice total-return gratuit à longue histoire, PAS le
    rendement réel d'un fonds/ETF obligataire (ignore les coûts de
    roulement, la convexité, les changements de composition de
    l'indice sous-jacent). Rapportée comme telle, pas comme un
    substitut parfait.

## Définition du mécanisme (fixée ici, avant tout résultat)

- Position équity `pos_eq(t)` = position DÉJÀ COMMITTÉE du #115
  (`results/nonml_defensive_calmar_vol_targeting_overlay_pnl.npz`,
  jamais >1.0x, jamais retunée).
- Position obligataire complémentaire : `pos_bond(t) = 1 - pos_eq(t)`.
- Rendement combiné : `r_combiné(t) = pos_eq(t)*r_NDX(t) +
  pos_bond(t)*r_bond(t)`.
- Coûts : 5 bps par unité de turnover de `pos_eq` (turnover obligataire
  non facturé séparément — même turnover sous-jacent que #115, pas de
  double-comptage).
- Fenêtre : intersection des dates #115 (NDX 1985-2026) et DGS10
  (1962-2026) → fenêtre limitée par le #115 (10252 séances).
- **Référence** : Buy & Hold 100% NDX, même fenêtre.

## Critère de succès (pré-enregistré, DEUX volets rapportés séparément, cohérence avec #115)

1. Critère standard : Sharpe ET rendement net de coûts > BH.
2. Critère Calmar (cohérence avec #115) : Calmar > BH.
Les deux sont rapportés, aucun n'est privilégié après coup.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py defensive_diversification_bond_overlay`,
n_trials=taille totale du backlog (jamais 1).

## Robustesse prévue (SI PASS niveau 1)

Grille non-tunable : maturité de l'obligation de référence dans la
formule de duration ∈ {5, 10, 20} ans (au lieu de fixer 10 ans) — teste
la sensibilité au choix de maturité, pas un retuning du mécanisme lui-même
(la position équity `pos_eq(t)` du #115 reste strictement inchangée).

## Anti-cheat

Ce fichier committé avant
`nonml_defensive_diversification_bond_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py defensive_diversification_bond_overlay`.
Fichier de données `data/dgs10_daily.csv` committé en même temps que ce
PREREG.

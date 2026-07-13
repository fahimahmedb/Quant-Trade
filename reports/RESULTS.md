# Résultats v1 — Récolte de la prime de risque de variance NASDAQ-100

**Produit** : moteur probabiliste vol/distribution + stratégie short-variance
conditionnelle sur le NASDAQ-100 (instrument tradeable : swaps de variance /
options QQQ delta-hedgées ; le NASDAQ Composite a été abandonné car
non-tradeable et mal sourcé). Mécanisme d'edge assumé : **prime de risque**
— on est payé pour porter le risque de krach, pas pour prédire le rendement.

Tous les chiffres ci-dessous sont **hors échantillon walk-forward**
(ré-estimation tous les 21 jours, fenêtre expansive, entraînement purgé des
fenêtres chevauchantes), période d'évaluation **2004-01 → 2026-06**.

---

## 1. Données et QC

| Série | Source | Période | QC |
|---|---|---|---|
| NDX OHLC | Yahoo | 1989→2026 | validé vs FRED et QQQ ; FRED bruité 2003-05 (corr QQQ 0,88 vs 0,98 Yahoo) → écarté |
| VXN | CBOE (2009+) + Yahoo (2001-09) | 2001→2026 | écart médian CBOE/Yahoo = 0,00 sur 4 231 jours de chevauchement |
| VIX, QQQ | CBOE / Yahoo | 1990/1999→2026 | covariable / arbitrage de sources |

Anomalies vérifiées réelles : +18 % le 2001-01-03 (baisse surprise Fed),
trou de calendrier sept. 2001 (fermeture post-11/09).

## 2. La prime existe (baseline inconditionnelle, 2001→2026)

- VRP moyenne (VXN² − RV²_fwd 21j) : **+158 pts de variance, t Newey-West = 4,6** ; positive 80 % des jours ; IV/RV ≈ 1,22 (t = 14).
- Short variance systématique : Sharpe ≈ 0,89 (2001-26) mais **0,36 net post-2004** — 2001-03 était exceptionnellement rémunérateur, honnêteté oblige.
- Le prix de la prime : skew −7,8, kurtosis 98. Février 2020 : **−195 pts de vol par vega en une fenêtre, ≈ 7 ans de prime moyenne**. Années rouges : 2008, 2018, 2020, 2022.

## 3. Moteur de volatilité (cible : variance réalisée 21j, jambe flottante du swap)

QLIKE hors échantillon, 5 632 jours, DM avec Newey-West lag 42 :

| Modèle | QLIKE | DM vs GARCH(1,1) | p |
|---|---|---|---|
| RW-RV 21j | 0,391 | +4,97 | 0,000 |
| EWMA λ=0,94 | 0,336 | +3,29 | 0,001 |
| GARCH(1,1) *(benchmark)* | 0,271 | — | — |
| GJR-GARCH-t | 0,290 | +1,33 | 0,182 |
| HAR (Yang-Zhang) | 0,257 | −1,35 | 0,177 |
| **HAR-X (HAR + VXN)** | **0,238** | **−4,04** | **0,000** |
| VXN débiaisé | 0,243 | −2,96 | 0,003 |
| VXN brut | 0,245 | −1,62 | 0,106 |

Verdicts : (i) **HAR-X bat significativement le GARCH(1,1)** — critère
« excellent » de la grille de conception atteint ; (ii) l'essentiel de
l'information est déjà dans le marché d'options (VXN débiaisé seul est 2ᵉ) ;
(iii) **le GJR-GARCH-t ne bat PAS le GARCH(1,1) à 21j** sur cet
échantillon — la recommandation « l'asymétrie n'est pas optionnelle » de la
revue de littérature ne survit pas au test à cet horizon.

## 4. Stratégie (mensuel non chevauchant, 3 tranches, coût 0,5 pt de vol/entrée)

Règle retenue : `prop` — vega w = clip(VXN²/E[RV²]−1, 0, 1), E[RV²] = HAR-X.

| Règle | Expo | Sharpe net | Pire mois | MaxDD | SR 04-14 | SR 15-26 |
|---|---|---|---|---|---|---|
| Short inconditionnel | 1,00 | 0,36 | −187 | −208 | 0,67 | 0,20 |
| **prop (HAR-X)** | 0,29 | **0,58** | **−64** | **−69** | 0,92 | 0,40 |
| prop (GARCH) | 0,30 | 0,56 | −81 | — | 0,85 | 0,46 |
| prop (RW-RV) | 0,49 | 0,47 | −82 | — | 0,85 | 0,32 |
| inverse-IV sans modèle | 0,81 | 0,41 | −187 | — | 0,86 | 0,22 |
| filtre spike RV<IV | 0,80 | 0,38 | −187 | −215 | — | — |

- **Écart de Sharpe prop(HAR-X) vs inconditionnel : +0,40, IC bootstrap stationnaire 90 % [+0,11 ; +0,70], P(diff≤0)=1,4 %.**
- Crises (P&L net/mois) : COVID −0,9 (vs −18,8 inconditionnel), 2008 −1,5 (vs −6,6), 2022 −0,05 (vs −0,3). Le filtre spike ÉCHOUE en COVID (−27) : sortir sur la vol réalisée arrive trop tard.
- Ablation : la règle prime/risque est le moteur principal (même GARCH donne 0,56) ; **la valeur propre du HAR-X est dans la queue** (pire mois −64 vs −81/−187).
- Coûts : breakeven ≈ 2 pts de vol/entrée pour prop ; à 1 pt (options QQQ delta-hedgées, réaliste retail) Sharpe ≈ 0,39.
- **Deflated Sharpe (comptage honnête N=10 essais) : 0,77 ; N=20 : 0,70.** Pas ≥ 0,95 : le Sharpe seul ne franchit pas la barre déflatée sur 22 ans de mensuel. Le dossier repose sur prime (t=4,6) + réduction de queue + bootstrap.

## 5. Moteur de risque (distribution prédictive 21j, 233 fenêtres non chevauchantes)

| Test | v1 (Student sym.) | v2 (skew-t Hansen, λ≈−0,53) |
|---|---|---|
| PIT (KS) | **rejeté** p=0,000 | **calibré** p=0,28 |
| VaR 5 % gauche (Kupiec / Christoffersen) | 0,69 / 0,75 ✓ | 0,92 / 0,64 ✓ |
| VaR 1 % gauche | **rejeté** p=0,003 | 0,13 / 0,08 ✓ (limite) |
| Quantile 95 %/99 % droit | rejetés | 0,84 / 0,32 ✓ |

L'itération v1→v2 illustre le protocole : le PIT a diagnostiqué le skew
manquant (masse excédentaire déciles 8-9, queue gauche sous-estimée), le
skew-t l'a corrigé, les tests sont repassés.

## 6. Limites honnêtes (à ne pas enterrer)

1. **La prime se comprime** : Sharpe ~0,9 (2004-14) → ~0,4 (2015-26) sur
   toutes les variantes. Extrapoler 0,58 vers l'avant est optimiste ;
   0,3-0,45 net est l'attente raisonnable.
2. **VaR 1 % à la limite** (5 violations vs 2,3 attendues, Christoffersen
   p=0,08) : le clustering des violations extrêmes n'est pas exclu.
3. **Implémentabilité** : les swaps de variance ne sont pas accessibles en
   retail ; la réplique delta-hedgée en options QQQ a des coûts ~2× et un
   tracking error non modélisé ici. Les futures VXN n'existent plus.
4. **Une seule histoire** : 269 mois, 4 crises. Le bootstrap n'invente pas
   les crises absentes de l'échantillon.
5. P&L en points de vol par vega, pas en % de capital : le passage à un
   portefeuille exige une politique de collatéral/marge (les appels de marge
   en crise sont le vrai risque de ruine du vendeur de variance).
6. Comptage des essais : 10 configurations testées dans ce projet,
   documentées dans les scripts ; aucune grille d'hyperparamètres balayée.

## 7. Prochaines itérations candidates

- CPCV (Lopez de Prado) en plus du walk-forward ; test SPA de Hansen sur
  l'ensemble des 8 modèles de vol.
- Expected Shortfall + test Acerbi-Székely (la VaR seule ne suffit pas pour
  un book short-vol).
- Réplique réaliste en options QQQ (delta-hedge quotidien, coûts mesurés).
- Terme VIX/VXN (pente du terme) comme covariable du sizing.
- Politique de collatéral et sizing en % de capital (Kelly fractionnaire).

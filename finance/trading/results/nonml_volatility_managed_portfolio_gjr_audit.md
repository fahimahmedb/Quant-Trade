# Audit adversarial — portefeuille volatility-managed GJR-t (cycle #165)

## 1. Réconciliation avec l'artefact déjà committé de l'Étape C

Les prévisions de volatilité de ce cycle doivent être *les mêmes objets* que celles publiées par l'Étape C sur NDX (script différent, committé avant ce cycle) — sinon le moteur validé au SPA de Hansen n'est pas celui qui est réellement utilisé ici.

| Grandeur | Étape C (committé) | Ce cycle | Identique |
|---|---|---|---|
| cadence de ré-estimation (j) | 21 | 21 | OUI |
| nombre de ré-estimations | 454 | 454 | OUI |
| nombre de prévisions OOS 1 pas | 9522 | 9522 | OUI |
| vol prévue min (%) | 8.6 | 8.6 | OUI |
| vol prévue médiane (%) | 19.1 | 19.1 | OUI |
| vol prévue max (%) | 111.2 | 111.2 | OUI |

**OK — le moteur de prévision est bien celui validé au SPA à l Étape C.**

## 2. Recalcul par la boucle de l'Étape C (sans le wrapper `overlay`)

Écart absolu maximal sur les 9522 prévisions OOS : **0.00e+00**

**OK — recalcul identique à la précision machine.**

## 3. Recalcul par la librairie `arch` (implémentation tierce)

`arch_model(...).fix(params).forecast(horizon=1)` sur `r[:t]` — code, initialisation et récursion écrits par les auteurs de la librairie, pas par ce projet.

| t | Vol prévue backtest | Vol prévue `arch` | Écart relatif |
|---|---|---|---|
| 750 | 14.7444 % | 14.7444 % | 0.00e+00 |
| 1950 | 15.1286 % | 15.1286 % | 0.00e+00 |
| 3150 | 25.0353 % | 25.0353 % | 0.00e+00 |
| 4350 | 35.6304 % | 35.6304 % | 0.00e+00 |
| 5550 | 17.0529 % | 17.0529 % | 0.00e+00 |
| 6750 | 21.6063 % | 21.6063 % | 0.00e+00 |
| 7950 | 10.2692 % | 10.2692 % | 0.00e+00 |
| 9150 | 29.3904 % | 29.3904 % | 0.00e+00 |

**OK — implémentation tierce concordante (tolérance 1e-3, même seuil que la validation de l Étape C).**

## 4. Alignement calendaire — la prévision pour r[t] ne lit que r[:t]

Récursion GJR réécrite de zéro en Python pur, alimentée par une tranche **strictement bornée à `r[:t]`** : si le backtest contenait la moindre fuite d'un jour, ce recalcul divergerait.

| t | Date | Position backtest | Position recalculée (r[:t] seulement) | Écart |
|---|---|---|---|---|
| 750 | 20/09/1988 | 1.356445 | 1.356445 | 0.00e+00 |
| 1950 | 18/06/1993 | 1.322001 | 1.322001 | 0.00e+00 |
| 3150 | 19/03/1998 | 0.798872 | 0.798872 | 0.00e+00 |
| 4350 | 26/12/2002 | 0.561319 | 0.561319 | 0.00e+00 |
| 5550 | 03/10/2007 | 1.172820 | 1.172820 | 0.00e+00 |
| 6750 | 09/07/2012 | 0.925656 | 0.925656 | 0.00e+00 |
| 7950 | 17/04/2017 | 1.947576 | 1.947576 | 0.00e+00 |
| 9150 | 20/01/2022 | 0.680494 | 0.680494 | 0.00e+00 |

**OK — aucune donnée postérieure à t-1 n intervient dans la position appliquée à r[t].**

## 5. Test anti-lookahead par mutation des 20 % de rendements les plus récents

Bruit gaussien σ=2 points de % ajouté sur les 2055 derniers rendements (indices ≥ 8217). Écart maximal sur les positions **antérieures** : **0.00e+00**

*Point de vigilance identifié et quantifié, pas passé sous silence* : `garch_path_fold_only` (code de l'Étape C, réutilisé tel quel) initialise la récursion avec la variance de l'échantillon **complet** passé en argument — donc techniquement avec une information postérieure. L'influence de cette initialisation décroît en β^t avec β ≈ 0.8180 (fit sur la fenêtre initiale) : à la première observation OOS (t = 750) elle vaut déjà β^750 ≈ 3.5e-66, très en dessous de la précision machine. La mesure ci-dessus le confirme empiriquement, et le contrôle 4 (récursion initialisée sur `r[:t]` uniquement) le confirme indépendamment.

**OK — le passé est inchangé, aucune information future exploitable.**

## 6. Recalcul manuel du verdict (boucles explicites, sans `trading_metrics`)

| Grandeur | Volatility-managed | Buy & Hold | Candidat > BH |
|---|---|---|---|
| Sharpe annualisé (recalcul manuel) | +0.6656 | +0.5209 | OUI |
| Rendement total composé (recalcul manuel) | +7178.8% | +4553.2% | OUI |

**OK — le verdict PASS de niveau 1 est confirmé par un recalcul totalement indépendant.**

## Synthèse

| Vérification | Statut |
|---|---|
| Réconciliation Étape C | OK |
| Recalcul boucle Étape C | OK |
| Recalcul librairie arch | OK |
| Alignement calendaire | OK |
| Anti-lookahead (mutation) | OK |
| Recalcul manuel du verdict | OK |

**Verdict de l'audit : CONFORME — aucun bug ni fuite détecté sur les 6 contrôles.**

*Limite honnête de cet audit* : il vérifie l'absence de fuite et l'exactitude du calcul, PAS la validité économique du mécanisme. La question « un meilleur prédicteur de variance donne-t-il un meilleur ratio rendement/risque ? » relève des contrôles statistiques de la Règle 9 (SPA, DSR, stabilité), pas d'un audit de code.

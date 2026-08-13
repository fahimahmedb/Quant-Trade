# Audit — Leaders + overlay SMA200, univers point-in-time

Le backtest a confirmé ce que le PREREG annonçait comme possible : sur
2015-2026 le signal SMA200 et l'union SMA200 ∪ 52w-high ne diffèrent jamais.
Ce cycle est une **identité arithmétique** du #401. L'audit le prouve plutôt
que de rejouer des contrôles déjà passés sur les mêmes nombres.

## 1. Identité bit-à-bit du P&L avec le #401

Comparaison des deux `.npz` sauvegardés, série par série, par égalité
**exacte** (`np.array_equal`, pas une tolérance numérique).

| Série | Longueur | Identique au #401 |
|---|---|---|
| `pnl_gross_ov` | 2900 | **OUI** |
| `pnl_gross_bh` | 2900 | **OUI** |
| `turn_ov` | 2900 | **OUI** |
| `turn_bh` | 2900 | **OUI** |
| `dates` | 2900 | **OUI** |
| `cost_bps` | — | **OUI** |

**IDENTITÉ CONFIRMÉE — les deux candidats produisent exactement la même série.**

Conséquence : les contrôles du #401 (simulation en nombre de parts,
anti-lookahead par perturbation des prix, appartenance PIT) portent sur ces
nombres-ci. Les transférer n'est pas un raccourci — c'est la même série. La
réserve du #401 (écart de niveau 6,34 % au contrôle en parts) se transfère
elle aussi, à l'identique, et n'est donc pas passée sous silence ici.

## 2. Inclusion des signaux, mesurée sur toute l'histoire de l'indice

Le backtest mesure la divergence sur la seule fenêtre testable (2900 séances).
Ce contrôle élargit la mesure à **tout** l'historique NDX-100 disponible, pour
vérifier que l'inclusion n'est pas un accident de fenêtre.

- séances d'indice examinées : **10273**
- séances où l'indice est au-dessus de sa SMA200 : **7588**
- séances où le 52w-high est actif **sans** la SMA200 : **0**

**INCLUSION STRICTE SUR TOUTE L'HISTOIRE** — « à ≥ 95 % du plus haut 252 j »
implique toujours « au-dessus de la SMA200 » sur ces données. L'union des deux
est donc identiquement égale à SMA200 seul : les candidats #33 et #41 ne sont
pas deux stratégies mais une seule, écrite deux fois.

## 3. Causalité du décalage des poids

Recalculé ici, pas hérité du #401.

- décalage d'exactement un jour vérifié : **OUI**

**CONFORME**

## 4. Appartenance point-in-time à la date de décision

Recalculé ici, pas hérité du #401.

- dates de rebalancement vérifiées : **139**
- sélections d'un non-membre à la décision : **0**

**CONFORME — aucun titre sélectionné avant son entrée dans l indice.**

## Verdict de l'audit

**CONFORME — et le cycle est établi comme un doublon exact du #401.**

Le verdict FAIL est correct, mais il ne constitue **pas** une observation
indépendante : conformément à la règle de comptage fixée au PREREG avant tout
calcul, ce cycle n'est pas ajouté au décompte des candidats testés de l'axe.

Ce que ce cycle apporte réellement, et qui n'est pas rien : la confirmation
que deux entrées du backlog comptées séparément depuis le #33 et le #41
désignent la même stratégie. Le nombre d'essais indépendants du backlog est
donc surestimé d'au moins une unité — ce qui compte pour les corrections de
multiplicité (DSR, SPA), et va dans le sens **défavorable** aux candidats.

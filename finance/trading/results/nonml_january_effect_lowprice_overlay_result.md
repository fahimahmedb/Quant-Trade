# Résultat — "January effect" (proxy prix bas) en overlay (pré-enregistré, exécuté une fois, règle renforcée)

Univers : 99 tickers NDX-100, 1375 séances testables (2021-02-03 → 2026-07-27), rebalancement tous les 21j, tercile au PRIX DE CLÔTURE le plus faible (proxy taille — vraie capitalisation boursière non disponible, voir limite dans PREREG). Overlay actif 7.3% du temps (mois de janvier).

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Tercile prix bas 1.0x (référence) | +0.88 | +156.4% | -36.3% |
| **+ overlay janvier x2.0** | **+0.91** | **+186.8%** | -42.1% |

1. Sharpe > référence : OUI
2. Rendement total > référence : OUI

**PASS — critère renforcé atteint.**

*(Résultat d'origine ci-dessus, conservé en traçabilité — voir nuance dans la correction ci-dessous.)*

## Correction 01/08/2026 — exécution causale

Voir `results/nonml_same_bar_execution_audit.md`. Le tercile "prix bas" est décidé sur `close[t]` puis les poids qui en découlent étaient appliqués au rendement `R[t]` déjà réalisé — même famille de défaut que #38/#14. Correctif mécanique : `weights_base` et `weights_lev` sont décalés d'un jour (`causal=True`, décider à la clôture de t-1, détenir pendant t) avant le calcul du PnL. Aucun seuil, aucune fenêtre, aucun paramètre modifié.

Même univers, mêmes paramètres (REBAL_EVERY=21, tercile 1/3 par prix, CAP=2.0x en janvier, coûts 5 bps) :

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Tercile prix bas 1.0x (référence, causal) | +0.92 | +168.8% | -36.0% |
| **+ overlay janvier x2.0 (causal)** | **+0.97** | **+210.5%** | -41.5% |

1. Sharpe > référence : OUI
2. Rendement total > référence : OUI

**PASS confirmé — critère renforcé (Sharpe ET rendement) toujours atteint après correction.** Particularité notable par rapport aux autres cycles corrigés : ici la performance de la RÉFÉRENCE elle-même (tercile prix bas 1.0x) *augmente* légèrement après correction (+0,88→+0,92 Sharpe, +156,4%→+168,8% rendement), contrairement au #4/#14/#38 où toute correction causale réduit la performance. Explication : le signal de sélection ici est le NIVEAU de prix de clôture (proxy taille), pas un rendement récent — la fuite « même barre » n'oriente donc pas mécaniquement le portefeuille vers le rendement du jour même comme le fait un signal de momentum, elle introduit simplement un bruit d'exécution dont le signe net dépend de la structure de corrélation entre niveau de prix et rendement journalier sur cet échantillon, pas d'un biais systématique favorable. L'overlay janvier lui-même conserve un edge marginal (+0,05 de Sharpe, +41,7 points de rendement au-dessus de sa propre référence causale), cohérent en ordre de grandeur avec le chiffrage d'origine (+0,03 de Sharpe, +30,4 points).

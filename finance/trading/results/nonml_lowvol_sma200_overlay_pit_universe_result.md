# Résultat — Low-Vol + overlay SMA200, univers POINT-IN-TIME (pré-enregistré)

Réutilisation stricte (Règle 7) du cycle d'origine (#43) : **aucun paramètre modifié**. Seul l'univers de sélection du panier Low-Vol change — appartenance NDX-100 résolue à chaque date de rebalancement. Exécution causale (#166/#167). Le signal SMA200 porte sur l'indice et est inchangé.

Référence = portefeuille Low-Vol 1,0×, **pas** Buy&Hold — le biais du survivant affecte donc les deux jambes.

Univers PIT : 178 tickers, couverture moyenne 88.1%. 2903 séances testables (2015-01-08 → 2026-07-27). Overlay actif 81.7% du temps.

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Low-Vol 1.0x (référence) | +0.61 | +252.3% | -31.5% |
| **Low-Vol + overlay SMA200 2.0x** | **+0.58** | **+557.8%** | -47.2% |

1. Sharpe overlay > référence : non
2. Rendement overlay > référence : OUI

**FAIL — critère renforcé (Sharpe ET rendement) NON atteint sur univers point-in-time.**

Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. Leur comparaison mesure l'effet du biais du survivant sur ce candidat.

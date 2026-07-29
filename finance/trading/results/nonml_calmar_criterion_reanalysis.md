# Ré-analyse du critère Calmar — Étape D v2 (défensif GJR-GARCH, cap=1.0×) sur Russell/S&P/DAX

PAS un nouveau backtest : mêmes paramètres exacts que `run_etape_d_v2.py` (CAP=1.0×, coupe 95e pctl, T0=750, REFIT_EVERY=21) — extrait uniquement le champ `calmar` déjà calculé en interne, jamais affiché dans `etape_D_v2_no_leverage.md`.

| Marché | Calmar BH | Calmar overlay | Sharpe BH | Sharpe overlay | Calmar>BH | Critère Étape D (>25%MDD/≥80%rdt) |
|---|---|---|---|---|---|---|
| Russell 2000 | 0.093 | 0.101 | +0.39 | +0.44 | OUI | NON |
| S&P 500 | 0.093 | 0.075 | +0.44 | +0.49 | non | NON |
| DAX | 0.115 | 0.110 | +0.43 | +0.40 | non | NON |

**1/3 marchés avec Calmar overlay > Calmar BH** (critère du #115), contre **0/3 sous le critère Étape D d'origine** (>25% réduction MDD ET ≥80% rendement conservé, déjà établi dans `etape_D_v2_no_leverage.md`).

**Conclusion : divergence MIXTE, ni purement le critère ni purement le moteur.** 1/3 marché(s) (Russell 2000 ici) inverse(nt) de verdict sous le critère Calmar simple -- pour ce marché, la divergence #115 vs Étape D vient bien du critère (bar plus stricte). Mais 2/3 (S&P 500, DAX) restent des ÉCHECS même sous le critère permissif -- pour ceux-là, c'est le moteur GJR-GARCH lui-même (ou le marché) qui ne répond pas au mécanisme défensif, pas seulement une barre trop haute. **Aucune des deux lectures simples ("c'est juste le critère" ou "c'est juste le moteur") n'est complète -- les deux facteurs jouent, à des degrés différents selon le marché.**

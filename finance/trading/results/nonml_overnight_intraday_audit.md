# Audit adversarial — Overnight vs Intraday

## Vérification d'identité (overnight + intraday == close-to-close)

| Marché | Écart max abs. (devrait être ~0) |
|---|---|
| Composite (5 ans) | 2.67e-16 |
| NDX (40 ans) | 3.13e-16 |
| Russell 2000 | 3.10e-16 |
| S&P 500 | 3.22e-16 |
| DAX | 3.06e-16 |

**OK** — identité mathématique vérifiée (aucun bug de décomposition).

**Note de traçabilité** : un bug a été trouvé et corrigé PENDANT ce cycle, avant de considérer le résultat final — le calcul initial du backtest soustrayait le coût de transaction de Buy & Hold à CHAQUE jour au lieu d'une seule fois à l'entrée, ce qui écrasait artificiellement son Sharpe (ex. NDX affichait faussement +0.04 au lieu de +0.53 attendu, cohérent avec les résultats déjà établis ailleurs dans le projet). Corrigé dans `nonml_overnight_intraday_backtest.py` avant tout commit de résultat — traçable dans l'historique git de ce fichier.

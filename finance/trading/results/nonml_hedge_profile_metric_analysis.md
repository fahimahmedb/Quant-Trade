# Analyse du profil de couverture — #115 (défensif Calmar) — cycle #117

Partition : 1443 séances "crise" (4 fenêtres, Règle 9b) vs 8809 séances "calme" (le reste), sur le pnl déjà committé (NDX, 40 ans).

| Groupe | Séances | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | MDD overlay | MDD BH | Diff. moyen/séance |
|---|---|---|---|---|---|---|---|---|
| Crise (4 fenêtres) | 1443 | -1.13 | -0.84 | -75.3% | -89.5% | -77.5% | -91.9% | +5.89 bps |
| Calme (reste) | 8809 | +1.09 | +1.08 | +73484.1% | +242505.5% | -29.0% | -39.9% | -1.35 bps |

## Lecture "coût d'assurance / prime"

Coût moyen par séance CALME (overlay moins BH) : -1.35 bps/j.
Gain moyen par séance de CRISE (overlay moins BH) : +5.89 bps/j.
Ratio |gain crise| / |coût calme| : 4.4x.

L'overlay coûte un peu en période calme (8809 séances, la grande majorité de l'historique) mais protège nettement pendant les 1443 séances de crise -- profil cohérent avec une COUVERTURE (petite prime payée en continu, gros versement rare et concentré), pas un edge homogène dans le temps.

## Pourquoi le SPA standard pénalise ce profil

Le SPA studentise le différentiel moyen de perte par son écart-type de long terme estimé par bootstrap stationnaire. Un profil de couverture a une variance du différentiel DOMINÉE par les 1443 séances de crise (peu nombreuses, écarts extrêmes) au regard des 8809 séances calmes (nombreuses, écarts faibles mais non nuls) -- ce qui gonfle l'écart-type long terme relativement à la moyenne, et fait mécaniquement baisser la statistique de test, même si le profil économique (payer peu, gagner beaucoup rarement) est exactement celui recherché pour une couverture de portefeuille. **Ceci documente une limite de l'OUTIL pour CE type de profil, PAS une invalidation du verdict Règle 9 déjà rendu sur #115 (qui reste FAIL sous la barre actuelle) ni un nouveau test statistique de substitution.**

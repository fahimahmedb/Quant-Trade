# Pré-enregistrement — Diagnostic : pourquoi le #126 échoue le stress de crise là où le #114 réussit

**Committé AVANT tout calcul.** Cycle #127 du backlog non-ML. Analyse
de diagnostic sur des résultats DÉJÀ committés (#114 NDX, #126 S&P
500), PAS un nouveau backtest, PAS une recherche de correction.

## Question posée (fixée ici, avant tout calcul)

Le #114 (NDX) et le #126 (S&P 500) utilisent EXACTEMENT le même signal
(pente T10Y2Y) et le même mécanisme. Le #114 passe le stress de crise
sur les 4 fenêtres ; le #126 échoue sur dot-com et 2008. Hypothèse
diagnostique : la porte était-elle activement LEVÉE (position > 1,0x)
plus souvent PENDANT ces deux crises précises sur S&P 500 que sur NDX,
expliquant mécaniquement le MDD dégradé (levier appliqué au mauvais
moment plutôt qu'absence de levier protecteur) ?

## Méthode (fixée ici)

Pour chaque fenêtre de crise (dot-com 2000-01→2002-12, 2008 2007-10→
2009-03), à partir des artefacts déjà committés
(`nonml_yield_curve_slope_vol_targeting_overlay_pnl.npz` pour NDX,
`nonml_yield_curve_slope_sp500_vol_targeting_overlay_pnl.npz` pour
S&P 500) :
1. `%activation` = fraction des séances de la fenêtre où la porte est
   active (position > 1,0x), pour les deux marchés.
2. `%activation_pire_décile` = fraction des séances où la porte est
   active, restreinte aux 10% des séances de la fenêtre avec le pire
   rendement quotidien (proxy du cœur du crash) — teste si le levier
   est concentré précisément sur les pires séances.
3. Comparaison directe NDX vs S&P 500 sur ces deux métriques.

## Ce que cette analyse NE fait PAS

Ne modifie aucun paramètre des #114/#126. Ne propose pas de "correction"
du signal pour S&P 500 (ce serait un nouvel essai à pré-enregistrer
séparément, pas un diagnostic). Documente une explication MÉCANISTE
plausible, ne prouve pas une causalité unique.

## Anti-cheat

Analyse committée en un seul passage, sans itération sur le résultat.

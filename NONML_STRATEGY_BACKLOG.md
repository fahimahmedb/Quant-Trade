
## Backlog #391 (12/08/2026) — robustesse portefeuille : chiffres très modifiés, plateaux inchangés

| 391 | Corriger et ré-exécuter les 22 scripts de robustesse de type portefeuille | Aucune nouvelle donnée | **FAIT — 21 rapports réécrits, 0 comptage de grille modifié.** 21 scripts reçoivent la correction d'agrégation (`R` en rendements simples + `log1p` vers `trading_metrics`) ; `amihud_illiquidity_tilt_robustness` reçoit un `R_simple` réservé au P&L, `R` restant en log pour son signal d'illiquidité. Aucun échec d'exécution. |

**Six des sept signalements « `R` sert au signal » étaient de faux positifs** —
de simples dépaquetages `P, R, weights = build_base()`. Vérifiés ligne à ligne
plutôt qu'écartés sur la foi du filtre.

### Les chiffres bougent énormément, les verdicts pas du tout

Exemple (`winners_index52w_high_overlay`, grille CAP) :

| CAP | Sharpe avant → après | Rendement avant → après |
|---|---|---|
| 1,5× | +2,78 → **+3,05** | +7 580,8 % → **+15 677,6 %** |
| 2,0× | +3,00 → **+3,24** | +29 636,2 % → **+72 236,2 %** |
| 3,0× | +3,19 → **+3,36** | +399 977,5 % → **+1 361 779,3 %** |

Toutes les cellules restaient `OUI` avant et le restent après : **aucun plateau
ne change**.

**Explication, et elle est cohérente avec le #380 :** sur un portefeuille, la
correction d'agrégation relève **les deux jambes ensemble** — la stratégie et sa
référence — parce qu'elles détiennent des paniers de titres de volatilité
comparable. Le biais ne les sépare donc pas, contrairement aux overlays
indiciels du #390 où la référence Buy&Hold subissait un traitement différent de
la stratégie et où 24 plateaux sur 27 se sont rétrécis.

**Contraste net entre les deux familles :**

| Famille | Rapports modifiés | Plateaux changés |
|---|---|---|
| robustesse **indicielle** (#390) | 92 | **27, dont 24 rétrécis (−29,8 % de cellules)** |
| robustesse **portefeuille** (#391) | 21 | **0** |

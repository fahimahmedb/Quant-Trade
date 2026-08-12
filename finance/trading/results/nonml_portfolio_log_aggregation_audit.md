# Audit — agrégation de rendements au niveau portefeuille

**Audit de code, non pré-enregistré** (aucun paramètre à calibrer, aucun seuil
de succès : on vérifie une identité comptable).

## Question

Les backtests de portefeuille au niveau titre calculaient le P&L quotidien
comme `Σ wᵢ·r_log,ᵢ` — une moyenne pondérée de rendements **log**. Or le
rendement d'un panier pondéré est `Σ wᵢ·r_simple,ᵢ` : l'agrégation entre
titres est additive en rendement simple, pas en log. La composition dans le
temps, elle, est additive en log. Les deux opérations ne commutent pas.

## Contrôle indépendant

Référence calculée **en nombre de parts** : capital initial 1,0 réparti entre
les titres cotés, parts détenues, portefeuille revalorisé aux prix du marché.
Aucune formule de rendement n'intervient — uniquement des prix et des
quantités. C'est la définition comptable de la performance, indépendante de
toute convention.

Univers : 99 titres, 1396 séances (2021-01-04 → 2026-07-27), rebalancement tous les 21 jours, équipondéré, sans coûts (on isole l'effet d'agrégation).

| Méthode d'agrégation | Capital final | Rendement total |
|---|---|---|
| `Σ wᵢ·r_log,ᵢ` puis `cumprod(1+·)` — **ancienne méthode** | 1.9408 | +94.1% |
| `Σ wᵢ·r_simple,ᵢ` puis `cumprod(1+·)` — **correction** | 3.2235 | +222.4% |
| Simulation en parts — **référence indépendante** | 3.2473 | +224.7% |

- écart de l'ancienne méthode à la référence : **40.23 %**
- écart de la correction à la référence : **0.73 %**

**La correction reproduit la référence comptable ; l'ancienne méthode non.**

Le résidu de la correction vis-à-vis de la simulation en parts n'est pas un
bug : entre deux rebalancements les poids dérivent avec les prix, alors que la
formule `Σ wᵢ·rᵢ` suppose les poids constants sur la période de détention.
C'est l'écart de rebalancement usuel, d'un ordre de grandeur sans rapport avec
l'erreur d'agrégation log.

## Sens du biais

`log(1+x) ≤ x`, donc `Σ wᵢ·r_log,ᵢ ≤ Σ wᵢ·r_simple,ᵢ` : l'ancienne méthode
**sous-estime systématiquement** le rendement de tout panier, et d'autant plus
que les titres sont volatils. Elle pénalise donc le plus le panier le plus
large et le plus volatil — en pratique la référence Buy&Hold équipondérée,
qui détient tout l'univers. Les stratégies sélectives étaient donc comparées
à une référence artificiellement affaiblie.

## Ré-exécution des 34 scripts où `R` ne sert qu'au P&L (#379)

Correction appliquée : `R` passe en rendements simples, `Σ wᵢ·Rᵢ` devient le vrai
rendement de panier, `cumprod(1+pnl)` redevient correct, et `trading_metrics`
reçoit `np.log1p(pnl)` puisqu'il attend une série log. Aucun seuil, aucune
fenêtre, aucun univers, aucun critère n'a été touché.

**Tri préalable, indispensable.** Sur les 42 scripts portant le motif, `R` ne
sert qu'au P&L dans 34 cas ; dans **8 autres il sert AUSSI à construire le
signal** (`amihud_illiquidity_tilt` ×2, `beta_dispersion`, `correlation_regime`,
`dispersion_vol_targeting` ×2, `skewness_tilt`, `leaders_index52w_high`). Y
changer `R` modifierait la stratégie elle-même et non sa seule mesure — un
retuning déguisé. Ces 8 sont **exclus** et recevront un `R_simple` distinct
réservé au P&L, le signal restant calculé en log comme pré-enregistré.

Résultat sur les 34 (18 PASS en jeu) :

| | |
|---|---|
| PASS → FAIL | **7** |
| FAIL → PASS | **0** |

Tombent : `leaders_tom_halloween_union_overlay`, `lowvol_index52w_high_overlay`,
`momentum12_1_sma200_overlay`, `momentum_consistency`,
`momentum_consistency_pit_universe`, `momentum_consistency_sma200_overlay`,
`winners_index52w_high_overlay`.

Avec `momentum_52w_high` corrigé au cycle précédent : **8 reclassifications** dues
à ce seul bug d'agrégation.

## Traitement des 8 derniers scripts (#380)

Les 8 scripts où `R` sert aussi au signal se répartissaient en réalité en deux
catégories distinctes, ce que l'examen du P&L a révélé :

**4 overlays sur INDICE** (`beta_dispersion`, `correlation_regime`,
`dispersion_vol_targeting` ×2) : leur P&L est `pos * bh_full` où `bh_full` est le
rendement log de l'INDICE. Aucune agrégation de panier n'y intervient — les titres
ne servent qu'à construire le signal. Ils n'avaient donc pas besoin de la
correction d'agrégation, **mais ils avaient été écartés à tort de la correction de
composition du #377** : le revert de masse les avait attrapés parce qu'ils
contiennent `np.log(P / P.shift(1))` pour leur signal. Trou comblé ici.

**4 vrais portefeuilles** (`amihud_illiquidity_tilt` ×2, `leaders_index52w_high`,
`skewness_tilt`) : un `R_simple` réservé au P&L a été introduit, `R` restant en
log pour le signal — la définition pré-enregistrée du signal est donc inchangée.
Dans `leaders_index52w_high`, `R_simple` était initialement hors portée (défini
dans `build_weights`, utilisé dans `main`) : la valeur est désormais propagée par
le retour de fonction.

**Résultat : aucun changement de verdict sur les 8** (0 PASS→FAIL, 0 FAIL→PASS).
Les 3 PASS concernés survivent (`amihud_illiquidity_tilt`,
`leaders_index52w_high_overlay`, `dispersion_vol_targeting_overlay`).

Les niveaux bougent pourtant beaucoup — par exemple `amihud_illiquidity_tilt` :

| | Sharpe | Rendement total |
|---|---|---|
| Buy&Hold équipondéré — avant | +0,59 | +70,0 % |
| Tilt illiquidité — avant | +0,84 | +142,8 % |
| Buy&Hold équipondéré — après | **+0,90** | **+171,6 %** |
| Tilt illiquidité — après | **+1,19** | **+334,1 %** |

La référence et la stratégie montent ensemble, l'écart relatif se maintient : le
biais d'agrégation frappait ici les deux jambes de façon comparable, contrairement
aux cas du #379 où il favorisait nettement la stratégie sélective.

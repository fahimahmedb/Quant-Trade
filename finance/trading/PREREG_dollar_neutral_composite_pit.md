# Pré-enregistrement — Portefeuille long/short dollar-neutre composite (univers PIT réel)

**Committé AVANT tout calcul.** Cycle #349 du backlog non-ML.

## 1. Contexte et motivation (Piste A de `RECHERCHE_dsr_par_construction.md`)

Ce cycle fait directement suite à `RECHERCHE_dsr_par_construction.md`
(revue de littérature commandée par l'utilisateur le 01/08/2026, puis
confirmée empiriquement au #133 : réduire `n_trials` par regroupement
en familles, même à `n_trials=8`, ne suffit PAS à franchir le seuil
DSR>0,95 — 0,5121 obtenu). La conclusion de cette revue, non remise en
cause ici, est que le plafond n'est pas un problème de calibrage du
DSR mais un problème d'**ampleur** (loi fondamentale de Grinold) : les
164+ cycles de ce backlog sont presque tous des paris de TIMING sur un
SEUL actif (~12 décisions indépendantes par an), ce qui borne
structurellement le Sharpe atteignable très en dessous du seuil requis
par le DSR à ce niveau de `n_trials`.

**Ce cycle teste la Piste A identifiée comme la plus prometteuse** :
un portefeuille **cross-sectionnel long/short DOLLAR-NEUTRE**, qui
change qualitativement le profil statistique de la stratégie (ampleur
~100+ paris simultanés au lieu de ~12, variance du facteur marché
retirée du dénominateur du Sharpe). **Aucun nouveau signal n'est créé** :
composite de 4 signaux DÉJÀ pré-enregistrés et testés individuellement
dans ce backlog (#4, #73, #82, #15) — zéro degré de liberté de signal
ajouté, seule la construction du PORTEFEUILLE (pondération continue
dollar-neutre au lieu d'une porte binaire long-only) est nouvelle.

## 2. Univers et données

Univers **point-in-time réel** du NDX-100, `data/pead/prices_pit/*.json`
(178 tickers exploitables sur 214, format `{"ts": [...], "close": [...]}`),
filtré à chaque date de rebalancement aux titres **réellement membres**
via `ndx100_membership.tickers_as_of_date()` (déjà vendorée au #163,
couverture 2015-2026). Ancrage `REBAL_ANCHOR = "2015-01-01"` (identique
aux #73/#82/#265/#266, Règle 7). Aucun nouveau fetch réseau.

## 3. Les 4 signaux composants (réutilisation STRICTE, Règle 7 — formules inchangées à la lettre)

| # | Signal | Formule exacte (source) | Direction |
|---|---|---|---|
| #4 | 52-week-high (George & Hwang 2004) | `ratio(t) = close(t) / max(close[t-251:t+1])`, NaN tant que <252j d'historique | z ÉLEVÉ = long (comme la porte tercile sup. déjà utilisée) |
| #73 | Momentum 12-1 (Jegadeesh & Titman 1993) | `momentum(t) = close(t-21)/close(t-252) - 1` | z ÉLEVÉ = long (idem) |
| #82 | Momentum de constance | fraction des 12 blocs de 21j précédents à rendement de bloc positif | z ÉLEVÉ = long (idem) |
| #15 | Low-volatility tilt | `vol(t) = std(rendements simples, fenêtre 60j)` (pct_change, causal) | z **BAS** = long → signal utilisé = **`-zscore(vol)`** (inversion de signe déclarée ici, cohérente avec la porte tercile INFÉRIEURE déjà utilisée pour #15) |

**Limite reconnue et déclarée à l'avance, honnêtement** : **#15 (low-vol)
est individuellement FAIL** dans ce backlog (seul FAIL des 4 composants,
confirmé le 01/08/2026 en exécution causale). Il est inclus ici
uniquement parce que `RECHERCHE_dsr_par_construction.md` §7 le
pré-spécifie explicitement comme composant du composite ("aucun
nouveau degré de liberté de signal ajouté" — le composite est fixé
AVANT de savoir si #15 seul aide ou nuit à l'ensemble). Ce choix est
un engagement pris avant calcul, pas une sélection post-hoc.

## 4. Construction du portefeuille (figée, aucun paramètre optimisé)

1. À chaque date de rebalancement `t` (tous les `REBAL_EVERY=21`
   jours, ancrage 2015-01-01, Règle 7) :
   - Univers éligible = tickers membres du NDX-100 ce jour-là
     (`tickers_as_of_date`) **ET** ayant les 4 signaux calculables
     (historique suffisant, aucune valeur manquante sur les 4). Si
     moins de **30 tickers éligibles** (seuil fixé ici, non retouché),
     portefeuille **à plat** (poids nuls) sur cette période — limite
     déclarée à l'avance, pas de report de poids périmés.
   - `z_k = (x_k - mean(x_k)) / std(x_k)` (écart-type population,
     `ddof=0`) pour chacun des 4 signaux `x_k`, calculé sur l'univers
     éligible uniquement.
   - `z_composite = mean(z_1, z_2, z_3, -z_4)` (moyenne ÉQUIPONDÉRÉE
     des 4 z-scores, `-z_4` = inversion low-vol déclarée en §3).
   - `w_raw = z_composite - mean(z_composite)` (recentrage → somme
     brute nulle, dollar-neutre par construction).
   - `w = w_raw / sum(|w_raw|) × 2` (normalisation à exposition brute
     `Σ|w| = 2`, soit `Σ w_long = 1`, `Σ w_short = -1` — spécification
     exacte de `RECHERCHE_dsr_par_construction.md` §7).
2. Poids maintenus constants entre deux rebalancements (Règle 7,
   identique aux #73/#82).
3. Exécution **causale** (`lag_one_day` — poids décidé à la clôture de
   `t-1`, détenu pendant la séance `t`, convention identique à
   #73/#82/#265/#266).
4. Coûts : **5 bps** (`COST_BPS=5.0`, réutilisé) sur le turnover
   (`Σ|Δw|/2`) à chaque rebalancement.
5. **Limite déclarée à l'avance, non modélisée** : aucun coût
   d'emprunt de titres, aucune contrainte de disponibilité ou de
   rappel de prêt sur la jambe courte. Sur un univers NDX-100
   (méga-capitalisations très liquides), c'est la situation la plus
   favorable possible pour un dollar-neutre — l'omission doit être
   rappelée dans le résultat, pas seulement ici.

## 5. Référence et critère de succès

**Portefeuille dollar-neutre ≠ construction long-only déjà utilisée
partout ailleurs dans ce backlog** — comparer son rendement brut à un
Buy&Hold n'a pas de sens économique (exposition marché ≈ 0 par
construction). **Critère de succès RÉUTILISÉ du seul précédent
dollar-neutre déjà committé dans ce repo** (`pead_backtest.py`,
`PEAD_PREREGISTRATION.md`, Règle 7) :

> **PASS niveau 1 si et seulement si, sur la période testable complète,
> net de coûts : Sharpe annualisé > 0 ET t-stat (moyenne/écart-type ×
> √n) > 2.**

**n_trials = 1** pour cette construction précise (un composite figé, un
schéma de pondération figé, aucun balayage de poids entre signaux ni
de seuil).

**Référence contextuelle rapportée en plus** (informative, pas le
critère de PASS) : Buy&Hold équipondéré de l'univers PIT (même
construction que #73/#82), pour situer le beta/la corrélation au
marché du sleeve.

## 6. Si PASS : combinaison avec le cœur Buy&Hold (portable alpha), règle FIXÉE ici avant tout calcul

Si le critère du §5 est atteint, un second tableau sera rapporté (mais
**ne change pas le verdict niveau 1** ci-dessus) : portefeuille combiné
`r_combiné(t) = r_BH_NDX(t) + r_sleeve(t)` — addition simple et directe
du sleeve autofinancé (dollar-neutre) au cœur Buy&Hold NDX, **à
l'échelle brute du sleeve telle que construite au §4 (Σ|w|=2), sans
aucun coefficient de calibrage optimisé après résultat** (Règle 2). Ce
choix — le plus simple possible, zéro paramètre — est fixé maintenant,
avant tout calcul, précisément pour éviter la tentation de choisir un
poids après avoir vu la performance du sleeve.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La loi de Grinold promet une AMPLEUR plus grande, pas automatiquement
   un meilleur `IC` (qualité de prévision) — les 4 signaux composants
   restent les mêmes signaux, avec la même qualité individuelle
   (dont un FAIL, #15). Combiner des signaux moyens en dollar-neutre
   peut simplement produire un Sharpe moyen avec moins de beta, pas
   nécessairement un Sharpe élevé en absolu.
2. La corrélation résiduelle entre titres NDX-100 (tous des
   méga-capitalisations technologiques très corrélées, corrélation
   moyenne par paires ≈ 0,278 mesurée au #90) réduit l'ampleur
   EFFECTIVE bien en dessous du nombre brut de titres — risque
   explicitement documenté dans `RECHERCHE_dsr_par_construction.md` §1.
3. `#15` étant individuellement FAIL, son inclusion pourrait dégrader
   le composite plutôt que l'améliorer — résultat rapporté tel quel,
   sans retrait post-hoc de #15 si le composite échoue.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_dollar_neutral_composite_pit_backtest.py`,
`scripts/nonml_dollar_neutral_composite_pit_audit.py`,
`results/nonml_dollar_neutral_composite_pit_{result,audit,anti_cheat}.md`.
Si PASS : batterie Règle 9 adaptée (format portefeuille, comme
#265/#266) au cycle suivant, PREREG dédié séparé.

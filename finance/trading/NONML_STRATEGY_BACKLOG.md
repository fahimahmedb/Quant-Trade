# Backlog — stratégies non-ML à itérer (une par cycle, même rigueur que PEAD)

Chaque entrée suit EXACTEMENT le même protocole que PEAD
(`PEAD_PREREGISTRATION.md` + les 4 scripts associés) : pré-enregistrement
committé AVANT tout résultat (hypothèse, univers, période, seuils, critère
de succès chiffrés, n_trials=1), backtest sur données réelles, audit
adversarial (recalcul indépendant + mesure des fuites/limites), vérification
anti-cheat automatisée (ordre chronologique des commits, absence de grille
de paramètres). Résultat rapporté tel quel, y compris si FAIL — pas de
nouvel essai sur la même hypothèse après un résultat, une nouvelle idée
séparée si besoin.

**Explicitement HORS ML** (pas de scikit-learn, pas de features apprises,
pas de walk-forward avec ré-estimation de modèle) — des règles simples,
déterministes, motivées par la littérature académique, pas par un
ajustement statistique sur nos données.

## Statut

| # | Stratégie | Données nécessaires | Statut |
|---|---|---|---|
| 0 | PEAD (surprise de résultats, NDX-100) | api.nasdaq.com + Yahoo (déjà récupérées) | **FAIT — FAIL** (t-stat 1.16 < 2), voir `results/pead_backtest_result.md` |
| 1 | Overnight vs intraday (close→open vs open→close) | OHLC déjà en local (`data/*.txt`) | **FAIT — FAIL** (0/5 marchés), voir `results/nonml_overnight_intraday_result.md` |
| 2 | Effet tournant de mois (turn-of-month, J-1 à J+3) | OHLC déjà en local | **FAIT — PASS Sharpe (4/5)** mais **rendement absolu < Buy&Hold** sur la simulation 300€ (326,62€ vs 349,93€) → **RECLASSÉ FAIL sous la règle renforcée du 28/07** (voir ci-dessous). Voir `results/nonml_turn_of_month_result.md` |
| 3 | Effet jour-de-semaine (lundi/vendredi) | OHLC déjà en local | **FAIT — FAIL** (0/5 marchés), voir `results/nonml_day_of_week_result.md` |
| 4 | Momentum 52-semaines (proximité du plus haut annuel, George & Hwang 2004) | prix NDX-100 déjà récupérés (`data/pead/prices/`) | **FAIT — PASS (Sharpe ET rendement)**, plateau robuste 5/5, voir `results/nonml_momentum_52w_high_result.md` |
| 5 | Reversal court terme (1 semaine, niveau titre) | prix NDX-100 déjà récupérés | **FAIT — FAIL catastrophique** (-83,6% de rendement, Sharpe -1,02), voir `results/nonml_short_term_reversal_result.md` |
| 6 | Rallye de fin d'année ("Santa Claus rally", 5 derniers j. déc. + 2 premiers j. janv.) | OHLC déjà en local | **FAIT — FAIL** (0/5, structurel : ~2,8% du temps investi), voir `results/nonml_santa_claus_rally_result.md` |
| 7 | Effet pré/post jour férié US | OHLC déjà en local, détection data-driven (pas de calendrier codé en dur) | **FAIT — FAIL** (0/5, structurel : ~7% du temps investi), voir `results/nonml_holiday_effect_result.md` |
| 8 | Turn-of-month EN OVERLAY (reste investi 1x en permanence comme Buy&Hold, ajoute un levier supplémentaire SEULEMENT pendant la fenêtre ToM déjà identifiée au lieu d'être flat hors fenêtre) | OHLC déjà en local | **FAIT — PASS (4/5)**, plateau robuste CAP 1.5x-3.0x, voir `results/nonml_tom_overlay_result.md` |
| 9 | Barbell structuré : overlay levé sur régime de vol calme (variante réalisée, pas ToM déjà couvert au #8) | OHLC déjà en local | **FAIT — FAIL** (2/5), voir `results/nonml_vol_regime_overlay_result.md` |
| 10 | Buy&Hold levé en continu (x2/x3 fixe, rebalancement quotidien) vs Buy&Hold 1x, test formel avec critère Sharpe+rendement sur les 5 marchés | OHLC déjà en local | **FAIT — FAIL** (0/5, invariance mathématique du Sharpe confirmée), voir `results/nonml_leveraged_bh_result.md` |
| 11 | Combiner momentum 52-semaines (#4, PASS) + overlay levé ToM (#8, PASS) | prix NDX-100 déjà récupérés | **FAIT — PASS**, plateau robuste et croissant CAP 1.5x-3.0x, voir `results/nonml_leaders_tom_overlay_result.md` |
| 12 | Effet janvier small-cap (Rozeff & Kinney 1976), overlay levé Russell 2000 | OHLC déjà en local | **FAIT — FAIL** (marginal, aucun effet janvier brut détecté), voir `results/nonml_january_smallcap_result.md` |
| 13 | Rebond post-drawdown extrême (overlay levé après choc -10%/20j) | OHLC déjà en local | **FAIT — FAIL net** (0/5, MDD bien pire), voir `results/nonml_post_drawdown_rebound_result.md` |

## Nouvelles idées ajoutées (backlog initial #0-10 épuisé, 28/07/2026)

Après un premier passage complet (2 PASS sur 11 hypothèses testées :
#4 momentum 52-semaines, #8 ToM overlay levé), 3 nouvelles pistes
ajoutées ci-dessus (#11-13), dans le même esprit (anomalie documentée ou
combinaison d'effets déjà validés, données déjà accessibles, hors ML).

| 14 | Momentum court terme titre (winners, inverse du #5) | prix NDX-100 déjà récupérés | **FAIT — PASS extrême** (Sharpe +2,35 à +3,75 selon variante — **prudence forte** : reflète un marché haussier concentré IA/semi 2021-2026, pas forcément généralisable), voir `results/nonml_short_term_momentum_result.md` |
| 15 | Low-volatility tilt (tercile inf. vol réalisée 60j, NDX-100) | prix NDX-100 déjà récupérés | **FAIT — FAIL** (Sharpe 0,54 vs 0,65, rendement 40,2% vs 86,1%, mais MDD bien meilleur -18,9% vs -35,2%), voir `results/nonml_low_vol_tilt_result.md` |
| 16 | Overlay levé déclenché par accélération du signal momentum 52-semaines — 3e variante de combinaison avec #4 | prix NDX-100 déjà récupérés | **FAIT — FAIL** (Sharpe quasi identique +0,78 vs +0,78, MDD pire -33,9% vs -25,7%), voir `results/nonml_leaders_accel_overlay_result.md` |

## Backlog #0-13 complet (28/07/2026, suite du rattrapage)

3 PASS sur 14 hypothèses testées (#4, #8, #11). 3 nouvelles pistes
ajoutées ci-dessus (#14-16).

## Backlog #0-16 complet (28/07/2026), 3 nouvelles idées (#17-19)

4 PASS sur 17 hypothèses testées (#4, #8, #11, #14).

| 17 | "Sell in May" / effet Halloween, overlay levé nov-avril | OHLC déjà en local | **FAIT — PASS (4/5)**, plateau 4,4,3,3 selon CAP, voir `results/nonml_halloween_effect_result.md` |
| 18 | Combiner winners momentum (#14) + overlay ToM (#8) | prix NDX-100 déjà récupérés | **FAIT — FAIL** (Sharpe +2,35→+2,22, MDD -22,4%→-29,2%), voir `results/nonml_winners_tom_overlay_result.md` |
| 19 | Window dressing de fin de trimestre (overlay levé) | OHLC déjà en local | **FAIT — FAIL** (2/5), voir `results/nonml_quarter_end_window_dressing_result.md` |

## Backlog #0-19 complet (28/07/2026), 3 nouvelles idées (#20-22)

5 PASS sur 20 hypothèses testées (#4, #8, #11, #14, #17).

| 20 | Combiner Halloween (#17) + Leaders 52w (#4) | prix NDX-100 déjà récupérés | **FAIT — FAIL** (Sharpe +0,78→+0,71, MDD -25,7%→-38,1%), voir `results/nonml_leaders_halloween_overlay_result.md` |
| 21 | Combiner ToM (#8) + Halloween (#17) : overlay levé quand L'UNE OU L'AUTRE fenêtre est active (union), sur Buy&Hold | OHLC déjà en local | **FAIT — PASS (4/5)**, robuste sur toute la grille CAP 1.5x-3.0x (constant 4/5), sim 300€ NDX : 412,24€ vs 349,93€ BH (+37,4% vs +16,6%), Sharpe +4,11 vs +2,74. MDD dégradé partout (levier ~66% du temps) — signalé honnêtement. Voir `results/nonml_tom_halloween_union_overlay_result.md` |
| 22 | Pullback court terme au niveau INDICE (pas titre) : repli 2-3j de quelques % (pas un choc extrême comme #13) → overlay levé sur le rebond, horizon différent de #13 | OHLC déjà en local | **FAIT — FAIL** (0/5, catastrophique : rendement jusqu'à -99% sur NDX/Russell/S&P 500 — le repli court terme indice est souvent le DÉBUT d'un krach prolongé, pas un signal de rebond ; confirmé par recalcul indépendant du déclencheur et de la position, aucun bug), voir `results/nonml_short_pullback_rebound_result.md` et `results/nonml_short_pullback_rebound_audit.md` |

## Backlog #0-32 complet (28/07/2026)

10 PASS sur 32 hypothèses testées (#4, #8, #11, #14, #17, #21, #23, #29, #30, #32 — #14 et #30 sous prudence forte, #32 avec robustesse partielle).

| 32 | Combiner filtre de tendance SMA200 (#29, meilleur PASS du backlog) + overlay union ToM∪Halloween (#21) sur Buy&Hold : union des deux signaux (levé si tendance haussière OU fenêtre calendaire) | OHLC déjà en local | **FAIT — PASS (5/5)** au CAP pré-enregistré, mais robustesse **moins solide que le #29 seul** : 5/5 à 1.5x/2.0x, dégradé à 4/5 (2.5x) puis 3/5 (3.0x) — l'union à 3 signaux atteint ~90% de jours levés (quasi-permanent), ce qui amplifie le volatility drag à fort levier. Gain de rendement énorme mais surtout mécanique (effet multiplicatif du levier, cf. #10), MDD très dégradé partout. Voir `results/nonml_sma200_tom_halloween_union_overlay_result.md` |
| 33 | Combiner filtre de tendance SMA200 (#29) + portefeuille Leaders 52-semaines (#4) : overlay levé quand l'indice NDX est en tendance haussière (SMA200), appliqué au portefeuille Leaders | prix NDX-100 déjà récupérés | à faire |
| 34 | "Golden cross" (SMA50 > SMA200, signal de tendance alternatif à la comparaison prix/SMA200 du #29) : overlay levé quand la moyenne mobile courte est au-dessus de la longue | OHLC déjà en local | à faire |

| 29 | Filtre de tendance SMA200 (Faber 2007) : overlay levé quand le prix de clôture est AU-DESSUS de sa moyenne mobile 200j (régime haussier structurel), 1.0x sinon — jamais testé jusqu'ici (différent des effets calendaires #2/#8/#17/#21 et des chocs #13/#22/#24) | OHLC déjà en local | **FAIT — PASS (5/5)**, le meilleur résultat du backlog à ce stade (Sharpe et rendement supérieurs sur tous les marchés, ex. NDX 40 ans : Sharpe +0,51→+0,59, rendement +5004%→+50026%), plateau parfait 5/5 sur toute la grille CAP 1.5x-3.0x, sim 300€ NDX : 402,66€ vs 349,93€ BH. MDD dégradé partout (levier ~70-75% du temps) — signalé honnêtement, et l'audit montre que le filtre ne coupe pas toujours vite pendant les krachs prolongés (61,6% de jours encore levés pendant les drawdowns NDX ≥40%). Voir `results/nonml_sma200_trend_overlay_result.md` |
| 30 | Cycle électoral américain (presidential cycle, 3e année de mandat historiquement la plus forte, Hirsch 1986) : overlay levé pendant l'année pré-électorale — testable sur NDX 40 ans (~10 cycles complets) | OHLC déjà en local (NDX 40 ans) | **FAIT — PASS (5/5)**, plateau parfait sur CAP 1.5x-3.0x — **prudence forte** : les 5 marchés ne sont PAS des essais indépendants (même cycle électoral US global affectant simultanément tous les indices mondiaux via la politique monétaire), et le Composite ne couvre qu'1 seule année pré-électorale partielle (2023) contre 7-14 pour les 4 autres marchés — le signal doit être jugé sur NDX/Russell/S&P/DAX (historique long), pas comme 5 confirmations indépendantes. Voir `results/nonml_presidential_cycle_overlay_result.md` |
| 31 | Overlay levé en régime de vol ÉLEVÉE (inverse du #9 qui testait la vol calme, FAIL 2/5) — capture le vol clustering (vol élevée persiste, ARCH massif déjà documenté à l'Étape A) plutôt qu'un simple rebond de prix (#13/#22/#24) | OHLC déjà en local | **FAIT — FAIL** (0/5, la vol élevée coïncide trop souvent avec les phases de baisse — même écueil économique que #13/#22/#24), voir `results/nonml_high_vol_regime_overlay_result.md` |

| 26 | "Triple witching" (3e vendredi de mars/juin/sept/déc, expiration options/futures trimestrielle — volatilité/volume documentés) : overlay levé ce jour-là + le suivant, détection data-driven (rang du vendredi dans le mois, pas de calendrier codé en dur) | OHLC déjà en local | **FAIT — FAIL** (1/5, seul Composite passe ; audit confirme la détection data-driven correcte face à un recalcul totalement indépendant, aucun bug malgré des cas particuliers de fermeture de marché en 2001/2004/2008/2026), voir `results/nonml_triple_witching_overlay_result.md` |
| 27 | Pré/post jour férié EN OVERLAY (reprise du #7, qui était flat hors fenêtre et structurellement désavantagé en rendement absolu comme #2/#6 — même détection data-driven que #7, mais design overlay comme #8) | OHLC déjà en local | **FAIT — FAIL** (1/5, seul DAX passe ; même en overlay l'effet pré/post férié reste trop faible/inconsistant net de coûts), voir `results/nonml_holiday_effect_overlay_result.md` |
| 28 | Combiner low-volatility tilt (#15, FAIL mais MDD bien meilleur) + overlay union ToM∪Halloween (#21, PASS) : teste si l'overlay calendaire aide aussi un portefeuille défensif (vol faible), pas seulement momentum (#11/#23) | prix NDX-100 déjà récupérés | **FAIT — FAIL** (Sharpe +0,54→+0,49 dégradé bien que rendement +40,2%→+59,3% supérieur — l'overlay calendaire n'aide QUE le momentum (#11/#23), pas un portefeuille défensif low-vol dont la vertu est justement d'éviter le levier), voir `results/nonml_lowvol_tom_halloween_union_overlay_result.md` |

| 23 | Combiner momentum 52-semaines (#4, PASS) + overlay Halloween∪ToM (#21, PASS) : 3e combinaison de calendrier sur le portefeuille Leaders, variante différente du #11 (ToM seul) et du #20 (Halloween seul, FAIL) | prix NDX-100 déjà récupérés | **FAIT — PASS** (Sharpe +0,78→+0,85, rendement +81,6%→+178,7%, MDD -25,7%→-38,1%), robuste et croissant sur toute la grille CAP 1.5x-3.0x, sim 300€ : 351,96€ vs 330,31€ référence. Confirme que l'union porte bien la totalité du gain de #21 même combinée à la sélection Leaders (contrairement à Halloween seul, #20, FAIL) — voir `results/nonml_leaders_tom_halloween_union_overlay_result.md` |
| 24 | Overlay levé sur rebond APRÈS jour de forte baisse (ampleur ≥5% en 1 seule séance, pas 3j comme #22) — horizon encore différent, teste si un choc plus brutal mais ponctuel (1 jour) change la conclusion du #22 | OHLC déjà en local | **FAIT — FAIL** (0/5, confirme le #22 : un choc ponctuel de ≥5% reste plus souvent annonciateur d'une poursuite de la baisse qu'un point bas isolé), voir `results/nonml_single_day_shock_rebound_result.md` |
| 25 | Effet fin de semaine élargi (vendredi + lundi combinés en fenêtre, variante du #3 day-of-week qui testait chaque jour séparément et avait FAIL) — overlay levé sur la fenêtre vendredi-lundi | OHLC déjà en local | **FAIT — FAIL** (0/5, même sous design overlay et fenêtre élargie, confirme #3 : pas d'edge week-end exploitable net de coûts), voir `results/nonml_friday_monday_overlay_result.md` |

## Règles du cycle

1. Prendre la PREMIÈRE ligne "à faire" du tableau (ordre = déjà trié par
   facilité de mise en œuvre avec les données déjà en local, pour limiter
   le nouveau fetch réseau à chaque cycle).
2. Écrire `finance/trading/PREREG_<nom>.md`, committer AVANT tout calcul.
3. Construire `scripts/nonml_<nom>_backtest.py`, `scripts/nonml_<nom>_audit.py`,
   réutiliser `pead_anti_cheat_check.py` en le généralisant (paramètre nom
   de stratégie) plutôt que dupliquer.
4. Exécuter, committer les résultats (PASS ou FAIL, honnêtement).
5. Mettre à jour CE tableau (statut), committer.
6. Si le tableau est épuisé, proposer 2-3 nouvelles idées non-ML (même
   esprit : anomalie documentée, données déjà accessibles ou facilement
   récupérables gratuitement) et les ajouter avant de clore le cycle.

## Règle de succès RENFORCÉE (instruction utilisateur, 28/07/2026)

Une stratégie n'est un vrai succès QUE si elle bat Buy & Hold **à la fois**
en Sharpe **et** en rendement total net de coûts — un Sharpe supérieur
avec un rendement absolu inférieur (ex. cycle #2) ne compte plus comme
PASS, même si le critère pré-enregistré d'origine (Sharpe seul) était
formellement atteint. **Tout nouveau pré-enregistrement à partir de
maintenant doit inclure cette double condition explicitement dans son
critère de succès chiffré** (ex. "Sharpe > BH ET rendement total ≥ BH sur
≥4/5 marchés"). Les cycles #0 à #3 restent documentés avec leur verdict
d'origine (traçabilité), mais le cycle #2 est explicitement reclassé
FAIL sous cette règle (voir tableau ci-dessus) — pas de retuning caché,
juste une barre plus stricte assumée à partir de maintenant.

## Levier autorisé (instruction utilisateur, 28/07/2026)

Les stratégies futures peuvent inclure des variantes à effet de levier —
ne pas exclure le levier par défaut comme c'était implicitement le cas
jusqu'ici (toutes les stratégies testées étaient ≤1x). Toujours fixer un
CAP de levier a priori dans le pré-enregistrement (même logique que les
analyses Kelly/vol-targeting déjà faites, ex. CAP=2.0 ou 3.0, jamais
« illimité ») et ne jamais retoucher ce CAP après avoir vu un résultat.
Le risque plus élevé est explicitement accepté par l'utilisateur — mais
reste signalé honnêtement dans chaque rapport (MDD, pas seulement
Sharpe/rendement).

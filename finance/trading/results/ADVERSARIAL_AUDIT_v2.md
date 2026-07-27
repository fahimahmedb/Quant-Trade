# Audit adversarial v2 — Étapes C/D (recalcul depuis les données brutes)

Objectif : chercher activement les failles de l'audit précédent (`AUDIT_CANONICAL_FRAMEWORK_FINAL.md`, `ROBUSTNESS_AUDIT_DETAILED.md`, 24/07/2026), pas confirmer ses conclusions. Aucun chiffre ci-dessous n'est recopié d'un rapport existant — tout est recalculé depuis `data/*.txt` par ce script.

## 1. Écart code / rapport — la grille "déployée" (cap 2.0×/90e) existe-t-elle encore dans le code ?

- Grille ACTUELLE dans `finance/trading/scripts/run_etape_d_optimize.py` : CAP_GRID=[1.50], PCTL_GRID=[95].
- Historique git de ce fichier :
  - `fab07d5d392ad622b349a80b33b39b0246b67f05 2026-07-27 Audit adversarial Étape C/D : corrige le pipeline cassé (bug de chemin d'import post-réorganisation) et ajoute le protocole anti-snooping`
  - `fdbd19342c587cf3eddc933a6bf2a7b63be14267 2026-07-25 Reorganize repository: finance/trading, divers/robot-politique, cours`
  - `ee8a2fd136216cd60a657f172743a6ede9d02ec1 2026-07-15 Phase 1 fixes: Pre-register combo (cap=1.50, pctl=95) + Increase embargo to 21 days`
  - `a40cc098b6cbb07688069d9c8114d414086b99d3 2026-07-14 Étape D optimisé + meta-labeling variantes : grid-search paramètres et secondaires`
- Le fichier de résultats `finance/trading/results/etape_D_overlay_optimized.md` cite-t-il encore la grille de 12 combos (cap 2.00×/90e) ? **OUI — stale, non régénéré depuis le fix**.
- L'audit précédent (`AUDIT_CANONICAL_FRAMEWORK_FINAL.md`, daté du 24/07) cite-t-il ce même combo cap=2.0×/90e comme déployé ? **non**.

**Constat** : le fix `ee8a2fd` (15/07/2026, "Phase 1 fixes: Pre-register combo") a réduit la grille à 1 seul combo pré-enregistré (cap=1.50×/pctl=95e, identique à celui de l'Étape D d'origine) précisément pour éliminer le biais de sélection sur 12 combinaisons. Le fichier de résultats et l'audit du 24/07 n'ont **jamais été régénérés** après ce fix : ils recommandent un déploiement (cap=2.0×/90e) que le code actuel ne produit plus.

## 2. DSR correct de la grille historique de 12 combinaisons

Grille historique recalculée depuis les données brutes (NDX, 9522 obs OOS) : cap ∈ [1.0, 1.25, 1.5, 2.0] × pctl ∈ [90, 95, 99] = 12 combinaisons.

| cap | pctl | Sharpe ann. | MDD % | ΔMDD rel. | Rdt/BH | Critère | **DSR (n=12, correct)** | DSR (n=1, à tort — cf. audit du 24/07) |
|---|---|---|---|---|---|---|---|---|
| 1.00× | 90e | +0.66 | -48.4 | +41.6% | 84.3% | OUI | **1.000** | 1.000 |
| 1.50× | 90e | +0.68 | -48.4 | +41.6% | 107.4% | OUI | **1.000** | 1.000 |
| 2.00× | 90e | +0.66 | -48.4 | +41.6% | 108.1% | OUI | **1.000** | 1.000 |
| 1.25× | 90e | +0.68 | -48.4 | +41.6% | 100.3% | OUI | **1.000** | 1.000 |
| 1.00× | 95e | +0.65 | -57.2 | +31.0% | 87.9% | OUI | **1.000** | 1.000 |
| 1.50× | 95e | +0.67 | -57.2 | +31.0% | 111.2% | OUI | **1.000** | 1.000 |
| 2.00× | 95e | +0.65 | -57.2 | +31.0% | 111.9% | OUI | **1.000** | 1.000 |
| 1.25× | 95e | +0.67 | -57.2 | +31.0% | 104.0% | OUI | **1.000** | 1.000 |
| 1.50× | 99e | +0.67 | -68.7 | +17.1% | 114.7% | non | **1.000** | 1.000 |
| 2.00× | 99e | +0.65 | -68.7 | +17.1% | 115.5% | non | **1.000** | 1.000 |
| 1.25× | 99e | +0.67 | -68.7 | +17.1% | 107.5% | non | **1.000** | 1.000 |
| 1.00× | 99e | +0.64 | -68.7 | +17.1% | 91.3% | non | **1.000** | 1.000 |

**Combo historiquement "gagnant"** : cap=2.00×, pctl=90e — DSR correct (n=12) = **1.000**, DSR affiché à tort dans l'audit du 24/07 (n=1) = 1.000.
→ Même avec la correction n_trials=12, ce combo reste au-dessus de 0,95 — la conclusion pratique ne change pas, mais le raisonnement de l'audit du 24/07 ("no trials inflation") était malgré tout incorrect en soi.

**Rappel** : ce combo n'est de toute façon plus celui produit par le code actuel (voir section 1) — le choix pré-enregistré en vigueur est cap=1.50×/pctl=95e (N=3 famille, `results/etape_D_overlay.md`), qui atteint déjà seul le critère de succès sur NDX sans nécessiter de grid-search.

## 3. Validation cross-marché réelle (Russell 2000 / S&P 500 / DAX)

Validation cross-marché **réelle** (Russell 2000 / S&P 500 / DAX — jamais testée pour C/D jusqu'ici ; Composite vs NDX ne compte pas comme indépendant, cf. protocole anti-snooping). Même protocole exact (T0=750, refit=21j, coûts 5bps), définitions figées, zéro tuning.

### Russell 2000 (n=9781, OOS obs=9031)
- Étape C — GJR-t vs GARCH-n (QLIKE, DM HAC) : t=+5.87, p(unilat., GJR-t meilleur)=0.0000 → bat le bench
- Étape D — overlay VolTarget+Cut (cap=1.5×, pctl=95e, figé, zéro tuning) : BuyHold Sharpe=+0.39/MDD=-59.9% vs Overlay Sharpe=+0.42/MDD=-51.6% → ΔMDD relatif=+13.9%, rendement conservé=83.1% → critère de succès : **NON**

### S&P 500 (n=14251, OOS obs=13501)
- Étape C — GJR-t vs GARCH-n (QLIKE, DM HAC) : t=+5.08, p(unilat., GJR-t meilleur)=0.0000 → bat le bench
- Étape D — overlay VolTarget+Cut (cap=1.5×, pctl=95e, figé, zéro tuning) : BuyHold Sharpe=+0.44/MDD=-56.8% vs Overlay Sharpe=+0.47/MDD=-49.8% → ΔMDD relatif=+12.3%, rendement conservé=66.6% → critère de succès : **NON**

### DAX (n=6776, OOS obs=6026)
- Étape C — GJR-t vs GARCH-n (QLIKE, DM HAC) : t=+4.74, p(unilat., GJR-t meilleur)=0.0000 → bat le bench
- Étape D — overlay VolTarget+Cut (cap=1.5×, pctl=95e, figé, zéro tuning) : BuyHold Sharpe=+0.43/MDD=-54.8% vs Overlay Sharpe=+0.41/MDD=-56.7% → ΔMDD relatif=-3.5%, rendement conservé=110.1% → critère de succès : **NON**


## 4. Grille de perturbation locale (diagnostic, NDX)

**Diagnostic uniquement — ne redéfinit PAS le combo déployé** (cap=1.50×/pctl=95e reste le choix pré-enregistré ; ceci vérifie juste l'absence de pic isolé autour de ce point sur NDX).

| cap | pctl | Sharpe ann. | MDD % | ΔMDD rel. | Rdt/BH | Critère |
|---|---|---|---|---|---|---|
| 1.30× | 93e | +0.67 | -55.2 | +33.4% | 102.7% | OUI |
| 1.30× | 95e | +0.68 | -57.2 | +31.0% | 106.0% | OUI |
| 1.30× | 97e | +0.69 | -60.0 | +27.6% | 109.7% | OUI |
| 1.50× | 93e | +0.67 | -55.2 | +33.4% | 107.8% | OUI |
| 1.50× | 95e | +0.67 | -57.2 | +31.0% | 111.2% | OUI |
| 1.50× | 97e | +0.69 | -60.0 | +27.6% | 114.9% | OUI |
| 1.70× | 93e | +0.66 | -55.2 | +33.4% | 109.0% | OUI |
| 1.70× | 95e | +0.66 | -57.2 | +31.0% | 112.3% | OUI |
| 1.70× | 97e | +0.68 | -60.0 | +27.6% | 116.1% | OUI |

**9/9** points de la grille locale atteignent le critère de succès → plateau (robuste au choix exact du paramètre).

## 5. Test de mutation anti-lookahead

Mutation des données **strictement postérieures** au bloc de refit courant (`r[tr+refit_every:]` re-tiré au hasard), vérification que les prévisions du bloc réellement exposé en production (`path[tr:tr+refit_every]`, ce que `vol_fcst` expose) sont inchangées, testé à 5 points de refit (précoce à tardif) :

| tr | bloc utilisé | écart max |
|---|---|---|
| 751 | [751:772] | 0.00e+00 |
| 855 | [855:876] | 0.00e+00 |
| 1800 | [1800:1821] | 0.00e+00 |
| 5136 | [5136:5157] | 0.00e+00 |
| 10230 | [10230:10251] | 0.00e+00 |

→ **PASS (aucune fuite détectée sur le bloc opérationnel, aux 5 points testés)**.

Dégradation par retard artificiel d'exécution (`backtest(..., delay=k)`, test intégré au repo) — une dégradation BRUTALE dès delay=1 (au lieu de progressive) indiquerait une fuite d'information plutôt qu'un effet temporel normal :
| delay (jours) | Sharpe ann. |
|---|---|
| 0 | +0.67 |
| 1 | +0.71 |
| 2 | +0.67 |
| 3 | +0.71 |

## Verdict corrigé

- Le combo "déployé" cité par l'audit du 24/07 (cap=2.0×/90e, DSR=1.000) n'est **plus produit par le code actuel** et son DSR était de toute façon mal calculé (n_trials=1 au lieu de 12).
- Le combo réellement pré-enregistré en vigueur (cap=1.50×/pctl=95e) reste valide sur NDX (Étape D d'origine, N=3, critère de succès atteint sans grid-search) — c'est CELUI-LÀ qui doit être cité comme référence, pas le combo de la grille de 12.
- Voir section 3 pour savoir si ce combo pré-enregistré réplique sur des marchés génétiquement indépendants (jamais vérifié avant ce script).
- Voir section 5 pour la détection de fuite d'information (mutation du futur + test de délai intégré).

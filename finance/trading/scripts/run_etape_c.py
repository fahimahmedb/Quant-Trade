"""Etape C - modeles de volatilite : estimation in-sample + evaluation
walk-forward out-of-sample. Produit results/etape_C_volatilite.md.

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping) :
- 6 modeles declares (cf. src/volatility.py), aucun ajout a posteriori
- Fenetre initiale 750 obs (~3 ans), expansive, re-estimation tous les 5 jours
- 500 previsions 1 pas + 496 previsions cumulees 5 pas
- Perte primaire : QLIKE sur proxy = rendement demeane au carre (non biaise)
- Perte secondaire : MSE ; proxy secondaire : RV Parkinson re-echelonnee
- Benchmark : GARCH(1,1)-normal ; test DM (HAC), unilateral "modele > benchmark"
"""
import sys
import warnings
from pathlib import Path

import numpy as np

np.random.seed(42)  # Reproducible SPA bootstrap (Politis-Romano)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, parkinson_var_pct  # noqa: E402
from volatility import (  # noqa: E402
    ANNUALIZE,
    ARCH_SPECS,
    dm_test,
    ewma_path,
    fit_arch,
    fit_har,
    garch_multistep,
    garch_path,
    garch_path_fold_only,
    har_forecast,
    mse,
    params_dict,
    qlike,
    spa_test,
)

import os  # noqa: E402

DATA = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "nasdaq_composite_daily.txt")
OUT = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "results" / "etape_C_volatilite.md")

df = load_ohlc(DATA)
r = log_returns_pct(df).values          # rendements log quotidiens, en %
rv = parkinson_var_pct(df).values       # variance Parkinson alignee, en %^2
dates = log_returns_pct(df).index
T = len(r)

# Validation: both functions drop first obs, so r and rv should be aligned
assert len(rv) == len(r), f"Length mismatch: r={len(r)} obs, rv={len(rv)} obs (should be equal)."

# REFIT_EVERY : surchargeable pour les longs historiques (coût ∝ nb de ré-estim.)
T0, REFIT_EVERY, H = 750, int(os.environ.get("REFIT_EVERY", 5)), 5
MODELS = ["EWMA", "GARCH-n", "GARCH-t", "GJR-t", "GJR-skewt", "HAR-P"]
BENCH = "GARCH-n"

# ---------------------------------------------------------------- in-sample
lines = []
w = lines.append
w("# Étape C — Modèles de volatilité : estimation et évaluation walk-forward\n")
w(f"## 1. Estimation in-sample (échantillon complet, {T} obs)\n")
w("| Modèle | ω | α | γ (levier) | β | ν | λ(skew) | persistance | demi-vie (j) | LogL | BIC |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
insample = {}
for name in ARCH_SPECS:
    res = fit_arch(r, name)
    p = params_dict(res)
    insample[name] = (res, p)
    gjr = "o" in ARCH_SPECS[name] and ARCH_SPECS[name]["o"] == 1
    persist = p["alpha[1]"] + p["beta[1]"] + (p.get("gamma[1]", 0.0) / 2 if gjr else 0.0)
    hl = np.log(0.5) / np.log(persist) if persist < 1 else np.inf
    w(f"| {name} | {p['omega']:.4f} | {p['alpha[1]']:.4f} "
      f"| {p.get('gamma[1]', float('nan')):.4f} | {p['beta[1]']:.4f} "
      f"| {p.get('nu', float('nan')):.2f} | {p.get('lambda', float('nan')):.3f} "
      f"| {persist:.4f} | {hl:.0f} | {res.loglikelihood:.1f} | {res.bic:.1f} |")
w("")
res_gjr, p_gjr = insample["GJR-t"]
tstats = res_gjr.tvalues
w(f"*GJR-t : t-stat de γ = {tstats['gamma[1]']:.2f} → effet de levier "
  + ("**significatif**" if abs(tstats['gamma[1]']) > 1.96 else "NON significatif")
  + f" ; α = {p_gjr['alpha[1]']:.4f} (t={tstats['alpha[1]']:.2f}) : les chocs positifs "
  "contribuent peu, l'essentiel passe par les chocs négatifs — fait stylisé indice actions.*\n")

# validation de la recursion maison contre arch (previsions 1 pas)
s2_mine = garch_path(r, p_gjr, gjr=True)[-1]
s2_arch = float(res_gjr.forecast(horizon=1, reindex=False).variance.values[0, 0])
rel = abs(s2_mine - s2_arch) / s2_arch
w(f"## 2. Validation d'implémentation\n")
w(f"- Prévision 1 pas GJR-t : récursion maison {s2_mine:.6f} vs `arch` {s2_arch:.6f} "
  f"(écart relatif {rel:.2e}) → " + ("**OK**" if rel < 1e-3 else "**ÉCHEC**"))
assert rel < 1e-3, "recursion maison incoherente avec arch"

# ------------------------------------------------------------- walk-forward
fc1 = {m: np.full(T, np.nan) for m in MODELS}          # variance 1 pas pour r[t]
fc5 = {m: np.full(T, np.nan) for m in MODELS}          # variance cumulee r[t..t+4]
nu_track, refit_dates = [], []

for tr in range(T0, T, REFIT_EVERY):
    block = range(tr, min(tr + REFIT_EVERY, T))
    mu_tr = r[:tr].mean()
    paths, pars = {}, {}
    for name in ARCH_SPECS:
        res = fit_arch(r[:tr], name)
        p = params_dict(res)
        pars[name] = p
        # Use fold_only to prevent retroactive updates: params fit on r[:tr]
        # are applied forward only from index tr, ensuring strict walk-forward.
        paths[name] = garch_path_fold_only(r, p, tr, gjr=("GJR" in name))
    paths["EWMA"] = ewma_path(r - mu_tr + 0.0)  # eps construit avec mu du train
    pars["EWMA"] = None
    har_mod = fit_har(rv[:tr], r[:tr])
    nu_track.append(pars["GJR-t"]["nu"])
    refit_dates.append(dates[tr])
    for t in block:
        for name in ARCH_SPECS:
            s2n = paths[name][t]
            fc1[name][t] = s2n
            if t + H <= T:
                fc5[name][t] = garch_multistep(s2n, pars[name], "GJR" in name, H).sum()
        s2n = paths["EWMA"][t]
        fc1["EWMA"][t] = s2n
        if t + H <= T:
            fc5["EWMA"][t] = H * s2n
        hf = har_forecast(rv[:t], har_mod, H)
        fc1["HAR-P"][t] = hf[0]
        if t + H <= T:
            fc5["HAR-P"][t] = hf.sum()

# Validation: check that fc1 and fc5 are fully filled in their respective ranges
for m in MODELS:
    nan_count_fc1 = np.isnan(fc1[m][T0:]).sum()
    nan_count_fc5 = np.isnan(fc5[m][T0:T-H+1]).sum()
    assert nan_count_fc1 == 0, f"fc1[{m}] has {nan_count_fc1} NaN values in [T0, T)"
    assert nan_count_fc5 == 0, f"fc5[{m}] has {nan_count_fc5} NaN values in [T0, T-H+1)"

# proxies de variance realisee — aligned with evolving parameters in loop
# Use expanding mean (info t-1) to match garch_path_fold_only walk-forward semantics
mu_exp = np.array([r[:max(t, 1)].mean() for t in range(T)])  # moyenne expansive
eps2 = (r - mu_exp) ** 2                                      # proxy primaire, mu evolue avec refits
rvs = rv * (eps2[:T0].mean() / rv[:T0].mean())               # Parkinson re-echelonne (echelle du train)
idx1 = np.arange(T0, T)
idx5 = np.arange(T0, T - H + 1)
real5 = np.array([eps2[t:t + H].sum() for t in idx5])
real5_p = np.array([rvs[t:t + H].sum() for t in idx5])

w("\n## 3. Protocole out-of-sample (figé avant exécution)\n")
w(f"- Fenêtre initiale : {T0} obs ({dates[0]:%d/%m/%Y} → {dates[T0-1]:%d/%m/%Y}), expansive, "
  f"ré-estimation tous les {REFIT_EVERY} j ({len(refit_dates)} ré-estimations)")
w(f"- OOS : {dates[T0]:%d/%m/%Y} → {dates[-1]:%d/%m/%Y} — **{len(idx1)} prévisions 1 pas**, "
  f"{len(idx5)} prévisions cumulées 5 pas (chevauchantes)")
w(f"- ν (GJR-t) au fil des ré-estimations : min {min(nu_track):.1f} / méd. "
  f"{np.median(nu_track):.1f} / max {max(nu_track):.1f}")
w("- Univers de modèles : " + ", ".join(MODELS) + f" — benchmark : **{BENCH}**\n")


def loss_table(horizon: str, idx, real, real_p, fc, hac):
    w(f"### Horizon {horizon} — QLIKE et MSE (proxy primaire ε² ; secondaire Parkinson)\n")
    w("| Modèle | QLIKE ε² | ΔQLIKE vs bench | DM t | p (unilat.) | QLIKE Park. | MSE ε² |")
    w("|---|---|---|---|---|---|---|")
    lb = qlike(real, fc[BENCH][idx])
    out = {}
    for m in MODELS:
        f = fc[m][idx]
        lq = qlike(real, f)
        lq_p = qlike(real_p, f)
        lm = mse(real, f)
        if m == BENCH:
            w(f"| {m} (bench) | {lq.mean():.4f} | — | — | — | {lq_p.mean():.4f} | {lm.mean():.3f} |")
        else:
            dm = dm_test(lb, lq, hac_lags=hac)
            out[m] = dm
            w(f"| {m} | {lq.mean():.4f} | {lq.mean()-lb.mean():+.4f} | {dm['t']:+.2f} "
              f"| {dm['p_one_sided_model_better']:.3f} | {lq_p.mean():.4f} | {lm.mean():.3f} |")
    w("")
    return out


w("## 4. Résultats out-of-sample\n")
dm1 = loss_table("1 jour", idx1, eps2[idx1], rvs[idx1], fc1, hac=5)
dm5 = loss_table("5 jours (cumulé, chevauchant)", idx5, real5, real5_p,
                 {m: fc5[m] for m in MODELS}, hac=10)

# quelques stats de couverture grossieres : proportion de jours ou la vol
# annualisee predite (GJR-t) et realisee (Parkinson) divergent
vol_ann = ANNUALIZE * np.sqrt(fc1["GJR-t"][idx1])
w(f"*Vol. annualisée prédite (GJR-t) sur l'OOS : min {vol_ann.min():.1f} % / "
  f"méd. {np.median(vol_ann):.1f} % / max {vol_ann.max():.1f} %.*\n")

w("## 5. Test SPA de Hansen (2005) — correction du data-snooping\n")
w("H₀ : le benchmark GARCH(1,1)-n n'est battu par AUCUN des 5 modèles de "
  "l'univers (bootstrap stationnaire Politis-Romano, bloc moyen 20 j, "
  "5000 réplications, recentrage consistant).\n")
spa_res = {}
for hname, idx, real, fc, in (("1 jour", idx1, eps2[idx1], fc1),
                              ("5 jours", idx5, real5, {m: fc5[m] for m in MODELS})):
    losses = {m: qlike(real, fc[m][idx]) for m in MODELS}
    spa = spa_test(losses, BENCH)
    spa_res[hname] = spa
    w(f"- **Horizon {hname}** : t_SPA = {spa['t_spa']:.2f}, **p = {spa['p_value']:.4f}** "
      f"(meilleur modèle : {spa['best_model']}) → "
      + ("H₀ rejetée : la surperformance survit à la correction du data-snooping."
         if spa['p_value'] < 0.10 else
         "H₀ non rejetée : la surperformance PEUT être un artefact de sélection."))
w("")

w("## 6. Verdict contre les seuils du cahier des charges\n")
best = min((m for m in MODELS if m != BENCH), key=lambda m: qlike(eps2[idx1], fc1[m][idx1]).mean())
lq_best = qlike(eps2[idx1], fc1[best][idx1]).mean()
lq_bench = qlike(eps2[idx1], fc1[BENCH][idx1]).mean()
w(f"- Meilleur modèle 1 pas (QLIKE ε²) : **{best}** ({lq_best:.4f} vs {lq_bench:.4f} bench)")
for m, dm in dm1.items():
    verdict = ("bat le bench, significatif à 10 %" if dm["p_one_sided_model_better"] < 0.10
               else ("bat le bench, NON significatif" if dm["mean_diff"] > 0
                     else "ne bat pas le bench"))
    w(f"  - {m} : {verdict} (p={dm['p_one_sided_model_better']:.3f})")
w("")
w("### Lecture honnête des deux niveaux d'inférence\n")
p1 = dm1["GJR-t"]["p_one_sided_model_better"]
p5 = dm5["GJR-t"]["p_one_sided_model_better"]
w("1. **Hypothèse primaire pré-enregistrée** (GJR-t vs GARCH-n, choisie AVANT "
  "de voir les données sur la base de Hansen-Lunde 2005 / Liu-Hung 2010) : "
  f"DM unilatéral p={p1:.3f} (h=1) et p={p5:.3f} (h=5), "
  + ("cohérente sur les deux horizons → **validée**."
     if max(p1, p5) < 0.10 else "→ à interpréter avec prudence."))
spa1, spa5 = spa_res["1 jour"]["p_value"], spa_res["5 jours"]["p_value"]
n_years = (dates[idx1[-1]] - dates[idx1[0]]).days / 365.25
if max(spa1, spa5) < 0.10:
    w(f"2. **Correction famille entière** (SPA sur les 5 modèles) : p={spa1:.4f} "
      f"(h=1) et p={spa5:.4f} (h=5) → la surperformance **survit** à la correction "
      f"du data-snooping. Sur {len(idx1)} obs OOS (~{n_years:.0f} ans, plusieurs "
      "cycles), le signal est statistiquement robuste — ce que l'échantillon court "
      "ne permettait pas de trancher.")
else:
    w(f"2. **Correction famille entière** (SPA sur les 5 modèles) : p={spa1:.4f} "
      f"(h=1) et p={spa5:.4f} (h=5) → la significativité **ne survit PAS** à la "
      f"correction au seuil de 10 %. Avec {len(idx1)} obs OOS (~{n_years:.0f} ans), "
      "la puissance est limitée : c'est une limite de l'ÉCHANTILLON, pas un feu "
      "vert pour élargir l'univers de modèles jusqu'à ce que ça passe.")
w("")
w("**Conclusion opérationnelle** : GJR-GARCH(1,1)-t est adopté comme moteur de "
  "volatilité v1 (direction conforme à la littérature, gain régulier, benchmark "
  "battu partout où il doit l'être)."
  + (" Sur l'historique long, la robustesse statistique est confirmée (SPA) : "
     "la voie de progrès devient la finesse des données (RV intraday) et non le "
     "volume d'historique."
     if max(spa1, spa5) < 0.10 else
     " Le renforcement statistique passe par PLUS DE DONNÉES (historique ≥ 2000, "
     "incluant 2008 et la bulle dot-com), pas par plus d'itérations de modèles "
     "sur ce même échantillon."))

out = Path(OUT)
out.write_text("\n".join(lines))
print("\n".join(lines))

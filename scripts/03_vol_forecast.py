"""Moteur de prévision de variance 21j — walk-forward honnête.

Cible: variance réalisée close-to-close cumulée t+1..t+21, annualisée en (%vol)^2
       (= jambe flottante d'un swap de variance 1 mois).

Modèles comparés (tous ré-estimés tous les 21 jours, fenêtre expansive):
  rw21     : RV des 21 derniers jours (random walk sur RV)
  ewma     : RiskMetrics lambda=0.94
  garch    : GARCH(1,1)-normal, prévision analytique cumulée 21 pas  <- BENCHMARK
  gjr_t    : GJR-GARCH(1,1)-t, prévision analytique cumulée 21 pas
  har      : HAR log-RV (composantes 1/5/22j, estimateur Yang-Zhang)
  harx     : HAR + log(VXN)
  vxn_reg  : log RV ~ a + b log VXN (VXN débiaisé)
  vxn_raw  : VXN^2 brut (sans débiaisage)

Anti-look-ahead:
- prédicteurs à t = information jusqu'à la clôture t
- entraînement HAR/regressions: seuls les couples dont la cible est
  entièrement réalisée à t (s <= t-21) — purge des chevauchements
- évaluation: QLIKE + DM (Newey-West lag 42) vs GARCH(1,1)
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from arch import arch_model
import warnings
warnings.filterwarnings("ignore")

DATA = "/home/user/Quant-Trade/data"
H = 21
REFIT = 21
MIN_TRAIN = 750  # ~3 ans avant la première prévision

df = pd.read_parquet(f"{DATA}/master.parquet")
df["ret"] = np.log(df["ndx_close"]).diff()
df = df.dropna(subset=["ret"])

# --- estimateur Yang-Zhang quotidien (variance quotidienne, unités log-ret^2) ---
o, h, l, c = [np.log(df[k]) for k in ["ndx_open", "ndx_high", "ndx_low", "ndx_close"]]
ovn = (o - c.shift()) ** 2                      # gap overnight
oc = (c - o) ** 2                                # open-to-close
rs = (h - c) * (h - o) + (l - c) * (l - o)       # Rogers-Satchell
k = 0.34
df["yz_var"] = ovn + k * oc + (1 - k) * rs
df["yz_var"] = df["yz_var"].clip(lower=1e-10)

# cible: variance annualisée (%^2) close-to-close sur t+1..t+H
ANN = 252 / H * 100 ** 2
df["target_var"] = df["ret"].pow(2).rolling(H).sum().shift(-H) * ANN

# composantes HAR (annualisées, %^2) — info jusqu'à t inclus
yz_ann = df["yz_var"] * 252 * 100 ** 2
df["har_d"] = yz_ann
df["har_w"] = yz_ann.rolling(5).mean()
df["har_m"] = yz_ann.rolling(22).mean()
df["rw21_var"] = df["ret"].pow(2).rolling(H).sum() * ANN

d = df.dropna(subset=["vxn", "har_m", "rw21_var"]).copy()
dates = d.index
n = len(d)
ret_pct = (d["ret"] * 100).values
lvxn = np.log(d["vxn"] ** 2).values           # log variance implicite (annualisée %^2)
lhar = np.log(d[["har_d", "har_w", "har_m"]].values)
ltarget = np.log(d["target_var"].values)       # NaN sur les H derniers jours

# EWMA RiskMetrics (récursif, pas de look-ahead)
lam = 0.94
ew = np.empty(n)
ew[0] = ret_pct[0] ** 2
for i in range(1, n):
    ew[i] = lam * ew[i - 1] + (1 - lam) * ret_pct[i] ** 2

preds = {m: np.full(n, np.nan) for m in
         ["rw21", "ewma", "garch", "gjr_t", "har", "harx", "vxn_reg", "vxn_raw"]}

def fit_ols(X, y):
    Xc = sm.add_constant(X)
    return sm.OLS(y, Xc).fit()

def garch_cum_var(res, horizon):
    """Somme des variances prévues sur `horizon` pas (unités %^2/jour)."""
    f = res.forecast(horizon=horizon, reindex=False)
    return float(f.variance.values[-1].sum())

har_coefs = harx_coefs = vxn_coefs = None
garch_res = gjr_res = None
smear_har = smear_harx = smear_vxn = 1.0

t0 = MIN_TRAIN
for t in range(t0, n):
    if (t - t0) % REFIT == 0:
        # ensemble d'entraînement purgé: cibles réalisées à t => s <= t-H
        idx = np.arange(0, t - H)
        y_tr = ltarget[idx]
        ok = ~np.isnan(y_tr)
        idx, y_tr = idx[ok], y_tr[ok]

        m_har = fit_ols(lhar[idx], y_tr)
        har_coefs = m_har.params
        smear_har = float(np.mean(np.exp(m_har.resid)))
        Xx = np.column_stack([lhar[idx], lvxn[idx]])
        m_harx = fit_ols(Xx, y_tr)
        harx_coefs = m_harx.params
        smear_harx = float(np.mean(np.exp(m_harx.resid)))
        m_vxn = fit_ols(lvxn[idx].reshape(-1, 1), y_tr)
        vxn_coefs = m_vxn.params
        smear_vxn = float(np.mean(np.exp(m_vxn.resid)))

        r_tr = ret_pct[: t + 1]
        garch_res = arch_model(r_tr, mean="Constant", vol="GARCH", p=1, q=1,
                               dist="normal").fit(disp="off", show_warning=False)
        gjr_res = arch_model(r_tr, mean="Constant", vol="GARCH", p=1, o=1, q=1,
                             dist="t").fit(disp="off", show_warning=False)
        garch_om = garch_res
        gjr_om = gjr_res
    else:
        # entre deux réajustements: re-filtrer les nouvelles données avec
        # les paramètres figés (fixed-parameter update)
        r_tr = ret_pct[: t + 1]
        garch_om = arch_model(r_tr, mean="Constant", vol="GARCH", p=1, q=1,
                              dist="normal").fix(garch_res.params.values)
        gjr_om = arch_model(r_tr, mean="Constant", vol="GARCH", p=1, o=1, q=1,
                            dist="t").fix(gjr_res.params.values)

    preds["rw21"][t] = d["rw21_var"].values[t]
    preds["ewma"][t] = ew[t] * 252
    preds["garch"][t] = garch_cum_var(garch_om, H) * (252 / H)
    preds["gjr_t"][t] = garch_cum_var(gjr_om, H) * (252 / H)
    preds["har"][t] = np.exp(har_coefs[0] + lhar[t] @ har_coefs[1:]) * smear_har
    xx = np.concatenate([lhar[t], [lvxn[t]]])
    preds["harx"][t] = np.exp(harx_coefs[0] + xx @ harx_coefs[1:]) * smear_harx
    preds["vxn_reg"][t] = np.exp(vxn_coefs[0] + vxn_coefs[1] * lvxn[t]) * smear_vxn
    preds["vxn_raw"][t] = np.exp(lvxn[t])

out = pd.DataFrame(preds, index=dates)
out["target_var"] = d["target_var"].values
out["vxn"] = d["vxn"].values
out["ret"] = d["ret"].values
out = out.iloc[t0:]
out.to_parquet(f"{DATA}/vol_forecasts.parquet")

# --- évaluation ---
ev = out.dropna(subset=["target_var"])
y = ev["target_var"].values

def qlike(pred, real):
    r = real / pred
    return r - np.log(r) - 1

print(f"évaluation: {ev.index[0].date()} -> {ev.index[-1].date()} ({len(ev)} jours, "
      f"fenêtres 21j chevauchantes, DM avec NW lag 42)")
print(f"\n{'modèle':10s} {'QLIKE':>8s} {'RMSE(vol)':>10s} {'biais(vol)':>10s} "
      f"{'DM vs garch':>12s} {'p':>7s}")
bench = qlike(ev["garch"].values, y)
for mname in ["rw21", "ewma", "garch", "gjr_t", "har", "harx", "vxn_reg", "vxn_raw"]:
    p = ev[mname].values
    ql = qlike(p, y)
    vol_p, vol_y = np.sqrt(p), np.sqrt(y)
    rmse = np.sqrt(np.mean((vol_p - vol_y) ** 2))
    bias = np.mean(vol_p - vol_y)
    if mname == "garch":
        print(f"{mname:10s} {ql.mean():8.4f} {rmse:10.2f} {bias:+10.2f} {'—':>12s}")
        continue
    diff = ql - bench
    dm = sm.OLS(diff, np.ones_like(diff)).fit(cov_type="HAC", cov_kwds={"maxlags": 42})
    print(f"{mname:10s} {ql.mean():8.4f} {rmse:10.2f} {bias:+10.2f} "
          f"{dm.tvalues[0]:12.2f} {dm.pvalues[0]:7.3f}")
print("\nQLIKE: plus bas = mieux. DM<0 = bat le GARCH(1,1).")

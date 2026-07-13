"""Diagnostics de la prime de risque de variance (VRP) sur le NASDAQ-100.

VRP_t = VXN_t^2 - RV_{t->t+21}^2  (points de variance annualisée, vol en %)

Convention Carr-Wu (2009): la jambe fixe est la variance implicite (VXN^2),
la jambe flottante la variance réalisée sur les 21 jours ouvrés suivants.
VRP > 0 = le vendeur de variance encaisse la prime.

P&L normalisé vega d'un swap de variance court: (IV^2 - RV^2) / (2*IV)
(en points de vol par unité de vega notional).

Stats avec erreurs Newey-West (lag 21: fenêtres chevauchantes).
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

DATA = "/home/user/Quant-Trade/data"
H = 21  # horizon du swap en jours ouvrés (~1 mois calendaire, convention VXN 30j)

df = pd.read_parquet(f"{DATA}/master.parquet")
df["ret"] = np.log(df["ndx_close"]).diff()

# RV réalisée annualisée en % sur les H prochains jours (fenêtre t+1..t+H)
rv_fwd = (df["ret"].pow(2).rolling(H).sum().shift(-H) * (252 / H)) ** 0.5 * 100
d = pd.DataFrame({"iv": df["vxn"], "rv_fwd": rv_fwd}).dropna()
d["vrp_var"] = d["iv"] ** 2 - d["rv_fwd"] ** 2          # points de variance
d["pnl_vega"] = d["vrp_var"] / (2 * d["iv"])             # points de vol / vega

def nw_tstat(x, lags=H):
    x = np.asarray(x, dtype=float)
    m = sm.OLS(x, np.ones_like(x)).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return m.params[0], m.tvalues[0]

print(f"échantillon: {d.index[0].date()} -> {d.index[-1].date()}  ({len(d)} jours)")
print(f"\n=== VRP inconditionnelle (jambe fixe VXN^2, flottante RV^2 fwd {H}j) ===")
mean_vrp, t_vrp = nw_tstat(d["vrp_var"])
mean_pnl, t_pnl = nw_tstat(d["pnl_vega"])
print(f"VRP moyenne: {mean_vrp:+.1f} pts de variance  (t NW = {t_vrp:.2f})")
print(f"VRP médiane: {d['vrp_var'].median():+.1f} | % jours > 0: {(d['vrp_var'] > 0).mean():.1%}")
print(f"P&L vega moyen (short): {mean_pnl:+.3f} pts de vol  (t NW = {t_pnl:.2f})")
print(f"IV moyenne: {d['iv'].mean():.1f} | RV fwd moyenne: {d['rv_fwd'].mean():.1f}")

print("\n=== ratio IV/RV (biais multiplicatif) ===")
lr = np.log(d["iv"] / d["rv_fwd"])
m, t = nw_tstat(lr)
print(f"log(IV/RV) moyen: {m:+.4f} (t NW = {t:.2f})  -> IV/RV ~ {np.exp(m):.3f}")

print("\n=== par année (P&L vega moyen, % jours VRP>0) ===")
by_y = d.groupby(d.index.year).agg(pnl=("pnl_vega", "mean"),
                                   pos=("vrp_var", lambda x: (x > 0).mean()),
                                   iv=("iv", "mean"), rv=("rv_fwd", "mean"))
print(by_y.round(2).to_string())

print("\n=== queues: pires fenêtres de 21j pour le vendeur ===")
worst = d.nsmallest(8, "pnl_vega")[["iv", "rv_fwd", "pnl_vega"]]
print(worst.round(1).to_string())
print("\npercentiles P&L vega:",
      {p: round(float(np.percentile(d['pnl_vega'], p)), 2) for p in [1, 5, 25, 50, 75, 95, 99]})

# Sharpe d'une stratégie mensuelle non-chevauchante (short var systématique)
print("\n=== stratégie mensuelle non-chevauchante (short 1 swap/mois, 3 tranches) ===")
sharpes = []
for start in range(0, 3):
    nol = d.iloc[start::H]  # fenêtres non chevauchantes
    s = nol["pnl_vega"].mean() / nol["pnl_vega"].std() * np.sqrt(12)
    sharpes.append(s)
print(f"Sharpe annualisé (moyenne des 3 tranches décalées): {np.mean(sharpes):.2f} "
      f"(min {min(sharpes):.2f}, max {max(sharpes):.2f})")
skew = d["pnl_vega"].skew()
kurt = d["pnl_vega"].kurt()
print(f"skew: {skew:.2f}, excess kurtosis: {kurt:.1f}  <- le prix de la prime")

d.to_parquet(f"{DATA}/vrp_daily.parquet")

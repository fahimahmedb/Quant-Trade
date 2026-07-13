"""Ablation: la règle `prop` paie-t-elle grâce au modèle HAR-X, ou n'importe
quel dimensionnement inverse-risque ferait-il pareil ?

Même règle w = clip(IV^2/E[RV^2] - 1, 0, 1) en remplaçant E[RV^2] par chaque
prévision, + une règle sans modèle w = k/IV^2 (inverse variance implicite,
k calibré pour expo moyenne ~0.3 sur données PASSÉES uniquement — ici fixé
ex ante à la médiane historique de IV^2 au premier point, pas optimisé).

+ stabilité par sous-période et IC bootstrap stationnaire (Politis-Romano)
sur la différence de Sharpe prop(harx) vs uncond.
"""
import numpy as np
import pandas as pd

DATA = "/home/user/Quant-Trade/data"
H = 21
COST = 0.5
rng = np.random.default_rng(42)

fc = pd.read_parquet(f"{DATA}/vol_forecasts.parquet").dropna(subset=["target_var"])
iv2 = fc["vxn"] ** 2
rv2 = fc["target_var"]
pnl = (iv2 - rv2) / (2 * fc["vxn"])

def prop_w(exp_rv2):
    return (iv2 / exp_rv2 - 1).clip(0, 1)

# règle sans modèle: inverse de la variance implicite, échelle fixée ex ante
w_inviv = (400.0 / iv2).clip(0, 1)  # 400 = (vol 20%)^2, constante de bon sens ex ante

variants = {
    "uncond": pd.Series(1.0, index=fc.index),
    "prop_harx": prop_w(fc["harx"]),
    "prop_vxnraw": prop_w(fc["vxn_raw"]),
    "prop_rw21": prop_w(fc["rw21"]),
    "prop_garch": prop_w(fc["garch"]),
    "inv_iv2": w_inviv,
}

def tranche_stats(w, cost=COST, sl=slice(None)):
    out = []
    for start in range(0, 21, 7):
        idx = fc.index[start::H]
        net = (w.reindex(idx) * pnl.reindex(idx) - cost * w.reindex(idx).abs()).loc[sl]
        out.append(net)
    return out

print(f"{'variante':13s} {'expo':>5s} {'Sharpe':>7s} {'pire mois':>10s} "
      f"{'SR 04-14':>9s} {'SR 15-26':>9s}")
for name, w in variants.items():
    tr = tranche_stats(w)
    sr = np.mean([t.mean() / t.std() * np.sqrt(12) for t in tr])
    worst = min(t.min() for t in tr)
    sr1 = np.mean([t.loc[:"2014"].mean() / t.loc[:"2014"].std() * np.sqrt(12) for t in tr])
    sr2 = np.mean([t.loc["2015":].mean() / t.loc["2015":].std() * np.sqrt(12) for t in tr])
    print(f"{name:13s} {w.mean():5.2f} {sr:7.2f} {worst:+10.1f} {sr1:9.2f} {sr2:9.2f}")

# --- bootstrap stationnaire sur la diff de Sharpe (prop_harx vs uncond, tranche 0) ---
def sharpe(x):
    return x.mean() / x.std() * np.sqrt(12)

net_u = tranche_stats(variants["uncond"])[0].values
net_p = tranche_stats(variants["prop_harx"])[0].values
n = len(net_u)
p_geom = 1 / 6  # blocs moyens de 6 mois
diffs = []
for _ in range(5000):
    idx = []
    while len(idx) < n:
        s = rng.integers(0, n)
        L = rng.geometric(p_geom)
        idx.extend([(s + j) % n for j in range(L)])
    idx = np.array(idx[:n])
    bu, bp = net_u[idx], net_p[idx]
    diffs.append(sharpe(pd.Series(bp)) - sharpe(pd.Series(bu)))
diffs = np.array(diffs)
d_obs = sharpe(pd.Series(net_p)) - sharpe(pd.Series(net_u))
print(f"\ndiff Sharpe prop_harx - uncond: {d_obs:+.2f}")
print(f"IC bootstrap stationnaire 90%: [{np.percentile(diffs,5):+.2f}, "
      f"{np.percentile(diffs,95):+.2f}] ; P(diff<=0) = {(diffs<=0).mean():.3f}")

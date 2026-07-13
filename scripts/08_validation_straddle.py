"""Validation statistique de la réplique straddle (cas central honnête:
haircut IV 0.95, coût 0.5 pt de vol) + test du filtre de compression de prime.

- DSR avec comptage honnête N=13 (10 précédents + straddle uncond/prop
  + filtre de tendance ci-dessous).
- Bootstrap stationnaire: diff de Sharpe prop vs uncond (straddle).
- Filtre tendance de prime (1 essai, compté): w=0 si la VRP réalisée moyenne
  des 252 derniers jours (entièrement observable à t) est < 0.
"""
import numpy as np
import pandas as pd
from scipy import stats
import importlib.util

DATA = "/home/user/Quant-Trade/data"
H = 21
N_TRIALS = 13
rng = np.random.default_rng(7)

spec = importlib.util.spec_from_file_location(
    "rep", "/home/user/Quant-Trade/scripts/07_options_replication.py")

# on recharge les briques sans exécuter le bloc de rapport du script 07
master = pd.read_parquet(f"{DATA}/master.parquet")
fc = pd.read_parquet(f"{DATA}/vol_forecasts.parquet")
rates = pd.read_csv(f"{DATA}/dtb3.csv", parse_dates=["observation_date"],
                    index_col="observation_date")["DTB3"]
rates = pd.to_numeric(rates, errors="coerce").reindex(master.index).ffill() / 100
S_all, iv_all = master["ndx_close"], master["vxn"]
SQ2PI = np.sqrt(2 * np.pi)
Q_DIV, HEDGE_HS = 0.007, 1.5e-4

def bs_straddle(S, K, T, iv, r, q):
    T = max(T, 1e-9)
    v = iv * np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * iv ** 2) * T) / v
    d2 = d1 - v
    eq, er = np.exp(-q * T), np.exp(-r * T)
    price = (S * eq * stats.norm.cdf(d1) - K * er * stats.norm.cdf(d2)
             + K * er * stats.norm.cdf(-d2) - S * eq * stats.norm.cdf(-d1))
    delta = eq * (2 * stats.norm.cdf(d1) - 1)
    vega = 2 * S * eq * np.exp(-d1 ** 2 / 2) / SQ2PI * np.sqrt(T) / 100
    return price, delta, vega

def run_tranche(entries, haircut):
    idx_all = master.index
    pos = {dt: i for i, dt in enumerate(idx_all)}
    out = {}
    for t in entries:
        i0 = pos[t]
        if i0 + H >= len(idx_all):
            continue
        S0 = K = S_all.iloc[i0]
        iv0 = iv_all.iloc[i0] / 100 * haircut
        prem0, d0, v0 = bs_straddle(S0, K, H / 252, iv0, rates.iloc[i0], Q_DIV)
        n = 1.0 / v0
        pnl = -abs(d0) * n * S0 * HEDGE_HS
        prev_p, prev_d = prem0, d0
        for j in range(1, H + 1):
            Su = S_all.iloc[i0 + j]
            if j < H:
                cu, du, _ = bs_straddle(Su, K, (H - j) / 252,
                                        iv_all.iloc[i0 + j] / 100 * haircut,
                                        rates.iloc[i0 + j], Q_DIV)
            else:
                cu, du = abs(Su - K), 0.0
            pnl += n * (-(cu - prev_p) + prev_d * (Su - S_all.iloc[i0 + j - 1]))
            pnl -= abs(du - prev_d) * n * Su * HEDGE_HS
            prev_p, prev_d = cu, du
        out[t] = pnl
    return pd.Series(out)

fc_ok = fc.dropna(subset=["harx"])
w_prop = (fc_ok["vxn"] ** 2 / fc_ok["harx"] - 1).clip(0, 1)

# filtre de tendance de prime, entièrement observable à t
ret = np.log(master["ndx_close"]).diff()
rv2_back = ret.pow(2).rolling(H).sum() * (252 / H) * 100 ** 2   # fenêtre s-20..s
vrp_realized = (master["vxn"] ** 2).shift(H) - rv2_back          # décision prise à s-21
trend = vrp_realized.rolling(252).mean().reindex(fc_ok.index)
w_trend = w_prop * (trend > 0).astype(float)

HAIRCUT, COST = 0.95, 0.5
nets = {}
for name, w_src in [("uncond", None), ("prop", w_prop), ("prop+trend", w_trend)]:
    per_t = []
    for start in [0, 7, 14]:
        entries = fc_ok.index[start::H]
        g = run_tranche(entries, HAIRCUT)
        w = pd.Series(1.0, index=g.index) if w_src is None else w_src.reindex(g.index)
        per_t.append(w * g - COST * w.abs())
    nets[name] = per_t

def dsr(sr_ann, n_obs, skew, kurt, n_trials, periods=12):
    sr = sr_ann / np.sqrt(periods)
    e = 0.5772156649
    sr0 = np.sqrt(1 / n_obs) * ((1 - e) * stats.norm.ppf(1 - 1 / n_trials)
                                + e * stats.norm.ppf(1 - 1 / (n_trials * np.e)))
    denom = np.sqrt((1 - skew * sr + (kurt - 1) / 4 * sr ** 2) / (n_obs - 1))
    return stats.norm.cdf((sr - sr0) / denom)

print(f"=== straddle haircut {HAIRCUT}, coût {COST} pt vol (cas central honnête) ===")
print(f"{'règle':11s} {'expo':>5s} {'moy/mois':>9s} {'Sharpe':>7s} {'pire mois':>10s} "
      f"{'SR 04-14':>9s} {'SR 15-26':>9s} {'DSR(13)':>8s}")
for name, per_t in nets.items():
    mu = np.mean([t.mean() for t in per_t])
    sr = np.mean([t.mean() / t.std() * np.sqrt(12) for t in per_t])
    worst = min(t.min() for t in per_t)
    s1 = np.mean([t.loc[:"2014"].mean() / t.loc[:"2014"].std() * np.sqrt(12) for t in per_t])
    s2 = np.mean([t.loc["2015":].mean() / t.loc["2015":].std() * np.sqrt(12) for t in per_t])
    sk = np.mean([t.skew() for t in per_t])
    ku = np.mean([t.kurt() + 3 for t in per_t])
    n = len(per_t[0])
    expo = {"uncond": 1.0, "prop": float(w_prop.mean()),
            "prop+trend": float(w_trend.mean())}[name]
    print(f"{name:11s} {expo:5.2f} {mu:+9.3f} {sr:7.2f} {worst:+10.1f} "
          f"{s1:9.2f} {s2:9.2f} {dsr(sr, n, sk, ku, N_TRIALS):8.3f}")

# bootstrap stationnaire diff Sharpe prop vs uncond (tranche 0)
def sharpe(x): return x.mean() / x.std() * np.sqrt(12)
nu, npr = nets["uncond"][0].values, nets["prop"][0].values
n = len(nu)
diffs = []
for _ in range(5000):
    idx = []
    while len(idx) < n:
        s0 = rng.integers(0, n)
        L = rng.geometric(1 / 6)
        idx.extend([(s0 + j) % n for j in range(L)])
    idx = np.array(idx[:n])
    diffs.append(sharpe(pd.Series(npr[idx])) - sharpe(pd.Series(nu[idx])))
diffs = np.array(diffs)
d_obs = sharpe(pd.Series(npr)) - sharpe(pd.Series(nu))
print(f"\ndiff Sharpe prop - uncond (straddle): {d_obs:+.2f} | "
      f"IC90 bootstrap [{np.percentile(diffs, 5):+.2f}, {np.percentile(diffs, 95):+.2f}] "
      f"| P(diff<=0) = {(diffs <= 0).mean():.3f}")

"""Réplique tradeable: vente mensuelle d'un straddle ATM NDX (européen,
cash-settled), delta-hedgé quotidiennement, tenu jusqu'à l'échéance (21j).

C'est le test qui tue ou sauve: le Sharpe idéalisé du swap de variance
(0.58 prop / 0.36 uncond) survit-il aux frictions réelles ?

Hypothèses (conservatrices, sensibilités rapportées):
- IV d'entrée = VXN * haircut (l'ATM 1 mois cote sous l'indice de variance
  qui inclut le skew; haircut base 0.97, sensibilité 1.00/0.95) -> on REÇOIT
  moins de prime que VXN.
- Marks quotidiens à IV_u = VXN_u * haircut (n'affecte que les deltas de
  hedge, pas le P&L total tenu à échéance).
- Coût d'entrée: c_opt pts de vol * vega d'entrée (bid-ask straddle ATM,
  base 0.5, grille 0-2). Pas de coût de sortie (settlement cash).
- Hedge: futures NQ à la clôture, demi-spread 1.5 bp * |Delta_change| * S.
- Taux: DTB3 (T-bill 3M) quotidien réel; dividendes NDX q=0.7%/an constant.
- Vega d'entrée normalisé à 1 (P&L en pts de vol par unité de vega,
  directement comparable aux scripts 04/05).

Position: w=1 (uncond) et w=prop=clip(VXN^2/HARX - 1, 0, 1) (même signal
que le script 04 — AUCUN nouveau paramètre, pas d'essai supplémentaire).
"""
import numpy as np
import pandas as pd
from scipy import stats

DATA = "/home/user/Quant-Trade/data"
H = 21
Q_DIV = 0.007
HEDGE_HALF_SPREAD = 1.5e-4  # 1.5 bp par transaction de hedge

master = pd.read_parquet(f"{DATA}/master.parquet")
fc = pd.read_parquet(f"{DATA}/vol_forecasts.parquet")
rates = pd.read_csv(f"{DATA}/dtb3.csv", parse_dates=["observation_date"],
                    index_col="observation_date")["DTB3"]
rates = pd.to_numeric(rates, errors="coerce").reindex(master.index).ffill() / 100

S_all = master["ndx_close"]
iv_all = master["vxn"]

SQ2PI = np.sqrt(2 * np.pi)

def bs_straddle(S, K, T, iv, r, q):
    """Prix et delta d'un straddle européen; vega en $ par pt de vol (1%)."""
    T = max(T, 1e-9)
    v = iv * np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * iv ** 2) * T) / v
    d2 = d1 - v
    eq, er = np.exp(-q * T), np.exp(-r * T)
    call = S * eq * stats.norm.cdf(d1) - K * er * stats.norm.cdf(d2)
    put = K * er * stats.norm.cdf(-d2) - S * eq * stats.norm.cdf(-d1)
    delta = eq * (2 * stats.norm.cdf(d1) - 1)
    vega = 2 * S * eq * np.exp(-d1 ** 2 / 2) / SQ2PI * np.sqrt(T) / 100
    return call + put, delta, vega

def run_tranche(entries, haircut, c_opt):
    """P&L net mensuel (pts de vol / vega) par date d'entrée."""
    idx_all = master.index
    pos = {dt: i for i, dt in enumerate(idx_all)}
    out = {}
    for t in entries:
        i0 = pos[t]
        if i0 + H >= len(idx_all):
            continue
        days = idx_all[i0:i0 + H + 1]
        S0, K = S_all.iloc[i0], S_all.iloc[i0]
        r0 = rates.iloc[i0]
        iv0 = iv_all.iloc[i0] / 100 * haircut
        prem0, delta0, vega0 = bs_straddle(S0, K, H / 252, iv0, r0, Q_DIV)
        n = 1.0 / vega0  # vega d'entrée = 1 pt de vol
        pnl, hedge_cost = 0.0, 0.0
        prev_price, prev_delta = prem0, delta0
        hedge_cost += abs(prev_delta) * n * S0 * HEDGE_HALF_SPREAD
        for j in range(1, H + 1):
            Su = S_all.iloc[i0 + j]
            Tu = (H - j) / 252
            ivu = iv_all.iloc[i0 + j] / 100 * haircut
            ru = rates.iloc[i0 + j]
            if j < H:
                cu, du, _ = bs_straddle(Su, K, Tu, ivu, ru, Q_DIV)
            else:
                cu, du = abs(Su - K), 0.0  # settlement intrinsèque
            pnl += n * (-(cu - prev_price) + prev_delta * (Su - S_all.iloc[i0 + j - 1]))
            hedge_cost += abs(du - prev_delta) * n * Su * HEDGE_HALF_SPREAD
            prev_price, prev_delta = cu, du
        out[t] = pnl - hedge_cost - c_opt
    return pd.Series(out)

fc_ok = fc.dropna(subset=["harx"])
w_prop = (fc_ok["vxn"] ** 2 / fc_ok["harx"] - 1).clip(0, 1)

def stats_line(net):
    sr = net.mean() / net.std() * np.sqrt(12)
    return net.mean(), sr, net.min(), net.skew()

print("=== straddle ATM delta-hedgé, haircut IV 0.97, coût option 0.5 pt vol ===")
print(f"{'règle':8s} {'moy/mois':>9s} {'Sharpe':>7s} {'pire mois':>10s} {'skew':>6s} "
      f"{'SR 04-14':>9s} {'SR 15-26':>9s}")
base = {}
for name in ["uncond", "prop"]:
    per_tranche = []
    for start in [0, 7, 14]:
        entries = fc_ok.index[start::H]
        gross = run_tranche(entries, 0.97, 0.5)
        w = pd.Series(1.0, index=gross.index) if name == "uncond" \
            else w_prop.reindex(gross.index)
        # coût option proportionnel à l'exposition
        gross_c0 = run_tranche(entries, 0.97, 0.0)
        net = w * gross_c0 - 0.5 * w.abs()
        per_tranche.append(net)
    base[name] = per_tranche
    mu = np.mean([t.mean() for t in per_tranche])
    sr = np.mean([t.mean() / t.std() * np.sqrt(12) for t in per_tranche])
    worst = min(t.min() for t in per_tranche)
    sk = np.mean([t.skew() for t in per_tranche])
    s1 = np.mean([t.loc[:"2014"].mean() / t.loc[:"2014"].std() * np.sqrt(12)
                  for t in per_tranche])
    s2 = np.mean([t.loc["2015":].mean() / t.loc["2015":].std() * np.sqrt(12)
                  for t in per_tranche])
    print(f"{name:8s} {mu:+9.3f} {sr:7.2f} {worst:+10.1f} {sk:6.1f} {s1:9.2f} {s2:9.2f}")

print("\n=== crises (P&L net/mois, tranche 0) ===")
for label, (a, b) in {"2008": ("2008-01", "2008-12"), "covid": ("2020-02", "2020-04"),
                      "2022": ("2022-01", "2022-12")}.items():
    u = base["uncond"][0].loc[a:b].mean()
    p = base["prop"][0].loc[a:b].mean()
    print(f"{label:8s} uncond {u:+7.2f} | prop {p:+7.2f}")

print("\n=== sensibilité: Sharpe (moy 3 tranches) selon coût option (pts vol) ===")
print(f"{'règle':8s} {'haircut':>8s}" + "".join(f"{c:>7.2f}" for c in [0.0, 0.5, 1.0, 1.5, 2.0]))
for name in ["uncond", "prop"]:
    for hc in [1.00, 0.97, 0.95]:
        srs = []
        for c in [0.0, 0.5, 1.0, 1.5, 2.0]:
            vals = []
            for start in [0, 7, 14]:
                entries = fc_ok.index[start::H]
                g = run_tranche(entries, hc, 0.0)
                w = pd.Series(1.0, index=g.index) if name == "uncond" \
                    else w_prop.reindex(g.index)
                net = w * g - c * w.abs()
                vals.append(net.mean() / net.std() * np.sqrt(12))
            srs.append(np.mean(vals))
        print(f"{name:8s} {hc:8.2f}" + "".join(f"{s:7.2f}" for s in srs))

# --- capital et marge: rendement sur capital engagé ---
print("\n=== passage en % de capital (prop, haircut 0.97, coût 0.5) ===")
net0 = base["prop"][0]
for vega_per_100 in [2.0, 4.0, 6.0]:
    r_cap = net0 * vega_per_100 / 100
    sr = r_cap.mean() / r_cap.std() * np.sqrt(12)
    worst = r_cap.min()
    ann = r_cap.mean() * 12
    print(f"vega {vega_per_100:.0f}/100$ de capital: rendement {ann:+.1%}/an, "
          f"Sharpe {sr:.2f}, pire mois {worst:+.1%}")

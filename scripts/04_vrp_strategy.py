"""Stratégie VRP conditionnelle vs short-variance inconditionnel.

Trades mensuels non chevauchants (3 tranches décalées de 7 jours ouvrés),
décision à l'entrée t avec l'information de clôture t, position tenue H=21j.

P&L par unité de vega: w_t * (IV_t^2 - RV_{t+1..t+H}^2) / (2*IV_t) - coût*|w_t|

Règles (N_essais documenté pour le Deflated Sharpe):
  uncond : w = 1 (benchmark)
  sign   : w = 1{VRP attendue > 0}, VRP attendue = VXN^2 - E[RV^2] (harx)
  prop   : w = clip(VRP_attendue / E[RV^2], 0, 1)  (ratio prime/risque)
  spike  : w = 1{RV_21j passée < VXN^2 en variance}  (filtre "vol qui explose")

Coûts: 0.5 pt de vol de vega à l'entrée (bid-ask swap de variance indice,
milieu de fourchette des estimations praticiens 0.3-1.0) ; sensibilité rapportée.

Deflated Sharpe (Bailey & Lopez de Prado 2014) avec le nombre TOTAL de
règles essayées dans ce projet (comptage honnête, y compris abandonnées).
"""
import numpy as np
import pandas as pd
from scipy import stats

DATA = "/home/user/Quant-Trade/data"
H = 21
COST_VOL_PTS = 0.5
N_TRIALS = 6  # uncond, sign, prop, spike + 2 variantes de seuil essayées puis abandonnées

fc = pd.read_parquet(f"{DATA}/vol_forecasts.parquet").dropna(subset=["target_var"])
iv2 = fc["vxn"] ** 2
exp_rv2 = fc["harx"]
rv2_real = fc["target_var"]
rw21 = pd.read_parquet(f"{DATA}/master.parquet")
ret = np.log(rw21["ndx_close"]).diff()
rv_past = (ret.pow(2).rolling(H).sum() * (252 / H) * 100 ** 2).reindex(fc.index)

exp_vrp = iv2 - exp_rv2
weights = {
    "uncond": pd.Series(1.0, index=fc.index),
    "sign": (exp_vrp > 0).astype(float),
    "prop": (exp_vrp / exp_rv2).clip(0, 1),
    "spike": (rv_past < iv2).astype(float),
}

pnl_gross = (iv2 - rv2_real) / (2 * fc["vxn"])  # pts de vol par vega


def dsr(sr_ann, n_obs, skew, kurt, n_trials, periods=12):
    """Deflated Sharpe Ratio -> probabilité que le vrai SR > 0."""
    sr = sr_ann / np.sqrt(periods)  # SR par période
    # SR attendu du meilleur de N essais sous H0 (Bailey-LdP eq. via EV de N gaussiennes)
    e = 0.5772156649
    var_sr = 1.0 / n_obs
    sr0 = np.sqrt(var_sr) * ((1 - e) * stats.norm.ppf(1 - 1 / n_trials)
                             + e * stats.norm.ppf(1 - 1 / (n_trials * np.e)))
    denom = np.sqrt((1 - skew * sr + (kurt - 1) / 4 * sr ** 2) / (n_obs - 1))
    return stats.norm.cdf((sr - sr0) / denom)


def evaluate(w, pnl, cost):
    rows = []
    for start in range(0, 3 * 7, 7):  # 3 tranches décalées
        sub_idx = fc.index[start::H]
        ww = w.reindex(sub_idx)
        pp = pnl.reindex(sub_idx)
        net = ww * pp - cost * ww.abs()
        rows.append(net)
    return rows


print(f"échantillon: {fc.index[0].date()} -> {fc.index[-1].date()}, "
      f"coût = {COST_VOL_PTS} pt de vol/entrée, N_essais DSR = {N_TRIALS}")
print(f"\n{'règle':8s} {'expo':>5s} {'moy/mois':>9s} {'Sharpe':>7s} {'skew':>6s} "
      f"{'pire mois':>10s} {'maxDD':>8s} {'DSR':>6s}")

results = {}
for name, w in weights.items():
    tranches = evaluate(w, pnl_gross, COST_VOL_PTS)
    stats_t = []
    for net in tranches:
        mu, sd = net.mean(), net.std()
        sr = mu / sd * np.sqrt(12) if sd > 0 else np.nan
        eq = net.cumsum()
        dd = (eq - eq.cummax()).min()
        stats_t.append((mu, sr, net.skew(), net.min(), dd, len(net),
                        net.kurt() + 3, net))
    mu = np.mean([s[0] for s in stats_t])
    sr = np.mean([s[1] for s in stats_t])
    sk = np.mean([s[2] for s in stats_t])
    worst = min(s[3] for s in stats_t)
    dd = min(s[4] for s in stats_t)
    n_obs = stats_t[0][5]
    kurt = np.mean([s[6] for s in stats_t])
    expo = float(np.mean([weights[name].mean()]))
    d = dsr(sr, n_obs, sk, kurt, N_TRIALS)
    print(f"{name:8s} {expo:5.2f} {mu:+9.3f} {sr:7.2f} {sk:6.1f} "
          f"{worst:+10.1f} {dd:8.1f} {d:6.2f}")
    results[name] = stats_t

# --- années de crise: la règle coupe-t-elle vraiment les queues ? ---
print("\n=== P&L net moyen/mois par période (tranche 0) ===")
crisis = {"2008": ("2008-01", "2008-12"), "2018Q4": ("2018-10", "2018-12"),
          "covid": ("2020-02", "2020-04"), "2022": ("2022-01", "2022-12"),
          "calme 2013-17": ("2013-01", "2017-12")}
line = f"{'période':14s}" + "".join(f"{n:>9s}" for n in weights)
print(line)
for label, (a, b) in crisis.items():
    vals = []
    for name in weights:
        net = results[name][0][7]
        vals.append(net.loc[a:b].mean() if len(net.loc[a:b]) else np.nan)
    print(f"{label:14s}" + "".join(f"{v:+9.2f}" for v in vals))

# --- sensibilité aux coûts ---
print("\n=== Sharpe (moyenne 3 tranches) selon le coût par entrée ===")
print(f"{'règle':8s}" + "".join(f"{c:>8.2f}" for c in [0.0, 0.5, 1.0, 1.5, 2.0]))
for name, w in weights.items():
    srs = []
    for c in [0.0, 0.5, 1.0, 1.5, 2.0]:
        tr = evaluate(w, pnl_gross, c)
        srs.append(np.mean([t.mean() / t.std() * np.sqrt(12) for t in tr]))
    print(f"{name:8s}" + "".join(f"{s:8.2f}" for s in srs))

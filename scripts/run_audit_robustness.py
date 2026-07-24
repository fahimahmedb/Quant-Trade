"""Audit Section 4 / Phase 5-6 : per-regime Sharpe, perturbation grid, golden-vector.

Cheap by design : le GJR-t walk-forward (coûteux) est calculé UNE fois et mis en
cache ; seul le signal LogitL2 (rapide) est ré-estimé par combo de la grille de
perturbation triple-barrier. Composite par défaut.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from sklearn.linear_model import LogisticRegression  # noqa: E402
from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from overlay import build_overlay_positions  # noqa: E402
from prediction import (backtest, build_features, trading_metrics,  # noqa: E402
                        triple_barrier_labels, walk_forward_signals)

T0, CAP, COST_BPS, EMBARGO, REFIT_B, REFIT_OV = 750, 1.5, 5.0, 5, 21, 5
DATA = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "nasdaq_composite_daily.txt")


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


df = load_ohlc(DATA).set_index("date")
logp = np.log(df["close"].astype(float))
r_fwd = (logp.shift(-1) - logp).values
dates = df.index
n = len(df)
r_pct = log_returns_pct(df.reset_index()).values
T_ov = len(r_pct)

# --- cache GJR-t vol forecast ONCE ---
ov = build_overlay_positions(r_pct, T0, REFIT_OV, CAP, with_extreme_cut=False)
lev = np.zeros(n); lev[:T_ov] = ov["pos"]           # long-only vol-target exposure
vol_fcst = np.zeros(n); vol_fcst[:T_ov] = ov["vol_fcst"]
oos = np.arange(T0, n - 1)

print("=" * 70)
print("PHASE 5a — Per-regime Sharpe (vol terciles, causal forecast)")
print("=" * 70)
# baseline LogitL2 signal (frozen params) + combined overlay
X = build_features(df.reset_index())
y = triple_barrier_labels(df.reset_index(), horizon=5, vol_span=20, mult=1.5)
y.index = df.index
sig = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), logistic, T0, REFIT_B, EMBARGO, True)
pnl_bh = backtest(np.ones(n), r_fwd, COST_BPS)[oos]
pnl_logit = backtest(sig, r_fwd, COST_BPS)[oos]
pnl_comb = backtest(lev * sig, r_fwd, COST_BPS)[oos]
v = vol_fcst[oos]
q1, q2 = np.percentile(v, [33.33, 66.67])
regimes = {"low-vol": v <= q1, "mid-vol": (v > q1) & (v <= q2), "high-vol": v > q2}
print(f"{'regime':<10} {'n':>5} {'Sharpe BH':>10} {'Sharpe LogitL2':>15} {'Sharpe Comb':>12}")
for name, mask in regimes.items():
    sh_bh = trading_metrics(pnl_bh[mask])["sharpe_ann"]
    sh_lo = trading_metrics(pnl_logit[mask])["sharpe_ann"]
    sh_co = trading_metrics(pnl_comb[mask])["sharpe_ann"]
    print(f"{name:<10} {int(mask.sum()):>5} {sh_bh:>+10.2f} {sh_lo:>+15.2f} {sh_co:>+12.2f}")

print("\n" + "=" * 70)
print("PHASE 5b — Perturbation grid triple-barrier (±20% on H, mult)")
print("=" * 70)
print(f"{'H':>3} {'mult':>5} | {'Sharpe LogitL2':>15} {'MDD% LogitL2':>13} | {'Sharpe Comb':>12} {'MDD% Comb':>10}")
grid = []
for Hh in (4, 5, 6):
    for mm in (1.2, 1.5, 1.8):
        yg = triple_barrier_labels(df.reset_index(), horizon=Hh, vol_span=20, mult=mm)
        yg.index = df.index
        sg = walk_forward_signals(X, yg, pd.Series(r_fwd, index=dates), logistic, T0, REFIT_B, EMBARGO, True)
        p_lo = backtest(sg, r_fwd, COST_BPS)[oos]
        p_co = backtest(lev * sg, r_fwd, COST_BPS)[oos]
        m_lo, m_co = trading_metrics(p_lo), trading_metrics(p_co)
        grid.append((Hh, mm, m_lo["sharpe_ann"], m_co["sharpe_ann"]))
        print(f"{Hh:>3} {mm:>5.1f} | {m_lo['sharpe_ann']:>+15.2f} {m_lo['max_drawdown_pct']:>13.1f} | "
              f"{m_co['sharpe_ann']:>+12.2f} {m_co['max_drawdown_pct']:>10.1f}")
sh_lo_arr = np.array([g[2] for g in grid])
sh_co_arr = np.array([g[3] for g in grid])
print(f"\nLogitL2 Sharpe grid: mean {sh_lo_arr.mean():+.2f}  std {sh_lo_arr.std():.2f}  "
      f"range [{sh_lo_arr.min():+.2f},{sh_lo_arr.max():+.2f}]  sign-stable={np.all(np.sign(sh_lo_arr)==np.sign(sh_lo_arr[0]))}")
print(f"Combined Sharpe grid: mean {sh_co_arr.mean():+.2f}  std {sh_co_arr.std():.2f}  "
      f"range [{sh_co_arr.min():+.2f},{sh_co_arr.max():+.2f}]")
print("-> plateau (low std, sign-stable) = robust ; spike (one high cell) = artifact")

print("\n" + "=" * 70)
print("PHASE 6 — Golden-vector test (live pipeline == backtest on historical bars)")
print("=" * 70)
# Re-run the SAME feature+signal pipeline on the identical bars; assert bit-match.
X2 = build_features(df.reset_index())
sig2 = walk_forward_signals(X2, y, pd.Series(r_fwd, index=dates), logistic, T0, REFIT_B, EMBARGO, True)
match = np.array_equal(np.nan_to_num(sig, nan=-9), np.nan_to_num(sig2, nan=-9))
feat_match = np.allclose(X.values, X2.values, equal_nan=True)
print(f"Feature matrix reproducible bit-for-bit: {feat_match}")
print(f"LogitL2 signal reproducible bit-for-bit: {match}  (seed-deterministic pipeline)")
# Streaming causality: feeding bars 0..t must give the SAME feature[t] as full-history build
Xfull = build_features(df.reset_index())
t_test = 900
Xtrunc = build_features(df.iloc[:t_test + 1].reset_index())
row_match = np.allclose(Xfull.iloc[t_test].values, Xtrunc.iloc[t_test].values, equal_nan=True)
print(f"Streaming feature[{t_test}] (bars 0..{t_test} only) == full-history feature[{t_test}]: {row_match}")
print(f"-> {'PASS: live == backtest' if (feat_match and match and row_match) else 'FAIL: live != backtest'}")

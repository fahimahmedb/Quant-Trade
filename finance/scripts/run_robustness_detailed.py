"""Exhaustive robustness audit (Phase 5-7) — driver for ROBUSTNESS_AUDIT_DETAILED.md.

Executes, on BOTH the frozen Composite (5y) and NDX (40y) samples, holding every
non-perturbed knob at its FROZEN Phase-D value (T0=750, cost 5 bps, embargo/purge 5,
H=5, barrier mult 1.5):

  1. Perturbation grid  N=27 = cap{1.2,1.5,1.8} x vol_span{15,20,25} x cut_pctl{85,90,95}
     -> Sharpe/Calmar/MDD/Return per combo + discrete Hessian curvature at frozen point.
  2. Per-regime QUINTILE tables for phases A(BuyHold) B(LogitL2) C(VolTarget) D(Combined),
     regimes = GJR-t forecast-vol quintiles; + Kruskal-Wallis + transition analysis.
  3. Cross-window 4x4 : GJR-t params fitted on {Comp-early,Comp-late,NDX-early,NDX-late}
     applied (frozen) to each of the same 4 data windows; criterion gates + var. decomp.
  4. Parameter stability : omega/alpha/beta/gamma/nu across ALL refits (NDX) + ADF +
     rolling AC + nu regime-break (>2 sigma) detection.
  6. CSCV / PBO on the 27-combo config matrix (NDX) — Bailey-Borwein-LdP-Zhu 2014.

Emits: scratchpad JSON (all numbers) + results/figures/*.png (5 heatmaps + stability plot).
GJR-t walk-forward is computed ONCE per market (reused across the 9 cap*pctl cells; only
the LogitL2 signal, cheap, is re-estimated per vol_span). NDX default refit=21.
"""
import json
import os
import sys
import warnings
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import kruskal  # noqa: E402
from statsmodels.tsa.stattools import adfuller  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from overlay import (extreme_cut, realized_ann_vol_pct,  # noqa: E402
                     vol_target_exposure)
from prediction import (backtest, build_features, trading_metrics,  # noqa: E402
                        triple_barrier_labels, walk_forward_signals)
from volatility import ANNUALIZE, fit_arch, garch_path, garch_path_fold_only, params_dict  # noqa: E402

# ------------------------------------------------------------- frozen protocol
T0, COST_BPS, EMBARGO, H, BARRIER_MULT = 750, 5.0, 5, 5, 1.5
CAPS = [1.2, 1.5, 1.8]
VOL_SPANS = [15, 20, 25]
PCTLS = [85.0, 90.0, 95.0]
FROZEN = (1.5, 20, 95.0)          # (cap, vol_span, cut_pctl) — Phase-D frozen point
SEED = 42
FIG = ROOT / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
OUTJSON = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    ROOT / "results" / "robustness_detailed_data.json")

DATASETS = {
    # label : (path, refit_gjr, refit_logit)
    "Composite": (ROOT / "data" / "nasdaq_composite_daily.txt", 5, 21),
    "NDX": (ROOT / "data" / "nasdaq100_daily.txt", 21, 21),
}


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def wf_vol_and_params(r, t0, refit_every, pctls):
    """One walk-forward GJR-t pass: vol_fcst, vol_target(const), vol_thresh{pctl}, params list."""
    T = len(r)
    vol_fcst = np.full(T, np.nan)
    vol_thresh = {pc: np.full(T, np.nan) for pc in pctls}
    vol_target_const = realized_ann_vol_pct(r[:t0])
    params = []
    for tr in range(t0, T, refit_every):
        block = range(tr, min(tr + refit_every, T))
        res = fit_arch(r[:tr], "GJR-t")
        p = params_dict(res)
        params.append({"tr": tr, **p})
        path = garch_path_fold_only(r, p, tr, gjr=True)
        vol_ann_in = ANNUALIZE * np.sqrt(path[:tr])
        th = {pc: float(np.percentile(vol_ann_in, pc)) for pc in pctls}
        for t in block:
            vol_fcst[t] = ANNUALIZE * np.sqrt(path[t])
            for pc in pctls:
                vol_thresh[pc][t] = th[pc]
    vol_target = np.full(T, np.nan)
    vol_target[t0:] = vol_target_const
    return {"vol_fcst": vol_fcst, "vol_target": vol_target,
            "vol_thresh": vol_thresh, "params": params, "vtar_const": vol_target_const}


def metrics_row(pnl):
    m = trading_metrics(pnl)
    return {k: (None if not np.isfinite(m[k]) else float(m[k]))
            for k in ("sharpe_ann", "sortino_ann", "calmar", "max_drawdown_pct",
                      "ann_return_pct", "profit_factor")}


# ---------------------------------------------------------------- per market
RESULTS = {}
for label, (path, refit_gjr, refit_logit) in DATASETS.items():
    refit_gjr = int(os.environ.get("REFIT_EVERY", refit_gjr))
    print(f"\n{'='*70}\n{label} — loading & GJR-t walk-forward (refit={refit_gjr})\n{'='*70}")
    df = load_ohlc(str(path)).set_index("date")
    close = df["close"].astype(float)
    logp = np.log(close)
    r_fwd = (logp.shift(-1) - logp).values           # t->t+1 log ret, len n
    dates = df.index
    n = len(df)
    r_pct = log_returns_pct(df.reset_index()).values  # len n-1, = 100*r_fwd[:-1]
    T_ov = len(r_pct)
    oos = np.arange(T0, n - 1)
    T_oos = len(oos)

    fc = wf_vol_and_params(r_pct, T0, refit_gjr, PCTLS)
    vol_fcst_full = np.zeros(n); vol_fcst_full[:T_ov] = np.nan_to_num(fc["vol_fcst"], nan=0.0)
    vf_oos = vol_fcst_full[oos]
    print(f"  GJR-t refits: {len(fc['params'])}   vol_target={fc['vtar_const']:.2f}% ann")

    # LogitL2 signals for each vol_span
    Xf = build_features(df.reset_index())
    sig = {}
    for vs in VOL_SPANS:
        y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=vs, mult=BARRIER_MULT)
        y.index = df.index
        sig[vs] = walk_forward_signals(Xf, y, pd.Series(r_fwd, index=dates), logistic,
                                       T0, refit_logit, EMBARGO, standardize=True)
        print(f"  LogitL2 vol_span={vs}: long {100*(sig[vs][oos]>0).mean():.0f}% of OOS")

    # exposure builder reusing the single GJR path
    def lev_for(cap, pctl, cut):
        expo = vol_target_exposure(fc["vol_fcst"], fc["vol_target"], cap)
        if cut:
            expo = extreme_cut(expo, fc["vol_fcst"], fc["vol_thresh"][pctl])
        lev = np.zeros(n); lev[:T_ov] = np.nan_to_num(expo, nan=0.0)
        return lev

    pnl_bh = backtest(np.ones(n), r_fwd, COST_BPS)[oos]

    # ---- 1. PERTURBATION GRID (27) ----
    grid = {}
    for cap in CAPS:
        for vs in VOL_SPANS:
            for pc in PCTLS:
                lev = lev_for(cap, pc, cut=True)
                pnl = backtest(lev * sig[vs], r_fwd, COST_BPS)[oos]
                grid[f"{cap}|{vs}|{pc}"] = metrics_row(pnl)
    # Hessian (discrete) of Sharpe at frozen point on each axis
    def sh(cap, vs, pc):
        return grid[f"{cap}|{vs}|{pc}"]["sharpe_ann"]
    c0, v0, p0 = FROZEN
    d2_cap = sh(1.8, v0, p0) - 2*sh(1.5, v0, p0) + sh(1.2, v0, p0)
    d2_vs = sh(c0, 25, p0) - 2*sh(c0, 20, p0) + sh(c0, 15, p0)
    d2_pc = sh(c0, v0, 95.0) - 2*sh(c0, v0, 90.0) + sh(c0, v0, 85.0)
    sh_vals = np.array([grid[k]["sharpe_ann"] for k in grid])
    hessian = {"d2_cap": d2_cap, "d2_vol_span": d2_vs, "d2_cut_pctl": d2_pc,
               "grid_mean": float(sh_vals.mean()), "grid_std": float(sh_vals.std()),
               "grid_min": float(sh_vals.min()), "grid_max": float(sh_vals.max()),
               "sign_stable": bool(np.all(np.sign(sh_vals) == np.sign(sh_vals[0])))}

    # ---- 2. PER-REGIME QUINTILE (A,B,C,D,+combined) ----
    # Phase strategies (honest mapping):
    #   A = BuyHold (Phase-A random-walk baseline return)
    #   B = LogitL2 direction signal (Phase B, rejected at DSR)
    #   C = VolTarget long-only, NO cut (Phase-C vol model driving exposure)
    #   D = VolTarget long-only + extreme cut (the DEFENSIBLE Phase-D overlay that PASSES)
    #   E = VolTarget+Cut x LogitL2 (canonical COMBINED variant, rejected — degrades D)
    cF, vF, pF = FROZEN
    pnl_phase = {
        "A_BuyHold": pnl_bh,
        "B_LogitL2": backtest(sig[vF], r_fwd, COST_BPS)[oos],
        "C_VolTarget": backtest(lev_for(cF, pF, cut=False), r_fwd, COST_BPS)[oos],
        "D_VolTargetCut": backtest(lev_for(cF, pF, cut=True), r_fwd, COST_BPS)[oos],
        "E_Combined": backtest(lev_for(cF, pF, cut=True) * sig[vF], r_fwd, COST_BPS)[oos],
    }
    qedges = np.percentile(vf_oos, [20, 40, 60, 80])
    qbin = np.digitize(vf_oos, qedges)  # 0..4
    regime_tables = {}
    kruskal_p = {}
    for ph, pnl in pnl_phase.items():
        rows = []
        groups = []
        for q in range(5):
            mask = qbin == q
            groups.append(pnl[mask])
            r_ = metrics_row(pnl[mask])
            r_["n"] = int(mask.sum())
            r_["total_return_pct"] = float(100 * (np.exp(pnl[mask].sum()) - 1))
            rows.append(r_)
        regime_tables[ph] = rows
        try:
            kruskal_p[ph] = float(kruskal(*groups).pvalue)
        except Exception:
            kruskal_p[ph] = None
    # transition analysis on quintile state series
    trans = np.zeros((5, 5))
    for a, b in zip(qbin[:-1], qbin[1:]):
        trans[a, b] += 1
    durations = []
    cur, dur = qbin[0], 1
    for s in qbin[1:]:
        if s == cur:
            dur += 1
        else:
            durations.append(dur); cur, dur = s, 1
    durations.append(dur)

    RESULTS[label] = {
        "n": int(n), "T_oos": int(T_oos),
        "oos_start": str(dates[T0].date()), "oos_end": str(dates[n-2].date()),
        "refit_gjr": refit_gjr, "n_refits": len(fc["params"]),
        "vtar_const": fc["vtar_const"],
        "grid": grid, "hessian": hessian,
        "regime_tables": regime_tables, "kruskal_p": kruskal_p,
        "regime_edges": [float(x) for x in qedges],
        "transition_counts": trans.tolist(),
        "avg_regime_duration": float(np.mean(durations)),
        "params": fc["params"],
        "bh": metrics_row(pnl_bh),
        "phase_frozen": {k: metrics_row(v) for k, v in pnl_phase.items()},
    }
    # stash arrays needed later
    RESULTS[label]["_r_pct"] = r_pct.tolist()
    RESULTS[label]["_grid_pnl_available"] = True

    # keep grid PnL matrix (T_oos x 27) in memory for CSCV (NDX only, big)
    if label == "NDX":
        M = []
        cfg_names = []
        for cap in CAPS:
            for vs in VOL_SPANS:
                for pc in PCTLS:
                    lev = lev_for(cap, pc, cut=True)
                    pnl = backtest(lev * sig[vs], r_fwd, COST_BPS)[oos]
                    M.append(pnl); cfg_names.append(f"cap{cap}_vs{vs}_p{int(pc)}")
        NDX_PNL_MATRIX = np.array(M).T  # (T_oos, 27)
        NDX_CFG = cfg_names

print("\n" + "="*70 + "\nCROSS-WINDOW 4x4 (params source x data window)\n" + "="*70)
# 4 windows: split each market into early/late halves (by r_pct index)
windows = {}
for label, (path, _, _) in DATASETS.items():
    df = load_ohlc(str(path)).set_index("date")
    logp = np.log(df["close"].astype(float))
    r_fwd = (logp.shift(-1) - logp).values
    r_pct = log_returns_pct(df.reset_index()).values
    half = len(r_pct) // 2
    windows[f"{label[:4]}-early"] = {"r_pct": r_pct[:half], "r_fwd": r_fwd[:half]}
    windows[f"{label[:4]}-late"] = {"r_pct": r_pct[half:], "r_fwd": r_fwd[half:]}

# fit GJR-t params once on the in-sample (first 60%) of each window
param_src = {}
for wname, wd in windows.items():
    rp = wd["r_pct"]
    tin = int(0.6 * len(rp))
    param_src[wname] = params_dict(fit_arch(rp[:tin], "GJR-t"))

def frozen_param_overlay(r_pct, r_fwd, p, cap=1.5):
    """Static-param (no refit) long-only vol-target overlay for cross-fit test."""
    T = len(r_pct)
    path = garch_path(r_pct, p, gjr=True)[:T]
    vol_fcst = ANNUALIZE * np.sqrt(path)
    t0 = int(0.6 * T)
    vtar = realized_ann_vol_pct(r_pct[:t0])
    expo = np.clip(vtar / np.maximum(vol_fcst, 1e-8), 0.0, cap)
    lev = np.zeros(len(r_fwd)); lev[:T] = np.nan_to_num(expo, nan=0.0)
    oos = np.arange(t0, len(r_fwd) - 1)
    pnl_ov = backtest(lev, r_fwd, COST_BPS)[oos]
    pnl_bh = backtest(np.ones(len(r_fwd)), r_fwd, COST_BPS)[oos]
    m_ov, m_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
    mdd_red = 1.0 - abs(m_ov["max_drawdown_pct"]) / abs(m_bh["max_drawdown_pct"])
    ret_ratio = (m_ov["ann_return_pct"] / m_bh["ann_return_pct"]
                 if m_bh["ann_return_pct"] != 0 else np.nan)
    gate = bool((mdd_red > 0.25) and (ret_ratio >= 0.80))
    return {"sharpe_ann": m_ov["sharpe_ann"], "calmar": m_ov["calmar"],
            "mdd_pct": m_ov["max_drawdown_pct"], "mdd_red": float(mdd_red),
            "ret_ratio": float(ret_ratio), "gate": gate}

cross = {}
wnames = list(windows.keys())
for ps in wnames:
    for ds in wnames:
        cross[f"{ps}||{ds}"] = frozen_param_overlay(windows[ds]["r_pct"],
                                                     windows[ds]["r_fwd"], param_src[ps])
# variance decomposition of Sharpe over the 4x4 (two-way, params vs data)
S = np.array([[cross[f"{ps}||{ds}"]["sharpe_ann"] for ds in wnames] for ps in wnames])
grand = S.mean()
row_eff = S.mean(axis=1) - grand      # params effect
col_eff = S.mean(axis=0) - grand      # data effect
ss_params = 4 * np.sum(row_eff**2)
ss_data = 4 * np.sum(col_eff**2)
ss_inter = np.sum((S - grand - row_eff[:, None] - col_eff[None, :])**2)
ss_tot = ss_params + ss_data + ss_inter
var_decomp = {"ss_params": float(ss_params), "ss_data": float(ss_data),
              "ss_interaction": float(ss_inter),
              "pct_params": float(100*ss_params/ss_tot),
              "pct_data": float(100*ss_data/ss_tot),
              "pct_interaction": float(100*ss_inter/ss_tot)}
CROSS = {"cells": cross, "windows": wnames, "param_src": {k: v for k, v in param_src.items()},
         "var_decomp": var_decomp}

print("\n" + "="*70 + "\nPARAMETER STABILITY (NDX)\n" + "="*70)
pp = pd.DataFrame(RESULTS["NDX"]["params"])
keymap = {"omega": "omega", "alpha[1]": "alpha", "beta[1]": "beta",
          "gamma[1]": "gamma", "nu": "nu"}
stability = {}
for raw, nm in keymap.items():
    if raw not in pp:
        continue
    s = pp[raw].values.astype(float)
    adf = adfuller(s, autolag="AIC")
    ac1 = float(pd.Series(s).autocorr(lag=1))
    breaks = int(np.sum(np.abs(np.diff(s)) > 2 * s.std()))
    stability[nm] = {"min": float(s.min()), "median": float(np.median(s)),
                     "max": float(s.max()), "std": float(s.std()),
                     "cv_pct": float(100 * s.std() / abs(np.mean(s))) if np.mean(s) != 0 else None,
                     "adf_stat": float(adf[0]), "adf_p": float(adf[1]),
                     "autocorr_lag1": ac1, "n_jumps_2sigma": breaks}
STABILITY = stability

print("\n" + "="*70 + "\nCSCV / PBO on 27-config grid (NDX)\n" + "="*70)
# Bailey et al. 2014 CSCV: split T into S blocks, all C(S,S/2) train/test halves.
def cscv_pbo(M, S=14):
    T, N = M.shape
    idx = np.array_split(np.arange(T), S)
    logits = []
    n_oos_below = 0
    combos = list(combinations(range(S), S // 2))
    for tr_blocks in combos:
        tr = np.concatenate([idx[b] for b in tr_blocks])
        te = np.concatenate([idx[b] for b in range(S) if b not in tr_blocks])
        def sharpe(x):
            sd = x.std(ddof=1)
            return x.mean() / sd if sd > 0 else 0.0
        sr_tr = np.array([sharpe(M[tr, j]) for j in range(N)])
        sr_te = np.array([sharpe(M[te, j]) for j in range(N)])
        j_star = int(np.argmax(sr_tr))
        # OOS rank of the IS-best config (fractional rank in [0,1])
        rank = (np.sum(sr_te <= sr_te[j_star]) - 1) / (N - 1)
        if rank < 0.5:
            n_oos_below += 1
        w = max(min(rank, 1 - 1e-6), 1e-6)
        logits.append(np.log(w / (1 - w)))
    pbo = n_oos_below / len(combos)
    return {"pbo": float(pbo), "n_partitions": len(combos), "S": S,
            "logit_mean": float(np.mean(logits)), "logit_median": float(np.median(logits))}

PBO = cscv_pbo(NDX_PNL_MATRIX, S=14)
print(f"  PBO={PBO['pbo']:.3f} over {PBO['n_partitions']} partitions (S={PBO['S']})")

# ------------------------------------------------------------------- FIGURES
def heatmap_panels(label, metric, fname, cmap, fmt="{:+.2f}"):
    grid = RESULTS[label]["grid"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    allv = [grid[f"{c}|{vs}|{p}"][metric] for c in CAPS for vs in VOL_SPANS for p in PCTLS]
    vmin, vmax = min(allv), max(allv)
    for ax, cap in zip(axes, CAPS):
        Z = np.array([[grid[f"{cap}|{vs}|{p}"][metric] for p in PCTLS] for vs in VOL_SPANS])
        im = ax.imshow(Z, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
        ax.set_xticks(range(3)); ax.set_xticklabels([f"{int(p)}" for p in PCTLS])
        ax.set_yticks(range(3)); ax.set_yticklabels([str(v) for v in VOL_SPANS])
        ax.set_xlabel("cut percentile"); ax.set_ylabel("vol_span (EWMA)")
        ax.set_title(f"{label}  cap={cap}x")
        for i in range(3):
            for j in range(3):
                star = " *" if (cap, VOL_SPANS[i], PCTLS[j]) == FROZEN else ""
                ax.text(j, i, fmt.format(Z[i, j]) + star, ha="center", va="center",
                        fontsize=8, color="black")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle(f"{label} — {metric} perturbation grid (frozen point *)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / fname, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {fname}")

heatmap_panels("NDX", "sharpe_ann", "heatmap_ndx_sharpe.png", "RdYlGn")
heatmap_panels("NDX", "max_drawdown_pct", "heatmap_ndx_mdd.png", "RdYlGn")
heatmap_panels("NDX", "calmar", "heatmap_ndx_calmar.png", "RdYlGn")
heatmap_panels("Composite", "sharpe_ann", "heatmap_comp_sharpe.png", "RdYlGn")
heatmap_panels("Composite", "max_drawdown_pct", "heatmap_comp_mdd.png", "RdYlGn")

# param stability time-series
pp = pd.DataFrame(RESULTS["NDX"]["params"])
fig, axes = plt.subplots(5, 1, figsize=(11, 12), sharex=True)
for ax, (raw, nm) in zip(axes, keymap.items()):
    if raw not in pp:
        continue
    s = pp[raw].values.astype(float)
    ax.plot(pp["tr"].values, s, lw=1.1)
    ax.axhline(np.median(s), ls="--", c="grey", lw=0.8)
    ax.set_ylabel(nm)
    ax.set_title(f"{nm}: median={np.median(s):.4g}, std={s.std():.4g}, "
                 f"ADF p={STABILITY[nm]['adf_p']:.3f}, {STABILITY[nm]['n_jumps_2sigma']} jumps>2σ",
                 fontsize=9, loc="left")
axes[-1].set_xlabel("refit index (bar tr, NDX)")
fig.suptitle("GJR-t parameter stability across NDX walk-forward refits", y=1.005)
fig.tight_layout()
fig.savefig(FIG / "param_stability_ndx.png", dpi=110, bbox_inches="tight")
plt.close(fig)
print("  wrote param_stability_ndx.png")

# ------------------------------------------------------------------- DUMP
for label in RESULTS:
    RESULTS[label].pop("_r_pct", None)
OUT = {"frozen": {"cap": FROZEN[0], "vol_span": FROZEN[1], "cut_pctl": FROZEN[2],
                  "T0": T0, "cost_bps": COST_BPS, "embargo": EMBARGO, "H": H,
                  "barrier_mult": BARRIER_MULT},
       "markets": RESULTS, "cross_window": CROSS, "stability": STABILITY, "pbo": PBO}
OUTJSON.write_text(json.dumps(OUT, indent=2, default=float))
print(f"\nWROTE {OUTJSON}")
print("DONE")

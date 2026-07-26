#!/usr/bin/env python3
"""
PHASE B + ML FILTER — STRICT REBUILD FROM SCRATCH
==================================================

Clean-room re-implementation of the Phase B signal + ML filter under the
strict anti-data-snooping protocol. NO previously optimized parameter is
imported. Every threshold used here is either (a) declared a priori as a
"round" value, or (b) estimated on a design sample and frozen.

TIMING CONVENTION (the single most important thing in this file)
----------------------------------------------------------------
    df.close[t]      = close of day t
    r.iloc[t]        = log return close[t] -> close[t+1]   (FORWARD return)

A position taken at the close of day t earns r.iloc[t]. Therefore any
feature used to build the position at index t may only use
    close[0..t]   equivalently   r.iloc[0..t-1]
Using r.iloc[t] inside a feature is a one-day LOOKAHEAD.

DECLARED UNIVERSE (N = 4 trials, frozen before any evaluation)
---------------------------------------------------------------
    B1  BuyHold          pos = 1
    B2  S5               pos = 1 if EMA50 > EMA200 else 0
    B3  S5-OV [Agg+]     B2 * overlay(1.5x if vol < q25, 0.3x if vol > q75, else 1.0)
    B4  S5-OV + ML       B3 * 1{ mom_5 > 0  AND  ema_trend > 0.98 }

HYPOTHESIS UNDER TEST
    "momentum_5d > 0 AND ema_trend > 0.98 adds value to S5-OV"

Momentum window is 5d (declared a priori, NOT the 3d value that a prior
search reported as better). Threshold is 0 (round), not 0.3 (searched).
The 0.98 EMA-trend gate is inherited as a stated a-priori hypothesis.

The ONLY quantities estimated from data are the two volatility quantiles
(q25 / q75). They are handled three ways so their effect is visible:
    - expanding (strictly causal) in the walk-forward
    - frozen from the design sample in the design/test split
    - frozen from the design sample for the cross-market test

Cost: 5 bps round-trip on |delta position|. No shorting. Long-only 0..1.5.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "finance" / "src"))

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from prediction import trading_metrics, dsr  # noqa: E402

TRADING_DAYS = 252
COST_BPS = 5.0

# ---------------------------------------------------------------------------
# A PRIORI CONSTANTS — declared here, never tuned anywhere below
# ---------------------------------------------------------------------------
EMA_FAST = 50
EMA_SLOW = 200
VOL_WINDOW = 20
MOM_WINDOW = 5           # a priori: 5 days (NOT the searched 3d)
MOM_THRESHOLD = 0.0      # a priori: round zero (NOT the searched +0.3)
EMA_TREND_GATE = 0.98    # a priori hypothesis value
OVERLAY_AMP = 1.5        # [Agg+]
OVERLAY_RED = 0.3        # [Agg+]
Q_LOW, Q_HIGH = 0.25, 0.75

N_TRIALS = 4             # size of the declared universe, for the DSR


# ---------------------------------------------------------------------------
# Feature construction — every value at index t uses close[0..t] only
# ---------------------------------------------------------------------------
def build_state(df: pd.DataFrame) -> pd.DataFrame:
    """Causal state variables aligned on the tradeable index t = 0..n-2.

    Row t holds everything observable at the close of day t, and is paired
    with r_fwd[t] = the return earned from t to t+1.
    """
    close = df["close"].astype(float).reset_index(drop=True)
    r_all = np.log(close).diff() * 100.0          # r_all[t] = close[t-1]->close[t]
    n = len(close)

    ema_f = close.ewm(span=EMA_FAST, adjust=False).mean()
    ema_s = close.ewm(span=EMA_SLOW, adjust=False).mean()

    # r_all[t] is the return realised INTO day t, so it is known at close[t].
    # rolling(w) on r_all ending at t therefore uses only known information.
    vol = r_all.rolling(VOL_WINDOW).std()
    mom = r_all.rolling(MOM_WINDOW).sum()

    st = pd.DataFrame(
        {
            "date": df["date"].reset_index(drop=True),
            "close": close,
            "ema_fast": ema_f,
            "ema_slow": ema_s,
            "ema_trend": ema_f / ema_s,
            "vol": vol,
            "mom": mom,
        }
    )
    # forward return earned by a position opened at close[t]
    st["r_fwd"] = np.log(close).diff().shift(-1) * 100.0
    return st.iloc[: n - 1].reset_index(drop=True)   # drop last row (no r_fwd)


# ---------------------------------------------------------------------------
# Volatility overlay multipliers
# ---------------------------------------------------------------------------
def overlay_from_thresholds(vol: np.ndarray, q_lo: float, q_hi: float) -> np.ndarray:
    mult = np.ones(len(vol))
    ok = np.isfinite(vol)
    mult[ok & (vol < q_lo)] = OVERLAY_AMP
    mult[ok & (vol > q_hi)] = OVERLAY_RED
    return mult


def overlay_expanding(vol: np.ndarray, min_obs: int = 250) -> np.ndarray:
    """Strictly causal overlay: quantiles at t use vol[0..t-1] only."""
    s = pd.Series(vol)
    q_lo = s.shift(1).expanding(min_obs).quantile(Q_LOW).values
    q_hi = s.shift(1).expanding(min_obs).quantile(Q_HIGH).values
    mult = np.ones(len(vol))
    ok = np.isfinite(vol) & np.isfinite(q_lo) & np.isfinite(q_hi)
    mult[ok & (vol < q_lo)] = OVERLAY_AMP
    mult[ok & (vol > q_hi)] = OVERLAY_RED
    return mult


# ---------------------------------------------------------------------------
# Signal universe
# ---------------------------------------------------------------------------
def signals(st: pd.DataFrame, overlay: np.ndarray) -> dict:
    base = np.where(st["ema_fast"].values > st["ema_slow"].values, 1.0, 0.0)
    s5ov = base * overlay
    ml_gate = (
        (st["mom"].values > MOM_THRESHOLD)
        & (st["ema_trend"].values > EMA_TREND_GATE)
    )
    ml_gate = np.where(np.isfinite(st["mom"].values), ml_gate, False)
    return {
        "B1_BuyHold": np.ones(len(st)),
        "B2_S5": base,
        "B3_S5-OV[Agg+]": s5ov,
        "B4_S5-OV+ML": s5ov * ml_gate.astype(float),
    }


def backtest(pos: np.ndarray, r_fwd: np.ndarray, cost_bps: float = COST_BPS,
             delay: int = 0) -> np.ndarray:
    pos = np.asarray(pos, dtype=float).copy()
    if delay:
        pos = np.concatenate([np.zeros(delay), pos[:-delay]])
    turn = np.abs(np.diff(pos, prepend=0.0))
    pnl = pos * np.asarray(r_fwd, dtype=float) - turn * (cost_bps / 1e4) * 100.0
    return pnl


def metrics(pnl: np.ndarray, pos: np.ndarray | None = None) -> dict:
    pnl = np.asarray(pnl, dtype=float)
    pnl = pnl[np.isfinite(pnl)]
    m = trading_metrics(pnl / 100.0)
    out = {
        "n": m["n"],
        "sharpe": m["sharpe_ann"],
        "sharpe_daily": m["sharpe_daily"],
        "sortino": m["sortino_ann"],
        "calmar": m["calmar"],
        "ann_return_pct": m["ann_return_pct"],
        "mdd_pct": m["max_drawdown_pct"],
        "profit_factor": m["profit_factor"],
        "skew": m["skew"],
        "excess_kurt": m["excess_kurt"],
    }
    if pos is not None:
        p = np.asarray(pos, dtype=float)
        out["exposure_pct"] = float(100.0 * (p > 0).mean())
        out["avg_position"] = float(np.nanmean(p))
        out["turnover_ann"] = float(
            np.abs(np.diff(p, prepend=0.0)).sum() / len(p) * TRADING_DAYS
        )
    return out


def sharpe_ann(pnl: np.ndarray) -> float:
    pnl = np.asarray(pnl, dtype=float)
    pnl = pnl[np.isfinite(pnl)]
    if len(pnl) < 3:
        return np.nan
    sd = pnl.std(ddof=1)
    return float(pnl.mean() / sd * np.sqrt(TRADING_DAYS)) if sd > 0 else 0.0


# ---------------------------------------------------------------------------
# STEP 0 — lookahead forensics on the legacy formulation
# ---------------------------------------------------------------------------
def legacy_replication(df: pd.DataFrame) -> dict:
    """Reproduce the legacy pipeline and isolate the lookahead term.

    Legacy code computed momentum as sum(r[i-w : i+1]), i.e. INCLUDING
    r.iloc[i] -- which is exactly the forward return the position is about
    to earn. It also drew the overlay quantiles from the full sample.
    """
    close = df["close"].astype(float).reset_index(drop=True)
    r = (np.log(close).diff() * 100.0).iloc[1:].reset_index(drop=True)  # r[t]=t->t+1
    n = len(r)
    ema_f = close.ewm(span=EMA_FAST).mean().values[:n]
    ema_s = close.ewm(span=EMA_SLOW).mean().values[:n]
    ema_trend = ema_f / ema_s

    vol = r.rolling(VOL_WINDOW).std()
    q_lo, q_hi = vol.quantile(Q_LOW), vol.quantile(Q_HIGH)      # full-sample
    ov = overlay_from_thresholds(vol.values, q_lo, q_hi)
    s5ov = np.where(ema_f > ema_s, 1.0, 0.0) * ov

    out = {}
    for tag, incl in (("legacy_lookahead", True), ("causal_momentum", False)):
        if incl:
            mom = r.rolling(MOM_WINDOW).sum().values          # includes r[t]
        else:
            mom = r.shift(1).rolling(MOM_WINDOW).sum().values  # excludes r[t]
        gate = (mom > MOM_THRESHOLD) & (ema_trend > EMA_TREND_GATE)
        gate = np.where(np.isfinite(mom), gate, False)
        pos = s5ov * gate.astype(float)
        out[tag] = metrics(backtest(pos, r.values), pos)
    out["S5-OV_base_fullsample_quantiles"] = metrics(backtest(s5ov, r.values), s5ov)
    return out


# ---------------------------------------------------------------------------
# STEP 3 — walk-forward with embargo
# ---------------------------------------------------------------------------
def walk_forward(st: pd.DataFrame, t0: int = 750, block: int = 21,
                 embargo: int = 21) -> dict:
    """Expanding walk-forward. Nothing is optimized: the only quantity
    re-estimated each block is the pair of volatility quantiles, fit on
    train data truncated by the embargo."""
    n = len(st)
    vol = st["vol"].values
    r_fwd = st["r_fwd"].values
    base = np.where(st["ema_fast"].values > st["ema_slow"].values, 1.0, 0.0)
    gate = (
        (st["mom"].values > MOM_THRESHOLD)
        & (st["ema_trend"].values > EMA_TREND_GATE)
    )
    gate = np.where(np.isfinite(st["mom"].values), gate, False).astype(float)

    is_sh, oos_sh, oos_pos, oos_idx, n_win = [], [], [], [], 0
    for tr in range(t0, n, block):
        tr_end = tr - embargo
        v_tr = vol[:tr_end]
        v_tr = v_tr[np.isfinite(v_tr)]
        if len(v_tr) < 250:
            continue
        q_lo, q_hi = np.quantile(v_tr, Q_LOW), np.quantile(v_tr, Q_HIGH)
        n_win += 1

        # in-sample block (train window, frozen quantiles)
        sl_is = slice(0, tr_end)
        p_is = base[sl_is] * overlay_from_thresholds(vol[sl_is], q_lo, q_hi) * gate[sl_is]
        is_sh.append(sharpe_ann(backtest(p_is, r_fwd[sl_is])))

        # out-of-sample block
        hi = min(tr + block, n)
        sl = slice(tr, hi)
        p_oos = base[sl] * overlay_from_thresholds(vol[sl], q_lo, q_hi) * gate[sl]
        blk = backtest(p_oos, r_fwd[sl])
        oos_sh.append(sharpe_ann(blk))
        oos_pos.append(p_oos)
        oos_idx.append(np.arange(tr, hi))

    pos_cat = np.concatenate(oos_pos)
    idx_cat = np.concatenate(oos_idx)
    pnl_cat = backtest(pos_cat, r_fwd[idx_cat])

    return {
        "n_windows": n_win,
        "t0": t0,
        "block": block,
        "embargo": embargo,
        "avg_IS_sharpe": float(np.nanmean(is_sh)),
        "avg_OOS_block_sharpe": float(np.nanmean(oos_sh)),
        "median_OOS_block_sharpe": float(np.nanmedian(oos_sh)),
        "stitched_OOS": metrics(pnl_cat, pos_cat),
        "pct_blocks_positive": float(100.0 * np.mean(np.array(oos_sh) > 0)),
    }


def walk_forward_reference(st: pd.DataFrame, name: str, t0: int = 750,
                           block: int = 21, embargo: int = 21) -> dict:
    """Same stitched-OOS window for a reference signal, so the comparison is
    on identical dates."""
    n = len(st)
    r_fwd = st["r_fwd"].values
    ov = overlay_expanding(st["vol"].values)
    sig = signals(st, ov)[name]
    idx = np.arange(t0, n)
    return metrics(backtest(sig[idx], r_fwd[idx]), sig[idx])


# ---------------------------------------------------------------------------
# STEP 4/5 — design / test split with frozen parameters
# ---------------------------------------------------------------------------
def fit_design(st_design: pd.DataFrame) -> dict:
    v = st_design["vol"].values
    v = v[np.isfinite(v)]
    return {
        "q_lo": float(np.quantile(v, Q_LOW)),
        "q_hi": float(np.quantile(v, Q_HIGH)),
        "n_design": int(len(st_design)),
    }


def evaluate(st: pd.DataFrame, params: dict) -> dict:
    ov = overlay_from_thresholds(st["vol"].values, params["q_lo"], params["q_hi"])
    sig = signals(st, ov)
    r_fwd = st["r_fwd"].values
    res = {}
    for k, p in sig.items():
        ok = np.isfinite(r_fwd) & np.isfinite(p)
        res[k] = metrics(backtest(p[ok], r_fwd[ok]), p[ok])
    return res


def add_dsr(res: dict) -> dict:
    """Deflated Sharpe Ratio across the declared universe of N=4."""
    daily = {k: v["sharpe_daily"] for k, v in res.items()}
    var_trials = float(np.var(list(daily.values()), ddof=1))
    for k, v in res.items():
        d = dsr(v["sharpe_daily"], v["n"], var_trials, N_TRIALS,
                v["skew"], v["excess_kurt"])
        v["dsr"] = d["dsr"]
        v["dsr_z"] = d["z"]
    return res


# ---------------------------------------------------------------------------
def table(res: dict, title: str) -> None:
    print(f"\n{title}")
    print("-" * 104)
    print(f"{'Signal':<20}{'N':>7}{'Sharpe':>9}{'AnnRet%':>9}{'MDD%':>9}"
          f"{'Calmar':>8}{'Expo%':>8}{'Turn':>7}{'DSR':>8}")
    print("-" * 104)
    for k, v in res.items():
        print(f"{k:<20}{v['n']:>7}{v['sharpe']:>9.3f}{v['ann_return_pct']:>9.2f}"
              f"{v['mdd_pct']:>9.1f}{v.get('calmar', float('nan')):>8.2f}"
              f"{v.get('exposure_pct', float('nan')):>8.1f}"
              f"{v.get('turnover_ann', float('nan')):>7.1f}"
              f"{v.get('dsr', float('nan')):>8.3f}")


def main() -> None:
    out: dict = {}

    print("=" * 104)
    print("PHASE B + ML FILTER — STRICT REBUILD (clean start, no imported parameters)")
    print("=" * 104)
    print(f"A priori universe N={N_TRIALS}: BuyHold / S5 / S5-OV[Agg+] / S5-OV+ML")
    print(f"ML filter (declared): mom_{MOM_WINDOW}d > {MOM_THRESHOLD} "
          f"AND ema_trend > {EMA_TREND_GATE}")
    print(f"Overlay [Agg+]: {OVERLAY_AMP}x below q{int(Q_LOW*100)}, "
          f"{OVERLAY_RED}x above q{int(Q_HIGH*100)} of {VOL_WINDOW}d vol")
    print(f"Costs: {COST_BPS} bps on |delta position|. Long-only.")

    ndx = load_ohlc(str(ROOT / "data" / "nasdaq100_daily.txt"))
    comp = load_ohlc(str(ROOT / "data" / "nasdaq_composite_daily.txt"))
    st_ndx, st_comp = build_state(ndx), build_state(comp)
    print(f"\nNDX       : {len(st_ndx)} tradeable days, "
          f"{st_ndx.date.iloc[0].date()} -> {st_ndx.date.iloc[-1].date()}")
    print(f"Composite : {len(st_comp)} tradeable days, "
          f"{st_comp.date.iloc[0].date()} -> {st_comp.date.iloc[-1].date()}")

    # ---- STEP 0: lookahead forensics ------------------------------------
    print("\n" + "=" * 104)
    print("STEP 0 — FORENSICS ON THE LEGACY FORMULATION (NDX, full sample)")
    print("=" * 104)
    print("Legacy momentum was sum(r[i-w : i+1]); r[i] is the forward return the")
    print("position earns. Removing that single term is the whole experiment.")
    leg = legacy_replication(ndx)
    out["step0_legacy_forensics"] = leg
    table(leg, "Legacy vs causal momentum (full-sample quantiles, as in legacy code)")
    d = leg["legacy_lookahead"]["sharpe"] - leg["causal_momentum"]["sharpe"]
    print(f"\n  >> Sharpe attributable to the 1-day lookahead: {d:+.3f}")

    # ---- STEP 3: walk-forward -------------------------------------------
    print("\n" + "=" * 104)
    print("STEP 3 — WALK-FORWARD WITH EMBARGO (NDX)")
    print("=" * 104)
    wf = walk_forward(st_ndx, t0=750, block=21, embargo=21)
    out["step3_walk_forward_ndx"] = wf
    print(f"  windows            : {wf['n_windows']}  (T0={wf['t0']}, "
          f"block={wf['block']}d, embargo={wf['embargo']}d)")
    print(f"  avg IS  Sharpe     : {wf['avg_IS_sharpe']:.3f}")
    print(f"  avg OOS block Sh.  : {wf['avg_OOS_block_sharpe']:.3f}")
    print(f"  median OOS block   : {wf['median_OOS_block_sharpe']:.3f}")
    print(f"  blocks with Sh > 0 : {wf['pct_blocks_positive']:.1f}%")
    s = wf["stitched_OOS"]
    print(f"  stitched OOS       : Sharpe {s['sharpe']:.3f}, "
          f"AnnRet {s['ann_return_pct']:.2f}%, MDD {s['mdd_pct']:.1f}%, "
          f"exposure {s['exposure_pct']:.1f}%")
    for ref in ("B1_BuyHold", "B3_S5-OV[Agg+]"):
        m = walk_forward_reference(st_ndx, ref)
        out.setdefault("step3_references", {})[ref] = m
        print(f"  reference {ref:<16}: Sharpe {m['sharpe']:.3f}, "
              f"MDD {m['mdd_pct']:.1f}%")
    print(f"\n  >> FLAG: OOS Sharpe {s['sharpe']:.3f} "
          f"{'< 1.0 -> SIGNAL FAILS' if s['sharpe'] < 1.0 else '>= 1.0 -> passes'}")

    # ---- STEP 4: design / test ------------------------------------------
    print("\n" + "=" * 104)
    print("STEP 4 — TRUE OOS: DESIGN (NDX 1985-2010) -> TEST (NDX 2010-2026)")
    print("=" * 104)
    cut = pd.Timestamp("2010-01-01")
    st_d = st_ndx[st_ndx.date < cut].reset_index(drop=True)
    st_t = st_ndx[st_ndx.date >= cut].reset_index(drop=True)
    params = fit_design(st_d)
    out["step4_frozen_params"] = params
    print(f"  design : {len(st_d)} obs, {st_d.date.iloc[0].date()} -> "
          f"{st_d.date.iloc[-1].date()}")
    print(f"  test   : {len(st_t)} obs, {st_t.date.iloc[0].date()} -> "
          f"{st_t.date.iloc[-1].date()}")
    print(f"  frozen vol quantiles from design: q25={params['q_lo']:.4f}, "
          f"q75={params['q_hi']:.4f}")

    res_d = add_dsr(evaluate(st_d, params))
    res_t = add_dsr(evaluate(st_t, params))
    out["step4_design"], out["step4_test"] = res_d, res_t
    table(res_d, "DESIGN (in-sample, NDX 1985-2010)")
    table(res_t, "TEST (true OOS, frozen params, NDX 2010-2026)")

    print("\n  DEGRADATION  (Test Sharpe - Design Sharpe)")
    print("  " + "-" * 74)
    deg = {}
    for k in res_d:
        g = res_t[k]["sharpe"] - res_d[k]["sharpe"]
        deg[k] = g
        verdict = "ACCEPT" if g >= -0.5 else "REJECT (overfit)"
        print(f"  {k:<20} design {res_d[k]['sharpe']:>7.3f} -> "
              f"test {res_t[k]['sharpe']:>7.3f}   {g:>+7.3f}   {verdict}")
    out["step4_degradation"] = deg

    # ---- STEP 5: cross-market -------------------------------------------
    print("\n" + "=" * 104)
    print("STEP 5 — CROSS-MARKET: design-frozen params applied to COMPOSITE 2021-2026")
    print("=" * 104)
    res_c = add_dsr(evaluate(st_comp, params))
    out["step5_composite"] = res_c
    table(res_c, "COMPOSITE (NDX-design params, untouched)")
    print("\n  CROSS-MARKET GAP (Composite Sharpe - NDX Test Sharpe)")
    print("  " + "-" * 74)
    gaps = {}
    for k in res_c:
        g = res_c[k]["sharpe"] - res_t[k]["sharpe"]
        gaps[k] = g
        if abs(g) <= 0.3:
            v = "ACCEPT (within 0.3)"
        elif g < -1.0:
            v = "REJECT (>1.0 worse)"
        else:
            v = "MARGINAL"
        print(f"  {k:<20} test {res_t[k]['sharpe']:>7.3f} -> "
              f"composite {res_c[k]['sharpe']:>7.3f}   {g:>+7.3f}   {v}")
    out["step5_gap"] = gaps

    # ---- execution-delay sensitivity ------------------------------------
    print("\n" + "=" * 104)
    print("ROBUSTNESS — EXECUTION DELAY (NDX test period, frozen params)")
    print("=" * 104)
    ov_t = overlay_from_thresholds(st_t["vol"].values, params["q_lo"], params["q_hi"])
    sig_t = signals(st_t, ov_t)
    delays = {}
    print(f"  {'Signal':<20}" + "".join(f"{'d=' + str(d):>10}" for d in range(4)))
    for k, p in sig_t.items():
        row = []
        for dl in range(4):
            ok = np.isfinite(st_t["r_fwd"].values) & np.isfinite(p)
            row.append(sharpe_ann(backtest(p[ok], st_t["r_fwd"].values[ok], delay=dl)))
        delays[k] = row
        print(f"  {k:<20}" + "".join(f"{x:>10.3f}" for x in row))
    out["robustness_delay_ndx_test"] = delays

    # ---- verdict ---------------------------------------------------------
    ml, bh = "B4_S5-OV+ML", "B1_BuyHold"
    print("\n" + "=" * 104)
    print("VERDICT")
    print("=" * 104)
    print(f"  hypothesis          : mom_5d > 0 AND ema_trend > 0.98 adds value to S5-OV")
    print(f"  design Sharpe       : {res_d[ml]['sharpe']:.3f}")
    print(f"  test Sharpe (OOS)   : {res_t[ml]['sharpe']:.3f}   "
          f"(degradation {deg[ml]:+.3f})")
    print(f"  walk-forward OOS    : {wf['stitched_OOS']['sharpe']:.3f}")
    print(f"  composite Sharpe    : {res_c[ml]['sharpe']:.3f}")
    print(f"  vs BuyHold on test  : {res_t[ml]['sharpe']:.3f} vs "
          f"{res_t[bh]['sharpe']:.3f}  -> "
          f"{'BEATS' if res_t[ml]['sharpe'] > res_t[bh]['sharpe'] else 'LOSES TO'} BuyHold")
    print(f"  vs S5-OV on test    : {res_t[ml]['sharpe']:.3f} vs "
          f"{res_t['B3_S5-OV[Agg+]']['sharpe']:.3f}")
    print(f"  DSR (test, N=4)     : ML {res_t[ml]['dsr']:.3f} | "
          f"BuyHold {res_t[bh]['dsr']:.3f}")

    dest = ROOT / "results" / "phase_b_strict_rebuild.json"
    dest.write_text(json.dumps(out, indent=2, default=float))
    print(f"\nSaved: {dest}")


if __name__ == "__main__":
    main()

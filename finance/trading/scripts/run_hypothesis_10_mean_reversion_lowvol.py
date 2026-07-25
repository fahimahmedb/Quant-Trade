#!/usr/bin/env python3
"""
Hypothesis H10: Mean Reversion in Low-Volatility Regimes
=========================================================

MOTIVATION:
  H1_MeanReversion (RSI) = Sharpe 0.213 (weak overall)
  H3_VolRegime partially addressed regime-based trading, but failed
  INSIGHT: Mean reversion works in CALM markets, not extreme volatility

  Why?
    - In calm markets (vol low), prices oscillate around mean
    - In volatile markets, momentum dominates (mean reversion dies)
    - So: Gate mean reversion signal by vol regime

APPROACH:
  1. Compute volatility terciles (low/mid/high)
  2. RSI-based mean reversion signal (overbought/sold)
  3. ONLY trade when in LOW-vol tercile (vol < 33rd percentile)
  4. In mid/high vol: go neutral
  5. Compare to "always trade" H1

MECHANISM:
  vol = rolling_std(returns, 20)
  vol_tercile_lo = vol.quantile(1/3)

  for each day:
    if vol < vol_tercile_lo:
      if RSI > 70: position = -1 (short overbought)
      elif RSI < 30: position = 1 (long oversold)
      else: position = 0
    else:
      position = 0 (neutral in higher vol)

EXPECTED:
  - Sharpe 0.25-0.30 (better than H1's 0.213)
  - MUCH lower MDD (only trades in calm periods)
  - Win rate might be higher (fewer trades, high-conviction)
  - Theory: Regime-aware beats regime-blind
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from data_loader import load_ohlc, log_returns_pct

def calc_sharpe(returns, ann=252):
    if len(returns) < 2:
        return 0.0
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    if sigma == 0:
        return 0.0
    return float(mu / sigma * np.sqrt(ann))

def calc_mdd(returns_pct):
    """Calculate maximum drawdown as percentage.

    returns_pct: daily returns in percentage points (e.g., 0.5 for 0.5%)
    Returns: MDD in percentage (e.g., -35.5 for -35.5% drawdown)
    """
    # Convert to equity curve: equity[t] = exp(cumsum(returns) / 100)
    cumsum_pct = np.cumsum(returns_pct)
    equity = np.exp(cumsum_pct / 100.0)
    peak = np.maximum.accumulate(equity)

    # Calculate drawdown as percentage
    drawdown_pct = ((equity - peak) / peak).min() * 100
    return float(drawdown_pct)

def calc_metrics(returns):
    sharpe = calc_sharpe(returns)
    mdd = calc_mdd(returns)
    total_ret = np.sum(returns) * 100
    if mdd < 0:
        calmar = total_ret / abs(mdd) if abs(mdd) > 0 else 0
    else:
        calmar = 0
    win_rate = np.mean(returns > 0) * 100 if len(returns) > 0 else 0
    return {
        'sharpe': sharpe,
        'mdd': mdd,
        'return_pct': total_ret,
        'calmar': calmar,
        'win_rate': win_rate
    }

def backtest_simple(positions, returns, cost_bps=5):
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    pnl = pnl - turn * (cost_bps / 1e4)
    return pnl

def run_hypothesis_10(data_path, output_path):
    """
    Mean reversion gated by low-volatility regime
    """
    print("\n" + "=" * 70)
    print("HYPOTHESIS H10: MEAN REVERSION IN LOW-VOL REGIMES")
    print("=" * 70)

    # Load data
    print("\n[H10] Loading data...")
    df = load_ohlc(data_path)
    r = log_returns_pct(df)

    # Compute volatility
    print("[H10] Computing volatility regime...")
    vol_20 = r.rolling(20).std()
    vol_tercile_lo = vol_20.quantile(1/3)
    vol_tercile_hi = vol_20.quantile(2/3)

    print(f"  Vol 33rd percentile (low thresh): {vol_tercile_lo:.4f}")
    print(f"  Vol 67th percentile (high thresh): {vol_tercile_hi:.4f}")

    # Compute RSI (for mean reversion signal)
    print("[H10] Computing RSI...")
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Strategy 1: Mean reversion ONLY in low-vol
    print("\n[H10] Strategy 1: Mean Reversion in Low-Vol ONLY")
    positions_lowvol_only = np.zeros(len(df))

    for i in range(min(len(df), len(vol_20))):
        v = vol_20.iloc[i]
        if pd.isna(v) or pd.isna(rsi.iloc[i]):
            positions_lowvol_only[i] = 0
        elif v < vol_tercile_lo:  # Only in low-vol regime
            if rsi.iloc[i] > 70:
                positions_lowvol_only[i] = -1  # Overbought → short
            elif rsi.iloc[i] < 30:
                positions_lowvol_only[i] = 1   # Oversold → long
            else:
                positions_lowvol_only[i] = 0
        else:  # Mid/High vol
            positions_lowvol_only[i] = 0  # Neutral

    min_len = min(len(positions_lowvol_only), len(r))
    pnl_lowvol = backtest_simple(positions_lowvol_only[:min_len], r.values[:min_len])
    metrics_lowvol = calc_metrics(pnl_lowvol)
    print(f"  Sharpe: {metrics_lowvol['sharpe']:.3f}")
    print(f"  MDD: {metrics_lowvol['mdd']:.1f}")
    print(f"  Win Rate: {metrics_lowvol['win_rate']:.1f}%")

    # Strategy 2: Mean reversion REDUCED in high-vol
    print("\n[H10] Strategy 2: Scaled by Vol Regime")
    positions_scaled = np.zeros(len(df))

    for i in range(min(len(df), len(vol_20))):
        v = vol_20.iloc[i]
        if pd.isna(v) or pd.isna(rsi.iloc[i]):
            positions_scaled[i] = 0
        elif v < vol_tercile_lo:  # Low-vol → full position
            if rsi.iloc[i] > 70:
                positions_scaled[i] = -1.0
            elif rsi.iloc[i] < 30:
                positions_scaled[i] = 1.0
            else:
                positions_scaled[i] = 0
        elif v < vol_tercile_hi:  # Mid-vol → half position
            if rsi.iloc[i] > 70:
                positions_scaled[i] = -0.5
            elif rsi.iloc[i] < 30:
                positions_scaled[i] = 0.5
            else:
                positions_scaled[i] = 0
        else:  # High-vol → quarter position (defensive)
            if rsi.iloc[i] > 80 or rsi.iloc[i] < 20:  # Only extreme RSI
                positions_scaled[i] = (1 if rsi.iloc[i] < 20 else -1) * 0.25
            else:
                positions_scaled[i] = 0

    min_len = min(len(positions_scaled), len(r))
    pnl_scaled = backtest_simple(positions_scaled[:min_len], r.values[:min_len])
    metrics_scaled = calc_metrics(pnl_scaled)
    print(f"  Sharpe: {metrics_scaled['sharpe']:.3f}")
    print(f"  MDD: {metrics_scaled['mdd']:.1f}")
    print(f"  Win Rate: {metrics_scaled['win_rate']:.1f}%")

    # Strategy 3: H1 mean reversion (for comparison, no regime gating)
    print("\n[H10] Strategy 3: H1 Mean Reversion (No Regime Gating, baseline)")
    positions_baseline = np.where(rsi > 70, -1, np.where(rsi < 30, 1, 0))

    min_len = min(len(positions_baseline), len(r))
    pnl_baseline = backtest_simple(positions_baseline[:min_len], r.values[:min_len])
    metrics_baseline = calc_metrics(pnl_baseline)
    print(f"  Sharpe: {metrics_baseline['sharpe']:.3f}")
    print(f"  MDD: {metrics_baseline['mdd']:.1f}")
    print(f"  Win Rate: {metrics_baseline['win_rate']:.1f}%")

    # Analysis
    print("\n[H10] Comparative Analysis:")
    print(f"  H1 baseline:       {metrics_baseline['sharpe']:.3f} Sharpe, {metrics_baseline['mdd']:.1f} MDD")
    print(f"  Low-vol gated:     {metrics_lowvol['sharpe']:.3f} Sharpe, {metrics_lowvol['mdd']:.1f} MDD")
    print(f"  Scaled by regime:  {metrics_scaled['sharpe']:.3f} Sharpe, {metrics_scaled['mdd']:.1f} MDD")

    best = max(
        ('H1_Baseline', metrics_baseline),
        ('Low_Vol_Only', metrics_lowvol),
        ('Scaled_Regime', metrics_scaled),
        key=lambda x: x[1]['sharpe']
    )

    print(f"\n✓ Best: {best[0]} (Sharpe {best[1]['sharpe']:.3f})")

    # Save results
    results = {
        'hypothesis': 'Mean Reversion in Low-Vol Regimes (H10)',
        'h1_baseline': {
            'sharpe': metrics_baseline['sharpe'],
            'mdd': metrics_baseline['mdd'],
            'win_rate': metrics_baseline['win_rate']
        },
        'lowvol_only': {
            'sharpe': metrics_lowvol['sharpe'],
            'mdd': metrics_lowvol['mdd'],
            'win_rate': metrics_lowvol['win_rate']
        },
        'scaled_regime': {
            'sharpe': metrics_scaled['sharpe'],
            'mdd': metrics_scaled['mdd'],
            'win_rate': metrics_scaled['win_rate']
        },
        'best_variant': best[0],
        'best_sharpe': best[1]['sharpe'],
        'interpretation': 'Gate mean reversion by vol regime to reduce whipsaws in high-vol periods'
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved → {output_path}\n")


if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/hypothesis_10_mean_reversion_lowvol.json'
    run_hypothesis_10(data_path, output_path)

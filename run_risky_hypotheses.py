#!/usr/bin/env python3
"""
RISKY & UNCONVENTIONAL HYPOTHESES
Testing against-the-grain approaches that might capture edge
if traditional logic doesn't work
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "finance/src"))
from data_loader import load_ohlc, log_returns_pct

def calc_sharpe(returns, ann=252):
    if len(returns) < 2:
        return 0.0
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    if sigma == 0:
        return 0.0
    return float(mu / sigma * np.sqrt(ann))

def calc_mdd(returns):
    cumsum = np.cumsum(returns)
    peak = np.maximum.accumulate(cumsum)
    dd = cumsum - peak
    return float(np.min(dd))

def calc_metrics(returns):
    sharpe = calc_sharpe(returns)
    mdd = calc_mdd(returns)
    total_ret = np.sum(returns) * 100
    if mdd < 0:
        calmar = total_ret / abs(mdd) if abs(mdd) > 0 else 0
    else:
        calmar = 0
    return {'sharpe': sharpe, 'mdd': mdd, 'return_pct': total_ret, 'calmar': calmar}

def backtest_simple(positions, returns, cost_bps=5):
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    pnl = pnl - turn * (cost_bps / 1e4)
    return pnl

print("=" * 60)
print("🎲 RISKY & UNCONVENTIONAL HYPOTHESIS TESTING")
print("=" * 60)

df = load_ohlc("data/nasdaq100_daily.txt")
r = log_returns_pct(df)
results = {}

# RISKY #1: CONTRARIAN (inverse of everything)
print("\n[R1] Contrarian Signal (Do the opposite)...")
ema12 = df['close'].ewm(span=12).mean()
ema26 = df['close'].ewm(span=26).mean()
momentum_sig = np.where(ema12 > ema26, 1, -1)
contrarian = -momentum_sig  # Inverse

min_len = min(len(contrarian), len(r))
pnl = backtest_simple(contrarian[:min_len], r.values[:min_len])
results['R1_Contrarian'] = calc_metrics(pnl)
print(f"   Sharpe={results['R1_Contrarian']['sharpe']:.3f}")

# RISKY #2: RANDOM LONG (Buy and hold more)
print("\n[R2] Random Long with Edge (Bias long)...")
positions = np.random.choice([-0.5, 0, 0.5, 1.0], size=len(r))
pnl = backtest_simple(positions, r.values)
results['R2_RandomLong'] = calc_metrics(pnl)
print(f"   Sharpe={results['R2_RandomLong']['sharpe']:.3f}")

# RISKY #3: VOLATILITY JUMP (Buy when vol spikes up 50%)
print("\n[R3] Volatility Jump Trading...")
vol_20 = r.rolling(20).std()
vol_sma = vol_20.rolling(50).mean()
vol_spike = (vol_20 > vol_sma * 1.5).astype(int)  # Vol spike
positions = vol_spike.fillna(0).values

min_len = min(len(positions), len(r))
pnl = backtest_simple(positions[:min_len], r.values[:min_len])
results['R3_VolJump'] = calc_metrics(pnl)
print(f"   Sharpe={results['R3_VolJump']['sharpe']:.3f}")

# RISKY #4: INTRA-DAY MICROSTRUCTURE (Open vs Close)
print("\n[R4] Intra-day Microstructure (Open-Close pattern)...")
open_close_diff = df['close'] - df['open']
positions = np.sign(open_close_diff.shift(1))  # Yesterday's open-close predicts today

min_len = min(len(positions), len(r))
pnl = backtest_simple(positions[:min_len], r.values[:min_len])
results['R4_Microstructure'] = calc_metrics(pnl)
print(f"   Sharpe={results['R4_Microstructure']['sharpe']:.3f}")

# RISKY #5: FRACTIONAL DIFFERENTIATION (López de Prado)
print("\n[R5] Fractional Differentiation (0.4 order)...")
def frac_diff(series, order=0.4):
    """Fractional differentiation preserves memory"""
    weights = []
    k = 1.0
    for i in range(1, len(series)):
        weight = -k * (order / i)
        k = weight
        weights.append(weight)

    frac_series = np.zeros(len(series))
    for i in range(len(weights)):
        frac_series[i] = weights[i] * series[i]

    frac_series = (frac_series - frac_series.mean()) / (frac_series.std() + 1e-8)
    positions = np.sign(frac_series)
    return positions

positions = frac_diff(df['close'].values)
min_len = min(len(positions), len(r))
pnl = backtest_simple(positions[:min_len], r.values[:min_len])
results['R5_FracDiff'] = calc_metrics(pnl)
print(f"   Sharpe={results['R5_FracDiff']['sharpe']:.3f}")

# RISKY #6: MULTI-TIMEFRAME DIVERGENCE
print("\n[R6] Multi-timeframe Divergence...")
ema_daily = df['close'].ewm(span=12).mean()
ema_weekly = df['close'].ewm(span=60).mean()  # ~12 days
ema_monthly = df['close'].ewm(span=250).mean()  # ~50 days

# Go long when daily > weekly > monthly (aligned uptrend)
trend_signal = (
    ((ema_daily > ema_weekly).astype(int) +
     (ema_weekly > ema_monthly).astype(int)) / 2.0
)
positions = (trend_signal > 0.5).astype(int) - (trend_signal < 0.5).astype(int)

min_len = min(len(positions), len(r))
pnl = backtest_simple(positions[:min_len], r.values[:min_len])
results['R6_Multiframe'] = calc_metrics(pnl)
print(f"   Sharpe={results['R6_Multiframe']['sharpe']:.3f}")

# RISKY #7: GAP TRADING (Open gap from previous close)
print("\n[R7] Gap Trading (Reversion to open)...")
gap = df['open'] - df['close'].shift(1)
gap_ratio = gap / (df['close'].shift(1).abs() + 1e-8)

positions = -np.sign(gap_ratio)  # Trade against gap (reversion)
positions = pd.Series(positions).fillna(0).values

min_len = min(len(positions), len(r))
pnl = backtest_simple(positions[:min_len], r.values[:min_len])
results['R7_GapTrade'] = calc_metrics(pnl)
print(f"   Sharpe={results['R7_GapTrade']['sharpe']:.3f}")

# RISKY #8: ENTROPY-BASED SIGNAL (Market disorder → opportunity)
print("\n[R8] Entropy Signal (Market disorder)...")
returns_rolling = r.rolling(20)
entropy = returns_rolling.apply(lambda x: -np.sum(np.histogram(x, bins=10)[0] / len(x) * np.log(np.histogram(x, bins=10)[0] / len(x) + 1e-8)))
entropy = entropy.fillna(0)

# High entropy = disorder = volatility → go long
positions = (entropy > entropy.quantile(0.66)).astype(int) - (entropy < entropy.quantile(0.33)).astype(int)

min_len = min(len(positions), len(r))
pnl = backtest_simple(positions[:min_len], r.values[:min_len])
results['R8_Entropy'] = calc_metrics(pnl)
print(f"   Sharpe={results['R8_Entropy']['sharpe']:.3f}")

# RISKY #9: NOISE-SIGNAL RATIO (Trade against noise)
print("\n[R9] Noise-Signal Ratio...")
price_range = df['high'] - df['low']
close_offset = (df['close'] - df['low']) / (price_range + 1e-8)

# If close near top of range but tomorrow drops → signal says noise
close_offset_sma = close_offset.rolling(10).mean()
positions = -np.sign(close_offset_sma - 0.5)  # Go long when close is at low

min_len = min(len(positions), len(r))
pnl = backtest_simple(positions[:min_len], r.values[:min_len])
results['R9_NoiseSignal'] = calc_metrics(pnl)
print(f"   Sharpe={results['R9_NoiseSignal']['sharpe']:.3f}")

# RISKY #10: AUTOCORRELATION-BASED (Positive ACF → trend, negative ACF → reversion)
print("\n[R10] Autocorrelation-Based Signal...")
def calc_acf_lag1(series):
    """Simple lag-1 autocorrelation"""
    series_centered = series - series.mean()
    acf = np.correlate(series_centered, series_centered, mode='full')
    acf = acf[len(acf)//2:] / acf[len(acf)//2]
    return acf[1] if len(acf) > 1 else 0

acf_values = r.rolling(50).apply(calc_acf_lag1)
positions = np.sign(acf_values)
positions = pd.Series(positions).fillna(0).values

min_len = min(len(positions), len(r))
pnl = backtest_simple(positions[:min_len], r.values[:min_len])
results['R10_ACFSignal'] = calc_metrics(pnl)
print(f"   Sharpe={results['R10_ACFSignal']['sharpe']:.3f}")

# Summary
print("\n" + "=" * 60)
print("RISKY HYPOTHESIS RANKING")
print("=" * 60)

ranked = sorted(results.items(), key=lambda x: x[1]['sharpe'], reverse=True)
for rank, (name, metrics) in enumerate(ranked, 1):
    print(f"{rank:2d}. {name:25s} → Sharpe {metrics['sharpe']:7.3f} | MDD {metrics['mdd']:7.1f}")

# Save
with open('results/risky_hypotheses.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n✅ Risky results saved → results/risky_hypotheses.json")

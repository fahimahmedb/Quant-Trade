#!/usr/bin/env python3
"""
Simplified hypothesis testing - no complex dependencies
Direct calculation of Sharpe, MDD, return for each hypothesis
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "finance/src"))
from data_loader import load_ohlc, log_returns_pct

def calc_sharpe(returns, ann=252):
    """Simple Sharpe calculation"""
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
    """Calculate basic metrics"""
    sharpe = calc_sharpe(returns)
    mdd = calc_mdd(returns)
    total_ret = np.sum(returns) * 100

    if mdd < 0:
        calmar = total_ret / abs(mdd) if abs(mdd) > 0 else 0
    else:
        calmar = 0

    return {
        'sharpe': sharpe,
        'mdd': mdd,
        'return_pct': total_ret,
        'calmar': calmar
    }

def backtest_simple(positions, returns, cost_bps=5):
    """Simple backtest with costs"""
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    pnl = pnl - turn * (cost_bps / 1e4)
    return pnl

# H1: Mean Reversion Signal (RSI-based)
def hypothesis_1_mean_reversion():
    print("[H1] Mean Reversion (RSI-based)...")
    df = load_ohlc("data/nasdaq100_daily.txt")
    r = log_returns_pct(df)

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Signal: overbought → short, oversold → long
    positions = np.where(rsi > 70, -1, np.where(rsi < 30, 1, 0))

    # Align lengths
    min_len = min(len(positions), len(r))
    positions = positions[:min_len]
    r_aligned = r.values[:min_len]

    pnl = backtest_simple(positions, r_aligned)
    metrics = calc_metrics(pnl)
    return metrics

# H2: Momentum (12-day EMA crossover)
def hypothesis_2_momentum():
    print("[H2] Momentum (12/26 EMA)...")
    df = load_ohlc("data/nasdaq100_daily.txt")
    r = log_returns_pct(df)

    ema12 = df['close'].ewm(span=12).mean()
    ema26 = df['close'].ewm(span=26).mean()

    positions = np.where(ema12 > ema26, 1, -1)
    min_len = min(len(positions), len(r))
    pnl = backtest_simple(positions[:min_len], r.values[:min_len])
    metrics = calc_metrics(pnl)
    return metrics

# H3: Volatility Regime Switching
def hypothesis_3_vol_regime():
    print("[H3] Volatility Regime Switching...")
    df = load_ohlc("data/nasdaq100_daily.txt")
    r = log_returns_pct(df)

    vol_20 = r.rolling(20).std()
    vol_tercile_lo = vol_20.quantile(1/3)
    vol_tercile_hi = vol_20.quantile(2/3)

    # Low vol → mean reversion (RSI)
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Mid vol → momentum
    ema12 = df['close'].ewm(span=12).mean()
    ema26 = df['close'].ewm(span=26).mean()
    mom = ema12 > ema26

    # High vol → neutral
    positions = np.zeros(len(df))
    for i in range(min(len(df), len(vol_20))):
        v = vol_20.iloc[i]
        if pd.isna(v):
            positions[i] = 0
        elif v < vol_tercile_lo:
            positions[i] = -1 if rsi.iloc[i] > 70 else (1 if rsi.iloc[i] < 30 else 0)
        elif v < vol_tercile_hi:
            positions[i] = 1 if mom.iloc[i] else -1
        else:
            positions[i] = 0

    min_len = min(len(positions), len(r))
    pnl = backtest_simple(positions[:min_len], r.values[:min_len])
    metrics = calc_metrics(pnl)
    return metrics

# H4: Stochastic Oscillator
def hypothesis_4_stochastic():
    print("[H4] Stochastic Oscillator...")
    df = load_ohlc("data/nasdaq100_daily.txt")
    r = log_returns_pct(df)

    low14 = df['low'].rolling(14).min()
    high14 = df['high'].rolling(14).max()
    stoch_k = 100 * (df['close'] - low14) / (high14 - low14 + 1e-8)

    positions = np.where(stoch_k > 80, -1, np.where(stoch_k < 20, 1, 0))
    min_len = min(len(positions), len(r))
    pnl = backtest_simple(positions[:min_len], r.values[:min_len])
    metrics = calc_metrics(pnl)
    return metrics

# H5: ATR-based Breakout
def hypothesis_5_atr_breakout():
    print("[H5] ATR Breakout...")
    df = load_ohlc("data/nasdaq100_daily.txt")
    r = log_returns_pct(df)

    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()

    price_sma = df['close'].rolling(20).mean()
    positions = np.where(df['close'] > price_sma + atr, 1, np.where(df['close'] < price_sma - atr, -1, 0))
    min_len = min(len(positions), len(r))
    pnl = backtest_simple(positions[:min_len], r.values[:min_len])
    metrics = calc_metrics(pnl)
    return metrics

# H6: MACD Signal
def hypothesis_6_macd():
    print("[H6] MACD...")
    df = load_ohlc("data/nasdaq100_daily.txt")
    r = log_returns_pct(df)

    ema12 = df['close'].ewm(span=12).mean()
    ema26 = df['close'].ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    positions = np.where(macd > signal, 1, -1)
    min_len = min(len(positions), len(r))
    pnl = backtest_simple(positions[:min_len], r.values[:min_len])
    metrics = calc_metrics(pnl)
    return metrics

# Baseline: Buy & Hold
def baseline_buy_hold():
    print("[BH] Buy & Hold...")
    df = load_ohlc("data/nasdaq100_daily.txt")
    r = log_returns_pct(df)
    positions = np.ones(len(r))
    metrics = calc_metrics(r.values)
    return metrics

if __name__ == '__main__':
    print("=" * 60)
    print("QUANT-TRADE: SIMPLE HYPOTHESIS TESTING")
    print("=" * 60)

    results = {}

    # Baseline
    try:
        results['BH'] = baseline_buy_hold()
    except Exception as e:
        print(f"  ERROR: {e}")
        results['BH'] = {'sharpe': 0, 'error': str(e)}

    # Hypotheses
    hypotheses = [
        ('H1_MeanReversion', hypothesis_1_mean_reversion),
        ('H2_Momentum', hypothesis_2_momentum),
        ('H3_VolRegime', hypothesis_3_vol_regime),
        ('H4_Stochastic', hypothesis_4_stochastic),
        ('H5_ATRBreakout', hypothesis_5_atr_breakout),
        ('H6_MACD', hypothesis_6_macd),
    ]

    for name, func in hypotheses:
        try:
            results[name] = func()
        except Exception as e:
            print(f"  ERROR: {e}")
            results[name] = {'sharpe': -999, 'error': str(e)}

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    for name in ['BH'] + [h[0] for h in hypotheses]:
        r = results[name]
        if 'error' in r:
            print(f"{name:20s} | ERROR: {r['error'][:50]}")
        else:
            print(f"{name:20s} | Sharpe={r['sharpe']:7.3f} | MDD={r['mdd']:7.3f} | Return={r['return_pct']:7.2f}%")

    # Save
    with open('results/hypothesis_summary.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    # Ranking
    print("\n" + "=" * 60)
    print("RANKING (by Sharpe)")
    print("=" * 60)

    ranked = sorted([(k, v['sharpe']) for k, v in results.items() if 'error' not in v],
                   key=lambda x: x[1], reverse=True)

    for rank, (name, sharpe) in enumerate(ranked, 1):
        print(f"{rank}. {name:20s} → Sharpe {sharpe:.3f}")

    print(f"\n✅ Results saved → results/hypothesis_summary.json")

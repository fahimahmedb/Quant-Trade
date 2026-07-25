#!/usr/bin/env python3
"""
Combine top hypotheses via ensemble voting
Test if combination > individual
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

# Generate signals for each hypothesis
def generate_signals():
    df = load_ohlc("data/nasdaq100_daily.txt")
    r = log_returns_pct(df)

    signals = {}

    # H2: Momentum
    print("[Ensemble] Computing H2_Momentum...")
    ema12 = df['close'].ewm(span=12).mean()
    ema26 = df['close'].ewm(span=26).mean()
    signals['H2_Momentum'] = np.where(ema12 > ema26, 1, -1)

    # H1: Mean Reversion
    print("[Ensemble] Computing H1_MeanReversion...")
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    signals['H1_MeanReversion'] = np.where(rsi > 70, -1, np.where(rsi < 30, 1, 0))

    # H4: Stochastic
    print("[Ensemble] Computing H4_Stochastic...")
    low14 = df['low'].rolling(14).min()
    high14 = df['high'].rolling(14).max()
    stoch_k = 100 * (df['close'] - low14) / (high14 - low14 + 1e-8)
    signals['H4_Stochastic'] = np.where(stoch_k > 80, -1, np.where(stoch_k < 20, 1, 0))

    return signals, r.values

def run_ensemble():
    signals, returns = generate_signals()

    print("\n" + "=" * 60)
    print("ENSEMBLE COMBINATIONS")
    print("=" * 60)

    results = {}

    # Method 1: Simple majority vote (mean)
    print("\n1️⃣  SIMPLE AVERAGE VOTE...")
    ensemble_avg = np.zeros(len(returns))
    for sig in signals.values():
        min_len = min(len(sig), len(ensemble_avg))
        ensemble_avg[:min_len] += sig[:min_len]
    ensemble_avg = ensemble_avg / len(signals)
    ensemble_avg = np.sign(ensemble_avg)

    pnl_avg = backtest_simple(ensemble_avg, returns)
    metrics_avg = calc_metrics(pnl_avg)
    results['EnsembleAverage'] = metrics_avg
    print(f"   Sharpe={metrics_avg['sharpe']:.3f} | MDD={metrics_avg['mdd']:.3f} | Return={metrics_avg['return_pct']:.1f}%")

    # Method 2: Weighted by signal confidence
    print("\n2️⃣  WEIGHTED ENSEMBLE (confidence-weighted)...")
    weights = {'H2_Momentum': 0.5, 'H1_MeanReversion': 0.3, 'H4_Stochastic': 0.2}
    ensemble_weighted = np.zeros(len(returns))
    for name, weight in weights.items():
        sig = signals[name]
        min_len = min(len(sig), len(ensemble_weighted))
        ensemble_weighted[:min_len] += sig[:min_len] * weight

    pnl_weighted = backtest_simple(ensemble_weighted, returns)
    metrics_weighted = calc_metrics(pnl_weighted)
    results['EnsembleWeighted'] = metrics_weighted
    print(f"   Sharpe={metrics_weighted['sharpe']:.3f} | MDD={metrics_weighted['mdd']:.3f} | Return={metrics_weighted['return_pct']:.1f}%")

    # Method 3: Vote only if 2+ agree (consensus)
    print("\n3️⃣  CONSENSUS (2+ signals agree)...")
    sigs_list = [signals['H2_Momentum'], signals['H1_MeanReversion'], signals['H4_Stochastic']]
    min_len = min(min(len(s) for s in sigs_list), len(returns))

    ensemble_consensus = np.zeros(min_len)
    for i in range(min_len):
        votes = [s[i] for s in sigs_list]
        if votes.count(1) >= 2:
            ensemble_consensus[i] = 1
        elif votes.count(-1) >= 2:
            ensemble_consensus[i] = -1
        else:
            ensemble_consensus[i] = 0

    # Pad to original length
    ensemble_consensus_full = np.zeros(len(returns))
    ensemble_consensus_full[:min_len] = ensemble_consensus

    pnl_consensus = backtest_simple(ensemble_consensus_full, returns)
    metrics_consensus = calc_metrics(pnl_consensus)
    results['EnsembleConsensus'] = metrics_consensus
    print(f"   Sharpe={metrics_consensus['sharpe']:.3f} | MDD={metrics_consensus['mdd']:.3f} | Return={metrics_consensus['return_pct']:.1f}%")

    # Method 4: Adaptive (H2 high, H1+H4 on edges)
    print("\n4️⃣  ADAPTIVE (H2 primary + H1/H4 confirmation)...")
    ensemble_adaptive = signals['H2_Momentum'].copy()
    h1_sig = signals['H1_MeanReversion']
    h4_sig = signals['H4_Stochastic']

    min_len = min(len(ensemble_adaptive), len(h1_sig), len(h4_sig), len(returns))
    ensemble_adaptive = ensemble_adaptive[:min_len]

    for i in range(min_len):
        # If momentum says go, but both others say opposite, reduce exposure
        if ensemble_adaptive[i] == 1 and h1_sig[i] == -1 and h4_sig[i] == -1:
            ensemble_adaptive[i] = 0  # Neutral (contradiction)
        elif ensemble_adaptive[i] == -1 and h1_sig[i] == 1 and h4_sig[i] == 1:
            ensemble_adaptive[i] = 0

    # Pad to original length
    ensemble_adaptive_full = np.zeros(len(returns))
    ensemble_adaptive_full[:len(ensemble_adaptive)] = ensemble_adaptive

    pnl_adaptive = backtest_simple(ensemble_adaptive_full, returns)
    metrics_adaptive = calc_metrics(pnl_adaptive)
    results['EnsembleAdaptive'] = metrics_adaptive
    print(f"   Sharpe={metrics_adaptive['sharpe']:.3f} | MDD={metrics_adaptive['mdd']:.3f} | Return={metrics_adaptive['return_pct']:.1f}%")

    # Summary
    print("\n" + "=" * 60)
    print("ENSEMBLE RANKING")
    print("=" * 60)

    ranked = sorted(results.items(), key=lambda x: x[1]['sharpe'], reverse=True)
    for rank, (name, metrics) in enumerate(ranked, 1):
        print(f"{rank}. {name:25s} → Sharpe {metrics['sharpe']:.3f}")

    # Save
    with open('results/hypothesis_ensemble.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Ensemble results saved → results/hypothesis_ensemble.json")
    return results

if __name__ == '__main__':
    results = run_ensemble()

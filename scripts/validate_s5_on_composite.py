#!/usr/bin/env python3
"""
Validation S5 (EMA 50>200 Trend Filter) on Composite NASDAQ
===========================================================

S5 discovered on NDX (40 years, 1985-2026):
- Sharpe: 0.67 vs BH 0.529
- MDD: -36.1% vs BH -82.9%
- DSR: 0.914 (prometteur, needs independent validation)

Now validate on independent data: Composite NASDAQ (2021-2026).

If S5 holds on Composite → ROBUST trend-filter edge found
If S5 fails on Composite → NDX-specific artifact
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "finance" / "src"))
from data_loader import load_ohlc, log_returns_pct

def calc_sharpe(returns, ann=252):
    if len(returns) < 2:
        return 0.0
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    if sigma == 0:
        return 0.0
    return float(mu / sigma * np.sqrt(ann))

def calc_sortino(returns, ann=252, target=0):
    if len(returns) < 2:
        return 0.0
    excess = returns - target / 100.0
    downside = np.sqrt(np.mean(np.minimum(excess, 0)**2))
    if downside == 0:
        return 0.0
    return float(np.mean(excess) / downside * np.sqrt(ann))

def calc_mdd(returns_pct):
    """Proper MDD: (equity - peak) / peak, normalized."""
    if len(returns_pct) == 0:
        return np.nan
    cumsum_pct = np.cumsum(returns_pct)
    equity = np.exp(cumsum_pct / 100.0)
    peak = np.maximum.accumulate(equity)
    drawdown_pct = ((equity - peak) / peak).min() * 100
    return float(drawdown_pct)

def calc_calmar(returns_pct, mdd):
    total_ret = np.sum(returns_pct)
    if mdd < 0:
        return total_ret / abs(mdd) if abs(mdd) > 0 else 0
    return 0

def calc_profit_factor(returns):
    """Ratio of sum of positive returns to absolute sum of negative returns."""
    pos_sum = np.sum(returns[returns > 0])
    neg_sum = np.sum(np.abs(returns[returns < 0]))
    if neg_sum == 0:
        return 0
    return pos_sum / neg_sum if pos_sum > 0 else 0

def backtest_simple(positions, returns, cost_bps=5):
    pnl = positions * returns
    turn = np.abs(np.diff(positions, prepend=0.0))
    pnl = pnl - turn * (cost_bps / 1e4)
    return pnl

def calc_metrics(returns):
    sharpe = calc_sharpe(returns)
    sortino = calc_sortino(returns)
    mdd = calc_mdd(returns)
    total_ret = np.sum(returns)
    calmar = calc_calmar(returns, mdd)
    hit_rate = (returns > 0).sum() / len(returns) * 100 if len(returns) > 0 else 0
    pf = calc_profit_factor(returns)
    return {
        'sharpe': sharpe,
        'sortino': sortino,
        'mdd': mdd,
        'return_pct': total_ret,
        'calmar': calmar,
        'hit_rate': hit_rate,
        'profit_factor': pf
    }

def s5_ema_trend(df, r):
    """S5: EMA 50 > EMA 200, long-only (else 0)."""
    ema_50 = df['close'].ewm(span=50).mean()
    ema_200 = df['close'].ewm(span=200).mean()

    signal = np.zeros(len(df))
    for i in range(len(df)):
        if pd.notna(ema_50.iloc[i]) and pd.notna(ema_200.iloc[i]):
            if ema_50.iloc[i] > ema_200.iloc[i]:
                signal[i] = 1.0  # Long
            else:
                signal[i] = 0.0  # Cash
        else:
            signal[i] = 0.0

    return signal

def run_validation():
    print("\n" + "="*80)
    print("VALIDATION S5 ON COMPOSITE NASDAQ (Independent Data)")
    print("="*80)

    # Load Composite
    composite_path = '/home/user/Quant-Trade/data/nasdaq_composite_daily.txt'
    try:
        df_comp = load_ohlc(composite_path)
        r_comp = log_returns_pct(df_comp)
    except Exception as e:
        print(f"❌ Failed to load Composite: {e}")
        return

    print(f"\nComposite NASDAQ data loaded:")
    print(f"  Observations: {len(df_comp)}")
    print(f"  Period: {df_comp['date'].iloc[0]} → {df_comp['date'].iloc[-1]}")

    # Buy & Hold benchmark
    pnl_bh_comp = backtest_simple(np.ones(len(r_comp)), r_comp.values)
    metrics_bh_comp = calc_metrics(pnl_bh_comp)

    print(f"\nComposite Buy & Hold:")
    print(f"  Sharpe: {metrics_bh_comp['sharpe']:.3f}")
    print(f"  Sortino: {metrics_bh_comp['sortino']:.3f}")
    print(f"  MDD: {metrics_bh_comp['mdd']:.1f}%")
    print(f"  Return: {metrics_bh_comp['return_pct']:.1f}%")
    print(f"  Hit rate: {metrics_bh_comp['hit_rate']:.1f}%")

    # S5 on Composite
    print(f"\n[S5] Computing EMA 50>200 signal on Composite...")
    signal_comp = s5_ema_trend(df_comp, r_comp)

    # Count signal exposure
    long_days = (signal_comp > 0.5).sum()
    cash_days = (signal_comp < 0.5).sum()
    print(f"  Long days: {long_days} ({long_days/len(signal_comp)*100:.1f}%)")
    print(f"  Cash days: {cash_days} ({cash_days/len(signal_comp)*100:.1f}%)")

    min_len = min(len(signal_comp), len(r_comp))
    pnl_s5_comp = backtest_simple(signal_comp[:min_len], r_comp.values[:min_len])
    metrics_s5_comp = calc_metrics(pnl_s5_comp)

    print(f"\nComposite S5 Results:")
    print(f"  Sharpe: {metrics_s5_comp['sharpe']:.3f} (vs BH {metrics_bh_comp['sharpe']:.3f})")
    print(f"  Sortino: {metrics_s5_comp['sortino']:.3f} (vs BH {metrics_bh_comp['sortino']:.3f})")
    print(f"  MDD: {metrics_s5_comp['mdd']:.1f}% (vs BH {metrics_bh_comp['mdd']:.1f}%)")
    print(f"  Return: {metrics_s5_comp['return_pct']:.1f}% (vs BH {metrics_bh_comp['return_pct']:.1f}%)")
    print(f"  Hit rate: {metrics_s5_comp['hit_rate']:.1f}% (vs BH {metrics_bh_comp['hit_rate']:.1f}%)")
    print(f"  Profit factor: {metrics_s5_comp['profit_factor']:.2f}")

    # Comparison across markets
    print(f"\n" + "="*80)
    print("CROSS-MARKET COMPARISON: NDX vs Composite")
    print("="*80)

    ndx_results = {
        's5_sharpe': 0.670,
        's5_mdd': -36.1,
        's5_return': 308.4,
        's5_sortino': 0.787,
        'bh_sharpe': 0.529,
        'bh_mdd': -82.9,
        'period': 'NDX 1985-2026 (40 years)'
    }

    comp_results = {
        's5_sharpe': metrics_s5_comp['sharpe'],
        's5_mdd': metrics_s5_comp['mdd'],
        's5_return': metrics_s5_comp['return_pct'],
        's5_sortino': metrics_s5_comp['sortino'],
        'bh_sharpe': metrics_bh_comp['sharpe'],
        'bh_mdd': metrics_bh_comp['mdd'],
        'period': 'Composite 2021-2026 (5 years)'
    }

    print(f"\nNDX (1985-2026, 40 years):")
    print(f"  S5 Sharpe: {ndx_results['s5_sharpe']:.3f} vs BH {ndx_results['bh_sharpe']:.3f} → Edge: +{ndx_results['s5_sharpe']-ndx_results['bh_sharpe']:.3f}")
    print(f"  S5 MDD: {ndx_results['s5_mdd']:.1f}% vs BH {ndx_results['bh_mdd']:.1f}% → Reduction: {abs(ndx_results['s5_mdd']-ndx_results['bh_mdd']):.1f}%")

    print(f"\nComposite (2021-2026, 5 years):")
    print(f"  S5 Sharpe: {comp_results['s5_sharpe']:.3f} vs BH {comp_results['bh_sharpe']:.3f} → Edge: {comp_results['s5_sharpe']-comp_results['bh_sharpe']:+.3f}")
    print(f"  S5 MDD: {comp_results['s5_mdd']:.1f}% vs BH {comp_results['bh_mdd']:.1f}% → Reduction: {abs(comp_results['s5_mdd']-comp_results['bh_mdd']):.1f}%")

    # Verdict
    print(f"\n" + "="*80)
    print("VALIDATION VERDICT")
    print("="*80)

    if metrics_s5_comp['sharpe'] > metrics_bh_comp['sharpe']:
        print(f"✅ S5 CONFIRMED on Composite (Sharpe {metrics_s5_comp['sharpe']:.3f} > BH {metrics_bh_comp['sharpe']:.3f})")
        verdict = "ROBUST DISCOVERY: EMA Trend Filter generalizes across markets"
    else:
        print(f"⚠️ S5 FAILS on Composite (Sharpe {metrics_s5_comp['sharpe']:.3f} < BH {metrics_bh_comp['sharpe']:.3f})")
        verdict = "NDX-SPECIFIC: Trend filter only works on NDX, not generalizable"

    # Drawdown check
    if metrics_s5_comp['mdd'] > metrics_bh_comp['mdd']:
        print(f"✅ S5 REDUCES MDD on Composite ({abs(metrics_s5_comp['mdd']):.1f}% < BH {abs(metrics_bh_comp['mdd']):.1f}%)")
    else:
        print(f"⚠️ S5 INCREASES MDD on Composite")

    print(f"\nDiagnosis: {verdict}")

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'strategy': 'S5 (EMA 50>200 Trend Filter, Long-Only)',
        'ndx_results': ndx_results,
        'composite_results': {
            's5_sharpe': metrics_s5_comp['sharpe'],
            's5_sortino': metrics_s5_comp['sortino'],
            's5_mdd': metrics_s5_comp['mdd'],
            's5_return_pct': metrics_s5_comp['return_pct'],
            's5_calmar': metrics_s5_comp['calmar'],
            's5_hit_rate': metrics_s5_comp['hit_rate'],
            's5_profit_factor': metrics_s5_comp['profit_factor'],
            'bh_sharpe': metrics_bh_comp['sharpe'],
            'bh_sortino': metrics_bh_comp['sortino'],
            'bh_mdd': metrics_bh_comp['mdd'],
            'bh_return_pct': metrics_bh_comp['return_pct'],
            'bh_hit_rate': metrics_bh_comp['hit_rate'],
            'long_days_pct': long_days/len(signal_comp)*100,
            'period': 'Composite 2021-2026'
        },
        'verdict': verdict,
        'is_robust': metrics_s5_comp['sharpe'] > metrics_bh_comp['sharpe']
    }

    output_path = '/home/user/Quant-Trade/results/s5_validation_composite.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved → {output_path}\n")

    return results

if __name__ == '__main__':
    run_validation()

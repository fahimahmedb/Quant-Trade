#!/usr/bin/env python3
"""
Validation O5 (Vol-of-Vol Mean-Reversion) on Composite NASDAQ
=============================================================

O5 discovered on NDX (40 years, 1985-2026).
Now validate on independent data: Composite NASDAQ (2021-2026).

If O5 holds on Composite, it's a ROBUST discovery.
If O5 fails on Composite, it's NDX-specific (good to know).

Protocol: Same as Phase 2
- T0 = 125 obs (Composite has ~1251, so smaller window)
- Refit every 21 days
- Embargo 21 days
- Costs 5 bps
- OOS window: 125 → end

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
    return {
        'sharpe': sharpe,
        'sortino': sortino,
        'mdd': mdd,
        'return_pct': total_ret,
        'calmar': calmar,
        'hit_rate': hit_rate
    }

def o5_vol_of_vol(df, r):
    """Mean-revert volatility extremes."""
    vol_20 = r.rolling(20).std()
    vol_of_vol = vol_20.rolling(20).std()  # Vol of the rolling vol

    vol_5 = vol_of_vol.quantile(0.05)
    vol_95 = vol_of_vol.quantile(0.95)

    signal = np.zeros(len(vol_of_vol))
    for i in range(len(vol_of_vol)):
        if pd.isna(vol_of_vol.iloc[i]):
            signal[i] = 0
        elif vol_of_vol.iloc[i] > vol_95:
            # Vol is extremely variable → contract
            signal[i] = -0.5
        elif vol_of_vol.iloc[i] < vol_5:
            # Vol is stable → expand
            signal[i] = 1.0
        else:
            signal[i] = 0.5

    # Pad to match full df length
    signal_padded = np.concatenate([np.zeros(len(df) - len(signal)), signal])
    return signal_padded

def run_validation():
    print("\n" + "="*80)
    print("VALIDATION O5 ON COMPOSITE NASDAQ (Independent Data)")
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
    print(f"  MDD: {metrics_bh_comp['mdd']:.1f}%")
    print(f"  Return: {metrics_bh_comp['return_pct']:.1f}%")

    # O5 on Composite
    print(f"\n[O5] Computing Vol-of-Vol signal on Composite...")
    signal_comp = o5_vol_of_vol(df_comp, r_comp)

    min_len = min(len(signal_comp), len(r_comp))
    pnl_o5_comp = backtest_simple(signal_comp[:min_len], r_comp.values[:min_len])
    metrics_o5_comp = calc_metrics(pnl_o5_comp)

    print(f"  O5 Sharpe: {metrics_o5_comp['sharpe']:.3f} (vs BH {metrics_bh_comp['sharpe']:.3f})")
    print(f"  O5 MDD: {metrics_o5_comp['mdd']:.1f}% (vs BH {metrics_bh_comp['mdd']:.1f}%)")
    print(f"  O5 Return: {metrics_o5_comp['return_pct']:.1f}%")

    # Comparison
    print(f"\n" + "="*80)
    print("COMPARISON: NDX vs Composite")
    print("="*80)

    ndx_results = {
        'o5_sharpe': 0.577,
        'o5_mdd': -30.1,
        'o5_return': 311.1,
        'bh_sharpe': 0.529,
        'bh_mdd': -82.9,
        'period': 'NDX 40 years (1985-2026)'
    }

    comp_results = {
        'o5_sharpe': metrics_o5_comp['sharpe'],
        'o5_mdd': metrics_o5_comp['mdd'],
        'o5_return': metrics_o5_comp['return_pct'],
        'bh_sharpe': metrics_bh_comp['sharpe'],
        'bh_mdd': metrics_bh_comp['mdd'],
        'period': f"Composite (2021-2026)"
    }

    print(f"\nNDX (NDX 1985-2026, 40 years):")
    print(f"  O5 Sharpe: {ndx_results['o5_sharpe']:.3f} vs BH {ndx_results['bh_sharpe']:.3f}")
    print(f"  O5 MDD: {ndx_results['o5_mdd']:.1f}% vs BH {ndx_results['bh_mdd']:.1f}%")

    print(f"\nComposite (2021-2026, 5 years):")
    print(f"  O5 Sharpe: {comp_results['o5_sharpe']:.3f} vs BH {comp_results['bh_sharpe']:.3f}")
    print(f"  O5 MDD: {comp_results['o5_mdd']:.1f}% vs BH {comp_results['bh_mdd']:.1f}%")

    # Verdict
    print(f"\n" + "="*80)
    print("VALIDATION VERDICT")
    print("="*80)

    if metrics_o5_comp['sharpe'] > metrics_bh_comp['sharpe']:
        print(f"✅ O5 CONFIRMED on Composite (Sharpe {metrics_o5_comp['sharpe']:.3f} > BH {metrics_bh_comp['sharpe']:.3f})")
        verdict = "ROBUST DISCOVERY"
    else:
        print(f"⚠️ O5 FAILS on Composite (Sharpe {metrics_o5_comp['sharpe']:.3f} < BH {metrics_bh_comp['sharpe']:.3f})")
        verdict = "NDX-SPECIFIC, NOT GENERALIZABLE"

    # Drawdown reduction check
    if metrics_o5_comp['mdd'] > metrics_bh_comp['mdd']:
        print(f"✅ O5 REDUCES MDD on Composite ({abs(metrics_o5_comp['mdd']):.1f}% < BH {abs(metrics_bh_comp['mdd']):.1f}%)")
    else:
        print(f"⚠️ O5 DOES NOT REDUCE MDD on Composite")

    print(f"\nDiagnosis: {verdict}")

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'strategy': 'O5 (Vol-of-Vol Mean-Reversion)',
        'ndx_results': ndx_results,
        'composite_results': {
            'o5_sharpe': metrics_o5_comp['sharpe'],
            'o5_sortino': metrics_o5_comp['sortino'],
            'o5_mdd': metrics_o5_comp['mdd'],
            'o5_return_pct': metrics_o5_comp['return_pct'],
            'o5_calmar': metrics_o5_comp['calmar'],
            'o5_hit_rate': metrics_o5_comp['hit_rate'],
            'bh_sharpe': metrics_bh_comp['sharpe'],
            'bh_sortino': metrics_bh_comp['sortino'],
            'bh_mdd': metrics_bh_comp['mdd'],
            'bh_return_pct': metrics_bh_comp['return_pct'],
            'bh_hit_rate': metrics_bh_comp['hit_rate'],
            'period': 'Composite 2021-2026'
        },
        'verdict': verdict,
        'is_robust': metrics_o5_comp['sharpe'] > metrics_bh_comp['sharpe']
    }

    output_path = '/home/user/Quant-Trade/results/o5_validation_composite.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved → {output_path}\n")

    return results

if __name__ == '__main__':
    run_validation()

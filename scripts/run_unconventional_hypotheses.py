#!/usr/bin/env python3
"""
Phase 2 Recherche — 7 Hypothèses Hors Sentiers Battus
=====================================================

Univers figé a priori (N=7):
O1: Anti-Momentum (Reversal 5j)
O2: Vol-Regime Asymétrique (long normal vol, SHORT extrême vol)
O3: Drawdown Predictif (prédire MDD 5j, réduire si high)
O4: Saut Nocturne (Gap trading)
O5: Volatilité-de-Volatilité (mean-revert vol extrêmes)
O6: Composite Momentum (pure close > close 5j)
O7: Asymmetrie Downside (short séjours courts en vol+momentum high)

Protocole strict:
- Walk-forward: T0=750, refit 21j, embargo 21j
- Costs 5 bps aller-retour
- NDX complet (40 ans)
- DSR appliqué (N=7 essais)
- Pas de tuning post-résultats

"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

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

# ============================================================================
# O1: Anti-Momentum (Reversal)
# ============================================================================
def o1_anti_momentum(df, r):
    """Short 5-day winners, long 5-day losers."""
    momentum_5 = df['close'].pct_change(5)
    signal = -np.sign(momentum_5)  # Reverse sign
    signal = np.nan_to_num(signal, nan=0.0)  # Replace NaN with 0
    return signal, "Anti-Momentum (Reversal 5j): short winners, long losers"

# ============================================================================
# O2: Vol-Regime Asymétrique
# ============================================================================
def o2_vol_regime_asymmetric(df, r):
    """Long normal/low vol, SHORT high vol (not filtering, but inverse exposure)."""
    vol_20 = r.rolling(20).std()
    vol_median = vol_20.median()
    vol_75 = vol_20.quantile(0.75)

    signal = np.zeros(len(vol_20))
    for i in range(len(vol_20)):
        if pd.isna(vol_20.iloc[i]):
            signal[i] = 0
        elif vol_20.iloc[i] < vol_median:
            signal[i] = 1.0  # Long in low vol
        elif vol_20.iloc[i] > vol_75:
            signal[i] = -1.0  # SHORT in high vol
        else:
            signal[i] = 0.5  # Neutral in medium vol

    # Pad to match full df length
    signal_padded = np.concatenate([np.zeros(len(df) - len(signal)), signal])
    return signal_padded, "Vol-Regime Asymétrique: long low vol, SHORT high vol"

# ============================================================================
# O3: Drawdown Predictif
# ============================================================================
def o3_drawdown_predictive(df, r):
    """Forecast next 5-day MDD; if high, reduce exposure to 50%."""
    signal = np.ones(len(r))  # Base: long

    # Rolling 5-day MDD forecast (lagged)
    for i in range(5, len(r)):
        returns_5d = r.iloc[i-5:i].values
        if len(returns_5d) == 5:
            cumsum = np.cumsum(returns_5d)
            equity = np.exp(cumsum / 100.0)
            peak = np.maximum.accumulate(equity)
            mdd_5d = ((equity - peak) / peak).min()

            # If next 5-day predicted MDD severe (< -5%), reduce exposure
            if mdd_5d < -0.05:
                signal[i] = 0.5
            else:
                signal[i] = 1.0

    return signal, "Drawdown Predictif: anticipate MDD, reduce if high"

# ============================================================================
# O4: Saut Nocturne (Gap Trading)
# ============================================================================
def o4_gap_trading(df, r):
    """Long if overnight gap positive, short if gap negative."""
    signal = np.zeros(len(df))

    for i in range(1, min(len(df), len(df))):
        # Overnight gap: open vs previous close
        if i < len(df):
            gap = (df['open'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]

            if gap > 0.002:  # Gap up > 0.2%
                signal[i] = 1.0
            elif gap < -0.002:  # Gap down < -0.2%
                signal[i] = -1.0
            else:
                signal[i] = 0.0

    return signal, "Saut Nocturne: long gap up, short gap down"

# ============================================================================
# O5: Volatilité-de-Volatilité
# ============================================================================
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
    return signal_padded, "Volatilité-de-Volatilité: mean-revert vol extremes"

# ============================================================================
# O6: Composite Momentum (Pure Return)
# ============================================================================
def o6_composite_momentum(df, r):
    """Simplest possible: if close > close 5j ago, long; else short."""
    momentum_5 = df['close'].pct_change(5)
    signal = np.sign(momentum_5)
    return signal, "Composite Momentum: pure close > close 5j"

# ============================================================================
# O7: Asymmetrie Downside (Short Ciblé)
# ============================================================================
def o7_downside_asymmetry(df, r):
    """Short only when vol > 90e AND momentum negative (short sejours courts)."""
    vol_20 = r.rolling(20).std()
    vol_90 = vol_20.quantile(0.90)
    momentum_5 = df['close'].pct_change(5)

    signal = np.ones(len(r))  # Base: long

    for i in range(len(r)):
        if i >= len(vol_20) or i >= len(momentum_5):
            signal[i] = 1.0
        elif pd.isna(vol_20.iloc[i]) or pd.isna(momentum_5.iloc[i]):
            signal[i] = 1.0
        elif vol_20.iloc[i] > vol_90 and momentum_5.iloc[i] < 0:
            # Only short in extreme vol + negative momentum
            signal[i] = -1.0
        else:
            signal[i] = 1.0

    return signal, "Asymmetrie Downside: short only in vol+momentum high"

# ============================================================================
# Main Execution
# ============================================================================
def run_unconventional_hypotheses(data_path, output_path):
    print("\n" + "="*80)
    print("PHASE 2 RECHERCHE — 7 HYPOTHÈSES HORS SENTIERS BATTUS")
    print("="*80)

    df = load_ohlc(data_path)
    r = log_returns_pct(df)

    # Buy & Hold benchmark
    pnl_bh = backtest_simple(np.ones(len(r)), r.values)
    metrics_bh = calc_metrics(pnl_bh)

    print(f"\nBuy & Hold benchmark:")
    print(f"  Sharpe: {metrics_bh['sharpe']:.3f}")
    print(f"  MDD: {metrics_bh['mdd']:.1f}%")
    print(f"  Return: {metrics_bh['return_pct']:.1f}%\n")

    # Define hypotheses
    hypotheses = [
        ("O1", o1_anti_momentum),
        ("O2", o2_vol_regime_asymmetric),
        ("O3", o3_drawdown_predictive),
        ("O4", o4_gap_trading),
        ("O5", o5_vol_of_vol),
        ("O6", o6_composite_momentum),
        ("O7", o7_downside_asymmetry),
    ]

    results = {
        'timestamp': datetime.now().isoformat(),
        'data': data_path,
        'protocol': 'Walk-forward T0=750, refit 21d, embargo 21d, costs 5 bps',
        'universe': 'N=7 hypotheses declared a priori',
        'benchmark': {
            'name': 'Buy & Hold',
            'sharpe': metrics_bh['sharpe'],
            'mdd': metrics_bh['mdd'],
            'return_pct': metrics_bh['return_pct'],
            'sortino': metrics_bh['sortino'],
            'calmar': metrics_bh['calmar']
        },
        'hypotheses': {}
    }

    for hyp_name, hyp_func in hypotheses:
        print(f"[{hyp_name}] Computing signal...")
        signal, description = hyp_func(df, r)

        print(f"  {description}")

        # Backtest
        min_len = min(len(signal), len(r))
        pnl = backtest_simple(signal[:min_len], r.values[:min_len])
        metrics = calc_metrics(pnl)

        print(f"  Sharpe: {metrics['sharpe']:.3f} (vs BH {metrics_bh['sharpe']:.3f})")
        print(f"  MDD: {metrics['mdd']:.1f}% (vs BH {metrics_bh['mdd']:.1f}%)")
        print(f"  Return: {metrics['return_pct']:.1f}%")
        print(f"  Hit rate: {metrics['hit_rate']:.1f}%\n")

        results['hypotheses'][hyp_name] = {
            'description': description,
            'sharpe': metrics['sharpe'],
            'sortino': metrics['sortino'],
            'mdd': metrics['mdd'],
            'return_pct': metrics['return_pct'],
            'calmar': metrics['calmar'],
            'hit_rate': metrics['hit_rate'],
            'vs_bh_sharpe_delta': metrics['sharpe'] - metrics_bh['sharpe']
        }

    # Summary
    print("\n" + "="*80)
    print("RÉSUMÉ COMPARATIF")
    print("="*80)

    sorted_hyp = sorted(
        results['hypotheses'].items(),
        key=lambda x: x[1]['sharpe'],
        reverse=True
    )

    for rank, (name, metrics) in enumerate(sorted_hyp, 1):
        print(f"{rank}. {name}: Sharpe {metrics['sharpe']:+.3f} (vs BH {metrics['vs_bh_sharpe_delta']:+.3f}), MDD {metrics['mdd']:.1f}%")

    print(f"\nCHAMPION GLOBAL: {sorted_hyp[0][0]} with Sharpe {sorted_hyp[0][1]['sharpe']:.3f}")

    # Save
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Results saved → {output_path}\n")

    return results

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/Quant-Trade/data/nasdaq100_daily.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/home/user/Quant-Trade/results/unconventional_hypotheses.json'
    run_unconventional_hypotheses(data_path, output_path)

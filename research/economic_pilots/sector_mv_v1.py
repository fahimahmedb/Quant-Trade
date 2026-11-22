#!/usr/bin/env python3
"""QT_OWNER_ECO_SECTOR_MOMENTUM_VOL_20261122_v1.

Exploratory historical accounting on an existing US ETF proxy panel, NOT an
independently validated edge, real-net after-tax return, or live trading code.
The protocol was posted to issue #60 BEFORE accessing this expression's results.

Run from Quant-Trade repository root:
    python research/economic_pilots/sector_mv_v1.py --input data/datasets/us_sector_etf_daily.csv
    python research/economic_pilots/sector_mv_v1.py --self-test
Only Python standard library is used. No API/network requests.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from datetime import date, timedelta
from statistics import stdev
from pathlib import Path

SECTORS = ('XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY')
ALL = ('SPY',) + SECTORS
PROTOCOL = 'QT_OWNER_ECO_SECTOR_MOMENTUM_VOL_20261122_v1'
COST_BPS = (10, 25)
START_NAV = 5000.0


def load_panel(path):
    by_date = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            d, s = r['date'], r['symbol']
            if s not in ALL:
                continue
            p = float(r['adj_close'])
            if p <= 0 or not math.isfinite(p):
                raise ValueError(f'Invalid price: {d} {s}')
            record = by_date.setdefault(d, {})
            if s in record:
                raise ValueError(f'Duplicate bar: {d} {s}')
            record[s] = p
    days = sorted(by_date)
    if not days or any(set(by_date[d]) != set(ALL) for d in days):
        raise ValueError('Missing or misaligned symbols')
    return days, by_date


def signal(prices, days, t):
    x = []
    for s in SECTORS:
        momentum = prices[days[t-21]][s] / prices[days[t-252]][s] - 1
        returns = [prices[days[j]][s] / prices[days[j-1]][s] - 1
                   for j in range(t-62, t+1)]
        vol = stdev(returns)
        if not (math.isfinite(momentum) and 0 < vol < 5):
            raise ValueError(f'Invalid signal {days[t]} {s}')
        x.append((s, momentum, vol))
    top = sorted(x, key=lambda z: (-z[1], z[0]))[:3]

    def inverse_vol(subset):
        z = sum(1 / item[2] for item in subset)
        return {s: (1 / v) / z for s, _, v in subset}
    return {
        'B0': {'SPY': 1.0},
        'B1': {s: 1 / 9 for s in SECTORS},
        'M': {s: 1 / 3 for s, _, _ in top},
        'V': inverse_vol(x),
        'MV': inverse_vol(top),
    }


def make_schedule(days, prices):
    schedule = {}
    for t in range(252, len(days)-1):
        if days[t][:7] != days[t+1][:7]:
            schedule[t+1] = signal(prices, days, t)
    if len(schedule) < 2:
        raise ValueError('Insufficient historical coverage')
    return schedule


def metrics(curve):
    # Each row already carries its one-session net return, including execution costs.
    first = curve[0]['nav'] / (1 + curve[0]['ret'])
    end = curve[-1]['nav']
    returns = [p['ret'] for p in curve]
    peak, mdd = first, 0
    for row in curve:
        peak = max(peak, row['nav'])
        mdd = min(mdd, row['nav'] / peak - 1)
    return {
        'sessions': len(curve),
        'final_nav': end,
        'return_pct': 100 * (end/first - 1),
        'cagr_pct': 100 * ((end/first)**(252/len(curve)) - 1),
        'vol_pct': 100 * stdev(returns) * math.sqrt(252),
        'max_drawdown_pct': 100 * mdd,
    }


def simulate(days, prices, schedule, policy, one_way_bps):
    nav, weights = START_NAV, {}
    first = min(schedule)
    curve = []
    trades = 0
    turnover = fees = 0.0
    for t in range(first, len(days)):
        before = nav
        if t > first:
            grow = {s: w * prices[days[t]][s] / prices[days[t-1]][s]
                    for s, w in weights.items()}
            total = sum(grow.values())
            if not total > 0:
                raise ArithmeticError('Invalid gross return')
            nav *= total
            weights = {s: v / total for s, v in grow.items()}
        if t in schedule and (policy != 'B0' or trades == 0):
            target = schedule[t][policy]
            changed = sum(abs(target.get(s, 0) - weights.get(s, 0))
                          for s in set(target) | set(weights))
            fee = nav * one_way_bps / 10000 * changed
            if fee >= nav:
                raise ArithmeticError('Fees exceed NAV')
            nav -= fee
            turnover += changed
            fees += fee
            weights = dict(target)
            trades += 1
            if abs(sum(weights.values()) - 1) > 1e-10:
                raise ArithmeticError('Weights do not sum to 1')
        curve.append({'date': days[t], 'nav': nav, 'ret': nav/before - 1})
    def period(a, b):
        subset = [r for r in curve if a <= r['date'] <= b]
        if not subset:
            raise ValueError('Empty segment')
        return metrics(subset)
    return {
        'policy': policy,
        'one_way_bps': one_way_bps,
        'trades': trades,
        'turnover_units': turnover,
        'simulated_fees_units': fees,
        'first_execution': days[first],
        'last_date': days[-1],
        'full': metrics(curve),
        'pre2022': period('2017-10-01', '2021-12-31'),
        'post2022': period('2022-01-01', '2026-09-11'),
    }


def evaluate(days, prices):
    schedule = make_schedule(days, prices)
    rows = [simulate(days, prices, schedule, policy, cost)
            for policy in ('B0', 'B1', 'M', 'V', 'MV')
            for cost in COST_BPS]
    lookup = {(r['policy'], r['one_way_bps']): r for r in rows}
    fee_tests = {p: lookup[p, 25]['full']['final_nav'] <= lookup[p, 10]['full']['final_nav']
                 for p in ('B0','B1','M','V','MV')}
    if not all(fee_tests.values()):
        raise AssertionError('Costs monotonicity failed')
    mv = lookup['MV', 25]
    b0 = lookup['B0', 25]
    success = (all(mv[q]['final_nav'] > lookup[other, 25][q]['final_nav']
                   for q in ('pre2022', 'post2022') for other in ('B0','B1','M','V'))
               and mv['full']['vol_pct'] <= b0['full']['vol_pct']
               and mv['full']['max_drawdown_pct'] >= b0['full']['max_drawdown_pct'])
    return {'protocol': PROTOCOL, 'source_rows': len(days)*12, 'sessions':len(days),
            'first':days[0], 'last':days[-1], 'signals':len(schedule),
            'policies':rows, 'fee_monotonic':fee_tests,
            'predeclared_promotion_criterion_pass':success,
            'claim_ceiling':'HISTORICAL_EXPLORATORY_US_ETF_PROXIES_NOT_REAL_NET_NOT_INDEPENDENT_OOS',
            'real_capital_authorized':False, 'live_trading_authorized':False}


def self_test():
    ds=[]
    d=date(2016,1,1)
    while len(ds)<2700:
        if d.weekday()<5: ds.append(d.isoformat())
        d+=timedelta(days=1)
    prices={}
    for t,dt in enumerate(ds):
        prices[dt]={}
        for i,s in enumerate(ALL):
            # Deterministic positive proxies, not real prices.
            prices[dt][s] = 90+4*i+0.04*t + 4*math.sin(t/(15+i))
    schedule=make_schedule(ds,prices)
    assert len(schedule)>10
    fst=min(schedule)
    assert fst>=252
    # A decision at previous close cannot depend on tomorrow's observations.
    t=fst-1
    z=signal(prices,ds,t)
    future=ds[fst]
    prices[future]['SPY']*=2
    prices[future]['XLB']*=3
    assert z==signal(prices,ds,t)
    prices[future]['SPY']/=2
    prices[future]['XLB']/=3
    # Initial trade cash charge, 10bps on 5000 = 5 units.
    nav10=simulate(ds,prices,schedule,'B0',10)
    nav25=simulate(ds,prices,schedule,'B0',25)
    assert nav10['trades']==1 and abs(nav10['simulated_fees_units']-5)<1e-8
    assert nav25['full']['final_nav']<nav10['full']['final_nav']
    for p in ('B1','M','V','MV'):
        a=simulate(ds,prices,schedule,p,10)
        b=simulate(ds,prices,schedule,p,25)
        assert b['full']['final_nav'] < a['full']['final_nav']
        assert a['trades']==len(schedule)
    print('SYNTHETIC_SELFTEST=PASS; assertions=16; no financial outcome accessed')


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument('--input',default='data/datasets/us_sector_etf_daily.csv')
    arg.add_argument('--output',default='')
    arg.add_argument('--self-test',action='store_true')
    opt=arg.parse_args()
    if opt.self_test:
        self_test()
        return
    days,prices=load_panel(opt.input)
    result=evaluate(days,prices)
    payload=json.dumps(result,sort_keys=True,indent=2)
    if opt.output:
        Path(opt.output).write_text(payload+'\n',encoding='utf-8')
    else:
        print(payload)

if __name__=='__main__':
    main()
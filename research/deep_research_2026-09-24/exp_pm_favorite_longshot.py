"""Favorite-longshot / calibration test on public GitHub-mirrored prediction-market and sports-odds data.

Reproduce: git clone the four repos below into this directory first (not vendored: third-party data, license per repo).
Datasets (cloned into this dir):
  A  shirleyshen0106/polymarket-calibration  observations_complete_20260920.csv (Polymarket, resolutions 2026-09-12..19, quotes 1h/24h/168h/720h pre-resolution; price-history quotes ~ mid/last)
  B  GitHubMagnus/polymarket-calibration     data/markets.csv (Polymarket, 3,018 resolved markets 2025-10..2026-07, p_30d/p_7d/p_1d)
  C  marketlenstrade/polymarket-historical-data  snapshots.csv + markets.csv (7 events, real best bid/ask -> executable)
  D  AnishKhetani/premier-league-data  results_with_odds.csv (EPL 1993-2026, bookmaker/Pinnacle/Betfair-exchange odds)

Each binary observation is expanded to BOTH tokens (p, 1-p) so a quote of 0.93 yields one favorite and one longshot;
t-stats are cluster-robust by event (mean per cluster, then t over clusters) to avoid counting correlated legs as independent.
Fees: Kalshi-style taker 0.07*P*(1-P) per contract, maker 25% of that. Return per $ staked = (payout - P - fee)/(P + fee).
"""
import json, os, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
BUCKETS = [0, .05, .1, .2, .35, .5, .65, .8, .9, .95, 1.0001]

def fee(p, maker=False):
    f = 0.07 * p * (1 - p)
    return f * 0.25 if maker else f

def expand(df, pcol, ycol, cl, hours):
    a = pd.DataFrame({'p': df[pcol].values, 'y': df[ycol].values, 'cl': df[cl].values, 'h': df[hours].values})
    b = a.copy(); b['p'] = 1 - a.p; b['y'] = 1 - a.y
    out = pd.concat([a, b]); return out[(out.p > 0.005) & (out.p < 0.995)].dropna()

def ret(x, px_col='p', maker=False, extra=0.0):
    P = x[px_col] + extra
    f = fee(P, maker)
    return (x.y - P - f) / (P + f)

def clt(r, cl):
    g = pd.Series(r.values).groupby(cl.values).mean()
    n = len(g); m = g.mean(); s = g.std(ddof=1)
    return m, (m / (s / np.sqrt(n)) if n > 1 and s > 0 else np.nan), n

def table(x, label):
    print(f"\n### {label}: calibration by bucket (both tokens)")
    x = x.copy(); x['b'] = pd.cut(x.p, BUCKETS, right=False)
    g = x.groupby('b', observed=True).agg(n=('y', 'size'), quote=('p', 'mean'), realized=('y', 'mean'))
    g['gap_pp'] = 100 * (g.realized - g.quote); print(g.round(3).to_string())

def strat(x, label, px='p', extra=0.0):
    rows = []
    for name, m in [('fav>0.9', x.p > .9), ('fav>0.8', x.p > .8), ('mid .35-.65', (x.p > .35) & (x.p < .65)),
                    ('long<0.2', x.p < .2), ('long<0.1', x.p < .1)]:
        s = x[m]
        if len(s) < 20: continue
        for fe, mk in [('taker', False), ('maker', True)]:
            r = ret(s, px, mk, extra)
            mu, t, nc = clt(r, s.cl)
            days = np.maximum(s.h.values / 24, 1 / 24)
            ann = r.mean() / days.mean() * 365 if days.mean() >= 1 else np.nan  # simple (non-compounded), ratio of means; NaN for <1d holds
            rows.append([name, fe, len(s), nc, round(100 * s.y.mean() - 100 * s[px].mean() - 100*extra, 2), round(100 * mu, 2), round(t, 2), round(100 * ann, 0)])
    print(f"\n### {label}: buy-and-hold to resolution (return per $ staked, net of fee)")
    print(pd.DataFrame(rows, columns=['bucket', 'fee', 'n', 'clusters', 'edge_pp', 'mean_ret%', 't_cl', 'simple_ann%']).to_string(index=False))

# ---------- A: Polymarket (shirleyshen) ----------
A = pd.read_csv(f'{H}/shirleyshen0106_polymarket-calibration/observations_complete_20260920.csv')
for h in [1, 24, 168]:
    x = expand(A[A.horizon_hours == h], 'quoted_prob', 'outcome', 'category', 'horizon_hours')
    table(x, f'A Polymarket Sep-2026, {h}h before resolution'); strat(x, f'A Polymarket {h}h (mid quote)')
    strat(x, f'A Polymarket {h}h (mid + 1c half-spread)', extra=0.01)

# ---------- B: Polymarket (Magnus) with by-month stability ----------
B = pd.read_csv(f'{H}/GitHubMagnus_polymarket-calibration/data/markets.csv')
B['month'] = pd.to_datetime(B.close_time_utc).dt.tz_localize(None).dt.to_period('Q').astype(str)
for pc, h in [('p_1d', 24), ('p_7d', 168), ('p_30d', 720)]:
    b = B.dropna(subset=[pc]).copy(); b['h'] = h
    x = expand(b, pc, 'outcome', 'event_id', 'h')
    table(x, f'B Polymarket Oct25-Jul26 {pc}'); strat(x, f'B Polymarket {pc}')
print('\n### B stability by close quarter (p_1d, taker fee, mid quote)')
for q, bq in B.dropna(subset=['p_1d']).groupby('month'):
    bq = bq.copy(); bq['h'] = 24; x = expand(bq, 'p_1d', 'outcome', 'event_id', 'h')
    for nm, m in [('fav>0.9', x.p > .9), ('long<0.1', x.p < .1)]:
        s = x[m]
        if len(s) >= 20:
            mu, t, nc = clt(ret(s), s.cl); print(q, nm, len(s), nc, f'{100*mu:.2f}%', f't={t:.2f}')

# ---------- C: executable Polymarket books (marketlens) ----------
rows = []
ML = f'{H}/marketlenstrade_polymarket-historical-data'
for d in sorted(os.listdir(ML)):
    if not os.path.exists(f'{ML}/{d}/snapshots.csv'): continue
    mk = pd.read_csv(f'{ML}/{d}/markets.csv'); sn = pd.read_csv(f'{ML}/{d}/snapshots.csv')
    mk = mk[mk.winning_outcome.notna()]
    mk['first'] = mk.outcomes.str.split('|').str[0]; mk['y'] = (mk.winning_outcome == mk['first']).astype(int)
    mk['res_ms'] = (pd.to_datetime(mk.resolved_at).map(lambda t: t.timestamp()) * 1000).astype('int64')
    sn = sn.merge(mk[['market_id', 'y', 'res_ms', 'event']], on='market_id')
    for lag_h in [1.0, 6.0]:
        s = sn[sn.t_ms <= sn.res_ms - lag_h * 3.6e6].sort_values('t_ms').groupby('market_id').tail(1)
        s = s[(s.best_ask > 0) & (s.best_bid > 0) & (s.spread <= 0.10)]
        for _, r in s.iterrows():
            rows.append(dict(ev=d, cl=r.event, lag=lag_h, p=r.best_ask, mid=r.midpoint, y=r.y, h=lag_h))
            rows.append(dict(ev=d, cl=r.event, lag=lag_h, p=1 - r.best_bid, mid=1 - r.midpoint, y=1 - r.y, h=lag_h))
C = pd.DataFrame(rows)
C = C[(C.p > 0.005) & (C.p < 0.995)]
for lag in [1.0, 6.0]:
    x = C[C.lag == lag]
    table(x, f'C Polymarket executable ASK, {lag}h pre-resolution (7 events)'); strat(x, f'C executable ask {lag}h')

# ---------- D: EPL odds (sports FLB proxy) ----------
D = pd.read_csv(f'{H}/AnishKhetani_premier-league-data/data/processed/results.csv')[['match_id', 'ftr']].merge(
    pd.read_csv(f'{H}/AnishKhetani_premier-league-data/data/processed/results_with_odds.csv'), on='match_id')
def sports(book, label):
    cols = [f'{book}_1x2_{s}' for s in ('home', 'draw', 'away')]
    d = D.dropna(subset=cols)
    rr = []
    for s, code in zip(('home', 'draw', 'away'), 'HDA'):
        o = d[f'{book}_1x2_{s}']
        inv = sum(1 / d[c] for c in cols)
        rr.append(pd.DataFrame({'p_raw': 1 / o, 'p': (1 / o) / inv, 'odds': o, 'y': (d.ftr == code).astype(int),
                                'cl': d.match_id, 'season': d.season}))
    x = pd.concat(rr)
    x['r'] = x.y * x.odds - 1
    print(f"\n### D EPL {label} (n matches={len(d)}, seasons {d.season.min()}..{d.season.max()}): bet at quoted odds, vig included")
    x['b'] = pd.cut(x.p, [0, .1, .2, .35, .5, .65, .75, 1.01])
    g = x.groupby('b', observed=True).agg(n=('y', 'size'), fair_p=('p', 'mean'), realized=('y', 'mean'), ret=('r', 'mean'))
    g['t'] = x.groupby('b', observed=True).r.apply(lambda r: r.mean() / (r.std() / np.sqrt(len(r))))
    print(g.round(3).to_string())
    return x
for bk, lb in [('bet365', 'Bet365 (retail)'), ('pinnacle', 'Pinnacle open (sharp)'), ('pinnacle', 'Pinnacle'), ('market_max', 'best-available max odds'), ('market_max', 'max close'), ('betfair_ex', 'Betfair exchange (gross of commission)')]:
    if lb == 'max close':
        for s in ('home', 'draw', 'away'): D[f'maxc_1x2_{s}'] = D[f'market_max_1x2_{s}_close']
        x = sports('maxc', lb)
    elif lb == 'Pinnacle':
        for s in ('home', 'draw', 'away'): D[f'pinc_1x2_{s}'] = D[f'pinnacle_1x2_{s}_close']
        x = sports('pinc', 'Pinnacle CLOSE')
    else:
        x = sports(bk, lb)
    if bk == 'bet365' and lb.startswith('Bet365'):
        print('\nBet365 by season: longshot(<0.2) vs favorite(>0.65) mean return')
        x['grp'] = np.where(x.p < .2, 'long', np.where(x.p > .65, 'fav', 'mid'))
        print(x.groupby(['season', 'grp']).r.mean().unstack().round(3).to_string())

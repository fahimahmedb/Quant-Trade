"""Cross-venue funding spread test: Hyperliquid vs Bybit, same coin (paper research only).
Signal at end of UTC day d uses funding settled <= end of day d; P&L on day d+1.
"""
import glob, os
import numpy as np, pandas as pd

C = '/tmp/claude-0/-home-user-Quant-Trade/d2846cea-5e9b-54a8-9c49-75ba0ab48fd0/scratchpad/crypto'
HL = C + '/freqtrade-hyperliquid-data/user_data/data/hyperliquid/futures'
BY = C + '/funding_arb/funding_analysis/raw_data'
KL = C + '/funding_arb/kline_data'

def hl_coin_to_bybit(c):
    if c.startswith('k') and c[1:].isupper():
        return '1000' + c[1:] + 'USDT'
    return c + 'USDT'

hlf, byf, hlp, byp = {}, {}, {}, {}
for f in glob.glob(HL + '/*_USDC_USDC-1h-funding_rate.feather'):
    coin = os.path.basename(f).split('_')[0]
    b = hl_coin_to_bybit(coin)
    bf = f'{BY}/{b}_funding.csv'
    if not os.path.exists(bf):
        continue
    h = pd.read_feather(f)
    h = h[h.date >= '2023-06-08 01:00']
    hlf[coin] = h.set_index('date').open.groupby(lambda t: t.floor('D')).sum()
    # require nearly full hourly coverage per day
    cnt = h.set_index('date').open.groupby(lambda t: t.floor('D')).count()
    hlf[coin] = hlf[coin][cnt >= 22]
    bb = pd.read_csv(bf)
    bb['t'] = pd.to_datetime(bb.fundingRateTimestamp, utc=True)
    # settlement at t pays for period ending t; 00:00 settlement belongs to previous day
    bb['d'] = (bb.t - pd.Timedelta(seconds=1)).dt.floor('D')
    byf[coin] = bb.groupby('d').fundingRate.sum()
    hd = pd.read_feather(f'{HL}/{coin}_USDC_USDC-1d-futures.feather').set_index('date').close
    hlp[coin] = hd
    kf = f'{KL}/{b}_1h_linear_kline.csv'
    if os.path.exists(kf):
        k = pd.read_csv(kf)
        k['t'] = pd.to_datetime(k.timestamp, utc=True)
        k = k.set_index('t').close
        byp[coin] = k[k.index.hour == 23].rename(lambda t: t.floor('D'))  # close of 23:00 bar ~ daily close

H = pd.DataFrame(hlf); B = pd.DataFrame(byf)
common = sorted(set(H.columns) & set(B.columns))
H, B = H[common], B[common]
idx = H.index.intersection(B.index)
H, B = H.loc[idx], B.loc[idx]
S = H - B  # daily funding spread (fraction), HL minus Bybit
print('coins', len(common), 'days', len(idx), idx[0].date(), idx[-1].date())
print('mean |spread| ann %:', (S.abs().stack().mean() * 365 * 100).round(1),
      ' median:', (S.abs().stack().median() * 365 * 100).round(1))
# persistence
s1 = S.stack(); s0 = S.shift(1).stack()
j = pd.concat([s0, s1], axis=1, keys=['prev', 'next']).dropna()
print('pooled corr(spread_d, spread_d+1)=%.2f' % j.corr().iloc[0, 1])
for thr in [0.10, 0.30, 1.0]:
    m = j.prev.abs() * 365 > thr
    print(f' |prev|>{thr:.0%}/yr: n={m.sum()}, sign persists {np.mean(np.sign(j.prev[m]) == np.sign(j.next[m])):.2f}, '
          f'mean next captured ann {np.mean(np.sign(j.prev[m]) * j.next[m]) * 365:.1%}')

# price legs (daily return per venue)
HP = pd.DataFrame(hlp).reindex(columns=common); BP = pd.DataFrame(byp).reindex(columns=common)
HP.index = HP.index.floor('D'); BP.index = BP.index.floor('D')
HR = HP.pct_change().reindex(idx); BR = BP.pct_change().reindex(idx)

def run(thr_in, look=3, fee_leg=0.0007, liquid=None, price=True):
    sig = S.rolling(look).mean() * 365
    cols = liquid or common
    pos = pd.DataFrame(0.0, index=idx, columns=cols)
    cur = pd.Series(0.0, index=cols)
    for i, d in enumerate(idx):
        s = sig.loc[d, cols]
        new = cur.copy()
        new[(s > thr_in)] = -1.0     # HL funding higher: short HL, long Bybit
        new[(s < -thr_in)] = 1.0
        new[(cur != 0) & ((np.sign(s) != -cur) | (s.abs() < thr_in / 2))] = 0.0
        new[(s > thr_in)] = -1.0; new[(s < -thr_in)] = 1.0
        new[s.isna()] = 0.0
        pos.loc[d] = new; cur = new
    p = pos.shift(1)  # decided end of d, held on d+1
    fund = p * S[cols]        # pos=+1 long HL/short BY: pay HL funding, receive BY -> -(H-B)?? fix sign below
    fund = -p * S[cols]       # long HL pays H, short BY receives B => -(H-B)
    pr = (p * (HR[cols] - BR[cols])).fillna(0) if price else 0
    turn = (pos.diff().abs().fillna(pos.abs())).shift(1).fillna(0)  # legs change
    cost = turn * 2 * fee_leg  # two legs
    net = fund + pr - cost
    act = (p != 0)
    daily = net.where(act).mean(axis=1).dropna()  # per unit notional per leg, EW across active pairs
    npos = act.sum(axis=1)
    gross_f = fund.where(act).mean(axis=1).dropna()
    ann = daily.mean() * 365; sr = daily.mean() / daily.std() * np.sqrt(365)
    y25 = daily[daily.index.year == 2025]
    by = daily.groupby(daily.index.year).mean() * 365
    pxc = (pr.where(act).mean(axis=1).dropna().mean() * 365) if price else 0
    print(f'thr={thr_in:.0%} look={look} fee/leg={fee_leg:.2%} univ={len(cols)} price={price}: '
          f'ann_net={ann:.1%} SR={sr:.2f} fundOnly={gross_f.mean()*365:.1%} priceLeg={pxc:.1%} '
          f'avgPairs={npos[npos>0].mean():.1f} days={len(daily)} 2025ann={y25.mean()*365:.1%} (n={len(y25)}) '
          f'byYr={" ".join(f"{k}:{v:.0%}" for k,v in by.items())}')
    return daily

liq = [c for c in ['BTC', 'ETH', 'SOL', 'DOGE', 'XRP', 'AVAX', 'LINK', 'ARB', 'OP', 'SUI', 'WIF', 'kPEPE', 'LTC', 'BNB', 'APT', 'TIA', 'SEI', 'INJ', 'NEAR', 'ADA'] if c in common]
print('--- price-leg coverage coins', int(HR.notna().any().sum()), int(BR.notna().any().sum()))
for thr in [0.2, 0.5, 1.0]:
    run(thr, price=False)
    run(thr, price=True)
for thr in [0.2, 0.5]:
    run(thr, liquid=liq, price=True)
run(0.5, fee_leg=0.0003, price=True)  # maker-ish
run(0.5, look=1, price=True)
run(0.5, look=7, price=True)

"""Post-forced-selling reversal test on 1h perp OHLCV (paper research only).
No liquidation feed -> proxy: 1h return <= -K * trailing 30d hourly vol AND volume >= V * trailing 7d median volume.
All thresholds use data strictly before the event bar. Entry at event-bar close, exit at close h bars later.
"""
import glob, os, sys
import numpy as np, pandas as pd

C = '/tmp/claude-0/-home-user-Quant-Trade/d2846cea-5e9b-54a8-9c49-75ba0ab48fd0/scratchpad/crypto'
src = sys.argv[1]

def load():
    out = {}
    if src == 'hl':
        for f in glob.glob(C + '/freqtrade-hyperliquid-data/user_data/data/hyperliquid/futures/*_USDC_USDC-1h-futures.feather'):
            d = pd.read_feather(f).set_index('date')
            out[os.path.basename(f).split('_')[0]] = d[~d.index.duplicated()][['close', 'volume']]
    else:
        for f in glob.glob(C + '/funding_arb/kline_data/*_1h_linear_kline.csv'):
            d = pd.read_csv(f); d['t'] = pd.to_datetime(d.timestamp, utc=True)
            d = d.set_index('t'); d['volume'] = d.turnover
            out[os.path.basename(f).split('_')[0]] = d[~d.index.duplicated()][['close', 'volume']]
    return out

data = load()
CL = pd.DataFrame({k: v.close for k, v in data.items()}).sort_index()
VO = pd.DataFrame({k: v.volume * v.close if src == 'hl' else v.volume for k, v in data.items()}).sort_index()
R = np.log(CL).diff()
MKT = R.median(axis=1)  # cross-sectional median hourly return
sig = R.rolling(24 * 30, min_periods=24 * 10).std().shift(1)
medv = VO.rolling(24 * 7, min_periods=48).median().shift(1)
advusd = VO.rolling(24 * 30, min_periods=48).mean().shift(1) * 24
print(src, 'coins', CL.shape[1], 'hours', CL.shape[0], CL.index[0], CL.index[-1])

def fwd(h):
    return np.log(CL).shift(-h) - np.log(CL)
FW = {h: fwd(h) for h in [1, 4, 12, 24, 72]}
MF = {h: MKT[::-1].rolling(h).sum()[::-1].shift(-1) for h in FW}  # market fwd sum over (t, t+h]

def events(K, V, min_adv=0, idio=False):
    x = R - MKT.values[:, None] if idio else R
    m = (x <= -K * sig) & (VO >= V * medv) & (advusd >= min_adv)
    return m

cost = {'hl': 0.0012, 'bybit': 0.0015}[src]  # round-trip taker + slippage, liquid-ish alts
rows = []
for K, V, idio, adv in [(4, 5, False, 0), (4, 5, True, 0), (6, 8, False, 0), (6, 8, True, 0), (4, 5, False, 5e6), (6, 8, False, 5e6)]:
    m = events(K, V, adv, idio)
    st = m.stack(); st = st[st]
    n = len(st)
    if n < 20:
        continue
    line = f'K={K} V={V} idio={idio} minADV=${adv/1e6:.0f}M n={n}'
    for h in [1, 4, 24, 72]:
        f = FW[h].stack().reindex(st.index)
        mf = pd.Series(MF[h].reindex(st.index.get_level_values(0)).values, index=st.index)
        ex = f - mf  # market-adjusted
        # cluster by day: average per event-day
        day = st.index.get_level_values(0).floor('D')
        dmean = f.groupby(day).mean().dropna(); dex = ex.groupby(day).mean().dropna()
        t = dmean.mean() / dmean.std() * np.sqrt(len(dmean))
        te = dex.mean() / dex.std() * np.sqrt(len(dex))
        y25 = dmean[dmean.index >= '2025-01-01']
        line += f' | h{h}: raw {f.mean()*100:+.2f}% (tDay {t:.1f}) net {(f.mean()-cost)*100:+.2f}% mktAdj {ex.mean()*100:+.2f}% (t {te:.1f}) 2025+ {y25.mean()*100:+.2f}%'
    print(line)

# Market-wide cascade: median hourly return <= -3 * trailing vol of median, buy EW basket of top-liquidity coins
msig = MKT.rolling(24 * 30, min_periods=24 * 10).std().shift(1)
for K in [4, 6]:
    ev = MKT[(MKT <= -K * msig)]
    # de-cluster: 24h separation
    keep, last = [], None
    for t in ev.index:
        if last is None or (t - last) >= pd.Timedelta(hours=24):
            keep.append(t); last = t
    line = f'MARKET cascade K={K} events={len(keep)}'
    for h in [1, 4, 24, 72]:
        f = MF[h].reindex(keep).dropna()
        line += f' | h{h}: {f.mean()*100:+.2f}% (t {f.mean()/f.std()*np.sqrt(len(f)):.1f}, hit {np.mean(f>0):.0%})'
    print(line)
    print('   dates:', [str(t)[:13] for t in keep][-12:])
# unconditional baseline
print('baseline mean fwd per coin-hour h24: %.3f%%, h72: %.3f%%' % (FW[24].stack().mean() * 100, FW[72].stack().mean() * 100))

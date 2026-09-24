# Minimum capital to run a diversified futures trend/carry book (Carver-style): per-instrument risk budget must hold
# >= 4 contracts' worth of annual $ risk so positions are not rounded to 0/1. Currency ignored (approx: non-USD ~ USD).
import pandas as pd, numpy as np, glob, os, sys
ROOT=sys.argv[1] if len(sys.argv)>1 else 'pst/data/futures'
cfg=pd.read_csv(f'{ROOT}/csvconfig/instrumentconfig.csv').set_index('Instrument')
rows=[]
for f in glob.glob(f'{ROOT}/adjusted_prices_csv/*.csv'):
    ins=os.path.basename(f)[:-4]; mp=f'{ROOT}/multiple_prices_csv/{ins}.csv'
    if ins not in cfg.index or not os.path.exists(mp): continue
    m=pd.read_csv(mp,index_col=0,parse_dates=True).PRICE.dropna()
    if m.index[-1]<pd.Timestamp('2024-01-01') or len(m)<500: continue
    d=m.groupby(m.index.normalize()).last(); vol=d.pct_change().loc['2023':].std()*16
    rows.append((ins,cfg.loc[ins,'AssetClass'],d.iloc[-1]*cfg.loc[ins,'Pointsize']*vol))
t=pd.DataFrame(rows,columns=['ins','cls','usd_vol_1ct']).replace([np.inf],np.nan).dropna().sort_values('usd_vol_1ct')
TV,IDM=0.20,2.5
print('instruments live in 2024:',len(t)); print(t.groupby('cls').usd_vol_1ct.median().round(0).to_string())
for N in [5,10,20,40]:
    # choose cheapest instrument per asset class round-robin for diversification
    pick=[];pool={c:g.ins.tolist() for c,g in t.groupby('cls')}
    while len(pick)<N and any(pool.values()):
        for c in list(pool):
            if pool[c] and len(pick)<N: pick.append(pool[c].pop(0))
    need=t.set_index('ins').loc[pick].usd_vol_1ct.max()*4*N/(TV*IDM)
    print(f'N={N:2d}  min capital ≈ ${need:,.0f}  (classes: {t.set_index("ins").loc[pick].cls.nunique()})')

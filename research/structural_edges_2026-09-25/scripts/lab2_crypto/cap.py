exec(open('xvenue.py').read().split("liq = [")[0])
import numpy as np
sig = S.rolling(3).mean()*365
act = (sig.abs()>0.5); act = act[[pd.Timestamp(t).year>=2025 for t in act.index]]
cnt = act.sum().sort_values(ascending=False)
vols={}
for c in cnt.index[:25]:
    try:
        d=pd.read_feather(f'{HL}/{c}_USDC_USDC-1h-futures.feather').set_index('date')
        d=d.loc['2025-01-01':'2025-05-15']; vols[c]=(d.volume*d.close).resample('D').sum().median()/1e6
    except Exception as e: vols[c]=np.nan
print(pd.DataFrame({'days_active_2025':cnt[:25],'HL_median_daily_vol_$M':pd.Series(vols)}).round(2).to_string())
# spread-weighted: fraction of 2025 capture from coins with HL vol > $10M

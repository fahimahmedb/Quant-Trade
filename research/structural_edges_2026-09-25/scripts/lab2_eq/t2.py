exec(open('tests.py').read().split('print("=== 1.')[0])
exec("\n".join(l for l in open('tests.py').read().split('print("=== 4.')[1].split('print("=== 5.')[0].splitlines()[1:] if not l.startswith('rep(') and not l.startswith('print')))
from scipy import stats
L=o.ret[o.spread<0]; S=o.ret[o.spread>0]
print("SPY last2d when bonds outperf (long leg): n=%d mean=%.1fbp; when equities outperf: n=%d mean=%.1fbp; welch t=%.2f"%(len(L),L.mean()*1e4,len(S),S.mean()*1e4,stats.ttest_ind(L,S,equal_var=False).statistic))
for lo,hi in [('2016','2021-08-31'),('2021-09-01','2027')]:
    oo=o.loc[lo:hi]; x=-np.sign(oo.spread)*oo.ret; print(lo,"signed SPY mean %.1fbp t=%.2f n=%d"%(x.mean()*1e4,stats.ttest_1samp(x,0).statistic,len(x)))
sl=stats.linregress(o.spread,o.ret); print("regress SPY last2d on MTD spread: slope=%.4f t=%.2f"%(sl.slope,sl.slope/sl.stderr))
exec(open('tests.py').read().split('print("=== 5. FOMC ===")')[1].split('print("n FOMC"')[0])
onF=spy.on.loc[F]; onN=spy.on.drop(F).dropna()
print("FOMC overnight vs other overnight welch t=%.2f"%stats.ttest_ind(onF,onN,equal_var=False).statistic)
for lo,hi in [('2016','2021-08-31'),('2021-09-01','2027')]:
    x=onF.loc[lo:hi]; print(lo,"FOMC ON mean %.1fbp t=%.2f n=%d hit=%.2f"%(x.mean()*1e4,stats.ttest_1samp(x,0).statistic,len(x),(x>0).mean()))
print("median %.1fbp, excluding top3: %.1fbp"%(onF.median()*1e4, onF.sort_values().iloc[:-3].mean()*1e4))
# pre-FOMC close(t-1)->open(t) plus intraday until 2pm unknown; also placebo: Wednesday overnight all
wed=spy.on[spy.index.dayofweek==2].drop(F,errors='ignore'); print("non-FOMC Wednesday overnight mean %.1fbp"%(wed.mean()*1e4))

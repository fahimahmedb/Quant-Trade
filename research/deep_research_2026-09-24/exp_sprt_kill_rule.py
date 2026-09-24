# How fast can shadow/paper trading KILL a bad strategy or CONFIRM a good one?
# Wald SPRT on daily returns: H0 SR=0 vs H1 SR=target (annual), alpha=beta=5%. Monte Carlo, fat tails (t, df=4).
import numpy as np
rng=np.random.default_rng(7); A=np.log(0.95/0.05); B=np.log(0.05/0.95)
def run(true_sr,h1_sr,days=252*10,n=2000):
    mu1=h1_sr/np.sqrt(252); out=[]
    for _ in range(n):
        x=rng.standard_t(4,days)/np.sqrt(2)+true_sr/np.sqrt(252)   # unit-variance daily returns
        llr=np.cumsum(mu1*x-mu1**2/2)                             # Gaussian LLR (sigma=1 known)
        hit=np.where((llr>A)|(llr<B))[0]
        out.append((hit[0],llr[hit[0]]>A) if len(hit) else (days,None))
    d=np.array([o[0] for o in out]); acc=np.mean([bool(o[1]) for o in out])
    return np.median(d)/21, np.percentile(d,90)/21, acc
print('H1 = SR target | true SR | median months to decision | p90 months | P(accept H1)')
for h1 in [1,2,4]:
    for t in [0,-0.5,h1]:
        m,p,a=run(t,h1); print(f'  H1={h1}  true={t:5.1f}  median={m:6.1f}  p90={p:6.1f}  accept={a:.2f}')

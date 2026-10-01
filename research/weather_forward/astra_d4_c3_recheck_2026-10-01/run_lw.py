import sys, json
from multiprocessing import Pool
import astra_lw as a
B = dict(D=120, S=48, m=35, th0=0.05)
def G(name, **kw):
    g = dict(B); g.update(kw); g['name'] = name; return g
GEOM = [
 G('L01 Architect scen.13: 120/48 m=17 thin TRUE', m=17, cap='thin', th0=0.10),
 G('L02 120/48 m=35 full TRUE (thick)', th0=0.10),
 G('L03 60/25 m=17 thin mixed dep wide prices', D=60, S=25, m=17, cap='thin', prices='wide', rho=(0.15, 0.15, 0.10)),
 G('L04 60/25 m=17 thin TRUE wide prices', D=60, S=25, m=17, cap='thin', prices='wide'),
 G('L05 60/25 m=17 thin TRUE std', D=60, S=25, m=17, cap='thin'),
 G('L06 120/48 m=17 mixed cap (1-10 vs 50) wide', m=17, cap='mixed', prices='wide'),
 G('L07 120/48 m=17 thin dominant station 20%', m=17, cap='thin', dom_st=0.20),
 G('L08 120/48 m=17 thin one dominant date (96 trades)', m=17, cap='thin', dom_date=True),
 G('L09 120/48 m=17 thin AR regime', m=17, cap='thin', regime=True),
 G('L10 120/48 m=17 thin heterogeneous station returns sd 0.2', m=17, cap='thin', het=0.2),
 G('L11 60/25 m=17 thin boundary legs strong station dep', D=60, S=25, m=17, cap='thin', prices='boundary', rho=(0.02, 0.30, 0.10)),
 G('L12 60/25 m=17 mixed cap wide mixed dep het 0.2', D=60, S=25, m=17, cap='mixed', prices='wide', rho=(0.15, 0.15, 0.10), het=0.2),
 G('L13 120/48 m=17 thin wide prices', m=17, cap='thin', prices='wide'),
 G('L14 60/25 m=35 full TRUE', D=60, S=25, m=35),
 G('L15 120/48 m=17 thin AR regime, theta=0 (size of window claim)', m=17, cap='thin', regime=True, th0=0.0),
 G('L16 120/48 m=35 full AR regime (thick)', regime=True, th0=0.10),
 G('L17 120/48 m=17 thin weak regime phi=0.8 var 0.05', m=17, cap='thin', regime=True, phi=0.8, regime_var=0.05),
 G('L18 120/48 m=35 full AR regime, theta=0 (size)', regime=True, th0=0.0),
 G('L19 120/48 m=35 full weak regime phi=0.8 var 0.05, theta=0', regime=True, phi=0.8, regime_var=0.05, th0=0.0),
 G('L20 120/48 m=35 full TRUE, theta=0 (size, no regime)', th0=0.0),
 G('L21 120/48 m=17 thin weak regime phi=0.8 var 0.05, theta=0 (size)', m=17, cap='thin', regime=True, phi=0.8, regime_var=0.05, th0=0.0),
 G('L22 120/48 m=17 thin TRUE, theta=0 (size, no regime)', m=17, cap='thin', th0=0.0),
 G('L23 120/48 m=17 full weak regime phi=0.8 var 0.05', m=17, regime=True, phi=0.8, regime_var=0.05, th0=0.10),
]
def job(args):
    i, reps = args
    return json.dumps(a.run(GEOM[i], reps, 1_001_000 + 1000 * i))
if __name__ == '__main__':
    reps = int(sys.argv[1]); idx = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(len(GEOM))
    with Pool(4) as p:
        for line in p.imap(job, [(i, reps) for i in idx]): print(line, flush=True)

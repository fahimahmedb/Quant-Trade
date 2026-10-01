import math, time, importlib.util, numpy as np
import astra_m1_engine as E
# direct trade-level two-way CR for cross-check
def direct(r, day, st, Q, b):
    blk = day // b
    out=[]
    for key in (blk, st, blk*10000+st):
        u, inv = np.unique(key, return_inverse=True)
        s = np.zeros(u.size); np.add.at(s, inv, r)
        G = u.size
        out.append((G/(G-1)*np.sum(s*s)/Q**2, G))
    (VB,GB),(VS,GS),(VBS,_) = out
    return math.sqrt(max(VB,VS,VB+VS-VBS)), min(GB,GS)-1
rng = np.random.default_rng(1)
g = dict(S=48, D=120, m=17, cap='thin', th=0.05, persist=(('date',0.9,0.05),), pause=7)
w = E.generate(rng, g)
z = E.latent(rng, w, g); y = (z < E.ndtri(w['p'])).astype(float)
n = w['C']/w['c']; N = n*(y-w['c']); Q = w['C'].sum(); th = N.sum()/Q; r = N-th*w['C']
M, Cn = E.mats(w['day'], w['st'], r, w['Tcal'], w['S'])
for b in (5,10,20,30):
    a = E.cr_from_matrix(M, Cn, Q, b)[:2]; d = direct(r, w['day'], w['st'], Q, b)
    print(b, a, d, abs(a[0]-d[0]) < 1e-12, a[1]==d[1])
# architect engine cross-check (validation only)
spec = importlib.util.spec_from_file_location('G', '/tmp/claude-0/arch/research/weather_forward/WEATHER_FORWARD_V2_D4_C3_LW_CAL_SIM_2026-10-01.py')
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
for b in (5,10,20,30):
    se, df, _ = G.cr2w(r, w['day']//b, w['st'], Q, w['S'])
    print('arch', b, se, df)
# latent variance check
zs = np.concatenate([E.latent(np.random.default_rng(i), w, g) for i in range(200)])
print('latent var', zs.var())
t=time.time()
K = E.run(dict(S=48, D=120, m=17, cap='thin', th=0.0, persist=(('date',0.8,0.05),)), 500, [1,2])
print('m17 500 reps', time.time()-t)
t=time.time()
K = E.run(dict(S=48, D=120, m=35, cap='full', th=0.0), 500, [1,3])
print('m35 500 reps', time.time()-t)

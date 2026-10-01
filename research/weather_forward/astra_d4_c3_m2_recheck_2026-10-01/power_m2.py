"""Power / feasibility analysis from Astra's power-plan output (joint with reach).
Also a non-adaptive oracle benchmark: with the TRUE sampling sd of theta_hat - theta_W known under the worst in-class truth
for the same design (sd_worst) and under no persistence (sd_none), the best fixed-critical-value one-sided 0.05 test that
is valid under the worst truth rejects iff theta_hat > 1.645 sd_worst; its power under no persistence at theta is
Phi((theta - 1.645 sd_worst) / sd_none) (normal approximation; reach not included).  It bounds what ANY non-adaptive
calibration that guards the worst truth in the class can achieve; adaptive procedures could do better only to the
extent the window itself can distinguish the truths."""
import json
import math
import sys
from scipy.stats import norm

R = {}
for f in sys.argv[1:]:
    for l in open(f):
        r = json.loads(l)
        R[r['key']] = r

print('%-58s %6s %8s %8s %8s %8s %8s %8s %8s' % ('cell', 'reach', 'T2 new', 'T2 old', 'T1a new', 'T1a 5d', 'NEG new', 'NEG 5d', 'pce mode'))
for k, r in R.items():
    if 'power' not in r.get('plan', ''):
        continue
    n = r['reps']
    if not r['reach']:
        continue
    pm = max(r['pce_hist'].items(), key=lambda x: x[1])[0]
    print('%-58s %6.3f %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f %8s' % (k, r['reach'] / n, r['new']['t2'] / n, r['old']['t2'] / n,
          r['new']['T1a'] / n, r['old']['T1a'] / n, r['new']['NEG'] / n, r['old']['NEG'] / n, pm))


def sd(r):
    k = r['reach']
    m = r['sum_err'] / k
    return math.sqrt(r['sum_err2'] / k - m * m)


print()
print('sampling sd of theta_hat - theta_W (given reach) and mean multi-block half-width H95:')
for k, r in R.items():
    if r['reach'] and 'th+0.00' in k:
        print('  %-58s sd %.4f  mean H95 %.4f  mean H95_5 %.4f  1.70*H95/sd %.2f' % (
            k, sd(r), r['sum_H95'] / r['reach'], r['sum_H95_5'] / r['reach'], 1.70 * r['sum_H95'] / r['reach'] / sd(r)))

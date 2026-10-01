import json, sys
f = sys.argv[1]
rows = [json.loads(l) for l in open(f)]
def p(d, k): return d[k]['p']
def ci(d, k): return '[%.4f, %.4f]' % tuple(d[k]['ci'])
print('%-58s %6s | %-24s | %-24s | %6s %6s | %6s %6s %6s | %6s %6s' % ('cell','reach','old miss','new miss','RM','newGR','T1a','NEG','UWm','T2new','fposN'))
for d in rows:
    print('%-58s %6.3f | %.4f %s | %.4f %s | %.4f %.4f | %.4f %.4f %.4f | %.4f %.4f' % (d['name'][:58], p(d,'reach'), p(d,'miss_old'), ci(d,'miss_old'), p(d,'miss_new'), ci(d,'miss_new'), p(d,'miss_rm'), d['miss_new_given_reach']['p'] or 0, p(d,'T1a'), p(d,'NEG'), p(d,'UW_miss'), p(d,'T2_new'), p(d,'fpos_new')))

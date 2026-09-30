"""Re-run of the worst run_search.py configurations: 20 fresh designs x 200 reps (seeds 980_000+). Output: out_search_top.jsonl"""
import json, run_search as s
from multiprocessing import Pool
if __name__ == '__main__':
    rows = [json.loads(l) for l in open('out_search.jsonl')]
    top = sorted(rows, key=lambda r: (-r['fERT'], r['cov']))[:3] + sorted(rows, key=lambda r: r['cov'])[:2]
    jobs = []
    for i, r in enumerate(top):
        cfg = dict(r['cfg']); cfg['geom'] = tuple(cfg['geom'])
        for k in range(20): jobs.append((cfg, 200, 980_000 + 100 * i + k))
    with Pool(4) as p: res = p.map(s.run, jobs)
    for i in range(len(top)):
        rr = res[20 * i:20 * i + 20]
        print(json.dumps(dict(cfg=top[i]['cfg'], R=4000, note='20 fresh designs x 200',
                              fERT=round(sum(x['fERT'] for x in rr) / 20, 4), cov=round(sum(x['cov'] for x in rr) / 20, 4),
                              viol=sum(x['viol'] for x in rr), mean_theta=round(sum(x['theta'] for x in rr) / 20, 4))))

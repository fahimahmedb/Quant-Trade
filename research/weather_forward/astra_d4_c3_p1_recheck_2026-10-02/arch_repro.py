"""Reproduce selected cells of the Architect's committed run-J raw output by running the Architect's UNMODIFIED script (copied byte-for-byte from 0cfdd4d).
This is the 'raw-output reproduction' check only; none of its output is used for any Astra verdict on levels or gate constants."""
import sys, json, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'arch_copy'))
sp = importlib.util.spec_from_file_location('arch', os.path.join(HERE, 'arch_copy', 'WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM_2026-10-02.py'))
A = importlib.util.module_from_spec(sp); sp.loader.exec_module(A)
from multiprocessing import Pool
RAW = '/tmp/claude-0/arch/research/weather_forward/'
files = dict(m3_astra='WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_M3_OUTPUT_2026-10-02.jsonl', p1_neg='WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_P1_DERIVE_OUTPUT_2026-10-02.jsonl',
             p1_hi='WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_P1_DERIVE_OUTPUT_2026-10-02.jsonl', p1_t2='WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_P1_DERIVE_OUTPUT_2026-10-02.jsonl',
             p1_verify='WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_P1_VERIFY_OUTPUT_2026-10-02.jsonl', m3_class='WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_M3_OUTPUT_2026-10-02.jsonl',
             m3_m35='WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_M3_OUTPUT_2026-10-02.jsonl')
SEL = [('m3_astra', i) for i in range(10)] + [('p1_verify', i) for i in (0, 12, 36, 67, 69, 73, 90)] + [('p1_neg', 100), ('p1_hi', 5), ('p1_t2', 100), ('p1_t2', 305), ('m3_class', 896), ('m3_m35', 231)]
committed = {}
for plan, f in set((p, files[p]) for p, _ in SEL):
    for l in open(RAW + f):
        r = json.loads(l)
        committed[(r['plan'], r['idx'])] = r
K = A.load_consts()


def job(a):
    plan, idx = a
    g = A.PLANS[plan]()[idx]
    return plan, idx, json.loads(A._job((plan, idx, g, 20000, 0, K)))


def strip(r):
    r = json.loads(json.dumps(r))
    r.get('design', {}).pop('pce_new', None)
    return r


if __name__ == '__main__':
    out = open(os.path.join(HERE, 'out_arch_repro.txt'), 'w')
    with Pool(3) as pool:
        for plan, idx, new in pool.imap(job, SEL):
            old = committed[(plan, idx)]
            same = strip(new) == strip(old)
            diffkeys = [k for k in set(new) | set(old) if json.dumps(new.get(k), sort_keys=True) != json.dumps(old.get(k), sort_keys=True)]
            line = '%s idx %d: %s%s' % (plan, idx, 'IDENTICAL' if same else 'DIFFERS', '' if same else ' keys=' + ','.join(sorted(diffkeys)))
            print(line, flush=True); out.write(line + '\n'); out.flush()

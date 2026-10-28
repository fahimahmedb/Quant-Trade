"""Offline challenge of extracted historical checks; never run either historical script.

No transport, clock, runner, scientific ledger or historical result is executed.
These tests demonstrate blockers, not qualification of a repaired successor.
"""
import ast
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

SHA = '68bbab8ec990c813310224bc8737c41480853108'
PREFIX = 'research/edge_lab/discovery/experiments/disc-crypto-book-pressure-prospective-l1-v0'


def source(suffix):
    return subprocess.check_output(['git', 'show', SHA + ':' + PREFIX + suffix], text=True)


capture = ast.parse(source('.original_capture.py'))
# Extract only JSON decoding/assertions/body-size check, excluding the HTTP call.
checks = next(n for n in ast.walk(capture) if isinstance(n, ast.With)
              and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                      and c.func.attr == 'open' for c in ast.walk(n.items[0].context_expr))
              and any(isinstance(c, ast.Assert) for c in n.body)).body[3:]
check_code = compile(ast.Module(body=checks, type_ignores=[]), '<historical-payload-checks>', 'exec')
calc = source('.original_calculation.py')
# Exact parser block, with in-memory receipt and payload instead of filesystem reads.
parser = ast.parse(calc)
loop = next(n for n in parser.body if isinstance(n, ast.For))
parse_try = next(n for n in loop.body if isinstance(n, ast.Try))
# Remove raw read/hash assignment; retain the hash assertion and JSON decode.
body = copy.deepcopy(parse_try)
body.body[0] = ast.parse("assert hashlib.sha256(raw).hexdigest()==rec['sha256'];row=json.loads(raw)[0]").body[0]
body.body.insert(1, ast.parse('row=json.loads(raw)[0]').body[0])
parse_code = compile(ast.fix_missing_locations(ast.Module(body=[body], type_ignores=[])), '<historical-admission>', 'exec')
utc = lambda x: dt.datetime.fromisoformat(x.replace('Z', '+00:00'))
base = {'timestamp': '2000-01-01T12:00:00Z', 'symbol': 'XBTUSD',
        'bidPrice': 100, 'askPrice': 101, 'bidSize': 2, 'askSize': 1}
cases = {'valid_bbo': [base]}
for name, field in [('missing_bid', 'bidPrice'), ('missing_ask', 'askPrice'), ('missing_timestamp', 'timestamp')]:
    row = dict(base); del row[field]; cases[name] = [row]
for name, patch in {
    'malformed_numeric': {'bidPrice': 'oops'}, 'zero_price': {'bidPrice': 0},
    'negative_price': {'bidPrice': -1}, 'stale': {'timestamp': '2000-01-01T11:59:49Z'},
    'future': {'timestamp': '2000-01-01T12:00:02Z'}, 'wrong_instrument': {'symbol': 'ETHUSD'},
    'wrong_venue': {'venue': 'OTHER'}, 'unexpected_units': {'units': 'cents'},
    'unexpected_precision': {'bidPrice': 100.00000000000001},
}.items():
    cases[name] = [dict(base, **patch)]
cases.update(wrong_schema={'data': base}, empty_body=b'', partial_body=b'[{', oversized=b' ' * 16384)
results = {}
for name, payload in cases.items():
    raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    env = {'b': raw, 'json': json}
    error = None
    try:
        exec(check_code, env)
    except Exception as exc:
        error = str(exc)
    rec = {'sha256': hashlib.sha256(raw).hexdigest(), 'receive_utc': '2000-01-01T12:00:00Z'}
    env = dict(raw=raw, rec=rec, json=json, hashlib=hashlib, utc=utc,
               math=__import__('math'), q={}, bad=[], i=0)
    exec(parse_code, env)
    results[name] = {'capture_error': error, 'historical_stop': bool(error),
                     'evaluator_rejected': bool(env['bad'])}

# The original interval time check, without calculating any trade or payoff.
gap_if = next(n for n in ast.walk(parser) if isinstance(n, ast.If)
              and ast.unparse(n.test).startswith('not 1 <= '))
for name, gap in [('duplicate_observation', 0), ('out_of_order', -5)]:
    t = utc(base['timestamp'])
    env = {'x': {'time': t}, 'y': {'time': t + dt.timedelta(seconds=gap)}, 'invalid': []}
    exec(compile(ast.Module(body=[gap_if], type_ignores=[]), '<historical-gap-check>', 'exec'), env)
    results[name] = {'interval_rejected': bool(env['invalid'])}

# Missing provenance is not consulted by the extracted evaluator parser.
results['missing_source_provenance'] = dict(results['valid_bbo'])
results['timeout'] = {'status': 'NOT_EXECUTED_TRANSPORT_BASELINE_UNQUALIFIED'}
results['http_error'] = {'status': 'NOT_EXECUTED_TRANSPORT_BASELINE_UNQUALIFIED'}
assert results['valid_bbo']['evaluator_rejected'] is False
assert results['missing_bid']['capture_error'] == ''
assert results['missing_bid']['historical_stop'] is False
assert results['wrong_instrument']['evaluator_rejected'] is False
assert results['unexpected_units']['evaluator_rejected'] is False
assert results['duplicate_observation']['interval_rejected'] is True
receipt = {'result': 'BLOCK', 'test_executed': 'offline extracted historical checks',
           'test_passed': 'blocker witnesses reproduced; no successor PASS implied',
           'source_sha': SHA, 'cases': results,
           'real_outcome_access': False, 'historical_runner_executed': False,
           'successor_runner_qualified': False, 'successor_evaluator_qualified': False}
Path(__file__).with_name('challenge_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))

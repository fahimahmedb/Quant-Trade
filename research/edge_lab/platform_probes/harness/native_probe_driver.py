"""Native same-Site operational canaries; credentials arrive on hidden stdin only.

This wraps an actual Python subprocess. It is WRAPPED documentary command-worker
evidence, never Codex or scheduled-ChatGPT identity evidence. No research access.
"""
import concurrent.futures
import hashlib
import json
import subprocess
import sys
import termios
import time
import urllib.error
import urllib.request
import uuid

tty = termios.tcgetattr(0)
hidden = termios.tcgetattr(0)
hidden[3] &= ~termios.ECHO
termios.tcsetattr(0, termios.TCSANOW, hidden)
print('READY_FOR_PROBE_CREDENTIALS_HIDDEN_STDIN', flush=True)
cfg = json.loads(sys.stdin.readline())
termios.tcsetattr(0, termios.TCSANOW, tty)
ROOT = 'https://quant-trade-lab.sassylime.chatgpt.site/__platform_probe'
trace = 'WORK-NATIVE-' + uuid.uuid4().hex[:12]
log = {'trace_id': trace, 'worker_type': 'benign_python_subprocess',
       'provenance': 'WRAPPED', 'scope': 'PLATFORM_PROBE_ONLY', 'checks': [], 'request_timings': []}

def call(path, payload=None, auth=True, origin=None):
    headers = {'OAI-Sites-Authorization': 'Bearer ' + cfg['bypass']}
    if auth:
        headers['Authorization'] = 'Bearer ' + cfg['worker_key']
    if origin:
        headers['Origin'] = origin
    data = None if payload is None else json.dumps(payload).encode()
    if data is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(ROOT + path, data=data, headers=headers)
    started = time.monotonic()
    try:
        r = urllib.request.urlopen(req, timeout=12)
        body = json.loads(r.read(100000))
        log['request_timings'].append({'path':path,'status':r.status,'round_trip_ms':(time.monotonic()-started)*1000})
        return r.status, body
    except urllib.error.HTTPError as e:
        raw = e.read(100000)
        log['request_timings'].append({'path':path,'status':e.code,'round_trip_ms':(time.monotonic()-started)*1000})
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {'error': raw.decode(errors='replace')[:180]}

def check(name, expected, status, body):
    entry = {'name': name, 'status': status, 'expected': expected,
             'pass': status == expected,
             'receipt': {k: v for k, v in body.items()
                         if k in ['status', 'error', 'event_id', 'cursor',
                                  'server_received_at', 'applied', 'command_id']}}
    log['checks'].append(entry)
    print(json.dumps(entry), flush=True)
    if status != expected:
        raise RuntimeError(name + ': unexpected native response')

def new_session():
    native = str(uuid.uuid4())
    import os
    log['launcher_pid'] = os.getpid()
    status, s = call('/session', {'worker_id': cfg['worker_id'],
                                'native_session_id': native, 'trace_id': trace})
    check('native_session_creation', 200, status, s)
    log.setdefault('session_bindings', []).append(
        {k: s[k] for k in ['worker_id', 'session_id', 'native_session_id',
                           'generation', 'lease_id', 'runtime_epoch']})
    return s

def event(s, sequence, kind, event_id=None, **extra):
    return {'worker_id': s['worker_id'], 'session_id': s['session_id'],
            'lease_id': s['lease_id'], 'session_generation': s['generation'],
            'sequence': sequence, 'event_id': event_id or trace + '-' + str(sequence),
            'trace_id': trace, 'type': kind, 'scope': 'PLATFORM_PROBE_ONLY', **extra}

try:
    mode = cfg.get('mode', 'semantics')
    if mode == 'restart_check':
        old = cfg['old_session']
        status, b = call('/event', event(old, 999, 'HEARTBEAT', trace + '-old-epoch'))
        check('old_lease_after_actual_redeployment_rejected', 409, status, b)
        status, snap = call('/snapshot', auth=False)
        check('snapshot_after_redeployment', 200, status, snap)
        own = next(x for x in snap['sessions'] if x['worker_id'] == cfg['worker_id'])
        log['restart_lease_status'] = own['lease_status']
        log['restart_previous_lease_not_active'] = own['lease_status'] == 'STALE_RESTART'
    elif mode == 'create_restart_lease':
        s = new_session()
        status, b = call('/event', event(s, 1, 'HEARTBEAT'))
        check('fresh_lease_before_redeployment', 200, status, b)
        log['restart_session'] = s
    else:
        status, b = call('/session', {'worker_id': cfg['worker_id']}, auth=False)
        check('anonymous_worker_ingress_rejected', 401, status, b)
        status, b = call('/session', {'worker_id': cfg['worker_id']},
                         origin='https://unauthorized.invalid')
        check('cross_origin_worker_ingress_rejected', 403, status, b)
        status, b = call('/owner-toggle', {'command_id': trace + '-anonymous'},
                         auth=False, origin=ROOT.split('/__platform_probe')[0])
        check('anonymous_owner_mutation_rejected', 401, status, b)
        status, b = call('/owner-toggle', {'command_id': trace + '-cross'},
                         auth=False, origin='https://unauthorized.invalid')
        check('cross_origin_owner_mutation_rejected', 403, status, b)
        s = new_session()
        status, b = call('/event', event(s, 1, 'HEARTBEAT'))
        check('A_fresh_lease_heartbeat', 200, status, b)
        status, snap = call('/snapshot', auth=False)
        own = next(x for x in snap['sessions'] if x['worker_id'] == cfg['worker_id'])
        log['fresh_lease_status'] = own['lease_status']
        log['snapshot_stream_ready'] = snap['stream_ready']
        status, b = call('/event', event(s, 2, 'ACTION_STARTED',
                         action='BENIGN_SHA256_CHAIN', emitter='wrapped_python_subprocess'))
        check('genuine_action_start_dispatched_before_launch', 200, status, b)
        code = ('import hashlib,time; d=b"PLATFORM_PROBE_ONLY"; '
                'end=time.monotonic()+8; n=0\n'
                'while time.monotonic()<end: d=hashlib.sha256(d).digest(); n+=1\n'
                'print(d.hex()); print(n)')
        launch = time.monotonic()
        process = subprocess.Popen([sys.executable, '-c', code],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sequence = 2
        while process.poll() is None:
            try:
                process.wait(timeout=1.5)
            except subprocess.TimeoutExpired:
                sequence += 1
                status, b = call('/event', event(s, sequence, 'HEARTBEAT'))
                check('actual_running_subprocess_heartbeat', 200, status, b)
        stdout, stderr = process.communicate()
        action_completed_boundary = time.monotonic()
        proof = {'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
                 'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
                 'exit_code': process.returncode,
                 'command_sha256': hashlib.sha256(code.encode()).hexdigest()}
        log['actual_subprocess_receipt'] = {'pid': process.pid, **proof,
             'duration_ms_same_launcher_clock': (time.monotonic()-launch)*1000}
        sequence += 1
        packet = event(s, sequence, 'ACTION_COMPLETED', effect_proof=proof)
        dispatch = time.monotonic()
        status, b = call('/event', packet)
        log['ACTION_TO_EMIT_DISPATCH_ms_same_launcher_clock'] = (dispatch-action_completed_boundary)*1000
        check('actual_action_completion_with_effect_proof', 200, status, b)
        log['last_applied_event_id'] = packet['event_id']
        log['server_received_at'] = b.get('server_received_at')
        status, duplicate = call('/event', packet)
        check('D_duplicate_event_one_transition', 200, status, duplicate)
        log['dedupe_same_cursor'] = duplicate.get('cursor') == b.get('cursor')
        status, b = call('/event', event(s, 1, 'HEARTBEAT', trace + '-old-sequence'))
        check('E_old_sequence_no_regression', 409, status, b)
        status, b = call('/event', {**event(s, sequence+1, 'HEARTBEAT', trace+'-spoof'),
                                   'worker_id':'unauthorized-worker'})
        check('worker_binding_spoof_rejected', 403, status, b)
        status, b = call('/event', event(s, sequence+1, 'SESSION_ENDED', trace+'-action-session-close'))
        check('real_action_session_clean_close',200,status,b)
        old_generation = new_session()
        newer = new_session()
        status, b = call('/event', event(old_generation, 1, 'HEARTBEAT', trace+'-old-generation'))
        check('C_old_generation_rejected', 409, status, b)
        status, b = call('/event', event(newer, 1, 'SESSION_ENDED', trace+'-new-close'))
        check('clean_new_session_close', 200, status, b)
        expiring = new_session()
        time.sleep(expiring.get("lease_duration_ms",6000)/1000+1)
        status, snap = call('/snapshot', auth=False)
        own = next(x for x in snap['sessions'] if x['worker_id'] == cfg['worker_id'])
        log['B_expired_lease_status'] = own['lease_status']
        status, b = call('/event', event(expiring, 1, 'HEARTBEAT', trace+'-expired'))
        check('B_expired_lease_cannot_revive', 409, status, b)
    print('NATIVE_PROBE_RESULT=' + json.dumps(log), flush=True)
except Exception as error:
    log['failure'] = str(error)
    print('NATIVE_PROBE_RESULT=' + json.dumps(log), flush=True)
    sys.exit(1)

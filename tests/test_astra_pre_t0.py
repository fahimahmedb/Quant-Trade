"""Independent red/green campaign; synthetic source bytes only, no SEC traffic."""
import copy
import http.client
import importlib.util
import json
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from types import SimpleNamespace
from unittest import mock
from datetime import datetime, timezone, timedelta

from quant.dataplane.sec.audit import audit_observation_window
from quant.dataplane.sec.transport import SecHttpTransport, RequestPermit, COMPLETE
from quant.dataplane.sec.policy import SecAccessPolicy
from quant.dataplane.sec.collector import SecForm4Collector
from quant.dataplane.sec.store import SecStorageFailure
from quant.state import append_jsonl, read_jsonl
from tests.test_sec_form4_capture import CollectorTestCase, USER_AGENT, ROOT

NOW = datetime(2026, 9, 18, 13, tzinfo=timezone.utc)
T = '2026-09-18T12:00:00+00:00'
DUE = '2026-09-18T12:05:00+00:00'
FP = 'sha256:' + 'a' * 64

class AuditCampaign(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        sec = Path(self.temp.name) / 'sec'
        sec.mkdir()
        self.transitions = []
        self.attempts = []
        self.lane = SimpleNamespace(
            paths=SimpleNamespace(sec=sec, sec_lifecycle=sec/'lifecycle.jsonl'),
            scheduler=SimpleNamespace(all=lambda: self.transitions,
                fingerprints_seen=lambda: sorted(set(r['acquisition_critical_fingerprint'] for r in self.transitions))),
            store=SimpleNamespace(attempts=lambda: self.attempts),
            state=SimpleNamespace(coverage_state='COMPLETE', open_gaps=[]),
            timebase=SimpleNamespace(now=lambda: NOW), fingerprint=FP)
        append_jsonl(self.lane.paths.sec_lifecycle, {
            'lifecycle_cause':'DEPLOYMENT_RESTART', 'boot_id':'child',
            'supervisor_id':'sup', 'recorded_at_utc':T,
            'boot_at_utc':T, 'acquisition_critical_fingerprint':FP})

    def transition(self, identity='one', due=DUE, supersedes=None, stamp=T):
        self.transitions.append(dict(transition_id='transition-'+str(identity),
            recorded_at_utc=stamp, next_due_at_utc=due, obligation_id=identity,
            state='AWAITING_POLL', cause='SERVICE_START',
            acquisition_critical_fingerprint=FP, supersedes_obligation_id=supersedes))

    def report(self):
        return audit_observation_window(self.lane, now=NOW)

    def test_missing_due_cannot_erase_all_expected_work(self):
        self.transition(identity=None, due=None)
        self.assertFalse(self.report()['accountable'])

    def test_two_node_circular_supersession_same_timestamp(self):
        self.transition('one', supersedes='two')
        self.transition('two', supersedes='one')
        self.assertFalse(self.report()['accountable'])

    def test_single_foreign_fingerprint_cannot_pass(self):
        self.transition(due=(NOW+timedelta(minutes=1)).isoformat())
        self.lane.fingerprint='sha256:'+'b'*64
        self.assertFalse(self.report()['accountable'])

    def test_future_due_is_commitment_not_future_evidence(self):
        self.transition(due=(NOW+timedelta(minutes=1)).isoformat())
        self.assertNotIn('FUTURE_EVIDENCE_TIMESTAMP',self.report()['findings'])

    def test_missing_transition_time_is_invalid(self):
        self.transition(due=T, stamp=None)
        self.assertIn('EVIDENCE_TIMESTAMP_MISSING', self.report()['findings'])

    def test_corrupt_journal_returns_explicit_failed_verdict(self):
        self.transition()
        self.lane.paths.sec_lifecycle.write_bytes(b'{')
        self.assertFalse(self.report()['accountable'])

    def test_nan_tolerance_cannot_make_obligations_pending(self):
        self.transition()
        report=audit_observation_window(self.lane, now=NOW, tolerance_seconds=float('inf'))
        self.assertFalse(report['accountable'])

class CollectorCampaign(CollectorTestCase):
    def test_fingerprint_mismatch_cannot_be_cleared_by_restoring_file(self):
        c=self.collector(self.fixture_router())
        c.lifecycle['qualifying_service_mode']=True
        c.materialize_fingerprint()
        original=self.paths.sec_fingerprint.read_bytes()
        self.paths.sec_fingerprint.write_bytes(b'{')
        with self.assertRaises(SecStorageFailure):
            c.require_active_materialization()
        self.paths.sec_fingerprint.write_bytes(original)
        with self.assertRaises(SecStorageFailure):
            c.require_active_materialization()

    def test_restart_does_not_replace_the_unanswered_obligation(self):
        c=self.collector(self.fixture_router())
        before=c.state.open_obligation_id
        c.record_service_start()
        self.assertEqual(c.state.open_obligation_id,before)

    def test_due_poll_wins_over_a_backlog_in_real_clock(self):
        from quant.clock import QuantSystem
        c=self.collector(self.fixture_router())
        c.poll()
        self.timebase.advance(61)
        system=QuantSystem(self.root)
        system.sec=c
        with mock.patch.object(c,'poll',wraps=c.poll) as poll, mock.patch.object(c,'drain',wraps=c.drain) as drain:
            system._capture_step(c)
        self.assertEqual(poll.call_count,1)
        self.assertEqual(drain.call_count,0)

class WireCampaign(unittest.TestCase):
    def exchange(self, wire, *, trickle=False):
        requests=[]
        class Handler(socketserver.BaseRequestHandler):
            def handle(inner):
                try:
                    data=b''
                    while b'\r\n\r\n' not in data:
                        piece=inner.request.recv(4096)
                        if not piece: return
                        data+=piece
                    requests.append(data)
                    if trickle:
                        inner.request.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 20\r\n\r\n')
                        for _ in range(20):
                            inner.request.sendall(b'x')
                            time.sleep(.025)
                    else:
                        inner.request.sendall(wire)
                except (BrokenPipeError,ConnectionResetError):
                    pass
        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address=True
            daemon_threads=True
        with Server(('127.0.0.1',0),Handler) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()
            p=SecAccessPolicy(user_agent=USER_AGENT,total_deadline_seconds=.12,
                connect_timeout_seconds=.12,read_timeout_seconds=.06)
            transport=SecHttpTransport(p)
            transport._connection=http.client.HTTPConnection(*server.server_address,timeout=.12)
            started=time.monotonic()
            try:
                result=transport.fetch('/fixture',RequestPermit('id',T,'test'))
            finally:
                elapsed=time.monotonic()-started
                transport.close()
                server.shutdown()
            return result,elapsed,requests

    def test_trickling_body_respects_total_deadline_real_socket(self):
        result,elapsed,requests=self.exchange(b'',trickle=True)
        self.assertEqual(len(requests),1)
        self.assertLess(elapsed,.35)
        self.assertNotEqual(result.transfer_outcome,COMPLETE)
        self.assertTrue(result.body,'partial evidence must be preserved')

    def test_real_connection_truncation_and_send_count(self):
        response,_,requests=self.exchange(b'HTTP/1.1 200 OK\r\nContent-Length: 9\r\n\r\npart')
        self.assertEqual(len(requests),1)
        self.assertEqual(response.body,b'part')
        self.assertNotEqual(response.transfer_outcome,COMPLETE)

class LauncherRealChild(unittest.TestCase):
    def test_real_main_child_exit_relaunch_keeps_host_identity(self):
        spec=importlib.util.spec_from_file_location('astra_launcher',ROOT/'deploy/quant_sec_supervisor.py')
        launcher=importlib.util.module_from_spec(spec); spec.loader.exec_module(launcher)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'scripts').mkdir()
            (root/'scripts/quant.py').write_text('raise SystemExit(0)\n')
            for invocation in ('first','second'):
                env={'QUANT_SEC_USER_AGENT':USER_AGENT,'INVOCATION_ID':invocation,
                     'QUANT_SEC_SERVICE_MANAGER':'systemd'}
                with mock.patch.dict(os.environ,env,clear=True), mock.patch.object(sys,'argv',['supervisor','--root',str(root)]), mock.patch.object(launcher,'current_fingerprint',return_value=FP), mock.patch.object(launcher,'materialize_if_absent',return_value=FP):
                    self.assertEqual(launcher.main(),0)
                state=json.loads((root/'var/sec/supervisor_state.json').read_text())
                self.assertEqual(state['host_boot_id'],Path('/proc/sys/kernel/random/boot_id').read_text().strip())
                self.assertEqual(state['lifecycle_cause'],'MANUAL_START')
                self.assertFalse(state['supervisor_running'])

if __name__=='__main__': unittest.main()

class MoreCollectorCampaign(CollectorTestCase):
    def test_request_intent_order_is_authority_not_just_event_counts(self):
        from quant.state import write_json
        c=self.collector(self.fixture_router())
        c.lifecycle.update(lifecycle_cause='DEPLOYMENT_RESTART',boot_id='b',supervisor_id='s')
        c.record_service_start();c.poll();c.drain(max_items=3)
        path=self.paths.sec/'request_intents.jsonl'
        records=list(read_jsonl(path))
        # Corrupt only the order: the old audit checked counts, not transitions.
        path.write_text(''.join(json.dumps(r)+'\n' for r in reversed(records)))
        report=audit_observation_window(c)
        self.assertIn('REQUEST_EVENT_ORDER_INVALID',report['findings'])
        self.assertFalse(report['accountable'])

    def test_missing_state_and_commit_ledger_with_request_history_refuses_bootstrap(self):
        c=self.collector(self.fixture_router());c.poll()
        self.paths.sec_collector_state.unlink()
        (self.paths.sec/'collector_state.commits.jsonl').unlink()
        with self.assertRaises(SecStorageFailure):
            self.reborn(self.fixture_router())

    def test_readiness_requires_live_enabled_and_complete_capture(self):
        from tests.test_sec_form4_capture import RodageFalsificationTests
        case=RodageFalsificationTests();case.setUp();self.addCleanup(case.doCleanups)
        c=case.qualifying_collector(case.fixture_router())
        c.record_service_start()
        # Valid-looking lifecycle and materialization, but no request ever ran.
        self.assertFalse(c.t0_readiness()['instrumentation_ready'])

    def test_public_snapshot_has_no_per_capture_events_or_counters(self):
        from quant.clock import QuantSystem
        from quant.dataplane.sec.visibility import find_count_proxies
        c=self.collector(self.fixture_router());system=QuantSystem(self.root)
        system.sec=c;c.emit=system.log.emit
        system._capture_step(c);system._capture_step(c)
        snapshot=system.snapshot()
        self.assertEqual(find_count_proxies(snapshot),[])
        self.assertNotIn('sec_raw_capture',json.dumps(snapshot))
        self.assertNotIn('last_active_at',snapshot['components'].get('SEC_CAPTURE',{}))
        self.assertNotIn('run_history',snapshot['control'])

    def test_shared_events_do_not_encode_one_row_per_capture(self):
        from quant.clock import QuantSystem
        c=self.collector(self.fixture_router());system=QuantSystem(self.root)
        c.emit=system.log.emit;c.poll();c.drain(max_items=3)
        self.assertNotIn('sec_raw_capture',self.paths.events.read_text() if self.paths.events.exists() else '')

    def test_successful_pages_survive_a_later_page_failure(self):
        from tests.test_sec_form4_capture import build_feed, response
        from quant.dataplane.sec.store import digest_text
        def handler(path, call):
            if 'start=0&' in path:return response(build_feed([100,99]))
            return response(b'',status=503)
        c=self.collector(handler,discovery_page_size=2)
        c.state.cursor_identity_digest=digest_text('0000000001-26-000001');c.save()
        c.poll()
        self.assertTrue(c.state.pending_tasks,'already observed filings must remain durably queued')
        recovered=self.reborn(handler,discovery_page_size=2)
        self.assertEqual(recovered.state.pending_tasks,c.state.pending_tasks)

    def test_reconciliation_404_cannot_hot_loop(self):
        from datetime import date
        c=self.collector(self.fixture_router());c.poll();c.drain(max_items=3)
        c.reconcile(date(2026,9,16))
        self.assertGreater(c.cooldown_remaining(),0)

    def test_qualifying_stop_after_answer_before_next_obligation_is_not_accountable(self):
        c=self.collector(self.fixture_router())
        c.lifecycle.update(lifecycle_cause='DEPLOYMENT_RESTART',boot_id='b',supervisor_id='s')
        c.record_service_start()
        # Crash boundary: request/attempt committed; poll close/next obligation absent.
        c._request('DISCOVERY','/cgi-bin/browse-edgar','https://www.sec.gov/cgi-bin/browse-edgar')
        self.timebase.advance(3600)
        c.state.coverage_state='COMPLETE';c.state.open_gaps=[]
        self.assertFalse(audit_observation_window(c)['accountable'])

    def test_materialization_valid_hash_wrong_commit_is_rejected(self):
        c=self.collector(self.fixture_router());c.materialize_fingerprint()
        payload=json.loads(self.paths.sec_fingerprint.read_text())
        payload['git_commit']='0'*40
        self.paths.sec_fingerprint.write_text(json.dumps(payload))
        self.assertIsNotNone(c._validated_materialization()[1])

class PublicArtifactCampaign(unittest.TestCase):
    def test_current_checkout_does_not_republish_historical_volume_proxies(self):
        from quant.dataplane.sec.visibility import find_count_proxies
        for path in (ROOT/'handoff').glob('SEC_FORM4*.json'):
            with self.subTest(path=path.name):
                self.assertEqual(find_count_proxies(json.loads(path.read_text())),[])

class MutatingCLIExclusion(unittest.TestCase):
    def test_probe_is_refused_before_state_load_while_service_lock_held(self):
        import fcntl
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);sec=root/'var/sec';sec.mkdir(parents=True)
            for name in ('src','scripts','deploy'): (root/name).symlink_to(ROOT/name, target_is_directory=True)
            with (sec/'collector_service.lock').open('w') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                result=subprocess.run([sys.executable,str(ROOT/'scripts/quant.py'),
                    'sec-disable','--root',str(root)],env={**os.environ,'QUANT_SEC_USER_AGENT':USER_AGENT},capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,2,result.stdout+result.stderr)
                self.assertIn('COLLECTOR_ALREADY_RUNNING',result.stdout)
                self.assertFalse((sec/'collector_state.json').exists())


class Phase3AuthorityAndBindingCampaign(CollectorTestCase):
    def test_verification_digest_changes_when_systemd_unit_changes(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('astra_verify_p0',ROOT/'scripts/verify_p0.py')
        verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)
        unit=ROOT/'deploy/quant-sec-capture.service'
        original=unit.read_bytes()
        before=verify.verified_tree_digest()
        try:
            unit.write_bytes(original+b'\n# adversarial unit mutation\n')
            after=verify.verified_tree_digest()
        finally:
            unit.write_bytes(original)
        self.assertNotEqual(before,after,
            'the verification binding must cover the effective service definition')

    def test_forged_child_environment_cannot_buy_qualifying_readiness(self):
        from tests.test_sec_form4_capture import RodageFalsificationTests
        case=RodageFalsificationTests();case.setUp();self.addCleanup(case.doCleanups)
        c=case.qualifying_collector(case.fixture_router())
        c.record_service_start();c.poll();c.drain(max_items=3)
        self.assertFalse(c.t0_readiness()['instrumentation_ready'],
            'environment markers without durable external launch authority are not proof')

    def test_future_last_poll_timestamp_cannot_suppress_due_acquisition(self):
        c=self.collector(self.fixture_router())
        c.state.last_poll_started_at_utc=(self.timebase.now()+timedelta(hours=1)).isoformat()
        c.save()
        self.assertTrue(c.poll_due(),
            'a future prior-poll timestamp must fail closed instead of suppressing polling')

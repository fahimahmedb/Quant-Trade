"""Fast-lane firewall, sealed pre-registration, git anchoring, grants and one-look holdout.

Every scenario runs in a throw-away git repository built in a temp directory; the
project repository is never touched. Fixtures are SYNTHETIC.
"""

import copy
import gzip
import json
import os
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

from quant.fastlane import holdout as ho
from quant.fastlane import preregistration as pr
from quant.fastlane import prices as px
from quant.fastlane.firewall import LINEAGE_ID, Firewall, FirewallViolation
from quant.fastlane.gitcheck import GitCheckFailed, verify_committed
from quant.fastlane.protocol_draft import build_protocol

REPO = Path(__file__).resolve().parents[1]
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "Synthetic", "GIT_AUTHOR_EMAIL": "synthetic@example.invalid",
           "GIT_COMMITTER_NAME": "Synthetic", "GIT_COMMITTER_EMAIL": "synthetic@example.invalid"}
EVAL_SPEC = "sha256:" + "e" * 64


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, env=GIT_ENV, check=True,
                          capture_output=True)


def synthetic_census(events_sha, relpath, rate=4000.0):
    fam = {"per_year": rate, "value_tiers_per_year": {"ge_10k": rate, "ge_100k": rate / 2,
                                                      "ge_1m": rate / 4}}
    return {"by_split": {s: {f: fam for f in ("OD", "CEO_CFO", "FROZEN_FV_PROXY_10WD")}
                         for s in pr.SPLITS},
            "inputs": {"events_sha256": events_sha, "events_relpath": relpath,
                       "events_rows": 1, "sec_manifest_set_fingerprint": "sha256:synthetic"}}


def final_protocol(events_sha="0" * 64, relpath="research/fastlane/data/events_primary_v1.jsonl.gz",
                   **overrides):
    protocol = build_protocol(synthetic_census(events_sha, relpath), "sha256:synthetic", {})
    protocol["status"] = pr.STATUS_FINAL
    protocol.update(overrides)
    return protocol


class World:
    """A temp git repo with a (optionally) sealed, committed and published protocol."""

    def __init__(self, tmp, *, seal=True, commit=True, publish=True, manifests=True):
        self.root = Path(tmp)
        git(self.root, "init", "-q", "-b", "main")
        self.fw = Firewall(self.root)
        events = self.fw.artifact("data", "events_primary_v1.jsonl.gz")
        payload = gzip.compress(b'{"accession":"synthetic"}\n', mtime=0)
        self.fw.write_bytes_atomic(events, payload)
        self.relpath = events.relative_to(self.root).as_posix()
        self.protocol = final_protocol(self.fw.sha256_file(events), self.relpath)
        self.record = None
        if manifests:
            self.fw.write_json_atomic(pr.delisting_map_path(self.fw), {
                "lineage": LINEAGE_ID, "vendor_id": "SYNTH",
                "mapping": {"A": "CASH_ACQUISITION", "B": "BANKRUPTCY_OR_CAUSE",
                            "Z": "UNKNOWN"}})
            self.fw.write_json_atomic(pr.benchmark_manifest_path(self.fw), {
                "lineage": LINEAGE_ID, "series": "SPY", "return_type": "TOTAL_RETURN",
                "vendor_id": "SYNTH", "dataset": "SYNTH/SEP", "fallback": "NONE"})
        if seal:
            self.record = pr.seal_protocol(self.fw, self.protocol)
        if commit:
            self.commit_all("seal")
        if publish:
            self.publish()

    @property
    def sha(self):
        return self.record["protocol_sha256"]

    def commit_all(self, msg):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "--allow-empty", "-m", msg)

    def publish(self):
        git(self.root, "update-ref", "refs/remotes/origin/main", "HEAD")

    def variants(self, n):
        return [v["variant_id"] for v in self.protocol["variants"]][:n]

    def trials(self, variants, splits=("discovery", "walk_forward")):
        ledger = ho.TrialLedger(self.fw)
        for v in variants:
            for s in splits:
                ledger.record(f"{v}-{s}", v, s, {"variant": v, "split": s})

    def request(self, request_id, variants, *, commit=True):
        self.trials(variants)
        record = ho.write_holdout_request(self.fw, request_id, variants, EVAL_SPEC)
        if commit:
            self.commit_all("holdout request")
            self.publish()
        return record

    def holdout(self, request_id, variants, spec=EVAL_SPEC):
        return pr.require_outcome_access(self.fw, "holdout", self.sha,
                                         holdout_request_id=request_id,
                                         holdout_variants=variants, eval_spec_digest=spec)


class FirewallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.fw = Firewall(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_allows_own_space(self):
        self.fw.write_json_atomic(self.fw.data("x", "a.json"), {"a": 1})
        self.fw.write_json_atomic(self.fw.artifact("b.json"), {"b": 2})
        self.assertEqual(self.fw.read_json(self.fw.data("x", "a.json")), {"a": 1})

    def test_refuses_writes_outside_its_space(self):
        for target in (self.root / "var" / "events.jsonl", self.root / "src" / "x.py",
                       self.root / "var" / "fastlane" / ".." / "book.json", Path("/tmp/x.json"),
                       self.root / "research" / "memory.jsonl"):
            with self.assertRaises(FirewallViolation, msg=str(target)):
                self.fw.write_json_atomic(target, {})
        self.assertFalse((self.root / "var" / "events.jsonl").exists())

    def test_refuses_frozen_lineage_paths_even_inside_its_space(self):
        for name in ("FORM4_FIRST_VERTICAL_MULTI_COHORT_V1", "form4_first_vertical_v1"):
            with self.assertRaises(FirewallViolation):
                self.fw.data(name, "ledger.jsonl")
            with self.assertRaises(FirewallViolation):
                self.fw.guard(self.root / "var" / "fastlane" / name, write=False)

    def test_refuses_symlink_escape(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.fw.mkdirs(self.fw.data_root)
        os.symlink(outside, self.fw.data_root / "link")
        with self.assertRaises(FirewallViolation):
            self.fw.write_json_atomic(self.fw.data_root / "link" / "x.json", {})

    def test_governance_is_read_only(self):
        (self.root / "governance").mkdir()
        (self.root / "governance" / "rule.md").write_text("synthetic rule\n")
        self.assertTrue(self.fw.sha256_file(self.root / "governance" / "rule.md"))
        with self.assertRaises(FirewallViolation):
            self.fw.write_text_atomic(self.root / "governance" / "rule.md", "changed")

    def test_create_exclusive_is_atomic_and_write_once(self):
        target = self.fw.artifact("prereg", "once.json")
        self.fw.create_exclusive(target, b"first\n")
        with self.assertRaises(FileExistsError):
            self.fw.create_exclusive(target, b"second\n")
        self.assertEqual(target.read_bytes(), b"first\n")
        self.assertEqual(sorted(p.name for p in target.parent.iterdir()), ["once.json"])


class SealValidationTests(unittest.TestCase):
    """Probes C and D: a sealable protocol must be complete and holdout-safe."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fw = Firewall(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def assertUnsealable(self, protocol):
        with self.assertRaises(pr.PreregInvalid):
            pr.seal_protocol(self.fw, protocol)
        self.assertFalse(pr.sealed_path(self.fw).exists())

    def test_complete_final_protocol_seals(self):
        record = pr.seal_protocol(self.fw, final_protocol())
        self.assertEqual(record["protocol_sha256"], pr.protocol_sha256(final_protocol()))

    def test_probe_c_incomplete_protocols_are_refused(self):
        self.assertUnsealable(final_protocol(open_decisions=["constructor size"]))
        self.assertUnsealable(final_protocol(frictions={}))
        p = final_protocol()
        p["multiplicity"]["M_declared"] = 999
        self.assertUnsealable(p)
        for seed in (None, "20260924", 2.5, True):
            p = final_protocol()
            p["inference"]["bootstrap_seed"] = seed
            self.assertUnsealable(p)
        for rule in ("return_object", "outcomes", "execution", "benchmark", "delisting"):
            p = final_protocol()
            p.pop(rule)
            self.assertUnsealable(p)
        p = final_protocol()
        p["population"].pop("footnote_exclusion_regex")
        self.assertUnsealable(p)
        p = final_protocol()
        p["benchmark"]["fallback"] = "YAHOO"
        self.assertUnsealable(p)

    def test_probe_d_price_windows_cannot_reach_the_holdout(self):
        for split in ("discovery", "walk_forward"):
            p = final_protocol()
            p["splits"][split]["price_window"]["end"] = "2026-09-30"
            self.assertUnsealable(p)

    def test_draft_cannot_be_sealed_and_frozen_splits_hold(self):
        self.assertUnsealable(final_protocol(status=pr.STATUS_DRAFT))
        p = final_protocol()
        p["splits"]["holdout"]["start"] = "2021-01-01"
        self.assertUnsealable(p)
        p = final_protocol()
        p["variants"] = [{"variant_id": f"V{i}", "census_family": "OD", "value_floor_usd": 0,
                          "horizon_sessions": 20} for i in range(49)]
        p["multiplicity"]["M_declared"] = 49
        self.assertUnsealable(p)

    def test_seal_is_write_once_and_canonical(self):
        record = pr.seal_protocol(self.fw, final_protocol())
        again = pr.seal_protocol(self.fw, final_protocol())
        self.assertEqual(again["sealed_at_utc"], record["sealed_at_utc"])
        changed = final_protocol()
        changed["variants"] = changed["variants"][:3]
        changed["multiplicity"]["M_declared"] = 3
        with self.assertRaises(pr.PreregAlreadySealed):
            pr.seal_protocol(self.fw, changed)
        a = {"b": 1, "a": [1, {"y": 2, "x": 1}]}
        b = json.loads('{"a": [1, {"x": 1, "y": 2}], "b": 1}')
        self.assertEqual(pr.protocol_sha256(a), pr.protocol_sha256(b))

    def test_repository_draft_is_complete_but_unsealable_as_draft(self):
        path = REPO / "research" / "fastlane" / "QUANT_FASTLANE_HPIT_V1_PROTOCOL.json"
        if not path.exists():
            self.skipTest("draft protocol not generated")
        protocol = json.loads(path.read_text())
        self.assertEqual(protocol["status"], pr.STATUS_DRAFT)
        self.assertEqual(protocol["open_decisions"], [])
        self.assertUnsealable(protocol)
        pr.validate_protocol({**protocol, "status": pr.STATUS_FINAL}, for_seal=True)
        ids = [v["variant_id"] for v in protocol["variants"]]
        self.assertEqual(protocol["multiplicity"]["M_declared"], len(ids))
        self.assertLessEqual(len(ids), pr.MAX_VARIANTS)


class GitAnchorTests(unittest.TestCase):
    """Probes H and B: a seal counts only if committed once, in HEAD, published, unchanged."""

    def test_probe_h_uncommitted_or_unpublished_seal_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp, commit=False, publish=False)
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", w.sha)
            w.commit_all("seal")                     # committed but not on any remote branch
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", w.sha)
            w.publish()
            grant = pr.require_outcome_access(w.fw, "discovery", w.sha)
            self.assertEqual(grant.split, "discovery")

    def test_probe_h_seal_outside_any_git_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            record = pr.seal_protocol(fw, final_protocol())
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(fw, "walk_forward", record["protocol_sha256"])

    def test_probe_b_delete_and_reseal_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            first = w.sha
            os.remove(pr.sealed_path(w.fw))
            other = final_protocol(w.protocol["census_binding"]["events_sha256"], w.relpath)
            other["variants"] = other["variants"][:3]
            other["multiplicity"]["M_declared"] = 3
            second = pr.seal_protocol(w.fw, other)["protocol_sha256"]
            self.assertNotEqual(first, second)
            # uncommitted replacement: bytes differ from the only adding commit
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", second)
            w.commit_all("reseal")
            w.publish()
            # committed replacement: the seal path now has more than one commit
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", second)

    def test_edited_seal_bytes_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            path = pr.sealed_path(w.fw)
            path.write_bytes(path.read_bytes() + b" ")     # same JSON, different bytes
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", w.sha)

    def test_verify_committed_reports_each_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            info = verify_committed(w.root, pr.sealed_path(w.fw))
            self.assertEqual(len(info.commit), 40)
            with self.assertRaises(GitCheckFailed):
                verify_committed(w.root, w.root / "missing.json")

    def test_probe_g_torn_seal_is_a_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            path = pr.sealed_path(fw)
            path.parent.mkdir(parents=True)
            path.write_bytes(b'{"lineage": "QUANT_')
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(fw, "discovery", "sha256:x")


class GrantTests(unittest.TestCase):
    """Probe A and friends: grants are minted only by require_outcome_access."""

    def test_probe_a_forged_grant_without_seal_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            forged = pr.OutcomeAccessGrant(LINEAGE_ID, "holdout", "sha256:forged",
                                           date(2021, 4, 1), date(2026, 9, 30), "r", tmp,
                                           "0" * 64)
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(forged, date(2021, 7, 1), date(2026, 6, 30))
            vendor = px.SharadarVendor(env={"NASDAQ_DATA_LINK_API_KEY": "synthetic-key"})
            with self.assertRaises(pr.OutcomeAccessRefused):
                vendor.daily_bars("SYN", date(2021, 7, 1), date(2026, 6, 30), grant=forged)
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(None, date(2021, 7, 1), date(2021, 7, 2))

    def test_forged_token_with_a_real_seal_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            real = pr.require_outcome_access(w.fw, "discovery", w.sha)
            px.check_grant(real, date(2010, 1, 4), date(2010, 2, 1))
            widened = pr.OutcomeAccessGrant(real.lineage, "discovery", real.prereg_sha256,
                                            real.price_window_start, date(2026, 9, 30), None,
                                            real.repo_root, real.token)
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(widened, date(2022, 1, 3), date(2022, 2, 1))
            as_holdout = pr.OutcomeAccessGrant(real.lineage, "holdout", real.prereg_sha256,
                                               real.price_window_start, real.price_window_end,
                                               "r", real.repo_root, real.token)
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(as_holdout, date(2010, 1, 4), date(2010, 2, 1))

    def test_discovery_grant_cannot_read_holdout_period_prices(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            grant = pr.require_outcome_access(w.fw, "discovery", w.sha)
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(grant, date(2021, 7, 1), date(2021, 8, 2))
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(grant, date(2018, 12, 1), date(2019, 1, 31))

    def test_grant_is_rechecked_against_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            grant = pr.require_outcome_access(w.fw, "discovery", w.sha)
            os.remove(pr.sealed_path(w.fw))
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(grant, date(2010, 1, 4), date(2010, 2, 1))

    def test_bound_event_table_and_vendor_manifests_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            events = w.root / w.relpath
            events.write_bytes(gzip.compress(b'{"accession":"changed"}\n', mtime=0))
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", w.sha)
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp, manifests=False)
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", w.sha)

    def test_wrong_expected_hash_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", "sha256:" + "0" * 64)


class HoldoutTests(unittest.TestCase):
    """Probes E1-E4 plus crash replay: one committed look, cache only in var/."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.w = World(self.tmp.name)
        self.finalists = self.w.variants(2)

    def tearDown(self):
        self.tmp.cleanup()

    def test_probe_e1_finalists_must_be_in_the_sealed_grid_with_trials(self):
        with self.assertRaises(pr.OutcomeAccessRefused):
            ho.write_holdout_request(self.w.fw, "look-1", ["NOT_IN_GRID"], EVAL_SPEC)
        v = self.w.variants(3)[2]
        self.w.trials([v], splits=("discovery",))                 # no walk-forward record
        with self.assertRaises(pr.OutcomeAccessRefused):
            ho.write_holdout_request(self.w.fw, "look-1", [v], EVAL_SPEC)
        with self.assertRaises(ho.NoFinalists):
            ho.write_holdout_request(self.w.fw, "look-1", [], EVAL_SPEC)
        self.assertFalse(ho.request_path(self.w.fw).exists())

    def test_probe_e2_replay_returns_the_same_grant(self):
        self.w.request("look-1", self.finalists)
        first = self.w.holdout("look-1", self.finalists)
        for _ in range(50):
            self.assertIs(self.w.holdout("look-1", list(reversed(self.finalists))), first)
        self.assertEqual(len(ho.HoldoutLedger(self.w.fw).records()), 1)
        px.check_grant(first, date(2021, 7, 1), date(2026, 6, 30))
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.holdout("look-1", self.finalists, spec="sha256:" + "f" * 64)

    def test_holdout_needs_a_committed_request(self):
        self.w.request("look-1", self.finalists, commit=False)
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.holdout("look-1", self.finalists)

    def test_probe_e3_deleting_the_cache_does_not_reopen_the_holdout(self):
        self.w.request("look-1", self.finalists)
        grant = self.w.holdout("look-1", self.finalists)
        cache = ho.HoldoutLedger(self.w.fw).path
        os.remove(cache)
        other = self.w.variants(3)[2:]
        self.w.trials(other)
        with self.assertRaises(ho.HoldoutAlreadyConsumed):
            self.w.holdout("look-2", other)
        with self.assertRaises(ho.HoldoutAlreadyConsumed):
            ho.write_holdout_request(self.w.fw, "look-2", other, EVAL_SPEC)
        # overwrite the committed request on disk: git bytes check refuses it
        path = ho.request_path(self.w.fw)
        forged = json.loads(path.read_text())
        forged.update({"request_id": "look-2", "finalists": sorted(other)})
        path.write_text(json.dumps(forged))
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.holdout("look-2", other)
        # commit the overwrite: the request is write-once, two commits touch it
        self.w.commit_all("second look")
        self.w.publish()
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.holdout("look-2", other)
        self.assertEqual(grant.holdout_request_id, "look-1")

    def test_cache_is_rebuilt_from_the_committed_request(self):
        self.w.request("look-1", self.finalists)
        grant = self.w.holdout("look-1", self.finalists)
        os.remove(ho.HoldoutLedger(self.w.fw).path)
        self.assertIs(self.w.holdout("look-1", self.finalists), grant)
        self.assertEqual(len(ho.HoldoutLedger(self.w.fw).records()), 1)

    def test_probe_e4_rewritten_cache_cannot_change_the_finalists(self):
        self.w.request("look-1", self.finalists)
        self.w.holdout("look-1", self.finalists)
        cache = ho.HoldoutLedger(self.w.fw).path
        record = json.loads(cache.read_text().splitlines()[0])
        other = self.w.variants(3)[2:]
        record.update({"request_id": "look-3", "finalists": other,
                       "request_fingerprint": "sha256:" + "1" * 64})
        cache.write_bytes(pr.canonical_json(record) + b"\n")
        with self.assertRaises(ho.HoldoutAlreadyConsumed):
            self.w.holdout("look-3", other)
        with self.assertRaises(ho.HoldoutAlreadyConsumed):     # cache disagrees: fail closed
            self.w.holdout("look-1", self.finalists)

    def test_idempotent_replay_after_simulated_crash(self):
        request = self.w.request("look-1", self.finalists)
        with self.assertRaises(ho.SimulatedCrash):
            ho.HoldoutLedger(self.w.fw).sync(request, crash_after_append=True)
        grant = self.w.holdout("look-1", self.finalists)
        self.assertEqual(grant.holdout_request_id, "look-1")
        self.assertEqual(len(ho.HoldoutLedger(self.w.fw).records()), 1)
        with self.assertRaises(ho.HoldoutAlreadyConsumed):
            self.w.holdout("look-2", self.finalists)

    def test_torn_cache_fails_closed(self):
        self.w.request("look-1", self.finalists)
        cache = ho.HoldoutLedger(self.w.fw).path
        self.w.fw.mkdirs(cache.parent)
        cache.write_bytes(b'{"request_id": "look-1", "requ')
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.holdout("look-1", self.finalists)

    def test_trial_ledger_rewrite_after_request_is_detected(self):
        self.w.request("look-1", self.finalists)
        path = ho.TrialLedger(self.w.fw).path
        lines = path.read_bytes().split(b"\n")[:-1]
        path.write_bytes(b"\n".join(lines[:-1]) + b"\n")          # truncate one trial
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.holdout("look-1", self.finalists)


class TrialLedgerTests(unittest.TestCase):
    def test_every_trial_is_recorded_once_and_chained(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp, commit=False, publish=False)
            ledger = ho.TrialLedger(w.fw)
            a, b = w.variants(2)
            spec = {"variant": a, "h": 20}
            first = ledger.record("t1", a, "discovery", spec)
            self.assertEqual(ledger.record("t1", a, "discovery", copy.deepcopy(spec)), first)
            self.assertEqual(first["prev_sha"], ho.GENESIS)
            with self.assertRaises(ho.TrialConflict):
                ledger.record("t1", a, "discovery", {"h": 60})
            with self.assertRaises(ho.TrialConflict):               # probe F: undeclared
                ledger.record("t2", "UNDECLARED", "discovery", {})
            ledger.record("t2", b, "walk_forward", {})
            ledger.record("t3", a, "walk_forward", {})
            self.assertEqual(ledger.multiplicity(), {
                "trials": 3, "distinct_variants": 2,
                "distinct_variants_by_split": {"discovery": 1, "walk_forward": 2}})
            lines = ledger.path.read_bytes().split(b"\n")
            edited = json.loads(lines[1])
            edited["variant_id"] = a
            lines[1] = pr.canonical_json(edited)
            ledger.path.write_bytes(b"\n".join(lines))
            with self.assertRaises(ho.LedgerCorrupted):
                ledger.records()

    def test_trials_need_a_seal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(pr.PreregNotSealed):
                ho.TrialLedger(Firewall(Path(tmp))).record("t1", "X", "discovery", {})


if __name__ == "__main__":
    unittest.main()

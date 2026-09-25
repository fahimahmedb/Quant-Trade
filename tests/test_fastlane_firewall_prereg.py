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


DOC_SOURCE = {"documentation_url": "https://example.invalid/vendor/delisting-codes",
              "retrieved_on": "2026-09-24"}


class World:
    """A temp git repo with a bare 'origin' remote and a sealed, committed, pushed protocol."""

    def __init__(self, tmp, *, seal=True, commit=True, publish=True, manifests=True):
        base = Path(tmp)
        self.remote = base / "remote.git"
        self.root = base / "work"
        self.root.mkdir()
        git(base, "init", "-q", "--bare", "-b", "main", str(self.remote))
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "remote", "add", "origin", str(self.remote))
        (self.root / "README").write_text("synthetic fast-lane test repository\n")
        self.commit_all("base")
        self.publish()
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
                "derivation": "VENDOR_DOCUMENTATION_ONLY", "source": DOC_SOURCE,
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

    def publish(self, force=False):
        git(self.root, "push", "-q", *(["-f"] if force else []), "origin", "HEAD:main")

    def head(self):
        return git(self.root, "rev-parse", "HEAD").stdout.decode().strip()

    def variants(self, n=None):
        ids = [v["variant_id"] for v in self.protocol["variants"]]
        return ids if n is None else ids[:n]

    def trials(self, variants, splits=("discovery", "walk_forward")):
        ledger = ho.TrialLedger(self.fw)
        for v in variants:
            for s in splits:
                ledger.record(f"{v}-{s}", v, s, {"variant": v, "split": s})

    def screen_all(self):
        self.trials(self.variants(), splits=("discovery",))

    def write_request(self, request_id, variants):
        """LOW-LEVEL: a structurally consistent screen report/spec plus an in-process receipt,
        handed to the private writer, to test git anchoring and the one-look cache. The
        verified path (full screen recomputation) is tested in test_fastlane_evaluation_screen."""
        sealed = pr.load_sealed(self.fw)
        records = {(r["variant_id"], r["split"]): r for r in ho.TrialLedger(self.fw).records()}
        listing = {}
        for v in self.variants():
            for s in ho.REQUIRED_TRIAL_SPLITS:
                if (v, s) in records:
                    listing.setdefault(v, {})[s] = {"trial_id": records[(v, s)]["trial_id"],
                                                    "spec_digest": records[(v, s)]["spec_digest"]}
        spec = {"kind": "SYNTHETIC_LOW_LEVEL_SPEC", "finalists": sorted(variants)}
        spec_digest = ho.json_digest(spec)
        report = {"prereg_sha256": self.sha, "finalists": sorted(variants), "trials": listing,
                  "holdout_request_payload": {"eval_spec_digest": spec_digest},
                  "n_trials_for_dsr": ho.n_trials_conservative(self.fw, sealed)["n_trials_for_dsr"]}
        report_digest = ho.json_digest(report)
        if not ho.request_path(self.fw).exists():
            for path, obj in ((ho.screen_report_path(self.fw), report),
                              (ho.eval_spec_path(self.fw), spec)):
                self.fw.write_bytes_atomic(path, pr.canonical_json(obj) + b"\n")
        receipt = ho._screen_receipt(self.fw, self.sha, request_id, variants, spec_digest,
                                     report_digest)
        record = ho._write_holdout_request(self.fw, request_id, variants, spec_digest,
                                           report_digest, receipt=receipt)
        self.spec_digest = spec_digest
        return record

    def request(self, request_id, variants, *, commit=True):
        self.trials(self.variants())                  # every declared variant, both splits
        record = self.write_request(request_id, variants)
        if commit:
            self.commit_all("holdout request")
            self.publish()
        return record

    def receipt(self):
        req = ho.read_holdout_request(self.fw) or {}
        return ho._screen_receipt(self.fw, self.sha, str(req.get("request_id")),
                                  req.get("finalists") or [], str(req.get("eval_spec_digest")),
                                  str(req.get("screen_report_digest")))

    def holdout(self, request_id, variants, spec=None, receipt=True):
        return pr.require_outcome_access(
            self.fw, "holdout", self.sha, holdout_request_id=request_id,
            holdout_variants=variants,
            eval_spec_digest=spec or getattr(self, "spec_digest", EVAL_SPEC),
            holdout_receipt=self.receipt() if receipt else None)


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

    def test_repository_protocol_is_the_sealed_protocol(self):
        path = REPO / "research" / "fastlane" / "QUANT_FASTLANE_HPIT_V1_PROTOCOL.json"
        sealed = REPO / "research" / "fastlane" / "prereg" / "QUANT_FASTLANE_HPIT_V1_PREREG_SEALED.json"
        if not path.exists() or not sealed.exists():
            self.skipTest("protocol not generated or not sealed")
        protocol = json.loads(path.read_text())
        record = json.loads(sealed.read_text())
        self.assertEqual(protocol["status"], pr.STATUS_FINAL)
        self.assertEqual(protocol["open_decisions"], [])
        pr.validate_protocol(protocol, for_seal=True)
        self.assertEqual(pr.protocol_sha256(protocol), record["protocol_sha256"])
        self.assertEqual(pr.protocol_sha256(record["protocol"]), record["protocol_sha256"])
        self.assertEqual(record["lineage"], LINEAGE_ID)
        # The draft form of the same content stays unsealable.
        self.assertUnsealable({**protocol, "status": pr.STATUS_DRAFT})
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
            w.commit_all("seal")                     # committed but not pushed
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(w.fw, "discovery", w.sha)
            w.publish()
            grant = pr.require_outcome_access(w.fw, "discovery", w.sha)
            self.assertEqual(grant.split, "discovery")

    def test_probe_n1_local_remote_tracking_ref_does_not_count_as_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp, publish=False)
            git(w.root, "update-ref", "refs/remotes/origin/fake", "HEAD")
            git(w.root, "update-ref", "refs/remotes/origin/main", "HEAD")
            with self.assertRaises(pr.OutcomeAccessRefused) as ctx:
                pr.require_outcome_access(w.fw, "discovery", w.sha)
            self.assertIn("(c)", str(ctx.exception))

    def test_probe_n3_shallow_clone_is_refused_with_unshallow_advice(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            shallow = Path(tmp) / "shallow"
            git(Path(tmp), "clone", "-q", "--depth", "1", "--branch", "main",
                "file://" + str(w.remote), str(shallow))
            fw = Firewall(shallow)
            with self.assertRaises(pr.OutcomeAccessRefused) as ctx:
                pr.require_outcome_access(fw, "discovery", w.sha)
            self.assertIn("git fetch --unshallow", str(ctx.exception))
            git(shallow, "fetch", "-q", "--unshallow")
            self.assertEqual(pr.require_outcome_access(fw, "discovery", w.sha).split, "discovery")

    def test_probe_n5_detached_head_is_fine(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            git(w.root, "checkout", "-q", "--detach")
            self.assertEqual(pr.require_outcome_access(w.fw, "discovery", w.sha).split,
                             "discovery")

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
            # committed and pushed replacement: the seal path now has more than one commit
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
            self.w.write_request("look-1", ["NOT_IN_GRID"])
        v = self.w.variants(3)[2]
        self.w.screen_all()                                       # every variant screened
        self.w.trials([v], splits=("discovery",))                 # no walk-forward record
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.write_request("look-1", [v])
        with self.assertRaises(ho.NoFinalists):
            self.w.write_request("look-1", [])
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
            self.w.write_request("look-2", other)
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

    def test_request_and_look_need_the_recomputation_receipt(self):
        self.assertFalse(hasattr(ho, "write_holdout_request"))   # no public bypass
        self.w.trials(self.w.variants())
        with self.assertRaises(pr.OutcomeAccessRefused):
            ho._write_holdout_request(self.w.fw, "look-1", self.finalists, EVAL_SPEC,
                                      "sha256:" + "0" * 64, receipt="0" * 64)
        self.assertFalse(ho.request_path(self.w.fw).exists())
        self.w.request("look-1", self.finalists)
        for forged in (False, "0" * 64):
            with self.assertRaises(pr.OutcomeAccessRefused):
                pr.require_outcome_access(self.w.fw, "holdout", self.w.sha,
                                          holdout_request_id="look-1",
                                          holdout_variants=self.finalists,
                                          eval_spec_digest=self.w.spec_digest,
                                          holdout_receipt=forged or None)
        self.assertEqual(ho.HoldoutLedger(self.w.fw).records(), [])   # look not consumed
        self.assertEqual(self.w.holdout("look-1", self.finalists).holdout_request_id, "look-1")

    def test_screen_report_must_match_every_declared_trial(self):
        self.w.request("look-1", self.finalists)
        path = ho.TrialLedger(self.w.fw).path
        lines = path.read_bytes().split(b"\n")[:-1]
        forged = json.loads(lines[-1])
        forged["spec_digest"] = "sha256:" + "9" * 64            # swap one record's content
        prev = forged["prev_sha"]
        path.write_bytes(b"\n".join(lines[:-1]) + b"\n" + pr.canonical_json(
            {**forged, "prev_sha": prev}) + b"\n")
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.holdout("look-1", self.finalists)
        self.assertEqual(ho.HoldoutLedger(self.w.fw).records(), [])

    def test_trial_ledger_rewrite_after_request_is_detected(self):
        self.w.request("look-1", self.finalists)
        path = ho.TrialLedger(self.w.fw).path
        lines = path.read_bytes().split(b"\n")[:-1]
        path.write_bytes(b"\n".join(lines[:-1]) + b"\n")          # truncate one trial
        with self.assertRaises(pr.OutcomeAccessRefused):
            self.w.holdout("look-1", self.finalists)


class SecondReviewTests(unittest.TestCase):
    """Re-review probes A', N4, the force-push pin, pinned numbers, doc-derived map, crash temp."""

    def test_probe_a_prime_in_process_token_on_uncommitted_seal_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp, commit=False, publish=False)
            start, end = pr.price_window(w.protocol, "walk_forward")
            token = pr._token(LINEAGE_ID, "walk_forward", w.sha, start, end, None, str(w.root))
            forged = pr.OutcomeAccessGrant(LINEAGE_ID, "walk_forward", w.sha, start, end, None,
                                           str(w.root), token)
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(forged, date(2019, 1, 2), date(2021, 6, 30))

    def test_probe_n4_every_declared_variant_needs_a_discovery_trial(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            finalist = w.variants(1)
            w.trials(finalist)                                   # finalist-only ledger
            with self.assertRaises(pr.OutcomeAccessRefused) as ctx:
                w.write_request("look-1", finalist)
            self.assertIn("declared variants have no discovery trial", str(ctx.exception))
            w.screen_all()                                       # discovery only
            with self.assertRaises(pr.OutcomeAccessRefused) as ctx:
                w.write_request("look-1", finalist)
            self.assertIn("walk_forward trial record", str(ctx.exception))
            w.trials(w.variants(), splits=("walk_forward",))
            request = w.write_request("look-1", finalist)
            m = w.protocol["multiplicity"]["M_declared"]
            self.assertEqual(request["multiplicity"]["M_declared"], m)
            self.assertEqual(request["multiplicity"]["sealed_rule"], 2 * m)
            self.assertEqual(request["multiplicity"]["n_trials_for_dsr"], 2 * m)
            self.assertEqual(ho.TrialLedger(w.fw).multiplicity()["n_trials_for_dsr"], 2 * m)

    def test_n_trials_is_at_least_m_declared(self):
        sealed = {"protocol_sha256": "sha256:x",
                  "protocol": {"multiplicity": {"M_declared": 21}}}
        few = [{"trial_id": f"t{i}", "prereg_sha256": "sha256:x"} for i in range(3)]
        many = [{"trial_id": f"t{i}", "prereg_sha256": "sha256:x"} for i in range(40)]
        self.assertEqual(ho.n_trials_for_dsr(sealed, few), 21)
        self.assertEqual(ho.n_trials_for_dsr(sealed, many), 40)

    def test_force_push_rewriting_the_seal_commit_is_detected_at_the_next_grant(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            finalists = w.variants(2)
            request = w.request("look-1", finalists)
            self.assertEqual(len(request["seal_commit"]), 40)
            grant = w.holdout("look-1", finalists)
            # rewrite history: squash seal and request into a new commit, force-push
            base = git(w.root, "rev-list", "--max-parents=0", "HEAD").stdout.decode().strip()
            git(w.root, "reset", "-q", "--soft", base)
            git(w.root, "commit", "-q", "-m", "rewritten history")
            w.publish(force=True)
            with self.assertRaises(pr.OutcomeAccessRefused) as ctx:
                w.holdout("look-1", finalists)
            self.assertIn("seal commit changed", str(ctx.exception))
            with self.assertRaises(pr.OutcomeAccessRefused):
                px.check_grant(grant, date(2021, 7, 1), date(2021, 8, 2))

    def test_pinned_d5_numbers_refuse_any_deviation(self):
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            changes = {
                "frictions.participation_cap_adv20": 0.002,
                "frictions.untradeable_adv20_below_usd": 50_000.0,
                "frictions.commission.per_share_usd": 0.0,
                "frictions.commission.minimum_usd": 0.0,
                "frictions.impact.coefficient": 0.5,
                "go_criterion.alpha_min_annual": 0.02,
                "go_criterion.holm_family_alpha": 0.10,
                "go_criterion.dsr_min": 0.90,
                "inference.block_length_sessions": 40,
                "inference.bootstrap_draws": 999,
                "inference.co_check.kernel": "none",
                "inference.co_check.bandwidth_b": 0.2,
                "inference.seed_robustness.gating": True,
                "outcomes.inconclusive_upper_bound_min_annual": 0.0,
            }
            for dotted, value in changes.items():
                p = final_protocol()
                node = p
                *parents, leaf = dotted.split(".")
                for part in parents:
                    node = node[part]
                node[leaf] = value
                with self.assertRaises(pr.PreregInvalid, msg=dotted):
                    pr.seal_protocol(fw, p)
            p = final_protocol()
            p["frictions"]["spread"]["adv20_bucket_floor_bps"][0]["floor_bps"] = 0.0
            with self.assertRaises(pr.PreregInvalid):
                pr.seal_protocol(fw, p)
            p = final_protocol()
            p["frictions"]["delisting_classes"]["UNKNOWN"]["base"] = 0.0
            with self.assertRaises(pr.PreregInvalid):
                pr.seal_protocol(fw, p)
            p = final_protocol()
            p["frictions"]["delisting_classes"]["BANKRUPTCY_OR_CAUSE"]["base"] = -0.5
            with self.assertRaises(pr.PreregInvalid):
                pr.seal_protocol(fw, p)
            p = final_protocol()
            p["delisting"]["classes"] = {"UNKNOWN": "0 %"}
            with self.assertRaises(pr.PreregInvalid):
                pr.seal_protocol(fw, p)
            p = final_protocol()
            p["governance"].pop("residual_risk")
            with self.assertRaises(pr.PreregInvalid):
                pr.seal_protocol(fw, p)
            self.assertFalse(pr.sealed_path(fw).exists())
            self.assertEqual(final_protocol()["inference"]["seed_robustness"]["seeds"],
                             [20260925, 20260926, 20260927, 20260928, 20260929])

    def test_delisting_map_must_cite_vendor_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp, commit=False, publish=False)
            m = w.fw.read_json(pr.delisting_map_path(w.fw))
            m.pop("source")
            w.fw.write_json_atomic(pr.delisting_map_path(w.fw), m)
            w.commit_all("seal")
            w.publish()
            with self.assertRaises(pr.OutcomeAccessRefused) as ctx:
                pr.require_outcome_access(w.fw, "discovery", w.sha)
            self.assertIn("documentation", str(ctx.exception))

    def test_probe_p9_crash_during_seal_leaves_no_committable_or_valid_partial(self):
        import fnmatch
        import sys
        child = (
            "import os, sys, json\n"
            "sys.path.insert(0, sys.argv[3])\n"
            "from pathlib import Path\n"
            "from quant.fastlane.firewall import Firewall\n"
            "from quant.fastlane import preregistration as pr\n"
            "p = json.loads(Path(sys.argv[2]).read_text())\n"
            "if sys.argv[4] == 'before_link':\n"
            "    os.link = lambda *a: os._exit(9)\n"
            "else:\n"
            "    os.unlink = lambda *a, **k: os._exit(9)\n"
            "pr.seal_protocol(Firewall(Path(sys.argv[1])), p)\n")
        src = str(REPO / "src")
        for where in ("before_link", "after_link"):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "root"
                root.mkdir()
                proto = Path(tmp) / "protocol.json"
                proto.write_text(json.dumps(final_protocol()))
                rc = subprocess.run([sys.executable, "-c", child, str(root), str(proto), src,
                                     where]).returncode
                self.assertEqual(rc, 9)
                fw = Firewall(root)
                folder = pr.sealed_path(fw).parent
                leftovers = [p.name for p in folder.iterdir() if p.name.endswith(".tmp")]
                self.assertEqual(len(leftovers), 1)
                self.assertTrue(fnmatch.fnmatch(f"research/fastlane/prereg/{leftovers[0]}",
                                                "research/fastlane/prereg/.*.tmp"))
                if where == "before_link":
                    with self.assertRaises(pr.PreregNotSealed):
                        pr.load_sealed(fw)
                else:
                    self.assertTrue(pr.load_sealed(fw)["protocol_sha256"].startswith("sha256:"))
                record = pr.seal_protocol(fw, final_protocol())       # recovery / replay
                self.assertEqual(record["protocol_sha256"], pr.protocol_sha256(final_protocol()))
                ho.request_path(fw).parent.mkdir(parents=True, exist_ok=True)
                fw.create_exclusive(folder / "probe.json", b"{}\n")   # cleans stale temps
                if where == "before_link":
                    self.assertFalse([p for p in folder.iterdir()
                                      if p.name.startswith(f".{pr.sealed_path(fw).name}")])
        ignore = (REPO / ".gitignore").read_text().splitlines()
        self.assertIn("research/fastlane/prereg/.*.tmp", ignore)


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
            m = w.protocol["multiplicity"]["M_declared"]
            self.assertEqual(ledger.multiplicity(), {
                "trials": 3, "distinct_variants": 2,
                "distinct_variants_by_split": {"discovery": 1, "walk_forward": 2},
                "n_trials_for_dsr": max(m, 3)})
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

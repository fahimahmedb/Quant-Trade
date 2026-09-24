"""Fast-lane SEC insider data-set ingestion: UA, fair access, manifests (no network)."""

import io
import tempfile
import unittest
import urllib.error
import zipfile
from pathlib import Path

from quant.fastlane import sec_insider as si
from quant.fastlane.firewall import Firewall
from tests.test_fastlane_events import owner, sub, synthetic_zip, trans

SYNTH_UA = "Synthetic Tester synthetic@example.invalid"


class FakeResponse:
    def __init__(self, body: bytes, status=200, headers=None):
        self._buf = io.BytesIO(body)
        self.status = status
        self.headers = {"Content-Length": str(len(body)), **(headers or {})}

    def read(self, n=-1):
        return self._buf.read(n)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeOpener:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def __call__(self, request, timeout=None):
        self.calls.append(request)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def http_error(code):
    return urllib.error.HTTPError("https://www.sec.gov/x", code, "synthetic", {}, None)


class Clock:
    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class UserAgentTests(unittest.TestCase):
    def test_missing_user_agent_raises(self):
        with self.assertRaises(si.MissingUserAgent):
            si.require_user_agent({})
        with self.assertRaises(si.MissingUserAgent):
            si.require_user_agent({si.USER_AGENT_ENV: "   "})
        with self.assertRaises(si.MissingUserAgent):
            si.require_user_agent({si.USER_AGENT_ENV: "no contact address"})
        with self.assertRaises(si.MissingUserAgent):
            si.SecClient("")
        self.assertEqual(si.require_user_agent({si.USER_AGENT_ENV: SYNTH_UA}), SYNTH_UA)

    def test_binding_never_contains_the_address(self):
        binding = si.ua_binding(SYNTH_UA)
        self.assertTrue(binding.startswith("sha256:"))
        self.assertNotIn("example", binding)
        self.assertEqual(binding, si.ua_binding(SYNTH_UA))
        self.assertNotEqual(binding, si.ua_binding(SYNTH_UA + "x"))

    def test_request_carries_declared_agent(self):
        opener = FakeOpener([FakeResponse(b"ok")])
        clock = Clock()
        client = si.SecClient(SYNTH_UA, opener=opener, sleep=clock.sleep,
                              monotonic=clock.monotonic)
        client.get_bytes("https://www.sec.gov/x")
        self.assertEqual(opener.calls[0].get_header("User-agent"), SYNTH_UA)


class FairAccessTests(unittest.TestCase):
    def client(self, script):
        clock = Clock()
        opener = FakeOpener(script)
        return si.SecClient(SYNTH_UA, opener=opener, sleep=clock.sleep,
                            monotonic=clock.monotonic), opener, clock

    def test_requests_are_paced_to_at_most_five_per_second(self):
        client, opener, clock = self.client([FakeResponse(b"a") for _ in range(6)])
        starts = []
        for _ in range(6):
            client.get_bytes("https://www.sec.gov/x")
            starts.append(clock.t)
        gaps = [b - a for a, b in zip(starts, starts[1:])]
        self.assertTrue(all(g >= 0.2 for g in gaps), gaps)

    def test_retry_with_backoff_on_429_403_and_5xx(self):
        client, opener, clock = self.client([http_error(429), http_error(503), http_error(403),
                                             FakeResponse(b"done")])
        self.assertEqual(client.get_bytes("https://www.sec.gov/x").body, b"done")
        self.assertEqual(len(opener.calls), 4)
        backoffs = [s for s in clock.sleeps if s >= 1.0]
        self.assertEqual(backoffs, [2.0, 4.0, 8.0])

    def test_non_retryable_status_fails_immediately(self):
        client, opener, _ = self.client([http_error(404)])
        with self.assertRaises(si.SecFetchError):
            client.get_bytes("https://www.sec.gov/x")
        self.assertEqual(len(opener.calls), 1)

    def test_gives_up_after_bounded_attempts(self):
        client, opener, _ = self.client([http_error(503)] * si.MAX_ATTEMPTS)
        with self.assertRaises(si.SecFetchError):
            client.get_bytes("https://www.sec.gov/x")
        self.assertEqual(len(opener.calls), si.MAX_ATTEMPTS)


class DiscoveryTests(unittest.TestCase):
    def test_links_are_read_from_the_page_not_constructed(self):
        html = ('<a href="/files/structureddata/data/insider-transactions-data-sets/'
                '2006q2_form345.zip">x</a><a href="/files/datastandardsinnovation/data/'
                'insider-transactions-data-sets/2026q2_form345.zip">y</a>'
                '<a href="/files/structureddata/data/insider-transactions-data-sets/'
                '2006q1_form345.zip">z</a>')
        links = si.parse_quarter_links(html)
        self.assertEqual([l.quarter for l in links], ["2006q1", "2006q2", "2026q2"])
        self.assertIn("datastandardsinnovation", links[-1].url)

    def test_conflicting_links_for_one_quarter_are_an_error(self):
        html = ('<a href="/files/a/2010q1_form345.zip"></a>'
                '<a href="/files/b/2010q1_form345.zip"></a>')
        with self.assertRaises(si.SecParseError):
            si.parse_quarter_links(html)

    def test_quarter_bounds(self):
        from datetime import date
        self.assertEqual(si.quarter_bounds("2024q1"), (date(2024, 1, 1), date(2024, 3, 31)))
        self.assertEqual(si.quarter_bounds("2023q4"), (date(2023, 10, 1), date(2023, 12, 31)))


class ManifestTests(unittest.TestCase):
    def test_fingerprint_is_stable_across_retrievals_and_sensitive_to_content(self):
        base = {"source": si.SOURCE_ID, "quarter": "2010q1", "url": "https://www.sec.gov/f.zip",
                "bytes": 10, "sha256": "ab" * 32, "members": [{"name": "SUBMISSION.tsv",
                                                               "size": 5, "crc32": "00000001"}],
                "retrieved_at_utc": "2026-09-24T00:00:00Z", "http_last_modified": "a",
                "ua_binding": "sha256:1"}
        later = {**base, "retrieved_at_utc": "2027-01-01T00:00:00Z",
                 "http_last_modified": "b", "http_etag": "z", "ua_binding": "sha256:2"}
        self.assertEqual(si.manifest_fingerprint(base), si.manifest_fingerprint(later))
        self.assertNotEqual(si.manifest_fingerprint(base),
                            si.manifest_fingerprint({**base, "sha256": "cd" * 32}))
        self.assertNotEqual(si.manifest_fingerprint(base),
                            si.manifest_fingerprint({**base, "url": "https://www.sec.gov/g.zip"}))

    def test_fetch_is_idempotent_and_resumable(self):
        payload = synthetic_zip([sub("0000000009-10-000001")], [owner("0000000009-10-000001")],
                                [trans("0000000009-10-000001", "1")])
        link = si.QuarterLink("2010q1", "https://www.sec.gov/files/synthetic/2010q1_form345.zip")
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            clock = Clock()
            opener = FakeOpener([FakeResponse(payload, headers={"Last-Modified": "synthetic"})])
            client = si.SecClient(SYNTH_UA, opener=opener, sleep=clock.sleep,
                                  monotonic=clock.monotonic)
            manifest, action = si.fetch_quarter(fw, client, link, budget_bytes=10**9, min_free_bytes=0)
            self.assertEqual(action, "fetched")
            self.assertEqual(manifest["bytes"], len(payload))
            self.assertEqual(manifest["http_last_modified"], "synthetic")
            self.assertNotIn("example", str(manifest))
            again, action = si.fetch_quarter(fw, client, link, budget_bytes=10**9, min_free_bytes=0)
            self.assertEqual(action, "skipped_sha256_match")
            self.assertEqual(len(opener.calls), 1)               # no second request
            self.assertEqual(again["fingerprint"], manifest["fingerprint"])
            # a damaged local copy is re-fetched, not trusted
            si.raw_path(fw, "2010q1").write_bytes(b"damaged")
            opener.script.append(FakeResponse(payload))
            _, action = si.fetch_quarter(fw, client, link, budget_bytes=10**9, min_free_bytes=0)
            self.assertEqual(action, "fetched")
            self.assertEqual(len(opener.calls), 2)

    def test_truncated_or_invalid_zip_is_rejected(self):
        link = si.QuarterLink("2010q1", "https://www.sec.gov/files/synthetic/2010q1_form345.zip")
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            clock = Clock()
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr("SUBMISSION.tsv", "ACCESSION_NUMBER\n")
            opener = FakeOpener([FakeResponse(buf.getvalue())])
            client = si.SecClient(SYNTH_UA, opener=opener, sleep=clock.sleep,
                                  monotonic=clock.monotonic)
            with self.assertRaises(si.SecParseError):
                si.fetch_quarter(fw, client, link, budget_bytes=10**9, min_free_bytes=0)
            self.assertIsNone(si.load_manifest(fw, "2010q1"))
            self.assertFalse(si.raw_path(fw, "2010q1").exists())
            self.assertEqual(list(si.raw_path(fw, "2010q1").parent.iterdir()), [])


class TableParsingTests(unittest.TestCase):
    def test_missing_required_column_and_malformed_rows(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("SUBMISSION.tsv", "ACCESSION_NUMBER\tFILING_DATE\nX\t01-JAN-2010\n")
            cols = list(si.REQUIRED_COLUMNS["REPORTINGOWNER.tsv"])
            z.writestr("REPORTINGOWNER.tsv", "\t".join(cols) + "\n" + "\t".join("a" * len(cols))
                       + "\n" + "too\tfew\n")
        with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as z:
            with self.assertRaises(si.SecParseError):
                list(si.iter_table(z, "SUBMISSION.tsv"))
            stats = si.TableStats("REPORTINGOWNER.tsv")
            rows = list(si.iter_table(z, "REPORTINGOWNER.tsv", stats))
            self.assertEqual(len(rows), 1)
            self.assertEqual(stats.malformed_rows, 1)


if __name__ == "__main__":
    unittest.main()

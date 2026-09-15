"""SEC HTTP identity contract.

The V2-A gate once failed with a green connectivity preflight and a refused
acquisition. The cause was not the network: the preflight and the Python
acquisition derived their HTTP identity from different places, so they were two
different clients, and only one of them was compliant.

These tests make that divergence impossible to reintroduce. They are transport
tests only and assert nothing about the census definition.
"""

import importlib.util
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def load_census_script():
    """Load the census entry point by path.

    ``scripts/`` cannot go on ``sys.path``: it contains ``quant.py``, which would
    shadow the ``quant`` package.
    """
    spec = importlib.util.spec_from_file_location(
        "sec_form4_census_under_test", ROOT / "scripts" / "sec_form4_census.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

from quant.dataplane import sec_form4
from quant.dataplane.sec_form4 import (
    NEW_SEC_ZIP_ROOT,
    OLD_SEC_ZIP_ROOT,
    SEC_USER_AGENT_ENV,
    SecIdentityError,
    sec_identity_is_compliant,
    sec_identity_problem,
    sec_request_headers,
    sec_user_agent,
    source_url_candidates,
)

COMPLIANT = "Quant-Trade Research analyst@example.com"
WORKFLOW = ROOT / ".github" / "workflows" / "sec-form4-census-proof.yml"


def declared(identity: str | None):
    """Context manager setting (or clearing) the declared SEC identity."""
    return mock.patch.dict(os.environ, {} if identity is None else
                           {SEC_USER_AGENT_ENV: identity},
                           clear=identity is None)


class IdentityContractTests(unittest.TestCase):
    def test_an_undeclared_identity_fails_loudly(self):
        with declared(None):
            with self.assertRaises(SecIdentityError) as caught:
                sec_user_agent()
        self.assertIn(SEC_USER_AGENT_ENV, str(caught.exception))

    def test_an_identity_without_a_contact_address_is_refused(self):
        # The exact declaration the WIP shipped with. SEC answers it with a 403
        # whose body says "Request Rate Threshold Exceeded", which is a
        # compliance rejection wearing a rate-limit message.
        legacy = "Quant-Trade SEC Form4 Census research contact: project-owner-via-github"
        self.assertFalse(sec_identity_is_compliant(legacy))
        self.assertIn("contact email", sec_identity_problem(legacy))

    def test_an_identity_containing_github_com_is_refused(self):
        """Empirically verified against the official 2020Q1 URL."""
        for identity in ("Quant-Trade Research a@users.noreply.github.com",
                         "Quant-Trade Research a@example.com https://github.com/x/y",
                         "Quant-Trade Research a@github.com"):
            with self.subTest(identity=identity):
                self.assertFalse(sec_identity_is_compliant(identity))
                self.assertIn("github.com", sec_identity_problem(identity))

    def test_a_reachable_contact_address_is_accepted(self):
        self.assertTrue(sec_identity_is_compliant(COMPLIANT))
        with declared(COMPLIANT):
            self.assertEqual(sec_user_agent(), COMPLIANT)


class OneIdentityTests(unittest.TestCase):
    """Every SEC request must be the same client."""

    def captured_headers(self, call) -> dict[str, str]:
        seen: dict[str, dict[str, str]] = {}

        class Response:
            status = 200

            def read(self, *_):
                return b"PK\x03\x04payload"

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

        def fake_urlopen(request, timeout=None):
            seen["headers"] = dict(request.headers)
            return Response()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            call()
        return seen["headers"]

    def test_http_get_uses_the_declared_identity(self):
        with declared(COMPLIANT):
            headers = self.captured_headers(
                lambda: sec_form4._http_get("https://www.sec.gov/x", delay=0))
        self.assertEqual(headers["User-agent"], COMPLIANT)

    def test_the_identity_is_not_frozen_at_import_time(self):
        """A default argument bound to a module constant would reintroduce the bug."""
        first = "Quant-Trade Research one@example.com"
        second = "Quant-Trade Research two@example.com"
        with declared(first):
            a = self.captured_headers(
                lambda: sec_form4._http_get("https://www.sec.gov/x", delay=0))
        with declared(second):
            b = self.captured_headers(
                lambda: sec_form4._http_get("https://www.sec.gov/x", delay=0))
        self.assertEqual(a["User-agent"], first)
        self.assertEqual(b["User-agent"], second)

    def test_preflight_and_acquisition_send_identical_headers(self):
        """The regression this suite exists for."""
        census = load_census_script()

        with declared(COMPLIANT):
            acquisition = self.captured_headers(
                lambda: census.sec_fetch("https://www.sec.gov/quarterly.zip"))
            acceptance = self.captured_headers(
                lambda: sec_form4._http_get("https://www.sec.gov/Archives/x", delay=0))
            preflight = self.captured_headers(lambda: census.preflight())
        self.assertEqual(acquisition, acceptance,
                         "quarterly acquisition and EDGAR acceptance headers differ")
        self.assertEqual(preflight, acquisition,
                         "the preflight is not the same HTTP client as the acquisition")

    def test_the_workflow_preflight_does_not_declare_its_own_identity(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("scripts/sec_form4_census.py --preflight", text,
                      "the CI preflight must run through the acquisition path")
        self.assertNotIn("--user-agent", text,
                         "the CI preflight must not carry its own User-Agent literal")

    def test_the_workflow_sec_identity_would_not_be_refused(self):
        """The declaration the gate exports must itself be acceptable to SEC."""
        lines = [line.split(":", 1)[1].strip()
                 for line in WORKFLOW.read_text(encoding="utf-8").splitlines()
                 if line.strip().startswith(f"{SEC_USER_AGENT_ENV}:")]
        self.assertEqual(len(lines), 1, "the gate must declare exactly one SEC identity")
        declaration = lines[0]
        for refused in sec_form4.SEC_REFUSED_UA_TOKENS:
            self.assertNotIn(refused, declaration.lower(),
                             f"SEC refuses any User-Agent containing {refused!r}")


class TransportSemanticsTests(unittest.TestCase):
    def test_a_client_refusal_is_not_retried(self):
        attempts = {"n": 0}

        def fake_urlopen(request, timeout=None):
            attempts["n"] += 1
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)

        with declared(COMPLIANT), mock.patch("urllib.request.urlopen", fake_urlopen):
            with self.assertRaises(urllib.error.HTTPError):
                sec_form4._http_get("https://www.sec.gov/missing.zip", delay=0)
        self.assertEqual(attempts["n"], 1, "a 404 is an absent object, not a transient fault")

    def test_both_quarter_candidates_are_official_sec_roots(self):
        for year, quarter in ((2020, 1), (2026, 1), (2026, 2)):
            with self.subTest(period=f"{year}Q{quarter}"):
                candidates = source_url_candidates(year, quarter)
                self.assertEqual(len(candidates), 2)
                for url in candidates:
                    self.assertTrue(url.startswith((OLD_SEC_ZIP_ROOT, NEW_SEC_ZIP_ROOT)),
                                    f"{url} is not an official SEC root")
                    self.assertTrue(url.startswith("https://www.sec.gov/"))

    def test_2026q1_and_2026q2_resolve_to_the_roots_sec_actually_serves(self):
        """A hardcoded year boundary asked the wrong root for 2026Q1."""
        self.assertTrue(source_url_candidates(2026, 1)[0].startswith(OLD_SEC_ZIP_ROOT))
        self.assertTrue(source_url_candidates(2026, 2)[0].startswith(NEW_SEC_ZIP_ROOT))

    def test_request_headers_are_one_mapping(self):
        with declared(COMPLIANT):
            headers = sec_request_headers()
        self.assertEqual(headers["User-Agent"], COMPLIANT)
        self.assertEqual(headers["Accept-Encoding"], "identity")


if __name__ == "__main__":
    unittest.main()

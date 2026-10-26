from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "oracle_release_install",
    ROOT / "deploy" / "oracle_release_install.py",
)
installer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(installer)


def payload(*, records=None, real_capital=False, live_trading=False, immutable=True):
    return {
        "schema_version": "legacy-research-ledger-v1",
        "governance": {
            "REAL_CAPITAL_AUTHORIZED": real_capital,
            "LIVE_TRADING_AUTHORIZED": live_trading,
            "historical_result_immutability": immutable,
        },
        "records": records if records is not None else [{"HYPOTHESIS_ID": "LEGACY-1"}],
    }


def manifest_for(data: bytes, **overrides):
    value = {
        "source_commit": "1" * 40,
        "ledger_path": "LEGACY_RESEARCH_LEDGER.json",
        "ledger_blob_sha": installer.git_blob_sha(data),
        "schema_version": "legacy-research-ledger-v1",
        "reconciliation_status": "PARTIAL_WITH_EXPLICIT_GAPS",
        "historical_research_items_found": 33,
        "governance": {
            "REAL_CAPITAL_AUTHORIZED": False,
            "LIVE_TRADING_AUTHORIZED": False,
            "historical_result_immutability": True,
        },
    }
    value.update(overrides)
    return value


def encoded(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


class OracleReleaseInstallTests(unittest.TestCase):
    def test_deploy_sha_must_be_exact_40_hex(self):
        self.assertEqual(installer.validate_sha("A" * 40), "a" * 40)
        for bad in ("", "abc", "g" * 40, "1" * 39, "1" * 41, "main"):
            with self.subTest(bad=bad), self.assertRaisesRegex(
                installer.InstallBlock, "INVALID_DEPLOY_SHA"
            ):
                installer.validate_sha(bad)

    def test_valid_pinned_legacy_payload_is_accepted_without_equating_census_and_records(self):
        data = encoded(payload(records=[{"HYPOTHESIS_ID": "L1"}, {"HYPOTHESIS_ID": "L2"}]))
        result = installer.verify_legacy_payload(manifest_for(data), data)
        self.assertEqual(result["loaded_record_count"], 2)
        self.assertEqual(result["manifest_historical_research_items_found"], 33)
        self.assertEqual(result["ledger_blob_sha"], installer.git_blob_sha(data))
        self.assertFalse(result["real_capital_authorized"])
        self.assertFalse(result["live_trading_authorized"])

    def test_wrong_blob_fails_closed(self):
        data = encoded(payload())
        manifest = manifest_for(data, ledger_blob_sha="0" * 40)
        with self.assertRaisesRegex(installer.InstallBlock, "LEGACY_LEDGER_BLOB_MISMATCH"):
            installer.verify_legacy_payload(manifest, data)

    def test_empty_ledger_fails_closed(self):
        data = encoded(payload(records=[]))
        with self.assertRaisesRegex(installer.InstallBlock, "LEGACY_LEDGER_EMPTY"):
            installer.verify_legacy_payload(manifest_for(data), data)

    def test_schema_mismatch_fails_closed(self):
        data = encoded(payload())
        manifest = manifest_for(data, schema_version="unexpected")
        with self.assertRaisesRegex(installer.InstallBlock, "LEGACY_LEDGER_SCHEMA_MISMATCH"):
            installer.verify_legacy_payload(manifest, data)

    def test_ledger_cannot_open_real_capital_or_live_trading(self):
        cases = (
            (dict(real_capital=True), "LEGACY_LEDGER_REAL_CAPITAL_AUTHORITY_UNSAFE"),
            (dict(live_trading=True), "LEGACY_LEDGER_LIVE_TRADING_AUTHORITY_UNSAFE"),
        )
        for overrides, code in cases:
            data = encoded(payload(**overrides))
            with self.subTest(code=code), self.assertRaisesRegex(installer.InstallBlock, code):
                installer.verify_legacy_payload(manifest_for(data), data)

    def test_historical_result_immutability_is_mandatory(self):
        data = encoded(payload(immutable=False))
        with self.assertRaisesRegex(
            installer.InstallBlock, "LEGACY_LEDGER_HISTORICAL_IMMUTABILITY_UNSAFE"
        ):
            installer.verify_legacy_payload(manifest_for(data), data)

    def test_manifest_governance_is_independently_enforced(self):
        data = encoded(payload())
        manifest = manifest_for(data)
        manifest["governance"] = dict(manifest["governance"], REAL_CAPITAL_AUTHORIZED=True)
        with self.assertRaisesRegex(
            installer.InstallBlock, "LEGACY_MANIFEST_REAL_CAPITAL_AUTHORITY_UNSAFE"
        ):
            installer.verify_legacy_payload(manifest, data)

    def test_manifest_historical_census_must_be_positive_but_not_record_equal(self):
        data = encoded(payload(records=[{"HYPOTHESIS_ID": "L1"}]))
        for bad in (0, -1, None, "33", True):
            with self.subTest(bad=bad), self.assertRaisesRegex(
                installer.InstallBlock, "LEGACY_MANIFEST_INVALID_HISTORICAL_ITEM_COUNT"
            ):
                installer.verify_legacy_payload(
                    manifest_for(data, historical_research_items_found=bad), data
                )

    def test_git_blob_sha_matches_git_object_encoding(self):
        # `printf test | git hash-object --stdin` = 30d74d258442c7c65512eafab474568dd706c430
        self.assertEqual(
            installer.git_blob_sha(b"test"),
            "30d74d258442c7c65512eafab474568dd706c430",
        )


if __name__ == "__main__":
    unittest.main()

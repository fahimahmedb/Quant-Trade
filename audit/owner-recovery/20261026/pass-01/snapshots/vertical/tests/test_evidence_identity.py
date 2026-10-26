from __future__ import annotations

import dataclasses
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from quant.dataplane.corporate_actions import (
    CorporateActionBook,
    CorporateActionEvent,
    CorporateActionLeg,
)
from quant.dataplane.evidence import (
    DerivedArtifact,
    EvidenceCorruptionError,
    EvidenceStore,
    RawObject,
    SemanticValidationError,
    ValidatedObject,
    ValidationOutcome,
)
from quant.dataplane.identity import (
    IdentityBook,
    IssuerIdentity,
    IssuerNameInterval,
    ListingInterval,
    SecurityIdentity,
    TickerInterval,
)


T0 = "2026-01-02T12:00:00+00:00"
T1 = "2026-01-03T12:00:00+00:00"


def h(char: str) -> str:
    return "sha256:" + char * 64


def issuer(issuer_id: str, char: str = "1") -> IssuerIdentity:
    return IssuerIdentity(
        issuer_id=issuer_id,
        valid_from="2000-01-01",
        valid_to=None,
        identifiers={"synthetic": issuer_id},
        evidence_hashes=(h(char),),
    )


def security(security_id: str, issuer_id: str, char: str) -> SecurityIdentity:
    return SecurityIdentity(
        security_id=security_id,
        issuer_id=issuer_id,
        security_type="COMMON_STOCK",
        valid_from="2000-01-01",
        valid_to=None,
        identifiers={"synthetic": security_id},
        evidence_hashes=(h(char),),
        currency="USD",
    )


class EvidenceStoreTests(unittest.TestCase):
    def test_content_addressed_bytes_and_provenance_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            first = store.put_bytes(
                b"same payload",
                source_uri="https://source.example/one",
                retrieved_at=T0,
                media_type="application/json",
                source_type="public_http",
            )
            second = store.put_bytes(
                b"same payload",
                source_uri="file:///replay/copy",
                retrieved_at=T1,
                media_type="application/json",
                source_type="replay",
            )
            self.assertEqual(first.sha256, second.sha256)
            self.assertNotEqual(first.receipt_id, second.receipt_id)
            self.assertEqual(store.get_bytes(first.sha256), b"same payload")
            self.assertEqual(len(store.receipts(first.sha256)), 2)
            self.assertTrue(store.audit_manifest())
            summary = store.rebuild_manifest()
            self.assertEqual(summary["raw_object"], 1)
            self.assertEqual(summary["raw_receipt"], 2)
            self.assertTrue(store.audit_manifest())

    def test_torn_manifest_tail_is_recovered_and_rebuild_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = EvidenceStore(root)
            store.put_bytes(b"payload", source_uri="synthetic://one", retrieved_at=T0)
            with store.manifest_path.open("ab") as handle:
                handle.write(b'{"kind":"raw_receipt"')
                handle.flush()
                os.fsync(handle.fileno())
            reopened = EvidenceStore(root)
            self.assertTrue(reopened.audit_manifest())
            reopened.manifest_path.unlink()
            summary = reopened.rebuild_manifest()
            first = reopened.manifest_path.read_bytes()
            second_summary = reopened.rebuild_manifest()
            second = reopened.manifest_path.read_bytes()
            self.assertEqual(summary, second_summary)
            self.assertEqual(first, second)

    def test_committed_manifest_corruption_is_not_silently_repaired(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            store.put_bytes(b"payload", source_uri="synthetic://one", retrieved_at=T0)
            with store.manifest_path.open("ab") as handle:
                handle.write(b"{not-json}\n")
                handle.flush()
                os.fsync(handle.fileno())
            reopened = EvidenceStore(Path(directory))
            with self.assertRaises(EvidenceCorruptionError):
                reopened.read_manifest()

    def test_torn_or_mutated_object_bytes_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            raw = store.put_bytes(b"abcdef", source_uri="synthetic://one", retrieved_at=T0)
            path = store.object_path(raw.sha256)
            path.write_bytes(b"abc")
            reopened = EvidenceStore(Path(directory))
            with self.assertRaises(EvidenceCorruptionError):
                reopened.get_bytes(raw.sha256)
            with self.assertRaises(EvidenceCorruptionError):
                reopened.rebuild_manifest()

    def test_validation_assertions_must_replay_from_raw_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            raw = store.put_bytes(
                b'{"issuer":"issuer-A"}', source_uri="synthetic://identity", retrieved_at=T0)

            def validator(payload: bytes) -> ValidationOutcome:
                parsed = json.loads(payload)
                return ValidationOutcome(
                    "VALID", {"issuer_id": parsed["issuer"]}, ())

            recorded = store.validate_object(
                raw.sha256,
                parser_name="synthetic-json",
                parser_version="1",
                validator=validator,
                validated_at=T1,
            )
            verified = store.verified_validation(
                recorded.validation_id,
                parser_name="synthetic-json",
                parser_version="1",
                validator=validator,
            )
            self.assertEqual(verified.identity_assertions, {"issuer_id": "issuer-A"})

            def conflicting(_: bytes) -> ValidationOutcome:
                return ValidationOutcome("VALID", {"issuer_id": "issuer-B"}, ())

            with self.assertRaises(SemanticValidationError):
                store.verified_validation(
                    recorded.validation_id,
                    parser_name="synthetic-json",
                    parser_version="1",
                    validator=conflicting,
                )

    def test_validation_sidecar_tamper_is_detected_by_its_own_content_address(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            raw = store.put_bytes(b"x", source_uri="synthetic://x", retrieved_at=T0)
            record = store.validate_object(
                raw.sha256,
                parser_name="byte-parser",
                parser_version="1",
                validator=lambda value: ValidationOutcome("VALID", {"length": len(value)}, ()),
                validated_at=T1,
            )
            path = store._validation_path(record.raw_sha256, record.validation_id)
            payload = json.loads(path.read_text())
            payload["identity_assertions"] = {"length": 999}
            path.write_text(json.dumps(payload) + "\n")
            with self.assertRaises(EvidenceCorruptionError):
                store.load_validation_record(record.validation_id)

    def test_derived_lineage_is_replayable_from_input_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EvidenceStore(Path(directory))
            left = store.put_bytes(b"left", source_uri="synthetic://left", retrieved_at=T0)
            right = store.put_bytes(b"right", source_uri="synthetic://right", retrieved_at=T0)

            def combine(inputs: tuple[bytes, ...], params: dict[str, object]) -> bytes:
                separator = str(params["separator"]).encode()
                return separator.join(inputs)

            artifact = store.derive(
                (left.sha256, right.sha256),
                transform_name="combine",
                transform_version="1",
                transform=combine,
                parameters={"separator": "|"},
                created_at=T1,
                output_media_type="text/plain",
            )
            self.assertEqual(store.get_bytes(artifact.output_sha256), b"left|right")
            self.assertEqual(artifact.input_sha256s, (left.sha256, right.sha256))
            self.assertEqual(
                store.verified_derived(
                    artifact.artifact_id,
                    transform_name="combine",
                    transform_version="1",
                    transform=combine,
                ),
                artifact,
            )
            with self.assertRaises(SemanticValidationError):
                store.verified_derived(
                    artifact.artifact_id,
                    transform_name="combine",
                    transform_version="1",
                    transform=lambda inputs, params: b"different",
                )
            self.assertTrue(store.audit_manifest())

    def test_real_process_kill_after_object_commit_recovers_from_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src_root = Path(__file__).resolve().parents[1] / "src"
            code = r'''
import os
import sys
from pathlib import Path
from quant.dataplane.evidence import EvidenceStore

def die(stage, context):
    if stage == "after_object_commit":
        os._exit(73)

store = EvidenceStore(Path(sys.argv[1]), fault_hook=die)
store.put_bytes(b"kill-boundary", source_uri="synthetic://kill", retrieved_at="2026-01-02T12:00:00+00:00")
'''
            env = dict(os.environ)
            env["PYTHONPATH"] = str(src_root) + os.pathsep + env.get("PYTHONPATH", "")
            killed = subprocess.run(
                [sys.executable, "-c", code, str(root)],
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(killed.returncode, 73, killed.stderr)
            recovered = EvidenceStore(root)
            summary = recovered.rebuild_manifest()
            self.assertEqual(summary, {"raw_object": 1})
            receipt = recovered.put_bytes(
                b"kill-boundary",
                source_uri="synthetic://kill",
                retrieved_at=T0,
            )
            self.assertEqual(recovered.get_bytes(receipt.sha256), b"kill-boundary")
            self.assertEqual(len(recovered.receipts(receipt.sha256)), 1)
            self.assertTrue(recovered.audit_manifest())


class IdentityContractTests(unittest.TestCase):
    def test_ticker_reuse_resolves_by_point_in_time_not_ticker_text(self) -> None:
        issuers = (issuer("oldco", "1"), issuer("newco", "2"))
        securities = (security("sec-old", "oldco", "3"), security("sec-new", "newco", "4"))
        book = IdentityBook(
            issuers=issuers,
            securities=securities,
            tickers=(
                TickerInterval("sec-old", "ABC", "2020-01-01", "2022-01-01", (h("5"),), "XNYS"),
                TickerInterval("sec-new", "ABC", "2022-01-01", None, (h("6"),), "XNYS"),
            ),
            listings=(
                ListingInterval("sec-old", "XNYS", "2020-01-01", "2022-01-01", (h("7"),)),
                ListingInterval("sec-new", "XNYS", "2022-01-01", None, (h("8"),)),
            ),
        )
        old = book.resolve_ticker("ABC", as_of="2021-06-01", venue="XNYS")
        new = book.resolve_ticker("ABC", as_of="2023-06-01", venue="XNYS")
        self.assertEqual(old.status, "RESOLVED")
        self.assertEqual(old.security_id, "sec-old")
        self.assertEqual(new.security_id, "sec-new")
        self.assertIn(h("5"), old.lineage_hashes)
        self.assertIn(h("6"), new.lineage_hashes)

    def test_name_change_is_an_interval_not_a_retroactive_overwrite(self) -> None:
        book = IdentityBook(
            issuers=(issuer("issuer-A"),),
            securities=(security("sec-A", "issuer-A", "2"),),
            names=(
                IssuerNameInterval("issuer-A", "Old Name", "2020-01-01", "2022-05-01", (h("3"),)),
                IssuerNameInterval("issuer-A", "New Name", "2022-05-01", None, (h("4"),)),
            ),
        )
        self.assertEqual(book.resolve_name("issuer-A", "2022-04-30").name, "Old Name")
        self.assertEqual(book.resolve_name("issuer-A", "2022-05-01").name, "New Name")

    def test_ambiguous_mapping_is_returned_as_ambiguous_not_guessed(self) -> None:
        book = IdentityBook(
            issuers=(issuer("issuer-A", "1"), issuer("issuer-B", "2")),
            securities=(security("sec-A", "issuer-A", "3"), security("sec-B", "issuer-B", "4")),
            tickers=(
                TickerInterval("sec-A", "DUP", "2024-01-01", None, (h("5"),), "XNAS"),
                TickerInterval("sec-B", "DUP", "2024-01-01", None, (h("6"),), "XNAS"),
            ),
            listings=(
                ListingInterval("sec-A", "XNAS", "2024-01-01", None, (h("7"),)),
                ListingInterval("sec-B", "XNAS", "2024-01-01", None, (h("8"),)),
            ),
        )
        result = book.resolve_ticker("DUP", as_of="2025-01-01", venue="XNAS")
        self.assertEqual(result.status, "AMBIGUOUS")
        self.assertEqual(result.candidate_security_ids, ("sec-A", "sec-B"))
        self.assertIsNone(result.security_id)

    def test_venue_is_part_of_resolution_context(self) -> None:
        book = IdentityBook(
            issuers=(issuer("issuer-A", "1"), issuer("issuer-B", "2")),
            securities=(security("sec-A", "issuer-A", "3"), security("sec-B", "issuer-B", "4")),
            tickers=(
                TickerInterval("sec-A", "VEN", "2024-01-01", None, (h("5"),), "XNYS"),
                TickerInterval("sec-B", "VEN", "2024-01-01", None, (h("6"),), "XNAS"),
            ),
            listings=(
                ListingInterval("sec-A", "XNYS", "2024-01-01", None, (h("7"),)),
                ListingInterval("sec-B", "XNAS", "2024-01-01", None, (h("8"),)),
            ),
        )
        self.assertEqual(
            book.resolve_ticker("VEN", as_of="2025-01-01", venue="XNYS").security_id,
            "sec-A",
        )
        self.assertEqual(
            book.resolve_ticker("VEN", as_of="2025-01-01", venue="XNAS").security_id,
            "sec-B",
        )
        self.assertEqual(book.resolve_ticker("VEN", as_of="2025-01-01").status, "AMBIGUOUS")


class CorporateActionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.identities = IdentityBook(
            issuers=(issuer("issuer-S", "1"), issuer("issuer-T", "2"), issuer("issuer-P", "3")),
            securities=(
                security("sec-S", "issuer-S", "4"),
                security("sec-T", "issuer-T", "5"),
                security("sec-P", "issuer-P", "6"),
            ),
            tickers=(TickerInterval("sec-S", "SRC", "2020-01-01", None, (h("7"),), "XNYS"),),
            listings=(ListingInterval("sec-S", "XNYS", "2020-01-01", None, (h("8"),)),),
        )

    def test_synthetic_contracts_cover_merger_cash_stock_mix_split_spin_delist_and_name(self) -> None:
        events = (
            CorporateActionEvent(
                "name", "NAME_CHANGE", "2024-01-01", "2024-02-01", (h("a"),),
                issuer_id="issuer-S", new_name="Issuer S Renamed"),
            CorporateActionEvent(
                "cash", "MERGER", "2024-01-02", "2024-03-01", (h("b"),),
                source_security_id="sec-S",
                legs=(CorporateActionLeg("CASH", cash_per_source_share=12.5, currency="USD"),)),
            CorporateActionEvent(
                "stock", "MERGER", "2024-01-03", "2024-03-02", (h("c"),),
                source_security_id="sec-S",
                legs=(CorporateActionLeg("STOCK", target_security_id="sec-T", units_per_source_share=0.5),)),
            CorporateActionEvent(
                "mix", "MERGER", "2024-01-04", "2024-03-03", (h("d"),),
                source_security_id="sec-S",
                legs=(
                    CorporateActionLeg("CASH", cash_per_source_share=4.0, currency="USD"),
                    CorporateActionLeg("STOCK", target_security_id="sec-T", units_per_source_share=0.25),
                )),
            CorporateActionEvent(
                "split", "SPLIT", "2024-01-05", "2024-03-04", (h("e"),),
                source_security_id="sec-S", split_ratio=2.0),
            CorporateActionEvent(
                "spin", "SPIN_OFF", "2024-01-06", "2024-03-05", (h("f"),),
                source_security_id="sec-S",
                legs=(CorporateActionLeg("SPIN", target_security_id="sec-P", units_per_source_share=0.2),)),
            CorporateActionEvent(
                "delist", "DELISTING", "2024-01-07", "2024-03-06", (h("9"),),
                source_security_id="sec-S", delisting_reason="synthetic acquisition"),
        )
        book = CorporateActionBook(events)
        book.validate_identity_links(self.identities)
        self.assertEqual({event.action_type for event in book.events},
                         {"NAME_CHANGE", "MERGER", "SPLIT", "SPIN_OFF", "DELISTING"})
        merger_shapes = [tuple(leg.kind for leg in event.legs)
                         for event in book.events if event.action_type == "MERGER"]
        self.assertIn(("CASH",), merger_shapes)
        self.assertIn(("STOCK",), merger_shapes)
        self.assertIn(("CASH", "STOCK"), merger_shapes)
        self.assertNotIn("ticker", {field.name for field in dataclasses.fields(CorporateActionEvent)})

    def test_pit_query_never_knows_late_reported_event_early(self) -> None:
        late = CorporateActionEvent(
            "late-delist",
            "DELISTING",
            knowledge_at="2024-05-02T12:00:00+00:00",
            effective_at="2024-05-01T09:30:00+00:00",
            evidence_hashes=(h("a"),),
            source_security_id="sec-S",
        )
        book = CorporateActionBook((late,))
        self.assertEqual(book.known_as_of("2024-05-01T16:00:00+00:00"), ())
        self.assertEqual(book.effective_as_of("2024-05-01T16:00:00+00:00"), ())
        self.assertEqual(book.effective_as_of("2024-05-03T16:00:00+00:00"), (late,))

    def test_unknown_stable_identity_is_rejected_instead_of_ticker_guessing(self) -> None:
        event = CorporateActionEvent(
            "bad", "DELISTING", "2024-01-01", "2024-02-01", (h("a"),),
            source_security_id="sec-DOES-NOT-EXIST")
        with self.assertRaises(ValueError):
            CorporateActionBook((event,)).validate_identity_links(self.identities)


class SchemaSurfaceTests(unittest.TestCase):
    def test_builder_c_schemas_are_parseable_and_closed(self) -> None:
        root = Path(__file__).resolve().parents[1]
        expected = {
            "raw_object.schema.json": RawObject,
            "validated_object.schema.json": ValidatedObject,
            "derived_artifact.schema.json": DerivedArtifact,
            "issuer_identity.schema.json": IssuerIdentity,
            "issuer_name_interval.schema.json": IssuerNameInterval,
            "security_identity.schema.json": SecurityIdentity,
            "ticker_interval.schema.json": TickerInterval,
            "listing_interval.schema.json": ListingInterval,
            "corporate_action_leg.schema.json": CorporateActionLeg,
            "corporate_action_event.schema.json": CorporateActionEvent,
        }
        for name, contract in expected.items():
            path = root / "schemas" / name
            self.assertTrue(path.exists(), name)
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertEqual(schema["type"], "object")
            self.assertFalse(schema["additionalProperties"])
            self.assertEqual(set(schema["properties"]),
                             {field.name for field in dataclasses.fields(contract)})


if __name__ == "__main__":
    unittest.main()

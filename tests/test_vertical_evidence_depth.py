"""Evidence storage adversaries use synthetic bytes in disposable directories."""

from concurrent.futures import ThreadPoolExecutor
import os
import threading
from unittest.mock import patch

import pytest

from quant.dataplane import evidence
from quant.dataplane.evidence import EvidenceStore, ValidationOutcome


T0 = "2026-10-20T00:00:00Z"


def test_two_atomic_writers_do_not_share_a_staging_file(tmp_path):
    destination = tmp_path / "object"
    gate = threading.Barrier(2)
    original = os.replace

    def together(source, target):
        gate.wait(timeout=5)
        original(source, target)

    with patch.object(evidence.os, "replace", side_effect=together):
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(evidence._atomic_write, destination, b"fixture") for _ in range(2)]
            for future in futures:
                future.result(timeout=10)
    assert destination.read_bytes() == b"fixture"


def test_identical_concurrent_ingestion_has_one_receipt_and_index_entry(tmp_path):
    stores = [EvidenceStore(tmp_path) for _ in range(8)]
    gate = threading.Barrier(len(stores))

    def ingest(store):
        gate.wait(timeout=5)
        return store.put_bytes(b"fixture", source_uri="synthetic://one", retrieved_at=T0)

    with ThreadPoolExecutor(max_workers=len(stores)) as pool:
        records = list(pool.map(ingest, stores))
    assert len({r.receipt_id for r in records}) == 1
    assert len(stores[0].read_manifest()) == 2
    assert stores[0].audit_manifest()
    assert stores[0].rebuild_manifest() == {"raw_object": 1, "raw_receipt": 1}
    assert stores[0].audit_manifest()


def test_index_check_and_append_are_one_exclusive_operation(tmp_path):
    store = EvidenceStore(tmp_path)
    entered, release, second_checked = threading.Event(), threading.Event(), threading.Event()
    original_append = evidence._append_jsonl
    original_read = evidence._read_jsonl_strict

    def delayed_append(path, record):
        entered.set()
        assert release.wait(timeout=5)
        return original_append(path, record)

    def observed_read(path):
        if threading.current_thread().name == "second-index-writer":
            second_checked.set()
        return original_read(path)

    record = {"kind": "raw_object", "sha256": "fixture", "size_bytes": 0}
    with patch.object(evidence, "_append_jsonl", side_effect=delayed_append), \
            patch.object(evidence, "_read_jsonl_strict", side_effect=observed_read):
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(store._append_manifest_once, record, "sha256")
            assert entered.wait(timeout=5)

            def second():
                threading.current_thread().name = "second-index-writer"
                store._append_manifest_once(record, "sha256")

            other = pool.submit(second)
            try:
                # While first publication is paused, second must not inspect an
                # empty manifest and decide to publish the same identity again.
                assert not second_checked.wait(timeout=0.15)
            finally:
                release.set()
            first.result(timeout=5)
            other.result(timeout=5)
    assert store.read_manifest() == [record]


@pytest.mark.parametrize("reference", ["validation:*", "*", "validation:?", "validation:[a-f]*",
                                        "wrong:{digest}", "{digest}"])
def test_validation_lookup_requires_exact_typed_identity(tmp_path, reference):
    store = EvidenceStore(tmp_path)
    raw = store.put_bytes(b"fixture", source_uri="synthetic://one", retrieved_at=T0)
    valid = store.validate_object(raw.sha256, parser_name="fixture", parser_version="1",
                                  validator=lambda _: ValidationOutcome("VALID"), validated_at=T0)
    reference = reference.format(digest=valid.validation_id.split(":")[1])
    with pytest.raises(ValueError):
        store.load_validation_record(reference)
    assert store.load_validation_record(valid.validation_id) == valid


@pytest.mark.parametrize("prefix", ["", "wrong:", "artifact:../derived/"])
def test_derived_lookup_rejects_partial_foreign_and_traversal_reference(tmp_path, prefix):
    store = EvidenceStore(tmp_path)
    raw = store.put_bytes(b"fixture", source_uri="synthetic://one", retrieved_at=T0)
    derived = store.derive([raw.sha256], transform_name="fixture", transform_version="1",
                           transform=lambda values, _: values[0], created_at=T0)
    with pytest.raises(ValueError):
        store.load_derived_record(prefix + derived.artifact_id.split(":")[1])
    assert store.load_derived_record(derived.artifact_id) == derived


def test_nonfinite_assertions_cannot_become_durable_identity(tmp_path):
    store = EvidenceStore(tmp_path)
    raw = store.put_bytes(b"fixture", source_uri="synthetic://one", retrieved_at=T0)
    before = store.read_manifest()
    with pytest.raises(ValueError):
        store.validate_object(raw.sha256, parser_name="fixture", parser_version="1",
                              validator=lambda _: ValidationOutcome("VALID", {"value": float("nan")}),
                              validated_at=T0)
    assert store.read_manifest() == before
    assert not list(store.validated_root.glob("*/*.json"))


def test_rebuild_during_receipt_ack_gap_does_not_duplicate_the_index(tmp_path):
    persisted, resume = threading.Event(), threading.Event()

    def fault(stage, _):
        if stage == "after_receipt_commit":
            persisted.set()
            assert resume.wait(timeout=5)

    writer = EvidenceStore(tmp_path, fault_hook=fault)
    recovery = EvidenceStore(tmp_path)
    with ThreadPoolExecutor(max_workers=1) as pool:
        work = pool.submit(writer.put_bytes, b"fixture", source_uri="synthetic://one", retrieved_at=T0)
        try:
            assert persisted.wait(timeout=5)
            assert recovery.rebuild_manifest() == {"raw_object": 1, "raw_receipt": 1}
        finally:
            resume.set()
        receipt = work.result(timeout=5)
    assert len(recovery.receipts(receipt.sha256)) == 1
    assert recovery.audit_manifest()
    assert len(recovery.read_manifest()) == 2

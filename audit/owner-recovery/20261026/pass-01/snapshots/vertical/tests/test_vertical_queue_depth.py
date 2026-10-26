"""Existing local queue clocks, reconstruction and failed-write replay."""

from concurrent.futures import ThreadPoolExecutor
import os
import threading
from unittest.mock import patch

import pytest

from autonomous_research.runtime import PersistentQueue, ResearchTask, _write_json
from quant.state import write_json


def task(identity, **changes):
    args = dict(task_id=identity, lane="fixture", priority=1, reason="synthetic",
                worker="fixture", created_at="2026-10-20T00:00:00Z")
    args.update(changes)
    return ResearchTask(**args)


@pytest.mark.parametrize("due,eligible", [
    ("2026-10-20T13:00:00+02:00", True),
    ("2026-10-20T11:00:00-02:00", False),
    ("2026-10-20T14:00:00+02:00", True),
])
def test_queue_due_boundary_compares_instants_not_iso_spelling(tmp_path, due, eligible):
    queue = PersistentQueue(tmp_path / "queue.json")
    queue.add(task("one", due_at=due))
    assert (queue.next_due("2026-10-20T12:00:00Z") is not None) is eligible


@pytest.mark.parametrize("instant", ["2026-10-20T12:00:00", "UNKNOWN", "", "2026-99-20T00:00:00Z"])
def test_naive_or_malformed_due_clock_is_not_scheduled(tmp_path, instant):
    queue = PersistentQueue(tmp_path / "queue.json")
    queue.add(task("one", due_at=instant))
    with pytest.raises(ValueError):
        queue.next_due("2026-10-20T12:00:00Z")


def test_failed_add_can_be_retried_on_same_queue(tmp_path):
    path = tmp_path / "queue.json"
    queue = PersistentQueue(path)
    with patch("autonomous_research.runtime._write_json", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            queue.add(task("one"))
    assert queue.add(task("one"))
    assert "one" in PersistentQueue(path).tasks


def test_publication_ack_loss_does_not_duplicate_task(tmp_path):
    path = tmp_path / "queue.json"
    queue = PersistentQueue(path)

    def lost_ack(path, value):
        write_json(path, value)
        raise OSError("ack lost")

    with patch("autonomous_research.runtime._write_json", side_effect=lost_ack):
        with pytest.raises(OSError):
            queue.add(task("one"))
    assert not queue.add(task("one"))
    assert len(PersistentQueue(path).tasks) == 1


def test_atomic_campaign_writers_use_unique_staging_files(tmp_path):
    gate = threading.Barrier(2)
    original = os.replace

    def together(source, target):
        gate.wait(timeout=5)
        return original(source, target)

    with patch("os.replace", side_effect=together):
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(_write_json, tmp_path / "state.json", {"fixture": True})
                       for _ in range(2)]
            for future in futures:
                future.result(timeout=5)


@pytest.mark.parametrize("version", [0, 2, True, "1"])
def test_unknown_queue_schema_cannot_be_silently_rewritten(tmp_path, version):
    path = tmp_path / "queue.json"
    write_json(path, {"version": version, "tasks": []})
    before = path.read_bytes()
    with pytest.raises(ValueError):
        PersistentQueue(path)
    assert path.read_bytes() == before


def test_conflicting_duplicate_task_records_are_ambiguous(tmp_path):
    from dataclasses import asdict
    path = tmp_path / "queue.json"
    write_json(path, {"version": 1, "tasks": [asdict(task("one")),
                                              asdict(task("one", status="COMPLETED"))]})
    with pytest.raises(ValueError):
        PersistentQueue(path)

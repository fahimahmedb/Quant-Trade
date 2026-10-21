"""Learning mutation isolation across stale instances, threads and processes."""

from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import threading
from unittest.mock import patch

import pytest

from quant.learning.store import BuildTask, LearningStore
from quant.state import write_json
from tests.test_vertical_learning_depth import result


def record(store, identity):
    return store.record_research("fixture", "FIXTURE", result(identity))


@pytest.mark.parametrize("same_identity", [False, True])
def test_stale_learning_instance_cannot_erase_acknowledged_ticket(tmp_path, same_identity):
    path = tmp_path / "learning.json"
    first, stale = LearningStore(path), LearningStore(path)
    assert record(first, "first")
    identity = "first" if same_identity else "second"
    with pytest.raises(RuntimeError):
        record(stale, identity)
    assert record(stale, identity) is (not same_identity)
    final = LearningStore(path)
    assert final.processed_research_tickets == ({"first"} if same_identity else {"first", "second"})
    assert final.lane_priorities["fixture"] == (24 if same_identity else 18)


def test_stale_build_task_cannot_erase_a_research_lesson(tmp_path):
    path = tmp_path / "learning.json"
    first, stale = LearningStore(path), LearningStore(path)
    record(first, "first")
    task = BuildTask("build", "fixture", "synthetic", ["BUILD"], "fixture", 1)
    with pytest.raises(RuntimeError):
        stale.raise_build_task(task)
    stale.raise_build_task(task)
    final = LearningStore(path)
    assert final.processed_research_tickets == {"first"}
    assert len(final.open_build_tasks()) == 1
    assert final.lane_priorities["fixture"] == 24


@pytest.mark.parametrize("fault", ["none", "before_write", "after_write"])
def test_shared_instance_isolates_mutation_through_publication_and_recovery(tmp_path, fault):
    path = tmp_path / "learning.json"
    store = LearningStore(path)
    entered, release, second_started, second_done = (threading.Event() for _ in range(4))

    def publication(path, document):
        if threading.current_thread().name == "first-learner":
            entered.set()
            assert release.wait(timeout=5)
            if fault == "before_write":
                raise OSError("first publication failed")
            write_json(path, document)
            if fault == "after_write":
                raise OSError("first acknowledgement lost")
        else:
            write_json(path, document)

    def first():
        threading.current_thread().name = "first-learner"
        try:
            return record(store, "first")
        except OSError:
            return "failed"

    def second():
        second_started.set()
        try:
            return record(store, "second")
        finally:
            second_done.set()

    with patch("quant.learning.store.write_json", side_effect=publication):
        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(first)
            assert entered.wait(timeout=5)
            b = pool.submit(second)
            try:
                assert second_started.wait(timeout=5)
                assert not second_done.wait(timeout=0.15)
            finally:
                release.set()
            assert a.result(timeout=5) == (True if fault == "none" else "failed")
            assert b.result(timeout=5) is True
    final = LearningStore(path)
    expected = {"second"} if fault == "before_write" else {"first", "second"}
    assert final.processed_research_tickets == expected
    assert {item["ticket_id"] for item in final.lessons} == expected
    assert final.lane_priorities["fixture"] == (24 if fault == "before_write" else 18)
    assert record(store, "first") is (fault == "before_write")
    assert LearningStore(path).lane_priorities["fixture"] == 18


def test_independent_processes_with_one_observed_snapshot_cannot_both_publish(tmp_path):
    path = tmp_path / "learning.json"
    code = """
import sys
from pathlib import Path
from quant.learning.store import LearningStore
store = LearningStore(Path(sys.argv[1]))
print('READY', flush=True)
sys.stdin.readline()
try:
    store.record_research('fixture', 'FIXTURE', {'ticket_id': sys.argv[2],
                          'lesson': 'synthetic negative', 'outcome': 'REJECTED'})
except RuntimeError:
    print('CONFLICT')
else:
    print('WRITTEN')
"""
    workers = [subprocess.Popen([sys.executable, "-c", code, str(path), str(index)],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True) for index in range(2)]
    try:
        for worker in workers:
            assert worker.stdout.readline().strip() == "READY"
        outcomes = []
        for worker in workers:
            stdout, stderr = worker.communicate("go\n", timeout=10)
            assert worker.returncode == 0, stderr
            outcomes.append(stdout.strip())
        assert sorted(outcomes) == ["CONFLICT", "WRITTEN"]
        assert len(LearningStore(path).processed_research_tickets) == 1
        assert LearningStore(path).lane_priorities["fixture"] == 24
    finally:
        for worker in workers:
            if worker.poll() is None:
                worker.kill()
                worker.communicate(timeout=5)


@pytest.mark.parametrize("target", ["quant.learning.store.os.open",
                                    "quant.learning.store.fcntl.flock", "pathlib.Path.mkdir"])
def test_lock_setup_failure_restores_prior_learning_before_retry(tmp_path, target):
    path = tmp_path / "learning.json"
    store = LearningStore(path)
    record(store, "seed")
    before = path.read_bytes()
    with patch(target, side_effect=OSError("lock setup failed")):
        with pytest.raises(OSError):
            record(store, "retry")
    assert path.read_bytes() == before
    assert store.processed_research_tickets == {"seed"}
    assert store.lane_priorities["fixture"] == 24
    assert record(store, "retry")
    assert LearningStore(path).lane_priorities["fixture"] == 18


@pytest.mark.parametrize("after_replace", [False, True])
def test_process_death_releases_lock_and_replays_one_learning_delta(tmp_path, after_replace):
    path = tmp_path / "learning.json"
    LearningStore(path).save()
    code = """
import os, sys
from pathlib import Path
from unittest.mock import patch
from quant.learning.store import LearningStore
store = LearningStore(Path(sys.argv[1]))
replace = os.replace
def die(source, destination):
    if sys.argv[2] == 'True':
        replace(source, destination)
    os._exit(73)
with patch('quant.state.os.replace', side_effect=die):
    store.record_research('fixture', 'FIXTURE', {'ticket_id': 'first',
                          'lesson': 'synthetic negative', 'outcome': 'REJECTED'})
"""
    outcome = subprocess.run([sys.executable, "-c", code, str(path), str(after_replace)], timeout=10)
    assert outcome.returncode == 73
    store = LearningStore(path)
    assert record(store, "first") is (not after_replace)
    assert LearningStore(path).processed_research_tickets == {"first"}
    assert LearningStore(path).lane_priorities["fixture"] == 24

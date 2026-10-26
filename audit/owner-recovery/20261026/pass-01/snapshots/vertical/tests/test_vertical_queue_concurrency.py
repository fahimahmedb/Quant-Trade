"""Local queue publication cannot erase acknowledged identities or completion."""

from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import threading
from unittest.mock import patch

import pytest

from autonomous_research.runtime import PersistentQueue
from quant.state import write_json
from tests.test_vertical_queue_depth import task


@pytest.mark.parametrize("same_identity", [False, True])
def test_stale_queue_add_cannot_erase_an_acknowledged_task(tmp_path, same_identity):
    path = tmp_path / "queue.json"
    first, stale = PersistentQueue(path), PersistentQueue(path)
    assert first.add(task("first"))
    identity = "first" if same_identity else "second"
    with pytest.raises(RuntimeError):
        stale.add(task(identity))
    assert stale.add(task(identity)) is (not same_identity)
    assert set(PersistentQueue(path).tasks) == ({"first"} if same_identity else {"first", "second"})


def test_stale_save_cannot_restore_pending_over_acknowledged_completion(tmp_path):
    path = tmp_path / "queue.json"
    first = PersistentQueue(path)
    first.add(task("one"))
    stale = PersistentQueue(path)
    first.tasks["one"].status = "COMPLETED"
    first.save()
    stale.tasks["one"].attempts += 1
    with pytest.raises(RuntimeError):
        stale.save()
    assert stale.tasks["one"].status == "COMPLETED"
    stale.save()
    assert PersistentQueue(path).tasks["one"].status == "COMPLETED"


@pytest.mark.parametrize("fault", ["none", "before_write", "after_write"])
def test_shared_queue_isolates_add_until_publication_or_recovery_finishes(tmp_path, fault):
    path = tmp_path / "queue.json"
    queue = PersistentQueue(path)
    entered, release, second_started, second_done = (threading.Event() for _ in range(4))

    def publication(path, document):
        if threading.current_thread().name == "first-queue-writer":
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
        threading.current_thread().name = "first-queue-writer"
        try:
            return queue.add(task("first"))
        except OSError:
            return "failed"

    def second():
        second_started.set()
        try:
            return queue.add(task("second"))
        finally:
            second_done.set()

    with patch("autonomous_research.runtime._write_json", side_effect=publication):
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
    expected = {"second"} if fault == "before_write" else {"first", "second"}
    assert set(PersistentQueue(path).tasks) == expected
    assert set(queue.tasks) == expected
    assert queue.add(task("first")) is (fault == "before_write")
    assert set(PersistentQueue(path).tasks) == {"first", "second"}


def test_document_preparation_failure_does_not_poison_add_retry(tmp_path):
    path = tmp_path / "queue.json"
    queue = PersistentQueue(path)
    queue.add(task("seed"))
    before = path.read_bytes()
    with pytest.raises((TypeError, ValueError)):
        queue.add(task("retry", created_at=None))
    assert path.read_bytes() == before
    assert set(queue.tasks) == {"seed"}
    assert queue.add(task("retry"))
    assert set(PersistentQueue(path).tasks) == {"seed", "retry"}


@pytest.mark.parametrize("target", ["os.open", "fcntl.flock", "pathlib.Path.mkdir"])
def test_lock_setup_failure_does_not_poison_add_retry(tmp_path, target):
    path = tmp_path / "queue.json"
    queue = PersistentQueue(path)
    queue.add(task("seed"))
    before = path.read_bytes()
    with patch(target, side_effect=OSError("lock setup failed")):
        with pytest.raises(OSError):
            queue.add(task("retry"))
    assert path.read_bytes() == before
    assert set(queue.tasks) == {"seed"}
    assert queue.add(task("retry"))


def test_independent_processes_cannot_both_publish_a_stale_queue(tmp_path):
    path = tmp_path / "queue.json"
    code = """
import sys
from pathlib import Path
from autonomous_research.runtime import PersistentQueue, ResearchTask
queue = PersistentQueue(Path(sys.argv[1]))
print('READY', flush=True)
sys.stdin.readline()
try:
    queue.add(ResearchTask(sys.argv[2], 'fixture', 1, 'synthetic', 'fixture'))
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
        assert len(PersistentQueue(path).tasks) == 1
    finally:
        for worker in workers:
            if worker.poll() is None:
                worker.kill()
                worker.communicate(timeout=5)


@pytest.mark.parametrize("after_replace", [False, True])
def test_process_death_releases_lock_and_preserves_one_queue_identity(tmp_path, after_replace):
    path = tmp_path / "queue.json"
    PersistentQueue(path).save()
    code = """
import os, sys
from pathlib import Path
from unittest.mock import patch
from autonomous_research.runtime import PersistentQueue, ResearchTask
queue = PersistentQueue(Path(sys.argv[1]))
replace = os.replace
def die(source, destination):
    if sys.argv[2] == 'True':
        replace(source, destination)
    os._exit(73)
with patch('quant.state.os.replace', side_effect=die):
    queue.add(ResearchTask('first', 'fixture', 1, 'synthetic', 'fixture'))
"""
    outcome = subprocess.run([sys.executable, "-c", code, str(path), str(after_replace)], timeout=10)
    assert outcome.returncode == 73
    queue = PersistentQueue(path)
    assert queue.add(task("first")) is (not after_replace)
    assert set(PersistentQueue(path).tasks) == {"first"}

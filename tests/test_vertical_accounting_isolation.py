"""Shared accounting instances must not lose an acknowledged second mutation."""

from concurrent.futures import ThreadPoolExecutor
import threading
from unittest.mock import patch

import pytest

from quant.book.ledger import Ledger
from quant.desk.journal import DeskJournal
from quant.state import write_json
from tests.test_vertical_book_depth import fill


def create(kind, path):
    if kind == "book":
        return Ledger(path, authority="EVALUATION", initial_capital=100)
    value = DeskJournal(path)
    value.save()
    return value


def mutate(kind, value, identity):
    if kind == "book":
        return fill(value, operation=identity)
    return value.commit(identity, "fixture", "NO_TRADE", "2026-10-20", False)


def seen(kind, value, identity):
    return value.has_applied(identity) if kind == "book" else value.is_processed(identity)


@pytest.mark.parametrize("kind", ["book", "journal"])
@pytest.mark.parametrize("fault", ["none", "before_write", "after_write"])
def test_failed_shared_mutation_cannot_erase_a_successful_competitor(tmp_path, kind, fault):
    path = tmp_path / "state.json"
    value = create(kind, path)
    entered, release, second_started, second_done = (threading.Event() for _ in range(4))
    target = "quant.book.ledger.write_json" if kind == "book" else "quant.desk.journal.write_json"

    def publication(path, document):
        if threading.current_thread().name == "first-accounting-writer":
            entered.set()
            assert release.wait(timeout=5)
            if fault == "before_write":
                raise OSError("first write failed")
            write_json(path, document)
            if fault == "after_write":
                raise OSError("first ACK lost")
        else:
            write_json(path, document)

    def first():
        threading.current_thread().name = "first-accounting-writer"
        try:
            mutate(kind, value, "first")
            return "written"
        except OSError:
            return "failed"

    def second():
        second_started.set()
        try:
            mutate(kind, value, "second")
            return "written"
        finally:
            second_done.set()

    with patch(target, side_effect=publication):
        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(first)
            assert entered.wait(timeout=5)
            b = pool.submit(second)
            try:
                assert second_started.wait(timeout=5)
                assert not second_done.wait(timeout=0.15)
            finally:
                release.set()
            assert a.result(timeout=5) == ("written" if fault == "none" else "failed")
            assert b.result(timeout=5) == "written"
    restored = create(kind, path)
    assert seen(kind, restored, "second")
    assert seen(kind, restored, "first") is (fault != "before_write")
    count = 1 if fault == "before_write" else 2
    if kind == "book":
        assert restored.state.fills == count
        assert restored.state.cash == 100 - 21 * count
    else:
        assert restored.stats_for("fixture")["sessions"] == count


@pytest.mark.parametrize("kind", ["book", "journal"])
@pytest.mark.parametrize("target", ["os.open", "fcntl.flock", "pathlib.Path.mkdir"])
def test_accounting_lock_setup_failure_restores_mutation_before_retry(tmp_path, kind, target):
    path = tmp_path / "state.json"
    value = create(kind, path)
    before = path.read_bytes()
    with patch(target, side_effect=OSError("lock setup failed")):
        with pytest.raises(OSError):
            mutate(kind, value, "retry")
    assert path.read_bytes() == before
    assert not seen(kind, value, "retry")
    mutate(kind, value, "retry")
    assert seen(kind, create(kind, path), "retry")


@pytest.mark.parametrize("kind", ["book", "journal"])
@pytest.mark.parametrize("failure", [False, True])
def test_identity_query_waits_until_mutation_is_durable_or_rolled_back(tmp_path, kind, failure):
    path = tmp_path / "state.json"
    value = create(kind, path)
    entered, release, reader_started, reader_done = (threading.Event() for _ in range(4))
    target = "quant.book.ledger.write_json" if kind == "book" else "quant.desk.journal.write_json"

    def publication(path, document):
        entered.set()
        assert release.wait(timeout=5)
        if failure:
            raise OSError("write failed")
        write_json(path, document)

    def write():
        try:
            mutate(kind, value, "one")
        except OSError:
            return "failed"
        return "written"

    def read():
        reader_started.set()
        try:
            return seen(kind, value, "one")
        finally:
            reader_done.set()

    with patch(target, side_effect=publication):
        with ThreadPoolExecutor(max_workers=2) as pool:
            writer = pool.submit(write)
            assert entered.wait(timeout=5)
            reader = pool.submit(read)
            try:
                assert reader_started.wait(timeout=5)
                assert not reader_done.wait(timeout=0.15)
            finally:
                release.set()
            assert writer.result(timeout=5) == ("failed" if failure else "written")
            assert reader.result(timeout=5) is (not failure)

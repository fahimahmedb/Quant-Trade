"""Disposable accounting stress; no market evidence or capital authority."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import threading
import os
import subprocess
import sys
from unittest.mock import patch

import pytest

from quant.book.ledger import Ledger
from quant.state import read_json, write_json


def fill(book, operation="one", **changes):
    args = dict(symbol="SYNTH", quantity=2.0, price=10.0, cost=1.0,
                date="2026-10-20", strategy_id="fixture", operation_id=operation)
    args.update(changes)
    return book.apply_fill(**args)


def test_failed_persist_does_not_turn_retry_into_false_success(tmp_path):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)
    with patch("quant.book.ledger.write_json", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            fill(book)
    assert not book.has_applied("one")
    assert book.state.cash == 100
    assert not fill(book)["replayed"]
    assert Ledger(path).state.cash == 79
    assert Ledger(path).state.fills == 1


def test_lost_ack_after_replace_recovers_on_same_object(tmp_path):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)

    def persisted_then_failed(path, value):
        write_json(path, value)
        raise OSError("directory fsync acknowledgement lost")

    with patch("quant.book.ledger.write_json", side_effect=persisted_then_failed):
        with pytest.raises(OSError):
            fill(book)
    assert fill(book)["replayed"]
    assert Ledger(path).state.cash == book.state.cash == 79
    assert book.state.fills == 1


def test_competing_stale_writers_cannot_silently_erase_a_fill(tmp_path):
    path = tmp_path / "book.json"
    books = [Ledger(path, authority="EVALUATION", initial_capital=100), Ledger(path)]
    gate = threading.Barrier(2)

    def compete(index):
        gate.wait(timeout=5)
        try:
            fill(books[index], str(index))
            return "written"
        except RuntimeError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(compete, range(2)))
    assert sorted(results) == ["conflict", "written"]
    for index, result in enumerate(results):
        if result == "conflict":
            assert not fill(books[index], str(index))["replayed"]
    reopened = Ledger(path)
    assert reopened.state.cash == 58
    assert reopened.state.fills == 2
    assert reopened.sleeves["fixture"]["SYNTH"].quantity == 4


def test_stale_mark_cannot_erase_new_fill(tmp_path):
    path = tmp_path / "book.json"
    first = Ledger(path, authority="EVALUATION", initial_capital=100)
    stale = Ledger(path)
    fill(first)
    with pytest.raises(RuntimeError):
        stale.mark_to_market("2026-10-20", {"SYNTH": 11})
    stale.mark_to_market("2026-10-20", {"SYNTH": 11})
    assert Ledger(path).nav == 101


@pytest.mark.parametrize("changes", [
    {"quantity": float("nan")}, {"price": float("inf")}, {"cost": float("nan")},
    {"price": 0}, {"cost": -1}, {"quantity": 0}, {"quantity": True},
    {"operation_id": " "}, {"strategy_id": ""}, {"symbol": ""},
    {"date": "2026-99-99"},
])
def test_invalid_fill_leaves_memory_and_disk_unchanged(tmp_path, changes):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)
    before = deepcopy(book.state.to_dict())
    with pytest.raises(ValueError):
        fill(book, **changes)
    assert book.state.to_dict() == before
    assert read_json(path) == before
    assert not book.has_applied("one")


def test_detached_decision_view_cannot_write_or_mutate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    book = Ledger(tmp_path / "book.json", authority="EVALUATION", initial_capital=100)
    detached = Ledger.from_document(book.state.to_dict())
    before = deepcopy(detached.state.to_dict())
    for action in (lambda: fill(detached),
                   lambda: detached.mark_to_market("2026-10-20", {}), detached.save):
        with pytest.raises(RuntimeError):
            action()
        assert detached.state.to_dict() == before
    assert not (tmp_path / "__detached_decision_ledger__").exists()


@pytest.mark.parametrize("after_replace", [False, True])
def test_process_death_at_replacement_replays_exactly_once(tmp_path, after_replace):
    path = tmp_path / "book.json"
    Ledger(path, authority="EVALUATION", initial_capital=100)
    script = """
import os, sys
from pathlib import Path
from unittest.mock import patch
from quant.book.ledger import Ledger
book = Ledger(Path(sys.argv[1]))
replace = os.replace
def die(source, destination):
    if sys.argv[2] == 'True':
        replace(source, destination)
    os._exit(73)
with patch('quant.state.os.replace', side_effect=die):
    book.apply_fill('SYNTH', 2.0, 10.0, 1.0, '2026-10-20', 'fixture', 'one')
"""
    result = subprocess.run([sys.executable, "-c", script, str(path), str(after_replace)],
                            env=os.environ.copy(), timeout=10)
    assert result.returncode == 73
    restarted = Ledger(path)
    assert fill(restarted)["replayed"] is after_replace
    assert Ledger(path).state.cash == 79
    assert Ledger(path).state.fills == 1


@pytest.mark.parametrize("prices", [{"SYNTH": -1}, {"SYNTH": float("nan")},
                                   {"SYNTH": float("inf")}, {"SYNTH": True}])
def test_invalid_marks_preserve_state(tmp_path, prices):
    book = Ledger(tmp_path / "book.json", authority="EVALUATION", initial_capital=100)
    fill(book)
    before = book.state.to_dict()
    with pytest.raises(ValueError):
        book.mark_to_market("2026-10-20", prices)
    assert book.state.to_dict() == before


def test_overflowing_fill_is_rolled_back(tmp_path):
    book = Ledger(tmp_path / "book.json", authority="EVALUATION", initial_capital=100)
    before = book.state.to_dict()
    with pytest.raises(ValueError):
        fill(book, quantity=1e308, price=1e308)
    assert book.state.to_dict() == before
    assert not book.has_applied("one")

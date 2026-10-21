"""An operation token must identify the exact persisted economic fill."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import threading
from unittest.mock import patch

import pytest

from quant.book.ledger import Ledger
from quant.state import read_json, write_json
from tests.test_vertical_book_depth import fill


@pytest.mark.parametrize("changes", [
    {"symbol": "OTHER"}, {"quantity": 3}, {"price": 11}, {"cost": 2},
    {"date": "2026-10-21"}, {"strategy_id": "foreign"},
])
def test_reused_operation_token_cannot_acknowledge_a_different_fill(tmp_path, changes):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)
    fill(book)
    restarted = Ledger(path)
    before = deepcopy(read_json(path))
    with pytest.raises(RuntimeError):
        fill(restarted, **changes)
    assert read_json(path) == before
    assert restarted.state.to_dict() == before


@pytest.mark.parametrize("field,value", [("ledger_id", "foreign"), ("authority", "CAPITAL"),
                                         ("currency", "EUR"), ("mode", "foreign")])
def test_replay_is_bound_to_stored_book_identity(tmp_path, field, value):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)
    fill(book)
    changed = read_json(path)
    changed[field] = value
    write_json(path, changed)
    with pytest.raises(RuntimeError):
        fill(Ledger(path))
    assert read_json(path) == changed


def test_equivalent_int_float_and_signed_zero_inputs_replay(tmp_path):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)
    fill(book, quantity=2, price=10, cost=0)
    assert fill(Ledger(path), quantity=2.0, price=10.0, cost=-0.0)["replayed"]
    assert Ledger(path).state.fills == 1


def test_legacy_id_only_history_cannot_prove_a_payload_match(tmp_path):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)
    fill(book)
    legacy = read_json(path)
    legacy.pop("operation_fingerprints", None)
    write_json(path, legacy)
    with pytest.raises(RuntimeError, match="UNVERIFIABLE"):
        fill(Ledger(path))
    assert read_json(path) == legacy


def test_legacy_history_can_add_new_ids_without_fabricating_old_bindings(tmp_path):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)
    fill(book)
    legacy = read_json(path)
    legacy.pop("operation_fingerprints", None)
    write_json(path, legacy)
    restored = Ledger(path)
    assert not fill(restored, operation="new")["replayed"]
    assert restored.state.fills == 2
    assert "one" not in restored.state.operation_fingerprints
    assert "new" in restored.state.operation_fingerprints


@pytest.mark.parametrize("after_write", [False, True])
def test_fill_and_identity_binding_have_one_publication_boundary(tmp_path, after_write):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)

    def fail(path, value):
        if after_write:
            write_json(path, value)
        raise OSError("publication/ack fault")

    with patch("quant.book.ledger.write_json", side_effect=fail):
        with pytest.raises(OSError):
            fill(book)
    restored = Ledger(path)
    assert ("one" in restored.state.operation_fingerprints) is after_write
    assert fill(restored)["replayed"] is after_write
    assert restored.state.fills == 1


def test_same_token_with_competing_payloads_cannot_claim_both_succeeded(tmp_path):
    path = tmp_path / "book.json"
    books = [Ledger(path, authority="EVALUATION", initial_capital=100), Ledger(path)]
    gate = threading.Barrier(2)

    def compete(index):
        gate.wait(timeout=5)
        try:
            fill(books[index], quantity=index + 1)
            return "written"
        except RuntimeError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(compete, range(2)))
    loser = outcomes.index("conflict")
    with pytest.raises(RuntimeError):
        fill(books[loser], quantity=loser + 1)
    assert Ledger(path).state.fills == 1


def test_fingerprint_does_not_collapse_distinct_large_integer_inputs(tmp_path):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=1e20)
    fill(book, quantity=2**53)
    with pytest.raises(RuntimeError):
        fill(Ledger(path), quantity=2**53 + 1)


@pytest.mark.parametrize("index", [None, [], {"one": "bad"}, {"one": False},
                                   {"orphan": "a" * 64}])
def test_malformed_or_orphan_payload_bindings_fail_closed_on_reconstruction(tmp_path, index):
    path = tmp_path / "book.json"
    book = Ledger(path, authority="EVALUATION", initial_capital=100)
    fill(book)
    malformed = read_json(path)
    malformed["operation_fingerprints"] = index
    write_json(path, malformed)
    before = path.read_bytes()
    with pytest.raises(ValueError):
        Ledger(path)
    assert path.read_bytes() == before

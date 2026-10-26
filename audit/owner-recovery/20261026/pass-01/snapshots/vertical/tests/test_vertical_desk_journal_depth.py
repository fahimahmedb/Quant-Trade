"""Write-ahead intent must retain one identity across retry and completion."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import threading
from unittest.mock import patch

import pytest

from quant.desk.journal import DeskJournal
from quant.state import read_json, write_json


DAY = "2026-10-20"


def begin(journal, **changes):
    args = dict(opportunity_id="one", strategy_id="fixture", session_date=DAY,
                ticket={"opportunity_id": "one"}, fills=[{"symbol": "SYNTH", "quantity": 1}])
    args.update(changes)
    journal.begin(**args)


@pytest.mark.parametrize("after_write", [False, True])
@pytest.mark.parametrize("operation", ["begin", "commit", "begin_session", "close_session"])
def test_write_failure_and_lost_ack_recover_the_same_object(tmp_path, operation, after_write):
    path = tmp_path / "journal.json"
    journal = DeskJournal(path)
    if operation == "commit":
        begin(journal)
    if operation == "close_session":
        journal.begin_session(DAY, {"cash": 100}, {"cash": 100})
    actions = {
        "begin": lambda: begin(journal),
        "commit": lambda: journal.commit("one", "fixture", "BOOKED", DAY, True),
        "begin_session": lambda: journal.begin_session(DAY, {"cash": 100}, {"cash": 100}),
        "close_session": lambda: journal.close_session(DAY),
    }

    def fail(path, payload):
        if after_write:
            write_json(path, payload)
        raise OSError("fixture disk/ack failure")

    with patch("quant.desk.journal.write_json", side_effect=fail):
        with pytest.raises(OSError):
            actions[operation]()
    # Identical retry must reach the same durable state as uninterrupted use.
    actions[operation]()
    recovered = DeskJournal(path)
    assert recovered.pending == journal.pending
    assert recovered.processed == journal.processed
    assert recovered.decision_snapshots == journal.decision_snapshots
    if operation == "commit":
        assert recovered.stats_for("fixture")["booked"] == 1
    if operation == "begin":
        assert recovered.pending_plan("one") is not None
    if operation == "begin_session":
        assert recovered.decision_snapshot(DAY) is not None
    if operation == "close_session":
        assert recovered.decision_snapshot(DAY) is None


@pytest.mark.parametrize("changes", [
    {"strategy_id": "foreign"}, {"session_date": "2026-10-21"},
    {"fills": [{"symbol": "SYNTH", "quantity": 9}]},
    {"ticket": {"opportunity_id": "foreign"}},
])
def test_duplicate_intent_cannot_replace_a_frozen_plan(tmp_path, changes):
    path = tmp_path / "journal.json"
    journal = DeskJournal(path)
    begin(journal)
    before = read_json(path)
    with pytest.raises((RuntimeError, ValueError)):
        begin(journal, **changes)
    assert read_json(path) == before
    assert journal.pending == before["pending"]


def test_completed_opportunity_cannot_regain_a_pending_plan(tmp_path):
    journal = DeskJournal(tmp_path / "journal.json")
    begin(journal)
    journal.commit("one", "fixture", "BOOKED", DAY, True)
    with pytest.raises(RuntimeError):
        begin(journal)
    assert not journal.pending


@pytest.mark.parametrize("changes", [
    {"strategy_id": "foreign"}, {"session_date": "2026-10-21"},
    {"status": "NO_TRADE"}, {"rebalanced": False},
    {"ticket": {"opportunity_id": "foreign"}},
])
def test_completion_cannot_discard_intent_under_a_different_identity(tmp_path, changes):
    path = tmp_path / "journal.json"
    journal = DeskJournal(path)
    begin(journal)
    before = read_json(path)
    args = dict(opportunity_id="one", strategy_id="fixture", status="BOOKED", session_date=DAY,
                rebalanced=True)
    args.update(changes)
    with pytest.raises((RuntimeError, ValueError)):
        journal.commit(**args)
    assert read_json(path) == before
    assert not journal.processed


def test_caller_and_returned_views_cannot_mutate_frozen_intent(tmp_path):
    journal = DeskJournal(tmp_path / "journal.json")
    fills = [{"symbol": "SYNTH", "quantity": 1}]
    begin(journal, fills=fills)
    fills[0]["quantity"] = 10
    returned = journal.pending_plan("one")
    returned["fills"][0]["quantity"] = 20
    assert journal.pending_plan("one")["fills"][0]["quantity"] == 1
    capital = {"cash": 100}
    snapshot = journal.begin_session(DAY, capital, {"cash": 100})
    capital["cash"] = 0
    snapshot["CAPITAL"]["cash"] = 10
    journal.decision_snapshot(DAY)["CAPITAL"]["cash"] = 20
    assert journal.decision_snapshot(DAY)["CAPITAL"]["cash"] == 100


def test_competing_journal_writers_do_not_erase_processed_identities(tmp_path):
    path = tmp_path / "journal.json"
    journals = [DeskJournal(path), DeskJournal(path)]
    gate = threading.Barrier(2)

    def commit(index):
        gate.wait(timeout=5)
        try:
            journals[index].commit(str(index), "fixture", "NO_TRADE", DAY, False)
            return "written"
        except RuntimeError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(commit, range(2)))
    assert sorted(results) == ["conflict", "written"]
    for index, outcome in enumerate(results):
        if outcome == "conflict":
            journals[index].commit(str(index), "fixture", "NO_TRADE", DAY, False)
    assert DeskJournal(path).processed == {"0", "1"}
    assert DeskJournal(path).stats_for("fixture")["sessions"] == 2


def test_out_of_order_completion_cannot_move_rebalance_recency_backward(tmp_path):
    journal = DeskJournal(tmp_path / "journal.json")
    journal.commit("new", "fixture", "BOOKED", "2026-10-21", True)
    journal.commit("old", "fixture", "BOOKED", DAY, True)
    assert journal.stats_for("fixture")["last_rebalance_date"] == "2026-10-21"


def test_unknown_terminal_state_cannot_be_recorded_as_a_processed_session(tmp_path):
    journal = DeskJournal(tmp_path / "journal.json")
    before = deepcopy(journal.stats)
    with pytest.raises(ValueError):
        journal.commit("one", "fixture", "UNKNOWN", DAY, False)
    assert not journal.processed
    assert journal.stats == before

"""Research lesson replay must not change scientific search priorities twice."""

from copy import deepcopy
from unittest.mock import patch

import pytest

from quant.learning.store import BuildTask, LearningStore
from quant.state import read_json, write_json


def result(ticket):
    return {"ticket_id": ticket, "lesson": "synthetic bounded negative",
            "outcome": "REJECTED", "next_action_hint": "review distinct mechanism"}


def test_replay_after_retention_and_restart_does_not_update_priority_twice(tmp_path):
    path = tmp_path / "learning.json"
    store = LearningStore(path)
    for index in range(205):
        assert store.record_research("fixture", "FIXTURE", result(f"ticket-{index}"))
    restarted = LearningStore(path)
    before = deepcopy(read_json(path))
    assert not restarted.record_research("fixture", "FIXTURE", result("ticket-0"))
    assert read_json(path) == before
    assert len(restarted.lessons) == 200
    assert restarted.lane_priorities["fixture"] == 30 - 6 * 205


def test_legacy_state_migrates_retained_ticket_identities(tmp_path):
    path = tmp_path / "learning.json"
    write_json(path, {"version": 1, "lessons": [
        {"source": "RESEARCH", "ticket_id": "old", "lesson": "synthetic negative"}],
        "lane_priorities": {"fixture": 24}})
    store = LearningStore(path)
    assert not store.record_research("fixture", "FIXTURE", result("old"))
    assert store.record_research("fixture", "FIXTURE", result("new"))
    assert not LearningStore(path).record_research("fixture", "FIXTURE", result("old"))


@pytest.mark.parametrize("after_write", [False, True])
def test_same_object_research_retry_recovers_actual_durable_state(tmp_path, after_write):
    path = tmp_path / "learning.json"
    store = LearningStore(path)

    def failure(path, value):
        if after_write:
            write_json(path, value)
        raise OSError("fixture persistence failure")

    with patch("quant.learning.store.write_json", side_effect=failure):
        with pytest.raises(OSError):
            store.record_research("fixture", "FIXTURE", result("one"))
    assert store.record_research("fixture", "FIXTURE", result("one")) is (not after_write)
    recovered = LearningStore(path)
    assert recovered.lane_priorities["fixture"] == 24
    assert recovered.lessons == store.lessons


def test_failed_build_task_write_does_not_suppress_retry(tmp_path):
    path = tmp_path / "learning.json"
    store = LearningStore(path)
    task = BuildTask("fixture", "fixture capability", "synthetic reason", ["BUILD"],
                     "synthetic acceptance", 1)
    with patch("quant.learning.store.write_json", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            store.raise_build_task(task)
    store.raise_build_task(task)
    assert len(LearningStore(path).open_build_tasks()) == 1


@pytest.mark.parametrize("identity", ["", " ", True, 1, [], {}])
def test_invalid_ticket_identity_cannot_change_search_priority(tmp_path, identity):
    store = LearningStore(tmp_path / "learning.json")
    with pytest.raises(ValueError):
        store.record_research("fixture", "FIXTURE", result(identity))
    assert not store.lessons
    assert not store.lane_priorities


@pytest.mark.parametrize("identities", ["one", {}, [None], [False], [" "]])
def test_malformed_replay_index_is_not_interpreted_as_valid_state(tmp_path, identities):
    path = tmp_path / "learning.json"
    write_json(path, {"version": 1, "processed_research_tickets": identities})
    with pytest.raises(ValueError):
        LearningStore(path)

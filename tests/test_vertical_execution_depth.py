"""Model fills must retain causal clocks and a positive capacity premise."""

from dataclasses import replace

import pytest

from quant.dataplane.panel import PricePanel
from quant.desk.execution import ExecutionModel


def panel(volume=100):
    return PricePanel([dict(date=day, symbol="SYNTH", open=10, high=11, low=9,
                            close=10, adj_close=10, volume=volume)
                       for day in ("2026-10-19", "2026-10-20")])


@pytest.mark.parametrize("volume", [0, -1, float("nan"), float("inf")])
def test_unusable_adv_cannot_produce_an_unbounded_fill(volume):
    with pytest.raises(ValueError):
        ExecutionModel().fill(panel(volume), "SYNTH", 100, "2026-10-19", "2026-10-20")


def test_no_predecision_history_cannot_be_reported_as_liquid():
    with pytest.raises(ValueError):
        ExecutionModel().fill(panel(), "SYNTH", 100, "2026-10-18", "2026-10-20")


@pytest.mark.parametrize("execution_date", ["2026-10-19", "2026-10-18"])
def test_fill_must_occur_after_its_signal(execution_date):
    with pytest.raises(ValueError):
        ExecutionModel().fill(panel(), "SYNTH", 1, "2026-10-19", execution_date)


@pytest.mark.parametrize("changes", [
    {"max_participation": 0}, {"max_participation": -1}, {"max_participation": float("nan")},
    {"max_participation": 2}, {"commission_bps": -1}, {"half_spread_bps": float("inf")},
    {"adv_lookback_days": 0}, {"adv_lookback_days": True},
])
def test_invalid_model_parameters_cannot_make_a_fill(changes):
    with pytest.raises(ValueError):
        replace(ExecutionModel(), **changes).fill(panel(), "SYNTH", 1, "2026-10-19", "2026-10-20")


@pytest.mark.parametrize("quantity", [float("nan"), float("inf"), True])
def test_nonfinite_or_boolean_quantity_is_rejected(quantity):
    with pytest.raises(ValueError):
        ExecutionModel().fill(panel(), "SYNTH", quantity, "2026-10-19", "2026-10-20")


def test_valid_capacity_truncation_remains_causal_and_bounded():
    model = ExecutionModel(max_participation=0.01)
    data = panel()
    before = model.fill(data, "SYNTH", 100, "2026-10-19", "2026-10-20")
    # Tomorrow's volume is inaccessible to the signal-time capacity estimate.
    data.bars[("2026-10-20", "SYNTH")]["volume"] = 1e9
    after = model.fill(data, "SYNTH", 100, "2026-10-19", "2026-10-20")
    assert after == before
    assert after["capacity_truncated"]
    assert after["quantity"] == 1
    assert after["participation"] == 0.01

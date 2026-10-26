import pytest

from research.research_os.discovery_engine import _outcome_payload_present


@pytest.mark.parametrize(
    "field",
    [
        "alpha",
        "observed_alpha",
        "pnl",
        "realized_pnl",
        "return_series",
        "effect_size",
        "observed_effect",
        "market_response",
        "price_response",
    ],
)
def test_outcome_shaped_aliases_are_detected_before_discovery(field):
    assert _outcome_payload_present({field: 0.1}) is True


def test_safe_unobserved_outcome_sentinels_do_not_fabricate_access():
    assert _outcome_payload_present({"alpha": "NOT_OBSERVED"}) is False
    assert _outcome_payload_present({"market_response": "NOT_OBSERVED"}) is False
    assert _outcome_payload_present({"outcome_accessed": False}) is False

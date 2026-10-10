"""Synthetic causal/restart checks, isolated from the stdlib-only core suite."""
import numpy as np
import pytest

from volatility import ewma_path, garch_path


PARAMS = {"mu": 0.25, "omega": 0.02, "alpha[1]": 0.08,
          "beta[1]": 0.85, "gamma[1]": 0.04}


def filter_path(kind, r, seed=0.4):
    if kind == "ewma":
        return ewma_path(r, mean=PARAMS["mu"], initial_variance=seed)
    return garch_path(r, PARAMS, gjr=(kind == "gjr"), initial_variance=seed)


@pytest.mark.parametrize("kind", ["ewma", "garch", "gjr"])
def test_future_append_and_replacement_leave_past_forecasts_unchanged(kind):
    past = np.array([0.1, -0.3, 0.8, -0.2])
    baseline = filter_path(kind, past)
    for future in [np.array([90.0, -200.0]), np.array([-800.0, 7.0, 55.0])]:
        extended = filter_path(kind, np.concatenate([past, future]))
        np.testing.assert_array_equal(extended[:len(past) + 1], baseline)


@pytest.mark.parametrize("kind", ["ewma", "garch", "gjr"])
def test_restart_from_saved_forecast_matches_uninterrupted_filter(kind):
    r = np.array([0.1, -0.3, 0.8, -0.2, 0.6, -0.5])
    uninterrupted = filter_path(kind, r)
    prefix = filter_path(kind, r[:3])
    resumed = filter_path(kind, r[3:], seed=prefix[-1])
    np.testing.assert_array_equal(resumed, uninterrupted[3:])


@pytest.mark.parametrize("kind", ["ewma", "garch", "gjr"])
def test_current_return_changes_only_next_forecast(kind):
    r = np.array([0.1, -0.3, 0.8, -0.2])
    altered = r.copy()
    altered[2] = -40.0
    baseline, changed = filter_path(kind, r), filter_path(kind, altered)
    np.testing.assert_array_equal(baseline[:3], changed[:3])
    assert baseline[3] != changed[3]


@pytest.mark.parametrize("kind", ["ewma", "garch", "gjr"])
def test_empty_restart_preserves_saved_forecast(kind):
    np.testing.assert_array_equal(filter_path(kind, np.array([]), seed=0.7), [0.7])


@pytest.mark.parametrize("state", [{"mean": 0.0}, {"initial_variance": 0.2}])
def test_ewma_rejects_partial_causal_state(state):
    with pytest.raises(ValueError, match="together"):
        ewma_path(np.array([0.1]), **state)


@pytest.mark.parametrize("kind", ["ewma", "garch", "gjr"])
@pytest.mark.parametrize("seed", [-1.0, np.nan, np.inf])
def test_invalid_saved_variance_is_rejected(kind, seed):
    with pytest.raises(ValueError, match="initial_variance"):
        filter_path(kind, np.array([0.1]), seed=seed)


@pytest.mark.parametrize("mean,lam", [(np.nan, 0.94), (np.inf, 0.94),
                                      (0.0, -0.1), (0.0, 1.1), (0.0, np.nan)])
def test_invalid_ewma_fixed_configuration_is_rejected(mean, lam):
    with pytest.raises(ValueError):
        ewma_path(np.array([0.1]), lam=lam, mean=mean, initial_variance=0.2)

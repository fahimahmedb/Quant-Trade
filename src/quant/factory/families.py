"""A second, structurally independent research family — declared, not assumed.

The Factory currently searches one mechanism: the asset's *own* cross-sectionally
demeaned trailing return.  Every expression in that space shares an input and a
story, so finding more of them adds trials without adding breadth.

This module declares a family whose signal never reads the asset's own return.
For each name it aggregates the trailing returns of that name's most correlated
*peers*, on the theory that information diffuses across related sectors with a
lag.  A name whose peers have moved while it has not is either about to catch up
(momentum direction) or the peers overreacted (reversal direction); both are
testable, and neither is a re-parameterisation of own-residual reversal.

Two details keep it honest.

* The correlation window used to choose peers **ends before** the signal window
  begins. Estimating peer correlation on the same returns that form the signal
  would select peers using the very data the signal is made of.
* Independence is declared on named structural axes and then *checked* against
  the other family's realised signal vectors. A declared independence that fails
  empirically is reported as ``FAMILIES_EMPIRICALLY_COLLINEAR`` rather than kept.

Integration point: ``quant.factory.signals.weights_for`` hard-codes the
cross-sectional scorer and is reached from ``quant.clock``, which is
fingerprint-critical for P0 and must not be modified in this wave. So the
dispatch lives here as :func:`weights_for_family`. When ``clock.py`` is no longer
fingerprint-critical, route ``weights_for`` through this dispatch and add
:func:`lead_lag_lane_definition` to ``lanes.lane_definitions`` so the declared
grid is counted in the multiple-testing budget before it is ever run.
"""

from __future__ import annotations

import statistics
from dataclasses import asdict, dataclass
from typing import Any, Callable, Sequence

from ..dataplane.panel import PricePanel
from .signals import StrategySpec, cross_sectional_scores, target_weights


FAMILY_CROSS_SECTIONAL = "cross_sectional"
FAMILY_PEER_LEAD_LAG = "peer_lead_lag"

#: Default peer-selection geometry. Declared here, and part of every grid label.
DEFAULT_PEER_COUNT = 3
DEFAULT_CORRELATION_WINDOW = 60


def peer_lead_lag_scores(panel: PricePanel, universe: list[str], asof: str,
                         lookback_days: int, peer_count: int = DEFAULT_PEER_COUNT,
                         correlation_window: int = DEFAULT_CORRELATION_WINDOW
                         ) -> dict[str, float]:
    """Peer-return score for every name, excluding the name's own return.

    Returns an empty mapping when history is insufficient. Callers must read that
    as "no signal", never as a zero signal — the same contract as
    :func:`quant.factory.signals.cross_sectional_scores`.
    """
    if peer_count < 1 or correlation_window < 5 or lookback_days < 1:
        return {}
    dates = panel.aligned_dates(universe)
    position = panel.aligned_index(universe, asof)
    required = lookback_days + correlation_window + 1
    if position is None or position < required:
        return {}
    if len(universe) < peer_count + 2:
        return {}

    # Signal window: the trailing `lookback_days` sessions ending at asof.
    signal_start, signal_end = dates[position - lookback_days], dates[position]
    # Correlation window: ends at the session *before* the signal window opens.
    correlation_end = position - lookback_days
    correlation_start = correlation_end - correlation_window
    window = dates[correlation_start:correlation_end + 1]

    daily: dict[str, list[float]] = {}
    for symbol in universe:
        series: list[float] = []
        for earlier, later in zip(window, window[1:]):
            before = panel.price(earlier, symbol)
            if before <= 0:
                return {}
            series.append(panel.price(later, symbol) / before - 1.0)
        if len(series) < 5:
            return {}
        daily[symbol] = series

    signal_return: dict[str, float] = {}
    for symbol in universe:
        before = panel.price(signal_start, symbol)
        if before <= 0:
            return {}
        signal_return[symbol] = panel.price(signal_end, symbol) / before - 1.0

    raw: dict[str, float] = {}
    for symbol in universe:
        peers = _most_correlated(symbol, universe, daily, peer_count)
        if not peers:
            return {}
        raw[symbol] = statistics.fmean(signal_return[peer] for peer in peers)
    mean = statistics.fmean(raw.values())
    residual = {symbol: value - mean for symbol, value in raw.items()}
    dispersion = statistics.pstdev(residual.values())
    if dispersion <= 0:
        return {}
    return {symbol: value / dispersion for symbol, value in residual.items()}


def _most_correlated(symbol: str, universe: Sequence[str], daily: dict[str, list[float]],
                     peer_count: int) -> list[str]:
    scores: list[tuple[float, str]] = []
    own = daily[symbol]
    for candidate in universe:
        if candidate == symbol:
            continue
        other = daily[candidate]
        correlation = _correlation(own, other)
        if correlation is None:
            continue
        scores.append((correlation, candidate))
    if len(scores) < peer_count:
        return []
    scores.sort(key=lambda item: (-item[0], item[1]))
    return [candidate for _, candidate in scores[:peer_count]]


def _correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right) or len(left) < 3:
        return None
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    covariance = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_spread = sum((a - left_mean) ** 2 for a in left)
    right_spread = sum((b - right_mean) ** 2 for b in right)
    if left_spread <= 0 or right_spread <= 0:
        return None
    return covariance / ((left_spread ** 0.5) * (right_spread ** 0.5))


#: family name -> scorer with the signature ``(panel, universe, asof, lookback)``.
FAMILY_SIGNALS: dict[str, Callable[[PricePanel, list[str], str, int], dict[str, float]]] = {
    FAMILY_CROSS_SECTIONAL: cross_sectional_scores,
    FAMILY_PEER_LEAD_LAG: peer_lead_lag_scores,
}


def scores_for_family(panel: PricePanel, spec: StrategySpec, asof: str) -> dict[str, float]:
    scorer = FAMILY_SIGNALS.get(spec.family)
    if scorer is None:
        return {}
    return scorer(panel, spec.universe, asof, spec.lookback_days)


def weights_for_family(panel: PricePanel, spec: StrategySpec, asof: str) -> dict[str, float]:
    """The family-dispatching signal path. Identical weighting for every family."""
    return target_weights(scores_for_family(panel, spec, asof), spec)


# --- declared structural independence ---------------------------------------

@dataclass(frozen=True)
class FamilyAxes:
    """The structural axes a family occupies. Declared before comparison."""

    family: str
    mechanism: str
    #: Does the score read the asset's own trailing return?
    uses_own_return: bool
    #: Does it read other assets' trailing returns?
    uses_peer_returns: bool
    #: What selects the inputs, e.g. "NONE" or "TRAILING_CORRELATION".
    input_selection: str
    exposure_construction: str
    turnover_profile: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CROSS_SECTIONAL_AXES = FamilyAxes(
    family=FAMILY_CROSS_SECTIONAL,
    mechanism="own trailing return demeaned across the universe; liquidity demand pushes a "
              "name's residual away from its peers and it reverts, or information diffuses "
              "slowly and it persists",
    uses_own_return=True, uses_peer_returns=False, input_selection="NONE",
    exposure_construction="DOLLAR_NEUTRAL_DEMEANED_SCORE",
    turnover_profile="REBALANCE_ON_HOLDING_PERIOD_AND_DRIFT_BAND")

PEER_LEAD_LAG_AXES = FamilyAxes(
    family=FAMILY_PEER_LEAD_LAG,
    mechanism="peers' trailing returns only; information about a shared factor reaches "
              "related sectors at different speeds, so a name that has not yet moved with "
              "its peers either catches up or the peers overreacted",
    uses_own_return=False, uses_peer_returns=True,
    input_selection="TRAILING_CORRELATION_WINDOW_ENDING_BEFORE_THE_SIGNAL_WINDOW",
    exposure_construction="DOLLAR_NEUTRAL_DEMEANED_SCORE",
    turnover_profile="REBALANCE_ON_HOLDING_PERIOD_AND_DRIFT_BAND")


STRUCTURALLY_INDEPENDENT = "STRUCTURALLY_INDEPENDENT"
SHARES_INPUT_AND_MECHANISM = "SHARES_INPUT_AND_MECHANISM"
EMPIRICALLY_COLLINEAR = "FAMILIES_EMPIRICALLY_COLLINEAR"


@dataclass(frozen=True)
class IndependenceReport:
    verdict: str
    shared_axes: tuple[str, ...]
    distinct_axes: tuple[str, ...]
    #: Mean absolute cross-sectional correlation of the two score vectors.
    realised_correlation: float | None = None
    sessions_compared: int = 0
    threshold: float = 0.7
    detail: str = ""

    @property
    def independent(self) -> bool:
        return self.verdict == STRUCTURALLY_INDEPENDENT

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def independence_report(left: FamilyAxes, right: FamilyAxes,
                        panel: PricePanel | None = None,
                        universe: list[str] | None = None,
                        sessions: Sequence[str] = (), lookback_days: int = 5,
                        threshold: float = 0.7) -> IndependenceReport:
    """Compare two families on declared axes, then check the declaration.

    A family pair that shares its input axis and mechanism is not independent
    however differently it is parameterised. A pair that looks independent on
    paper but produces near-identical score vectors is reported as empirically
    collinear: the declaration lost.
    """
    shared: list[str] = []
    distinct: list[str] = []
    for axis in ("mechanism", "uses_own_return", "uses_peer_returns", "input_selection",
                 "exposure_construction", "turnover_profile"):
        if getattr(left, axis) == getattr(right, axis):
            shared.append(axis)
        else:
            distinct.append(axis)
    input_shared = (left.uses_own_return == right.uses_own_return
                    and left.uses_peer_returns == right.uses_peer_returns)
    if input_shared and left.mechanism == right.mechanism:
        return IndependenceReport(SHARES_INPUT_AND_MECHANISM, tuple(shared), tuple(distinct),
                                  threshold=threshold,
                                  detail="same inputs and the same stated mechanism")

    correlation: float | None = None
    compared = 0
    if panel is not None and universe is not None and sessions:
        correlations: list[float] = []
        for session in sessions:
            first = FAMILY_SIGNALS[left.family](panel, universe, session, lookback_days)
            second = FAMILY_SIGNALS[right.family](panel, universe, session, lookback_days)
            common = sorted(set(first) & set(second))
            if len(common) < 3:
                continue
            value = _correlation([first[symbol] for symbol in common],
                                 [second[symbol] for symbol in common])
            if value is not None:
                correlations.append(abs(value))
        compared = len(correlations)
        if correlations:
            correlation = statistics.fmean(correlations)

    if correlation is not None and correlation > threshold:
        return IndependenceReport(EMPIRICALLY_COLLINEAR, tuple(shared), tuple(distinct),
                                  correlation, compared, threshold,
                                  detail="declared independence is not visible in the "
                                         "realised score vectors")
    return IndependenceReport(STRUCTURALLY_INDEPENDENT, tuple(shared), tuple(distinct),
                              correlation, compared, threshold)


# --- the declared lane -------------------------------------------------------

def _grid(universe: list[str], dataset_id: str, lookbacks: tuple[int, ...],
          holdings: tuple[int, ...], band: float,
          thresholds: tuple[float, ...]) -> list[StrategySpec]:
    return [StrategySpec(family=FAMILY_PEER_LEAD_LAG, universe=universe,
                         lookback_days=lookback, direction=direction,
                         min_abs_score=threshold, holding_days=holding,
                         no_trade_band=band, dataset_id=dataset_id)
            for lookback in lookbacks for holding in holdings
            for direction in (-1, 1) for threshold in thresholds]


def lead_lag_lane_definition(universe: list[str], dataset_id: str) -> dict[str, Any]:
    """The lane, declared in full before any of it is run.

    Not yet added to ``lanes.lane_definitions``: doing so changes what
    ``clock.py`` schedules, and ``clock.py`` is fingerprint-critical for P0 in
    this wave. The grid is declared here so its trial count is known in advance
    and cannot be widened after results are seen.
    """
    return {
        "peer_lead_lag_diffusion": {
            "lane": "cross_asset_information_diffusion",
            "priority": 27.0,
            "question": "Does a sector that has not yet moved with its most correlated peers "
                        "catch up over one to twenty-one sessions, or did the peers "
                        "overreact, net of costs?",
            "mechanism": "Sectors share factors but absorb information at different speeds. "
                         "A score built only from peers' trailing returns carries no part of "
                         "the name's own residual, so it is not a re-parameterisation of "
                         "own-residual reversal. Peers are chosen on a correlation window "
                         "that ends before the signal window opens, so peer selection cannot "
                         "use the returns the signal is made of.",
            "falsification": "Reject unless the out-of-sample window is profitable after "
                             "modelled costs and at double those costs, profitable in both "
                             "subperiods, beta-neutral, unconcentrated, and significant "
                             "against a multiple-testing threshold that charges this grid on "
                             "top of every expression already tried on this dataset.",
            "independence_claim": PEER_LEAD_LAG_AXES.to_dict(),
            "grid": _grid(universe, dataset_id, (1, 2, 3, 5, 10, 21), (1, 5), 0.0, (0.5, 1.0)),
        }
    }


def declared_trial_count(universe: list[str], dataset_id: str) -> int:
    """Trials this lane adds to the family-wise budget, known before running."""
    definition = lead_lag_lane_definition(universe, dataset_id)
    return sum(len(entry["grid"]) for entry in definition.values())

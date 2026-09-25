"""Per-market Capital Desk configuration.

The SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK chain is the same for every
market; what differs is what a *hard limit* means. A relative-value ETF book
must stay dollar-neutral; a futures trend/carry book is directional by design
and holds notional well above capital in low-volatility contracts (a 2-year
note future moves ~1.5% a year), so neutrality and 1.5x gross would veto the
strategy the research validated. Both profiles keep the drawdown throttle,
drawdown halt and NAV floor unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass

from .execution import ExecutionModel
from .risk import RiskLimits


FUTURES_DATASET = "futures_excess_return_daily"
FUTURES_BROAD_DATASET = "futures_excess_return_daily_broad"


@dataclass(frozen=True)
class DeskProfile:
    name: str
    limits: RiskLimits
    execution: ExecutionModel


DEFAULT_PROFILE = DeskProfile("etf_relative_value", RiskLimits(), ExecutionModel())

FUTURES_PROFILE = DeskProfile(
    "futures_trend_carry",
    RiskLimits(max_gross_ratio=4.0, max_net_ratio=2.0, max_symbol_ratio=0.60),
    # Liquid futures: ~0.5bp commission and ~1.5bp half-spread per unit notional,
    # under the 4bp research assumption. Volume is unavailable in the futures
    # panel, so the participation cap cannot bind (declared dataset caveat).
    ExecutionModel(commission_bps=0.5, half_spread_bps=1.5,
                   impact_bps_at_full_participation=10.0),
)


CALENDAR_DATASET = "us_calendar_legs_daily"

#: One directional SPY (or SPY overnight-leg) sleeve: net exposure is the
#: strategy, so the neutrality limit is lifted; SPY costs ~0.3bp half-spread.
CALENDAR_PROFILE = DeskProfile(
    "calendar_flows",
    RiskLimits(max_gross_ratio=1.5, max_net_ratio=1.0, max_symbol_ratio=1.0),
    ExecutionModel(commission_bps=0.3, half_spread_bps=0.5,
                   impact_bps_at_full_participation=10.0),
)


PERP_DATASET = "perp_funding_pairs_daily"

#: Market-neutral pairs: neutrality stays binding; per-leg cap; taker fees ~5bp
#: plus spread on thin listings; capacity from each venue's daily notional.
PERP_PROFILE = DeskProfile(
    "perp_funding_spread",
    RiskLimits(max_gross_ratio=1.5, max_net_ratio=0.10, max_symbol_ratio=0.10),
    ExecutionModel(commission_bps=5.0, half_spread_bps=2.5,
                   impact_bps_at_full_participation=15.0, max_participation=0.01),
)


def profile_for(dataset_id: str) -> DeskProfile:
    if dataset_id == PERP_DATASET:
        return PERP_PROFILE
    if dataset_id == CALENDAR_DATASET:
        return CALENDAR_PROFILE
    if dataset_id in (FUTURES_DATASET, FUTURES_BROAD_DATASET):
        return FUTURES_PROFILE
    return DEFAULT_PROFILE

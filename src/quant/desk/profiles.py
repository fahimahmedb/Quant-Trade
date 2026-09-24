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


def profile_for(dataset_id: str) -> DeskProfile:
    return FUTURES_PROFILE if dataset_id == FUTURES_DATASET else DEFAULT_PROFILE

"""Opening-regime execution, with the market move kept out of the cost.

The Form 4 entry rule targets the first authorized regular-session open after
public observability, and the envelope contract section 6 requires that regime to
be an explicit modelling dimension:

* ``ENTRY_AT_OPEN_REQUIRES_OPENING_REGIME_COST_MODEL``
* ``GENERIC_INTRADAY_SPREAD_IS_NOT_AUTOMATIC_OPEN_CALIBRATION``
* ``OPEN_EXECUTION_COST_MUST_NOT_DOUBLE_COUNT_MARKET_RETURN``

The third is the one that quietly ruins event studies. If execution loss is
measured against the prior session's close, the overnight gap — which is market
return, and part of ``T_j`` — is charged as a trading cost. The gap is reported
here, separately and labelled, and the only admissible cost reference is the
authorized open itself.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any


#: The only admissible reference for an execution-loss measurement at the open.
REFERENCE_AUTHORIZED_OPEN = "AUTHORIZED_OPEN_PRICE"
#: Bases that would fold market return into execution cost.
REFERENCE_PRIOR_CLOSE = "PRIOR_SESSION_CLOSE"
REFERENCE_SIGNAL_CLOSE = "SIGNAL_DATE_CLOSE"

FORBIDDEN_REFERENCES = {
    REFERENCE_PRIOR_CLOSE: "OPEN_EXECUTION_COST_MUST_NOT_DOUBLE_COUNT_MARKET_RETURN",
    REFERENCE_SIGNAL_CLOSE: "OPEN_EXECUTION_COST_MUST_NOT_DOUBLE_COUNT_MARKET_RETURN",
}

#: Opening mechanisms. They are not interchangeable and must not share a
#: calibration without evidence that one represents the other.
MECHANISM_OPENING_AUCTION = "OPENING_AUCTION"
MECHANISM_CONTINUOUS_AFTER_OPEN = "CONTINUOUS_AFTER_OPEN"
MECHANISMS = (MECHANISM_OPENING_AUCTION, MECHANISM_CONTINUOUS_AFTER_OPEN)


@dataclass(frozen=True)
class OpeningExecutionModel:
    """Expected execution loss at the authorized open.

    Every coefficient carries the regime it was calibrated on. A model whose
    calibration regime differs from the mechanism it is being applied to reports
    a violation rather than silently transporting an intraday number into the
    opening auction.
    """

    mechanism: str
    half_spread_bps: float
    impact_bps_at_reference: float
    reference_participation: float
    #: Regime the coefficients were calibrated on.
    calibration_regime: str
    #: Provenance class of the coefficients, mirroring the parameter inventory.
    provenance: str = "UNAVAILABLE"
    #: Largest share of reference liquidity the policy may take.
    max_participation: float = 0.05

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.mechanism not in MECHANISMS:
            problems.append("OPENING_MECHANISM_NOT_DECLARED")
        if self.calibration_regime not in MECHANISMS:
            problems.append("CALIBRATION_REGIME_NOT_DECLARED")
        elif self.calibration_regime != self.mechanism:
            problems.append("GENERIC_INTRADAY_SPREAD_IS_NOT_AUTOMATIC_OPEN_CALIBRATION")
        if self.reference_participation <= 0:
            problems.append("REFERENCE_PARTICIPATION_MUST_BE_POSITIVE")
        if self.half_spread_bps < 0 or self.impact_bps_at_reference < 0:
            problems.append("NEGATIVE_EXECUTION_COEFFICIENT")
        if not 0 < self.max_participation <= 1:
            problems.append("PARTICIPATION_LIMIT_OUT_OF_RANGE")
        return problems

    def impact_bps(self, participation: float) -> float:
        if participation <= 0:
            return 0.0
        shape = math.sqrt(min(participation, 1.0) / self.reference_participation)
        return self.impact_bps_at_reference * shape

    def execution_loss_bps(self, participation: float) -> float:
        return self.half_spread_bps + self.impact_bps(participation)

    def fill(self, authorized_open: float, quantity: float, reference_liquidity: float,
             prior_close: float | None = None,
             reference_basis: str = REFERENCE_AUTHORIZED_OPEN) -> dict[str, Any]:
        """Model one entry at the authorized open.

        ``reference_liquidity`` is the permitted liquidity reference in notional
        terms. The returned document separates three things that are routinely
        merged: the execution loss, the capacity truncation, and the overnight
        market move.
        """
        problems = self.violations()
        if reference_basis in FORBIDDEN_REFERENCES:
            problems.append(FORBIDDEN_REFERENCES[reference_basis])
        elif reference_basis != REFERENCE_AUTHORIZED_OPEN:
            problems.append("EXECUTION_REFERENCE_BASIS_NOT_RECOGNISED")
        if authorized_open <= 0:
            problems.append("AUTHORIZED_OPEN_PRICE_NOT_POSITIVE")
            return {"filled_quantity": 0.0, "violations": sorted(set(problems))}

        ceiling = reference_liquidity * self.max_participation
        requested = abs(quantity) * authorized_open
        truncated = False
        if ceiling > 0 and requested > ceiling:
            quantity = math.copysign(ceiling / authorized_open, quantity)
            requested = ceiling
            truncated = True
        participation = requested / reference_liquidity if reference_liquidity > 0 else 0.0
        loss_bps = self.execution_loss_bps(participation)
        side = 1.0 if quantity >= 0 else -1.0
        fill_price = authorized_open * (1.0 + side * loss_bps / 10_000.0)
        gap_bps = (None if not prior_close or prior_close <= 0
                   else (authorized_open / prior_close - 1.0) * 10_000.0)
        return {
            "mechanism": self.mechanism,
            "reference_basis": REFERENCE_AUTHORIZED_OPEN,
            "reference_price": authorized_open,
            "filled_quantity": quantity,
            "notional": requested,
            "participation": participation,
            "capacity_truncated": truncated,
            "execution_loss_bps": loss_bps,
            "impact_bps": self.impact_bps(participation),
            "fill_price": fill_price,
            "execution_loss": requested * loss_bps / 10_000.0,
            # Reported, never charged: this is market return and belongs to T_j.
            "overnight_gap_bps": gap_bps,
            "overnight_gap_classification": "MARKET_RETURN_NOT_EXECUTION_COST",
            "provenance": self.provenance,
            "violations": sorted(set(problems)),
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

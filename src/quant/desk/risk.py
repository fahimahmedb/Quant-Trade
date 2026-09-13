"""RISK: portfolio-context evaluation of the final simulated state.

``OPERATING_MODEL.md``: RISK "may reject the proposal even when the candidate
itself is credible". These limits are about the Book, not the signal.

Two properties matter and both were wrong in the first implementation:

* The portfolio a proposal produces is the *aggregate* of every sleeve, so the
  strategy's own current sleeve must be removed before its target is added.
  Otherwise a strategy is charged twice for the position it already holds.
* An approval must describe the state that will actually be simulated. If a
  proposal is throttled or scaled, the limits are re-checked on the scaled
  portfolio, and after execution they are re-checked again on the portfolio the
  fills actually produce, because capacity truncation can move it further.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ..book.ledger import Ledger


@dataclass(frozen=True)
class RiskLimits:
    max_gross_ratio: float = 1.50
    max_net_ratio: float = 0.10
    max_symbol_ratio: float = 0.25
    drawdown_throttle: float = -0.10
    drawdown_halt: float = -0.20
    throttle_scale: float = 0.5
    min_nav_ratio: float = 0.50

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def project(ledger: Ledger, strategy_id: str,
            target_notional: dict[str, float]) -> dict[str, float]:
    """The portfolio that results if this strategy moves to ``target_notional``.

    Aggregate exposure, less this strategy's existing sleeve, plus its target.
    Symbols the strategy is dropping must appear in ``target_notional`` at zero;
    the desk guarantees that.
    """
    resulting = dict(ledger.symbol_exposures())
    for symbol, value in ledger.sleeve_exposures(strategy_id).items():
        resulting[symbol] = resulting.get(symbol, 0.0) - value
    for symbol, value in target_notional.items():
        resulting[symbol] = resulting.get(symbol, 0.0) + value
    return {symbol: value for symbol, value in resulting.items() if abs(value) > 1e-9}


def assess(portfolio: dict[str, float], nav: float, drawdown: float,
           limits: RiskLimits, initial_capital: float) -> dict[str, Any]:
    """Check every hard limit against one concrete portfolio."""
    gross = sum(abs(value) for value in portfolio.values())
    net = sum(portfolio.values())
    gross_ratio = gross / nav if nav else 0.0
    net_ratio = net / nav if nav else 0.0
    largest = max((abs(value) / nav for value in portfolio.values()), default=0.0) if nav else 0.0

    violations: list[str] = []
    if nav <= initial_capital * limits.min_nav_ratio:
        violations.append(f"NAV {nav:,.0f} is below the {limits.min_nav_ratio:.0%} floor of "
                          f"initial capital")
    if drawdown <= limits.drawdown_halt:
        violations.append(f"drawdown {drawdown:.2%} breaches the halt level "
                          f"{limits.drawdown_halt:.0%}")
    if gross_ratio > limits.max_gross_ratio + 1e-9:
        violations.append(f"gross exposure {gross_ratio:.2f}x exceeds the "
                          f"{limits.max_gross_ratio:.2f}x limit")
    if abs(net_ratio) > limits.max_net_ratio + 1e-9:
        violations.append(f"net exposure {net_ratio:+.2%} exceeds the "
                          f"{limits.max_net_ratio:.0%} neutrality limit")
    if largest > limits.max_symbol_ratio + 1e-9:
        violations.append(f"largest single-name weight {largest:.2%} exceeds "
                          f"{limits.max_symbol_ratio:.0%}")
    return {"violations": violations, "gross_ratio": gross_ratio, "net_ratio": net_ratio,
            "largest_symbol_ratio": largest, "gross": gross, "net": net,
            "checks": {
                "nav_above_floor": nav > initial_capital * limits.min_nav_ratio,
                "drawdown_within_halt": drawdown > limits.drawdown_halt,
                "gross_within_limit": gross_ratio <= limits.max_gross_ratio + 1e-9,
                "net_within_neutrality": abs(net_ratio) <= limits.max_net_ratio + 1e-9,
                "concentration_within_limit": largest <= limits.max_symbol_ratio + 1e-9}}


def evaluate(ledger: Ledger, strategy_id: str, target_notional: dict[str, float],
             limits: RiskLimits) -> dict[str, Any]:
    """Decide on the proposal, and judge the state the decision actually produces.

    Returns the scaled targets alongside the verdict so the caller cannot apply
    a different portfolio from the one that was approved.
    """
    nav, drawdown = ledger.nav, ledger.drawdown
    initial = ledger.state.initial_capital

    proposed = assess(project(ledger, strategy_id, target_notional), nav, drawdown,
                      limits, initial)

    cap = 1.0
    if limits.drawdown_halt < drawdown <= limits.drawdown_throttle:
        cap = limits.throttle_scale

    def within_gross(candidate: float) -> bool:
        portfolio = project(ledger, strategy_id,
                            {symbol: value * candidate
                             for symbol, value in target_notional.items()})
        gross = sum(abs(value) for value in portfolio.values())
        return (gross / nav if nav else 0.0) <= limits.max_gross_ratio + 1e-12

    # Scaling is a sizing remedy, so it answers only the limits that are about
    # size: gross exposure and the drawdown throttle. A neutrality or
    # concentration breach is structural -- shrinking a directional proposal
    # until it fits the neutrality limit still leaves a directional position
    # that the strategy's evidence does not support, so those are vetoed below
    # rather than quietly resized.
    #
    # Scaling only shrinks this strategy's own legs; exposure held by other
    # sleeves is fixed, so a closed-form ratio of the proposed gross is wrong.
    # Search for the largest admissible scale instead.
    if within_gross(cap):
        scale = cap
    elif not within_gross(0.0):
        scale = 0.0  # Not repairable by sizing: the rest of the book is the problem.
    else:
        low, high = 0.0, cap
        for _ in range(60):
            middle = (low + high) / 2.0
            if within_gross(middle):
                low = middle
            else:
                high = middle
        scale = low

    scaled = {symbol: value * scale for symbol, value in target_notional.items()}
    # The approval describes this portfolio, not the pre-scale one.
    final = assess(project(ledger, strategy_id, scaled), nav, drawdown, limits, initial)

    return {"approved": not final["violations"], "scale": scale,
            "throttled": scale < 1.0, "scaled_target": scaled,
            "vetoes": final["violations"], "checks": final["checks"],
            "drawdown": drawdown, "nav": nav,
            "gross_ratio": final["gross_ratio"], "net_ratio": final["net_ratio"],
            "largest_symbol_ratio": final["largest_symbol_ratio"],
            "pre_scale": {key: proposed[key] for key in
                          ("gross_ratio", "net_ratio", "largest_symbol_ratio", "violations")},
            "limits": limits.to_dict()}


def verify_final(ledger: Ledger, strategy_id: str, executed_notional: dict[str, float],
                 limits: RiskLimits) -> dict[str, Any]:
    """Re-check the limits on the portfolio the modelled fills actually produce.

    Capacity truncation happens after sizing, so the executed portfolio is not
    necessarily the approved one.
    """
    verdict = assess(project(ledger, strategy_id, executed_notional), ledger.nav,
                     ledger.drawdown, limits, ledger.state.initial_capital)
    return {"approved": not verdict["violations"], "vetoes": verdict["violations"],
            "gross_ratio": verdict["gross_ratio"], "net_ratio": verdict["net_ratio"],
            "largest_symbol_ratio": verdict["largest_symbol_ratio"],
            "checks": verdict["checks"]}

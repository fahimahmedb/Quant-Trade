"""RISK: portfolio-context evaluation of the final simulated state.

``OPERATING_MODEL.md``: RISK "may reject the proposal even when the candidate
itself is credible". These limits are about the Book, not the signal.

Two properties matter:

* the strategy's own current sleeve is removed before its target is added;
* approval and final verification describe the exact portfolio/NAV state that
  sizing or modelled fills produce, including implementation costs.
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
            target_notional: dict[str, float], prices: dict[str, float] | None = None) -> dict[str, float]:
    """The portfolio that results if this strategy moves to ``target_notional``."""
    resulting = dict(ledger.symbol_exposures_at(prices) if prices is not None else ledger.symbol_exposures())
    sleeve = ledger.sleeve_exposures_at(strategy_id, prices) if prices is not None else ledger.sleeve_exposures(strategy_id)
    for symbol, value in sleeve.items():
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
             limits: RiskLimits, prices: dict[str, float] | None = None) -> dict[str, Any]:
    """Decide on the proposal and return the exact scaled target approved."""
    nav = ledger.nav_at(prices) if prices is not None else ledger.nav
    drawdown = nav / max(ledger.state.peak_nav, ledger.state.initial_capital) - 1.0
    initial = ledger.state.initial_capital

    proposed = assess(project(ledger, strategy_id, target_notional, prices), nav, drawdown,
                      limits, initial)

    cap = 1.0
    if limits.drawdown_halt < drawdown <= limits.drawdown_throttle:
        cap = limits.throttle_scale

    def within_gross(candidate: float) -> bool:
        portfolio = project(ledger, strategy_id,
                            {symbol: value * candidate
                             for symbol, value in target_notional.items()}, prices)
        gross = sum(abs(value) for value in portfolio.values())
        return (gross / nav if nav else 0.0) <= limits.max_gross_ratio + 1e-12

    if within_gross(cap):
        scale = cap
    elif not within_gross(0.0):
        scale = 0.0
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
    final = assess(project(ledger, strategy_id, scaled, prices), nav, drawdown, limits, initial)

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
                 limits: RiskLimits, prices: dict[str, float] | None = None,
                 nav_adjustment: float = 0.0) -> dict[str, Any]:
    """Re-check the exact post-fill portfolio before it is committed to Book.

    ``executed_notional`` must already be final quantity multiplied by the one
    valuation vector supplied in ``prices``. ``nav_adjustment`` carries cash-only
    implementation frictions (currently commissions) that Book will deduct when
    the fills are applied, so a floor/drawdown check cannot approve a NAV that
    will not exist after booking.
    """
    nav = (ledger.nav_at(prices) if prices is not None else ledger.nav) + nav_adjustment
    drawdown = nav / max(ledger.state.peak_nav, ledger.state.initial_capital) - 1.0
    verdict = assess(project(ledger, strategy_id, executed_notional, prices), nav,
                     drawdown, limits, ledger.state.initial_capital)
    return {"approved": not verdict["violations"], "vetoes": verdict["violations"],
            "gross_ratio": verdict["gross_ratio"], "net_ratio": verdict["net_ratio"],
            "largest_symbol_ratio": verdict["largest_symbol_ratio"],
            "checks": verdict["checks"], "nav": nav, "drawdown": drawdown}

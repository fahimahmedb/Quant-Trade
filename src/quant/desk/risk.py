"""RISK: portfolio-context evaluation.

``OPERATING_MODEL.md``: RISK "may reject the proposal even when the candidate
itself is credible". These limits are about the Book, not about the signal, so
they are evaluated against the portfolio the fills would produce rather than
against the opportunity in isolation.
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


def evaluate(ledger: Ledger, target_notional: dict[str, float],
             limits: RiskLimits) -> dict[str, Any]:
    """Judge the post-trade portfolio. Returns a verdict, a scale and the reasons."""
    nav = ledger.nav
    vetoes: list[str] = []
    scale = 1.0
    drawdown = ledger.drawdown

    if nav <= ledger.state.initial_capital * limits.min_nav_ratio:
        vetoes.append(f"NAV {nav:,.0f} is below the {limits.min_nav_ratio:.0%} floor of "
                      f"initial capital")
    if drawdown <= limits.drawdown_halt:
        vetoes.append(f"drawdown {drawdown:.2%} breaches the halt level "
                      f"{limits.drawdown_halt:.0%}")
    elif drawdown <= limits.drawdown_throttle:
        scale = limits.throttle_scale

    scaled = {symbol: value * scale for symbol, value in target_notional.items()}
    # Positions the desk is not proposing to change stay in the portfolio, so the
    # limits are checked against the whole resulting book, not the new legs alone.
    resulting = {position["symbol"]: position["market_value"]
                 for position in ledger.open_positions()}
    resulting.update(scaled)
    resulting = {symbol: value for symbol, value in resulting.items() if abs(value) > 1e-9}

    gross = sum(abs(value) for value in resulting.values())
    net = sum(resulting.values())
    gross_ratio = gross / nav if nav else 0.0
    net_ratio = net / nav if nav else 0.0
    largest = max((abs(value) / nav for value in resulting.values()), default=0.0) if nav else 0.0

    if gross_ratio > limits.max_gross_ratio:
        if gross_ratio > 0:
            scale *= limits.max_gross_ratio / gross_ratio
    if abs(net_ratio) > limits.max_net_ratio:
        vetoes.append(f"net exposure {net_ratio:+.2%} exceeds the "
                      f"{limits.max_net_ratio:.0%} neutrality limit")
    if largest > limits.max_symbol_ratio:
        vetoes.append(f"largest single-name weight {largest:.2%} exceeds "
                      f"{limits.max_symbol_ratio:.0%}")

    checks = {
        "nav_above_floor": nav > ledger.state.initial_capital * limits.min_nav_ratio,
        "drawdown_within_halt": drawdown > limits.drawdown_halt,
        "gross_within_limit": gross_ratio <= limits.max_gross_ratio or scale < 1.0,
        "net_within_neutrality": abs(net_ratio) <= limits.max_net_ratio,
        "concentration_within_limit": largest <= limits.max_symbol_ratio,
    }
    return {"approved": not vetoes, "scale": scale, "vetoes": vetoes, "checks": checks,
            "drawdown": drawdown, "gross_ratio": gross_ratio, "net_ratio": net_ratio,
            "largest_symbol_ratio": largest, "nav": nav,
            "throttled": scale < 1.0, "limits": limits.to_dict()}

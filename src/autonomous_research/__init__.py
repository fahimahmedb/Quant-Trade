"""Small, auditable primitives for the autonomous research loop."""

from .pipeline import run_discovery_cycle
from .ticket import ResearchTicket

__all__ = ["ResearchTicket", "run_discovery_cycle"]

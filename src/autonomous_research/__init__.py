"""Small, auditable primitives for the autonomous research loop."""

from .pipeline import run_discovery_cycle
from .runtime import CampaignRuntime, ResearchTask, TaskOutcome
from .ticket import ResearchTicket

__all__ = [
    "CampaignRuntime", "ResearchTask", "ResearchTicket", "TaskOutcome",
    "run_discovery_cycle",
]

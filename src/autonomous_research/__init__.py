"""Small, auditable primitives for the autonomous research loop."""

from .pipeline import run_discovery_cycle
from .orchestrator import ResearchCampaign
from .runtime import CampaignState, PersistentQueue, ResearchTask
from .ticket import ResearchTicket

__all__ = ["CampaignState", "PersistentQueue", "ResearchCampaign", "ResearchTask",
           "ResearchTicket", "run_discovery_cycle"]

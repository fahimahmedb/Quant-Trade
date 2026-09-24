"""Fast lane ``QUANT_FASTLANE_HPIT_V1`` (historical point-in-time validation).

Weeks 0-2 scope: firewall, SEC insider data ingestion, outcome-blind census,
price-vendor interface, friction functions and pre-registration tooling.
Nothing in this package reads prices or returns without a sealed
pre-registration grant, and no price vendor is wired yet.
"""

from quant.fastlane.firewall import FROZEN_LINEAGE_ID, LINEAGE_ID  # noqa: F401

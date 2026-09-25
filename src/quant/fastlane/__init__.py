"""Fast lane ``QUANT_FASTLANE_HPIT_V1`` (historical point-in-time validation).

Weeks 0-2 scope: firewall, SEC insider data ingestion, outcome-blind census,
price-vendor interface, friction functions and pre-registration tooling.
Evaluation engine (sealed protocol): ``evaluation`` (calendar-time portfolio),
``inference`` (block bootstrap, fixed-b HAC, DSR, Holm, Romano-Wolf),
``screen`` (discovery/walk-forward screen, trial records, holdout request) and
``verdict`` (GO / INCONCLUSIVE / NO_GO and the one holdout look).
Nothing in this package reads prices or returns without a sealed
pre-registration grant, and no price vendor is wired yet.
"""

from quant.fastlane.firewall import FROZEN_LINEAGE_ID, LINEAGE_ID  # noqa: F401

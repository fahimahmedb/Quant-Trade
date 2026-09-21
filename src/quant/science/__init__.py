"""Scientific protocol objects: what is frozen, made executable.

This package implements decisions that are already closed in ``governance/`` and
parameterises the dimensions those artifacts leave explicitly open. It decides
nothing: an undeclared open dimension yields an ``UNRESOLVED`` state, never a
default that would quietly select a geometry.
"""

from .eligibility import (QualifyingEvent, qualifying_events, qualifying_owner,
                          qualifying_transaction)
from .formation import (FORMATION_UNRESOLVED, GeometryChoice, O1_ADMISSIBLE,
                        O3Convention, SessionCalendar, ExposureInterval, FormationEngine,
                        FormationEvent, QualifyingObservation)
from .inference import (MultiplicityBudget, RatioEstimate, StatisticalEconomicVerdict,
                        cluster_bootstrap_ratio, ratio_estimate,
                        statistical_economic_verdict)
from .invariance import (AMBIGUOUS_EMBARGO, CLAIM_DESIGN_SENSITIVE, DESIGN_INVARIANT,
                         admissible_geometries, design_invariance)
from .nulls import (NullDraws, cluster_sign_flip_null, empirical_p_value, placebo_null,
                    placebo_offsets)
from .regimes import RegimeBreakdown, RegimePartition, regime_breakdown

__all__ = ["AMBIGUOUS_EMBARGO", "CLAIM_DESIGN_SENSITIVE", "DESIGN_INVARIANT",
    "ExposureInterval", "FORMATION_UNRESOLVED", "FormationEngine", "FormationEvent",
    "GeometryChoice", "MultiplicityBudget", "NullDraws", "O1_ADMISSIBLE", "O3Convention",
    "QualifyingEvent", "QualifyingObservation", "RatioEstimate", "RegimeBreakdown",
    "RegimePartition", "SessionCalendar", "StatisticalEconomicVerdict",
    "admissible_geometries", "cluster_bootstrap_ratio", "cluster_sign_flip_null",
    "design_invariance", "empirical_p_value", "placebo_null", "placebo_offsets",
    "qualifying_events", "qualifying_owner", "qualifying_transaction", "ratio_estimate",
    "regime_breakdown", "statistical_economic_verdict"
]

"""P0 hybrid qualification harness.

External, non-intrusive tooling that exercises the frozen Gate A v4 candidate
(``blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072``)
without modifying its production/acquisition semantics.

This package implements the mission described in
``handoff/BUILDER_P0_HYBRID_QUALIFICATION_MISSION_2026-09-20.md``: a
reproducible qualification system spanning Gate A (accelerated repository/
fault proof), Gate B (target-host entrance tooling), Gate C (event-based live
window planner + continuity verifier) and Gate D (final evidence binder).

Nothing here declares t0, amends P14D governance, or claims target-host or
live-source evidence from repository execution. Every module that could be
mistaken for such a claim says so explicitly in its output.
"""

from __future__ import annotations

FROZEN_CANDIDATE_SHA = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
FROZEN_CANDIDATE_REF = "blue/p0-gate-a-v4-frozen-2026-09-20"
BUILDER_IMPLEMENTATION_SHA = "0bdd397d7409b01529c1f958c68781499679a95e"

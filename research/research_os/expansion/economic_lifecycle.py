"""Canonical Wave-2 C2 adapter for the qualified MEGA D0 lifecycle kernel.

The qualified D0 implementation was produced from historical builder base
97165db2faa3300cef1f23de0045ed93d25eb9cb. C2 preserves that implementation
verbatim in ``_economic_lifecycle_d0`` and rebinds its single embedded Wave-2
base identity to canonical immutable base law before any public API is used.

This is an internal compatibility adapter, not a second lifecycle engine.
"""
from __future__ import annotations

from . import _economic_lifecycle_d0 as _impl

_SOURCE_D0_BUILDER_BASE_SHA = "97165db2faa3300cef1f23de0045ed93d25eb9cb"
WAVE2_IMMUTABLE_BASE_SHA = "2b99d8aeb8a342f1ef32544247d366cb8a26037e"

if _impl.WAVE2_IMMUTABLE_BASE_SHA != _SOURCE_D0_BUILDER_BASE_SHA:
    raise RuntimeError(
        "unexpected MEGA D0 source base; semantic adapter must be requalified"
    )

# D0 functions resolve this module global at call time. Rebinding here adapts
# the qualified implementation to canonical C2 base law without altering its
# lifecycle, authority, evidence, or state-machine semantics.
_impl.WAVE2_IMMUTABLE_BASE_SHA = WAVE2_IMMUTABLE_BASE_SHA

for _name in dir(_impl):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_impl, _name)

# Keep the public canonical value explicit even if source internals evolve.
WAVE2_IMMUTABLE_BASE_SHA = "2b99d8aeb8a342f1ef32544247d366cb8a26037e"
C2_D0_INTERNAL_ADAPTER = True

# Public reference admission must prove explicit closed evidence. The preserved
# kernel's optional-field guard remains appropriate for generic diagnostics,
# but absence in a serialized canonical reference is not a FALSE observation.
_source_validate_economic_identity_ref = _impl.validate_economic_identity_ref
_source_validate_portfolio_readiness_ref = _impl.validate_portfolio_readiness_ref


def validate_economic_identity_ref(ref):
    _source_validate_economic_identity_ref(ref)
    for key in ("outcome_accessed", "empirical_return_data_consumed"):
        if ref.get(key) is not False:
            raise ValueError(f"EconomicIdentityRef.{key} must be explicitly false")


def validate_portfolio_readiness_ref(ref, identity_ref):
    _source_validate_portfolio_readiness_ref(ref, identity_ref)
    for key in (*AUTHORITY_STATE, "return_series_consumed"):
        if ref.get(key) is not False:
            raise ValueError(f"PortfolioReadinessRef.{key} must be explicitly false")


_impl.validate_economic_identity_ref = validate_economic_identity_ref
_impl.validate_portfolio_readiness_ref = validate_portfolio_readiness_ref

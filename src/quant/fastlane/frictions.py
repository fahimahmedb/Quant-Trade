"""Friction model for ``QUANT_FASTLANE_HPIT_V1`` (pure functions).

Every numeric parameter comes from the protocol's ``frictions`` section via
:class:`FrictionParams.from_protocol`; nothing economic is a buried constant.

* Spread: Abdi & Ranaldo (2017, RFS 30(12)) close-high-low estimator,
  ``s_t^2 = 4 (c_t - eta_t)(c_t - eta_{t+1})`` with log close ``c`` and log
  mid-range ``eta = (log H + log L) / 2``, floored by an ADV20 bucket.
* Commission: per share with a minimum (and an optional cap as a fraction of
  notional).
* Impact: square-root law ``Y * sigma_daily * sqrt(Q / ADV20)``.
* Participation: notional capped at ``cap * ADV20`` (0.1 % in D5); a name
  whose ADV20 is below the untradeable threshold is skipped.
* Delisting: vendor-agnostic classes with base/stress extra returns.
* Stress: all friction costs times the protocol multiplier (reported, not gating).

The values live in the protocol and are frozen from literature/engineering;
they are never calibrated on the data being evaluated.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


def _finite(name: str, value: float, *, positive: bool = False, nonneg: bool = False) -> float:
    if value is None or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    if positive and value <= 0:
        raise ValueError(f"{name} must be > 0, got {value}")
    if nonneg and value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return float(value)


@dataclass(frozen=True)
class SpreadBucket:
    adv_below_usd: float | None      # None = open upper bucket
    floor_bps: float


@dataclass(frozen=True)
class FrictionParams:
    spread_variant: str
    spread_min_pairs: int
    spread_buckets: tuple[SpreadBucket, ...]
    commission_per_share_usd: float
    commission_minimum_usd: float
    commission_max_fraction_of_notional: float | None
    impact_coefficient: float
    participation_cap_adv20: float
    untradeable_adv20_below_usd: float
    stress_multiplier: float
    delisting_classes: Mapping[str, Mapping[str, float]]

    @classmethod
    def from_protocol(cls, frictions: Mapping[str, Any]) -> "FrictionParams":
        spread = frictions["spread"]
        buckets = tuple(SpreadBucket(None if b["adv_below_usd"] is None
                                     else _finite("adv_below_usd", b["adv_below_usd"], positive=True),
                                     _finite("floor_bps", b["floor_bps"], nonneg=True))
                        for b in spread["adv20_bucket_floor_bps"])
        bounds = [b.adv_below_usd for b in buckets]
        if not bounds or bounds[-1] is not None or any(x is None for x in bounds[:-1]):
            raise ValueError("spread buckets must end with exactly one open (null) bucket")
        finite = bounds[:-1]
        if any(b <= a for a, b in zip(finite, finite[1:])):
            raise ValueError("spread bucket bounds must increase")
        commission = frictions["commission"]
        cap = commission.get("max_fraction_of_notional")
        from quant.fastlane.prices import DELISTING_CLASSES
        delist = frictions["delisting_classes"]
        if sorted(delist) != sorted(DELISTING_CLASSES):
            raise ValueError(f"delisting classes must be exactly {DELISTING_CLASSES}")
        stress = frictions["stress"]
        if stress.get("gating") is not False:
            raise ValueError("friction stress is reported, never gating")
        return cls(
            spread_variant=spread["variant"],
            spread_min_pairs=int(spread["min_pairs"]),
            spread_buckets=buckets,
            commission_per_share_usd=_finite("per_share_usd", commission["per_share_usd"], nonneg=True),
            commission_minimum_usd=_finite("minimum_usd", commission["minimum_usd"], nonneg=True),
            commission_max_fraction_of_notional=None if cap is None else _finite(
                "max_fraction_of_notional", cap, positive=True),
            impact_coefficient=_finite("impact coefficient", frictions["impact"]["coefficient"],
                                       nonneg=True),
            participation_cap_adv20=_finite("participation_cap_adv20",
                                            frictions["participation_cap_adv20"], positive=True),
            untradeable_adv20_below_usd=_finite("untradeable_adv20_below_usd",
                                                frictions["untradeable_adv20_below_usd"],
                                                nonneg=True),
            stress_multiplier=_finite("stress multiplier", stress["multiplier"], positive=True),
            delisting_classes={c: {"base": _finite(f"{c} base", delist[c]["base"]),
                                   "stress": _finite(f"{c} stress", delist[c]["stress"])}
                               for c in DELISTING_CLASSES},
        )


# --- spread --------------------------------------------------------------------

def abdi_ranaldo_spread(high: Sequence[float], low: Sequence[float], close: Sequence[float],
                        *, variant: str, min_pairs: int) -> float | None:
    """Proportional effective-spread estimate over one window, or None if too short.

    ``variant``:
    * ``"two_day_corrected_mean"``: mean over t of sqrt(max(s_t^2, 0));
    * ``"pooled"``: sqrt(max(mean(s_t^2), 0)).
    """
    n = len(close)
    if not (len(high) == len(low) == n):
        raise ValueError("high, low and close must have equal length")
    for i in range(n):
        h = _finite("high", high[i], positive=True)
        lo = _finite("low", low[i], positive=True)
        c = _finite("close", close[i], positive=True)
        if lo > h:
            raise ValueError(f"low {lo} > high {h} at {i}")
        if not (lo <= c <= h):
            raise ValueError(f"close {c} outside [low, high] at {i}")
    if n - 1 < min_pairs:
        return None
    eta = [(math.log(high[i]) + math.log(low[i])) / 2.0 for i in range(n)]
    logc = [math.log(close[i]) for i in range(n)]
    squares = [4.0 * (logc[t] - eta[t]) * (logc[t] - eta[t + 1]) for t in range(n - 1)]
    if variant == "two_day_corrected_mean":
        return sum(math.sqrt(max(s, 0.0)) for s in squares) / len(squares)
    if variant == "pooled":
        return math.sqrt(max(sum(squares) / len(squares), 0.0))
    raise ValueError(f"unknown Abdi-Ranaldo variant {variant!r}")


def spread_floor(adv20_usd: float, buckets: Sequence[SpreadBucket]) -> float:
    adv = _finite("adv20_usd", adv20_usd, positive=True)
    for bucket in buckets:
        if bucket.adv_below_usd is None or adv < bucket.adv_below_usd:
            return bucket.floor_bps / 10_000.0
    raise ValueError("no spread bucket matched")


def effective_spread(ar_spread: float | None, adv20_usd: float, params: FrictionParams) -> float:
    """max(Abdi-Ranaldo estimate, ADV-bucket floor); floor only if the estimate is missing."""
    floor = spread_floor(adv20_usd, params.spread_buckets)
    if ar_spread is None:
        return floor
    return max(_finite("ar_spread", ar_spread, nonneg=True), floor)


def half_spread_cost_usd(notional_usd: float, spread: float) -> float:
    return _finite("notional", notional_usd, nonneg=True) * _finite("spread", spread, nonneg=True) / 2.0


# --- commission ------------------------------------------------------------------

def commission_usd(shares: float, notional_usd: float, params: FrictionParams) -> float:
    shares = _finite("shares", shares, nonneg=True)
    notional = _finite("notional", notional_usd, nonneg=True)
    if shares == 0:
        return 0.0
    fee = max(params.commission_per_share_usd * shares, params.commission_minimum_usd)
    if params.commission_max_fraction_of_notional is not None:
        fee = min(fee, params.commission_max_fraction_of_notional * notional)
    return fee


# --- impact and participation --------------------------------------------------------

def sqrt_impact_fraction(notional_usd: float, adv20_usd: float, daily_volatility: float,
                         coefficient: float) -> float:
    notional = _finite("notional", notional_usd, nonneg=True)
    adv = _finite("adv20_usd", adv20_usd, positive=True)
    sigma = _finite("daily_volatility", daily_volatility, nonneg=True)
    return _finite("coefficient", coefficient, nonneg=True) * sigma * math.sqrt(notional / adv)


def participation_capped_notional(target_notional_usd: float, adv20_usd: float,
                                  cap_fraction: float) -> float:
    target = _finite("target_notional", target_notional_usd, nonneg=True)
    adv = _finite("adv20_usd", adv20_usd, positive=True)
    return min(target, _finite("cap_fraction", cap_fraction, positive=True) * adv)


def is_tradeable(adv20_usd: float, params: FrictionParams) -> bool:
    return _finite("adv20_usd", adv20_usd, nonneg=True) >= params.untradeable_adv20_below_usd


def one_side_cost_usd(notional_usd: float, shares: float, adv20_usd: float,
                      daily_volatility: float, ar_spread: float | None,
                      params: FrictionParams, *, stress: bool = False,
                      require_tradeable: bool = True) -> dict:
    """Cost of one leg. ``require_tradeable=False`` is for exit legs only: a held
    position must still be closed (and pay frictions) if its ADV20 fell below the
    untradeable threshold after entry."""
    if require_tradeable and not is_tradeable(adv20_usd, params):
        raise ValueError(f"ADV20 {adv20_usd} is below the untradeable threshold")
    spread = effective_spread(ar_spread, adv20_usd, params)
    half = half_spread_cost_usd(notional_usd, spread)
    fee = commission_usd(shares, notional_usd, params)
    impact = notional_usd * sqrt_impact_fraction(notional_usd, adv20_usd, daily_volatility,
                                                 params.impact_coefficient)
    scale = params.stress_multiplier if stress else 1.0
    return {"spread": spread, "half_spread_usd": half * scale, "commission_usd": fee * scale,
            "impact_usd": impact * scale, "total_usd": (half + fee + impact) * scale,
            "stress": stress}


def delisting_extra_return(delisting_class: str, scenario: str, params: FrictionParams) -> float:
    """Extra return applied after the last traded price, by delisting class."""
    try:
        return params.delisting_classes[delisting_class][scenario]
    except KeyError as exc:
        raise ValueError(f"no delisting treatment for {delisting_class!r}/{scenario!r}") from exc

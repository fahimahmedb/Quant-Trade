"""Draft (unsealed) protocol for ``QUANT_FASTLANE_HPIT_V1`` built from the census.

The draft encodes D5 of ``handoff/CLAUDE_DELEGATED_DECISIONS_AND_PLAN_2026-09-23.md``
plus the lead's repair-round decisions, and a variant grid chosen *only* from
outcome-blind event counts (which include holdout-period counts; disclosed in
the protocol). It is written with ``status = DRAFT_NOT_SEALED``;
:func:`quant.fastlane.preregistration.seal_protocol` refuses it until an
explicit decision flips it to ``FINAL_FOR_SEAL``. With that single flip the
draft passes the full seal validation (``open_decisions == []``).

Power (audit convention: sigma of a 20-session excess return 14 %, design
effect 1.5, one-sided alpha 0.05, power 80 %):

* per-event MDE ``(z_a + z_b) * sigma_h * sqrt(deff / N_eff)``, ``N_eff``
  capped by slot capacity ``K * 252 / h`` per year;
* annualized portfolio MDE on invested capital with a common-factor tracking
  error vs SPY: ``(z_a + z_b) * hypot(sigma_idio, TE) / sqrt(years)`` with
  ``sigma_idio = sigma_daily * sqrt(252 * deff / K_avg)`` and TE = 8 %/yr.
"""

from __future__ import annotations

import copy
import math
from statistics import NormalDist
from typing import Any, Mapping

from quant.fastlane import events as ev
from quant.fastlane.firewall import LINEAGE_ID, Firewall
from quant.fastlane.frictions import FrictionParams
from quant.fastlane.preregistration import (BOOTSTRAP_SEED, FROZEN_SPREAD_FLOORS,
                                            ROBUSTNESS_SEEDS, SPLITS, STATUS_DRAFT,
                                            protocol_sha256, validate_protocol)

SIGMA_20D = 0.14
DESIGN_EFFECT = 1.5
TRACKING_ERROR = 0.08
ALPHA_ONE_SIDED = 0.05
POWER = 0.80
HOLDOUT_YEARS = 5.0

GRID_FAMILIES = {
    "OD": ("OD", "issuer-day value of primary accessions with >=1 officer/director owner"),
    "CEO_CFO": ("CEO_CFO", "issuer-day value of primary accessions with >=1 CEO/CFO owner"),
    "FROZEN_FV_10S": ("FROZEN_FV_PROXY_10WD",
                      "sum of O/D accession values in the 10-session formation window at the "
                      "crossing; census counts use the weekday proxy, evaluation uses exact "
                      "vendor sessions and literal distinct CIKs (D07 2.1)"),
}
GRID_VALUE_FLOORS = (("V10K", 10_000.0, "ge_10k"), ("V100K", 100_000.0, "ge_100k"),
                     ("V1M", 1_000_000.0, "ge_1m"))
GRID_HORIZONS = (5, 20, 60)
# The literal frozen D07 cell: no value floor, 20-session hold.
LITERAL_FROZEN_CELL = ("FROZEN_FV_10S", "V0", 0.0, None, 20)
MIN_EVENTS_PER_YEAR_EACH_SPLIT = 50.0
MIN_HOLDOUT_CONCURRENT_POSITIONS = 20.0

CONSTRUCTOR = {
    "id": "FASTLANE_SLOTK_ADV20_V1",
    "C0_usd": 100_000.0,
    "slots": 100,
    "book": "paper only",
    "slot_target_notional": "C0 / slots",
    "allocation": "a_j = min(C0/slots, participation_cap_adv20 * ADV20_j); ADV20 = mean of "
                  "raw_close*raw_volume over the 20 completed vendor sessions before entry; "
                  "ADV20 below frictions.untradeable_adv20_below_usd -> skipped (counted)",
    "order": "entries are processed by (entry_session, tie_break); the lowest free slot is "
             "taken; an issuer with an active slot or a full book gets a_j = 0 (reason logged)",
    "tie_break": "sha256(utf8(str(inference.bootstrap_seed) + '|' + ','.join(sorted("
                 "accessions of the issuer-day)))) ascending hex "
                 "(quant.fastlane.constructor.tie_break_key); never issuer CIK",
    "slot_release": "time-based at the scheduled exit close; never early on gain, loss or "
                    "delisting",
    "no_recycling": "realized P&L is not recycled into C0",
}

FRICTIONS = {
    "provenance": "frozen from literature/engineering choices; NOT calibrated on the data "
                  "being evaluated",
    "spread": {
        "estimator": "ABDI_RANALDO_2017_CHL",
        "variant": "two_day_corrected_mean",
        "window_sessions": 21,
        "min_pairs": 15,
        "adv20_bucket_floor_bps": [dict(b) for b in FROZEN_SPREAD_FLOORS],
        "effective": "max(Abdi-Ranaldo estimate over the 21 sessions before the leg, "
                     "ADV20-bucket full-spread floor); cost per side = half of it",
    },
    "untradeable_adv20_below_usd": 100_000.0,
    "commission": {"per_share_usd": 0.0035, "minimum_usd": 0.35,
                   "max_fraction_of_notional": None},
    "impact": {"model": "SQUARE_ROOT", "coefficient": 1.0,
               "formula": "k * sigma_daily * sqrt(Q / ADV20)",
               "volatility": "stdev of daily log close-to-close over the 20 sessions before "
                             "the leg"},
    "participation_cap_adv20": 0.001,
    "delisting_classes": {
        "CASH_ACQUISITION": {"base": 0.0, "stress": 0.0},
        "STOCK_MERGER": {"base": 0.0, "stress": 0.0},
        "BANKRUPTCY_OR_CAUSE": {"base": -1.0, "stress": -1.0},
        "UNKNOWN": {"base": -0.30, "stress": -1.0},
    },
    "stress": {"multiplier": 2.0, "gating": False,
               "rule": "all friction costs x2, reported alongside; never part of GO"},
}


def _z(p: float) -> float:
    return NormalDist().inv_cdf(p)


def per_event_mde(n_events: float, horizon: int, *, sigma20: float = SIGMA_20D,
                  deff: float = DESIGN_EFFECT, alpha: float = ALPHA_ONE_SIDED,
                  power: float = POWER) -> float | None:
    if n_events <= 0:
        return None
    sigma_h = sigma20 * math.sqrt(horizon / 20.0)
    return (_z(1 - alpha) + _z(power)) * sigma_h * math.sqrt(deff / n_events)


def portfolio_mde_annual(k_avg: float, years: float, *, tracking_error: float = TRACKING_ERROR,
                         sigma20: float = SIGMA_20D, deff: float = DESIGN_EFFECT,
                         alpha: float = ALPHA_ONE_SIDED, power: float = POWER) -> float | None:
    if k_avg <= 0 or years <= 0:
        return None
    sigma_daily = sigma20 / math.sqrt(20.0)
    idio = sigma_daily * math.sqrt(252.0 * deff / k_avg)
    return (_z(1 - alpha) + _z(power)) * math.hypot(idio, tracking_error) / math.sqrt(years)


def variant_power(rate_per_year: float, horizon: int, slots: int, years: float = HOLDOUT_YEARS,
                  alpha: float = ALPHA_ONE_SIDED) -> dict:
    capacity_per_year = slots * 252.0 / horizon
    n_eff = min(rate_per_year, capacity_per_year) * years
    k_avg = min(float(slots), rate_per_year * horizon / 252.0)
    return {
        "holdout_rate_per_year": rate_per_year,
        "slot_capacity_entries_per_year": round(capacity_per_year, 1),
        "holdout_traded_events_upper_bound": round(n_eff),
        "avg_concurrent_positions": round(k_avg, 1),
        "per_event_mde_bp": _bp(per_event_mde(n_eff, horizon, alpha=alpha)),
        "portfolio_mde_annual_pct": _pct(portfolio_mde_annual(k_avg, years, alpha=alpha)),
        "portfolio_mde_annual_pct_no_te": _pct(portfolio_mde_annual(k_avg, years, alpha=alpha,
                                                                    tracking_error=0.0)),
    }


def _bp(x: float | None) -> float | None:
    return None if x is None else round(x * 10_000.0, 1)


def _pct(x: float | None) -> float | None:
    return None if x is None else round(x * 100.0, 2)


def audit_table_check() -> dict:
    """Reproduce the audit's §4.2 per-event table (5-year holdout, no slot cap)."""
    return {str(rate): _bp(per_event_mde(rate * HOLDOUT_YEARS, 20))
            for rate in (300, 500, 1000, 2000)}


def _cells():
    for fam_id in GRID_FAMILIES:
        for tier_id, floor, tier_key in GRID_VALUE_FLOORS:
            for horizon in GRID_HORIZONS:
                yield fam_id, tier_id, floor, tier_key, horizon
    yield LITERAL_FROZEN_CELL


def build_grid(census: Mapping[str, Any], slots: int) -> tuple[list[dict], list[dict]]:
    variants, excluded = [], []
    for fam_id, tier_id, floor, tier_key, horizon in _cells():
        census_family, value_basis = GRID_FAMILIES[fam_id]
        rates = {}
        for split in SPLITS:
            m = census["by_split"][split][census_family]
            rates[split] = m["per_year"] if tier_key is None else m["value_tiers_per_year"][tier_key]
        vid = f"{fam_id}_{tier_id}_H{horizon}"
        power = variant_power(rates["holdout"], horizon, slots)
        power_holm = variant_power(rates["holdout"], horizon, slots, alpha=ALPHA_ONE_SIDED / 3)
        reasons = []
        low = [s for s, r in rates.items() if r < MIN_EVENTS_PER_YEAR_EACH_SPLIT]
        if low:
            reasons.append(f"fewer than {MIN_EVENTS_PER_YEAR_EACH_SPLIT:.0f} issuer-days/yr in {low}")
        if power["avg_concurrent_positions"] < MIN_HOLDOUT_CONCURRENT_POSITIONS:
            reasons.append(f"holdout average concurrent positions "
                           f"{power['avg_concurrent_positions']} < "
                           f"{MIN_HOLDOUT_CONCURRENT_POSITIONS:.0f}")
        row = {
            "variant_id": vid,
            "family": fam_id,
            "census_family": census_family,
            "literal_frozen_d07_cell": (fam_id, tier_id, horizon) == ("FROZEN_FV_10S", "V0", 20),
            "value_floor_usd": floor,
            "value_basis": value_basis,
            "horizon_sessions": horizon,
            "exit": f"regular close of vendor session e+{horizon - 1} "
                    f"({horizon} sessions including entry session e)",
            "census_issuer_days_per_year": rates,
            "power_one_sided_0p05": power,
            "power_holm_first_step_0p0167": {
                "per_event_mde_bp": power_holm["per_event_mde_bp"],
                "portfolio_mde_annual_pct": power_holm["portfolio_mde_annual_pct"]},
        }
        if reasons:
            excluded.append({"variant_id": vid, "reasons": reasons,
                             "census_issuer_days_per_year": rates,
                             "avg_concurrent_positions": power["avg_concurrent_positions"]})
        else:
            variants.append(row)
    return variants, excluded


def build_protocol(census: Mapping[str, Any], census_sha256: str,
                   governance_sha256: Mapping[str, str | None]) -> dict:
    slots = int(CONSTRUCTOR["slots"])
    variants, excluded = build_grid(census, slots)
    FrictionParams.from_protocol(FRICTIONS)  # fail early if the section is malformed
    splits = {
        "discovery": {"price_window": {"start": "2005-10-01", "end": "2018-12-31"},
                      "role": "screen and rank all declared variants"},
        "walk_forward": {"price_window": {"start": "2018-10-01", "end": "2021-06-30"},
                         "role": "out-of-sample check of the discovery ranking; no re-tuning"},
        "holdout": {"price_window": {"start": "2021-04-01", "end": "2026-09-30"},
                    "role": "sealed, one look, <=3 finalists"},
    }
    for name, (start, end) in SPLITS.items():
        splits[name].update({"start": start.isoformat(), "end": end.isoformat(),
                             "assignment": "by available_after_date (FILING_DATE)"})
    k20 = portfolio_mde_annual(20, HOLDOUT_YEARS)
    k100 = portfolio_mde_annual(100, HOLDOUT_YEARS)
    k100_holm = portfolio_mde_annual(100, HOLDOUT_YEARS, alpha=ALPHA_ONE_SIDED / 3)
    literal = next((v for v in variants if v["literal_frozen_d07_cell"]), None)
    return {
        "lineage": LINEAGE_ID,
        "protocol_version": "1.1-draft",
        "status": STATUS_DRAFT,
        "open_decisions": [],
        "evidence_class_target": "HISTORICAL_PIT_VALIDATION (D6, pending ratification)",
        "authority": {
            "decisions": "handoff/CLAUDE_DELEGATED_DECISIONS_AND_PLAN_2026-09-23.md §D5-D6 plus "
                         "the lead's repair-round decisions (2026-09-24)",
            "design": "handoff/CLAUDE_PROJECT_REVIEW_AUDIT_2026-09-23.md §4",
            "frozen_signal_definition": "governance/D07_OPEN_SPACE_BOUNDARY.md §2.1-2.3",
            "source_sha256": dict(governance_sha256),
        },
        "census_binding": {
            "census_sha256": census_sha256,
            "events_sha256": census["inputs"]["events_sha256"],
            "events_relpath": census["inputs"]["events_relpath"],
            "events_rows": census["inputs"]["events_rows"],
            "sec_manifest_set_fingerprint": census["inputs"]["sec_manifest_set_fingerprint"],
            "grant_time_check": "require_outcome_access recomputes the sha256 of events_relpath "
                                "and refuses on mismatch",
            "grid_selection_disclosure": "the variant grid and its adequacy screen were chosen "
                                         "from outcome-blind event COUNTS that include "
                                         "holdout-period (2021-07..2026-06) counts; no outcome "
                                         "of any split was read",
        },
        "population": {
            "source": "SEC Insider Transactions Data Sets (quarterly, 2006Q1 onward), as filed",
            "document_type": "original Form 4 only ('4'); 4/A never creates or modifies an event",
            "rows": "NONDERIV_TRANS with TRANS_CODE 'P' and TRANS_ACQUIRED_DISP_CD 'A'",
            "roles": "relationship flags only; CEO/CFO requires the Officer flag plus a CEO/CFO "
                     "title; titles never promote a role",
            "security_title_include_regex": ev.SECURITY_TITLE_INCLUDE,
            "security_title_include_explicit_regex": ev.SECURITY_TITLE_INCLUDE_EXPLICIT,
            "security_title_exclude_regex": ev.SECURITY_TITLE_EXCLUDE,
            "security_title_unit_exemption_regex": ev.SECURITY_TITLE_UNIT_EXEMPTION,
            "security_title_rule": "upper-cased, whitespace-collapsed title must re.search the "
                                   "include or the explicit-include regex (COMMON UNITS, SHARES OF "
                                   "BENEFICIAL INTEREST, CLASS X [COMMON] STOCK/SHARES, ORDINARY "
                                   "SHARES, bare SHARES / CAPITAL STOCK) and must not re.search "
                                   "the exclude regex, whose UNIT(S) token is waived for COMMON "
                                   "UNIT(S); frozen from title counts only",
            "footnote_exclusion_regex": ev.FOOTNOTE_EXCLUSION,
            "footnote_rule": "a row is excluded if a footnote attached to its security title or "
                             "a transaction field, or the filing REMARKS, matches a category "
                             "(case-insensitive); holdings/ownership footnotes are never scanned",
            "footnote_scanned_columns": list(ev.TRANSACTION_FOOTNOTE_COLUMNS),
            "footnote_never_scanned_columns": list(ev.HOLDINGS_FOOTNOTE_COLUMNS),
            "dedupe": "exact duplicates dropped first-seen by (FILING_DATE, accession) on "
                      "(issuer, sorted owner CIKs, sorted (trans_date, shares, per-share figure))",
            "backdating_exclusion": "accession sequence year > FILING_DATE year -> excluded; "
                                    "residual risk: same-year backdating is undetectable in "
                                    "the data sets",
            "unique_key": "ACCESSION_NUMBER (duplicates are build errors)",
            "entry_event": "issuer CIK x FILING_DATE",
            "unfiltered_role": "the population before title/footnote/dedupe filters is reported "
                               "as sensitivity only and never enters GO",
        },
        "timing": {
            "available_after_date": "FILING_DATE",
            "entry": "open of the first vendor session strictly after available_after_date",
            "calendar": "the licensed price vendor's session list; none is invented",
            "transaction_date": "never used as a public date",
        },
        "splits": splits,
        "purge": "in discovery and walk_forward, events whose scheduled exit session falls "
                 "after the split end are excluded from that split (logged); discovery and "
                 "walk-forward price windows end at their split ends, so no holdout-period "
                 "price is reachable before the one look",
        "security_mapping": {
            "rule": "issuer CIK -> vendor security as of the entry date (vendor PIT tickers "
                    "table with CIK); as-filed ticker is a cross-check only",
            "ambiguous": "multiple common share classes or no mapping -> unresolved, counted, "
                         "never resolved with future prices or current tickers",
            "window": "mapping validity is clipped to the grant's price window",
        },
        "universe_eligibility": {
            "bars": "20 complete vendor bars before entry; finite positive ADV20",
            "untradeable": "ADV20 < USD 100,000 -> skipped (counted)",
            "min_last_close_usd": 1.0,
            "note": "eligibility uses only pre-entry data",
        },
        "constructor": copy.deepcopy(CONSTRUCTOR),
        "execution": {
            "missing_entry_bar": "no vendor bar at the entry session -> no fill; the event is "
                                 "skipped and counted",
            "missing_exit_bar": "no bar at the scheduled exit -> exit at the next available "
                                "open; if none within 20 sessions, apply the delisting "
                                "treatment from the last traded price",
        },
        "return_object": {
            "formula": "r_ex,t = sum_i w_{i,t-1} (r_{i,t} - r_SPY,t) / sum_i w_{i,t-1}",
            "weights": "buy-and-hold weights on INVESTED capital: w_i starts at the entry "
                       "notional a_j and drifts with the position's value; no daily "
                       "rebalancing",
            "idle_cash": "earns 0 %; reported separately as utilization; cash drag is never "
                         "counted as alpha",
            "annualized_alpha": "252 x arithmetic mean of r_ex,t over the split's sessions "
                                "with at least one open position",
            "net": "r_{i,t} net of the frozen frictions at 1x C0 (entry/exit legs booked on "
                   "their sessions); stress 2x reported",
        },
        "inference": {
            "unit": "daily net r_ex,t of the calendar-time portfolio (return_object)",
            "primary_test": "one-sided studentized moving-block bootstrap of mean r_ex (H1: > 0)",
            "block_length_sessions": 80,
            "bootstrap_draws": 10_000,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "co_check": {"test": "fixed-b HAC t-test of mean r_ex, one-sided",
                         "kernel": "Bartlett", "bandwidth_b": 0.1,
                         "critical_values": "Kiefer-Vogelsang (2005) fixed-b",
                         "purpose": "valid with few effective 80-session blocks "
                                    "(~15 in the holdout)"},
            "go_requires": "BOTH the bootstrap and the fixed-b HAC p-values below the Holm "
                           "threshold",
            "seed_robustness": {
                "seeds": list(ROBUSTNESS_SEEDS),
                "gating": False,
                "role": "REPORTING ONLY: the verdict statistics (bootstrap p-values, CI bounds, "
                        "admitted sets) recomputed under seeds seed+1..seed+5 are published "
                        "alongside; they never change the verdict",
            },
            "robustness": "FF5+UMD alpha (robustness only, never GO)",
        },
        "robustness": {
            "ff5_umd_files": [
                "Kenneth R. French Data Library: F-F_Research_Data_5_Factors_2x3_daily_CSV.zip",
                "Kenneth R. French Data Library: F-F_Momentum_Factor_daily_CSV.zip",
            ],
            "snapshot": "downloaded once, sha256 recorded in a committed manifest before the look",
            "role": "robustness only",
        },
        "benchmark": {
            "series": "SPY total return (dividends reinvested) from the licensed vendor",
            "manifest": "research/fastlane/vendor/BENCHMARK_SOURCE.json (lineage, series SPY, "
                        "return_type TOTAL_RETURN, vendor_id, dataset, fallback NONE)",
            "fallback": "NONE",
            "rule": "the exact vendor dataset is recorded in the committed manifest before any "
                    "grant; no other source may substitute",
        },
        "delisting": {
            "classes": {
                "CASH_ACQUISITION": "last traded price, no extra loss",
                "STOCK_MERGER": "last traded price",
                "BANKRUPTCY_OR_CAUSE": "-100 %",
                "UNKNOWN": "-30 % (stress -100 %)",
            },
            "mapping_manifest": "research/fastlane/vendor/DELISTING_CLASS_MAP.json (vendor code "
                                "-> class) with derivation VENDOR_DOCUMENTATION_ONLY and source "
                                "{documentation_url, retrieved_on}; committed AND pushed before "
                                "ANY outcome grant in any split (enforced by "
                                "require_outcome_access)",
            "mapping_source": "VENDOR_DOCUMENTATION_ONLY",
            "vendor_agnostic": True,
        },
        "variant_grid_rule": {
            "families": {k: v[1] for k, v in GRID_FAMILIES.items()},
            "value_floors_usd": [f for _, f, _ in GRID_VALUE_FLOORS],
            "horizons_sessions": list(GRID_HORIZONS),
            "literal_frozen_cell": "FROZEN_FV_10S_V0_H20 (no value floor, 20-session hold) "
                                   "added as the literal D07 cell"
                                   + ("" if literal else "; DROPPED by the adequacy rule"),
            "adequacy": {
                "min_issuer_days_per_year_each_split": MIN_EVENTS_PER_YEAR_EACH_SPLIT,
                "min_holdout_avg_concurrent_positions": MIN_HOLDOUT_CONCURRENT_POSITIONS,
            },
            "M_max": 48,
            "post_eligibility_recheck": "after the discovery/walk-forward grants and before any "
                                        "return is computed, PIT mapping and pre-entry "
                                        "eligibility are applied to DISCOVERY AND WALK-FORWARD "
                                        "events only; a variant whose eligible counts then fail "
                                        "the adequacy rule is dropped and logged, never "
                                        "replaced; holdout eligibility is not inspected before "
                                        "the look",
            "census_caveat": "census counts precede security mapping and liquidity "
                             "eligibility; eligible counts will be lower",
        },
        "variants": variants,
        "excluded_cells": excluded,
        "power": {
            "assumptions": {"sigma_20d": SIGMA_20D, "design_effect": DESIGN_EFFECT,
                            "tracking_error_vs_spy": TRACKING_ERROR,
                            "alpha_one_sided": ALPHA_ONE_SIDED, "power": POWER,
                            "holdout_years": HOLDOUT_YEARS,
                            "sigma_daily": "sigma_20d / sqrt(20)"},
            "audit_table_reproduction_bp": audit_table_check(),
            "portfolio_mde_annual_pct": {"K20": _pct(k20), "K100": _pct(k100),
                                         "K100_holm_first_step": _pct(k100_holm)},
            "reading": "per-event MDE is per trade at horizon h; portfolio MDE is annualized "
                       "on invested capital including 8 %/yr tracking error vs SPY and is the "
                       "relevant scale for the 3 %/yr GO bar; the significance legs, not the "
                       "3 % leg, bind",
        },
        "multiplicity": {
            "M_declared": len(variants),
            "trial_ledger": "var/fastlane/ledgers/trials.jsonl (hash-chained); every evaluated "
                            "variant appended; its head is stored in the committed holdout "
                            "request",
            "dsr": "Deflated Sharpe on discovery with N = N_trials",
            "n_trials_rule": "max(M_declared, trial_ledger_evaluations)",
            "n_trials_context": "N_trials is the multiplicity count for DSR and the Holm context; "
                                "it is recorded in the committed holdout request",
            "all_declared_need_discovery_trials": True,
            "screening_rule": "before a holdout request is accepted, ALL M_declared variants "
                              "must have discovery trial-ledger records (not only finalists)",
            "discovery": "DSR ranking; Romano-Wolf stepdown (Hansen SPA as cross-check) on "
                         "net r_ex",
            "finalist_rule": "top <=3 by discovery DSR among variants with Romano-Wolf p<0.10 "
                             "and positive walk-forward net annualized alpha; finalists must "
                             "have discovery and walk-forward trial-ledger records",
            "max_finalists": 3,
            "holdout": "Holm at family alpha 0.05 over the finalists, applied to both tests",
        },
        "frictions": copy.deepcopy(FRICTIONS),
        "capacity": {"multiples_of_C0": [1, 10, 100],
                     "rule": "same constructor at each multiple with the 0.1% ADV20 cap; "
                             "net annualized alpha reported at each"},
        "outcomes": {
            "go": "all go_criterion legs hold",
            "no_go": "GO fails and the one-sided 95% upper bound of net annualized alpha "
                     "is < 3%/yr; recorded as a result",
            "inconclusive": "GO fails but the one-sided 95% upper bound is >= 3%/yr; logged "
                            "distinctly from NO_GO",
            "zero_finalists": "NO_GO; the holdout stays unopened",
            "inconclusive_upper_bound_min_annual": 0.03,
            "inconclusive_ci_level_one_sided": 0.95,
            "sizing": "neither NO_GO nor INCONCLUSIVE authorizes any sizing",
        },
        "go_criterion": {
            "alpha_min_annual": 0.03,
            "holm_family_alpha": 0.05,
            "dsr_min": 0.95,
            "all_of": [
                "annualized net alpha vs SPY >= 3%/yr at 1x C0 (base delisting)",
                "Holm-adjusted p < 0.05 for BOTH the studentized block bootstrap and the "
                "fixed-b HAC co-check",
                "net result positive at 1x C0 after frictions",
                "DSR > 0.95 (discovery, N = trial-ledger count)",
                "vendor attestation go_eligible (includes delisted, PIT mapping, raw prices "
                "plus actions, verified)",
            ],
            "authority_if_go": "SHADOW_PROVISIONAL paper only (D6 caps); never "
                               "FORWARD_CONFIRMATION or real capital",
        },
        "firewall": {
            "space": "var/fastlane/ (data, ledger caches), research/fastlane/ (committed "
                     "artifacts)",
            "frozen_lineage": "no read/write of FORM4_FIRST_VERTICAL_MULTI_COHORT_V1; its "
                              "cohorts are prospective and were never activated, so the "
                              "2006-2026H1 fast-lane population cannot overlap them",
            "outcome_access": "only via require_outcome_access: complete (non-shallow) clone; "
                              "seal reloaded and git-anchored (one commit ever touches it, "
                              "ancestor of HEAD, ancestor of a branch tip advertised by `git "
                              "ls-remote origin` - local refs/remotes never count - bytes "
                              "equal); vendor manifests anchored the same way; event table sha "
                              "equal to census_binding; holdout via the committed write-once "
                              "HOLDOUT_REQUEST.json which pins the seal commit (var/ ledger is "
                              "a cache); grants are HMAC-tokenized and re-verified, including "
                              "the git anchor, on every vendor call",
        },
        "governance": {
            "external_anchor_required": True,
            "external_anchor": "OWNER ACTION: record the seal commit hash and, later, the holdout "
                               "request commit hash outside the repository (e.g. a dated message "
                               "or note held by the owner) as soon as each is pushed; a later "
                               "grant whose anchors differ from these records is void",
            "branch_protection_required": True,
            "branch_protection": "OWNER ACTION: protect the fast-lane branch on the remote (no "
                                 "force-push, no deletion) before the seal is pushed",
            "residual_risk": "code cannot prevent a force-push or branch deletion by someone "
                             "with remote write access; it detects a rewrite of the seal commit "
                             "(the request pins it and every grant re-checks it against the "
                             "advertised tip) but a rewrite of only the request commit that "
                             "keeps the seal commit is detectable only through the external "
                             "anchor and branch protection",
        },
        "vendor": {"primary": "Sharadar (Nasdaq Data Link SEP, ACTIONS, TICKERS with CIK)",
                   "fallback": "EODHD for development only; the benchmark has no fallback",
                   "purchase": "owner action",
                   "attestation_required": ["includes_delisted", "corporate_actions",
                                            "pit_security_mapping", "license_note"]},
    }


def render_markdown(protocol: Mapping[str, Any], digest: str) -> str:
    power = protocol["power"]["portfolio_mde_annual_pct"]
    lines = [
        f"# `{LINEAGE_ID}` protocol — DRAFT (not sealed)",
        "",
        f"Status `{protocol['status']}`; `open_decisions` = {protocol['open_decisions']}. "
        f"Canonical sha256 of this draft: `{digest}`. Sealing requires flipping status to "
        "`FINAL_FOR_SEAL` by explicit decision, then `python3 scripts/fastlane.py seal-prereg "
        "--protocol research/fastlane/QUANT_FASTLANE_HPIT_V1_PROTOCOL.json`, then committing "
        "and pushing the sealed file (grants require it in a branch the remote advertises, in "
        "a complete clone: run `git fetch --unshallow` first if the clone is shallow).",
        "",
        "## Frozen elements",
        "",
        "- Events: SEC Insider Transactions Data Sets, original Form 4, code P / acquired A; "
        "primary = common-equity titles, frozen footnote exclusions (plan/DRIP/fees, IPO/"
        "underwritten, conversion, private placement), exact duplicates removed, backdated "
        "accessions excluded. Unfiltered = sensitivity only.",
        "- Entry: open of the first vendor session strictly after FILING_DATE; missing entry "
        "bar → skipped; missing exit bar → next open, else delisting treatment after 20 sessions.",
        "- Splits: discovery 2006-01-01→2018-12-31, walk-forward 2019-01-01→2021-06-30, "
        "holdout 2021-07-01→2026-06-30 (sealed, one look).",
        "- Return: r_ex,t = Σ w_{i,t−1}(r_{i,t} − r_SPY,t)/Σ w_{i,t−1}, buy-and-hold weights on "
        "invested capital; idle cash 0 % reported separately; alpha = 252 × mean r_ex.",
        f"- Inference: one-sided studentized moving-block bootstrap (80 sessions, B = 10,000, "
        f"seed {BOOTSTRAP_SEED}) AND fixed-b HAC t (Bartlett, b = 0.1, Kiefer–Vogelsang); both "
        "below the Holm threshold. FF5+UMD robustness only.",
        "- Multiplicity: M declared below; N_trials = max(M_declared, trial-ledger "
        "evaluations) for DSR and the Holm context; ALL declared variants need discovery trial "
        "records before a holdout request; Romano-Wolf/SPA; ≤ 3 finalists with discovery and "
        "walk-forward trial records; Holm α = 0.05. Zero finalists → NO_GO, holdout unopened.",
        f"- Seed robustness (reporting only, never gating): seeds {ROBUSTNESS_SEEDS}.",
        "- Constructor: K = 100 slots, C0 = USD 100,000 paper; tie-break sha256(seed|sorted "
        "accessions), never CIK.",
        "- Frictions (frozen, not calibrated): Abdi–Ranaldo with ADV20 floors 250/120/60/30/10 bp "
        "(<0.5M/0.5–2M/2–10M/10–50M/≥50M); ADV20 < USD 100k untradeable; USD 0.0035/share, "
        "min USD 0.35; impact 1.0·σ·√(Q/ADV20); participation ≤ 0.1 % ADV20; 2× stress reported.",
        "- Delisting by class: cash acquisition / stock merger → last trade; bankruptcy/cause "
        "−100 %; unknown −30 % (stress −100 %); vendor code→class map committed before any "
        "grant. Benchmark: SPY total return from the vendor, committed manifest, no fallback.",
        "- Outcomes: GO (all legs), INCONCLUSIVE (GO fails, one-sided 95 % upper bound "
        "≥ 3 %/yr), NO_GO; only GO may authorize paper sizing.",
        "- Anchoring: grants need a complete (non-shallow) clone and the seal, request and "
        "vendor manifests contained in a branch the real remote advertises; the request pins "
        "the seal commit. OWNER ACTIONS: branch protection (no force-push/deletion) and an "
        "external record of the seal and request commit hashes. Residual risk: a force-push "
        "that rewrites only the request commit is caught only by those owner actions.",
        "",
        f"## Variant grid (M = {len(protocol['variants'])})",
        "",
        "Adequacy (outcome-blind): ≥ "
        f"{MIN_EVENTS_PER_YEAR_EACH_SPLIT:.0f} issuer-days/yr in every split and ≥ "
        f"{MIN_HOLDOUT_CONCURRENT_POSITIONS:.0f} average concurrent holdout positions. "
        "Disclosure: these counts include holdout-period counts (no outcomes).",
        "",
        "| Variant | Disc/yr | WF/yr | Holdout/yr | Avg concurrent (K=100) | Per-event MDE (bp) | Portfolio MDE, TE 8% (%/yr) | Holm-step (%/yr) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in protocol["variants"]:
        r = v["census_issuer_days_per_year"]
        p = v["power_one_sided_0p05"]
        lines.append(f"| `{v['variant_id']}` | {r['discovery']} | {r['walk_forward']} | "
                     f"{r['holdout']} | {p['avg_concurrent_positions']} | "
                     f"{p['per_event_mde_bp']} | {p['portfolio_mde_annual_pct']} | "
                     f"{v['power_holm_first_step_0p0167']['portfolio_mde_annual_pct']} |")
    lines += ["", "Excluded cells:", ""]
    lines += [f"- `{e['variant_id']}`: {'; '.join(e['reasons'])}"
              for e in protocol["excluded_cells"]] or ["- none"]
    lines += [
        "",
        "## Power reading",
        "",
        f"Audit per-event table reproduced (bp, 5-year holdout, h=20): "
        f"{protocol['power']['audit_table_reproduction_bp']}.",
        "",
        "The holdout tests a portfolio. With σ20d = 14 %, deff 1.5 and 8 %/yr tracking error "
        f"vs SPY, the annualized MDE on invested capital is ≈ {power['K20']} %/yr at K = 20 "
        f"and ≈ {power['K100']} %/yr at K = 100 ({power['K100_holm_first_step']} %/yr at the "
        "first Holm step). All exceed the 3 %/yr GO bar: the significance legs bind, and a "
        "true 3–10 %/yr alpha will most likely read INCONCLUSIVE rather than GO.",
        "",
    ]
    return "\n".join(lines)


def write_draft(fw: Firewall) -> dict:
    census_path = fw.artifact("census_v1.json")
    census = fw.read_json(census_path)
    census_sha = "sha256:" + fw.sha256_file(census_path)
    gov = {}
    for rel in ("governance/D07_OPEN_SPACE_BOUNDARY.md",
                "handoff/CLAUDE_DELEGATED_DECISIONS_AND_PLAN_2026-09-23.md",
                "handoff/CLAUDE_PROJECT_REVIEW_AUDIT_2026-09-23.md"):
        try:
            gov[rel] = "sha256:" + fw.sha256_file(fw.repo_root / rel)
        except OSError:
            gov[rel] = None
    protocol = build_protocol(census, census_sha, gov)
    validate_protocol({**protocol, "status": "FINAL_FOR_SEAL"}, for_seal=True)
    digest = protocol_sha256(protocol)
    fw.write_json_atomic(fw.artifact("QUANT_FASTLANE_HPIT_V1_PROTOCOL.json"), protocol)
    fw.write_text_atomic(fw.artifact("QUANT_FASTLANE_HPIT_V1_PROTOCOL.md"),
                         render_markdown(protocol, digest))
    return protocol

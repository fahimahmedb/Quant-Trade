"""Draft (unsealed) protocol for ``QUANT_FASTLANE_HPIT_V1`` built from the census.

The draft encodes D5 of ``handoff/CLAUDE_DELEGATED_DECISIONS_AND_PLAN_2026-09-23.md``
plus a variant grid chosen *only* from outcome-blind event counts. It is written
with ``status = DRAFT_NOT_SEALED``; :func:`quant.fastlane.preregistration.seal_protocol`
refuses it until an explicit decision flips it to ``FINAL_FOR_SEAL``.

Power follows the audit convention (sigma of a 20-session excess return 14 %,
design effect 1.5, one-sided alpha 0.05, power 80 %), reported two ways:

* per-event MDE ``(z_a + z_b) * sigma_h * sqrt(deff / N_eff)``, where
  ``N_eff`` is capped by slot capacity ``K * 252 / h`` per year;
* annualized MDE of the calendar-time portfolio on invested capital,
  ``(z_a + z_b) * sigma_daily * sqrt(252 * deff / K_avg) / sqrt(years)``, with
  ``K_avg = min(K, rate * h / 252)`` concurrent positions.
"""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any, Mapping

from quant.fastlane.firewall import LINEAGE_ID, Firewall
from quant.fastlane.frictions import FrictionParams
from quant.fastlane.preregistration import SPLITS, STATUS_DRAFT, protocol_sha256

SIGMA_20D = 0.14
DESIGN_EFFECT = 1.5
ALPHA_ONE_SIDED = 0.05
POWER = 0.80
HOLDOUT_YEARS = 5.0

GRID_FAMILIES = {
    "OD": ("OD", "issuer-day value of accessions with >=1 officer/director owner"),
    "CEO_CFO": ("CEO_CFO", "issuer-day value of accessions with >=1 CEO/CFO owner"),
    "FROZEN_FV_10S": ("FROZEN_FV_PROXY_10WD",
                      "sum of O/D accession values in the 10-session formation window at the "
                      "crossing; census counts use the weekday proxy, evaluation uses exact "
                      "vendor sessions"),
}
GRID_VALUE_FLOORS = (("V10K", 10_000.0, "ge_10k"), ("V100K", 100_000.0, "ge_100k"),
                     ("V1M", 1_000_000.0, "ge_1m"))
GRID_HORIZONS = (5, 20, 60)
MIN_EVENTS_PER_YEAR_EACH_SPLIT = 50.0
MIN_HOLDOUT_CONCURRENT_POSITIONS = 20.0

CONSTRUCTOR = {
    "id": "FASTLANE_SLOTK_ADV20_V1",
    "C0_usd": 100_000.0,
    "slots": 100,
    "slot_target_notional": "C0 / slots",
    "allocation": "a_j = min(C0/slots, participation_cap_adv20 * ADV20_j); ADV20 = mean of "
                  "raw_close*raw_volume over the 20 completed vendor sessions before entry",
    "order": "process entries by (entry_session, issuer_cik, accession-set digest); lowest free "
             "slot; if the issuer already holds an active slot or all slots are busy, a_j = 0 "
             "with the reason logged",
    "slot_release": "time-based at the scheduled exit close; never early on gain, loss or "
                    "delisting",
    "no_recycling": "realized P&L is not recycled into C0",
    "owner_decision_required": True,
    "rationale": "Power of the one-look holdout scales with concurrent positions, not event "
                 "count: K=20 gives an annualized MDE of ~15%/yr on invested capital, K=100 "
                 "~7%/yr. C0 = USD 100,000 keeps a USD 1,000 slot so the USD 1 commission "
                 "minimum costs 10 bp per side.",
    "alternative_audit_4_2": {"C0_usd": 10_000.0, "slots": 20,
                              "source": "audit §4.2 / FORM4_SLOT20_ADV20_V1 geometry"},
}

FRICTIONS = {
    "spread": {
        "estimator": "ABDI_RANALDO_2017_CHL",
        "variant": "two_day_corrected_mean",
        "window_sessions": 21,
        "min_pairs": 15,
        "adv20_bucket_floor_bps": [
            {"adv_below_usd": 1_000_000.0, "floor_bps": 150.0},
            {"adv_below_usd": 5_000_000.0, "floor_bps": 75.0},
            {"adv_below_usd": 25_000_000.0, "floor_bps": 35.0},
            {"adv_below_usd": 100_000_000.0, "floor_bps": 15.0},
            {"adv_below_usd": None, "floor_bps": 5.0},
        ],
        "cost_per_side": "half of max(Abdi-Ranaldo estimate over the 21 sessions before entry "
                         "(before exit for the exit leg), ADV20 bucket floor)",
        "note": "Floors are draft engineering values (full quoted spread, bp), not calibration.",
    },
    "commission": {"per_share_usd": 0.005, "minimum_usd": 1.0, "max_fraction_of_notional": 0.01,
                   "note": "draft; shaped like a published retail per-share schedule; owner to "
                           "confirm against the actual paper broker"},
    "impact": {"model": "SQUARE_ROOT", "coefficient": 1.0,
               "volatility": "stdev of daily log close-to-close over the 20 sessions before "
                             "the leg"},
    "participation_cap_adv20": 0.001,
    "missing_delisting_return": {"base": -0.30, "stress": -1.00},
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


def portfolio_mde_annual(k_avg: float, years: float, *, sigma20: float = SIGMA_20D,
                         deff: float = DESIGN_EFFECT, alpha: float = ALPHA_ONE_SIDED,
                         power: float = POWER) -> float | None:
    if k_avg <= 0 or years <= 0:
        return None
    sigma_daily = sigma20 / math.sqrt(20.0)
    sigma_annual = sigma_daily * math.sqrt(252.0 * deff / k_avg)
    return (_z(1 - alpha) + _z(power)) * sigma_annual / math.sqrt(years)


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
    }


def _bp(x: float | None) -> float | None:
    return None if x is None else round(x * 10_000.0, 1)


def _pct(x: float | None) -> float | None:
    return None if x is None else round(x * 100.0, 2)


def audit_table_check() -> dict:
    """Reproduce the audit's §4.2 per-event table (5-year holdout, no slot cap)."""
    return {str(rate): _bp(per_event_mde(rate * HOLDOUT_YEARS, 20))
            for rate in (300, 500, 1000, 2000)}


def build_grid(census: Mapping[str, Any], slots: int) -> tuple[list[dict], list[dict]]:
    variants, excluded = [], []
    for fam_id, (census_family, value_basis) in GRID_FAMILIES.items():
        for tier_id, floor, tier_key in GRID_VALUE_FLOORS:
            rates = {split: census["by_split"][split][census_family]["value_tiers_per_year"][tier_key]
                     for split in SPLITS}
            for horizon in GRID_HORIZONS:
                vid = f"{fam_id}_{tier_id}_H{horizon}"
                power = variant_power(rates["holdout"], horizon, slots)
                power_holm = variant_power(rates["holdout"], horizon, slots,
                                           alpha=ALPHA_ONE_SIDED / 3)
                reasons = []
                low = [s for s, r in rates.items() if r < MIN_EVENTS_PER_YEAR_EACH_SPLIT]
                if low:
                    reasons.append(f"fewer than {MIN_EVENTS_PER_YEAR_EACH_SPLIT:.0f} "
                                   f"issuer-days/yr in {low}")
                if power["avg_concurrent_positions"] < MIN_HOLDOUT_CONCURRENT_POSITIONS:
                    reasons.append(f"holdout average concurrent positions "
                                   f"{power['avg_concurrent_positions']} < "
                                   f"{MIN_HOLDOUT_CONCURRENT_POSITIONS:.0f}")
                row = {
                    "variant_id": vid,
                    "family": fam_id,
                    "census_family": census_family,
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
                                     "avg_concurrent_positions":
                                         power["avg_concurrent_positions"]})
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
                         "role": "out-of-sample check of discovery ranking; no re-tuning"},
        "holdout": {"price_window": {"start": "2021-04-01", "end": "2026-09-30"},
                    "role": "sealed, one look, <=3 finalists"},
    }
    for name, (start, end) in SPLITS.items():
        splits[name].update({"start": start.isoformat(), "end": end.isoformat(),
                             "assignment": "by available_after_date (FILING_DATE)"})
    return {
        "lineage": LINEAGE_ID,
        "protocol_version": "1.0-draft",
        "status": STATUS_DRAFT,
        "evidence_class_target": "HISTORICAL_PIT_VALIDATION (D6, pending ratification)",
        "authority": {
            "decisions": "handoff/CLAUDE_DELEGATED_DECISIONS_AND_PLAN_2026-09-23.md §D5-D6",
            "design": "handoff/CLAUDE_PROJECT_REVIEW_AUDIT_2026-09-23.md §4",
            "frozen_signal_definition": "governance/D07_OPEN_SPACE_BOUNDARY.md §2.1-2.3",
            "source_sha256": dict(governance_sha256),
        },
        "census_binding": {
            "census_sha256": census_sha256,
            "events_sha256": census["inputs"]["events_sha256"],
            "sec_manifest_set_fingerprint": census["inputs"]["sec_manifest_set_fingerprint"],
            "note": "variant grid chosen from outcome-blind counts only",
        },
        "population": {
            "source": "SEC Insider Transactions Data Sets (quarterly, 2006Q1 onward), as filed",
            "document_type": "original Form 4 only ('4'); 4/A never creates or modifies an event",
            "rows": "NONDERIV_TRANS with TRANS_CODE 'P' and TRANS_ACQUIRED_DISP_CD 'A'",
            "unique_key": "ACCESSION_NUMBER (duplicates are build errors)",
            "entry_event": "issuer CIK x FILING_DATE",
        },
        "timing": {
            "available_after_date": "FILING_DATE",
            "entry": "open of the first vendor session strictly after available_after_date",
            "calendar": "the licensed price vendor's session list; none is invented",
            "transaction_date": "never used as a public date",
        },
        "splits": splits,
        "purge": "in discovery and walk_forward, events whose scheduled exit session falls "
                 "after the split end are excluded from that split (logged), so no holdout-"
                 "period price is read before the one look",
        "security_mapping": {
            "rule": "issuer CIK -> vendor security as of the entry date (vendor PIT tickers "
                    "table with CIK); as-filed ticker is a cross-check only",
            "ambiguous": "multiple common share classes or no mapping -> unresolved, counted, "
                         "never resolved with future prices or current tickers",
        },
        "universe_eligibility": {
            "bars": "20 complete vendor bars before entry; finite positive ADV20",
            "min_last_close_usd": 1.0,
            "note": "eligibility uses only pre-entry data",
        },
        "constructor": CONSTRUCTOR,
        "variant_grid_rule": {
            "families": {k: v[1] for k, v in GRID_FAMILIES.items()},
            "value_floors_usd": [f for _, f, _ in GRID_VALUE_FLOORS],
            "horizons_sessions": list(GRID_HORIZONS),
            "adequacy": {
                "min_issuer_days_per_year_each_split": MIN_EVENTS_PER_YEAR_EACH_SPLIT,
                "min_holdout_avg_concurrent_positions": MIN_HOLDOUT_CONCURRENT_POSITIONS,
            },
            "M_max": 48,
            "post_eligibility_recheck": "after the sealed grant and before any return is "
                                        "computed, PIT mapping and pre-entry eligibility are "
                                        "applied; a variant whose eligible counts then fail "
                                        "the adequacy rule is dropped and logged, never "
                                        "replaced",
            "census_caveat": "census counts precede security mapping and liquidity "
                             "eligibility; eligible counts will be lower",
        },
        "variants": variants,
        "excluded_cells": excluded,
        "power": {
            "assumptions": {"sigma_20d": SIGMA_20D, "design_effect": DESIGN_EFFECT,
                            "alpha_one_sided": ALPHA_ONE_SIDED, "power": POWER,
                            "holdout_years": HOLDOUT_YEARS,
                            "sigma_daily": "sigma_20d / sqrt(20)"},
            "audit_table_reproduction_bp": audit_table_check(),
            "reading": "per-event MDE is per trade at horizon h; portfolio MDE is annualized "
                       "on invested capital and is the relevant scale for the 3%/yr GO bar",
        },
        "inference": {
            "unit": "daily net return of the calendar-time portfolio in excess of SPY "
                    "(simple total returns, same corporate-action convention on both legs)",
            "interval": "moving-block bootstrap, block 80 sessions, 9,999 draws, seed fixed "
                        "in the sealed file",
            "robustness": "FF5+UMD alpha (Ken French library, snapshot fingerprinted)",
        },
        "multiplicity": {
            "M_declared": len(variants),
            "trial_ledger": "var/fastlane/ledgers/trials.jsonl; every evaluated variant appended",
            "discovery": "Deflated Sharpe (N = trial-ledger count) ranking; Romano-Wolf stepdown "
                         "(Hansen SPA as cross-check) on net excess returns",
            "finalist_rule": "top <=3 by discovery DSR among variants with Romano-Wolf p<0.10 "
                             "and positive walk-forward net excess return",
            "max_finalists": 3,
            "holdout": "Holm at family alpha 0.05 over the finalists",
        },
        "frictions": FRICTIONS,
        "delisting": {"missing_return_base": -0.30, "missing_return_stress": -1.00,
                      "rule": "a position whose security stops trading without a vendor "
                              "delisting return takes the base value; stress is reported"},
        "capacity": {"multiples_of_C0": [1, 10, 100],
                     "rule": "same constructor at each multiple with the 0.1% ADV20 cap; "
                             "net excess return reported at each"},
        "go_criterion": {
            "all_of": [
                "annualized net alpha vs SPY >= 3%/yr at 1x C0 (base delisting)",
                "Holm-adjusted p < 0.05",
                "net result positive at 1x C0 after frictions",
                "DSR > 0.95",
                "vendor attestation go_eligible (includes delisted, PIT mapping, raw prices "
                "plus actions, verified)",
            ],
            "otherwise": "NO_GO recorded as a result",
            "authority_if_go": "SHADOW_PROVISIONAL paper only (D6 caps); never "
                               "FORWARD_CONFIRMATION or real capital",
        },
        "firewall": {
            "space": "var/fastlane/ (data, ledgers), research/fastlane/ (artifacts)",
            "frozen_lineage": "no read/write of FORM4_FIRST_VERTICAL_MULTI_COHORT_V1; its "
                              "cohorts are prospective and were never activated, so the "
                              "2006-2026H1 fast-lane population cannot overlap them",
            "outcome_access": "only via a sealed prereg whose sha256 matches; holdout via the "
                              "one-look ledger",
        },
        "vendor": {"primary": "Sharadar (Nasdaq Data Link SEP, ACTIONS, TICKERS with CIK)",
                   "fallback": "EODHD", "purchase": "owner action",
                   "attestation_required": ["includes_delisted", "corporate_actions",
                                            "pit_security_mapping", "license_note"]},
        "open_decisions": [
            "constructor slots/C0 (K=100, C0=USD 100k drafted; audit K=20, C0=USD 10k gives "
            "~15%/yr holdout MDE)",
            "commission schedule of the actual paper broker",
            "spread floors by ADV20 bucket",
        ],
    }


def render_markdown(protocol: Mapping[str, Any], digest: str) -> str:
    lines = [
        f"# `{LINEAGE_ID}` protocol — DRAFT (not sealed)",
        "",
        f"Status `{protocol['status']}`. Canonical sha256 of this draft: `{digest}`. Sealing "
        "requires flipping status to `FINAL_FOR_SEAL` by explicit decision, then "
        "`python3 scripts/fastlane.py seal-prereg --protocol research/fastlane/"
        "QUANT_FASTLANE_HPIT_V1_PROTOCOL.json`; the seal is write-once.",
        "",
        "## Frozen D5 elements",
        "",
        "- Events: SEC Insider Transactions Data Sets, original Form 4 only, code P / acquired A.",
        "- Entry: open of the first vendor session strictly after FILING_DATE.",
        "- Splits: discovery 2006-01-01→2018-12-31, walk-forward 2019-01-01→2021-06-30, "
        "holdout 2021-07-01→2026-06-30 (sealed, one look).",
        "- Inference: daily net return of a calendar-time portfolio in excess of SPY; "
        "80-session block bootstrap; FF5+UMD robustness.",
        "- Multiplicity: M ≤ 48 declared; DSR + Romano-Wolf/SPA on discovery; ≤ 3 finalists; "
        "Holm α=0.05 on holdout.",
        "- Frictions: Abdi–Ranaldo spread with ADV20-bucket floor, per-share commission with "
        "minimum, square-root impact, participation ≤ 0.1 % ADV20; missing delisting −30 % "
        "(−100 % stress); capacity at 1×/10×/100× C0.",
        "- GO: net alpha vs SPY ≥ 3 %/yr AND Holm p < 0.05 AND positive at 1× C0 AND "
        "DSR > 0.95 AND a GO-eligible vendor attestation.",
        "",
        f"## Variant grid (M = {len(protocol['variants'])})",
        "",
        "Adequacy (outcome-blind): ≥ "
        f"{MIN_EVENTS_PER_YEAR_EACH_SPLIT:.0f} issuer-days/yr in every split and ≥ "
        f"{MIN_HOLDOUT_CONCURRENT_POSITIONS:.0f} average concurrent holdout positions.",
        "",
        "| Variant | Disc/yr | WF/yr | Holdout/yr | Avg concurrent (K=100) | Per-event MDE (bp) | Portfolio MDE (%/yr) | Holm-step MDE (%/yr) |",
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
    for e in protocol["excluded_cells"]:
        lines.append(f"- `{e['variant_id']}`: {'; '.join(e['reasons'])}")
    k20 = portfolio_mde_annual(20, HOLDOUT_YEARS)
    k100 = portfolio_mde_annual(100, HOLDOUT_YEARS)
    lines += [
        "",
        "## Power reading",
        "",
        f"Audit per-event table reproduced (bp, 5-year holdout, h=20): "
        f"{protocol['power']['audit_table_reproduction_bp']}.",
        "",
        "The holdout tests a *portfolio*, whose noise falls with the number of concurrent "
        "positions, not with the number of events. With σ20d = 14 % and deff 1.5, the "
        f"annualized MDE on invested capital is ≈ {k20 * 100:.1f} %/yr at K = 20 concurrent "
        f"positions and ≈ {k100 * 100:.1f} %/yr at K = 100. Both exceed the 3 %/yr GO bar, "
        "so the Holm p < 0.05 leg — not the 3 % leg — is the binding GO condition. The "
        "drafted constructor therefore uses K = 100 slots and C0 = USD 100,000; the audit's "
        "K = 20 / C0 = USD 10,000 remains an owner option.",
        "",
        "## Open decisions before sealing",
        "",
    ]
    lines += [f"- {d}" for d in protocol["open_decisions"]]
    lines.append("")
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
    digest = protocol_sha256(protocol)
    fw.write_json_atomic(fw.artifact("QUANT_FASTLANE_HPIT_V1_PROTOCOL.json"), protocol)
    fw.write_text_atomic(fw.artifact("QUANT_FASTLANE_HPIT_V1_PROTOCOL.md"),
                         render_markdown(protocol, digest))
    return protocol

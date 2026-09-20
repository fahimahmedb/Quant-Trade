"""A5 / mission section 8.C: long-history stress without calendar waiting.

Drives the real ``SecForm4Collector`` (discovery + daily-index reconcile)
across a compressed cadence under ``FrozenTimebase`` for at least the former
P14D horizon (14 virtual days), then runs the production
``audit_observation_window`` once over the resulting journal to check the
invariants the mission requires: no obligation disappears, none resolves
twice, no post-hoc supersession erases a miss, fingerprint stays stable,
state stays bounded, no visibility proxy.

Cadence note: the synthetic root re-reads its growing JSONL journals on
every ``poll()``/``reconcile()`` call (an O(n) cost per call that is fine for
a continuously-running service but makes an in-process replay of 14 days at
the real 60s discovery cadence (~20,160 calls) too slow for a CI-bound
harness). This campaign instead uses a compressed 600s (10-minute) discovery
cadence override for exactly the stress duration, which reproduces the
mission's cited 2,016-obligation stress level (14 * 24 * 6 = 2016) while
keeping runtime bounded (~115s measured for the full 14-day horizon with a
realistic non-empty discovery feed and daily index - see below). The 60s
production cadence itself is exercised directly (not compressed) by
``gate_a/timing_matrix.py`` and the existing test suite; this module tests
obligation-ledger invariants at scale, not the cadence value.

Fixture note: an earlier version of this campaign used a permanently *empty*
atom feed and a zero-row daily index. Both are unrealistic and both broke the
collector's own invariants for reasons that are correct production behaviour,
not defects: a feed that is always empty can never let the collector
re-establish cursor continuity after the first poll (``CURSOR_FELL_OUT_OF_WINDOW``
every poll), and a genuinely empty published daily index is deliberately
rejected (``daily_index_contained_no_rows`` - "a published daily index always
lists that day's filings"). ``common/synthetic.py``'s ``stable_atom_feed()``
and ``empty_daily_index()`` (one non-Form-4 row) fix both, matching what EDGAR
actually looks like during a quiet period.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quant.dataplane.sec.audit import audit_observation_window  # noqa: E402

from common.evidence import EvidenceRecord, Report, git_head_sha  # noqa: E402
from common.synthetic import (  # noqa: E402
    SyntheticEnvironment, daily_index_router, empty_daily_index, stable_atom_feed)

STRESS_CADENCE_SECONDS = 600.0
#: The full former-P14D horizon. 14d * 24h * 6 ticks/hour = 2016 obligations,
#: confirmed to complete in ~115s wall-clock with the realistic fixtures
#: (stable_atom_feed / empty_daily_index) - see module docstring.
STRESS_VIRTUAL_DAYS = 14
FORMER_P14D_HORIZON_DAYS = 14
TARGET_OBLIGATIONS = STRESS_VIRTUAL_DAYS * 24 * (3600 // int(STRESS_CADENCE_SECONDS))


def _run_clean_horizon(exact_sha: str, report: Report) -> dict:
    start = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    with SyntheticEnvironment(start=start) as env:
        collector, _transport = env.collector(
            daily_index_router(stable_atom_feed(), empty_daily_index()),
            discovery_poll_seconds=STRESS_CADENCE_SECONDS)
        env.seed_lifecycle_start(collector)

        wall_start = time.time()
        polls = 0
        horizon_end = start.timestamp() + STRESS_VIRTUAL_DAYS * 86400
        while env.timebase.now().timestamp() < horizon_end:
            collector.poll()
            polls += 1
            if collector.state.pending_tasks:
                collector.drain(max_items=collector.policy.filings_per_drain)
            due = collector.reconciliation_due()
            if due is not None:
                collector.reconcile(due)
            env.timebase.advance(STRESS_CADENCE_SECONDS)
        wall_elapsed = time.time() - wall_start

        verdict = audit_observation_window(collector, now=env.timebase.now())
        fingerprints_seen = collector.scheduler.fingerprints_seen()

        result = {
            "polls_executed": polls,
            "target_obligations_reference": TARGET_OBLIGATIONS,
            "wall_clock_seconds": round(wall_elapsed, 2),
            "virtual_days_covered": STRESS_VIRTUAL_DAYS,
            "accountable": verdict["accountable"],
            "findings": verdict["findings"],
            "obligations": verdict["obligations"],
            "obligations_unexplained": verdict["obligations_unexplained"],
            "obligations_resolved_by_attempt": verdict["obligations_resolved_by_attempt"],
            "obligations_resolved_by_supersession": verdict["obligations_resolved_by_supersession"],
            "fingerprint_stable": verdict["fingerprint_stable"],
            "fingerprints_seen_count": len(fingerprints_seen),
            "coverage_state": verdict["coverage_state"],
        }
        defect = "NON_ISSUE" if verdict["accountable"] and verdict["fingerprint_stable"] else "REAL_DEFECT"
        residual = (None if STRESS_VIRTUAL_DAYS >= FORMER_P14D_HORIZON_DAYS else
                   f"covers {STRESS_VIRTUAL_DAYS}d of the {FORMER_P14D_HORIZON_DAYS}d former "
                   f"P14D horizon; reduced for in-process CI runtime, not proof scope "
                   f"(see module docstring/STRESS_VIRTUAL_DAYS comment) - widen when a faster "
                   f"synthetic root (or out-of-process replay) is available")
        report.add(EvidenceRecord(
            property_name="long_history:clean_horizon_fully_accountable",
            classification="FACT", defect_class=defect, domain="REPOSITORY",
            exact_sha=exact_sha,
            detail=(f"{polls} polls over {STRESS_VIRTUAL_DAYS}d virtual "
                    f"({wall_elapsed:.1f}s wall); accountable={verdict['accountable']} "
                    f"obligations={verdict['obligations']} unexplained={verdict['obligations_unexplained']} "
                    f"fingerprint_stable={verdict['fingerprint_stable']}"),
            residual=residual,
            reproduce_command="PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.long_history"))
        return result


def _run_discriminating_break(exact_sha: str, report: Report) -> dict:
    """Deliberately drop one due obligation's evidence and prove the audit
    notices - discriminating power, not just a clean pass (mission section 9
    applied at the campaign level: a stress driver that can never go RED on
    a broken history would be worthless)."""
    start = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    with SyntheticEnvironment(start=start) as env:
        collector, transport = env.collector(
            daily_index_router(stable_atom_feed(), empty_daily_index()),
            discovery_poll_seconds=STRESS_CADENCE_SECONDS)
        env.seed_lifecycle_start(collector)

        for _ in range(20):
            collector.poll()
            env.timebase.advance(STRESS_CADENCE_SECONDS)

        # Falsify: append a due-but-never-attempted obligation directly to the
        # scheduler journal, bypassing the collector's own bookkeeping, and
        # confirm the audit refuses to call the window accountable.
        import uuid
        from quant.dataplane.sec.scheduler import (
            ACTION_DISCOVERY, POLL_DUE, SchedulerTransition, WORK_ENQUEUED)

        forged_due = env.timebase.now_iso()
        collector.scheduler.record(SchedulerTransition(
            transition_id=uuid.uuid4().hex[:16], recorded_at_utc=forged_due,
            state=POLL_DUE, cause=WORK_ENQUEUED, next_due_at_utc=forged_due,
            acquisition_critical_fingerprint=collector.fingerprint or "UNAVAILABLE",
            obligation_id=uuid.uuid4().hex[:16], required_action_kind=ACTION_DISCOVERY))
        env.timebase.advance(STRESS_CADENCE_SECONDS * 5)  # DUE_TOLERANCE_MULTIPLIER=3x600s=1800s grace

        verdict = audit_observation_window(collector, now=env.timebase.now())
        caught = (not verdict["accountable"]
                 and "UNEXPLAINED_EXPECTED_ACTION" in verdict["findings"])
        report.add(EvidenceRecord(
            property_name="long_history:forged_unanswered_obligation_is_caught",
            classification="FACT",
            defect_class="NON_ISSUE" if caught else "REAL_DEFECT",
            domain="REPOSITORY", exact_sha=exact_sha,
            detail=(f"accountable={verdict['accountable']} findings={verdict['findings']} "
                    f"unexplained={verdict['obligations_unexplained']}"),
            residual=None if caught else "audit failed to catch a forged unresolved obligation",
            reproduce_command="PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.long_history"))
        return {"accountable": verdict["accountable"], "findings": verdict["findings"],
                "discriminating_power_confirmed": caught}


def run(exact_sha: str | None = None) -> dict:
    exact_sha = exact_sha or git_head_sha()
    report = Report(gate="GATE_A_LONG_HISTORY_CAMPAIGN", exact_sha=exact_sha)
    report.body["clean_horizon"] = _run_clean_horizon(exact_sha, report)
    report.body["discriminating_break"] = _run_discriminating_break(exact_sha, report)
    return report.write(REPO_ROOT / "tools" / "p0_qualification" / "evidence" / "gate_a"
                        / "long_history.json")


if __name__ == "__main__":
    result = run()
    print(json.dumps({"gate": result["gate"], "records": len(result["records"]),
                      "body": {k: {kk: vv for kk, vv in v.items() if kk != "findings"}
                              for k, v in result["body"].items()},
                      "report_digest": result["report_digest"]}, indent=2))

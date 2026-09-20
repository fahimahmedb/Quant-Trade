"""A3 timing-boundary matrix.

Reads every acquisition-critical timing constant directly from the frozen V4
production source (never a copied number), cites the exact existing
discriminating test(s) that already prove boundary behaviour for it, and
verifies those citations still resolve to real tests in this exact tree (a
stale citation is a MISSING_PROOF finding, not a silent pass).

One genuinely new boundary is exercised here rather than merely cited: the
deployment-authority maximum age (``DEPLOYMENT_AUTHORITY_MAX_AGE_SECONDS``),
because no existing test pins its exact edge (age == max accepted,
age == max + epsilon rejected). That gap is closed with a direct call into
the frozen ``_consume_deployment_authority`` through an isolated root -
never by editing the launcher.
"""

from __future__ import annotations

import dataclasses
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from quant.dataplane.sec import collector as collector_module  # noqa: E402
from quant.dataplane.sec.policy import SecAccessPolicy  # noqa: E402
from quant.dataplane.sec.supervisor import host_boot_id  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.evidence import EvidenceRecord, Report, git_head_sha  # noqa: E402
from common.launcher_loader import stage_isolated_root  # noqa: E402


def _test_exists(dotted_name: str) -> bool:
    try:
        suite = unittest.TestLoader().loadTestsFromName(dotted_name)
    except (ImportError, AttributeError):
        return False
    return suite.countTestCases() >= 1


#: The exact A3 mission list, in policy-field terms. Restricting to these
#: (rather than every ``SecAccessPolicy`` field) keeps the matrix scoped to
#: acquisition-timing boundaries; non-timing fields (page size, encoding,
#: documentation provenance, ...) are policy/fingerprint concerns already
#: covered by ``fingerprint.py``'s classification tests, not this A3 matrix.
A3_TIMING_POLICY_FIELDS: tuple[str, ...] = (
    "discovery_poll_seconds", "idle_reuse_seconds", "connect_timeout_seconds",
    "read_timeout_seconds", "total_deadline_seconds", "backoff_schedule_seconds",
    "rate_limit_cooldown_seconds", "forbidden_cooldown_seconds",
)


def _policy_defaults() -> dict[str, object]:
    all_defaults = {field.name: field.default for field in dataclasses.fields(SecAccessPolicy)
                    if field.default is not dataclasses.MISSING}
    return {name: all_defaults[name] for name in A3_TIMING_POLICY_FIELDS}


CITATIONS: dict[str, tuple[str, ...]] = {
    "discovery_poll_seconds": ("tests.test_sec_form4_capture.SchedulerProvenanceTests"
                               ".test_next_due_at_reflects_cadence_backoff_and_pending_work",),
    "idle_reuse_seconds": ("tests.test_astra_pre_t0.WireCampaign"
                          ".test_real_connection_truncation_and_send_count",),
    "connect_timeout_seconds": ("tests.test_astra_pre_t0.WireCampaign"
                                ".test_trickling_body_respects_total_deadline_real_socket",),
    "read_timeout_seconds": ("tests.test_astra_pre_t0.WireCampaign"
                             ".test_trickling_body_respects_total_deadline_real_socket",),
    "total_deadline_seconds": ("tests.test_astra_pre_t0.WireCampaign"
                               ".test_trickling_body_respects_total_deadline_real_socket",),
    "backoff_schedule_seconds": ("tests.test_sec_form4_capture.TrafficBudgetTests"
                                 ".test_backoff_walks_the_frozen_ladder_with_jitter_and_stops_growing",),
    "rate_limit_cooldown_seconds": ("tests.test_sec_form4_capture.TrafficBudgetTests"
                                    ".test_retry_after_is_parsed_in_both_permitted_forms",),
    "forbidden_cooldown_seconds": ("tests.test_sec_form4_capture.TrafficBudgetTests"
                                   ".test_cooldown_is_durable_across_restart_and_never_shortened",),
    "daily_index_settle_hours": (
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_settle_delay_is_measured_after_edgar_close_not_utc_date_start",
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_spring_dst_does_not_shorten_30_elapsed_hours",
        "tests.test_p0_continuity_compression.CalendarBoundaryCompressionTests"
        ".test_fall_dst_does_not_lengthen_30_elapsed_hours",
    ),
    "restart_delay_seconds": ("tests.test_p0_deployment_boundaries.SupervisorRealProcessBoundaryTests"
                              ".test_sigterm_stop_is_clean_but_replacement_supervisor_is_manual",),
    "restart_burst_window_seconds": (
        "tests.test_astra_pre_t0.Phase5AuthorityBindingCampaign"
        ".test_automatic_restart_requires_external_exit_witness",),
    "stop_timeout_seconds": (
        "tests.test_astra_pre_t0.Phase7EffectiveSystemdContractCampaign"
        ".test_effective_restart_and_timeout_timing_drift_is_rejected",),
    "restart_burst_limit": (
        "tests.test_astra_pre_t0.Phase4LifecycleAndWindowCampaign"
        ".test_unsolicited_zero_child_exit_cannot_cleanly_stop_qualifying_service",),
    # deployment_authority_max_age_seconds intentionally has no prior citation:
    # it is the one gap this module closes directly, below.
}


def _cited_evidence(report: Report, exact_sha: str, name: str, value: object,
                    source: str) -> None:
    citations = CITATIONS.get(name, ())
    missing = [dotted for dotted in citations if not _test_exists(dotted)]
    if not citations:
        report.add(EvidenceRecord(
            property_name=f"timing_boundary:{name}", classification="FACT",
            defect_class="MISSING_PROOF", domain="REPOSITORY",
            detail=f"value={value!r} read from {source}; no citation registered yet",
            exact_sha=exact_sha, residual="new boundary test required"))
        return
    if missing:
        report.add(EvidenceRecord(
            property_name=f"timing_boundary:{name}", classification="CLAIM",
            defect_class="MISSING_PROOF", domain="REPOSITORY",
            detail=f"value={value!r} read from {source}; stale citation(s): {missing}",
            exact_sha=exact_sha, residual="citation no longer resolves; re-cite or re-test"))
        return
    report.add(EvidenceRecord(
        property_name=f"timing_boundary:{name}", classification="FACT",
        defect_class="NON_ISSUE", domain="REPOSITORY",
        detail=f"value={value!r} read from {source}; boundary proven by {citations}",
        exact_sha=exact_sha,
        reproduce_command=f"PYTHONPATH=src python3 -m unittest {citations[0]} -v"))


def _deployment_authority_max_age_boundary(report: Report, exact_sha: str, max_age: float
                                           ) -> None:
    """New discriminant: age == max accepted, age == max + 1s rejected."""
    import tempfile
    from unittest import mock as _mock

    reference_now = datetime(2026, 9, 20, 12, 0, 0, tzinfo=timezone.utc)

    for label, delta, should_accept in (
        ("at_exact_max_age", timedelta(seconds=max_age), True),
        ("one_microsecond_over_max_age", timedelta(seconds=max_age, microseconds=1), False),
        ("one_second_over_max_age", timedelta(seconds=max_age + 1.0), False),
    ):
        with tempfile.TemporaryDirectory(prefix="quant-p0-authority-boundary-") as directory:
            root = Path(directory)
            launcher = stage_isolated_root(root)
            fingerprint = "sha256:" + "0" * 64
            authorized_at = reference_now - delta
            payload = {
                "schema": "p0_deployment_authority/v1",
                "cause": "DEPLOYMENT_RESTART",
                "acquisition_critical_fingerprint": fingerprint,
                "host_boot_id": host_boot_id(),
                "nonce": f"qualification-{label}",
                "authorized_at_utc": authorized_at.isoformat(),
            }
            path = launcher.authority_path(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload), encoding="utf-8")

            # The production check reads real wall-clock time
            # (``datetime.now(timezone.utc)``), so the exact boundary can only be
            # pinned deterministically by freezing "now" inside the loaded
            # launcher module - a subclass override, never an edit to the file.
            class _FrozenDatetime(datetime):
                @classmethod
                def now(cls, tz=None):
                    return reference_now if tz is not None else reference_now.replace(tzinfo=None)

            with mock.patch.object(launcher, "datetime", _FrozenDatetime):
                try:
                    launcher._consume_deployment_authority(root, fingerprint)
                    accepted = True
                except RuntimeError:
                    accepted = False
            defect = "NON_ISSUE" if accepted == should_accept else "REAL_DEFECT"
            report.add(EvidenceRecord(
                property_name=f"timing_boundary:deployment_authority_max_age_seconds:{label}",
                classification="FACT", defect_class=defect, domain="REPOSITORY",
                detail=(f"max_age={max_age}s age={delta.total_seconds()}s (clock frozen) "
                        f"accepted={accepted} expected_accept={should_accept}"),
                exact_sha=exact_sha,
                reproduce_command=(
                    "PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.timing_matrix")))


def run(exact_sha: str | None = None) -> dict:
    exact_sha = exact_sha or git_head_sha()
    report = Report(gate="GATE_A_TIMING_BOUNDARY_MATRIX", exact_sha=exact_sha)

    policy_defaults = _policy_defaults()
    for name, value in policy_defaults.items():
        _cited_evidence(report, exact_sha, name, value,
                        "src/quant/dataplane/sec/policy.py:SecAccessPolicy")

    _cited_evidence(report, exact_sha, "daily_index_settle_hours",
                    collector_module.DAILY_INDEX_SETTLE_HOURS,
                    "src/quant/dataplane/sec/collector.py:DAILY_INDEX_SETTLE_HOURS")

    launcher = stage_isolated_root(Path(__import__("tempfile").mkdtemp(
        prefix="quant-p0-timing-constants-")))
    for attr, name in (
        ("RESTART_DELAY_SECONDS", "restart_delay_seconds"),
        ("RESTART_BURST_LIMIT", "restart_burst_limit"),
        ("RESTART_BURST_WINDOW_SECONDS", "restart_burst_window_seconds"),
        ("TIMEOUT_STOP_SECONDS", "stop_timeout_seconds"),
        ("DEPLOYMENT_AUTHORITY_MAX_AGE_SECONDS", "deployment_authority_max_age_seconds"),
    ):
        _cited_evidence(report, exact_sha, name, getattr(launcher, attr),
                        "deploy/quant_sec_supervisor.py")

    _deployment_authority_max_age_boundary(
        report, exact_sha, launcher.DEPLOYMENT_AUTHORITY_MAX_AGE_SECONDS)

    report.body["policy_backoff_ladder_boundary_check"] = _backoff_ladder_boundary(
        SecAccessPolicy(user_agent="Quant P0 Qualification Harness harness@quant.example.com"))
    return report.write(REPO_ROOT / "tools" / "p0_qualification" / "evidence" / "gate_a"
                        / "timing_matrix.json")


def _backoff_ladder_boundary(policy: SecAccessPolicy) -> dict:
    """Direct call into the production backoff function at every step boundary."""
    schedule = policy.backoff_schedule_seconds
    observed = {step: policy.backoff_seconds(step)
               for step in (-1, 0, 1, len(schedule) - 1, len(schedule), len(schedule) + 10)}
    expected_clamped_low = observed[-1] == observed[0] == schedule[0]
    expected_clamped_high = (observed[len(schedule) - 1] == observed[len(schedule)]
                             == observed[len(schedule) + 10] == schedule[-1])
    return {
        "schedule": list(schedule),
        "observed_by_step": {str(k): v for k, v in observed.items()},
        "clamps_below_zero_to_first_step": expected_clamped_low,
        "clamps_beyond_last_step_to_final_step": expected_clamped_high,
        "accountable": expected_clamped_low and expected_clamped_high,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps({"gate": result["gate"], "records": len(result["records"]),
                      "report_digest": result["report_digest"]}, indent=2))

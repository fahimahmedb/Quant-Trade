#!/usr/bin/env python3
"""
ML Iteration Orchestrator — Full Pipeline

Runs a batch of tests, audits passing strategies, and produces final report.

Usage:
  python3 scripts/iterate_ml_pipeline.py <batch_name> <num_tests>

Example:
  python3 scripts/iterate_ml_pipeline.py iteration_2 10
  python3 scripts/iterate_ml_pipeline.py iteration_3 50
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[0].parent

def run_batch_tests(batch_name: str, num_tests: int) -> dict:
    """Run the appropriate test script."""
    print(f"\n{'='*80}")
    print(f"RUNNING BATCH: {batch_name} ({num_tests} tests)")
    print(f"{'='*80}")

    if num_tests == 10:
        script = ROOT / "scripts" / "ml_tests_runner.py"
        result_file = ROOT / "results" / "ml_tests_results.json"
    elif num_tests == 50:
        script = ROOT / "scripts" / "ml_tests_50_robust.py"
        result_file = ROOT / "results" / "iteration_3_summary.json"
    else:
        raise ValueError(f"Unsupported test count: {num_tests}")

    # Run the script
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"ERROR running {script}:")
        print(result.stderr)
        return {"error": result.stderr}

    # Parse results
    if result_file.exists():
        with open(result_file) as f:
            results = json.load(f)
        return results
    else:
        print(f"Results file not found: {result_file}")
        return {"error": "No results file"}


def audit_passing_strategies(batch_name: str) -> dict:
    """Run audit on all passing strategies."""
    print(f"\n{'='*80}")
    print(f"AUDITING PASSING STRATEGIES")
    print(f"{'='*80}")

    results_dir = ROOT / "results"
    strategy_files = sorted(results_dir.glob("strategy_*.json"))

    audit_results = {
        "total_strategies": len(strategy_files),
        "passed_without_lookahead": 0,
        "failed_audit": 0,
        "audit_details": [],
    }

    for strategy_file in strategy_files:
        with open(strategy_file) as f:
            strategy = json.load(f)

        # Only audit if it passed the statistical criteria
        if strategy.get("result") != "PASS":
            continue

        # Run audit
        audit_script = ROOT / "scripts" / "anti_data_snooping_audit.py"
        data_path = ROOT / "data" / "nasdaq100_daily.txt"

        result = subprocess.run(
            [sys.executable, str(audit_script), str(strategy_file), str(data_path)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            audit_results["passed_without_lookahead"] += 1
            audit_results["audit_details"].append({
                "file": strategy_file.name,
                "audit_status": "PASS",
            })
        else:
            audit_results["failed_audit"] += 1
            audit_results["audit_details"].append({
                "file": strategy_file.name,
                "audit_status": "FAIL",
            })

    return audit_results


def generate_report(batch_name: str, test_results: dict, audit_results: dict) -> None:
    """Generate final report."""
    print(f"\n{'='*80}")
    print(f"ITERATION REPORT: {batch_name}")
    print(f"{'='*80}")

    report = {
        "batch": batch_name,
        "timestamp": datetime.now().isoformat(),
        "test_results": test_results,
        "audit_results": audit_results,
        "summary": {
            "strategies_passed_tests": test_results.get("passed", 0),
            "strategies_passed_audit": audit_results.get("passed_without_lookahead", 0),
            "recommendation": None,
        },
    }

    # Recommendation logic
    if audit_results.get("passed_without_lookahead", 0) > 0:
        report["summary"]["recommendation"] = (
            f"✅ SUCCESS: {audit_results['passed_without_lookahead']} strategy(ies) passed "
            "both tests and audit. Ready for paper-trading."
        )
    elif test_results.get("passed", 0) > 0:
        report["summary"]["recommendation"] = (
            f"⚠️ CAUTION: {test_results['passed']} strategy(ies) passed tests but "
            "failed audit. Check for lookahead bias."
        )
    else:
        report["summary"]["recommendation"] = (
            "❌ NO PASS: Continue to next iteration. Adjust model/feature combinations."
        )

    # Save report
    report_path = ROOT / "results" / f"report_{batch_name}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(report["summary"]["recommendation"])
    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: iterate_ml_pipeline.py <batch_name> <num_tests>")
        print("  iterate_ml_pipeline.py iteration_2 10")
        print("  iterate_ml_pipeline.py iteration_3 50")
        sys.exit(1)

    batch_name = sys.argv[1]
    num_tests = int(sys.argv[2])

    # Run batch
    test_results = run_batch_tests(batch_name, num_tests)

    # Audit passing strategies
    audit_results = audit_passing_strategies(batch_name)

    # Generate report
    generate_report(batch_name, test_results, audit_results)

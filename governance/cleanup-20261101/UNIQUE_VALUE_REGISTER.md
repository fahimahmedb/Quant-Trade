# Unique Value / Residual Register

This register is intentionally compact. It records only material that prevented pointer deletion or requires later reconciliation.

| Branch | Disposition | Reason | Unique commits vs canonicals | Tree/blob delta |
|---|---|---|---:|---|
| `audit/forensic-checkpoint-20261019` | PROTECTED_ACTIVE_AUDIT | active forensic semantic-reading branch | 91 | YES |
| `audit/owner-recovery-preserved-20261026` | PARK | exact branch ref appears in open issue/comment(s): 44,44 | 0 | YES |
| `blue/master-v2-2026-09-20` | PARK | repository default branch; admin-level default migration not performed by cleanup | 0 | YES |
| `builder/autonomy-e2e-20261012` | PARK | exact branch ref appears in open issue/comment(s): 38,38 | 0 | YES |
| `builder/convergence-wave2-canonical-20261021` | KEEP_ACTIVE | live repository dependency: .github/workflows/wave2-c2-acceptance.yml,.github/workflows/wave2-c2-c0-qualification.yml,.github/workflows/wave2-c2-final-cumulative-qualification.yml,.github/workflows/wave2-c2-mega-e-qualification.yml,.github/workflows/wave2-c2-multisource-late-adversarial.yml,.github/workflows/wave2-c2-multisource-qualification.yml,.github/workflows/wave2-c2-refresh-status-artifacts.yml,.github/workflows/wave2-c2-scientific-economic-seam.yml | 0 | YES |
| `builder/econ-readiness-integration-20261016` | KEEP_ACTIVE | live repository dependency: .github/workflows/economic-readiness-integration-ci.yml | 0 | YES |
| `builder/evidence-store-identity-v2` | PARK | exact branch ref appears in open issue/comment(s): 38 | 0 | YES |
| `builder/issue44-gpt-oss-codex-phase1-remote-20261030` | PARK | exact branch ref appears in open issue/comment(s): 44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44,44 | 0 | YES |
| `builder/live-lab-3d-full-build-20261015` | KEEP_ACTIVE | live repository dependency: .github/workflows/live-lab-3d-ci.yml | 0 | YES |
| `builder/live-lab-native-integration-20261015` | KEEP_ACTIVE | live repository dependency: .github/workflows/live-lab-native-integration-ci.yml | 0 | YES |
| `builder/live-lab-oracle-canonical-20261020` | KEEP_ACTIVE | live repository dependency: .github/workflows/live-lab-oracle-ci.yml | 0 | YES |
| `builder/live-lab-owner-ux-rebuild-20261015` | KEEP_ACTIVE | live repository dependency: .github/workflows/live-lab-3d-ci.yml | 0 | YES |
| `builder/mega-e-autonomous-runtime-20261021` | PARK | exact branch ref appears in open issue/comment(s): 38 | 0 | YES |
| `builder/multi-source-ideation-intake-20261021` | KEEP_ACTIVE | live repository dependency: .github/workflows/wave2-c2-final-cumulative-qualification.yml,.github/workflows/wave2-c2-multisource-late-adversarial.yml,.github/workflows/wave2-c2-multisource-qualification.yml | 0 | YES |
| `builder/oracle-economic-loop-recovery-20261019` | KEEP_ACTIVE | live repository dependency: .github/workflows/oracle-economic-loop-recovery-ci.yml,deploy/oracle-worker.example.json,deploy/oracle_scheduler_install.py,deploy/oracle_v1_host_prepare.py,deploy/oracle_v2_canary.py | 0 | YES |
| `builder/oracle-v2-core-20261020` | KEEP_ACTIVE | live repository dependency: .github/workflows/live-lab-3d-ci.yml,.github/workflows/live-lab-oracle-ci.yml,.github/workflows/oracle-v2-core.yml,deploy/oracle_live_host_prepare.py,deploy/oracle_v2_deploy.py,deploy/oracle_v2_host_prepare.py,scripts/prove_oracle_v2_dry_run.py | 130 | YES |
| `builder/research-os-aggressive-architecture-20261015` | KEEP_ACTIVE | live repository dependency: .github/workflows/research-os-aggressive-architecture-ci.yml,.github/workflows/research-os-aggressive-final-gate.yml,.github/workflows/research-os-canonical-depth-ci.yml,.github/workflows/research-os-canonical-spine-ci.yml | 0 | YES |
| `builder/research-os-autonomous-econ-readiness-port-20261016` | KEEP_ACTIVE | live repository dependency: .github/workflows/economic-readiness-integration-ci.yml | 0 | YES |
| `builder/research-os-autonomous-loop-20261015` | KEEP_ACTIVE | active autonomous-agent working ref | 0 | YES |
| `builder/research-os-vm-autonomy-20261019` | PARK | exact branch ref appears in open issue/comment(s): 38 | 0 | YES |
| `builder/v2-forward-20261020` | KEEP_ACTIVE | live repository dependency: .github/workflows/live-lab-3d-ci.yml,.github/workflows/live-lab-oracle-ci.yml,.github/workflows/oracle-v2-core.yml,deploy/oracle_v2_deploy.py,deploy/oracle_v2_host_prepare.py | 0 | YES |
| `builder/wp1-book-pressure-preexposure-20261028` | PARK | exact branch ref appears in open issue/comment(s): 36,38,36,36,36 | 0 | YES |
| `builder/wp2-single-lineage-binding-20261030` | PARK | exact branch ref appears in open issue/comment(s): 40,42,42 | 0 | YES |
| `claude/data-feeds-6vr22g` | KEEP_ACTIVE | live repository dependency: .github/workflows/data-feeds.yml | 4 | YES |
| `codex/c0-membrane-qualification-20261027` | PARK | exact branch ref appears in open issue/comment(s): 40,38 | 0 | YES |
| `codex/horizontal-completeness-prewave2-20261021` | PARK | exact branch ref appears in open issue/comment(s): 44 | 0 | YES |
| `codex/vertical-depth-prewave2-20261021` | PARK | exact branch ref appears in open issue/comment(s): 44 | 0 | YES |
| `owner/weather-v4-a2-dedicated-harness-builder-decision-2026-10-04` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-execution-authority-draft-2026-10-08` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-execution-authority-e-d2-2026-10-08` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-harness-attestation-decision-2026-10-04` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-harness-suitability-decision-2026-10-04` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-lot2-freezes-2026-10-08` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-lot2-technical-authorization-2026-10-07` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-partial-configuration-decision-2026-10-06` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-residual-d5-final-state-invariant-repair-2026-10-05` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-static-audit-repair-decision-2026-10-05` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-a2-team-charter-ratification-2026-10-08` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-od01-od03-decision-2026-10-04` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-od04-od12-structural-decision-2026-10-04` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `owner/weather-v4-phase-gate-a1-decision-2026-10-04` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/antigravity-gate-b-run-authority-adversarial-precheck-2026-09-21` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/claude-economic-question-falsification-map-2026-09-21` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/claude-economic-v2-2026-09-20` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/claude-first-slice-cohort-geometry-2026-09-21` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/claude-forward-data-2026-09-20` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/claude-post-p0-vertical-build-prep-2026-09-21` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/claude-research-frozen-effect-estimate-prestage-2026-09-21` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/claude-s11-dependence-interval-challenge-2026-09-21` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/codex-wave1-economic-system-2026-09-19` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `parallel/economic-acceleration-2026-09-21` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `recovery/claude-sec-local-20260914` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/close-auction-source-readiness-20261017` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/delta-research-pack-v1-20261015` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/design-v1` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/duebill-source-readiness-20261017` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/economic-reorientation-checkpoint-2026-09-29` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/economic-test-form144-supply-20261017` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/edge-lab-continuous` | KEEP_ACTIVE | live repository dependency: .github/workflows/edge-lab-binance-funding-reversal.yml,.github/workflows/edge-lab-monthend-pension-rebalance.yml,.github/workflows/edge-lab-sector-relative-shock-reversal.yml,.github/workflows/edge-lab-stockbond-joint-stress-rebound.yml,.github/workflows/edge-lab.yml | 0 | YES |
| `research/f2-primary-terms-decision-2026-10-09` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/legacy-economic-reconciliation-20261015` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/paused-lanes-qualification-20261015` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `research/technical-signals-literature-2026-10-10` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `review/blind-roadmap-pass-a-20261027` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `review/independent-architecture-challenger-20261026` | PARK | exact branch ref appears in open issue/comment(s): 44,44 | 0 | YES |
| `review/independent-wp1a-blind-pass-a-20261027` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `review/post-disclosure-pass-b-20261027` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `review/wp2-independent-d40053-20261030` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `reviewer/v1-final-red-team` | KEEP_ACTIVE | live repository dependency: .github/workflows/v1-proof-gate.yml | 0 | YES |
| `sol/scout-crypto-20261008-1847` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `sol/scout-events-f413d` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `sol/scout-macro-tauc-gfs` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `sol/scout-prediction-flb-nr` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `team/weather-v4-a2-coordination-2026-10-08` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `tmp/deep-week-20260713` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |
| `ux/intake-20261015` | DELETE_PROVEN_SAFE | current tip is reachable from retained authority history; no live branch-name/PR/issue/auditor dependency found | 0 | YES |

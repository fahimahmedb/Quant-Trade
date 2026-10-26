# BUILDER CP011 — Task-scoped snapshot observation gap

WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: 99bba9e16fa2bf830e3e13da7bcb4cd91dd77b58
CURRENT_BUILDER_HEAD_DESCRIBED: 99bba9e16fa2bf830e3e13da7bcb4cd91dd77b58
OBSERVED_ORACLE_V2_HEAD: 1e79d039f69da8bef11f935ed538918ef6cc9a1e
SAFE_TO_CONTINUE: TRUE

## Objective / evidence

Continue the bounded Builder stream under CP16, without taking over the Owner's
Oracle/Site integration. CP010 is present and pushed. Its optional composed
projection has no production consumers: repository searches for
`build_edge_observability_projection` find its definition and tests only.
CP002 already identified collection of durable inputs as a potential residual.

Inspected `github_state.Snapshot`, `oracle_worker` stage publication/receipts,
`worker_stages.artifact_path`, V2 epoch/state/sidecar contracts, source
qualification/readiness, CP009's Site/bridge audit and current producer tasks.
The existing Snapshot verifies Git blob identity; the worker binds completed
stages with artifact content hashes, and blocked stages with per-session
receipts. These capabilities must be reused rather than adding a state store.

At the exact observed Oracle commit, metadata inventory includes 16 documentary
research artifacts, 13 mechanism artifacts and no producer/readiness-named
artifact. `economic_test_readiness_v1` can already produce a producer-readiness
specification inside validation packages; its pure helper also accepts a real
producer output and dossier. No collector currently joins those inputs for CP010.

Actual EVENT_DOCUMENT-010 and FUNDAMENTAL-010 stages have engine outputs but no
dossier, and structural screen blockers. INST-FLOW-010 has no mechanism artifact
yet. Therefore absent evidence cannot be relabeled as acquisition readiness, and
a blocked research attempt cannot be mistaken for an unexecuted task or a failed
economic experiment. No outcome/evaluation data was inspected in this audit.

## Confirmed minimal residual

Provide one task-scoped, read-only observation adapter over an exact snapshot:

- accept a pinned snapshot and explicit task ID, never arbitrary artifact paths;
- read only current policy/epoch, that task, its canonical producer stage, and
  that task's last receipt when needed to prove a blocked stage;
- verify active epoch/policy and exact task/artifact/receipt/hash bindings;
- retain source blob identities and snapshot HEAD in the observation hash;
- call existing dossier/readiness/projection functions only when their durable
  inputs actually exist; do not manufacture a dossier for blocked research;
- treat unsupported readiness families and missing/uncommitted artifacts as
  explicit incomplete states, never infer an experiment-ready state;
- preserve task-scoped semantics; do not traverse validator handoffs or pretend
  this is a full lineage, portfolio or deployed Site status view;
- add an offline CLI over local exact Git objects for reproducible inspection.

The CLI must issue only Git read commands, with no fetch, push, mutation or
service management. Explicit caller-supplied catalogs may be used, never inferred.
No source packet, evaluation folder or arbitrary reference is followed/read.

## Verification required before handoff

Tests must reject traversal/cross-task refs, wrong HEAD/blob/content hash,
epoch/policy mismatch, stale receipt generation/session, forbidden outcome or
open authority, and a stage file with no durable task binding. Prove absent,
blocked and successful-dossier cases; use real local Git/Snapshot checks, verify
exact read sets, no writes/network and deterministic hashes. Exercise the CLI
on a fresh, pinned real Oracle commit without changing the autonomous branch.

## CI access / environment boundary

Git remains usable; Actions API access remains unavailable under the observed
restricted policy. An additive draft proposal for `api.github.com` failed with
`stale_base`: environment configuration was published/changed. No network change
was confirmed, no repeated write attempted and no credential requested. The
complete network-only proposal is retained in
`/workspace/.setup/ci-access-proposal.tar.gz`; installation/start fields need no
change. A future setup session must reconcile current custom domains before
saving. This external limit does not block the offline Builder increment.

## Changes / authority / next action

Audit checkpoint only; no code tests needed for this document. All four
authorities remain FALSE, OUTCOME_ACCESSED FALSE, ECONOMIC_RESULT NOT_OBSERVED.
No autonomous task, runtime, source, policy, epoch or Site changed.

Next: implement the bounded reader/CLI and adversarial tests, execute workflow
qualification on the exact code commit, then persist CP012 with local-vs-hosted
evidence distinguished. Final Integrator owns later use by the existing Site.

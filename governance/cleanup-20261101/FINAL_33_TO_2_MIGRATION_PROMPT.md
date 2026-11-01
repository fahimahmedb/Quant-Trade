QUANT-TRADE — FINAL 33 → 2 BRANCH MIGRATION
DEPENDENCY MIGRATION BEFORE DELETION

REPOSITORY
fahimahmedb/Quant-Trade

MISSION TYPE
FINAL SURVIVOR DEPENDENCY AUDIT
DEPENDENCY MIGRATION
EXTERNAL-CONSUMER REBIND
SAFE FINAL BRANCH RETIREMENT

TARGET END STATE

Only two active branches remain:

project/canonical
code/canonical

The previous cleanup already removed 247 branch pointers after proving their exact tips remained reachable from retained authority history. DO NOT restart or re-audit those 247 branches unless a concrete contradictory primary proof appears.

This mission concerns ONLY the current surviving branch set, whatever its fresh count is at start.

============================================================
0. PRIMARY LAW
============================================================

MIGRATE FIRST.
VERIFY SECOND.
DELETE LAST.

A surviving branch must not remain merely because an old file, workflow, issue, comment, automation, runtime config or host checkout still names it.

But it must also not be deleted until that dependency has either:

A. been migrated to project/canonical or code/canonical and verified;
B. been proven historical/non-operational;
C. been preserved as evidence elsewhere with sufficient provenance;
or
D. been classified PARK/BLOCK because the external dependency cannot yet be safely changed.

UNKNOWN IS NEVER DELETE.

Do not let one PARK/BLOCK candidate stop independent migration of the others.

============================================================
1. AUTHORITY — VERIFY FRESH
============================================================

Expected future authority pair:

project/canonical
code/canonical

Fetch fresh heads. Do not trust SHAs in this prompt.

Determine fresh:

PROJECT_CANONICAL_SHA=
CODE_CANONICAL_SHA=
CURRENT_DEFAULT_BRANCH=
CURRENT_REMOTE_BRANCH_COUNT=
OPEN_PRS=
OPEN_ISSUES=
ACTIVE_OR_QUEUED_ACTIONS=
KNOWN_ACTIVE_AUTOMATION_BRANCHES=
ACTIVE_FORENSIC_AUDITOR_REF=

Do not assume the current branch count is still 33.

============================================================
2. PREVIOUS CLEANUP — DO NOT REOPEN WITHOUT CONTRADICTION
============================================================

Read only the durable cleanup outputs needed to understand the surviving set:

governance/cleanup-20261101/CLEANUP_STATE.json
governance/cleanup-20261101/BRANCH_CLASSIFICATION.csv
governance/cleanup-20261101/UNIQUE_VALUE_REGISTER.md
governance/cleanup-20261101/DELETION_RECEIPT.md
governance/cleanup-20261101/INDEPENDENT_SAFETY_REVIEW_2026-11-01.md

governance/BRANCH_RETIREMENT_RECEIPT.json

Do not re-run the 279-branch audit.

Do not restore deleted branches pre-emptively.

If a deleted branch name appears while inspecting a current dependency, first verify whether the dependency can simply be rebound to a canonical branch. Restore only if a concrete current execution need cannot otherwise be satisfied and the exact historical SHA is still required.

============================================================
3. THIS TIME, DEEPLY INSPECT EVERY SURVIVING NON-CANONICAL BRANCH
============================================================

The residue is small enough that every surviving non-canonical branch now deserves a complete bounded dependency review.

For each survivor record:

BRANCH=
TIP_SHA=
WHY_IT_SURVIVED_PREVIOUS_CLEANUP=
UNIQUE_COMMITS_VS_CANONICALS=
UNIQUE_USEFUL_VALUE=
WORKFLOW_REFERENCES=
CONFIG_REFERENCES=
SCRIPT_REFERENCES=
DEPLOYMENT_REFERENCES=
SYSTEMD_CRON_RUNTIME_REFERENCES=
OPEN_PR_REFERENCE=
OPEN_ISSUE_OR_COMMENT_REFERENCE=
AUDITOR_REFERENCE=
AUTOMATION_REFERENCE=
EXTERNAL_HOST_REFERENCE=
DEFAULT_BRANCH_ROLE=
CURRENT_CONSUMER=
MIGRATION_TARGET=
MIGRATION_ACTION=
VERIFICATION=
FINAL_DISPOSITION=

Allowed final dispositions:

DELETE_PROVEN_SAFE
KEEP_ACTIVE_TEMPORARILY
KEEP_EVIDENCE_TEMPORARILY
PARK
BLOCK
UNKNOWN
CANONICAL

No surviving non-canonical branch may finish UNCLASSIFIED.

============================================================
4. SEARCH ALL SURVIVORS, NOT ONLY THE CANONICALS
============================================================

The first cleanup had a bounded blind spot: operational branch-name dependencies were primarily indexed from canonical operational files, with a later specific check of the default branch.

This final pass must search the operational surfaces of EVERY CURRENT SURVIVING BRANCH.

Inspect all text files plausibly capable of creating a live dependency, including at minimum:

.github/workflows/**
.github/actions/**
scripts/**
ops/**
infra/**
deploy/**
deployment/**
systemd/**
services/**
config/**
configs/**
docker/**
k8s/**
kubernetes/**
terraform/**
ansible/**
Makefile
Dockerfile
compose files
Procfile
AGENTS.md
README.md
runtime/runbook/state/router files

Search exact surviving branch names and any deleted branch names referenced by those operational files.

Classify each hit as:

LIVE_DEPENDENCY
HISTORICAL_REFERENCE
DOCUMENTATION_ONLY
TEST_FIXTURE_ONLY
STALE_CONFIGURATION
UNKNOWN

A textual mention alone does not justify retaining a branch.

============================================================
5. GITHUB DEPENDENCIES
============================================================

Inspect fresh GitHub state for each survivor:

- open PR head/base;
- open issue bodies;
- open issue comments;
- workflow branch filters;
- workflow scripts checking out named refs;
- scheduled workflows;
- reusable workflows/actions;
- releases/tags if they point at or semantically depend on a branch name;
- repository default branch;
- rulesets/branch protection if readable;
- deployment/environment references if readable;
- recent workflow runs where branch identity materially affects execution.

IMPORTANT:

An old open issue/comment mentioning a branch is not automatically a live dependency.

For each issue/comment hit classify:

ACTIONABLE_CURRENT_DEPENDENCY
or
HISTORICAL_MENTION_ONLY

If historical only, update the durable current state/issue linkage if necessary and do not retain the branch solely because the text exists.

============================================================
6. KNOWN EXTERNAL SYSTEMS
============================================================

Search all external systems to which the mission actually has authorized access.

Examples include:

- authenticated existing VM/host;
- systemd unit files;
- timers;
- cron entries;
- deployed environment/config files;
- checked-out Git branch/ref on the host;
- running process command lines;
- deployment scripts;
- automation/workflow definitions;
- persistent worker state;
- any durable orchestration state visible to the agent.

START READ-ONLY.

For every observed external reference record:

SYSTEM=
LOCATION=
OLD_BRANCH=
WHY_USED=
TARGET_CANONICAL=
SAFE_TO_REBIND=
BACKUP_OR_ROLLBACK=
MIGRATION_EXECUTED=
POST_MIGRATION_TEST=

Do not claim external absence from systems you cannot access.

If a known external consumer may depend on a branch but cannot be inspected:

EXTERNAL_DEPENDENCY_UNKNOWN
→ PARK THAT BRANCH ONLY.

Do not global-stop the mission.

============================================================
7. ACTIVE AUTOMATIONS / AGENTS
============================================================

Any branch currently used by an active autonomous agent, scheduled task or worker must be migrated before deletion.

Do not simply kill the automation to achieve two branches.

Preferred sequence:

1. identify the exact current branch/ref;
2. identify whether its current useful state already exists on code/canonical/project/canonical;
3. migrate the automation configuration to the appropriate canonical branch;
4. verify one bounded successful wake/run after rebinding where execution access permits;
5. only then retire the old branch.

If automation configuration is outside available permissions:

PARK the branch with an exact action required.

Do not invent success.

============================================================
8. DEFAULT BRANCH MIGRATION
============================================================

The historical default branch must not remain merely because GitHub requires one default branch.

Determine which canonical branch should become repository default.

Default candidate should be selected from:

project/canonical
or
code/canonical

Choose based on the repository’s intended entrypoint and operational consequences, not naming preference.

Before changing default branch verify:

- workflows whose behavior depends on default-branch context;
- scheduled workflows;
- relative links/readme entrypoint;
- branch protection/rulesets where visible;
- scripts/API calls assuming the old default;
- GitHub Pages/deployment assumptions if any;
- external clones/checkouts where visible.

If permissions allow and all migration gates pass, change the default branch and verify repository behavior.

If admin permission is unavailable:

BLOCK only deletion of the old default branch.

Continue all other migrations.

============================================================
9. UNIQUE VALUE MIGRATION
============================================================

For every survivor with commits not reachable from the canonicals, determine whether those commits contain current material value.

Classify unique value as:

CODE_CAPABILITY
BUG_FIX
TEST_ORACLE
WORKFLOW
RUNTIME_CONFIG
RECOVERY_CAPABILITY
SCIENTIFIC_PROTOCOL
SCIENTIFIC_NEGATIVE_RESULT
SCIENTIFIC_MEMORY
DATASET_IDENTITY
QUALIFICATION_EVIDENCE
SECURITY_HARDENING
DOCUMENTATION_ONLY
HISTORICAL_ONLY
NO_CURRENT_VALUE
UNKNOWN

Use:

REUSE > CONNECT > PORT > REPAIR > BUILD

Do not merge a whole historical branch merely to preserve one useful file.

Port the smallest necessary current semantics to:

code/canonical for executable product/runtime/tests/workflows;
project/canonical for project state, decisions, scientific memory, provenance and durable evidence.

After porting, qualify the exact canonical SHA containing the migrated material.

Construction is not qualification.
Qualification is not activation.
Activation is not end-to-end proof.

============================================================
10. SCIENTIFIC MEMORY MUST SURVIVE
============================================================

Before retiring a scientific/research branch, verify that materially relevant memory is durably represented:

- hypothesis/experiment identity;
- protocol/freeze identity;
- datasets/provenance;
- holdout/exposure history;
- multiplicity/family history where relevant;
- negative result;
- falsification;
- known-invalid prior result;
- qualification receipt;
- next admissible action if any.

The branch itself does not have to survive if the evidence does.

If exact historical Git lineage itself is materially required and cannot yet be represented safely elsewhere:

KEEP_EVIDENCE_TEMPORARILY.

Do not delete merely to hit the number 2.

============================================================
11. WORKFLOW MIGRATION
============================================================

For workflows that currently depend on surviving old branches:

1. identify why the old branch is referenced;
2. determine whether that branch contains unique code or merely acts as a stable ref;
3. move required executable semantics into code/canonical;
4. update workflow checkout/ref/filter semantics to code/canonical or project/canonical as appropriate;
5. execute the smallest decisive workflow test;
6. verify the exact migrated workflow SHA;
7. only then retire the old branch.

Do not preserve an obsolete branch merely because a workflow can easily be changed.

Do not change scientific semantics while migrating workflow plumbing.

============================================================
12. RUNTIME / HOST MIGRATION
============================================================

If an authenticated known host references an old branch:

- capture current config and SHA first;
- identify current deployed bytes;
- prove equivalent/migrated bytes exist on code/canonical;
- change only the branch/ref binding required for migration;
- preserve rollback information;
- perform a bounded health/continuity verification;
- do not run a new economic experiment merely to prove branch migration.

A host that is healthy before migration must not become the experiment surface for unrelated changes.

============================================================
13. DELETION GATE — STRICTER THAN FIRST CLEANUP
============================================================

A surviving non-canonical branch becomes DELETE_PROVEN_SAFE only if ALL applicable conditions pass:

1. fresh remote tip SHA known;
2. SHA unchanged since final classification;
3. no open PR operational dependency;
4. no actionable open issue dependency;
5. no workflow dependency remains;
6. no runtime/config/deployment dependency remains;
7. no active automation/agent dependency remains;
8. no known external host dependency remains;
9. default-branch role migrated if applicable;
10. any unique useful code is present and qualified on code/canonical;
11. any unique project/scientific evidence is present on project/canonical or equivalent durable archive;
12. exact provenance/recovery identity is recorded;
13. current tip remains reachable from a retained authority OR all materially required unique bytes/provenance have been durably preserved;
14. a fresh exact-name search across all current survivors finds no live dependency;
15. adversarial counterexample search finds no concrete reason to retain it.

If one condition fails:

DO NOT DELETE.

Classify PARK/BLOCK/KEEP_* and continue.

============================================================
14. TRANSACTIONAL DELETION
============================================================

For every final deletion:

- re-read remote SHA immediately before mutation;
- if SHA changed → PARK;
- use server-side force-with-lease against the exact SHA;
- never use blind force;
- verify remote absence after deletion;
- record deleted branch + exact SHA + canonical replacement + migrated dependency proof.

Persist state before destructive mutation and after each deletion batch.

Recommended batch size for this small residue:

5–10 branches.

============================================================
15. DO NOT CREATE ANOTHER LARGE GOVERNANCE SYSTEM
============================================================

Use the existing cleanup directory.

Only maintain/update these bounded durable artifacts:

governance/cleanup-20261101/FINAL_MIGRATION_STATE.json
governance/cleanup-20261101/SURVIVOR_DEPENDENCY_MATRIX.csv
governance/cleanup-20261101/MIGRATION_RECEIPT.md
governance/cleanup-20261101/FINAL_DELETION_RECEIPT.md

Do not generate dozens of reports.

============================================================
16. REQUIRED DEPENDENCY MATRIX
============================================================

One row per current survivor with at least:

BRANCH
TIP_SHA
PREVIOUS_REASON_RETAINED
UNIQUE_COMMITS
UNIQUE_VALUE
GITHUB_DEPENDENCY
WORKFLOW_DEPENDENCY
RUNTIME_DEPENDENCY
AUTOMATION_DEPENDENCY
EXTERNAL_DEPENDENCY
ISSUE_REFERENCE_CLASS
DEFAULT_BRANCH_ROLE
MIGRATION_TARGET
MIGRATION_COMMIT
TEST_EXECUTED
TEST_RESULT
CURRENT_STATUS
FINAL_DISPOSITION
DELETION_SHA

The matrix is the primary anti-memory-loss artifact.

============================================================
17. CHALLENGE EACH MIGRATION
============================================================

Before deleting each branch ask:

Could an actual current consumer still resolve this exact branch name?

Did I merely copy files, or did I preserve behavior?

Did I move evidence but lose provenance?

Did I change scientific semantics while “migrating plumbing”?

Did I qualify the exact canonical SHA containing the replacement?

Could a scheduled or external process still be using the old ref?

Am I preserving a stale branch because a historical comment mentions it?

Am I about to delete a branch with unique commits merely because its current tree looks similar?

If a concrete counterexample survives, investigate that counterexample only.

Do not reopen full repository archaeology.

============================================================
18. ORDER OF OPERATIONS FOR SPEED
============================================================

Process survivor families in this order:

A. branches retained only because of stale/historical issue comments;
B. branches referenced by workflows but with zero unique useful commits;
C. branches referenced by configs/runtime but whose semantics already exist canonically;
D. active automation/agent branches;
E. default branch;
F. branches containing unique code/evidence;
G. active auditor/meta-audit evidence branches last, after their required evidence has been absorbed or archived.

This order should eliminate easy dependencies first and reserve expensive semantic migration for the small true residue.

============================================================
19. AUDITOR NON-INTERFERENCE
============================================================

If the forensic auditor is still active:

- do not delete its active branch;
- read only its latest durable cursor when needed;
- if it currently depends on another survivor, PARK that survivor;
- continue independent migrations;
- when the auditor finishes, perform one delta reconciliation only.

Do not restart its chronology.

============================================================
20. SUCCESS CONDITION
============================================================

Preferred success:

REMOTE_BRANCH_COUNT=2

REMAINING_BRANCHES=
project/canonical
code/canonical

But do NOT force this number if a proven unresolved external dependency remains.

Acceptable intermediate result:

2 + N explicitly PARK/BLOCK branches

where every residual branch has:

- exact dependency;
- exact missing permission/proof;
- exact migration action;
- no vague “keep just in case”.

The mission is complete only when every survivor is either deleted, canonical, or explicitly blocked by a concrete unresolved dependency.

============================================================
21. FINAL VERIFICATION
============================================================

After final deletions:

1. fetch fresh remote branches;
2. verify canonical heads;
3. search the entire remaining repository for deleted branch names in live operational surfaces;
4. verify default branch;
5. verify critical workflows/configs;
6. verify known active automation bindings where accessible;
7. verify known authenticated host bindings where accessible;
8. verify no open PR depends on deleted refs;
9. verify scientific/evidence registers remain recoverable;
10. verify working tree and repository state are clean.

Do not claim SYSTEM-WIDE ZERO RISK for inaccessible external systems.

Use:

PASS
PASS_WITH_BOUNDED_EXTERNAL_UNKNOWN
BLOCK

============================================================
22. FINAL RESPONSE CONTRACT
============================================================

Return exactly enough evidence to resume:

FINAL_MIGRATION_STATUS=
PROJECT_CANONICAL_SHA=
CODE_CANONICAL_SHA=
DEFAULT_BRANCH=
BRANCH_COUNT_START=
BRANCH_COUNT_END=
BRANCHES_DELETED_THIS_MISSION=
BRANCHES_REMAINING=
DEPENDENCIES_MIGRATED=
WORKFLOWS_REBOUND=
AUTOMATIONS_REBOUND=
EXTERNAL_HOST_REFS_REBOUND=
UNIQUE_CODE_PORTED=
SCIENTIFIC_EVIDENCE_PORTED=
PARK=
BLOCK=
UNKNOWN=
KNOWN_EXTERNAL_UNVERIFIED=
FINAL_DELETION_RECEIPT=
FINAL_MIGRATION_STATE=
NEXT_ACTION=
FINAL_VERDICT=

For every residual non-canonical branch state in one line:

BRANCH → EXACT_REASON → EXACT_NEXT_ACTION

============================================================
START
============================================================

1. Fresh-fetch all refs and repository metadata.
2. Read current cleanup state and survivor register only.
3. Build the fresh survivor dependency matrix.
4. Search operational surfaces on EVERY survivor.
5. Reconcile GitHub issues/PRs/workflows/default branch.
6. Inspect known external systems read-only where authorized.
7. Classify each dependency as live, historical, stale or unknown.
8. Migrate easy branch-name dependencies first.
9. Port only genuinely unique useful value.
10. Qualify exact canonical replacements.
11. Rebind active automations/runtime where authorized and verify.
12. Re-read every candidate SHA.
13. Delete only DELETE_PROVEN_SAFE with lease.
14. Persist receipts after each bounded batch.
15. Perform one final whole-residue verification.
16. End with exactly two branches if and only if all dependencies are safely migrated; otherwise retain only concrete PARK/BLOCK exceptions.

DO NOT RE-AUDIT THE 247 DELETED BRANCHES.
DO NOT RESTORE THEM PRE-EMPTIVELY.
DO NOT BUILD A NEW ARCHITECTURE.
DO NOT USE OLD OPEN COMMENTS AS PERMANENT BRANCH AUTHORITY.
DO NOT DELETE UNIQUE VALUE TO HIT A NUMERIC TARGET.
DO NOT LET ONE BLOCKER STOP THE REST OF THE CLEANUP.

OPTIMIZE FOR:

TWO-BRANCH AUTHORITY
+
NO BROKEN DEPENDENCY
+
NO LOST CODE
+
NO LOST SCIENTIFIC MEMORY
+
NO STALE BRANCH-NAME CONSUMER
+
FAST BOUNDED EXECUTION
+
RECOVERABLE EVIDENCE

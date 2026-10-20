# CP056 — release source is not scientific state authority

STATUS=AUDIT_BEFORE_HARDENING
BASE=103af12
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

CP055: 754 configured / 263 core V2 / 268 broader Research OS and composed JS
gates PASS; exact-head local qualification and real read-only entrypoint PASS.

CONCRETE CONVERGENCE BLOCKER: deploy.oracle_v2_deploy.verify_ci hardcodes both
the scientific state branch and CI source branch to builder/oracle-v2-core-20261020.
A fully qualified isolated Builder executable therefore cannot supply its exact
CI evidence to this qualifier, even though scientific state must continue to use
Oracle. Branch identity and executable SHA are distinct provenance dimensions.

HARDEN/ADAPT: explicitly allow only the two Owner-authorized source rails (Oracle
and this Builder), with the legacy default Oracle. Bind both required successful
workflow runs to the same explicitly declared source branch and exact release SHA;
record server-observed head_branch in evidence. Reject unknown/null/ambiguous source
branches before network access. State repository/branch/cache/lane validation stays
unchanged and cannot be redirected by the source-branch field.

BOUNDARY RETAINED: prepare must still reject active V2. This does not implement
an unqualified hot upgrade, relax root/CI/VM/model/canary/authority gates, install
a release, rewrite scientific identity, or remove the observer's old-core pin.
The explicit V2→V2 repair handoff still needs actual host facts/access. Future
root preparation may name an authorized source branch via the Python prepare API;
fixed no-argument root controls remain unchanged.

NEXT: adversarial tests for matching legacy/Builder provenance, foreign branch,
mixed branch runs, wrong SHA/workflow/status/conclusion, unchanged canonical state
branch enforcement, and early preparation rejection. Preserve all four membranes.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
DEPLOYMENT_PERFORMED=FALSE

# SEC Form-4 — existing census reuse qualification

Date: 2026-10-12
Branch: `research/edge-lab-continuous`
Economic outcomes accessed: **NO**
Fresh SEC crawl performed: **NO**

## Decision

`PARK_DATA` for the dependency on the previously-built deterministic census.

This is **not** a rejection of the Form-4 mechanism or expression. It only records that the existing census cannot currently be reused cheaply from the durable GitHub surfaces inspected, so Discovery must not spend another cycle rebuilding it by default.

## Existing work verified

Known branch: `builder/sec-form4-census-v2a`
Observed HEAD: `08dcfc39b4b22e0b25e54edde7b6accbb2bc4502`

The frozen mission exists and defines the intended deterministic population:
- official SEC EDGAR ownership/raw filing inputs;
- 2020-01-01 through 2026-06-30;
- original Form 4 only;
- non-derivative `P` + acquired `A`;
- director/officer owners;
- exact issuer/reporting-owner CIK identity;
- ambiguous joint-owner rows excluded;
- 2 distinct qualified insiders in a trailing 10-XNYS-session crossing/re-arm rule;
- `event_time` is the earliest public observability from EDGAR acceptance timestamps;
- returns/P&L were forbidden in the census mission.

## Durable-output lookup performed

- Current branch HEAD does not expose `artifacts/sec_form4_census/` through repository contents.
- Latest census-proof run #42 (`35416321420`) completed `failure`; its artifact listing is empty.
- Earlier successful visible census-workflow runs #32 (`34880954696`) and #30 (`34878811352`) have empty artifact listings and correspond to takeover/hotfix proof work rather than a published census artifact.
- Successful bootstrap run #4 (`34814829221`) also has an empty artifact listing.
- Run #37 (`34902024018`), previously treated as an authoritative continuation point, completed `failure`, not a successful published census.
- No commit matching a deterministic census publication was found in the current branch history search performed here.

This does not prove no recoverable cache exists anywhere in GitHub infrastructure; it proves that no reusable census artifact is cheaply available from the durable repository/action surfaces inspected in this bounded recovery pass.

## Consequence

Do **not** start a fresh SEC crawl merely to unblock Discovery. Do not infer that implementation code equals an available census. Preserve the prior mission/branch as historical work.

A future Form-4 economic test remains eligible if a deterministic census artifact becomes cheaply recoverable or if a separately declared low-cost population can be assembled without outcome contamination. Any such test must be predeclared before price access and use filing-public `event_time`, never transaction date, as its information clock.

## Next

Return to the Discovery frontier and choose a different high-decision-leverage / low-data-friction candidate. Prefer an already-predeclared V4.2 expression whose first result can be obtained from public zero-cost data without architecture work. The existing France OAT/Bund pilot is a candidate, but its event set and public yield-pair route must be frozen before outcome access; policy-announcement capture remains prospective and date-gated.

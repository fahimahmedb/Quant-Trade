# France OAT / Bund L1 — rights correction before outcome access

Date: 2026-10-12
Affected declaration: `disc-france-oat-bund-debt-release-l1-v1`
Economic yield outcomes accessed/joined: **NO**

## Decision

`PARK_DATA` for this exact TEC10-based expression **before any market outcome access**.

This note supersedes the earlier source-pair conclusion in `france-oat-bund-l1-source-pair-2026-10-12.md` on one decisive dimension: rights to create the derived France-minus-Germany series.

## New primary-source fact

The Banque de France CNO-TEC publication notice states that:

- CNO-TEC indices are made available free to site visitors exclusively for information;
- they may not be redistributed;
- visitors may not create derived data having CNO-TEC indices as underlying without express written Banque de France authorization.

Official page example carrying the notice:
`https://www.banque-france.fr/fr/statistiques/taux-et-cours/indices-obligataires-2026-05-26`

The predeclared L1 requires computing `FR_TEC10 - DE_10Y` and changes of that spread. That is derived data using TEC10 as an underlying. No written authorization is held in this project.

## Consequence

Do not fetch/join TEC10 outcomes for `disc-france-oat-bund-debt-release-l1-v1`.
Do not silently substitute another France series inside that experiment after this rights fact.
Do not reinterpret the park as evidence against France sovereign repricing.

The event population and thresholds were frozen before outcomes and remain useful as a reusable *design reference*, but a different permitted France proxy requires a **new linked expression** with its own predeclaration and bias map.

## Verdict scope

- exact TEC10/Bundesbank expression: `PARK_DATA`
- broader France sovereign-repricing mechanism: OPEN / NOT TESTED by this expression
- paid data or written-license pursuit: NOT AUTHORIZED

## Next

Return to the Discovery frontier. Prefer a mechanism with official zero-cost data and no ambiguous derivative-use restriction. The existing Treasury-auction inventory-pressure family is a candidate for a new cheap L1 because U.S. Treasury publishes both auction metadata and daily 5-year par-yield data publicly; any new expression must be separately frozen before outcome access and must not claim futures execution.

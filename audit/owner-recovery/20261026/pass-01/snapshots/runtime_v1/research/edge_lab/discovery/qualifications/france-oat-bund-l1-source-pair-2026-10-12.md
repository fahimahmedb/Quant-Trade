# France OAT / Bund L1 — public source-pair qualification

Date: 2026-10-12
Parent design: `research/edge_lab/discovery/v4_2_pilot/disc-france-oat-bund-l1-v0.md`
Economic event/outcome join performed: **NO**
Return series inspected around candidate events: **NO**
Paid source/account used: **NO**

## Decision

`SOURCE_PAIR_QUALIFIED_FOR_DECLARATION_ONLY`

The public France/Germany daily yield routes are adequate to support a **coarse L1 relative-spread proxy** if and only if the event population/classification is frozen before any event-return join. They do not establish futures P&L or execution.

## France proxy

Banque de France publishes daily `TEC-n` constant-maturity Treasury indices, including TEC10, and states that historical observations are available in a consolidated history file.

Official page family: `https://www.banque-france.fr/fr/statistiques/taux-et-cours/indices-obligataires-*`

Definition recorded by Banque de France: TEC-n is the actuarial yield of a fictitious Treasury security whose remaining life is constantly n years, obtained by interpolation between Treasury securities bracketing that maturity.

Selected L1 proxy: `TEC10` daily.

## Germany proxy

Deutsche Bundesbank publishes a daily Svensson-estimated term structure for listed Federal securities with downloadable time series. The 10.0-year spot-yield series is:

`BBSIS.D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A`

Official source page: `https://www.bundesbank.de/en/statistics/money-and-capital-markets/interest-rates-and-yields/daily-term-structure-on-listed-federal-securities-651570`

Selected L1 proxy: daily 10-year German Federal-security term-structure spot rate.

## Bias / comparability

The pair is deliberately coarse:

- France TEC10 = constant-maturity interpolated actuarial Treasury yield.
- Germany series = 10-year point from a Svensson-estimated spot term structure on listed Federal securities.
- Both are daily public sovereign-rate proxies, but construction methods are not identical.
- This mismatch can add level/noise bias and makes the test unsuitable for executable P&L, precise basis-point DV01 conversion, CTD, carry, roll or intraday reaction claims.
- Because the L1 target is only same-sign **relative daily repricing** around frozen official fiscal/financing events, the pair may be used as a directional/discovery proxy with these limits predeclared.

## Inference rights from this qualification

This source check can support only creating the linked executable L1 declaration. It cannot support or kill the economic mechanism by itself.

No yield observations may be joined to events until all of the following are frozen in a linked declaration:

1. official event IDs/dates/public timestamps;
2. source for each event;
3. ex-ante adverse/benign/neutral classification rule;
4. exclusions and clustering rule;
5. exact before/after daily-observation rule;
6. sign convention;
7. adequacy threshold / minimum event-count logic;
8. `TEST_CAN_KILL`, `TEST_CAN_SUPPORT`, `TEST_CANNOT_SAY`;
9. one fixed cheap red-team/control;
10. prior exposures and hashes.

## Next

Build the smallest defensible official French fiscal/financing event set **without looking at France/Germany yield outcomes**. Prefer mechanically enumerable official releases over remembered/famous episodes. If that cannot be done cheaply without hindsight, `PARK_DATA`; do not relax the event rule after seeing prices.

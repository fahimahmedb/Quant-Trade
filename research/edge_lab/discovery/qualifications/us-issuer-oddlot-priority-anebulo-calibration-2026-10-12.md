# US issuer odd-lot priority — Anebulo calibration closure

DECISION = CALIBRATION_ONLY
FRESH_ECONOMIC_EVIDENCE = NO
FAMILY = us-issuer-oddlot-priority
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

This closes the historical Anebulo implementation as a calibration example and prevents it from being miscounted as a fresh L1.

## Primary-document resolution

- Original commencement: Anebulo Pharmaceuticals SC TO-I, accession `0001493152-25-028828`, filed and accepted by EDGAR on 2025-12-22; EDGAR filing detail reports accepted time `2025-12-22 17:25:22`.
- Original Offer to Purchase: Exhibit (a)(1)(A), dated 2025-12-22, fixed cash price $3.50/share, up to 300,000 shares, expiration one minute after 11:59 p.m. New York City time on 2026-01-26 unless extended/terminated.
- The full Offer to Purchase confirms Nasdaq symbol ANEB and states that nominee/broker deadlines can be earlier than issuer expiration.
- Amendment No. 1: accession `0001493152-26-000914`, accepted 2026-01-08 09:21:12. It changes background/conditions but does not replace the stated 2026-01-26 expiration in the original offer.
- Amendment No. 2 / result amendment exists after expiration. During documentary source resolution, public search output exposed completion/result information. Therefore this historical case is contaminated for confirmation and cannot be used as untouched evidence.

The earlier client-instruction letter's isolated `2006` year is therefore a document typo/inconsistency, not a viable alternative clock: the controlling original Offer to Purchase states 2026-01-26 and the amendment chain is consistent with that offer.

## Price-route documentation

Nasdaq's public Historical Data surface states that historical data provides up to 10 years of daily historical stock prices and volumes. This is sufficient documentary evidence for a public EOD route concept, but symbol-level availability must still be verified prospectively before reading a selected event's payload. If the selected symbol is not retrievable, the prospective protocol requires PARK_DATA rather than event substitution.

No ANEB entry-price payload was intentionally fetched for an economic calculation in this closure.

## Exposure receipt

While resolving the document chain, public search results exposed Anebulo preliminary/final result snippets. This is completion-outcome exposure. It is recorded explicitly and permanently disqualifies Anebulo from being counted as a fresh prospective case. No profitability, P&L, Sharpe or edge claim is made from Anebulo.

## Next

The linked prospective protocol is:
`research/edge_lab/discovery/experiments/disc-us-issuer-oddlot-priority-prospective-l1-v1.md`

Its prospective clock starts at `2026-10-12T20:00:00Z`. Only the first chronologically qualifying issuer-tender event strictly after that T0 may enter the prospective sample. Historical exposed issuer names are excluded.

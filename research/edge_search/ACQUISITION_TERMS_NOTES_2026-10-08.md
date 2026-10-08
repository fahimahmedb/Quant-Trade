# Acquisition terms-of-use notes (read before any acquisition)

Date: 2026-10-08. Read-only documentation fetches; no market data downloaded. Fetch summaries come from a small model, so they are not verbatim legal text; re-read the primary document at manifest time.

## F1 — Binance Vision (`data.binance.vision`)

Source: `https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md` (summary by fetch tool).

- Licence: CC BY-NC-SA 4.0 plus the Vision Dataset Terms. Non-commercial research (academic research, personal non-production backtesting) is the permitted class.
- Prohibited: live proprietary trading, automated commercial order generation, selling signals, integrating the data into trading bots or commercial products (Sections 4.2–4.4); sublicensing/hosting; evading rate limits (7.1–7.2).
- Redistribution of derivatives must credit Binance Vision and stay CC BY-NC-SA 4.0 (4.5). Do not imply endorsement (8.2).
- Checksum convention: each zip has a `.CHECKSUM` file in the same folder; verify with `sha256sum -c`.

Consequences recorded for the project:
1. Paper/shadow research on this data is inside the permitted class. **Raw files will not be committed to the repository** (redistribution); the repository stores manifests, hashes, and derived statistics only.
2. **A positive F1 result could not be promoted to live trading on the strength of this dataset alone.** Any later live use needs a separately licensed or REST-sourced dataset. This caveat is part of the F1 pre-registration, and it does not change the research value of a negative result.
3. Acquisition uses plain file downloads with a generic User-Agent and a conservative rate (no parallel flood).

## F2 — Kalshi

- `docs.kalshi.com/getting_started/historical_data.md`: the page states no authentication requirement, no earliest date, no rate limits, no data-use terms; historical cutoffs advance over time and pagination is cursor-based.
- `kalshi.com/regulatory/rulebook`: HTTP 429 at fetch time; terms **not read**.
- **Gate before acquisition:** read the Kalshi API/market-data terms and make one unauthenticated metadata call. If registration, an account or a key is required, F2 is re-routed and no workaround is attempted.

## F3 — SEC EDGAR / Insider Transactions Data Sets

- From the audit agent: SEC fair-access rules, maximum 10 requests per second, a declared User-Agent, no key, free; the data-set page states no licence. Re-confirm at manifest time.
- The User-Agent for SEC requests must identify the research project without the user's personal email address unless the Owner supplies a contact string; absent an Owner-approved contact, F3 acquisition is deferred (this is a compliance boundary, not a blocker for F1/F2).

## Rule

No outcome data is downloaded before (a) the manifest and pre-registration for that family are published, (b) Codex's challenge window has closed, and (c) the family's terms note above is cleared.

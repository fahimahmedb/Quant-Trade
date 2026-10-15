# Documentary adapter compatibility review

## Demonstrated insufficiency

The auxiliary EngineAdapterOutput schema forced synthetic_only=true. That rule
was suitable for the development fixture but could not truthfully carry the
primary documentary inputs required by work lot B01. Relabeling captured data
as synthetic or calling fixture tests real evidence would be incorrect.

## Bounded extension

The six canonical contracts are unchanged. The existing auxiliary engine output
keeps the same fields and run(source, context) interface. Its evidence-mode
boolean may now be false only with qualified documentary evidence attached to
the candidate. Synthetic callers and existing fixtures retain their prior mode.

The first supported primary document is Apple's public FY2025 financial
statements. The adapter extracts annual revenue, operating income, operating cash
flow and capital-expenditure magnitude from one consistent twelve-month basis.
It preserves the original PDF digest, primary URL, numeric-cell representation,
extraction spans, page/column provenance, units, period and capture time.
The columns were also checked visually against PDF pages 1 and 3.

Availability is conservatively the actual public capture time. The field named
published_at uses the same bound, explicitly labeled FIRST_VERIFIED_PUBLIC_CAPTURE_NOT_HISTORICAL_PIT.
This does not reconstruct historical source availability or assert publication
at that exact instant. The original raw PDF is not bundled with the derived
numeric capture; its digest and public locator permit an independent recheck.
Capture provenance is a recorded acquisition receipt, not a publisher signature.
Revision status is CAPTURED_VERSION_AS_OF_RETRIEVAL. The current download is
not asserted to be the original version published in 2025.

The offline runner can replay these pinned accounting transformations. It does
not run an economic experiment or consume prices, returns or future outcomes.
Derived free cash flow is operating cash flow less capital expenditures; it is
an arithmetic diagnostic, not an estimate of alpha or a valuation recommendation.

## Scope and remaining limits

- Only the Fundamental primary-document adapter is qualified in this increment.
  The exact FY2025 annual basis and Apple provider are checked; this is not a
  claim that arbitrary company documents can already be ingested.
- Event, Quant, Flow and Archaeology documentary adapters still need their own
  provider/period/unit/clock evidence. Synthetic depth tests are retained.
- No common scientific contract, authority flag, production worker, schedule or
  live deployment changes.
- A documentary engine output alone does not establish cost/capacity feasibility,
  independent scientific validation, a frozen economic test or forward authority.
- Prospective/decay activation, market outcomes, allocation and orders remain closed.

This is a Builder compatibility review, not an independent Astra audit.

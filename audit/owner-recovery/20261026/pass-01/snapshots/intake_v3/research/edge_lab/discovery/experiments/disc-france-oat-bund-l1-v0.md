# disc-france-oat-bund-l1-v0

EXPLORATORY. Pre-declared 2026-10-11T22:23:23.734417+00:00; previous repository head9e452f314fa292da1862ec885082608fc807bd10. No yield/return data acquired before this declaration.

- ID: disc-france-oat-bund-l1-v0
- mechanism: fiscal-disclosure risk may produce delayed relative repricing of French sovereign debt against Germany.
- who_pays: investors repricing fiscal risk with delay; a larger risk premium is not automatically mispricing.
- why_persist: constrained mandates/information processing; ECB backstop and anticipated releases are strong contradictions.
- level: L1.
- question: does a fixed short-France/long-Germany relative-yield expression after scheduled EDP releases exhibit material delayed drift?
- proxy: ECB daily10Y benchmark sovereign yield series, current vintage,2022–2025. Indicative yield changes, NOT executable PnL. Only two predeclared API URLs in manifest; no substitute if absent.
- known_biases: current-vintage/revised benchmark yields; no futures roll, CTD/DV01/duration/convexity/financing/carry or fills; small dependent event set; no measured fiscal surprise, other contemporaneous news; anticipated information; crisis and country narrative are already in LLM knowledge. Direction is a deliberately narrow bearish expression, not a prediction of French default.
- fixed_rule: eight scheduled Eurostat EDP release dates 2022-04-22, 2022-10-21, 2023-04-21, 2023-10-23, 2024-04-22, 2024-10-22, 2025-04-22, 2025-10-21. These calendar dates are fixed ex ante, not selected by prices; calendar reference https://ec.europa.eu/eurostat/web/government-finance-statistics/publications . On each date use first common daily observation strictly AFTER release date as entry; cover on fifth subsequent common daily observation. Entry must be within7calendar days, exit within12days of entry; require all8 events. Spread=France10Y minus Germany10Y in basis points. Gross payoff proxy=exit spread minus entry spread (shortFrance, longGermany with idealised equal DV01). Report all8 changes, mean/median/worst and calendar-year totals; no sign filter, event substitution or alternate horizon. Estimate95percent descriptive year-block bootstrap mean with4 year blocks,2000draws,seed41012; no confirmatory significance.
- cost_assumption: subtract2bp round-trip centrally,4bp stress from each spread change; arbitrary conservative screening allowances, not historical quote costs or capital returns. Duration/roll/financing remain unmodelled; no EUR/PnL/Sharpe claim. Break-even cost=mean gross bp.
- max_time_minutes:60; two requests only, each<=30s and1048576bodybytes, batch<=120s/2MiB, no retry, account or paid access.
- kill_if: complete valid8-event sample and mean gross<=0 or central-net mean<=0; kill exact delayed bearish EDP expression ONLY, not the broader fiscal mechanism. No inference if calendars/units/sampling prove inconsistent.
- promote_if: complete sample, central-net mean>=3bp, stress-net positive and at least6/8 gross positive. Otherwise PARK mixed/weak. PROMOTE_HIGH forbidden at L1. Even PROMOTE justifies an L2 surprise/benchmark red-team before futures reconstruction.
- prior_exposures: PRIVATE_UNKNOWN; public French fiscal/ECB narrative and incidental TEC10 quote2026-09-25=4.63percent already exposed; not used to select dates/thresholds. This is one expression,two fixed cost scenarios; effectiveM UNKNOWN. V4.2 design pilot preserved and not silently claimed as executed.
- RESULT: declared France daily SDMX key HTTP404; zero rows. Germany not fetched. Economic question remains untested.
- DECISION: PARK (PARK_DATA).
- NEXT: one bounded acquisition/calculation after publication; any missing series => PARK without selecting a different window.

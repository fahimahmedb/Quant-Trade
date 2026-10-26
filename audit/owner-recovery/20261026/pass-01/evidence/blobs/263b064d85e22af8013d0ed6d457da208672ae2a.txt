# Quant-Trade — Legacy Negative Knowledge

Date: 2026-10-15  
Rule: a failed expression, data route or implementation does **not** kill a broader mechanism unless the historical evidence had scope and power to do so.

| Item | Historical outcome | NEGATIVE_KNOWLEDGE | FALSIFICATION_SCOPE | TRANSFERABLE_LESSON |
|---|---|---|---|---|
| TSR-NDX-001 | `REJECT_RESEARCH` | The recovered fixed short-horizon NASDAQ reversal did not survive its historical cost/OOS checks | Fixed legacy expression; protocol details partly unrecovered | Do not re-run the same idea under a new name solely because tooling improved |
| B2 sector XRev | `NEGATIVE_REPLICATION_CONFIRMED`, 36 existing expressions | Sector cross-sectional relative-value/reversal family as expressed failed cost, subperiod and multiplicity gates | The 36 existing expressions on the spent dataset | Renaming thresholds/lookbacks does not reset the validation window or trial budget |
| Edge Lab sector shock reversal | `KILL_EXPRESSION` | Conditioning sector reversal on the frozen shock rule did not rescue economics | Exact shock-conditioned expression | Do not upgrade expression failure to `KILL_MECHANISM` |
| B4 macro TSMOM | `FAMILY_REJECTED`, 40 dataset-level trials | Selected variant had positive net return but failed t-stat, half-sample stability and annual-concentration criteria | Three-ETF B4 family on its spent data | Positive point estimate is not sufficient when breadth/stability/multiplicity fail; do not rescue post hoc |
| Broad futures trend+carry | Positive retrospective, later cost-optimism warning | Historical strength does not equal clean deployable alpha; recent carry weakened and universe/cost assumptions matter | Does not negate the historical result | Preserve the result but require execution/prospective evidence rather than repeating discovery |
| Generic prediction FLB | Sign unstable across samples | Favorite/longshot direction changed with sample and execution surface | Generic taker rules tested | Market microstructure/executable prices matter; do not treat a published behavioral bias as invariant |
| F2 Kalshi FLB | `BLOCKED_DATA_PERMISSION` | Public endpoint availability does not establish research rights | No empirical falsification | Rights/access is a separate evidence dimension; do not bypass ToS to “complete” a test |
| Prediction-market negRisk/combinatorial | Rejected after fees; cross-venue identical-rule matches absent in screened set | Easy public arbitrage was largely consumed by fees or replaced by settlement-basis risk | Tested historical implementations | Apparent price inconsistency is not arbitrage until settlement clauses, fees and fillability align |
| BTC/prediction-market latency | Positive only around 1s; gone by 3s/5s | Any edge was infrastructure-speed dependent and inaccessible to slower execution | Slow implementation, not all low-latency systems | A statistically visible lead can be economically unusable once latency is modeled |
| Generic SPY overnight | Net evidence weak | Broad overnight premium was not strong enough after simple costs in the recovered sample | Generic overnight expression | Event conditioning must not be claimed as independent from prior calendar exploration |
| Turn-of-month | Not better than unconditional beta in recovered comparison | Calendar window alone did not isolate a compelling effect | Recovered TOM expression | Compare against unconditional exposure; calendar labels can repackage beta |
| Leveraged-ETF flow proxies | Negative continuation variants | Simple daily-bar proxies did not support the anticipated flow continuation | Tested daily proxy expressions | A plausible flow mechanism can fail when the observable proxy/timing is wrong |
| Crypto liquidation rebound | Negative/unstable, particularly 2025+ | Simple hourly cascade-rebound rules did not generalize; some long-horizon apparent positives reversed in later slices | Simple hourly forced-liquidation rebound | Do not rediscover “buy after liquidation cascade” without a materially different microstructure signal |
| Crypto carry | Historical BTC carry decayed toward/below cash hurdle; altcoin cross-sectional carry weak after costs | Structural funding premium can be real yet cease to be economically attractive as arbitrage capital enters | Recovered historical expressions/regime | Always compare financing premia to cost of capital/cash hurdle; structural does not mean permanent magnitude |
| CFE VIX v0/v1 | `PARK_DATA` | Source coverage/format failure prevented a clean economic result | No mechanism falsification | Data completeness is not a nuisance to patch after seeing outcomes; preserve failed acquisition state |
| CFE VIX reader repair | `PROMOTE_EXPRESSION`, not edge validation | Technical repair can make an expression runnable without adding independent economic evidence | No new falsification | Parser/reader repairs must share the parent's trial/evidence lineage |
| Treasury 5Y / ZF | `PARK_DATA`; outcome exposure partly consumed | Population/source inadequacy can contaminate pristine status without yielding an admissible economic verdict | No economic rejection | Record outcome exposure even when the final result is quarantined; do not claim a fresh holdout later |
| France OAT/Bund | `PARK_DATA` across routes | Public daily-route work did not establish a canonical economic result | No family rejection | A new data vendor/route is an implementation change, not a new hypothesis |
| CFTC ES leveraged extremes | `PARK_DATA`, economics not opened | The lane failed before an admissible economic test | No mechanism rejection | Do not treat data-gated work as negative alpha evidence |
| Later formal month-end pension lane | `PARK_DATA`, economics not opened | Formalization did not independently confirm or reject the earlier retrospective screen | No new economic scope | Preserve earlier result and later data failure separately |
| Binance extreme-funding reversal | `PARK_DATA`, HTTP 451, economics false | Official frozen source could not be acquired in the one-shot run | No mechanism rejection | Do not substitute sources/thresholds after failure and then call it the same pristine experiment |
| Crypto book-pressure prospective | `CAPTURE_INVALID`, zero valid trades | 21 responses were not valid order-book observations; recorder stop behavior was defective | Failed implementation/capture only | Prospective timing alone does not make evidence valid; schema/data integrity precedes P&L |
| Russell deletion basket | No outcome access; predeclared/not armed | One event cluster with dependent names would have limited inferential scope even if run | Exact future eight-name expression only | Event studies need cluster-aware scope; avoid pseudo-independent constituent counts |
| SEC Form 4 census/EOD | Census publication missing durably; EOD `economic_test_count=0` | Code/workflow existence is not evidence that the event dataset exists or that the hypothesis was tested | No economic rejection | Recover the actual durable population artifact before price outcomes; do not rebuild from zero by default |
| Weather V2 | Design blocked by D4 false economic exclusion | A formally rigorous-looking upper-bound design could falsely exclude true economic value | V2 inference design, not Weather economics | Audit the semantics of terminal claims, not just nominal error rates |
| Weather V3 | `V3_NOT_JUSTIFIED` | Better scientific hygiene did not create a freezeable/economically closer candidate | V3 program direction | Research-process sophistication is not evidence of an edge |
| Weather V4 | Phase gate not granted | Hypothesis archaeology and structural readiness are not execution or evidence | No economic result | Keep `PASS_FOR_OWNER_PHASE_GATE_CONSIDERATION` distinct from authorization and validation |
| Sports sharp-price/CLV lab | Mixed; hindsight close lines can look strong | Close-price/CLV diagnostics are not causal executable signals; many transformations create multiplicity | Tested transformations | Keep causal open/open evidence separate from hindsight benchmark diagnostics |

## Secondary-only negative claims requiring provenance caution

The October research board reports additional historical negatives from unmerged branches, including sharp-vs-venue `0/60` capacity and a Hyperliquid listing-fade result whose top 10% of events accounted for 98% of P&L. Their primary artifacts were not recovered during this mission. They are useful warnings, but remain `SECONDARY_PROVENANCE_ONLY` and must not be promoted to canonical family kills without the underlying artifact.

## Data / access failures that must not be mislabelled as economic negatives

The following are primarily **blockers**, not evidence that the mechanism has no edge:

- CFE source coverage/reader failures;
- Treasury/ZF population/source adequacy;
- France OAT/Bund public route adequacy;
- CFTC ES data gate;
- later month-end pension data gate;
- Binance HTTP 451 source failure;
- SEC Form 4 missing durable census;
- F2 Kalshi permission restriction;
- invalid crypto order-book capture.

Future systems should encode these as `BLOCKED_*` or `PARK_DATA/PERMISSION`, never `NEGATIVE` by default.

## Research that should not be repeated as-is

- B2's existing 36-expression family on the spent dataset.
- B4's 40-trial small-universe macro family on the spent validation window.
- The exact killed sector-shock and stock/bond-stress expressions.
- Generic public negRisk/combinatorial screens with the same fee/settlement assumptions.
- Simple hourly liquidation-cascade rebound screens without a materially different mechanism.
- Generic favorite/longshot taker rules presented as novel without acknowledging sign instability.
- Weather V1-V3 design paths as if prior audit history did not exist.
- A fresh Form-4 census build before exhausting recovery of the prior raw/census work.

This prohibition is scientific memory, not permanent authority over genuinely new generations. A materially new generation still requires its own explicit authorization.

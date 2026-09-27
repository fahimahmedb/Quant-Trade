# H-003 result (Kalshi favourite-longshot: buy NO on cheap YES)

Mechanical verdict: CANDIDATE (all pre-registered gates pass). Integrity flag: NOT credible yet —
validation had zero YES resolutions, so the t-stat measures price dispersion, not tail risk.

- Dataset: 18,591 settled markets / 1,595 events / 22 series (`data/fast_rail/h003/`, 3.0 MB, MANIFEST sha256).
- Split by event close: discovery 877 (2021-07..2025-07), validation 478 (2025-07..2026-04), holdout 240 untouched.
- Trials: 6 (no reruns). required_t(6) = 2.638.

Discovery grid (per-event mean net, t, N events):
| expression | mean net | t | N |
|---|---|---|---|
| yes<=0.05 @T-24h | -0.64% | -1.13 | 345 |
| yes<=0.05 @T-1h | +0.01% | +0.02 | 177 |
| yes<=0.10 @T-24h | -0.96% | -1.33 | 489 |
| yes<=0.10 @T-1h | -1.63% | -1.47 | 236 |
| yes<=0.20 @T-24h | -0.64% | -0.83 | 607 |
| yes<=0.20 @T-1h | -2.68% | -2.02 | 277 |

Best discovery expression: yes<=0.05 @T-1h (t = 0.02, i.e. no discovery edge).

Validation (yes<=0.05 @T-1h):
- N events 34 (48 contracts); mean net +1.09%/event; t = 7.15 >= 2.64
- gross +2.12%, fee drag 1.03% (per-contract fee rounding: 1c on a ~98c NO); fee x2 net +0.08%
- halves +1.14% / +1.04%; max series share 16.5% (KXU3); top-10% events share 27.7%
- capacity $11.5k/month (10% of trailing-24h volume capped by OI, at NO price); median $672/event

Tail diagnostic (`diagnose.py`, no new trial):
- discovery: 248 contracts, 2 YES losses (0.81%) vs break-even loss rate 0.72% -> no edge
- validation: 48 contracts, 0 YES losses; P(<=0 losses | discovery rate) = 0.68
- => validation pass is what a zero-edge strategy produces 68% of the time.

Read: gross favourite-longshot premium ~1-2% exists at T-1h, but per-contract fee rounding eats
~half and one YES loss (-100%) per ~100 contracts removes the rest. At T-24h and wider thresholds
net is negative in discovery. Do not promote without >= 300 forward events (registry requirement).

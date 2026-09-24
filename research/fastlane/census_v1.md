# Fast-lane census v1 — `QUANT_FASTLANE_HPIT_V1`

Outcome-blind: built only from SEC Insider Transactions Data Sets filing fields. No prices, returns, market caps or delisting status were read.

Coverage: 2006-01-03 → 2026-06-30, 393907 original Form 4 P/A accessions. Events input `071d48baed7c1f8c…`.

Entry-event unit: issuer × filing date. Value tiers use the reported transaction value (window sum for the crossing families).

## Entry events per year by split

| Family | Split | Issuer-days/yr | Issuer-days | Unique issuers | ≥$10k/yr | ≥$100k/yr | ≥$1M/yr | Cluster formations | Lag p50/p90 (d) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| ALL_P | discovery | 14922.4 | 193991 | 11101 | 10491.2 | 4268.8 | 1175.7 | 44981 | 2/5 |
| ALL_P | walk_forward | 11556.8 | 28892 | 4381 | 8885.2 | 4224.0 | 1340.4 | 6975 | 2/4 |
| ALL_P | holdout | 10965.6 | 54828 | 5698 | 8421.6 | 4265.2 | 1337.0 | 12475 | 2/5 |
| OD | discovery | 12341.2 | 160435 | 10264 | 8366.8 | 2917.0 | 588.8 | 35217 | 2/5 |
| OD | walk_forward | 9756.8 | 24392 | 4038 | 7320.4 | 3103.2 | 755.6 | 5667 | 2/4 |
| OD | holdout | 8884.8 | 44424 | 5224 | 6656.4 | 2967.6 | 717.8 | 9326 | 2/5 |
| CEO_CFO | discovery | 3749.7 | 48746 | 7021 | 2332.0 | 847.1 | 141.8 | 5518 | 2/5 |
| CEO_CFO | walk_forward | 3346.0 | 8365 | 2190 | 2247.6 | 901.6 | 192.4 | 1019 | 2/4 |
| CEO_CFO | holdout | 3182.2 | 15911 | 3209 | 2135.0 | 939.0 | 205.8 | 1829 | 2/4 |
| OD_CLUSTER_10CD | discovery | 2709.0 | 35217 | 6757 | 2232.0 | 1023.3 | 236.1 | 35217 | 2/6 |
| OD_CLUSTER_10CD | walk_forward | 2266.8 | 5667 | 2251 | 1959.2 | 1154.4 | 337.6 | 5667 | 2/4 |
| OD_CLUSTER_10CD | holdout | 1865.2 | 9326 | 2934 | 1652.0 | 986.0 | 299.0 | 9326 | 2/5 |
| FROZEN_FV_PROXY_10WD | discovery | 2709.4 | 35222 | 6871 | 2249.5 | 1040.4 | 240.4 | 35222 | 2/6 |
| FROZEN_FV_PROXY_10WD | walk_forward | 2236.8 | 5592 | 2297 | 1956.8 | 1160.0 | 337.2 | 5592 | 2/4 |
| FROZEN_FV_PROXY_10WD | holdout | 1871.6 | 9358 | 2988 | 1663.0 | 1003.6 | 302.6 | 9358 | 2/5 |

## Issuer-days per calendar year

| Year | ALL_P | OD | CEO_CFO | OD_CLUSTER_10CD | FROZEN_FV_PROXY_10WD |
|---|---:|---:|---:|---:|---:|
| 2006 | 16387 | 13030 | 3603 | 2765 | 2787 |
| 2007 | 20189 | 16366 | 4524 | 3796 | 3789 |
| 2008 | 26636 | 21402 | 6193 | 4609 | 4577 |
| 2009 | 17349 | 14625 | 4215 | 3053 | 3033 |
| 2010 | 13714 | 11532 | 3312 | 2411 | 2407 |
| 2011 | 15371 | 13117 | 3951 | 2931 | 2935 |
| 2012 | 12972 | 11026 | 3402 | 2397 | 2439 |
| 2013 | 10869 | 9155 | 2739 | 2050 | 2074 |
| 2014 | 11641 | 10025 | 3317 | 2324 | 2321 |
| 2015 | 14326 | 11901 | 3994 | 2667 | 2620 |
| 2016 | 12191 | 9984 | 3184 | 2164 | 2162 |
| 2017 | 10525 | 8611 | 2984 | 1875 | 1895 |
| 2018 | 11821 | 9661 | 3328 | 2175 | 2183 |
| 2019 | 11166 | 9271 | 3265 | 2164 | 2155 |
| 2020 | 13438 | 11490 | 3890 | 2670 | 2601 |
| 2021 | 10336 | 8755 | 3023 | 1988 | 1973 |
| 2022 | 12977 | 10782 | 3891 | 2162 | 2166 |
| 2023 | 11824 | 9586 | 3498 | 2023 | 2009 |
| 2024 | 9530 | 7384 | 2717 | 1542 | 1555 |
| 2025 | 9653 | 7742 | 2754 | 1644 | 1673 |
| 2026 | 4796 | 3806 | 1238 | 800 | 818 |

## Definitions

- `ALL_P`: any original Form 4 non-derivative P/A purchase.
- `OD`: at least one officer/director reporting owner (10%-only/Other-only excluded).
- `CEO_CFO`: at least one owner whose title matches CEO or CFO.
- `OD_CLUSTER_10CD`: crossing <2 -> >=2 distinct O/D owner CIKs over filing dates [d-9,d], re-armed only after the window count falls below 2.
- `FROZEN_FV_PROXY_10WD`: frozen first-vertical signal (D07 2.1-2.2) with regular sessions approximated by weekdays (no holidays); rate estimate only, not the frozen object.

Caveats: tickers are as filed, not a point-in-time security mapping; the `FROZEN_FV_PROXY_10WD` family approximates regular sessions by weekdays; the data sets are SEC-published extracts (fingerprinted in `sec_insider_manifest_v1.json`), not the raw XML.

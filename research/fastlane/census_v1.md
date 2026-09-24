# Fast-lane census v1 — `QUANT_FASTLANE_HPIT_V1`

Outcome-blind: built only from SEC Insider Transactions Data Sets filing fields. No prices, returns, market caps or delisting status were read.

Coverage: 2006-01-03 → 2026-06-30, 341213 primary accessions (`research/fastlane/data/events_primary_v1.jsonl.gz`, sha256 `1113a2058e854e16…`).

Primary population: original Form 4 P/A, common-equity titles, frozen footnote/remarks exclusions, exact duplicates removed, backdated accessions excluded. Entry-event unit: issuer × filing date.

Row exclusions (base): P_acquired_disposed_not_A 3997, accession_year_after_filing_year 4, document_type_not_original_form4 280528, shares_missing_nonpositive_or_unparseable 3763, trans_code_not_P 6195978.

Row exclusions (primary): exact_duplicate_of_earlier_accession 3247, footnote_exclusion 36012, remarks_exclusion 1550, security_title_not_common_equity 47195; footnote categories: conversion 683, ipo_underwritten 4733, plan_drip_fees 28368, private_placement 2228, remarks:conversion 11, remarks:ipo_underwritten 124, remarks:plan_drip_fees 1353, remarks:private_placement 62.

## Primary entry events per year by split

| Family | Split | Issuer-days/yr | Issuer-days | Unique issuers | ≥$10k/yr | ≥$100k/yr | ≥$1M/yr | Cluster formations | Lag p50/p90 (d) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| ALL_P | discovery | 13412.5 | 174362 | 10392 | 9441.5 | 3797.2 | 1031.3 | 28894 | 2/5 |
| ALL_P | walk_forward | 10360.0 | 25900 | 3983 | 8025.2 | 3772.8 | 1146.8 | 4535 | 2/4 |
| ALL_P | holdout | 9783.4 | 48917 | 5182 | 7564.6 | 3774.6 | 1139.0 | 7548 | 2/4 |
| OD | discovery | 11118.1 | 144535 | 9673 | 7538.5 | 2580.3 | 500.2 | 26873 | 2/5 |
| OD | walk_forward | 8737.6 | 21844 | 3682 | 6608.4 | 2762.4 | 626.0 | 4211 | 2/4 |
| OD | holdout | 7912.2 | 39561 | 4793 | 5981.8 | 2618.6 | 601.2 | 6881 | 2/4 |
| CEO_CFO | discovery | 3349.9 | 43549 | 6557 | 2090.2 | 744.4 | 123.7 | 3942 | 1/5 |
| CEO_CFO | walk_forward | 2993.6 | 7484 | 1967 | 2035.2 | 786.8 | 153.6 | 754 | 2/4 |
| CEO_CFO | holdout | 2807.8 | 14039 | 2906 | 1912.8 | 823.6 | 172.2 | 1276 | 2/4 |
| OD_CLUSTER_10CD | discovery | 2067.2 | 26873 | 5941 | 1773.2 | 810.1 | 161.5 | 26873 | 2/5 |
| OD_CLUSTER_10CD | walk_forward | 1684.4 | 4211 | 1872 | 1520.4 | 897.6 | 201.2 | 4211 | 2/4 |
| OD_CLUSTER_10CD | holdout | 1376.2 | 6881 | 2496 | 1270.6 | 741.2 | 171.4 | 6881 | 2/4 |
| FROZEN_FV_PROXY_10WD | discovery | 2306.4 | 29983 | 6324 | 1959.0 | 899.0 | 198.6 | 29983 | 2/5 |
| FROZEN_FV_PROXY_10WD | walk_forward | 1849.2 | 4623 | 2037 | 1676.0 | 1001.2 | 264.4 | 4623 | 2/4 |
| FROZEN_FV_PROXY_10WD | holdout | 1552.6 | 7763 | 2682 | 1425.8 | 861.0 | 246.2 | 7763 | 2/4 |
| FROZEN_FV_PROXY_10WD_MERGED | discovery | 2095.5 | 27241 | 6055 | 1805.7 | 831.8 | 167.2 | 27241 | 2/5 |
| FROZEN_FV_PROXY_10WD_MERGED | walk_forward | 1685.2 | 4213 | 1924 | 1531.6 | 908.8 | 202.0 | 4213 | 2/4 |
| FROZEN_FV_PROXY_10WD_MERGED | holdout | 1397.4 | 6987 | 2547 | 1289.2 | 761.2 | 177.2 | 6987 | 2/4 |

## Sensitivity: unfiltered population (issuer-days/yr)

| Family | discovery | walk_forward | holdout |
|---|---:|---:|---:|
| ALL_P | 14922.4 | 11556.8 | 10965.6 |
| OD | 12341.2 | 9756.8 | 8884.6 |
| CEO_CFO | 3741.1 | 3340.0 | 3179.0 |
| OD_CLUSTER_10CD | 2419.0 | 2028.4 | 1643.2 |
| FROZEN_FV_PROXY_10WD | 2708.3 | 2234.0 | 1869.6 |
| FROZEN_FV_PROXY_10WD_MERGED | 2443.0 | 2013.2 | 1657.8 |

## Primary issuer-days per calendar year

| Year | ALL_P | OD | CEO_CFO | OD_CLUSTER_10CD | FROZEN_FV_PROXY_10WD | FROZEN_FV_PROXY_10WD_MERGED |
|---|---:|---:|---:|---:|---:|---:|
| 2006 | 14792 | 11823 | 3238 | 2157 | 2400 | 2205 |
| 2007 | 18351 | 15025 | 4149 | 3087 | 3385 | 3121 |
| 2008 | 24070 | 19359 | 5523 | 3796 | 4069 | 3798 |
| 2009 | 15654 | 13216 | 3833 | 2375 | 2627 | 2376 |
| 2010 | 12333 | 10376 | 2954 | 1774 | 2016 | 1814 |
| 2011 | 13950 | 11890 | 3552 | 2267 | 2522 | 2299 |
| 2012 | 11614 | 9903 | 3045 | 1762 | 2029 | 1816 |
| 2013 | 9606 | 8101 | 2348 | 1417 | 1635 | 1448 |
| 2014 | 10436 | 8981 | 2917 | 1713 | 1918 | 1737 |
| 2015 | 12824 | 10660 | 3578 | 1997 | 2219 | 2009 |
| 2016 | 10865 | 8863 | 2817 | 1546 | 1776 | 1574 |
| 2017 | 9283 | 7672 | 2630 | 1356 | 1554 | 1387 |
| 2018 | 10584 | 8666 | 2965 | 1626 | 1833 | 1657 |
| 2019 | 10145 | 8402 | 2974 | 1603 | 1808 | 1635 |
| 2020 | 12049 | 10276 | 3468 | 2059 | 2166 | 2010 |
| 2021 | 9176 | 7817 | 2667 | 1412 | 1593 | 1420 |
| 2022 | 11781 | 9796 | 3518 | 1613 | 1817 | 1637 |
| 2023 | 10619 | 8527 | 3061 | 1527 | 1695 | 1528 |
| 2024 | 8442 | 6510 | 2374 | 1095 | 1257 | 1116 |
| 2025 | 8484 | 6824 | 2423 | 1198 | 1384 | 1244 |
| 2026 | 4121 | 3253 | 1038 | 585 | 666 | 610 |

## Definitions

- `ALL_P`: any primary purchase.
- `OD`: at least one officer/director owner by relationship flag (10%-only and Other-only excluded; titles never promote).
- `CEO_CFO`: at least one owner with the Officer relationship flag and a CEO/CFO title.
- `OD_CLUSTER_10CD`: crossing <2 -> >=2 distinct O/D decision units over filing dates [d-9,d], re-armed below 2; owners on one accession or with an identical (date, shares, per-share) row are one unit (PIT merge).
- `FROZEN_FV_PROXY_10WD`: frozen first-vertical signal taken literally (distinct O/D CIKs, D07 2.1-2.2) with regular sessions approximated by weekdays; rate estimate only, not the frozen object.
- `FROZEN_FV_PROXY_10WD_MERGED`: SENSITIVITY: the frozen proxy with decision-unit merging; not a grid family.

Caveats: tickers are as filed, not a point-in-time security mapping; the frozen proxies approximate regular sessions by weekdays; counts precede PIT security mapping and liquidity eligibility; the data sets are SEC-published extracts (fingerprinted in `sec_insider_manifest_v1.json`), not the raw XML; same-year backdating cannot be detected from the data sets.

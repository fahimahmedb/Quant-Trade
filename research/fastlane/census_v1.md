# Fast-lane census v1 — `QUANT_FASTLANE_HPIT_V1`

Outcome-blind: built only from SEC Insider Transactions Data Sets filing fields. No prices, returns, market caps or delisting status were read.

Coverage: 2006-01-03 → 2026-06-30, 360115 primary accessions (`research/fastlane/data/events_primary_v1.jsonl.gz`, sha256 `dc72010fefc2709b…`).

Primary population: original Form 4 P/A, common-equity titles, frozen footnote/remarks exclusions, exact duplicates removed, backdated accessions excluded. Entry-event unit: issuer × filing date.

Row exclusions (base): P_acquired_disposed_not_A 3997, accession_year_after_filing_year 4, document_type_not_original_form4 280528, shares_missing_nonpositive_or_unparseable 3763, trans_code_not_P 6195978.

Row exclusions (primary): exact_duplicate_of_earlier_accession 3312, footnote_exclusion 20680, remarks_exclusion 1598, security_title_not_common_equity 28356; footnote categories: conversion 328, ipo_underwritten 4406, plan_drip_fees 13839, private_placement 2107, remarks:conversion 52, remarks:ipo_underwritten 129, remarks:plan_drip_fees 1355, remarks:private_placement 62.

## Primary entry events per year by split

| Family | Split | Issuer-days/yr | Issuer-days | Unique issuers | ≥$10k/yr | ≥$100k/yr | ≥$1M/yr | Cluster formations | Lag p50/p90 (d) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| ALL_P | discovery | 14005.5 | 182071 | 10645 | 9914.2 | 4020.8 | 1087.9 | 30694 | 2/5 |
| ALL_P | walk_forward | 10869.2 | 27173 | 4117 | 8426.4 | 3970.8 | 1210.8 | 4866 | 2/4 |
| ALL_P | holdout | 10254.8 | 51274 | 5340 | 7940.6 | 3991.4 | 1200.4 | 8082 | 2/4 |
| OD | discovery | 11632.8 | 151226 | 9914 | 7945.8 | 2759.4 | 540.5 | 28591 | 2/5 |
| OD | walk_forward | 9176.8 | 22942 | 3801 | 6950.0 | 2916.0 | 667.6 | 4528 | 2/4 |
| OD | holdout | 8294.6 | 41473 | 4917 | 6277.0 | 2771.6 | 637.2 | 7397 | 2/4 |
| CEO_CFO | discovery | 3506.5 | 45584 | 6750 | 2212.2 | 799.0 | 130.5 | 4334 | 2/5 |
| CEO_CFO | walk_forward | 3122.8 | 7807 | 2032 | 2125.2 | 831.2 | 162.0 | 823 | 2/4 |
| CEO_CFO | holdout | 2941.8 | 14709 | 2988 | 2003.8 | 873.6 | 178.8 | 1438 | 2/4 |
| OD_CLUSTER_10CD | discovery | 2199.3 | 28591 | 6142 | 1888.7 | 868.8 | 174.2 | 28591 | 2/5 |
| OD_CLUSTER_10CD | walk_forward | 1811.2 | 4528 | 1943 | 1619.6 | 950.4 | 216.0 | 4528 | 2/4 |
| OD_CLUSTER_10CD | holdout | 1479.4 | 7397 | 2588 | 1355.8 | 789.8 | 186.2 | 7397 | 2/4 |
| FROZEN_FV_PROXY_10WD | discovery | 2453.4 | 31894 | 6537 | 2086.7 | 962.3 | 214.0 | 31894 | 2/5 |
| FROZEN_FV_PROXY_10WD | walk_forward | 1991.2 | 4978 | 2114 | 1791.6 | 1062.0 | 283.6 | 4978 | 2/4 |
| FROZEN_FV_PROXY_10WD | holdout | 1671.4 | 8357 | 2782 | 1524.4 | 915.4 | 261.4 | 8357 | 2/4 |
| FROZEN_FV_PROXY_10WD_MERGED | discovery | 2225.4 | 28930 | 6257 | 1919.5 | 890.7 | 180.0 | 28930 | 2/5 |
| FROZEN_FV_PROXY_10WD_MERGED | walk_forward | 1809.2 | 4523 | 1996 | 1632.0 | 962.8 | 217.6 | 4523 | 2/4 |
| FROZEN_FV_PROXY_10WD_MERGED | holdout | 1499.0 | 7495 | 2643 | 1375.2 | 811.8 | 192.4 | 7495 | 2/4 |

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
| 2006 | 15186 | 12176 | 3355 | 2251 | 2512 | 2301 |
| 2007 | 18917 | 15524 | 4287 | 3215 | 3513 | 3237 |
| 2008 | 25112 | 20271 | 5796 | 3997 | 4278 | 3990 |
| 2009 | 16204 | 13703 | 3956 | 2481 | 2765 | 2487 |
| 2010 | 12793 | 10786 | 3080 | 1883 | 2136 | 1919 |
| 2011 | 14495 | 12385 | 3718 | 2414 | 2668 | 2436 |
| 2012 | 12145 | 10375 | 3184 | 1894 | 2175 | 1948 |
| 2013 | 10061 | 8520 | 2483 | 1539 | 1785 | 1575 |
| 2014 | 11026 | 9527 | 3108 | 1865 | 2087 | 1888 |
| 2015 | 13657 | 11359 | 3779 | 2170 | 2396 | 2171 |
| 2016 | 11483 | 9390 | 2949 | 1667 | 1925 | 1698 |
| 2017 | 9835 | 8084 | 2781 | 1473 | 1693 | 1507 |
| 2018 | 11157 | 9126 | 3108 | 1742 | 1961 | 1773 |
| 2019 | 10602 | 8790 | 3087 | 1720 | 1937 | 1748 |
| 2020 | 12691 | 10843 | 3639 | 2206 | 2341 | 2159 |
| 2021 | 9589 | 8170 | 2776 | 1529 | 1716 | 1528 |
| 2022 | 12267 | 10195 | 3675 | 1727 | 1956 | 1750 |
| 2023 | 11067 | 8930 | 3195 | 1637 | 1826 | 1637 |
| 2024 | 8888 | 6850 | 2495 | 1186 | 1369 | 1210 |
| 2025 | 8969 | 7188 | 2556 | 1295 | 1483 | 1335 |
| 2026 | 4374 | 3449 | 1093 | 625 | 707 | 651 |

## Definitions

- `ALL_P`: any primary purchase.
- `OD`: at least one officer/director owner by relationship flag (10%-only and Other-only excluded; titles never promote).
- `CEO_CFO`: at least one owner with the Officer relationship flag and a CEO/CFO title.
- `OD_CLUSTER_10CD`: crossing <2 -> >=2 distinct O/D decision units over filing dates [d-9,d], re-armed below 2; owners on one accession or with an identical (date, shares, per-share) row are one unit (PIT merge).
- `FROZEN_FV_PROXY_10WD`: frozen first-vertical signal taken literally (distinct O/D CIKs, D07 2.1-2.2) with regular sessions approximated by weekdays; rate estimate only, not the frozen object.
- `FROZEN_FV_PROXY_10WD_MERGED`: SENSITIVITY: the frozen proxy with decision-unit merging; not a grid family.

Caveats: tickers are as filed, not a point-in-time security mapping; the frozen proxies approximate regular sessions by weekdays; counts precede PIT security mapping and liquidity eligibility; the data sets are SEC-published extracts (fingerprinted in `sec_insider_manifest_v1.json`), not the raw XML; same-year backdating cannot be detected from the data sets.

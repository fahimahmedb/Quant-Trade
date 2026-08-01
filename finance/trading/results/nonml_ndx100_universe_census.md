# Recensement de l'univers NDX-100 et mesure du biais du survivant (cycle #163)

**Aucune performance de stratégie n'est calculée dans ce document** — uniquement la composition de l'indice et la disponibilité des prix. Produit par `scripts/nonml_ndx100_universe_census.py`, committé AVANT `PREREG_leaders_index52w_high_overlay_pit_universe.md` (Règle 1 : le pré-enregistrement doit fixer un périmètre justifié, pas deviné ; Règle 6 : traçabilité).

Source de composition point-in-time : `nasdaq-100-ticker-history` v2026.7.0 (https://github.com/jmccarrell/n100tickers, licence MIT), données YAML vendorées verbatim dans `data/ndx100_history/` et rechargées par `scripts/ndx100_membership.py` (portage minimal vérifié contre les doctests amont). Couverture amont : 2015-01-01 → au moins 2026-06-22.

**214 tickers différents** ont appartenu au NDX-100 entre 2015 et 2026, contre **103** dans la liste figée de 2026 utilisée par les cycles #161 et #162.

## 1. Biais du survivant des cycles #161/#162, mesuré année par année

Les cycles #161 (fenêtre 2022-2026) et #162 (fenêtre 1970-2026) ont utilisé la liste des membres de 2026 appliquée rétroactivement. Le tableau donne, à chaque 1er janvier, le nombre de VRAIS membres de l'indice, combien d'entre eux figurent dans cette liste de 2026, et la fraction manquante — composée exclusivement de titres sortis de l'indice depuis, donc en moyenne des sous-performants (biais orienté à la HAUSSE des rendements).

| Date | Vrais membres | Présents dans la liste 2026 | Couverture | Manquants (sortis depuis) |
|---|---|---|---|---|
| 2015-01-01 | 105 | 44 | 42% | 61 |
| 2016-01-01 | 105 | 47 | 45% | 58 |
| 2017-01-01 | 104 | 49 | 47% | 55 |
| 2018-01-01 | 103 | 55 | 53% | 48 |
| 2019-01-01 | 103 | 58 | 56% | 45 |
| 2020-01-01 | 103 | 60 | 58% | 43 |
| 2021-01-01 | 102 | 63 | 62% | 39 |
| 2022-01-01 | 101 | 69 | 68% | 32 |
| 2023-01-01 | 101 | 75 | 74% | 26 |
| 2024-01-01 | 101 | 80 | 79% | 21 |
| 2025-01-01 | 101 | 86 | 85% | 15 |
| 2026-01-01 | 101 | 93 | 92% | 8 |

Exemples de membres réels absents de la liste 2026 (donc jamais investissables dans les cycles #161/#162) :

- **2015** (61 manquants) : AAL, AKAM, ALTR, ALXN, ATVI, BBBY, BIDU, BIIB, BRCM, CA, CELG, CERN, CHKP, CHRW, CHTR, CTRX, CTSH, CTXS, DISCA, DISCK, DISH, DLTR, DTV, EBAY, EQIX, ESRX, EXPD, FB, FISV, FOX, FOXA, GMCR, GRMN, HSIC, ILMN, KRFT, LBTYA, LBTYK, LLTC, LMCA, LMCK, MAT, MYL, NLOK, NTAP, QRTEA, SBAC, SIAL, SIRI, SPLS, SRCL, TRIP, TSCO, VIAB, VIP, VOD, VRSK, WFM, WYNN, XLNX, YHOO
- **2020** (43 manquants) : AAL, ALGN, ALXN, ANSS, ATVI, BIDU, BIIB, BMRN, CDW, CERN, CHKP, CHTR, CSGP, CTSH, CTXS, DLTR, EBAY, EXPE, FB, FISV, FOX, FOXA, ILMN, INCY, JD, LBTYA, LBTYK, LULU, MXIM, NTAP, NTES, SGEN, SIRI, SPLK, SWKS, TCOM, UAL, ULTA, VRSK, VRSN, WBA, WLTW, XLNX
- **2023** (26 manquants) : ALGN, ANSS, ATVI, AZN, BIIB, CHTR, CSGP, CTSH, DLTR, EBAY, ENPH, FISV, GFS, ILMN, JD, LCID, LULU, MRNA, RIVN, SGEN, SIRI, TEAM, VRSK, WBA, ZM, ZS

## 2. Disponibilité des prix déjà committés

Éligible à la date D = 252 séances de prix disponibles se terminant à D (critère identique à `has_full` dans `build_weights()`, aucun changement de logique).

| Date | `prices_extended/` (103 titres, liste 2026) | `prices/` (99 titres, borne PEAD 2021) |
|---|---|---|
| 1990-01-01 | 34 | 0 |
| 1995-01-01 | 49 | 0 |
| 2000-01-01 | 55 | 0 |
| 2005-01-01 | 64 | 0 |
| 2008-01-01 | 70 | 0 |
| 2010-01-01 | 73 | 0 |
| 2013-01-01 | 77 | 0 |
| 2015-01-01 | 82 | 0 |
| 2016-01-01 | 82 | 0 |
| 2018-01-01 | 86 | 0 |
| 2020-01-01 | 87 | 0 |
| 2022-01-03 | 93 | 91 |
| 2026-01-01 | 99 | 97 |

## 3. Prix manquants pour une reconstruction point-in-time

Une reconstruction sans biais du survivant sur 2015-2026 exige les prix des 214 tickers ayant appartenu à l'indice, pas seulement des 103 membres actuels.

Tickers sans prix dans `data/pead/prices_extended/` : **113** sur 214.

AAL, AKAM, ALGN, ALTR, ALXN, ANSS, ATVI, AZN, BATRA, BATRK, BBBY, BIDU, BIIB, BMRN, BRCM, CA, CDW, CELG, CERN, CHKP, CHRW, CHTR, CSGP, CTRP, CTRX, CTSH, CTXS, DISCA, DISCK, DISH, DLTR, DOCU, DTV, EBAY, ENDP, ENPH, EQIX, ESRX, EXPD, EXPE, FB, FISV, FOX, FOXA, GFS, GMCR, GRMN, HAS, HOLX, HSIC, ILMN, INCY, INSM, JBHT, JD, KRFT, LBTYA, LBTYK, LCID, LILA, LILAK, LLTC, LMCA, LMCK, LULU, MAT, MDB, MRNA, MTCH, MXIM, MYL, NCLH, NLOK, NTAP, NTES, OKTA, ON, PTON, QRTEA, RIVN, SBAC, SGEN, SHPG, SIAL, SIRI, SMCI, SOLS, SPLK, SPLS, SRCL, SWKS, TCOM, TEAM, TRIP, TSCO, TTD, UAL, ULTA, VIAB, VIP, VOD, VRSK, VRSN, VSNT, WBA, WFM, WLTW, WYNN, XLNX, XRAY, YHOO, ZM, ZS


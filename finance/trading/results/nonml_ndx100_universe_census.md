# Recensement de l'univers NDX-100 par date (cycle #163, AVANT pré-enregistrement)

**Aucune performance de stratégie n'est calculée dans ce document** — uniquement la disponibilité des prix. Produit par `scripts/nonml_ndx100_universe_census.py`, committé AVANT `PREREG_leaders_index52w_high_overlay_defensible_window.md` pour justifier chiffrément le choix de la borne de début (Règle 1 + Règle 6).

Source : `data/pead/prices_extended/` (103 titres exploitables, liste de constituants NDX-100 **de 2026**). Comparaison : `data/pead/prices/` (99 titres, borne artificielle 2021 du protocole PEAD).

## Titres éligibles par date

Éligible à la date D = dispose de 252 séances de prix se terminant à D (critère identique à `has_full` dans `build_weights()`, aucun changement de logique).

| Date | Titres éligibles | % du plateau (103) | Titres manquants |
|---|---|---|---|
| 1990-01-01 | 34 | 33% | 69 |
| 1995-01-01 | 49 | 48% | 54 |
| 2000-01-01 | 55 | 53% | 48 |
| 2003-01-01 | 61 | 59% | 42 |
| 2005-01-01 | 64 | 62% | 39 |
| 2006-01-01 | 68 | 66% | 35 |
| 2007-01-01 | 70 | 68% | 33 |
| 2008-01-01 | 70 | 68% | 33 |
| 2010-01-01 | 73 | 71% | 30 |
| 2013-01-01 | 77 | 75% | 26 |
| 2015-01-01 | 82 | 80% | 21 |
| 2018-01-01 | 86 | 83% | 17 |
| 2020-01-01 | 87 | 84% | 16 |
| 2022-01-03 | 93 | 90% | 10 |
| 2026-01-01 | 99 | 96% | 4 |

## Titres absents (pas encore 252 séances) aux bornes candidates

**2000-01-01** — 48 manquants : ABNB, ALAB, ALNY, APP, ARM, AVGO, AXON, BKNG, CEG, CRWD, CRWV, DASH, DDOG, DXCM, FANG, FER, FTNT, GEHC, GOOG, GOOGL, HONA, ISRG, KDP, KHC, LITE, MDLZ, MELI, META, MPWR, MRVL, NBIS, NFLX, NVDA, NXPI, PANW, PDD, PLTR, PYPL, RKLB, SHOP, SNDK, SPCX, STX, TMUS, TRI, TSLA, WBD, WDAY

**2005-01-01** — 39 manquants : ABNB, ALAB, ALNY, APP, ARM, AVGO, CEG, CRWD, CRWV, DASH, DDOG, DXCM, FANG, FER, FTNT, GEHC, GOOG, GOOGL, HONA, KDP, KHC, LITE, MELI, META, MPWR, NBIS, NXPI, PANW, PDD, PLTR, PYPL, RKLB, SHOP, SNDK, SPCX, TMUS, TSLA, WBD, WDAY

**2008-01-01** — 33 manquants : ABNB, ALAB, APP, ARM, AVGO, CEG, CRWD, CRWV, DASH, DDOG, FANG, FER, FTNT, GEHC, HONA, KDP, KHC, LITE, MELI, META, NBIS, NXPI, PANW, PDD, PLTR, PYPL, RKLB, SHOP, SNDK, SPCX, TMUS, TSLA, WDAY

**2010-01-01** — 30 manquants : ABNB, ALAB, APP, ARM, AVGO, CEG, CRWD, CRWV, DASH, DDOG, FANG, FER, FTNT, GEHC, HONA, KHC, LITE, META, NBIS, NXPI, PANW, PDD, PLTR, PYPL, RKLB, SHOP, SNDK, SPCX, TSLA, WDAY

## Première date de cotation disponible, par titre

| Ticker | 1re séance (étendu) | 1re séance (`prices/`) |
|---|---|---|
| AAPL | 1980-12-12 | 2021-01-04 |
| ABNB | 2020-12-10 | 2021-01-04 |
| ADBE | 1986-08-13 | 2021-01-04 |
| ADI | 1980-03-17 | 2021-01-04 |
| ADP | 1980-03-17 | 2021-01-04 |
| ADSK | 1985-06-28 | 2021-01-04 |
| AEP | 1970-01-02 | 2021-01-04 |
| ALAB | 2024-03-20 | 2024-03-20 |
| ALNY | 2004-06-01 | 2021-01-04 |
| AMAT | 1980-03-17 | 2021-01-04 |
| AMD | 1980-03-17 | 2021-01-04 |
| AMGN | 1983-06-17 | 2021-01-04 |
| AMZN | 1997-05-15 | 2021-01-04 |
| APP | 2021-04-15 | 2021-04-15 |
| ARM | 2023-09-14 | 2023-09-14 |
| ASML | 1995-03-15 | 2021-01-04 |
| AVGO | 2009-08-06 | 2021-01-04 |
| AXON | 2001-06-19 | 2021-01-04 |
| BKNG | 1999-03-31 | 2021-01-04 |
| BKR | 1987-04-06 | 2021-01-04 |
| CCEP | 1986-11-24 | -- |
| CDNS | 1987-06-10 | 2021-01-04 |
| CEG | 2022-01-19 | 2022-01-19 |
| CMCSA | 1980-03-17 | 2021-01-04 |
| COST | 1986-07-09 | 2021-01-04 |
| CPRT | 1994-03-17 | 2021-01-04 |
| CRWD | 2019-06-12 | 2021-01-04 |
| CRWV | 2025-03-28 | 2025-03-28 |
| CSCO | 1990-02-16 | 2021-01-04 |
| CSX | 1980-11-03 | 2021-01-04 |
| CTAS | 1983-08-19 | 2021-01-04 |
| DASH | 2020-12-09 | 2021-01-04 |
| DDOG | 2019-09-19 | 2021-01-04 |
| DXCM | 2005-04-14 | 2021-01-04 |
| EA | 1989-09-20 | 2021-01-04 |
| EXC | 1973-05-02 | 2021-01-04 |
| FANG | 2012-10-12 | 2021-01-04 |
| FAST | 1987-08-20 | 2021-01-04 |
| FER | 2012-08-13 | -- |
| FTNT | 2009-11-18 | 2021-01-04 |
| GEHC | 2022-12-15 | 2022-12-15 |
| GILD | 1992-01-22 | 2021-01-04 |
| GOOG | 2004-08-19 | 2021-01-04 |
| GOOGL | 2004-08-19 | 2021-01-04 |
| HON | 1970-01-02 | 2021-01-04 |
| HONA | 2026-06-15 | -- |
| IDXX | 1991-06-21 | 2021-01-04 |
| INTC | 1980-03-17 | 2021-01-04 |
| INTU | 1993-03-12 | 2021-01-04 |
| ISRG | 2000-06-16 | 2021-01-04 |
| KDP | 2008-05-07 | 2021-01-04 |
| KHC | 2015-07-06 | 2021-01-04 |
| KLAC | 1980-10-08 | 2021-01-04 |
| LIN | 1992-06-17 | 2021-01-04 |
| LITE | 2015-07-23 | 2021-01-04 |
| LRCX | 1984-05-04 | 2021-01-04 |
| MAR | 1998-03-23 | 2021-01-04 |
| MCHP | 1993-03-19 | 2021-01-04 |
| MDLZ | 2001-06-13 | 2021-01-04 |
| MELI | 2007-08-10 | 2021-01-04 |
| META | 2012-05-18 | 2021-01-04 |
| MNST | 1985-12-09 | 2021-01-04 |
| MPWR | 2004-11-19 | 2021-01-04 |
| MRVL | 2000-06-30 | 2021-01-04 |
| MSFT | 1986-03-13 | 2021-01-04 |
| MSTR | 1998-06-11 | 2021-01-04 |
| MU | 1984-06-01 | 2021-01-04 |
| NBIS | 2024-10-21 | 2024-10-21 |
| NFLX | 2002-05-23 | 2021-01-04 |
| NVDA | 1999-01-22 | 2021-01-04 |
| NXPI | 2010-08-06 | 2021-01-04 |
| ODFL | 1991-10-24 | 2021-01-04 |
| ORLY | 1993-04-23 | 2021-01-04 |
| PANW | 2012-07-20 | 2021-01-04 |
| PAYX | 1983-08-26 | 2021-01-04 |
| PCAR | 1980-03-17 | 2021-01-04 |
| PDD | 2018-07-26 | 2021-01-04 |
| PEP | 1972-06-01 | 2021-01-04 |
| PLTR | 2020-09-30 | 2021-01-04 |
| PYPL | 2015-07-06 | 2021-01-04 |
| QCOM | 1991-12-13 | 2021-01-04 |
| REGN | 1991-04-02 | 2021-01-04 |
| RKLB | 2020-11-24 | 2021-01-04 |
| ROP | 1992-02-13 | 2021-01-04 |
| ROST | 1985-08-08 | 2021-01-04 |
| SBUX | 1992-06-26 | 2021-01-04 |
| SHOP | 2015-05-20 | 2021-01-04 |
| SNDK | 2025-02-13 | 2025-02-13 |
| SNPS | 1992-02-26 | 2021-01-04 |
| SPCX | 2026-06-12 | -- |
| STX | 2002-12-11 | 2021-01-04 |
| TER | 1973-02-21 | 2021-01-04 |
| TMUS | 2007-04-19 | 2021-01-04 |
| TRI | 2002-06-12 | 2021-01-04 |
| TSLA | 2010-06-29 | 2021-01-04 |
| TTWO | 1997-04-15 | 2021-01-04 |
| TXN | 1972-06-01 | 2021-01-04 |
| VRTX | 1991-07-24 | 2021-01-04 |
| WBD | 2005-07-08 | 2021-01-04 |
| WDAY | 2012-10-12 | 2021-01-04 |
| WDC | 1978-10-31 | 2021-01-04 |
| WMT | 1972-08-25 | 2021-01-04 |
| XEL | 1973-02-21 | 2021-01-04 |

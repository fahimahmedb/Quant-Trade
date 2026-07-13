"""QC croisé des sources de données et assemblage du dataset maître.

Sources:
- ndx_yahoo.csv   : ^NDX OHLC quotidien (Yahoo, 1989-)
- qqq_yahoo.csv   : QQQ OHLC + AdjClose (Yahoo, 1999-)  -> instrument tradeable
- nasdaq100_fred.csv : NDX close (FRED, 1986-)          -> source indépendante pour QC
- vxn_yahoo.csv   : ^VXN close (Yahoo, 2001-)
- VXN_History.csv : VXN close (CBOE, 2009-)             -> source indépendante pour QC
- VIX_History.csv : VIX close (CBOE, 1990-)             -> covariable

Sortie: data/master.parquet (Date-indexé, NDX OHLC, QQQ, VXN, VIX)
"""
import pandas as pd
import numpy as np

DATA = "/home/user/Quant-Trade/data"

ndx = pd.read_csv(f"{DATA}/ndx_yahoo.csv", parse_dates=["Date"], index_col="Date")
qqq = pd.read_csv(f"{DATA}/qqq_yahoo.csv", parse_dates=["Date"], index_col="Date")
fred = pd.read_csv(f"{DATA}/nasdaq100_fred.csv", parse_dates=["observation_date"],
                   index_col="observation_date").rename(columns={"NASDAQ100": "ndx_fred"})
fred["ndx_fred"] = pd.to_numeric(fred["ndx_fred"], errors="coerce")
vxn_y = pd.read_csv(f"{DATA}/vxn_yahoo.csv", parse_dates=["Date"], index_col="Date")
vxn_c = pd.read_csv(f"{DATA}/VXN_History.csv", parse_dates=["DATE"], index_col="DATE")
vix_c = pd.read_csv(f"{DATA}/VIX_History.csv", parse_dates=["DATE"], index_col="DATE")

print("=== QC 1: NDX Yahoo vs FRED (clôtures) ===")
m = ndx[["Close"]].join(fred, how="inner").dropna()
rel = (m["Close"] / m["ndx_fred"] - 1).abs()
print(f"jours comparés: {len(m)}, écart relatif médian: {rel.median():.2e}, "
      f"max: {rel.max():.2e}, jours >0.1%: {(rel > 1e-3).sum()}")

print("\n=== QC 2: VXN Yahoo vs CBOE ===")
mv = vxn_y[["Close"]].join(vxn_c[["CLOSE"]], how="inner").dropna()
d = (mv["Close"] - mv["CLOSE"]).abs()
print(f"jours comparés: {len(mv)}, écart absolu médian: {d.median():.4f}, "
      f"max: {d.max():.4f}, jours >0.05: {(d > 0.05).sum()}")

print("\n=== QC 3: intégrité OHLC NDX ===")
bad = ((ndx["High"] < ndx["Low"]) | (ndx["High"] < ndx["Close"]) |
       (ndx["Low"] > ndx["Close"]) | (ndx["High"] < ndx["Open"]) |
       (ndx["Low"] > ndx["Open"]) | (ndx["Close"] <= 0)).sum()
zero_range = (ndx["High"] == ndx["Low"]).sum()
na = ndx[["Open", "High", "Low", "Close"]].isna().any(axis=1).sum()
print(f"violations OHLC: {bad}, jours High==Low: {zero_range}, jours avec NA: {na}")
r = np.log(ndx["Close"]).diff()
print(f"|rendement| > 15%: {(r.abs() > 0.15).sum()} jours -> {list(ndx.index[r.abs() > 0.15].date)}")

print("\n=== QC 4: calendrier ===")
gaps = ndx.index.to_series().diff().dt.days
print(f"trous > 5 jours calendaires: {(gaps > 5).sum()} "
      f"-> {list(ndx.index[gaps > 5].date)[:10]}")

# --- assemblage ---
master = pd.DataFrame(index=ndx.index)
master["ndx_open"], master["ndx_high"] = ndx["Open"], ndx["High"]
master["ndx_low"], master["ndx_close"] = ndx["Low"], ndx["Close"]
master["qqq_adj"] = qqq["AdjClose"]
# VXN: Yahoo avant 2009 (seule source), CBOE ensuite (source primaire)
vxn = vxn_c["CLOSE"].combine_first(vxn_y["Close"])
master["vxn"] = vxn
master["vix"] = vix_c["CLOSE"]
master = master.dropna(subset=["ndx_close"])
master.to_parquet(f"{DATA}/master.parquet")
print(f"\nmaster: {master.shape}, {master.index[0].date()} -> {master.index[-1].date()}")
print(master.notna().sum())

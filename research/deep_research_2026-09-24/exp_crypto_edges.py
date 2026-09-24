"""Crypto structural-edge tests (paper research only).

Data (all cloned from public GitHub; see report):
  Erdos_project/data/raw/BTCUSDT_funding.csv, BTCUSDT_premium_5m.csv  (Binance BTCUSDT perp, 2020-01..2026-06)
  funding_arb/funding_analysis/raw_data/*_funding.csv, kline_data/*_1h_{linear,spot}_kline.csv  (Bybit, 2023-01..2025-05)
  freqtrade-hyperliquid-data/.../*-1h-funding_rate.feather, *-1d-futures.feather  (Hyperliquid, funding 2023-05.., daily OHLCV..2026-03)
  statArb/data/*USDT-1d-data.csv  (Binance spot daily 2017-08..2021-02, includes some delisted pairs)

Causality: every signal at decision time t uses only data stamped <= t; P&L accrues over (t, t+h].
Trials are counted in TRIALS and printed.
"""
import glob, os, sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
TRIALS = []
ROWS = []


def stats(r, per_year, label, extra=None):
    r = pd.Series(r).dropna()
    if len(r) < 10:
        return
    mu, sd = r.mean(), r.std()
    sr = mu / sd * np.sqrt(per_year) if sd > 0 else np.nan
    t = mu / sd * np.sqrt(len(r)) if sd > 0 else np.nan
    eq = (1 + r).cumprod()
    mdd = (eq / eq.cummax() - 1).min()
    yr = r.groupby(r.index.year).apply(lambda x: x.mean() * per_year)
    ysr = r.groupby(r.index.year).apply(lambda x: x.mean() / x.std() * np.sqrt(per_year) if x.std() > 0 else np.nan)
    r25 = r[r.index.year == 2025]
    sr25 = r25.mean() / r25.std() * np.sqrt(per_year) if len(r25) > 5 and r25.std() > 0 else np.nan
    row = dict(test=label, start=r.index[0].date(), end=r.index[-1].date(), ann_ret=mu * per_year, SR=sr, t=t,
               MDD=mdd, SR2025=sr25, ann2025=(r25.mean() * per_year if len(r25) else np.nan),
               by_year=" ".join(f"{y}:{v*100:.0f}%/{s:.1f}" for (y, v), s in zip(yr.items(), ysr.values)))
    if extra:
        row.update(extra)
    ROWS.append(row)
    TRIALS.append(label)


# ---------------------------------------------------------------- A. BTC Binance conditional cash-and-carry
def test_btc_carry():
    d = os.path.join(ROOT, "Erdos_project/data/raw")
    f = pd.read_csv(f"{d}/BTCUSDT_funding.csv")
    f["ts"] = pd.to_datetime(f.fundingTime, utc=True, format="mixed").dt.floor("h")
    f = f.drop_duplicates("ts").set_index("ts").fundingRate.astype(float)
    p = pd.read_csv(f"{d}/BTCUSDT_premium_5m.csv", header=0)
    p.columns = ["ts", "o", "h", "l", "c", "v"][: len(p.columns)]
    p["ts"] = pd.to_datetime(p.ts, utc=True, format="mixed")
    # premium index at funding timestamps: 5m bar that opens at ts -> its open ~ premium at ts
    prem = p.set_index("ts").o.astype(float)
    prem = prem.reindex(f.index, method="ffill")
    df = pd.DataFrame({"f": f, "prem": prem}).dropna()
    # P&L for short perp + long spot per unit notional held over (t, t+1]:
    #   funding received at t+1  minus change in perp-over-index premium (approx perp ret - spot ret)
    df["pnl_next"] = df.f.shift(-1) - (df.prem.shift(-1) - df.prem)
    df["trail"] = df.f.rolling(21).mean() * 3 * 365  # 7d trailing, annualized, known at t
    perp_leg, spot_leg = 0.0005 + 0.0001, 0.0010 + 0.0001  # fee + half spread (VIP0 taker)
    switch_cost = perp_leg + spot_leg
    CAP = 1.5  # capital per unit notional: spot fully paid + 50% perp margin
    for entry, exit_ in [(None, None), (0.05, 0.0), (0.10, 0.05), (0.20, 0.10)]:
        pos = np.zeros(len(df))
        cur = 0
        for i, tr in enumerate(df.trail.values):
            if entry is None:
                cur = 1
            elif np.isnan(tr):
                cur = 0
            elif cur == 0 and tr > entry:
                cur = 1
            elif cur == 1 and tr < exit_:
                cur = 0
            pos[i] = cur
        pos = pd.Series(pos, df.index)
        cost = pos.diff().abs().fillna(pos.iloc[0]) * switch_cost
        r8 = (pos * df.pnl_next - cost) / CAP
        daily = r8.groupby(r8.index.floor("D")).sum()
        lab = "A BTC Binance carry " + ("always-on" if entry is None else f"enter>{entry:.0%} exit<{exit_:.0%}")
        stats(daily, 365, lab, dict(time_in=pos.mean(), switches=int(pos.diff().abs().sum())))
    # decomposition: funding-only vs basis
    fa = df.f.groupby(df.index.year).mean() * 3 * 365
    print("BTC Binance mean funding annualized by year:", (fa * 100).round(1).to_dict())


# ---------------------------------------------------------------- B. Bybit cross-sectional carry (spot long / perp short)
def load_bybit():
    kd = os.path.join(ROOT, "funding_arb/kline_data")
    fd = os.path.join(ROOT, "funding_arb/funding_analysis/raw_data")
    mp = pd.read_csv(f"{kd}/future_to_spot_mapping.csv").set_index("symbol").spotSymbol.to_dict()
    perp, spot, fund, turn = {}, {}, {}, {}
    for fp in glob.glob(f"{kd}/*_1h_linear_kline.csv"):
        s = os.path.basename(fp).split("_1h")[0]
        x = pd.read_csv(fp, usecols=["timestamp", "close", "turnover"], parse_dates=["timestamp"]).set_index("timestamp")
        x = x[~x.index.duplicated()]
        perp[s] = x.close[x.index.hour == 0]
        turn[s] = x.turnover.resample("D").sum()
    for fp in glob.glob(f"{kd}/*_1h_spot_kline.csv"):
        s = os.path.basename(fp).split("_1h")[0]
        x = pd.read_csv(fp, usecols=["timestamp", "close"], parse_dates=["timestamp"]).set_index("timestamp")
        x = x[~x.index.duplicated()]
        spot[s] = x.close[x.index.hour == 0]
    for fp in glob.glob(f"{fd}/*_funding.csv"):
        s = os.path.basename(fp).replace("_funding.csv", "")
        x = pd.read_csv(fp)
        ts = pd.to_datetime(x.fundingRateTimestamp, utc=True).dt.tz_convert(None)
        v = pd.Series(x.fundingRate.values, ts)
        v = v[~v.index.duplicated()]
        # payment at ts belongs to the day ending at next 00:00 -> label by ceil
        fund[s] = v.groupby(v.index.ceil("D")).sum()
    return perp, spot, fund, turn, mp


def test_bybit_carry(perp, spot, fund, turn, mp):
    pairs = [s for s in perp if s in fund and mp.get(s) in spot]
    P = pd.DataFrame({s: perp[s] for s in pairs})
    S = pd.DataFrame({s: spot[mp[s]] for s in pairs})
    F = pd.DataFrame({s: fund[s] for s in pairs}).reindex(P.index).fillna(0.0)
    T = pd.DataFrame({s: turn[s] for s in pairs}).reindex(P.index)
    B = np.log(P / S)
    avail = P.notna() & S.notna()
    F = F.where(avail)
    # next-day P&L of short perp/long spot, per unit notional: funding(d+1) - dBasis
    pnl = F.shift(-1) - (B.shift(-1) - B)
    pnl = pnl.clip(-0.5, 0.5)
    trail = F.rolling(7, min_periods=7).sum() / 7 * 365
    liq = T.rolling(30, min_periods=20).mean()
    print(f"Bybit carry universe: {len(pairs)} perp/spot pairs, {P.index[0].date()}..{P.index[-1].date()}")
    CAP = 1.5
    leg = (0.00055 + 0.0005) + (0.0010 + 0.0005)  # perp taker+slip, spot taker+slip
    for N in (5, 10):
        for reb in (1, 7):
            for thr in (0.0, 0.10):
                w_prev = pd.Series(0.0, index=pairs)
                out = []
                W = None
                for i, d in enumerate(P.index[:-1]):
                    if i % reb == 0:
                        tr = trail.loc[d]
                        ok = avail.loc[d] & avail.iloc[i + 1] if i + 1 < len(P) else avail.loc[d]
                        elig = tr[ok & (liq.loc[d] > 2e6)].dropna()
                        top = elig[elig > thr].nlargest(N)
                        W = pd.Series(0.0, index=pairs)
                        if len(top):
                            W[top.index] = 1.0 / N  # uninvested slots stay in cash
                    turnover = (W - w_prev).abs().sum()
                    r = (W * pnl.loc[d].fillna(0)).sum() - turnover * leg
                    out.append((P.index[i + 1], r / CAP))
                    w_prev = W
                r = pd.Series(dict(out))
                stats(r, 365, f"B Bybit XS carry top{N} reb{reb}d thr{thr:.0%}")


# ---------------------------------------------------------------- C/D. Cross-sectional momentum & funding signal (weekly)
def xs_weekly(close, dvol, fundd, label, topk=30, costs_leg=0.001, lookbacks=(7, 28), per="W", funding_sig=False):
    """close: daily close DataFrame; dvol: daily dollar volume; fundd: daily funding paid by longs (or None)."""
    idx = close.index
    reb_days = idx[idx.dayofweek == 0]  # Mondays 00:00 closes
    liq = dvol.rolling(30, min_periods=20).mean()
    res = {}
    sigs = []
    for L in lookbacks:
        sigs.append((f"mom{L}d", close / close.shift(L) - 1, 1))
        if L == 7:
            sigs.append(("rev7d", close / close.shift(7) - 1, -1))
    if funding_sig and fundd is not None:
        sigs.append(("lowfund7d", fundd.rolling(7, min_periods=7).sum(), -1))
    for name, sig, sgn in sigs:
        rows = []
        w_prev = pd.Series(0.0, index=close.columns)
        for a, b in zip(reb_days[:-1], reb_days[1:]):
            l = liq.loc[a].dropna()
            uni = l.nlargest(topk).index
            s = (sgn * sig.loc[a, uni]).dropna()
            s = s[close.loc[a, s.index].notna()]
            if len(s) < 10:
                continue
            q = max(2, len(s) // 5)
            longs, shorts = s.nlargest(q).index, s.nsmallest(q).index
            W = pd.Series(0.0, index=close.columns)
            W[longs] = 0.5 / q
            W[shorts] = -0.5 / q
            # holding return; if price missing at b (delisted/halt) use last available price <= b
            pb = close.loc[:b].ffill().loc[b]
            ret = (pb / close.loc[a] - 1).clip(-0.95, 5)
            if fundd is not None:
                ret = ret - fundd.loc[a:b].iloc[1:].sum()  # longs pay funding, shorts receive
            ret = ret.fillna(0)
            turnover = (W - w_prev).abs().sum()
            r = (W * ret).sum() - turnover * costs_leg
            ew = ret[uni].mean()
            rows.append((b, r, (W[longs] * 2 * ret[longs]).sum() - ew))
            w_prev = W
        r = pd.DataFrame(rows, columns=["d", "ls", "long_minus_ew"]).set_index("d")
        stats(r.ls, 52, f"{label} {name} L/S top{topk}")
        stats(r.long_minus_ew, 52, f"{label} {name} long-leg minus EW (gross of costs)")


def test_hl():
    h = os.path.join(ROOT, "freqtrade-hyperliquid-data/user_data/data/hyperliquid/futures")
    C, V, F = {}, {}, {}
    for fp in glob.glob(f"{h}/*_USDC_USDC-1d-futures.feather"):
        s = os.path.basename(fp).split("_USDC")[0]
        if "-" in s:  # HIP-3 builder markets (equities etc.) excluded
            continue
        x = pd.read_feather(fp).set_index("date")
        x = x[x.volume > 0]  # drop pre-listing backfilled rows (volume==0)
        if len(x) < 60:
            continue
        C[s] = x.close
        V[s] = x.close * x.volume
        ff = f"{h}/{s}_USDC_USDC-1h-funding_rate.feather"
        if os.path.exists(ff):
            y = pd.read_feather(ff).set_index("date").open
            y = y[y.index >= "2023-06-01"]
            F[s] = y.groupby(y.index.ceil("D")).sum()
    C = pd.DataFrame(C).sort_index()
    C = C[C.index >= "2023-06-01"]
    V = pd.DataFrame(V).reindex(C.index)
    F = pd.DataFrame(F).reindex(index=C.index, columns=C.columns).fillna(0.0)
    print(f"HL universe: {C.shape[1]} coins {C.index[0].date()}..{C.index[-1].date()}")
    xs_weekly(C, V, F, "C HL perps", topk=30, costs_leg=0.00045 + 0.0005, funding_sig=True)
    # funding-only carry on HL: short perp (hedge assumed elsewhere at zero basis cost), top-10 trailing funding
    trail = F.rolling(7, min_periods=7).sum()
    liq = V.rolling(30, min_periods=20).mean()
    out = []
    for i in range(30, len(C) - 1):
        d = C.index[i]
        uni = liq.loc[d].dropna().nlargest(30).index
        top = trail.loc[d, uni].nlargest(10)
        top = top[top > 0.10 / 365 * 7]
        r = F.iloc[i + 1][top.index].sum() / 10 if len(top) else 0.0
        out.append((C.index[i + 1], r / 1.5))
    r = pd.Series(dict(out))
    stats(r, 365, "C HL funding-only carry top10 >10% (NO basis, NO fees: upper bound)")
    oct = r["2025-10-05":"2025-10-20"]
    print("HL funding-only carry daily around 2025-10-10:", (oct * 1e4).round(1).to_dict())
    # BTC/ETH HL median funding by year
    for s in ("BTC", "ETH", "SOL"):
        print(s, "HL funding annualized by year:", (F[s].groupby(F.index.year).mean() * 365 * 100).round(1).to_dict())


def test_binance_spot_mom():
    d = os.path.join(ROOT, "statArb/data")
    C, V = {}, {}
    for fp in glob.glob(f"{d}/*USDT-1d-data.csv"):
        s = os.path.basename(fp).split("-1d")[0]
        if s.replace("USDT", "") in ("USDC", "BUSD", "TUSD", "PAX", "USDS", "EUR", "GBP", "AUD", "DAI", "SUSD") or \
                any(k in s for k in ("UP", "DOWN", "BULL", "BEAR")):
            continue
        x = pd.read_csv(fp, parse_dates=["timestamp"]).drop_duplicates("timestamp").set_index("timestamp")
        C[s], V[s] = x.close, x.close * x.volume
    C = pd.DataFrame(C).sort_index()
    V = pd.DataFrame(V).reindex(C.index)
    C = C[C.index >= "2018-01-01"]
    V = V.reindex(C.index)
    print(f"Binance spot universe: {C.shape[1]} pairs {C.index[0].date()}..{C.index[-1].date()} "
          f"(ended early/delisted: {(C.iloc[-1].isna()).sum()})")
    xs_weekly(C, V, None, "D Binance spot", topk=50, costs_leg=0.001 + 0.001)


def test_bybit_mom(perp, fund, turn):
    C = pd.DataFrame(perp).sort_index()
    V = pd.DataFrame(turn).reindex(C.index)
    F = pd.DataFrame(fund).reindex(index=C.index, columns=C.columns).fillna(0.0)
    xs_weekly(C, V, F, "E Bybit perps", topk=30, costs_leg=0.00055 + 0.0005, funding_sig=True)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    test_btc_carry()
    perp, spot, fund, turn, mp = load_bybit()
    test_bybit_carry(perp, spot, fund, turn, mp)
    test_bybit_mom(perp, fund, turn)
    test_hl()
    test_binance_spot_mom()
    out = pd.DataFrame(ROWS)
    fmt = out.copy()
    for c in ("ann_ret", "MDD", "ann2025", "time_in"):
        if c in fmt:
            fmt[c] = (fmt[c] * 100).round(1)
    for c in ("SR", "t", "SR2025"):
        fmt[c] = fmt[c].round(2)
    print(fmt.drop(columns=["by_year"]).to_string())
    print()
    for _, r in out.iterrows():
        print(r.test, "|", r.by_year)
    print("\nTOTAL TRIALS:", len(TRIALS))
    out.to_csv(os.path.join(ROOT, "results.csv"), index=False)

"""Factor edge lab (paper/shadow research only).

Data (all fetched from GitHub mirrors; see SHA256SUMS / README in report):
  ff/   Ken French CSVs mirrored in github.com/fernando-duarte/ERP (Input/, LFS via media.githubusercontent.com), CRSP vintage 202111.
  aqrx/ AQR data library xlsx mirrored in github.com/scotty-jackson/AQRFactorX (data/aqr_raw), through 2025-09-30.
Everything causal: signals at t use returns through t-1 only. Trial counter printed at end.
"""
import os, io, re, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.join(HERE, "ff")
AQR = os.path.join(HERE, "aqrx", "data", "aqr_raw")
TRIALS = []


def trial(name):
    TRIALS.append(name)


# ---------------- loaders ----------------
def read_ff(fname, section=0):
    """Parse the `section`-th table of a Ken French CSV (0 = first, usually monthly VW)."""
    lines = open(os.path.join(FF, fname), encoding="latin1").read().splitlines()
    blocks, cur, hdr = [], None, None
    for ln in lines:
        s = ln.strip()
        if s.startswith(",") or (s.lower().startswith("date,") ):
            hdr = [h.strip() for h in s.split(",")[1:]]
            cur = []
            blocks.append((hdr, cur))
            continue
        if cur is not None and re.match(r"^\d{6,8}\s*,", s):
            cur.append(s)
        elif cur is not None and cur and not s:
            cur = None
    hdr, rows = blocks[section]
    df = pd.read_csv(io.StringIO("\n".join(rows)), header=None)
    idx = df[0].astype(str).str.strip()
    df = df.iloc[:, 1:]
    df.columns = hdr[: df.shape[1]]
    if len(idx.iloc[0]) == 6:
        df.index = pd.to_datetime(idx, format="%Y%m") + pd.offsets.MonthEnd(0)
    else:
        df.index = pd.to_datetime(idx, format="%Y%m%d")
    df = df.astype(float).replace([-99.99, -999], np.nan) / 100.0
    return df


def read_aqr(path, sheet, col="USA"):
    d = pd.read_excel(os.path.join(AQR, path), sheet_name=sheet, skiprows=18)
    d = d[pd.to_datetime(d["DATE"], format="%m/%d/%Y", errors="coerce").notna()]
    s = pd.Series(d[col].values, index=pd.to_datetime(d["DATE"], format="%m/%d/%Y"), name=sheet).astype(float)
    return s.dropna()


# ---------------- stats ----------------
def nw_t(x, lags=6):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    n = len(x)
    e = x - x.mean()
    v = e @ e / n
    for L in range(1, lags + 1):
        v += 2 * (1 - L / (lags + 1)) * (e[L:] @ e[:-L]) / n
    return x.mean() / np.sqrt(v / n)


def stats(r, ppy=12):
    r = r.dropna()
    if len(r) < 24:
        return dict(n=len(r), ann=np.nan, vol=np.nan, sr=np.nan, t=np.nan)
    return dict(n=len(r), ann=r.mean() * ppy, vol=r.std() * np.sqrt(ppy),
                sr=r.mean() / r.std() * np.sqrt(ppy), t=nw_t(r))


def ols_alpha(y, x):
    d = pd.concat([y, x], axis=1).dropna()
    Y = d.iloc[:, 0].values
    X = np.column_stack([np.ones(len(d)), d.iloc[:, 1:].values])
    b, *_ = np.linalg.lstsq(X, Y, rcond=None)
    e = Y - X @ b
    # HAC (NW 6) se for intercept
    n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    S = (X * e[:, None]).T @ (X * e[:, None])
    for L in range(1, 7):
        w = 1 - L / 7
        G = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None])
        S += w * (G + G.T)
    V = XtXi @ S @ XtXi
    return b[0] * 12, b[0] / np.sqrt(V[0, 0])


def fmt(d):
    return f"{d['n']:4d} {d['ann']*100:7.2f}% {d['vol']*100:6.2f}% SR {d['sr']:5.2f} t {d['t']:5.2f}"


# ---------------- load ----------------
ff3 = read_ff("F-F_Research_Data_Factors.CSV")
mom = read_ff("F-F_Momentum_Factor.CSV")
ff5 = read_ff("F-F_Research_Data_5_Factors_2x3.CSV")
ffm = pd.concat([ff3[["Mkt-RF", "SMB", "HML"]], mom.iloc[:, 0].rename("MOM"), ff5[["RMW", "CMA"]], ff3["RF"]], axis=1)
ffd3 = read_ff("F-F_Research_Data_Factors_daily.CSV")
ffdm = read_ff("F-F_Momentum_Factor_daily.CSV")
ffd5 = read_ff("F-F_Research_Data_5_Factors_2x3_daily.CSV")
ffd = pd.concat([ffd3[["Mkt-RF", "SMB", "HML"]], ffdm.iloc[:, 0].rename("MOM"), ffd5[["RMW", "CMA"]]], axis=1)
ind = read_ff("49_Industry_Portfolios.CSV", 0)

aqrm = pd.concat({
    "MKT": read_aqr("Betting_Against_Beta/Betting-Against-Beta-Equity-Factors-Monthly.xlsx", "MKT"),
    "SMB": read_aqr("Betting_Against_Beta/Betting-Against-Beta-Equity-Factors-Monthly.xlsx", "SMB"),
    "HML_FF": read_aqr("Betting_Against_Beta/Betting-Against-Beta-Equity-Factors-Monthly.xlsx", "HML FF"),
    "HML_DEVIL": read_aqr("HML_Details/The-Devil-in-HMLs-Details-Factors-Monthly.xlsx", "HML Devil"),
    "UMD": read_aqr("Betting_Against_Beta/Betting-Against-Beta-Equity-Factors-Monthly.xlsx", "UMD"),
    "BAB": read_aqr("Betting_Against_Beta/Betting-Against-Beta-Equity-Factors-Monthly.xlsx", "BAB Factors"),
    "QMJ": read_aqr("Quality_Minus_Junk/Quality-Minus-Junk-Factors-Monthly.xlsx", "QMJ Factors"),
}, axis=1)
aqrm.index = aqrm.index + pd.offsets.MonthEnd(0)

print("DATA COVERAGE")
for n, d in [("FF monthly", ffm), ("FF daily", ffd), ("49 ind", ind), ("AQR monthly", aqrm)]:
    print(f"  {n:12s} {d.index.min().date()} -> {d.index.max().date()}  cols={list(d.columns)[:8]}")
# cross-check AQR vs FF where they overlap (provenance sanity)
ov = pd.concat([aqrm["MKT"], ffm["Mkt-RF"], aqrm["UMD"], ffm["MOM"]], axis=1).dropna()
print(f"  corr AQR MKT vs FF Mkt-RF {ov.iloc[:,0].corr(ov.iloc[:,1]):.4f}; AQR UMD vs FF MOM {ov.iloc[:,2].corr(ov.iloc[:,3]):.4f}")

# ---------------- (A) factor premia by era ----------------
print("\n(A) FACTOR PREMIA  n ann vol SR t(NW6)")
PUB = {"Mkt-RF": None, "SMB": 1981, "HML": 1992, "MOM": 1993, "RMW": 2015, "CMA": 2015,
       "BAB": 2014, "QMJ": 2019, "HML_DEVIL": 2013, "UMD": 1993, "HML_FF": 1992, "MKT": None}
series = {**{k: ffm[k] for k in ["Mkt-RF", "SMB", "HML", "MOM", "RMW", "CMA"]},
          **{"AQR_" + k: aqrm[k] for k in aqrm.columns}}
rows = []
for k, s in series.items():
    s = s.dropna()
    base = k.replace("AQR_", "")
    p = PUB.get(base)
    eras = {"full": s, "<2000": s[:"1999"], "2000+": s["2000":], "2010+": s["2010":], "2020+": s["2020":]}
    if p:
        eras["postpub"] = s[str(p + 1):]
    out = {e: stats(v) for e, v in eras.items()}
    trial(f"premia:{k}")
    rows.append((k, out))
    print(f"{k:14s} full {fmt(out['full'])}")
    for e in ["<2000", "2000+", "2010+", "2020+", "postpub"]:
        if e in out:
            print(f"{'':14s} {e:7s} {fmt(out[e])}")

# decade SR table
print("\nDECADE SHARPE (annualised)")
dec = {}
for k, s in series.items():
    s = s.dropna()
    g = s.groupby((s.index.year // 10) * 10).apply(lambda r: r.mean() / r.std() * np.sqrt(12) if len(r) > 23 else np.nan)
    dec[k] = g
dec = pd.DataFrame(dec).T
print(dec.round(2).to_string())

# ---------------- (B) volatility-managed (Moreira-Muir 2017) ----------------
print("\n(B) VOL-MANAGED f*c/RV_{t-1}; alpha vs unmanaged, SR diff; expanding c (causal)")
aqrd = {}
for nm, f, sh in [("BAB", "Betting_Against_Beta/Betting-Against-Beta-Equity-Factors-Daily.xlsx", "BAB Factors"),
                  ("QMJ", "Quality_Minus_Junk/Quality-Minus-Junk-Factors-Daily.xlsx", "QMJ Factors"),
                  ("MKT", "Betting_Against_Beta/Betting-Against-Beta-Equity-Factors-Daily.xlsx", "MKT"),
                  ("UMD", "Betting_Against_Beta/Betting-Against-Beta-Equity-Factors-Daily.xlsx", "UMD")]:
    try:
        aqrd[nm] = read_aqr(f, sh)
    except Exception as ex:
        print("  daily load fail", nm, ex)
aqrd = pd.DataFrame(aqrd)


def vol_managed(daily, monthly, name, start=None, cap=None, cost_bps=0):
    rv = daily.dropna().pow(2).groupby(pd.Grouper(freq="ME")).sum()
    rv = rv[rv > 0]
    w = (1 / rv).shift(1)  # use previous month's realised variance only
    m = monthly.dropna()
    d = pd.concat([m, w], axis=1, keys=["f", "w"], sort=True).dropna()
    raw = d["f"] * d["w"]
    # causal scale: expanding target vol from past unmanaged returns
    c = d["f"].expanding(36).std().shift(1) / raw.expanding(36).std().shift(1)
    lev0 = (d["w"] * c)
    if cap:
        lev0 = lev0.clip(upper=cap)
    # cost: cost_bps per unit change in factor notional (both legs of a L/S factor => charge applies to gross change)
    vm = (lev0 * d["f"] - lev0.diff().abs() * cost_bps / 1e4).dropna()
    f = d["f"].loc[vm.index]
    if start:
        vm, f = vm[start:], f[start:]
    a, t = ols_alpha(vm, f)
    s1, s0 = stats(vm), stats(f)
    trial(f"volman:{name}:{start}:{cap}:{cost_bps}")
    lev = lev0.loc[vm.index]
    print(f"  {name:10s} {str(start or 'full'):5s} cap{cap} c{cost_bps:2d} SR unm {s0['sr']:5.2f} -> vm {s1['sr']:5.2f}  alpha {a*100:6.2f}%/yr t {t:5.2f}  max lev {lev.max():5.1f}x")


for k in ["Mkt-RF", "SMB", "HML", "MOM", "RMW", "CMA"]:
    for st in [None, "2000"]:
        vol_managed(ffd[k], ffm[k], "FF_" + k, st)
for k in aqrd.columns:
    for st in [None, "2000", "2010"]:
        vol_managed(aqrd[k], aqrm[k], "AQR_" + k, st)

print("  -- implementable variant: leverage cap 2x, 20bp per unit notional change")
for k in ["MOM"]:
    for st in [None, "2000"]:
        vol_managed(ffd[k], ffm[k], "FF_" + k, st, cap=2, cost_bps=20)
for k in aqrd.columns:
    for st in [None, "2000", "2010"]:
        vol_managed(aqrd[k], aqrm[k], "AQR_" + k, st, cap=2, cost_bps=20)

# ---------------- (C) factor momentum (Ehsani-Linnainmaa) ----------------
print("\n(C) TIME-SERIES FACTOR MOMENTUM: long f if trailing 12m sum>0 else short (causal)")


def factor_mom(df, name, look=12, longonly=False):
    sig = np.sign(df.rolling(look).sum().shift(1))
    if longonly:
        sig = sig.clip(lower=0)
    tsfm = (sig * df).mean(axis=1, skipna=True)
    ew = df.mean(axis=1, skipna=True)
    d = pd.concat([tsfm, ew], axis=1, keys=["tsfm", "ew"]).dropna()
    d = d[d.index >= df.dropna(how="all").index[look + 1]]
    trial(f"fmom:{name}:{look}:{longonly}")
    for st in [None, "2000", "2010"]:
        x = d[st:] if st else d
        a, t = ols_alpha(x["tsfm"], x["ew"])
        print(f"  {name:22s} L{look:2d} {'LO' if longonly else 'LS'} {str(st or 'full'):5s} TSFM SR {stats(x['tsfm'])['sr']:5.2f} | EW SR {stats(x['ew'])['sr']:5.2f} | alpha vs EW {a*100:5.2f}% t {t:5.2f}")


ffset = ffm[["SMB", "HML", "MOM", "RMW", "CMA"]]["1964":]
aqset = aqrm[["SMB", "HML_FF", "UMD", "BAB", "QMJ"]]["1958":]
for look in [1, 12]:
    factor_mom(ffset, "FF5+MOM ex-mkt", look)
    factor_mom(aqset, "AQR SMB,HML,UMD,BAB,QMJ", look)
factor_mom(aqset, "AQR ... long-or-flat", 12, longonly=True)

# ---------------- (D) industry momentum (Moskowitz-Grinblatt) with costs ----------------
print("\n(D) 49-INDUSTRY MOMENTUM, VW, long top-N short bottom-N, monthly rebalance; cost per unit one-way turnover")
R = ind.copy()
R = R.where(R > -0.99)


def ind_mom(look, skip, N, cost_bps, start="1930"):
    sig = (1 + R).rolling(look).apply(np.prod, raw=True).shift(1 + skip) - 1
    wts = []
    for dt in R.index:
        s = sig.loc[dt].dropna()
        r = R.loc[dt].dropna()
        s = s[s.index.isin(r.index)]
        w = pd.Series(0.0, index=R.columns)
        if len(s) >= 2 * N:
            o = s.sort_values()
            w[o.index[-N:]] = 1.0 / N
            w[o.index[:N]] = -1.0 / N
        wts.append(w)
    W = pd.DataFrame(wts, index=R.index)
    gross = (W * R.fillna(0)).sum(axis=1)
    # drifted-weight turnover approximated by weight change (ignores intra-month drift: slightly understates)
    to = W.diff().abs().sum(axis=1)
    net = gross - to * cost_bps / 1e4
    ok = W.abs().sum(axis=1) > 0
    return gross[ok][start:], net[ok][start:], to[ok][start:].mean()


for look, skip in [(12, 1), (6, 0), (1, 0)]:
    for cost in [0, 10, 25]:
        g, n_, to = ind_mom(look, skip, 7, cost)
        trial(f"indmom:{look}-{skip}:{cost}")
        line = f"  L{look:2d}/skip{skip} N7 cost {cost:2d}bp  turnover/mo {to:4.2f}"
        for st in ["1930", "2000", "2010"]:
            x = n_[st:]
            s = stats(x)
            line += f" | {st}+ SR {s['sr']:5.2f} t {s['t']:5.2f} ann {s['ann']*100:5.1f}%"
        print(line)

print(f"\nTOTAL TRIALS (configurations evaluated): {len(TRIALS)}")
print("Bonferroni-ish 5% two-sided hurdle for", len(TRIALS), "trials: |t| >", round(float(__import__('scipy.stats', fromlist=['norm']).norm.ppf(1 - 0.025 / len(TRIALS))), 2) if 'scipy' in sys.modules or True else "")

"""F1 CRYPTO-CARRY-001 analysis harness (Revision 1 of the pre-registration).

Reads only files named in an acquisition manifest directory. Never touches the
network. Fails closed: any unrecognised format raises before a result is
persisted or printed.

    python3 -I run_f1.py STAGE_A DATA_DIR RESULT_PATH
    python3 -I run_f1.py STAGE_B DATA_DIR RESULT_PATH STAGE_A_RESULT_PATH

Raw-line date filtering: a line whose first-field timestamp is outside the
stage's file window is dropped before any numeric conversion.
"""
import csv
import io
import json
import math
import os
import statistics
import sys
import zipfile
from collections import defaultdict

sys.dont_write_bytecode = True

DAY_MS = 86_400_000
MIN_MS = 60_000


def _ms(y, m, d):
    import datetime as dt
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


# Stage windows: raw-line acceptance (inclusive start, exclusive end), in ms.
STAGES = {
    "STAGE_A": {"read": (_ms(2020, 1, 1), _ms(2024, 1, 1)),
                "stat": (_ms(2020, 1, 1), _ms(2024, 1, 1))},
    "STAGE_B": {"read": (_ms(2023, 11, 1), _ms(2026, 10, 1)),
                "stat": (_ms(2024, 1, 1), _ms(2026, 10, 1))},
}
THETAS = (0.05, 0.10, 0.20)
FEE_SPOT, FEE_PERP = 0.0010, 0.0005
SLIP_TOP, SLIP_REST = 0.0002, 0.0010
CAP_W, LIQ_MULT, LIQ_PEN, BAR_DAYS = 0.10, 1.25, 0.01, 30
MIN_QV, MIN_HIST = 5_000_000.0, 60
CASH_HURDLE = 0.04
Z_ONE_SIDED = 2.5391848


class FormatError(RuntimeError):
    pass


def norm_ts(token):
    """Normalise a timestamp token to milliseconds; fail closed otherwise."""
    v = int(token)
    if 10**12 <= v < 10**14:
        return v
    if 10**15 <= v < 10**17:
        return v // 1000
    raise FormatError(f"unrecognised timestamp magnitude: {len(token)} digits")


def iter_rows(zip_path, read_lo, read_hi, n_fields_min):
    """Yield split rows whose first-field timestamp lies in [read_lo, read_hi)."""
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        if len(names) != 1 or not names[0].endswith(".csv"):
            raise FormatError("unexpected zip layout")
        with z.open(names[0]) as f:
            first = True
            for raw in io.TextIOWrapper(f, encoding="ascii", newline=""):
                line = raw.strip()
                if not line:
                    continue
                head = line.split(",", 1)[0]
                if first:
                    first = False
                    if not head.lstrip("-").isdigit():
                        continue  # header row; content checked by caller via width
                if not head.isdigit():
                    raise FormatError("non-numeric timestamp field")
                ts = norm_ts(head)
                if ts < read_lo or ts >= read_hi:
                    continue
                row = next(csv.reader([line]))
                if len(row) < n_fields_min:
                    raise FormatError("row too short")
                row[0] = str(ts)
                yield row


def load_symbol(data_dir, sym, read):
    lo, hi = read
    out = {"funding": defaultdict(list), "spot": {}, "perp": {}}
    for ds in ("funding", "perp1d", "spot1d"):
        d = os.path.join(data_dir, ds, sym)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".zip"):
                continue
            p = os.path.join(d, fn)
            if ds == "funding":
                for r in iter_rows(p, lo, hi, 3):
                    ts = int(r[0])
                    slot = int(round(ts / MIN_MS)) * MIN_MS
                    out["funding"][slot].append(float(r[-1]))
            else:
                tgt = out["spot" if ds == "spot1d" else "perp"]
                for r in iter_rows(p, lo, hi, 8):
                    day = int(r[0]) // DAY_MS
                    tgt[day] = {"high": float(r[2]), "close": float(r[4]), "qv": float(r[7])}
    return out


def build_funding_days(funding):
    """fund_sig[d] = rows with slot in [D_d, D_d+1); fund_earn[d] = slot in (D_d, D_d+1]."""
    sig, earn = defaultdict(float), defaultdict(float)
    has = set()
    for slot, vals in funding.items():
        v = sum(vals)
        d_sig = slot // DAY_MS
        sig[d_sig] += v
        has.add(d_sig)
        d_earn = (slot - 1) // DAY_MS
        earn[d_earn] += v
    return sig, earn, has


def median(xs):
    return statistics.median(xs)


class SymData:
    def __init__(self, sym, raw):
        self.sym = sym
        self.spot, self.perp = raw["spot"], raw["perp"]
        self.sig, self.earn, self.has_fund = build_funding_days(raw["funding"])

    def eligible(self, d):
        for k in range(MIN_HIST):
            if (d - k) not in self.spot or (d - k) not in self.perp:
                return False, None
        qv = [self.spot[d - k]["qv"] for k in range(30)]
        m = median(qv)
        return m >= MIN_QV, m

    def signal(self, d):
        days = range(d - 6, d + 1)
        if any(x not in self.has_fund for x in days):
            return None
        return sum(self.sig[x] for x in days) / 7.0 * 365.0


def simulate(syms, theta, cost_mult, d_first, d_last):
    """Return daily returns list for days d_first..d_last, plus diagnostics."""
    nav = 1.0
    pos = {}
    barred = {}
    rets, exposure_days, liqs = [], 0, 0
    fee_total = 0.0
    day_nav = {}
    for d in range(d_first, d_last + 1):
        nav_start = nav
        # 1. P&L of positions open at the start of day d
        for sym in sorted(pos):
            p, s = pos[sym], syms[sym]
            if d not in s.spot or d not in s.perp or (d - 1) not in s.spot or (d - 1) not in s.perp:
                raise FormatError(f"missing bar for open position {sym} on day {d}")
            sp0, sp1 = s.spot[d - 1]["close"], s.spot[d]["close"]
            pp0, pp1 = s.perp[d - 1]["close"], s.perp[d]["close"]
            q = p["q"]
            if s.perp[d]["high"] >= LIQ_MULT * p["ref"]:
                liq_px = LIQ_MULT * p["ref"]
                pnl = q * (sp1 - sp0) - q * (liq_px - pp0)
                pen = LIQ_PEN * q * liq_px
                exit_cost = cost_mult * q * sp1 * (FEE_SPOT + p["slip"])
                nav += pnl - pen - exit_cost
                fee_total += pen + exit_cost
                barred[sym] = d + BAR_DAYS
                p["liq"] = True
                liqs += 1
            else:
                fund = s.earn.get(d, 0.0) * q * pp1
                nav += q * (sp1 - sp0) - q * (pp1 - pp0) + fund
        for sym in [k for k, v in pos.items() if v.get("liq")]:
            del pos[sym]
        # 2. decisions at the close of day d
        info = {}
        for sym, s in syms.items():
            ok, m = s.eligible(d)
            sg = s.signal(d)
            info[sym] = (ok, m, sg)
        for sym in sorted(pos):
            ok, m, sg = info[sym]
            if (not ok) or sg is None or sg < theta / 2.0:
                p, s = pos.pop(sym), syms[sym]
                c = cost_mult * p["q"] * (s.spot[d]["close"] * (FEE_SPOT + p["slip"]) + s.perp[d]["close"] * (FEE_PERP + p["slip"]))
                nav -= c
                fee_total += c
        elig = {k: v for k, v in info.items() if v[0]}
        ranked = sorted(elig, key=lambda k: (-elig[k][1], k))
        top20 = set(ranked[:20])
        cands = [k for k in sorted(elig) if k not in pos and barred.get(k, -1) < d
                 and elig[k][2] is not None and elig[k][2] >= theta]
        if cands:
            deployed = sum(p["cap"] for p in pos.values())
            avail = max(0.0, nav - deployed)
            k_after = len(pos) + len(cands)
            w = min(CAP_W, 1.0 / k_after, avail / nav / len(cands)) if nav > 0 else 0.0
            if w > 0:
                for sym in cands:
                    s = syms[sym]
                    cap = w * nav
                    notional = cap * 0.75
                    sp, pp = s.spot[d]["close"], s.perp[d]["close"]
                    q = notional / sp
                    slip = SLIP_TOP if sym in top20 else SLIP_REST
                    c = cost_mult * q * (sp * (FEE_SPOT + slip) + pp * (FEE_PERP + slip))
                    nav -= c
                    fee_total += c
                    pos[sym] = {"q": q, "ref": pp, "cap": cap, "slip": slip}
        if d == d_last:
            for sym in sorted(pos):
                p, s = pos.pop(sym), syms[sym]
                c = cost_mult * p["q"] * (s.spot[d]["close"] * (FEE_SPOT + p["slip"]) + s.perp[d]["close"] * (FEE_PERP + p["slip"]))
                nav -= c
                fee_total += c
        if pos:
            exposure_days += 1
        rets.append(nav / nav_start - 1.0)
        day_nav[d] = nav
    return rets, {"exposure_days": exposure_days, "liquidations": liqs, "fees": fee_total, "final_nav": nav}


def nw_se_mean(x, lags):
    n = len(x)
    mu = sum(x) / n
    e = [v - mu for v in x]
    g0 = sum(v * v for v in e) / n
    s = g0
    for L in range(1, lags + 1):
        w = 1.0 - L / (lags + 1.0)
        g = sum(e[i] * e[i - L] for i in range(L, n)) / n
        s += 2.0 * w * g
    return math.sqrt(max(s, 0.0) / n)


def stats_for(rets, d_first, quarter_of):
    n = len(rets)
    mu = sum(rets) / n
    sd = statistics.pstdev(rets)
    se = max(nw_se_mean(rets, 7), nw_se_mean(rets, 21))
    sr = mu / sd * math.sqrt(365) if sd > 0 else 0.0
    se_sr = se / sd * math.sqrt(365) if sd > 0 else float("inf")
    t = mu / se if se > 0 else 0.0
    q = defaultdict(list)
    for i, r in enumerate(rets):
        q[quarter_of(d_first + i)].append(r)
    qpos = 0
    for k, v in q.items():
        prod = 1.0
        for r in v:
            prod *= 1.0 + r
        if any(r != 0.0 for r in v) and prod - 1.0 > 0:
            qpos += 1
    return {"n_days": n, "mean_daily": mu, "sd_daily": sd, "sharpe_annual": sr, "se_mean_max_nw": se,
            "se_sharpe": se_sr, "t_one_sided": t, "quarters": len(q), "quarters_positive": qpos,
            "excess_over_cash_daily": mu - CASH_HURDLE / 365.0, "exposure_days_share": None}


def quarter_of(day):
    import datetime as dt
    x = dt.datetime.fromtimestamp(day * 86400, dt.timezone.utc)
    return (x.year, (x.month - 1) // 3 + 1)


def classify(base, stress, n_quarters, exposure_share):
    if exposure_share < 0.10:
        return "DEGENERATE_EXPOSURE"
    confirmed = (base["t_one_sided"] >= Z_ONE_SIDED and stress["mean_daily"] > 0
                 and base["quarters_positive"] >= 6 and n_quarters == 11)
    if confirmed:
        return "CONFIRMED"
    if base["sharpe_annual"] + 1.645 * base["se_sharpe"] < 1.5:
        return "NOT_CONFIRMED_EXCLUDES_SR_1.5"
    return "INCONCLUSIVE_UNDERPOWERED"


def run(stage, data_dir, result_path, stage_a_result=None):
    cfg = STAGES[stage]
    syms_list = sorted(os.listdir(os.path.join(data_dir, "funding")))
    syms = {}
    for sym in syms_list:
        raw = load_symbol(data_dir, sym, cfg["read"])
        sd = SymData(sym, raw)
        if sd.spot and sd.perp and sd.sig:
            syms[sym] = sd
    d_first, d_last = cfg["stat"][0] // DAY_MS, (cfg["stat"][1] - 1) // DAY_MS
    if stage == "STAGE_B":
        sa = json.load(open(stage_a_result))
        thetas = [sa["selected_theta"]]
    else:
        thetas = list(THETAS)
    cells = {}
    for th in THETAS:
        if th not in thetas and stage == "STAGE_B":
            pass
        base_r, base_d = simulate(syms, th, 1.0, d_first, d_last)
        stress_r, _ = simulate(syms, th, 2.0, d_first, d_last)
        b = stats_for(base_r, d_first, quarter_of)
        s = stats_for(stress_r, d_first, quarter_of)
        share = base_d["exposure_days"] / len(base_r)
        b["exposure_days_share"] = share
        cells[str(th)] = {"base": b, "stress": s, "diag": base_d,
                          "status": classify(b, s, b["quarters"], share)}
        if stage == "STAGE_B" and th != thetas[0]:
            cells[str(th)]["eligible_for_confirmed"] = False
    out = {"stage": stage, "n_symbols": len(syms), "cells": cells}
    if stage == "STAGE_A":
        best = max(THETAS, key=lambda th: (round(cells[str(th)]["base"]["sharpe_annual"], 12), th))
        out["selected_theta"] = best
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, "x") as f:
        json.dump(out, f, sort_keys=True, indent=1)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    res = run(a[0], a[1], a[2], a[3] if len(a) > 3 else None)
    print(json.dumps({"stage": res["stage"], "written": a[2]}))

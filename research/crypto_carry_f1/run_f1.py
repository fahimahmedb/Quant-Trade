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


HEADERS = {
    "funding": "calc_time,funding_interval_hours,last_funding_rate",
    "kline": "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore",
}
NCOLS = {"funding": 3, "kline": 12}


def norm_ts(token):
    """Normalise a timestamp token to milliseconds; fail closed otherwise."""
    v = int(token)
    if 10**12 <= v < 10**14:
        return v
    if 10**15 <= v < 10**17:
        return v // 1000
    raise FormatError(f"unrecognised timestamp magnitude: {len(token)} digits")


def iter_rows(zip_path, read_lo, read_hi, kind):
    """Yield split rows whose first-field timestamp lies in [read_lo, read_hi).

    `kind` is 'funding' or 'kline'. The header, if present, must equal the known one; every
    row must have exactly the expected number of columns (checked for in-window rows)."""
    n_fields = NCOLS[kind]
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
                        if line != HEADERS[kind]:
                            raise FormatError("unrecognised header")
                        continue
                if not head.isdigit():
                    raise FormatError("non-numeric timestamp field")
                ts = norm_ts(head)
                if ts < read_lo or ts >= read_hi:
                    continue
                row = next(csv.reader([line]))
                if len(row) != n_fields:
                    raise FormatError("unexpected column count")
                row[0] = str(ts)
                yield row


def file_month_ms(fn):
    """Start of the month named by `...-YYYY-MM.zip`, in ms."""
    import datetime as dt
    stem = fn[:-4]
    y, m = int(stem[-7:-3]), int(stem[-2:])
    return int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def sha256_file(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def finite_pos(x, allow_zero=False):
    v = float(x)
    if not math.isfinite(v) or v < 0 or (v == 0 and not allow_zero):
        raise FormatError("non-finite or non-positive value")
    return v


def load_symbol(data_dir, sym, read, allowed):
    """`allowed` maps absolute zip path -> expected sha256 (from the acquisition manifest)."""
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
            m0 = file_month_ms(fn)
            if m0 + 31 * DAY_MS <= lo or m0 >= hi:
                continue  # file outside the stage's read window: never opened
            if p not in allowed:
                raise FormatError(f"file not in manifest: {p}")
            if sha256_file(p) != allowed[p]:
                raise FormatError(f"checksum mismatch: {p}")
            if ds == "funding":
                for r in iter_rows(p, lo, hi, "funding"):
                    ts = int(r[0])
                    slot = int(round(ts / MIN_MS)) * MIN_MS
                    v = float(r[2])
                    if not math.isfinite(v):
                        raise FormatError("non-finite funding rate")
                    out["funding"][slot].append(v)
            else:
                tgt = out["spot" if ds == "spot1d" else "perp"]
                for r in iter_rows(p, lo, hi, "kline"):
                    day = int(r[0]) // DAY_MS
                    tgt[day] = {"high": finite_pos(r[2]), "close": finite_pos(r[4]), "qv": finite_pos(r[7], True)}
    return out


def read_manifest(data_dir, names):
    """Allowed files and their sha256 from one or more manifest_*.jsonl files in data_dir."""
    allowed = {}
    for n in names:
        with open(os.path.join(data_dir, n)) as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("ok"):
                    p = os.path.join(data_dir, rec["dataset"], rec["symbol"], rec["key"].rsplit("/", 1)[-1])
                    allowed[p] = rec["sha256"]
    return allowed


def require_manifest_files(allowed, read):
    """A successful capture in the read window cannot silently disappear.

    Check presence before loading any symbol. Out-of-window captures are not
    opened; load_symbol verifies the hashes of the files it parses.
    """
    lo, hi = read
    for path in sorted(allowed):
        m0 = file_month_ms(os.path.basename(path))
        if m0 + 31 * DAY_MS <= lo or m0 >= hi:
            continue
        if not os.path.isfile(path):
            raise FormatError(f"manifest file missing: {path}")


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
        self._elig, self._sig = {}, {}

    def eligible(self, d):
        if d not in self._elig:
            self._elig[d] = self._eligible(d)
        return self._elig[d]

    def signal(self, d):
        if d not in self._sig:
            self._sig[d] = self._signal(d)
        return self._sig[d]

    def _eligible(self, d):
        for k in range(MIN_HIST):
            if (d - k) not in self.spot or (d - k) not in self.perp:
                return False, None
        qv = [self.spot[d - k]["qv"] for k in range(30)]
        m = median(qv)
        # Eligibility is the preregistered median gate; low-slippage ranking uses
        # aggregate trailing-30-day quote volume, as separately preregistered.
        return m >= MIN_QV, sum(qv)

    def _signal(self, d):
        days = range(d - 6, d + 1)
        if any(x not in self.has_fund for x in days):
            return None
        return sum(self.sig[x] for x in days) / 7.0 * 365.0


def simulate(syms, theta, cost_mult, d_first, d_last):
    """Daily NAV simulation. Returns (daily returns, diagnostics)."""
    nav = 1.0
    pos = {}
    barred = {}
    rets, exposure_days, liqs, forced = [], 0, 0, 0
    parts = {"funding": 0.0, "basis": 0.0, "fees": 0.0, "liquidation_penalty": 0.0}

    def top20_on(dd):
        el = {}
        for k, sd in syms.items():
            ok, m = sd.eligible(dd)
            if ok:
                el[k] = m
        return set(sorted(el, key=lambda k: (-el[k], k))[:20])

    def exit_cost(p, s, dd, mult, sym):
        slip = SLIP_TOP if sym in top20_on(dd) else SLIP_REST   # R12: exit-day (dd) liquidity rank
        return mult * p["q"] * (s.spot[dd]["close"] * (FEE_SPOT + slip) + s.perp[dd]["close"] * (FEE_PERP + slip))

    for d in range(d_first, d_last + 1):
        nav_start = nav
        if pos:
            exposure_days += 1  # positions held through day d
        # 1. P&L of positions open at the start of day d
        for sym in sorted(pos):
            p, s = pos[sym], syms[sym]
            if d not in s.spot or d not in s.perp:
                # R12: bar gap/delisting while open -> forced exit at the last available close (day d-1)
                c = exit_cost(p, s, d - 1, cost_mult, sym)
                nav -= c
                parts["fees"] += c
                barred[sym] = d + BAR_DAYS
                p["dead"] = True
                forced += 1
                continue
            sp0, sp1 = s.spot[d - 1]["close"], s.spot[d]["close"]
            pp0, pp1 = s.perp[d - 1]["close"], s.perp[d]["close"]
            q = p["q"]
            if s.perp[d]["high"] >= LIQ_MULT * p["ref"]:
                liq_px = LIQ_MULT * p["ref"]
                pnl = q * (sp1 - sp0) - q * (liq_px - pp0)
                pen = LIQ_PEN * q * liq_px
                slip = SLIP_TOP if sym in top20_on(d) else SLIP_REST
                ec = cost_mult * q * sp1 * (FEE_SPOT + slip)
                nav += pnl - pen - ec
                parts["basis"] += pnl
                parts["liquidation_penalty"] += pen
                parts["fees"] += ec
                barred[sym] = d + BAR_DAYS
                p["dead"] = True
                liqs += 1
            else:
                fund = s.earn.get(d, 0.0) * q * pp1
                basis = q * (sp1 - sp0) - q * (pp1 - pp0)
                nav += basis + fund
                parts["basis"] += basis
                parts["funding"] += fund
        for sym in [k for k, v in pos.items() if v.get("dead")]:
            del pos[sym]
        # 2. decisions at the close of day d
        info = {}
        for sym, s in syms.items():
            ok, m = s.eligible(d)
            info[sym] = (ok, m, s.signal(d) if ok else None)
        elig = {k: v for k, v in info.items() if v[0]}
        ranked = sorted(elig, key=lambda k: (-elig[k][1], k))
        top20 = set(ranked[:20])
        for sym in sorted(pos):
            ok, m, sg = info[sym]
            if (not ok) or sg is None or sg < theta / 2.0:
                p, s = pos.pop(sym), syms[sym]
                slip = SLIP_TOP if sym in top20 else SLIP_REST
                c = cost_mult * p["q"] * (s.spot[d]["close"] * (FEE_SPOT + slip) + s.perp[d]["close"] * (FEE_PERP + slip))
                nav -= c
                parts["fees"] += c
        cands = [k for k in sorted(elig) if k not in pos and barred.get(k, -1) < d
                 and elig[k][2] is not None and elig[k][2] >= theta]
        if cands and d < d_last and nav > 0:
            nav0 = nav
            deployed = sum(p["cap"] for p in pos.values())
            avail = max(0.0, nav0 - deployed)
            k_after = len(pos) + len(cands)
            w = min(CAP_W, 1.0 / k_after, avail / nav0 / len(cands))
            if w > 0:
                for sym in cands:
                    s = syms[sym]
                    cap = w * nav0
                    notional = cap * 0.75
                    sp, pp = s.spot[d]["close"], s.perp[d]["close"]
                    q = notional / sp
                    slip = SLIP_TOP if sym in top20 else SLIP_REST
                    c = cost_mult * q * (sp * (FEE_SPOT + slip) + pp * (FEE_PERP + slip))
                    nav -= c
                    parts["fees"] += c
                    pos[sym] = {"q": q, "ref": pp, "cap": cap, "slip": slip}
        if d == d_last:
            for sym in sorted(pos):
                p, s = pos.pop(sym), syms[sym]
                slip = SLIP_TOP if sym in top20 else SLIP_REST
                c = cost_mult * p["q"] * (s.spot[d]["close"] * (FEE_SPOT + slip) + s.perp[d]["close"] * (FEE_PERP + slip))
                nav -= c
                parts["fees"] += c
        rets.append(nav / nav_start - 1.0)
    return rets, {"exposure_days": exposure_days, "liquidations": liqs, "forced_exits": forced,
                  "components": parts, "final_nav": nav}


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


def max_drawdown(rets):
    nav, peak, mdd = 1.0, 1.0, 0.0
    for r in rets:
        nav *= 1.0 + r
        peak = max(peak, nav)
        mdd = max(mdd, 1.0 - nav / peak)
    return mdd


def extra_reports(rets, d_first):
    import datetime as dt
    by_year = defaultdict(float)
    nav = 1.0
    yr_start = {}
    for i, r in enumerate(rets):
        y = dt.datetime.fromtimestamp((d_first + i) * 86400, dt.timezone.utc).year
        yr_start.setdefault(y, nav)
        nav *= 1.0 + r
        by_year[y] = nav / yr_start[y] - 1.0
    pos_sum = sum(r for r in rets if r > 0)
    top10 = sum(sorted((r for r in rets if r > 0), reverse=True)[:10])
    return {"by_year_return": dict(sorted(by_year.items())), "max_drawdown": max_drawdown(rets),
            "top10_day_share_of_positive_pnl": (top10 / pos_sum if pos_sum > 0 else None)}


def snapshot(data_dir):
    snap = []
    for root, _, files in os.walk(data_dir):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            st = os.stat(p)
            # ctime catches an in-place rewrite even if size and mtime are
            # restored; device/inode identity also catches file replacement.
            # Reading metadata leaves sealed ZIP contents untouched.
            snap.append((p, st.st_dev, st.st_ino, st.st_size,
                         st.st_mtime_ns, st.st_ctime_ns))
    return sorted(snap)


def select_theta(cells):
    """Stage A selection rule: highest base Sharpe, ties -> larger theta."""
    return max(THETAS, key=lambda th: (round(cells[str(th)]["base"]["sharpe_annual"], 12), th))


def run(stage, data_dir, result_path, stage_a_result=None, manifest_names=None, stage_a_sha256=None):
    cfg = STAGES[stage]
    me = sha256_file(os.path.abspath(__file__))
    snap0 = snapshot(data_dir)
    selected = None
    if stage == "STAGE_B":
        # Authenticate the published Stage A result before any Stage B byte is read.
        import hashlib
        if not stage_a_sha256 or not stage_a_result:
            raise FormatError("Stage A result missing or does not match the published sha256")
        with open(stage_a_result, "rb") as f:
            stage_a_bytes = f.read()
        if hashlib.sha256(stage_a_bytes).hexdigest() != stage_a_sha256:
            raise FormatError("Stage A result missing or does not match the published sha256")
        # Parse the authenticated buffer, never a second read of a mutable path.
        sa = json.loads(stage_a_bytes)
        if sa.get("stage") != "STAGE_A" or sa.get("harness_sha256") != me:
            raise FormatError("Stage A result produced by a different harness")
        selected = select_theta(sa["cells"])
        if sa.get("selected_theta") != selected:
            raise FormatError("Stage A selected_theta inconsistent with its cells")
    names = manifest_names or [f"manifest_{stage}.jsonl"]
    allowed = read_manifest(data_dir, names)
    require_manifest_files(allowed, cfg["read"])
    syms_list = sorted(os.listdir(os.path.join(data_dir, "funding")))
    syms = {}
    for sym in syms_list:
        raw = load_symbol(data_dir, sym, cfg["read"], allowed)
        sd = SymData(sym, raw)
        if sd.spot and sd.perp and sd.sig:
            syms[sym] = sd
    d_first, d_last = cfg["stat"][0] // DAY_MS, (cfg["stat"][1] - 1) // DAY_MS
    cells = {}
    for th in THETAS:
        base_r, base_d = simulate(syms, th, 1.0, d_first, d_last)
        stress_r, stress_d = simulate(syms, th, 2.0, d_first, d_last)
        b = stats_for(base_r, d_first, quarter_of)
        s = stats_for(stress_r, d_first, quarter_of)
        share = base_d["exposure_days"] / len(base_r)
        b["exposure_days_share"] = share
        status = classify(b, s, b["quarters"], share)
        if stage == "STAGE_B" and th != selected:
            status = "REPORTED_NOT_ELIGIBLE"
        cells[str(th)] = {"base": b, "stress": s, "diag_base": base_d, "diag_stress": stress_d,
                          "reports": extra_reports(base_r, d_first), "status": status,
                          "daily_returns_base": base_r, "daily_returns_stress": stress_r,
                          "excess_over_cash_annualised_base": b["excess_over_cash_daily"] * 365.0}
    out = {"stage": stage, "harness_sha256": me, "n_symbols": len(syms), "cells": cells}
    if stage == "STAGE_A":
        out["selected_theta"] = select_theta(cells)
    else:
        out["selected_theta"] = selected
    # late-mutation invalidation: harness source and data directory must be unchanged
    if sha256_file(os.path.abspath(__file__)) != me or snapshot(data_dir) != snap0:
        raise FormatError("harness or data changed during the run; result not persisted")
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    tmp = result_path + ".tmp"
    with open(tmp, "x") as f:
        json.dump(out, f, sort_keys=True, indent=1)
    try:
        os.link(tmp, result_path)  # fails if the result already exists
    finally:
        os.remove(tmp)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    res = run(a[0], a[1], a[2], a[3] if len(a) > 3 else None, None, a[4] if len(a) > 4 else None)
    print(json.dumps({"stage": res["stage"], "written": a[2]}))

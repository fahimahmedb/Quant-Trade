"""Step 4c: weather determination from the METAR archive (Iowa Environmental Mesonet ASOS/METAR, public).

Markets: "Will the highest|lowest temperature in <city> be <N>°C [or higher|or below] on <Month> <d>?" and
"... between <a>-<b>°F ...". Station = ICAO in the market's resolution URL (NOAA timeseries site= or WU path).
Rule (protocol §3): T_DET = valid time of the first METAR of the next local day (station tz from IEM metadata);
the day's extreme from METAR temps; °C markets use whole-degree METAR values (the source's stated precision);
°F markets verified only if the METAR extreme is >= 1.0 °F from every bracket edge. HKO / no-URL → UNVERIFIABLE.
An extreme reached by an observation at exactly local midnight → UNVERIFIABLE (day attribution ambiguous).

Usage: python3 s04c_weather.py markets_primary 2026-08-27 2026-10-01
Outputs: data/weather_determination_<tag>.csv.gz ; caches data/raw/wx/
"""
import csv
import datetime as dt
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.request
from zoneinfo import ZoneInfo

from common import DATA, RAW, get
from s02_classify import classify, load

CACHE = os.path.join(RAW, "wx")
os.makedirs(CACHE, exist_ok=True)
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                        "September", "October", "November", "December"], 1)}
QRE = re.compile(r"Will the (highest|lowest) temperature in (.+?) (?:be |between )(-?\d+)(?:-(-?\d+))?°([CF])"
                 r"( or higher| or below)? on (\w+) (\d+)\?")


def iem_id(icao):
    return icao[1:] if icao.startswith("K") and len(icao) == 4 else icao


def station_meta(icao):
    fn = os.path.join(CACHE, f"meta_{icao}.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    d = get(f"https://mesonet.agron.iastate.edu/api/1/station/{iem_id(icao)}.json")
    rec = d["data"][0] if d.get("data") else None
    json.dump(rec, open(fn, "w"))
    return rec


def metars(icao, d0, d1):
    fn = os.path.join(CACHE, f"obs_{icao}_{d0}_{d1}.csv")
    if not os.path.exists(fn):
        a, b = dt.date.fromisoformat(d0), dt.date.fromisoformat(d1)
        url = ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=" + iem_id(icao) +
               f"&data=tmpf&data=tmpc&year1={a.year}&month1={a.month}&day1={a.day}&year2={b.year}&month2={b.month}"
               f"&day2={b.day}&tz=Etc/UTC&format=onlycomma&latlon=no&missing=M&report_type=3&report_type=4")
        for i in range(12):
            try:
                txt = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
                                             timeout=120).read().decode()
                if txt.startswith("station"):
                    break
            except Exception:
                txt = ""
            time.sleep(5 + 5 * i)
        if not txt.startswith("station"):
            raise RuntimeError("IEM failed " + icao)
        open(fn, "w").write(txt)
    rows = []
    for r in csv.DictReader(io.StringIO(open(fn).read())):
        if r["tmpf"] in ("M", "") and r["tmpc"] in ("M", ""):
            continue
        t = dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
        tf = float(r["tmpf"]) if r["tmpf"] not in ("M", "") else None
        tc = float(r["tmpc"]) if r["tmpc"] not in ("M", "") else None
        rows.append((t, tf, tc))
    rows.sort()
    return rows


def main():
    name, d0, d1 = sys.argv[1], sys.argv[2], sys.argv[3]
    tag = name.replace("markets_", "")
    ms = [m for m in load(name) if not classify(m)[0] and classify(m)[1] == "wx"]
    out_rows = []
    parsed = []
    for m in ms:
        desc = m.get("description") or ""
        q = m.get("question") or ""
        s = re.search(r"timeseries\?site=([A-Za-z0-9]+)", desc) or re.search(
            r"wunderground\.com/history/daily/\S*?/([A-Z0-9]{4})\b", desc)
        mq = QRE.search(q)
        base = {"id": m["id"], "conditionId": m["conditionId"], "question": q[:120]}
        if "weather.gov.hk" in desc:
            out_rows.append({**base, "status": "UNVERIFIABLE_HKO"})
            continue
        if not s or not mq:
            out_rows.append({**base, "status": "UNVERIFIABLE_UNPARSED"})
            continue
        kind, city, a, b, unit, tail, mon, day = mq.groups()
        if mon not in MONTHS:
            out_rows.append({**base, "status": "UNVERIFIABLE_UNPARSED"})
            continue
        parsed.append((m, base, s.group(1).upper(), kind, int(a), int(b) if b else None, unit, (tail or "").strip(),
                       dt.date(2026, MONTHS[mon], int(day)), "wunderground" in desc and "timeseries" not in desc))
    stations = sorted({p[2] for p in parsed})
    print("weather markets", len(ms), "parsed", len(parsed), "stations", len(stations), flush=True)
    obs = {}
    tzs = {}
    for icao in stations:
        try:
            meta = station_meta(icao)
            tzs[icao] = ZoneInfo(meta["tzname"])
            obs[icao] = metars(icao, d0, d1)
        except Exception as ex:
            print("station fail", icao, ex, flush=True)
    for (m, base, icao, kind, a, b, unit, tail, day, is_wu) in parsed:
        if icao not in obs or not obs[icao]:
            out_rows.append({**base, "station": icao, "status": "UNVERIFIABLE_NO_METAR"})
            continue
        tz = tzs[icao]
        dayobs = [(t, tf, tc) for t, tf, tc in obs[icao] if t.astimezone(tz).date() == day]
        nxt = [t for t, _, _ in obs[icao] if t.astimezone(tz).date() > day]
        if len(dayobs) < 12 or not nxt:
            out_rows.append({**base, "station": icao, "status": "UNVERIFIABLE_SPARSE_METAR"})
            continue
        t_det = nxt[0].timestamp()
        vals = [(tc if unit == "C" else tf, t) for t, tf, tc in dayobs if (tc if unit == "C" else tf) is not None]
        ext_v, ext_t = (max if kind == "highest" else min)(vals, key=lambda x: x[0])
        ext_t_local = ext_t.astimezone(tz)
        rec = {**base, "station": icao, "tz": str(tz), "day": day.isoformat(), "kind": kind, "unit": unit,
               "a": a, "b": b, "tail": tail, "extreme": ext_v, "n_obs": len(dayobs), "t_det": t_det,
               "source": "WU" if is_wu else "NOAA"}
        if ext_t_local.hour == 0 and ext_t_local.minute == 0:
            out_rows.append({**rec, "status": "UNVERIFIABLE_MIDNIGHT_EXTREME"})
            continue
        if unit == "C":
            v = round(ext_v)  # METAR whole degrees C
            lo, hi = (a, b if b is not None else a)
            if tail == "or higher":
                yes = v >= a
            elif tail == "or below":
                yes = v <= a
            else:
                yes = lo <= v <= hi
            out_rows.append({**rec, "status": "VERIFIED", "det_yes": int(yes)})
        else:
            lo, hi = (a, b if b is not None else a)
            if tail == "or higher":
                edges = [a - 0.5]
                yes = ext_v >= a - 0.5
            elif tail == "or below":
                edges = [a + 0.5]
                yes = ext_v < a + 0.5
            else:
                edges = [lo - 0.5, hi + 0.5]
                yes = lo - 0.5 <= ext_v < hi + 0.5
            if min(abs(ext_v - e) for e in edges) < 1.0:
                out_rows.append({**rec, "status": "UNVERIFIABLE_F_ROUNDING"})
            else:
                out_rows.append({**rec, "status": "VERIFIED", "det_yes": int(yes)})
    cols = ["id", "conditionId", "question", "station", "tz", "day", "kind", "unit", "a", "b", "tail", "extreme",
            "n_obs", "t_det", "source", "status", "det_yes"]
    out = os.path.join(DATA, f"weather_determination_{tag}.csv.gz")
    with gzip.open(out, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
    import collections
    print("wrote", out, len(out_rows), collections.Counter(r["status"] for r in out_rows))


if __name__ == "__main__":
    main()

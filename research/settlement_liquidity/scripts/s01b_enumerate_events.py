"""Step 1b (secondary replication only): event-based enumeration when gamma /markets/keyset is unstable.

Pages gamma /events?closed=true (offset pagination) for three predeclared families over a UTC window and flattens
their markets into the S1 record format; keeps markets with volumeNum >= MIN_VOLUME and closedTime in the window.
  - MLB      : series_slug=mlb, start_time in [D0-1d, D1]
  - soccer   : tag_slug=soccer, start_time in [D0-1d, D1]
  - weather  : tag_slug=weather, end_date in [D0-1d, D1+1d] (temperature questions only are kept later by S2)
Not a census of all categories (the primary window is the census); used only to replicate S2 economics.
Usage: python3 s01b_enumerate_events.py 2026-07-31 2026-08-30 markets_secondary
"""
import datetime as dt
import os
import sys

from common import MIN_VOLUME, RAW, get, parse_ts, write_jsonl_gz
from s01_enumerate_markets import EV_KEEP, KEEP


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    d0 = dt.datetime.fromisoformat(sys.argv[1]).replace(tzinfo=dt.timezone.utc)
    d1 = dt.datetime.fromisoformat(sys.argv[2]).replace(tzinfo=dt.timezone.utc)
    name = sys.argv[3]
    lo, hi = d0 - dt.timedelta(days=1), d1 + dt.timedelta(days=1)
    queries = [f"series_slug=mlb&start_time_min={iso(lo)}&start_time_max={iso(d1)}",
               f"tag_slug=soccer&start_time_min={iso(lo)}&start_time_max={iso(d1)}",
               f"tag_slug=weather&end_date_min={iso(lo)}&end_date_max={iso(hi)}"]
    rows, seen = [], set()
    for q in queries:
        # split into daily slices so each stays under the 10,000 offset cap
        day = lo
        while day < hi:
            nxt = day + dt.timedelta(days=1)
            qq = q
            for a, b in (("start_time_min", "start_time_max"), ("end_date_min", "end_date_max")):
                if a in qq:
                    qq = qq.split("&" + a)[0] + f"&{a}={iso(day)}&{b}={iso(nxt)}"
            for off in range(0, 10000, 100):
                d = None
                for attempt in range(20):
                    try:
                        d = get(f"https://gamma-api.polymarket.com/events?closed=true&limit=100&offset={off}&{qq}")
                        break
                    except Exception:
                        import time
                        time.sleep(20)
                if not d:
                    break
                for e in d:
                    for m in e.get("markets", []) or []:
                        ct = parse_ts(m.get("closedTime"))
                        if ct is None or not (d0.timestamp() <= ct < d1.timestamp()):
                            continue
                        if float(m.get("volumeNum") or 0) < MIN_VOLUME or m["id"] in seen:
                            continue
                        seen.add(m["id"])
                        r = {k: m.get(k) for k in KEEP}
                        r["description"] = (m.get("description") or "")[:4000]
                        r["event"] = {k: e.get(k) for k in EV_KEEP}
                        rows.append(r)
                if len(d) < 100:
                    break
            day = nxt
        print(q.split("&")[0], "cumulative markets", len(rows), flush=True)
    out = os.path.join(RAW, name + ".jsonl.gz")
    write_jsonl_gz(out, rows)
    print("markets", len(rows), "->", out)


if __name__ == "__main__":
    main()

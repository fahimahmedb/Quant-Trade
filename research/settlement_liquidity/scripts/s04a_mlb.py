"""Step 4a: MLB authoritative game timeline from statsapi.mlb.com (public, official MLB data).

For every MLB game on dates [D0-1, D1] extracts, from the official live feed:
  start, status, final score, per-half-inning end wall-clock times, first-inning scoring time,
  t_final = endTime of the last play (game-over transition).
Cached per game in data/raw/mlb/<gamePk>.json (resumable). Output: data/mlb_games.csv.gz

Usage: python3 s04a_mlb.py 2026-08-29 2026-09-28
"""
import concurrent.futures as cf
import csv
import datetime as dt
import gzip
import json
import os
import sys

from common import DATA, RAW, get, parse_ts

CACHE = os.path.join(RAW, "mlb")
os.makedirs(CACHE, exist_ok=True)


def extract(pk):
    path = os.path.join(CACHE, f"{pk}.json")
    if os.path.exists(path):
        return json.load(open(path))
    d = get(f"https://statsapi.mlb.com/api/v1.1/game/{pk}/feed/live")
    gd = d["gameData"]
    ld = d["liveData"]
    plays = ld["plays"]["allPlays"]
    half_end = {}
    first_inn_run = None
    runs_by_half = {}
    for p in plays:
        a = p["about"]
        key = f"{a['inning']}{'T' if a['isTopInning'] else 'B'}"
        et = parse_ts(a.get("endTime"))
        if et is not None:
            half_end[key] = max(half_end.get(key, 0), et)
        r = sum(1 for x in p.get("runners", []) if (x.get("movement") or {}).get("end") == "score")
        if r:
            runs_by_half[key] = runs_by_half.get(key, 0) + r
            if a["inning"] == 1 and et is not None:
                first_inn_run = et if first_inn_run is None else min(first_inn_run, et)
    ls = ld.get("linescore", {})
    rec = {
        "gamePk": pk,
        "officialDate": gd["datetime"].get("officialDate"),
        "start": gd["datetime"].get("dateTime"),
        "status": gd["status"].get("detailedState"),
        "coded": gd["status"].get("codedGameState"),
        "away": gd["teams"]["away"]["name"], "home": gd["teams"]["home"]["name"],
        "away_abbr": gd["teams"]["away"].get("abbreviation"), "home_abbr": gd["teams"]["home"].get("abbreviation"),
        "away_runs": ls.get("teams", {}).get("away", {}).get("runs"),
        "home_runs": ls.get("teams", {}).get("home", {}).get("runs"),
        "innings": [{"n": i.get("num"), "a": (i.get("away") or {}).get("runs"), "h": (i.get("home") or {}).get("runs")}
                    for i in ls.get("innings", [])],
        "half_end": half_end,
        "first_inning_run_t": first_inn_run,
        "t_final": parse_ts(plays[-1]["about"].get("endTime")) if plays else None,
        "n_plays": len(plays),
        "feed_ts": (d.get("metaData") or {}).get("timeStamp"),
        "game_events": (d.get("metaData") or {}).get("gameEvents"),
    }
    json.dump(rec, open(path, "w"))
    return rec


def main():
    d0 = dt.date.fromisoformat(sys.argv[1])
    d1 = dt.date.fromisoformat(sys.argv[2])
    pks = []
    day = d0
    while day <= d1:
        s = get(f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={day.isoformat()}")
        for dd in s.get("dates", []):
            for g in dd["games"]:
                pks.append(g["gamePk"])
        day += dt.timedelta(days=1)
    pks = sorted(set(pks))
    print("games", len(pks), flush=True)
    with cf.ThreadPoolExecutor(8) as ex:
        recs = list(ex.map(extract, pks))
    out = os.path.join(DATA, "mlb_games.csv.gz")
    cols = ["gamePk", "officialDate", "start", "status", "coded", "away", "home", "away_abbr", "home_abbr",
            "away_runs", "home_runs", "t_final", "first_inning_run_t", "n_plays", "innings", "half_end"]
    with gzip.open(out, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in recs:
            row = {k: r.get(k) for k in cols}
            row["innings"] = json.dumps(r["innings"], separators=(",", ":"))
            row["half_end"] = json.dumps(r["half_end"], separators=(",", ":"))
            w.writerow(row)
    print("wrote", out, len(recs))


if __name__ == "__main__":
    main()

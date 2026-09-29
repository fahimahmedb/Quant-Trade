"""Step 4d: assemble per-market T_DETERMINED, T_RESOLUTION and source-derived determined side.

Inputs: S1 markets file, data/mlb_games.csv.gz, data/espn_events_<tag>.csv.gz + pm_espn_map, weather file.
Output: data/determination_<tag>.csv.gz with one row per non-excluded market:
  status VERIFIED | UNVERIFIABLE_<reason> ; t_det ; t_res ; window_s ; det_side (outcome index or '') ;
  det_side_method (source | '' ) ; venue_finished (Polymarket finishedTimestamp, cross-check only).
Outcome-blind with respect to Polymarket: det_side comes only from the external source.

Usage: python3 s04d_assemble.py markets_primary
"""
import collections
import csv
import gzip
import json
import os
import re
import sys

from common import DATA, parse_ts
from s02_classify import classify, load
from s04b_espn import sim

FIRST_HALF = re.compile(r"first_half|halftime|1h_|_1h|first-half")
Q1 = re.compile(r"(^|_)q1(_|$)|first_quarter")
F5 = re.compile(r"first_five|first5|f5")
REG_ONLY = re.compile(r"90 minutes|regular time|regulation", re.I)


def rcsv(p):
    return list(csv.DictReader(gzip.open(p, "rt")))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def team_side(outcomes, home, away):
    """Map teams to outcome indices; DEVIATION D2: mapping must be unique and one-to-one, else {}."""
    if len(outcomes) != 2:
        return {}
    s = [[sim([nm], o) for o in outcomes] for nm in (home, away)]
    # home->0/away->1 or home->1/away->0 must be the only assignment with both sims >= 0.99
    a = s[0][0] >= 0.99 and s[1][1] >= 0.99
    b = s[0][1] >= 0.99 and s[1][0] >= 0.99
    if a == b:
        return {}
    if a and (s[0][1] >= 0.99 or s[1][0] >= 0.99):
        return {}
    if b and (s[0][0] >= 0.99 or s[1][1] >= 0.99):
        return {}
    return {"home": 0, "away": 1} if a else {"home": 1, "away": 0}


def source_side(m, sc_home, sc_away, h1_home=None, h1_away=None):
    """Source-derived winning outcome index for simple game markets; None if not computable."""
    smt = (m.get("sportsMarketType") or "").lower()
    outs = json.loads(m["outcomes"])
    q = m.get("question") or ""
    line = fnum(m.get("line"))
    home, away = m["_home"], m["_away"]
    if FIRST_HALF.search(smt):
        if h1_home is None:
            return None
        sc_home, sc_away = h1_home, h1_away
    if smt in ("moneyline", "first_half_moneyline", "soccer_halftime_result", "child_moneyline"):
        if outs == ["Yes", "No"]:
            # soccer 3-way binary: "Will X win ...?" / "... end in a draw?"
            if re.search(r"draw", q, re.I):
                return 0 if sc_home == sc_away else 1
            # DEVIATION D2: the named team must match uniquely (other team's similarity <= 0.5)
            if sim([home], q) >= 0.99 and sim([away], q) <= 0.5:
                return 0 if sc_home > sc_away else 1
            if sim([away], q) >= 0.99 and sim([home], q) <= 0.5:
                return 0 if sc_away > sc_home else 1
            return None
        ts = team_side(outs, home, away)
        if len(ts) != 2 or sc_home == sc_away:
            return None
        return ts["home"] if sc_home > sc_away else ts["away"]
    if smt in ("totals", "first_half_totals") and line is not None:
        tot = sc_home + sc_away
        if tot == line:
            return None
        lo = [i for i, o in enumerate(outs) if o.lower().startswith("over")]
        un = [i for i, o in enumerate(outs) if o.lower().startswith("under")]
        if not lo or not un:
            return None
        return lo[0] if tot > line else un[0]
    if smt in ("spreads", "first_half_spreads") and line is not None:
        # question "Spread: Team (-1.5)": outcome[0] is the team carrying the line
        ts = team_side(outs, home, away)
        if len(ts) != 2:
            return None
        fav = 0
        fav_is_home = ts["home"] == fav
        margin = (sc_home - sc_away) if fav_is_home else (sc_away - sc_home)
        adj = margin + line
        if adj == 0:
            return None
        return fav if adj > 0 else 1 - fav
    if smt == "both_teams_to_score" and outs == ["Yes", "No"]:
        return 0 if (sc_home > 0 and sc_away > 0) else 1
    return None


def main():
    name = sys.argv[1]
    tag = name.replace("markets_", "")
    ms = load(name)
    mlb = rcsv(os.path.join(DATA, "mlb_games.csv.gz"))
    for g in mlb:
        g["_start"] = parse_ts(g["start"])
        g["_half"] = json.loads(g["half_end"])
    esp = {r["espn_id"]: r for r in rcsv(os.path.join(DATA, f"espn_events_{tag}.csv.gz"))}
    emap = {r["pm_event"]: r["espn_id"] for r in rcsv(os.path.join(DATA, f"pm_espn_map_{tag}.csv.gz"))}
    wxp = os.path.join(DATA, f"weather_determination_{tag}.csv.gz")
    wx = {r["id"]: r for r in rcsv(wxp)} if os.path.exists(wxp) else {}
    rows = []
    for m in ms:
        excl, fam = classify(m)
        if excl:
            continue
        ev = m.get("event") or {}
        smt = (m.get("sportsMarketType") or "").lower()
        slug = (ev.get("slug") or "").lower()
        t_res = parse_ts(m.get("closedTime"))
        r = {"id": m["id"], "conditionId": m["conditionId"], "family": fam, "smt": smt, "t_res": t_res,
             "t_det": None, "status": "", "method": "", "det_side": "", "src": "",
             "venue_finished": parse_ts(ev.get("finishedTimestamp")), "disputes": 0}
        try:
            r["disputes"] = sum(1 for s in json.loads(m.get("umaResolutionStatuses") or "[]") if s == "disputed")
        except Exception:
            pass
        if fam == "mlb":
            st = parse_ts(m.get("gameStartTime") or ev.get("startTime"))
            title = ev.get("title") or m.get("question") or ""
            parts = re.split(r"\s+vs\.?\s+", title, maxsplit=1)
            best = None
            if st is not None and len(parts) == 2:
                for g in mlb:
                    if g["_start"] is None or abs(g["_start"] - st) > 1200:
                        continue
                    s = max(sim([g["away"]], parts[0]) + sim([g["home"]], parts[1]),
                            sim([g["home"]], parts[0]) + sim([g["away"]], parts[1]))
                    # DEVIATION D1: tie-break equal team scores by closest scheduled start (doubleheaders)
                    key = (s, -abs(g["_start"] - st))
                    if s >= 1.5 and (best is None or key > best[0]):
                        best = (key, g)
            if not best:
                r["status"] = "UNVERIFIABLE_MLB_UNMATCHED"
            else:
                g = best[1]
                r["src"] = "mlb:" + g["gamePk"]
                if g["status"] != "Final":
                    r["status"] = "UNVERIFIABLE_MLB_NOT_FINAL"
                else:
                    he = g["_half"]
                    inn = re.search(r"inning-(\d+)", slug)
                    if smt == "nrfi":
                        cands = [x for x in (fnum(g["first_inning_run_t"]), he.get("1B")) if x]
                        r["t_det"], r["method"] = (min(cands) if cands else None), "mlb_nrfi"
                    elif F5.search(smt):
                        r["t_det"], r["method"] = (max(x for x in (he.get("5T"), he.get("5B")) if x) if he.get("5T") else None), "mlb_f5"
                    elif inn:
                        n = inn.group(1)
                        r["t_det"], r["method"] = (he.get(n + "B") or he.get(n + "T")), "mlb_inning"
                    else:
                        r["t_det"], r["method"] = fnum(g["t_final"]), "mlb_final"
                    r["status"] = "VERIFIED" if r["t_det"] else "UNVERIFIABLE_MLB_NO_TIME"
                    if r["method"] == "mlb_final":
                        m["_home"], m["_away"] = g["home"], g["away"]
                        try:
                            side = source_side(m, int(g["home_runs"]), int(g["away_runs"]))
                        except Exception:
                            side = None
                        if side is not None:
                            r["det_side"], r["det_side_method"] = side, "source"
        elif fam.startswith("espn:") or fam.startswith("sports_other:"):
            eid = emap.get(ev.get("id"))
            if not eid or eid not in esp:
                r["status"] = "UNVERIFIABLE_NO_INDEPENDENT_SOURCE"
            else:
                e = esp[eid]
                r["src"] = "espn:" + eid
                if FIRST_HALF.search(smt):
                    t, meth = fnum(e["t_half"]), "espn_half"
                elif Q1.search(smt):
                    t, meth = fnum(e["t_q1"]), "espn_q1"
                else:
                    t, meth = fnum(e["t_final"]), "espn_" + (e["method"] or "none")
                    tall = fnum(e.get("t_end_all"))
                    if e["path"].startswith("soccer") and tall and t and tall > t + 600 and not REG_ONLY.search(m.get("description") or ""):
                        t, meth = tall, "espn_soccer_after_extra_time"
                if not t:
                    r["status"] = "UNVERIFIABLE_ESPN_NO_TERMINAL_TIMESTAMP"
                elif e["completed"] not in ("True", "true", "1"):
                    r["status"] = "UNVERIFIABLE_ESPN_NOT_COMPLETED"
                else:
                    r["t_det"], r["method"], r["status"] = t, meth, "VERIFIED"
                    m["_home"], m["_away"] = e["home"], e["away"]
                    try:
                        hl, al = json.loads(e["home_lines"] or "[]"), json.loads(e["away_lines"] or "[]")
                        h1h = int(hl[0]) + (int(hl[1]) if e["path"].startswith("football") or e["path"].startswith("basketball") else 0) if hl else None
                        h1a = int(al[0]) + (int(al[1]) if e["path"].startswith("football") or e["path"].startswith("basketball") else 0) if al else None
                        side = source_side(m, int(float(e["home_score"])), int(float(e["away_score"])), h1h, h1a)
                    except Exception:
                        side = None
                    if side is not None and meth != "espn_q1":
                        r["det_side"], r["det_side_method"] = side, "source"
        elif fam == "wx":
            w = wx.get(m["id"])
            if not w:
                r["status"] = "UNVERIFIABLE_WX_UNPARSED"
            elif w["status"] != "VERIFIED":
                r["status"] = w["status"]
            else:
                r["t_det"], r["method"], r["status"], r["src"] = float(w["t_det"]), "metar_next_day_first_obs", "VERIFIED", "metar:" + w["station"]
                outs = json.loads(m["outcomes"])
                if outs == ["Yes", "No"]:
                    r["det_side"], r["det_side_method"] = (0 if w["det_yes"] == "1" else 1), "source"
        else:
            r["status"] = "UNVERIFIABLE_" + ("SPORTS_NO_INDEPENDENT_SOURCE" if fam.startswith("sports_other") else "CATEGORY")
        if r["t_det"] and t_res:
            r["window_s"] = t_res - r["t_det"]
        rows.append(r)
    cols = ["id", "conditionId", "family", "smt", "status", "method", "src", "t_det", "t_res", "window_s",
            "det_side", "det_side_method", "venue_finished", "disputes"]
    out = os.path.join(DATA, f"determination_{tag}.csv.gz")
    with gzip.open(out, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    c = collections.Counter(r["status"] for r in rows)
    print("wrote", out, len(rows))
    for k, v in c.most_common():
        print(f"  {k:45s} {v}")
    ver = [r for r in rows if r["status"] == "VERIFIED"]
    print("verified with window>0:", sum(1 for r in ver if (r.get("window_s") or 0) > 0),
          "det_side from source:", sum(1 for r in ver if r["det_side"] != ""))


if __name__ == "__main__":
    main()

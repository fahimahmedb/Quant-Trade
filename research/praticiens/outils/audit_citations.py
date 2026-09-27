#!/usr/bin/env python3
"""Check every recorded quote of ../sources.jsonl against the raw text of its source.

Usage:  python audit_citations.py [--ids A-01,L-11] [--write]

For each source: raw text via fxtwitter (x.com links), the HN Algolia API
(news.ycombinator.com links) or fetch_text.py; the quote and the text are
normalised and the share of the quote's 6-word shingles found in the text is
scored. FOUND >= 0.8, PARTIAL >= 0.3, NOT_FOUND < 0.3, UNOPENABLE when the page
cannot be re-downloaded (it may still have been read through WebFetch). Dated
API answers (method curl-api) are skipped. --write refreshes
../audit_citations.json (the manual notes of the report's §6 are kept).
"""
import argparse
import collections
import html
import json
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(HERE, "..", "sources.jsonl")
OUT = os.path.join(HERE, "..", "audit_citations.json")
TWEET = re.compile(r"(?:x|twitter)\.com/([^/]+)/status/(\d+)")
HN = re.compile(r"news\.ycombinator\.com/item\?id=(\d+)")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"-\s*\n\s*", "", s.lower())
    s = re.sub(r"[^0-9a-zà-ÿ$%]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def curl(url: str) -> str:
    return subprocess.run(["curl", "-sS", "--max-time", "30", url],
                          capture_output=True, text=True).stdout


def raw_text(url: str) -> str | None:
    m = HN.search(url)
    if m:
        body = curl(f"https://hn.algolia.com/api/v1/items/{m.group(1)}")
        return html.unescape(re.sub(r"<[^>]+>", " ", body)) or None
    m = TWEET.search(url)
    if m:
        try:
            tw = json.loads(curl(f"https://api.fxtwitter.com/{m.group(1)}/status/{m.group(2)}")).get("tweet") or {}
        except json.JSONDecodeError:
            return None
        return (tw.get("text") or "") or None
    out = subprocess.run([sys.executable, os.path.join(HERE, "fetch_text.py"), url, "--head", "0"],
                         capture_output=True, text=True)
    m = re.search(r"CACHE: (\S+)", out.stdout)
    return open(m.group(1), encoding="utf-8").read() if out.returncode == 0 and m else None


def score(quote: str, text: str) -> float:
    q, t = norm(quote), norm(text)
    if not q:
        return 0.0
    if q in t:
        return 1.0
    words = q.split()
    if len(words) < 6:
        return 0.0
    shingles = [" ".join(words[i:i + 6]) for i in range(len(words) - 5)]
    return sum(s in t for s in shingles) / len(shingles)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    wanted = {i.strip() for i in args.ids.split(",") if i.strip()}
    manual = {}
    if os.path.exists(OUT):
        manual = {r["id"]: r["manuel"] for r in json.load(open(OUT))["resultats"] if r.get("manuel")}
    results = []
    for line in open(SOURCES, encoding="utf-8"):
        src = json.loads(line)
        if wanted and src["id"] not in wanted:
            continue
        row = {"lane": src.get("couloir"), "id": src["id"], "url": src["url"], "methode": src.get("methode")}
        if src.get("methode") == "curl-api":
            row["status"] = "API(skip)"
        else:
            text = raw_text(src["url"])
            if text is None:
                row["status"] = "UNOPENABLE"
            else:
                sc = score(src.get("citation", ""), text)
                row.update(status="FOUND" if sc >= 0.8 else "PARTIAL" if sc >= 0.3 else "NOT_FOUND",
                           score=round(sc, 2))
        if src["id"] in manual:
            row["manuel"] = manual[src["id"]]
        results.append(row)
        print(row["id"], row["status"], row.get("score", ""), row.get("manuel", "")[:60])
    print(dict(collections.Counter(r["status"] for r in results)))
    if args.write:
        json.dump({"methode": "voir l'en-tête de outils/audit_citations.py", "resultats": results},
                  open(OUT, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

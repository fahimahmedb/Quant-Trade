#!/usr/bin/env python3
"""Fetch a public URL and extract its raw text (HTML or PDF) to check a quote.

Usage:
  python fetch_text.py URL                 # fetch, cache, print path + head
  python fetch_text.py URL -g "regex" ...  # also print matching lines
  python fetch_text.py URL --head 4000     # print more of the text

Needs `pip install beautifulsoup4 pypdf`. The cache lives outside the repo
(PRATICIENS_CACHE, default: <tmp>/praticiens_cache). It never bypasses logins,
paywalls or anti-bot pages: HTTP >= 400 or a challenge page is reported as
NOT OPENED (exit code 2 or 3).
"""
import argparse
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile

CACHE = os.environ.get("PRATICIENS_CACHE", os.path.join(tempfile.gettempdir(), "praticiens_cache"))
UA = "Mozilla/5.0 (research; Quant practitioner study)"
BLOCK_MARKERS = ("Verifying your browser", "Anubis", "You've been blocked",
                 "Just a moment...", "cf-challenge", "Access Denied")


def fetch(url: str) -> tuple[int, str, bytes]:
    out = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "60", "-A", UA,
         "-w", "\n__META__%{http_code} %{content_type}", url],
        capture_output=True)
    raw = out.stdout
    meta_at = raw.rfind(b"\n__META__")
    meta = raw[meta_at + 9:].decode(errors="replace").split(" ", 1)
    code = int(meta[0]) if meta[0].isdigit() else 0
    return code, (meta[1] if len(meta) > 1 else ""), raw[:meta_at]


def to_text(ctype: str, body: bytes, url: str) -> str:
    if "pdf" in ctype or body[:5] == b"%PDF-" or url.lower().endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join((page.extract_text() or "") for page in PdfReader(io.BytesIO(body)).pages)
    if "json" in ctype:
        return body.decode(errors="replace")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(body, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return re.sub(r"\n\s*\n+", "\n", soup.get_text("\n"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("-g", "--grep", action="append", default=[])
    ap.add_argument("--head", type=int, default=1500)
    ap.add_argument("-C", type=int, default=1, help="context lines for grep")
    args = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, hashlib.sha1(args.url.encode()).hexdigest()[:16] + ".txt")
    if os.path.exists(path):
        text = open(path, encoding="utf-8").read()
    else:
        code, ctype, body = fetch(args.url)
        if code >= 400 or code == 0:
            print(f"NOT OPENED: HTTP {code} for {args.url}")
            sys.exit(2)
        text = to_text(ctype, body, args.url)
        if any(m in text[:5000] for m in BLOCK_MARKERS) and len(text) < 20000:
            print(f"NOT OPENED: anti-bot or block page for {args.url}")
            sys.exit(3)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"URL: {args.url}\n\n" + text)
    print(f"OPENED: {args.url}\nCACHE: {path}\nCHARS: {len(text)}")
    lines = text.splitlines()
    for pattern in args.grep:
        rx = re.compile(pattern, re.I)
        hits = [i for i, line in enumerate(lines) if rx.search(line)]
        print(f"\n--- grep /{pattern}/ : {len(hits)} hit(s)")
        for i in hits[:12]:
            lo, hi = max(0, i - args.C), min(len(lines), i + args.C + 1)
            print(f"[{i}] " + " | ".join(l.strip() for l in lines[lo:hi]))
    if not args.grep:
        print("\n" + text[: args.head])


if __name__ == "__main__":
    main()

"""F1 acquisition (Stage A or warm-up/Stage B by explicit month window).

Downloads Binance Vision monthly zips + .CHECKSUM files named by the F1
pre-registration, verifies sha256, and records a manifest. It never parses a
data row. The month window is passed explicitly and hard-asserted so that a
Stage A run cannot fetch a Stage B month.

Usage (outside the repo data dir):
    python3 -I acquire_f1.py STAGE_A OUT_DIR CANDIDATES_TXT CANDIDATES_SHA256
"""
import hashlib
import json
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

HOST = "https://data.binance.vision/"
LIST_BASE = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
UA = "quant-research-paper-shadow/0.1"
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
MAX_RPS = 5.0
WINDOWS = {
    # pre-registered windows (inclusive, YYYY-MM)
    "STAGE_A": ("2020-01", "2023-12"),
    "STAGE_B": ("2023-11", "2026-09"),  # includes 2023-11/12 warm-up files
}
DATASETS = {
    "funding": "data/futures/um/monthly/fundingRate/{s}/",
    "perp1d": "data/futures/um/monthly/klines/{s}/1d/",
    "spot1d": "data/spot/monthly/klines/{s}/1d/",
}


class RateLimiter:
    def __init__(self, rps):
        self.interval = 1.0 / rps
        self.lock = threading.Lock()
        self.next_t = 0.0

    def wait(self):
        with self.lock:
            now = time.monotonic()
            t = max(now, self.next_t)
            self.next_t = t + self.interval
        if t > now:
            time.sleep(t - now)


LIMITER = RateLimiter(MAX_RPS)
LISTING_404 = []


def http_get(url, tries=5):
    delay = 2.0
    for attempt in range(tries):
        LIMITER.wait()
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, b""
            if e.code in (403, 429):
                if attempt >= 2:
                    raise RuntimeError(f"HTTP {e.code} repeated for {url}; stopping")
            time.sleep(delay)
            delay *= 2
        except (urllib.error.URLError, TimeoutError):
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"giving up on {url}")


def list_files(prefix):
    """File names (keys) under a prefix; names only."""
    keys, marker = [], None
    while True:
        q = {"prefix": prefix}
        if marker:
            q["marker"] = marker
        status, body = http_get(LIST_BASE + "?" + urllib.parse.urlencode(q))
        if status == 404:
            # observed transient S3 404 on a listing that answers 200 on retry: retry, then record as empty
            for _ in range(3):
                time.sleep(3.0)
                status, body = http_get(LIST_BASE + "?" + urllib.parse.urlencode(q))
                if status != 404:
                    break
            if status == 404:
                LISTING_404.append(prefix)
                return keys
        if status != 200:
            raise RuntimeError(f"listing returned HTTP {status} for {prefix}")
        root = ET.fromstring(body)
        for c in root.iter(NS + "Contents"):
            keys.append(c.find(NS + "Key").text)
        if root.find(NS + "IsTruncated").text != "true":
            return keys
        marker = keys[-1]


def month_of(key):
    stem = key.rsplit("/", 1)[-1]
    if not stem.endswith(".zip"):
        return None
    return stem[:-4][-7:]  # ...-YYYY-MM


def parse_checksum(text, expect_name):
    parts = text.split()
    if len(parts) < 2 or len(parts[0]) != 64:
        raise ValueError("unrecognised checksum file format")
    if parts[1].lstrip("*") != expect_name:
        raise ValueError("checksum file names a different file")
    int(parts[0], 16)
    return parts[0].lower()


def fetch_one(job, out_dir):
    ds, sym, key = job
    name = key.rsplit("/", 1)[-1]
    st, zbody = http_get(HOST + key)
    st2, cbody = http_get(HOST + key + ".CHECKSUM")
    rec = {"dataset": ds, "symbol": sym, "key": key, "zip_status": st,
           "checksum_status": st2, "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if st != 200 or st2 != 200:
        rec["ok"] = False
        return rec
    want = parse_checksum(cbody.decode("ascii"), name)
    got = hashlib.sha256(zbody).hexdigest()
    rec.update({"bytes": len(zbody), "sha256": got, "checksum_sha256": want, "ok": got == want})
    if got == want:
        import os
        path = f"{out_dir}/{ds}/{sym}/{name}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            with open(path, "rb") as f:
                same = hashlib.sha256(f.read()).hexdigest() == got
            if same:
                rec["already_present"] = True
            else:
                os.remove(path)   # partial file from a killed run; replaced by the verified download
                rec["replaced_partial"] = True
        if not rec.get("already_present"):
            tmp = path + ".tmp"
            with open(tmp, "wb") as f:
                f.write(zbody)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
    return rec


def main(argv):
    stage, out_dir, cand_path, cand_sha = argv
    lo, hi = WINDOWS[stage]
    raw = open(cand_path, "rb").read()
    if hashlib.sha256(raw).hexdigest() != cand_sha:
        raise SystemExit("candidate list hash mismatch")
    symbols = raw.decode().split()
    jobs, listing_log = [], []
    for sym in symbols:
        for ds, pat in DATASETS.items():
            keys = list_files(pat.format(s=sym))
            months = sorted(m for m in (month_of(k) for k in keys) if m)
            listing_log.append({"dataset": ds, "symbol": sym, "n_listed": len(months),
                                "first": months[0] if months else None,
                                "last": months[-1] if months else None})
            for k in keys:
                m = month_of(k)
                if m and lo <= m <= hi:
                    assert lo <= m <= hi
                    jobs.append((ds, sym, k))
    for ds, sym, k in jobs:
        assert lo <= month_of(k) <= hi, "window violation"
    import os
    os.makedirs(out_dir, exist_ok=True)
    # Resume support (infra restarts): keys already recorded ok whose file is present with the same sha256 are skipped.
    mpath = f"{out_dir}/manifest_{stage}.jsonl"
    done = set()
    if os.path.exists(mpath):
        with open(mpath) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue  # a truncated last line from a killed process
                p = f"{out_dir}/{rec['dataset']}/{rec['symbol']}/{rec['key'].rsplit('/', 1)[-1]}"
                if rec.get("ok") and os.path.exists(p):
                    with open(p, "rb") as zf:
                        if hashlib.sha256(zf.read()).hexdigest() == rec["sha256"]:
                            done.add(rec["key"])
    jobs = [j for j in jobs if j[2] not in done]
    n = 0
    while os.path.exists(f"{out_dir}/listing_{stage}{'' if n == 0 else '_resume' + str(n)}.json"):
        n += 1
    with open(f"{out_dir}/listing_{stage}{'' if n == 0 else '_resume' + str(n)}.json", "x") as f:
        json.dump({"prefixes": listing_log, "persistent_404_prefixes": LISTING_404}, f)
    if os.path.exists(mpath):
        with open(mpath, "rb+") as f:   # drop a truncated trailing line, if any
            data = f.read()
            if data and not data.endswith(b"\n"):
                f.seek(0)
                f.truncate(data.rfind(b"\n") + 1)
    with open(mpath, "a") as mf:
        for j in jobs:   # sequential: the first repeated 403/429 raises and stops everything
            mf.write(json.dumps(fetch_one(j, out_dir), sort_keys=True) + "\n")
            mf.flush()
    print(f"{stage}: {len(jobs)} jobs fetched this run; {len(done)} already present")


if __name__ == "__main__":
    main(sys.argv[1:])

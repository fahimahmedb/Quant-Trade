"""Telecharge et convertit au format du repo l'historique OHLC quotidien de
3 indices externes (Russell 2000, S&P 500, DAX) pour le backtest cross-market
(cf. scripts/run_backtest_indices.py). Meme logique que la source
`quant-data-fetcher` deja utilisee dans le repo (Stooq d'abord), mais Stooq
bloque desormais les requetes non-navigateur (challenge JS) : source de
repli utilisee ici = API publique Yahoo Finance "chart" (aucune cle requise).

Ne touche jamais data/nasdaq_composite_daily.txt ni data/nasdaq100_daily.txt.
Sauvegarde sous 3 nouveaux fichiers :
  data/russell2000_daily.txt   (^RUT)
  data/sp500_daily.txt         (^GSPC)
  data/dax_daily.txt           (^GDAXI)

Nettoyage minimal, comme le reste du repo : clamp OHLC (high=max(o,h,c),
low=min(o,l,c) - ne supprime aucune ligne pour ca), coupe avant la premiere
date a volume non nul (ere de cotation fiable - les tout premiers historiques
d'indice sont souvent non trades/reconstruits), dedoublonnage par date.

Usage : python3 scripts/fetch_index_data.py
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402

# Univers FIGE de 3 indices (cf. CLAUDE.md / tache), aucun ajout a posteriori.
TARGETS = [
    ("%5ERUT", ROOT / "data" / "russell2000_daily.txt", "Russell 2000 (^RUT)"),
    ("%5EGSPC", ROOT / "data" / "sp500_daily.txt", "S&P 500 (^GSPC)"),
    ("%5EGDAXI", ROOT / "data" / "dax_daily.txt", "DAX (^GDAXI)"),
]

YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=0&period2={now}&interval=1d"


def fetch_json(symbol: str) -> dict:
    now = int(time.time())
    url = YAHOO_URL.format(sym=symbol, now=now)
    out = subprocess.run(
        ["curl", "-sS", "-m", "60", url, "-H", "User-Agent: Mozilla/5.0"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def convert(data: dict, out_path: Path) -> dict:
    res = data["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    o, h, l, c, v = q["open"], q["high"], q["low"], q["close"], q["volume"]

    rows = []
    n_dropped_nan = 0
    n_clamped = 0
    for i in range(len(ts)):
        if o[i] is None or h[i] is None or l[i] is None or c[i] is None:
            n_dropped_nan += 1
            continue
        dt = datetime.datetime.utcfromtimestamp(ts[i])
        vol = v[i] if v[i] is not None else 0
        oo, hh, ll, cc = float(o[i]), float(h[i]), float(l[i]), float(c[i])
        new_hh, new_ll = max(oo, hh, cc), min(oo, ll, cc)
        if new_hh != hh or new_ll != ll:
            n_clamped += 1
        rows.append((dt, oo, new_hh, new_ll, cc, vol))

    # coupe avant la premiere date a volume non nul (ere fiable, cf. docstring)
    first_vol_idx = next((i for i, r in enumerate(rows) if r[5] and r[5] > 0), 0)
    rows = rows[first_vol_idx:]

    by_date = {}
    for r in rows:
        by_date[r[0].date()] = r  # dedoublonnage, garde la derniere occurrence
    rows = [by_date[k] for k in sorted(by_date.keys())]

    lines = ["date\touv\thaut\tbas\tclot\tvol\tdevise\t\r"]
    for dt, oo, hh, ll, cc, vol in rows:
        lines.append(
            f"{dt.strftime('%d/%m/%Y')} 00:00\t{oo:.3f}\t{hh:.3f}\t{ll:.3f}\t{cc:.3f}\t{int(vol)}\tPts\t\r"
        )
    out_path.write_text("\n".join(lines) + "\n", newline="\n")

    return {
        "n_rows": len(rows), "n_dropped_nan": n_dropped_nan, "n_clamped": n_clamped,
        "start": rows[0][0].date(), "end": rows[-1][0].date(),
        "cut_idx": first_vol_idx,
    }


def main():
    for symbol, out_path, label in TARGETS:
        print(f"=== {label} -> {out_path.name} ===")
        data = fetch_json(symbol)
        info = convert(data, out_path)
        print(f"  {info['n_rows']} séances, {info['start']} -> {info['end']} "
              f"(coupe à l'indice {info['cut_idx']} = 1re date volume>0 ; "
              f"{info['n_dropped_nan']} lignes NaN ignorées, "
              f"{info['n_clamped']} OHLC clampés)")
        df = load_ohlc(str(out_path))
        rep = quality_report(df)  # leve si donnees corrompues
        print(f"  quality_report OK : {rep['n_obs']} obs, "
              f"{rep['dup_dates']} doublons, {rep['bad_ohlc_rows']} lignes OHLC incohérentes, "
              f"max |rdt| {rep['max_abs_ret_pct']:.1f}%")


if __name__ == "__main__":
    main()

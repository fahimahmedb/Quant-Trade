"""Quantification honnête put-write/covered-call (CBOE PUT/BXM) vs S&P 500,
donnees REELLES (Yahoo Finance, indices publics ^PUT, ^BXM, ^GSPC).

Ce sont des indices officiels CBOE (methodologie publique, calcules depuis
des dizaines d'annees) -- pas une strategie qu'on construit, un produit deja
construit par le marche des options qu'on ne fait qu'observer/investir.
Sert de point de comparaison honnete a l'edge de volatilite deja valide
(Etape C) et aux pistes alternatives (funding rate arb crypto).
"""
import calendar
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]        # finance/trading
COST_FREE = True  # indices officiels, pas de simulation de cout ici (deja net dans la methodo CBOE)

TICKERS = {"^BXM": "Covered-call (Buy-Write)", "^PUT": "Put-Write", "^GSPC": "S&P 500 (référence)"}


YEARS_BACK = 30  # fenetre bornee explicitement : "range=max" fait taire Yahoo qui
                  # renvoie alors des barres 3mo (verifie empiriquement), pas daily.
                  # 30 ans pour capturer 2008 (GFC) en plus du bull run 2011-2026,
                  # sinon comparaison biaisee contre put-write/covered-call (qui
                  # sous-performe precisement en marche fortement haussier, cf.
                  # litterature -- ne pas se limiter a la fenetre la plus favorable
                  # au buy-hold pur).


def fetch_yahoo_daily(ticker: str) -> dict:
    period2 = int(time.time())
    period1 = period2 - YEARS_BACK * 365 * 86400
    url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={period1}&period2={period2}&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read())
    result = payload["chart"]["result"][0]
    granularity = result["meta"].get("dataGranularity")
    if granularity != "1d":
        raise ValueError(f"granularite inattendue: {granularity} (donnees non fiables)")
    ts = np.array(result["timestamp"])
    close = np.array(result["indicators"]["quote"][0]["close"], dtype=float)
    mask = np.isfinite(close)
    return {"ts": ts[mask], "close": close[mask]}


def metrics_from_close(close: np.ndarray) -> dict:
    r = np.diff(np.log(close))
    ann = np.sqrt(252)
    equity = close / close[0]
    running_max = np.maximum.accumulate(equity)
    dd = equity / running_max - 1.0
    mdd = dd.min() * 100
    cagr = (close[-1] / close[0]) ** (252.0 / len(close)) - 1.0
    sharpe = (r.mean() / r.std()) * ann if r.std() > 0 else float("nan")
    return {
        "cagr_pct": 100 * cagr,
        "vol_ann_pct": 100 * ann * r.std(),
        "sharpe_ann": sharpe,
        "mdd_pct": mdd,
    }


CRISIS_START = calendar.timegm((2007, 6, 1, 0, 0, 0))
CRISIS_END = calendar.timegm((2009, 12, 31, 23, 59, 59))


def main():
    lines = [
        "# Quantification — put-write / covered-call vs S&P 500 (données réelles CBOE via Yahoo)",
        "",
        "Indices officiels CBOE (méthodologie publique) — produit déjà construit par "
        "le marché des options, pas une stratégie qu'on bâtit soi-même. Deux fenêtres "
        "rapportées : plein historique (30 ans) ET la crise 2007-2009 isolément — "
        "éviter de choisir la seule fenêtre favorable à un camp (le bull run "
        "2011-2026 favorise mécaniquement le Buy&Hold pur face au covered-call).",
        "",
        "## Plein historique (30 ans, inclut 2000-02 et 2008)",
        "",
        "| Indice | Historique | CAGR | Vol ann. | Sharpe ann. | MDD |",
        "|---|---|---|---|---|---|",
    ]

    fetched = {}
    for ticker, label in TICKERS.items():
        try:
            data = fetch_yahoo_daily(ticker)
        except Exception as e:
            lines.append(f"| {label} ({ticker}) | ERREUR: {e} | | | | |")
            continue
        fetched[ticker] = data
        close = data["close"]
        ts = data["ts"]
        t0 = time.strftime("%Y-%m-%d", time.gmtime(int(ts[0])))
        t1 = time.strftime("%Y-%m-%d", time.gmtime(int(ts[-1])))
        me = metrics_from_close(close)
        lines.append(
            f"| {label} ({ticker}) | {t0} → {t1} ({len(close)} obs) | "
            f"{me['cagr_pct']:+.1f}% | {me['vol_ann_pct']:.1f}% | {me['sharpe_ann']:+.2f} | "
            f"{me['mdd_pct']:.1f}% |"
        )
        time.sleep(0.5)

    lines.append("")
    lines.append("## Sous-période crise (2007-06 → 2009-12, GFC)")
    lines.append("")
    lines.append("| Indice | Obs | CAGR (période) | Vol ann. | Sharpe ann. | MDD (période) |")
    lines.append("|---|---|---|---|---|---|")
    for ticker, label in TICKERS.items():
        if ticker not in fetched:
            lines.append(f"| {label} ({ticker}) | pas de données | | | | |")
            continue
        ts = fetched[ticker]["ts"]
        close = fetched[ticker]["close"]
        mask = (ts >= CRISIS_START) & (ts <= CRISIS_END)
        if mask.sum() < 30:
            lines.append(f"| {label} ({ticker}) | {mask.sum()} obs (insuffisant, hors couverture) | | | | |")
            continue
        me = metrics_from_close(close[mask])
        lines.append(
            f"| {label} ({ticker}) | {mask.sum()} | {me['cagr_pct']:+.1f}% | "
            f"{me['vol_ann_pct']:.1f}% | {me['sharpe_ann']:+.2f} | {me['mdd_pct']:.1f}% |"
        )

    lines.append("")
    lines.append(
        "**Lecture honnête** : le put-write/covered-call n'est pas de l'alpha au sens "
        "strict (pas un edge de prévision) — c'est une reconfiguration du profil de "
        "risque de la prime actions (moins de volatilité, moins de risque de queue à la "
        "hausse en échange d'un plafonnement des gains extrêmes). Comparable à Étape C "
        "par l'esprit (les deux monétisent la prime de risque de volatilité plutôt "
        "qu'un pari directionnel), mais Étape C n'a jamais été testé sur le marché des "
        "options lui-même — ce tableau donne juste la référence empirique de ce que le "
        "marché encaisse déjà pour ce type de risque, à comparer avec le funding rate "
        "arbitrage crypto (voir `funding_rate_arb_quantification.md`)."
    )

    out = ROOT / "results" / "putwrite_quantification.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

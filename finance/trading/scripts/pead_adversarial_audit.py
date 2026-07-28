"""Audit adversarial de la stratégie PEAD — recalcule depuis les données
brutes, ne fait confiance à aucun chiffre de `pead_backtest.py`.

Trois angles :
1. Recalcul INDÉPENDANT (méthode event-time simple, différente du
   calendar-time du backtest principal) pour vérifier que le signe/ordre
   de grandeur de l'effet ne dépend pas d'un bug de construction du
   portefeuille calendar-time.
2. Quantification de la fuite potentielle des terciles "pleine période"
   (déjà signalée comme limite dans PEAD_PREREGISTRATION.md, mais jamais
   MESURÉE) : comparaison des terciles fixés sur tout l'échantillon vs des
   terciles causaux (fenêtre expansive, ne connaissant que le passé à
   chaque date) — quelle fraction des événements changerait de panier ?
3. Concentration : la performance repose-t-elle sur une poignée de titres
   (effective N faible), ou est-elle diffuse sur l'univers ?
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "pead"
EVENTS_PATH = DATA_DIR / "earnings_events.json"
PRICES_DIR = DATA_DIR / "prices"
H = 60
COST_BPS = 10.0


def load_price_series(ticker: str):
    path = PRICES_DIR / f"{ticker}.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text())
    if "error" in payload:
        return None
    ts = pd.to_datetime(payload["ts"], unit="s").normalize()
    close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
    close = close[~close.index.duplicated(keep="first")].sort_index()
    return close if len(close) > H + 5 else None


def event_time_return(price: pd.Series, event_date: pd.Timestamp):
    idx = price.index
    pos_after = idx.searchsorted(event_date, side="right")
    if pos_after >= len(idx):
        return None
    exit_i = min(pos_after + H, len(idx) - 1)
    if exit_i <= pos_after:
        return None
    total_r = np.log(price.iloc[exit_i] / price.iloc[pos_after]) - COST_BPS / 1e4
    return total_r


def main():
    events = json.loads(EVENTS_PATH.read_text())
    events_sorted = sorted(events, key=lambda e: e["date"])
    surprises_full = np.array([e["surprise_pct"] for e in events_sorted])
    q_lo_full, q_hi_full = np.percentile(surprises_full, [100 / 3, 200 / 3])

    lines = [
        "# Audit adversarial — stratégie PEAD",
        "",
        "## 1. Recalcul indépendant (event-time, méthode différente du backtest principal)",
        "",
    ]

    price_cache = {}
    long_rets, short_rets = [], []
    for e in events_sorted:
        sym = e["symbol"]
        if sym not in price_cache:
            price_cache[sym] = load_price_series(sym)
        price = price_cache[sym]
        if price is None:
            continue
        s = e["surprise_pct"]
        if s >= q_hi_full:
            r = event_time_return(price, pd.Timestamp(e["date"]))
            if r is not None:
                long_rets.append(r)
        elif s <= q_lo_full:
            r = event_time_return(price, pd.Timestamp(e["date"]))
            if r is not None:
                short_rets.append(r)

    long_rets, short_rets = np.array(long_rets), np.array(short_rets)
    mean_long = long_rets.mean() if len(long_rets) else float("nan")
    mean_short = short_rets.mean() if len(short_rets) else float("nan")
    spread = mean_long - mean_short

    lines.append(
        f"Méthode event-time (moyenne simple du rendement total sur H={H}j par "
        f"événement, PAS le portefeuille calendar-time du backtest principal) :\n\n"
        f"- Rendement moyen long ({len(long_rets)} événements) : {100*mean_long:+.2f}% sur {H}j\n"
        f"- Rendement moyen court ({len(short_rets)} événements) : {100*mean_short:+.2f}% sur {H}j\n"
        f"- Spread long−court : {100*spread:+.2f}% sur {H}j\n\n"
        f"**Cohérence avec le backtest principal (calendar-time)** : le signe du spread "
        f"doit être {'positif' if spread > 0 else 'négatif ou nul'} dans les deux méthodes "
        "pour exclure un bug de construction — à comparer manuellement avec "
        "`results/pead_backtest_result.md`."
    )
    lines.append("")

    # --- 2. Fuite des terciles pleine periode vs causal (expansive) ---
    lines.append("## 2. Fuite mesurée des terciles \"pleine période\" (vs terciles causaux)")
    lines.append("")
    n_flip = 0
    n_checked = 0
    MIN_CAUSAL_N = 30  # pas de tercile fiable avant d'avoir vu assez d'evenements
    for i, e in enumerate(events_sorted):
        if i < MIN_CAUSAL_N:
            continue
        past_surprises = surprises_full[:i]
        q_lo_c, q_hi_c = np.percentile(past_surprises, [100 / 3, 200 / 3])
        s = e["surprise_pct"]

        def bucket(s, lo, hi):
            return "long" if s >= hi else ("short" if s <= lo else "mid")

        b_full = bucket(s, q_lo_full, q_hi_full)
        b_causal = bucket(s, q_lo_c, q_hi_c)
        n_checked += 1
        if b_full != b_causal:
            n_flip += 1

    pct_flip = 100 * n_flip / n_checked if n_checked else float("nan")
    lines.append(
        f"Sur {n_checked} événements comparables (après {MIN_CAUSAL_N} événements de "
        f"warmup), **{pct_flip:.1f}%** changeraient de panier (long/court/ignoré) si on "
        "utilisait des terciles causaux (fenêtre expansive, ne connaissant que le passé) "
        "au lieu des terciles pleine-période utilisés dans le backtest principal. "
        + ("C'est une fuite MINEURE, le résultat principal est probablement robuste à ce "
           "choix." if pct_flip < 10 else
           "**C'est une fuite NON négligeable** — le résultat du backtest principal "
           "pourrait changer significativement avec des terciles causaux ; à re-tester "
           "avant toute conclusion définitive (nouveau pré-enregistrement requis, pas un "
           "simple correctif sur celui-ci).")
    )
    lines.append("")

    # --- 3. Concentration ---
    lines.append("## 3. Concentration de l'échantillon")
    lines.append("")
    long_syms = pd.Series([e["symbol"] for e in events_sorted if e["surprise_pct"] >= q_hi_full])
    short_syms = pd.Series([e["symbol"] for e in events_sorted if e["surprise_pct"] <= q_lo_full])
    top_long = long_syms.value_counts().head(5)
    top_short = short_syms.value_counts().head(5)
    lines.append(f"Panier long : {long_syms.nunique()} tickers distincts sur {len(long_syms)} événements. "
                 f"Top 5 : {dict(top_long)} ({100*top_long.sum()/len(long_syms):.1f}% du panier).")
    lines.append("")
    lines.append(f"Panier court : {short_syms.nunique()} tickers distincts sur {len(short_syms)} événements. "
                 f"Top 5 : {dict(top_short)} ({100*top_short.sum()/len(short_syms):.1f}% du panier).")
    lines.append("")
    conc_ok = (top_long.sum() / max(len(long_syms), 1) < 0.30) and (top_short.sum() / max(len(short_syms), 1) < 0.30)
    lines.append(
        "Concentration jugée "
        + ("acceptable (aucun groupe de 5 titres ne domine >30% d'un panier)."
           if conc_ok else
           "**préoccupante** (un petit nombre de titres domine un panier — le résultat "
           "pourrait refléter quelques trajectoires idiosyncratiques plutôt qu'un effet "
           "diffus PEAD).")
    )

    out = ROOT / "results" / "pead_adversarial_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

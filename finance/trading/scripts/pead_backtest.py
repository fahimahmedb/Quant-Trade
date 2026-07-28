"""Backtest PEAD — EXÉCUTE la spécification figée dans
`PEAD_PREREGISTRATION.md` (committé avant ce script). Aucun paramètre ici
n'est choisi après avoir vu un résultat.

Construction "calendar-time portfolio" (Fama-style, préférée à la moyenne
event-time à cause du chevauchement des fenêtres de détention) : pour
chaque jour de bourse, on moyenne le rendement du jour de toutes les
positions longues actives, et séparément de toutes les positions courtes
actives ; le rendement du portefeuille dollar-neutre = moyenne(longues) -
moyenne(courtes) ce jour-là.
"""
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]  # finance/trading
DATA_DIR = ROOT / "data" / "pead"
EVENTS_PATH = DATA_DIR / "earnings_events.json"
PRICES_DIR = DATA_DIR / "prices"

H = 60             # seances de detention, pre-enregistre
COST_BPS = 10.0    # aller-retour, pre-enregistre (5bps entree + 5bps sortie)
DESIGN_TEST_SPLIT = "2024-01-01"


def load_price_series(ticker: str) -> pd.Series | None:
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


def build_position(price: pd.Series, event_date: pd.Timestamp, sign: float):
    """Renvoie une Series de rendements log quotidiens signes (avec cout
    d'entree/sortie deduits), indexee sur les jours de detention reels de
    CE titre (peut differer du calendrier NDX-100 global : jours feries
    locaux, etc. -- neglige ici, limite mineure assumee)."""
    idx = price.index
    pos_after = idx.searchsorted(event_date, side="right")
    if pos_after >= len(idx):
        return None
    entry_i = pos_after  # 1er jour de bourse APRES l'annonce (pre-enregistre)
    exit_i = min(entry_i + H, len(idx) - 1)
    if exit_i <= entry_i:
        return None
    window = price.iloc[entry_i:exit_i + 1]
    r = np.log(window).diff().dropna() * sign
    if r.empty:
        return None
    cost = (COST_BPS / 2.0) / 1e4  # moitie a l'entree, moitie a la sortie
    r.iloc[0] -= cost
    r.iloc[-1] -= cost
    return r


def main():
    events = json.loads(EVENTS_PATH.read_text())
    print(f"{len(events)} événements chargés")

    surprises = np.array([e["surprise_pct"] for e in events])
    q_lo, q_hi = np.percentile(surprises, [100 / 3, 200 / 3])
    print(f"Terciles de surprise (fixés sur la distribution complète, pas sur les rendements) : "
          f"q1={q_lo:.2f}%, q2={q_hi:.2f}%")

    price_cache = {}
    long_positions = []   # liste de (event_date, pd.Series rendement)
    short_positions = []
    skipped_no_price = 0

    for e in events:
        sym = e["symbol"]
        if sym not in price_cache:
            price_cache[sym] = load_price_series(sym)
        price = price_cache[sym]
        if price is None:
            skipped_no_price += 1
            continue
        surprise = e["surprise_pct"]
        if surprise >= q_hi:
            sign, bucket = +1.0, long_positions
        elif surprise <= q_lo:
            sign, bucket = -1.0, short_positions
        else:
            continue  # tercile median ignore, pre-enregistre
        event_date = pd.Timestamp(e["date"])
        r = build_position(price, event_date, sign)
        if r is not None:
            bucket.append((event_date, sym, r))

    print(f"Positions longues ouvertes : {len(long_positions)}, courtes : {len(short_positions)}, "
          f"événements sans prix exploitable : {skipped_no_price}")

    def to_panel(positions):
        frames = [r.rename(f"{i}_{sym}") for i, (_, sym, r) in enumerate(positions)]
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, axis=1)

    long_panel = to_panel(long_positions)
    short_panel = to_panel(short_positions)

    all_days = long_panel.index.union(short_panel.index).sort_values()
    mean_long = long_panel.reindex(all_days).mean(axis=1).fillna(0.0)
    mean_short = short_panel.reindex(all_days).mean(axis=1).fillna(0.0)
    n_long_active = long_panel.reindex(all_days).notna().sum(axis=1)
    n_short_active = short_panel.reindex(all_days).notna().sum(axis=1)

    port = (mean_long - mean_short)
    # seuls les jours ou au moins une jambe est active des le depart (warmup)
    active_mask = (n_long_active > 0) | (n_short_active > 0)
    port = port[active_mask]

    ann = np.sqrt(252)

    def sharpe_tstat(r: pd.Series):
        if len(r) < 20 or r.std() == 0:
            return float("nan"), float("nan")
        sharpe = r.mean() / r.std() * ann
        tstat = r.mean() / r.std() * np.sqrt(len(r))
        return sharpe, tstat

    sharpe_full, tstat_full = sharpe_tstat(port)

    design = port[port.index < DESIGN_TEST_SPLIT]
    test = port[port.index >= DESIGN_TEST_SPLIT]
    sharpe_design, _ = sharpe_tstat(design)
    sharpe_test, _ = sharpe_tstat(test)
    degradation = (sharpe_design - sharpe_test) / abs(sharpe_design) if sharpe_design not in (0, float("nan")) else float("nan")

    ok_full = (sharpe_full > 0) and (tstat_full > 2)
    ok_split = (sharpe_test > 0) and (not np.isnan(degradation)) and (degradation < 0.5)
    verdict = ok_full and ok_split

    lines = [
        "# Backtest PEAD — résultat (spécification pré-enregistrée, exécutée UNE fois)",
        "",
        f"Univers : NDX-100 actuel ({len(price_cache)} tickers avec prix exploitable). "
        f"Événements longs/courts retenus : {len(long_positions)}/{len(short_positions)} "
        f"(tercile médian ignoré). {skipped_no_price} événements écartés faute de prix.",
        "",
        f"Terciles de surprise : long si surprise ≥ {q_hi:.2f}%, court si surprise ≤ {q_lo:.2f}%.",
        "",
        "## Portefeuille long-short dollar-neutre (calendar-time, net de coûts 10bps)",
        "",
        f"- Période complète ({port.index.min().date()} → {port.index.max().date()}, "
        f"{len(port)} jours actifs) : Sharpe ann. = {sharpe_full:+.2f}, t-stat = {tstat_full:+.2f}",
        f"- Design (< {DESIGN_TEST_SPLIT}, {len(design)} obs) : Sharpe ann. = {sharpe_design:+.2f}",
        f"- Test (≥ {DESIGN_TEST_SPLIT}, {len(test)} obs) : Sharpe ann. = {sharpe_test:+.2f}",
        f"- Dégradation design→test : {100*degradation:+.1f}%" if not np.isnan(degradation) else "- Dégradation : N/A",
        "",
        "## Verdict vis-à-vis du critère pré-enregistré",
        "",
        f"1. Sharpe>0 ET t-stat>2 sur période complète : {'OUI' if ok_full else 'NON'}",
        f"2. Sharpe test>0 ET dégradation<50% : {'OUI' if ok_split else 'NON'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
        f"{'atteint' if verdict else 'NON atteint'}.**",
        "",
        "**Rappel des limites pré-enregistrées** : biais de survie (constituants NDX-100 "
        "actuels, pas point-in-time), coûts 10bps modélisés de façon simplifiée "
        "(5bps entrée + 5bps sortie, pas de slippage réel), jours de détention "
        "calés sur le calendrier propre à chaque titre (pas de gestion fine des "
        "jours fériés croisés). n_trials=1, aucune variante testée après ce résultat.",
    ]

    out = ROOT / "results" / "pead_backtest_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")

    # Sauvegarde de la serie du portefeuille pour l'audit adversarial (recalcul independant)
    port.to_frame("port_ret").to_csv(DATA_DIR / "pead_portfolio_returns.csv")


if __name__ == "__main__":
    main()

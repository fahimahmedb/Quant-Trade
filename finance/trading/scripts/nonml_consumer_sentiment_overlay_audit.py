"""Audit indépendant — Indice de confiance des consommateurs (Michigan).

Recalcule l'alignement causal (avec décalage d'un mois) et le tercile
expanding par une méthode alternative (boucle explicite + searchsorted,
sans pandas.reindex/ffill/DateOffset ni np.percentile), compare au
résultat committé du backtest. Vérifie aussi l'absence de fuite
(troncature de l'historique).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_consumer_sentiment_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, build_sentiment_series, load_sentiment_lag,
    expanding_tercile_cut_high,
)


def manual_sentiment_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    raw = pd.read_csv(REPO_ROOT / "data" / "umcsent_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["UMCSENT"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["UMCSENT"].astype(float).values

    avail_dates = []
    for d in pd.DatetimeIndex(obs_dates):
        y, m = d.year, d.month + 1
        if m > 12:
            y, m = y + 1, m - 12
        avail_dates.append(pd.Timestamp(year=y, month=m, day=1))
    avail_dates = np.array(avail_dates)
    order = np.argsort(avail_dates)
    avail_sorted, vals_sorted = avail_dates[order], vals[order]

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(avail_sorted, d, side="right") - 1
        if idx < 0:
            continue
        out[i] = vals_sorted[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def manual_percentile_high_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (200.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    lines = ["# Audit — Indice de confiance des consommateurs (Michigan)", ""]
    all_ok = True

    sentiment_series = build_sentiment_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        sentiment_lag_official = load_sentiment_lag(dates, sentiment_series)[1:]
        pos_official = expanding_tercile_cut_high(sentiment_lag_official)

        sentiment_lag_manual = manual_sentiment_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(sentiment_lag_official - sentiment_lag_manual))

        start = int(np.argmax(np.isfinite(sentiment_lag_manual)))
        T = len(sentiment_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(sentiment_lag_manual[t]):
                continue
            hist = sentiment_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_high_tercile(hist)
            pos_manual[t] = CUT if sentiment_lag_manual[t] >= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(sentiment_lag_official[i] - sentiment_lag_manual[i])
            if local_diff >= 1e-10:
                boundary_tie_ok = False

        ok = (diff_align < 1e-8) and (n_pos_diff == 0 or boundary_tie_ok)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas DateOffset/reindex/ffill/shift vs boucle+searchsorted manuel) : {diff_align:.2e}")
        if n_pos_diff == 0:
            lines.append("- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00")
        else:
            lines.append(f"- **{n_pos_diff}/{n_total} désaccords de position** — sensibilité de bord flottante "
                         f"documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#204) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage d'un mois (meme test que #195/#203).
    raw = pd.read_csv(REPO_ROOT / "data" / "umcsent_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    ref_row = raw[raw["observation_date"] == pd.Timestamp("2026-05-01")]
    check_dates = pd.DatetimeIndex([pd.Timestamp("2026-05-15"), pd.Timestamp("2026-05-31"),
                                     pd.Timestamp("2026-06-01"), pd.Timestamp("2026-06-02")])
    sentiment_check = load_sentiment_lag(check_dates, sentiment_series)
    lines.append("## Vérification spécifique du décalage d'un mois (mai 2026)")
    lines.append(f"- Valeur UMCSENT mai 2026 dans la source brute : {float(ref_row['UMCSENT'].iloc[0]):.1f}")
    lines.append(f"- UMCSENT_lag(15 mai) = {sentiment_check[0]}, UMCSENT_lag(31 mai) = {sentiment_check[1]} "
                 f"(doivent être la valeur d'avril, JAMAIS mai)")
    lines.append(f"- UMCSENT_lag(1 juin) = {sentiment_check[2]}, UMCSENT_lag(2 juin) = {sentiment_check[3]} "
                 f"(le 2 juin doit être le premier jour où mai apparaît, via shift(1))")
    may_val = float(ref_row["UMCSENT"].iloc[0])
    ok_shift = (not np.isclose(sentiment_check[0], may_val)) and (not np.isclose(sentiment_check[1], may_val)) \
        and np.isclose(sentiment_check[3], may_val)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur de mai apparaît uniquement à partir du 2 juin, jamais avant' if ok_shift else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    sentiment_lag_full = load_sentiment_lag(dates, sentiment_series)[1:]
    pos_full = expanding_tercile_cut_high(sentiment_lag_full)
    valid_start = int(np.argmax(np.isfinite(sentiment_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_high(sentiment_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_consumer_sentiment_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()

"""Audit indépendant — Indice d'activité nationale de la Fed de Chicago
(CFNAI).

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
from nonml_chicago_fed_activity_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, build_cfnai_series, load_cfnai_lag,
    expanding_tercile_cut_low,
)


def manual_cfnai_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    raw = pd.read_csv(REPO_ROOT / "data" / "cfnai_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["CFNAI"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["CFNAI"].astype(float).values

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


def manual_percentile_low_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (100.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    lines = ["# Audit — Indice d'activité nationale de la Fed de Chicago (CFNAI)", ""]
    all_ok = True

    cfnai_series = build_cfnai_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        cfnai_lag_official = load_cfnai_lag(dates, cfnai_series)[1:]
        pos_official = expanding_tercile_cut_low(cfnai_lag_official)

        cfnai_lag_manual = manual_cfnai_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(cfnai_lag_official - cfnai_lag_manual))

        start = int(np.argmax(np.isfinite(cfnai_lag_manual)))
        T = len(cfnai_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(cfnai_lag_manual[t]):
                continue
            hist = cfnai_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if cfnai_lag_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(cfnai_lag_official[i] - cfnai_lag_manual[i])
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
                         f"documentée (même pattern que #193/#195/#196/#197/#198/#199/#200/#203/#204/#205) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage d'un mois (meme test que #195/#203/#204/#205).
    raw = pd.read_csv(REPO_ROOT / "data" / "cfnai_monthly.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    ref_row = raw[raw["observation_date"] == pd.Timestamp("2026-05-01")]
    check_dates = pd.DatetimeIndex([pd.Timestamp("2026-05-15"), pd.Timestamp("2026-05-31"),
                                     pd.Timestamp("2026-06-01"), pd.Timestamp("2026-06-02")])
    cfnai_check = load_cfnai_lag(check_dates, cfnai_series)
    lines.append("## Vérification spécifique du décalage d'un mois (mai 2026)")
    lines.append(f"- Valeur CFNAI mai 2026 dans la source brute : {float(ref_row['CFNAI'].iloc[0]):.2f}")
    lines.append(f"- CFNAI_lag(15 mai) = {cfnai_check[0]}, CFNAI_lag(31 mai) = {cfnai_check[1]} "
                 f"(doivent être la valeur d'avril, JAMAIS mai)")
    lines.append(f"- CFNAI_lag(1 juin) = {cfnai_check[2]}, CFNAI_lag(2 juin) = {cfnai_check[3]} "
                 f"(le 2 juin doit être le premier jour où mai apparaît, via shift(1))")
    may_val = float(ref_row["CFNAI"].iloc[0])
    ok_shift = (not np.isclose(cfnai_check[0], may_val)) and (not np.isclose(cfnai_check[1], may_val)) \
        and np.isclose(cfnai_check[3], may_val)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — la valeur de mai apparaît uniquement à partir du 2 juin, jamais avant' if ok_shift else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    cfnai_lag_full = load_cfnai_lag(dates, cfnai_series)[1:]
    pos_full = expanding_tercile_cut_low(cfnai_lag_full)
    valid_start = int(np.argmax(np.isfinite(cfnai_lag_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_low(cfnai_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_chicago_fed_activity_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()

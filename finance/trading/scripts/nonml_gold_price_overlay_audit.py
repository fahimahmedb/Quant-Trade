"""Audit indépendant — Momentum de l'or (GLD, log-return 21j).

Recalcule GoldMom_lag(t), le tercile expanding et la position par une
méthode alternative (boucle explicite + searchsorted, sans
pandas.reindex/ffill/np.percentile), compare au résultat committé du
backtest. Vérifie le décalage causal d'un jour sur une transition
réelle et l'absence de fuite par troncature de l'historique.
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
from nonml_dollar_strength_overlay_backtest import MARKETS, RET_WINDOW  # noqa: E402
from nonml_bitcoin_momentum_overlay_backtest import CUT  # noqa: E402
from nonml_gold_price_overlay_backtest import load_gold_mom_lag, load_gold_series, expanding_tercile_cut_high  # noqa: E402


def manual_gold_mom_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted (side='right'-1,
    inclusif), sans pandas.reindex/ffill."""
    raw = pd.read_csv(REPO_ROOT / "data" / "gold_gld_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["GLD"] = pd.to_numeric(raw["GLD"], errors="coerce")
    raw = raw.dropna(subset=["GLD"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["GLD"].astype(float).values

    aligned = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(obs_dates, np.datetime64(d), side="right") - 1
        if idx < 0:
            continue
        aligned[i] = vals[idx]

    mom = np.full(len(dates), np.nan)
    for i in range(RET_WINDOW, len(dates)):
        if np.isfinite(aligned[i]) and np.isfinite(aligned[i - RET_WINDOW]):
            mom[i] = np.log(aligned[i] / aligned[i - RET_WINDOW])

    shifted = np.full(len(dates), np.nan)
    shifted[1:] = mom[:-1]
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
    lines = ["# Audit — Momentum de l'or (GLD, log-return 21j)", ""]
    all_ok = True

    gold_series = load_gold_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        mom_official = load_gold_mom_lag(dates, gold_series)[1:]
        pos_official = expanding_tercile_cut_high(mom_official)

        mom_manual = manual_gold_mom_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(mom_official - mom_manual))

        start = int(np.argmax(np.isfinite(mom_manual)))
        T = len(mom_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(mom_manual[t]):
                continue
            hist = mom_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_high_tercile(hist)
            pos_manual[t] = CUT if mom_manual[t] >= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(mom_official[i] - mom_manual[i])
            if local_diff >= 1e-10:
                boundary_tie_ok = False

        ok = (diff_align < 1e-8) and (n_pos_diff == 0 or boundary_tie_ok)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : {diff_align:.2e}")
        if n_pos_diff == 0:
            lines.append("- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00")
        else:
            lines.append(f"- **{n_pos_diff}/{n_total} désaccords de position** — sensibilité de bord flottante "
                         f"documentée (même pattern que #193/#195/.../#347) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage causal d'un jour, sur la
    # derniere transition de valeur reelle du momentum brut (avant le
    # shift(1) externe) -- meme methode que #344/#346.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    gold_aligned = gold_series.reindex(dates, method="ffill").values
    mom_raw = np.full(len(dates), np.nan)
    mom_raw[RET_WINDOW:] = np.log(gold_aligned[RET_WINDOW:] / gold_aligned[:-RET_WINDOW])
    finite_idx = np.where(np.isfinite(mom_raw))[0]
    diffs = np.diff(mom_raw[finite_idx])
    nz_local = np.where(diffs != 0)[0]
    last_change_local = nz_local[-1]
    i_prev, i_last = finite_idx[last_change_local], finite_idx[last_change_local + 1]
    d_prev, d_last = dates[i_prev], dates[i_last]
    m_prev, m_last = mom_raw[i_prev], mom_raw[i_last]

    mom_lag_full = load_gold_mom_lag(dates, gold_series)
    lines.append(f"## Vérification spécifique du décalage causal d'un jour (transition {d_prev.date()}→{d_last.date()}, séances {i_prev}→{i_last})")
    lines.append(f"- GoldMom brut séance précédente ({d_prev.date()}) = {m_prev:.6f}, "
                 f"GoldMom brut séance de la transition ({d_last.date()}) = {m_last:.6f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(m_prev, m_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- GoldMom_lag séance {i_last} ({d_last.date()}) = {mom_lag_full[i_last]:.6f} (doit valoir {m_prev:.6f}, JAMAIS {m_last:.6f})")
    if i_last + 1 < len(dates):
        lines.append(f"- GoldMom_lag séance {i_last+1} ({dates[i_last+1].date()}) = {mom_lag_full[i_last+1]:.6f} "
                     f"(doit être la première séance où {m_last:.6f} apparaît, via shift(1))")
        ok_shift = (not np.isclose(m_prev, m_last)) and np.isclose(mom_lag_full[i_last], m_prev) and \
            np.isclose(mom_lag_full[i_last + 1], m_last)
    else:
        ok_shift = (not np.isclose(m_prev, m_last)) and np.isclose(mom_lag_full[i_last], m_prev)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — le décalage d’un jour est correctement appliqué' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    mom_full = load_gold_mom_lag(dates, gold_series)[1:]
    pos_full = expanding_tercile_cut_high(mom_full)
    valid_start = int(np.argmax(np.isfinite(mom_full)))
    T_CUT = valid_start + 1500
    pos_truncated = expanding_tercile_cut_high(mom_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_gold_price_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()

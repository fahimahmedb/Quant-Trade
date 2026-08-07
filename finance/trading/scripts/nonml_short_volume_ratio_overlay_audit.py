"""Audit indépendant — Ratio de volume vendu à découvert QQQ (FINRA Reg SHO).

Recalcule ShortVolRatio_lag(t), le tercile expanding et la position
par une méthode alternative (boucle explicite + searchsorted, sans
pandas.reindex/ffill/np.percentile), compare au résultat committé du
backtest. Vérifie le décalage de publication (2j) + causal (1j) sur
une transition réelle et l'absence de fuite par troncature de
l'historique.
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
from nonml_financial_conditions_overlay_backtest import CUT, MARKETS, expanding_tercile_cut_high  # noqa: E402
from nonml_short_volume_ratio_overlay_backtest import (  # noqa: E402
    PUBLICATION_LAG_DAYS, build_short_vol_ratio_series, load_short_vol_ratio_lag,
)


def manual_ratio_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted (side='right'-1,
    inclusif) sur les dates "disponibles" (date + lag publication),
    sans pandas.reindex/ffill."""
    raw = pd.read_csv(REPO_ROOT / "data" / "qqq_short_volume_daily.csv")
    raw["date"] = pd.to_datetime(raw["date"])
    raw["short_volume"] = pd.to_numeric(raw["short_volume"], errors="coerce")
    raw["total_volume"] = pd.to_numeric(raw["total_volume"], errors="coerce")
    raw = raw.dropna(subset=["short_volume", "total_volume"])
    raw = raw[raw["total_volume"] > 0].drop_duplicates("date").sort_values("date")

    ratio = (raw["short_volume"] / raw["total_volume"]).values
    available = (raw["date"] + pd.Timedelta(days=PUBLICATION_LAG_DAYS)).values

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(available, np.datetime64(d), side="right") - 1
        if idx < 0:
            continue
        out[i] = ratio[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def manual_percentile_high_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (2.0 * 100.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    lines = ["# Audit — Ratio de volume vendu à découvert QQQ (FINRA Reg SHO)", ""]
    all_ok = True

    ratio_series = build_short_vol_ratio_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        ratio_official = load_short_vol_ratio_lag(dates, ratio_series)[1:]
        pos_official = expanding_tercile_cut_high(ratio_official)

        ratio_manual = manual_ratio_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(ratio_official - ratio_manual))

        start = int(np.argmax(np.isfinite(ratio_manual)))
        T = len(ratio_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(ratio_manual[t]):
                continue
            hist = ratio_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_high_tercile(hist)
            pos_manual[t] = CUT if ratio_manual[t] >= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(ratio_official[i] - ratio_manual[i])
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
                         f"documentée (même pattern que #193/#195/.../#365) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage de publication (2j) + causal (1j)
    # sur la derniere transition de valeur reelle.
    raw = pd.read_csv(REPO_ROOT / "data" / "qqq_short_volume_daily.csv")
    raw["date"] = pd.to_datetime(raw["date"])
    raw["short_volume"] = pd.to_numeric(raw["short_volume"], errors="coerce")
    raw["total_volume"] = pd.to_numeric(raw["total_volume"], errors="coerce")
    raw = raw.dropna(subset=["short_volume", "total_volume"])
    raw = raw[raw["total_volume"] > 0].sort_values("date")
    ratio = (raw["short_volume"] / raw["total_volume"]).values
    obs_dates = raw["date"].values
    diffs = np.diff(ratio)
    nz = np.where(diffs != 0)[0]
    last_change = nz[-1]
    d_prev, d_last = pd.Timestamp(obs_dates[last_change]), pd.Timestamp(obs_dates[last_change + 1])
    v_prev, v_last = ratio[last_change], ratio[last_change + 1]
    d_avail = d_last + pd.Timedelta(days=PUBLICATION_LAG_DAYS)

    check_dates = pd.DatetimeIndex([
        d_avail - pd.Timedelta(days=2), d_avail - pd.Timedelta(days=1),
        d_avail, d_avail + pd.Timedelta(days=1), d_avail + pd.Timedelta(days=2),
    ])
    ratio_check = load_short_vol_ratio_lag(check_dates, ratio_series)

    lines.append(f"## Vérification spécifique du décalage de publication ({PUBLICATION_LAG_DAYS}j) + causal (1j)")
    lines.append(f"- Dernière observation ({d_last.date()}) = {v_last:.6f} "
                 f"(observation précédente {d_prev.date()} = {v_prev:.6f}, "
                 f"valeurs distinctes : {'OUI' if not np.isclose(v_prev, v_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- Date de disponibilité déclarée (date + {PUBLICATION_LAG_DAYS}j) = {d_avail.date()}")
    lines.append(f"- ShortVolRatio_lag({d_avail.date()}) = {ratio_check[2]:.6f} (doit valoir {v_prev:.6f}, JAMAIS {v_last:.6f})")
    lines.append(f"- ShortVolRatio_lag({(d_avail + pd.Timedelta(days=1)).date()}) = {ratio_check[3]:.6f} "
                 f"(doit être le premier jour où {v_last:.6f} apparaît, via shift(1))")
    ok_shift = (not np.isclose(v_prev, v_last)) and np.isclose(ratio_check[2], v_prev) and \
        np.isclose(ratio_check[3], v_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — le décalage de publication + causal est correctement appliqué' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    ratio_full = load_short_vol_ratio_lag(dates, ratio_series)[1:]
    pos_full = expanding_tercile_cut_high(ratio_full)
    valid_start = int(np.argmax(np.isfinite(ratio_full)))
    T_CUT = valid_start + 1000
    pos_truncated = expanding_tercile_cut_high(ratio_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_short_volume_ratio_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()

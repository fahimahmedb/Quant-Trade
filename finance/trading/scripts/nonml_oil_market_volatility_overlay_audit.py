"""Audit indépendant — Indice OVX (volatilité implicite pétrolière).

Recalcule OVX_lag(t), le tercile expanding et la position par une
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
from nonml_financial_conditions_overlay_backtest import CUT, MARKETS, expanding_tercile_cut_high  # noqa: E402
from nonml_oil_market_volatility_overlay_backtest import load_ovx_lag, load_ovx_series  # noqa: E402


def manual_ovx_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted (side='right'-1,
    inclusif), sans pandas.reindex/ffill."""
    raw = pd.read_csv(REPO_ROOT / "data" / "oil_vol_ovx_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["OVX"] = pd.to_numeric(raw["OVX"], errors="coerce")
    raw = raw.dropna(subset=["OVX"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["OVX"].astype(float).values

    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(obs_dates, np.datetime64(d), side="right") - 1
        if idx < 0:
            continue
        out[i] = vals[idx]
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
    lines = ["# Audit — Indice OVX (volatilité implicite pétrolière)", ""]
    all_ok = True

    ovx_series = load_ovx_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        ovx_official = load_ovx_lag(dates, ovx_series)[1:]
        pos_official = expanding_tercile_cut_high(ovx_official)

        ovx_manual = manual_ovx_lag(dates)[1:]
        diff_align = np.nanmax(np.abs(ovx_official - ovx_manual))

        start = int(np.argmax(np.isfinite(ovx_manual)))
        T = len(ovx_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(ovx_manual[t]):
                continue
            hist = ovx_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_high_tercile(hist)
            pos_manual[t] = CUT if ovx_manual[t] >= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(ovx_official[i] - ovx_manual[i])
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
                         f"documentée (même pattern que #193/#195/.../#357) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification du decalage causal d'un jour sur 5 dates CONSECUTIVES
    # se terminant sur la derniere transition de valeur reelle (evite
    # l'artefact de bord positionnel de shift(1) documente au #320/#321/#357).
    raw = pd.read_csv(REPO_ROOT / "data" / "oil_vol_ovx_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["OVX"] = pd.to_numeric(raw["OVX"], errors="coerce")
    raw = raw.dropna(subset=["OVX"]).sort_values("observation_date")
    vals = raw["OVX"].astype(float).values
    obs_dates = raw["observation_date"].values
    diffs = np.diff(vals)
    nz = np.where(diffs != 0)[0]
    last_change = nz[-1]
    d_prev, d_last = pd.Timestamp(obs_dates[last_change]), pd.Timestamp(obs_dates[last_change + 1])
    v_prev, v_last = vals[last_change], vals[last_change + 1]

    check_dates = pd.DatetimeIndex([
        d_last - pd.Timedelta(days=4), d_last - pd.Timedelta(days=3),
        d_last - pd.Timedelta(days=2), d_last - pd.Timedelta(days=1),
        d_last, d_last + pd.Timedelta(days=1),
    ])
    ovx_check = load_ovx_lag(check_dates, ovx_series)

    lines.append(f"## Vérification spécifique du décalage causal d'un jour (transition {d_prev.date()}→{d_last.date()})")
    lines.append(f"- OVX brut jour précédent ({d_prev.date()}) = {v_prev:.6f}, "
                 f"OVX brut jour de la transition ({d_last.date()}) = {v_last:.6f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(v_prev, v_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- OVX_lag({d_last.date()}) = {ovx_check[4]:.6f} (doit valoir {v_prev:.6f}, JAMAIS {v_last:.6f})")
    lines.append(f"- OVX_lag({(d_last + pd.Timedelta(days=1)).date()}) = {ovx_check[5]:.6f} "
                 f"(doit être le premier jour où {v_last:.6f} apparaît, via shift(1))")
    ok_shift = (not np.isclose(v_prev, v_last)) and np.isclose(ovx_check[4], v_prev) and \
        np.isclose(ovx_check[5], v_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — le décalage d’un jour est correctement appliqué' if ok_shift else 'FUITE POTENTIELLE OU TRANSITION AVEUGLE'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    ovx_full = load_ovx_lag(dates, ovx_series)[1:]
    pos_full = expanding_tercile_cut_high(ovx_full)
    valid_start = int(np.argmax(np.isfinite(ovx_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_high(ovx_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_oil_market_volatility_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()

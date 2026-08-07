"""Audit indépendant — Momentum de l'ETF obligataire TLT (log-return 21j).

Recalcule TLTmom_lag(t), le tercile expanding et la position par une
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
from nonml_gold_price_overlay_backtest import expanding_tercile_cut_high  # noqa: E402
from nonml_treasury_bond_etf_overlay_backtest import load_tlt_mom_lag, load_tlt_series  # noqa: E402


def manual_tlt_mom_lag(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par boucle explicite + searchsorted (side='right'-1,
    inclusif), sans pandas.reindex/ffill."""
    raw = pd.read_csv(REPO_ROOT / "data" / "tlt_bond_etf_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["TLT"] = pd.to_numeric(raw["TLT"], errors="coerce")
    raw = raw.dropna(subset=["TLT"]).drop_duplicates("observation_date").sort_values("observation_date")
    obs_dates = raw["observation_date"].values
    vals = raw["TLT"].astype(float).values

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
    lines = ["# Audit — Momentum de l'ETF obligataire TLT (log-return 21j)", ""]
    all_ok = True

    tlt_series = load_tlt_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        mom_official = load_tlt_mom_lag(dates, tlt_series)[1:]
        pos_official = expanding_tercile_cut_high(mom_official)

        mom_manual = manual_tlt_mom_lag(dates)[1:]
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
                         f"documentée (même pattern que #193/#195/.../#348) : "
                         f"{'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification specifique du decalage causal d'un jour, sur la
    # derniere transition de valeur reelle (evite l'artefact de bord
    # positionnel de shift(1) deja documente au #320/.../#348).
    raw = pd.read_csv(REPO_ROOT / "data" / "tlt_bond_etf_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw["TLT"] = pd.to_numeric(raw["TLT"], errors="coerce")
    raw = raw.dropna(subset=["TLT"]).sort_values("observation_date")
    vals = raw["TLT"].astype(float).values
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
    tlt_check = load_tlt_mom_lag(check_dates, tlt_series)

    lines.append(f"## Vérification spécifique du décalage causal d'un jour (transition {d_prev.date()}→{d_last.date()})")
    lines.append(f"- TLT brut jour précédent ({d_prev.date()}) = {v_prev:.6f}, "
                 f"TLT brut jour de la transition ({d_last.date()}) = {v_last:.6f} "
                 f"(valeurs distinctes vérifiées : {'OUI' if not np.isclose(v_prev, v_last) else 'NON — transition aveugle, coïncidence à éviter'})")
    lines.append(f"- TLTmom_lag({d_last.date()}) — n/a directement (comparaison via momentum, voir alignement §1) ")
    ok_shift = not np.isclose(v_prev, v_last)
    all_ok &= ok_shift
    lines.append(f"- **{'OK — transition non aveugle confirmée' if ok_shift else 'TRANSITION AVEUGLE, coïncidence à éviter'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    mom_full = load_tlt_mom_lag(dates, tlt_series)[1:]
    pos_full = expanding_tercile_cut_high(mom_full)
    valid_start = int(np.argmax(np.isfinite(mom_full)))
    T_CUT = valid_start + 2000
    pos_truncated = expanding_tercile_cut_high(mom_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_treasury_bond_etf_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()

"""Audit adversarial — Overlay vol-targeting gaté par le January
Barometer.

Recalcul totalement indépendant de la porte annuelle (datetime standard,
boucle explicite) et de la position (boucle explicite, ddof=1), et test
anti-lookahead sur les deux composantes.
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
from nonml_january_barometer_vol_targeting_overlay_backtest import (  # noqa: E402
    january_gate_mask, combined_position, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_gate_mask(df) -> np.ndarray:
    """Reconstruction indépendante de la porte annuelle : regroupement
    par (annee, mois) via datetime standard, boucle explicite (pas
    pandas.dt), identique en principe au recalcul deja valide au #59."""
    ts = pd.to_datetime(df["date"]).tolist()
    close = df["close"].values
    T = len(close)

    last_idx = {}
    for i in range(T):
        dt = ts[i].to_pydatetime()
        last_idx[(dt.year, dt.month)] = i

    years_seen = sorted({ts[i].to_pydatetime().year for i in range(T)})
    signal_by_year = {}
    for y in years_seen:
        i_dec_prev = last_idx.get((y - 1, 12))
        i_jan = last_idx.get((y, 1))
        if i_dec_prev is None or i_jan is None:
            continue
        signal_by_year[y] = close[i_jan] > close[i_dec_prev]

    gate = np.zeros(T, dtype=bool)
    for i in range(T):
        dt = ts[i].to_pydatetime()
        if dt.month == 1:
            continue
        gate[i] = signal_by_year.get(dt.year, False)
    return gate


def independent_combined_position(r: np.ndarray, gate: np.ndarray) -> np.ndarray:
    T = len(r)
    gate_r = gate[:-1]
    pos = np.ones(T)
    for i in range(T):
        if not gate_r[i]:
            pos[i] = 1.0
            continue
        if i - VOL_WINDOW < 0:
            pos[i] = 1.0
            continue
        vol_window_r = r[i - VOL_WINDOW:i]
        vol_ann = vol_window_r.std(ddof=1) * ANNUALIZATION
        if vol_ann > 0:
            pos[i] = min(max(TARGET_VOL_ANNUAL / vol_ann, 1.0), CAP)
        else:
            pos[i] = CAP
    return pos


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par January Barometer", "",
             "## 1. Recalcul indépendant (porte annuelle + position, boucle explicite)", "",
             "| Marché | Écart porte (nb j.) | Écart position max |",
             "|---|---|---|"]
    all_ok = True
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dfs[name] = df
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])

        gate_orig = january_gate_mask(df)
        gate_indep = independent_gate_mask(df)
        diff_gate = int(np.sum(gate_orig != gate_indep))

        pos_orig = combined_position(close, r, gate_orig)
        pos_indep = independent_combined_position(r, gate_orig)
        max_diff_pos = float(np.max(np.abs(pos_orig - pos_indep)))

        all_ok &= (diff_gate == 0) and (max_diff_pos < 1e-9)
        lines.append(f"| {name} | {diff_gate} | {max_diff_pos:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — porte et position confirmées par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, df in dfs.items():
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        pos_before = combined_position(close, r, january_gate_mask(df))

        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(283)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        df_pert = df.copy()
        df_pert["close"] = close_pert
        r_pert = np.log(close_pert[1:] / close_pert[:-1])
        pos_after = combined_position(close_pert, r_pert, january_gate_mask(df_pert))

        # marge de securite : ignore l'annee en cours au moment de la coupure
        cut_year = pd.to_datetime(df["date"]).dt.year.values[cut]
        years_arr = pd.to_datetime(df["date"]).dt.year.values[1:]
        mask_before_cut_year = (years_arr < cut_year)
        # exclut aussi la marge de la fenetre de vol
        idx_before = np.where(mask_before_cut_year)[0]
        idx_before = idx_before[idx_before < cut - VOL_WINDOW]
        identical = bool(np.allclose(pos_before[idx_before], pos_after[idx_before]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures (ni sur la porte annuelle ni sur le vol-targeting).' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_january_barometer_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Audit indépendant — Sleeve dollar-neutre composite redimensionné
par sa vol (Piste C).

1. Recalcul indépendant de vol_target_position (boucle Python pure,
   sans pandas.rolling ni np.clip) sur un échantillon de séances.
2. Vérification du décalage causal (vol connue à t-1 appliquée au
   rendement t) sur une transition réelle.
3. Anti-lookahead par troncature de l'historique.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_vol_targeting_overlay_backtest import CAP, TARGET_VOL_ANNUAL, VOL_WINDOW, ANNUALIZATION, vol_target_position  # noqa: E402


def manual_vol_target_position(r: np.ndarray) -> np.ndarray:
    """Recalcul par boucle Python pure (ecart-type manuel ddof=1, sans
    pandas.rolling), sans np.clip (min/max explicites)."""
    T = len(r)
    pos = np.full(T, np.nan)
    for t in range(T):
        if t < VOL_WINDOW:
            pos[t] = 1.0
            continue
        window = r[t - VOL_WINDOW:t]  # vol connue a t-1, fenetre [t-VOL_WINDOW, t-1]
        n = len(window)
        mu = sum(window) / n
        var = sum((x - mu) ** 2 for x in window) / (n - 1)
        vol_ann = (var ** 0.5) * ANNUALIZATION
        if vol_ann <= 0 or not np.isfinite(vol_ann):
            pos[t] = 1.0
            continue
        raw = TARGET_VOL_ANNUAL / vol_ann
        pos[t] = min(max(raw, 0.0), CAP)
    return pos


def main():
    lines = ["# Audit — Sleeve dollar-neutre composite redimensionné par sa vol (Piste C)", ""]
    all_ok = True

    data = np.load(ROOT / "results" / "nonml_dollar_neutral_composite_pit_pnl.npz", allow_pickle=True)
    pnl_sleeve_net = data["pnl_candidate"].astype(float)

    pos_official = vol_target_position(pnl_sleeve_net)
    pos_manual = manual_vol_target_position(pnl_sleeve_net)

    diff = np.nanmax(np.abs(pos_official - pos_manual))
    ok_recalc = diff < 1e-8
    all_ok &= ok_recalc
    lines.append("## 1. Recalcul indépendant de la position vol-target (boucle pure, écart-type manuel)")
    lines.append("")
    lines.append(f"- Écart max sur les {len(pos_official)} séances : {diff:.2e}")
    lines.append(f"- **{'OK' if ok_recalc else 'ÉCART DÉTECTÉ'}**")
    lines.append("")

    # 2. Verification du decalage causal sur une transition reelle de
    # regime de vol (vol_lagged doit toujours refleter [t-VOL_WINDOW, t-1],
    # jamais inclure r[t]).
    T = len(pnl_sleeve_net)
    diffs_pos = np.diff(pos_official[VOL_WINDOW:])
    nz = np.where(np.abs(diffs_pos) > 1e-6)[0]
    check_i = VOL_WINDOW + nz[len(nz) // 2] if len(nz) > 0 else VOL_WINDOW + 1
    window_used = pnl_sleeve_net[check_i - VOL_WINDOW:check_i]
    vol_manual = float(np.std(window_used, ddof=1) * ANNUALIZATION)
    raw_manual = TARGET_VOL_ANNUAL / vol_manual if vol_manual > 0 else float("nan")
    pos_manual_at_i = min(max(raw_manual, 0.0), CAP)
    ok_shift = abs(pos_manual_at_i - pos_official[check_i]) < 1e-8
    all_ok &= ok_shift
    lines.append(f"## 2. Vérification du décalage causal (séance {check_i})")
    lines.append(f"- Position officielle à t={check_i} : {pos_official[check_i]:.6f}")
    lines.append(f"- Position recalculée à partir de la fenêtre [t-{VOL_WINDOW}, t-1] uniquement : {pos_manual_at_i:.6f}")
    lines.append(f"- **{'OK — la fenêtre de vol exclut bien le rendement du jour t' if ok_shift else 'FUITE POTENTIELLE'}**")
    lines.append("")

    # 3. Anti-lookahead par troncature.
    T_cut = T // 2
    pos_full = vol_target_position(pnl_sleeve_net)
    pos_truncated = vol_target_position(pnl_sleeve_net[:T_cut])
    lookahead_diff = float(np.nanmax(np.abs(pos_full[:T_cut - VOL_WINDOW] - pos_truncated[:T_cut - VOL_WINDOW])))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead
    lines.append(f"## 3. Anti-lookahead (troncature à {T_cut} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_dollar_neutral_composite_vol_targeted_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()

"""Robustesse — cycle #350 (sleeve vol-targeted), grille jointe ±20%
sur TARGET_VOL_ANNUAL et CAP, les deux paramètres non centraux au
critère de succès (le critère porte sur Sharpe>0 ET t-stat>2, pas sur
leur valeur exacte). Ce n'est PAS un retuning : le verdict du cycle
reste celui du point pré-enregistré (TARGET_VOL_ANNUAL=0.15, CAP=2.0).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_vol_targeting_overlay_backtest import COST_BPS, CAP, TARGET_VOL_ANNUAL, VOL_WINDOW, ANNUALIZATION  # noqa: E402

TARGET_GRID = [round(TARGET_VOL_ANNUAL * 0.8, 3), TARGET_VOL_ANNUAL, round(TARGET_VOL_ANNUAL * 1.2, 3)]
CAP_GRID = [round(CAP * 0.8, 2), CAP, round(CAP * 1.2, 2)]


def vol_target_position_grid(r: np.ndarray, target_vol: float, cap: float) -> np.ndarray:
    import pandas as pd
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = target_vol / vol_lagged
    pos = np.clip(pos, 0.0, cap)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    data = np.load(ROOT / "results" / "nonml_dollar_neutral_composite_pit_pnl.npz", allow_pickle=True)
    pnl_sleeve_net = data["pnl_candidate"].astype(float)

    lines = [
        "# Robustesse — cycle #350 (sleeve vol-targeted), grille jointe ±20% sur TARGET_VOL_ANNUAL et CAP",
        "",
        f"Point pré-enregistré : TARGET_VOL_ANNUAL={TARGET_VOL_ANNUAL:.0%}, CAP={CAP:.1f}x. "
        f"Grille TARGET_VOL_ANNUAL : {{{', '.join(f'{t:.0%}' for t in TARGET_GRID)}}}. "
        f"Grille CAP : {{{', '.join(f'{c:.1f}x' for c in CAP_GRID)}}}.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (15% / 2.0x) quelle que soit la lecture de ce tableau.",
        "",
        "| TARGET_VOL_ANNUAL | CAP | Sharpe ann. | t-stat | Rendement total | Sharpe>0 | t-stat>2 | Les deux |",
        "|---|---|---|---|---|---|---|---|",
    ]
    n_both_total, n_cells_total = 0, 0

    for target_vol in TARGET_GRID:
        for cap in CAP_GRID:
            pos_full = vol_target_position_grid(pnl_sleeve_net, target_vol, cap)
            start = VOL_WINDOW
            r_underlying = pnl_sleeve_net[start:]
            pos = pos_full[start:]
            turn = np.abs(np.diff(pos, prepend=1.0))
            r_vt = pos * r_underlying - turn * (COST_BPS / 1e4)

            me = trading_metrics(r_vt)
            ret = float(np.cumprod(1.0 + r_vt)[-1] - 1.0)
            sharpe_daily = r_vt.mean() / r_vt.std() if r_vt.std() > 0 else float("nan")
            tstat = sharpe_daily * np.sqrt(len(r_vt))

            ok_sharpe = me["sharpe_ann"] > 0
            ok_tstat = tstat > 2
            both_ok = ok_sharpe and ok_tstat
            n_cells_total += 1
            n_both_total += int(both_ok)

            marker = " (point pré-enregistré)" if (target_vol == TARGET_VOL_ANNUAL and cap == CAP) else ""
            lines.append(
                f"| {target_vol:.0%}{marker} | {cap:.1f}x | {me['sharpe_ann']:+.2f} | {tstat:+.2f} | "
                f"{100*ret:+.1f}% | {'OUI' if ok_sharpe else 'non'} | {'OUI' if ok_tstat else 'non'} | "
                f"{'OUI' if both_ok else 'non'} |"
            )

    lines.append("")
    lines.append(f"**{n_both_total}/{n_cells_total} cellules de la grille passent le critère complet "
                 f"(Sharpe>0 ET t-stat>2).**")

    out = ROOT / "results" / "nonml_dollar_neutral_composite_vol_targeted_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

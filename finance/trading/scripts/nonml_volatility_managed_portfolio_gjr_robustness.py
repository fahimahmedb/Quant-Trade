"""Robustesse — portefeuille volatility-managed GJR-t (cycle #165).

Grille de PERTURBATION ±20 % autour du point pré-enregistré (TARGET_VOL = 20 %,
CAP = 2.0x), annoncée au §8 du PREREG AVANT tout calcul.

**Ce n'est PAS un retuning** : le verdict du cycle reste celui du point
pré-enregistré 20 %/2.0x, quoi que montre cette grille. Son seul rôle est de
répondre à la question « le résultat tient-il sur un plateau, ou est-il un
point isolé ? ». Aucune valeur de la grille ne peut devenir le nouveau
paramètre de référence.

Les prévisions de volatilité ne dépendent NI de TARGET_VOL NI de CAP : le
walk-forward GJR-t n'est calculé qu'une seule fois, la grille ne fait que
re-mapper la même série de prévisions en positions.
"""
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import vol_target_exposure, walk_forward_vol_forecast  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_volatility_managed_portfolio_gjr_backtest import (  # noqa: E402
    CAP, COST_BPS, MARKET_FILE, REFIT_EVERY, T0, TARGET_VOL_ANNUAL_PCT,
)

# Perturbation +/-20 % declaree au PREREG (§8), figee avant tout calcul.
TARGET_GRID = [round(TARGET_VOL_ANNUAL_PCT * 0.8, 1), TARGET_VOL_ANNUAL_PCT,
               round(TARGET_VOL_ANNUAL_PCT * 1.2, 1)]
CAP_GRID = [round(CAP * 0.8, 2), CAP, round(CAP * 1.2, 2)]


def evaluate(vol_fcst, r_t, target, cap):
    pos = vol_target_exposure(vol_fcst, target, cap)[T0:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    me = trading_metrics(pnl_ov)
    ret = float(np.cumprod(1.0 + pnl_ov)[-1] - 1.0)
    return me, ret, pos


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    r_pct = log_returns_pct(df).values
    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    vol_fcst = fc["vol_fcst"]
    r_t = r_pct[T0:] / 100.0

    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh = trading_metrics(pnl_bh)
    ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)

    lines = [
        "# Robustesse — portefeuille volatility-managed GJR-t (perturbation ±20 %)",
        "",
        f"Point pré-enregistré : TARGET_VOL = {TARGET_VOL_ANNUAL_PCT:.0f} %, CAP = {CAP}x. "
        f"Grille annoncée au §8 du PREREG avant tout calcul : "
        f"TARGET_VOL ∈ {{{', '.join(f'{t:.0f} %' for t in TARGET_GRID)}}} × "
        f"CAP ∈ {{{', '.join(f'{c}x' for c in CAP_GRID)}}}.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré quelle que soit la lecture de ce tableau.",
        "",
        f"Référence Buy & Hold sur la même fenêtre OOS ({len(r_t)} séances) : "
        f"Sharpe {me_bh['sharpe_ann']:+.2f}, rendement {100 * ret_bh:+.1f} %, "
        f"MDD {me_bh['max_drawdown_pct']:.1f} %.",
        "",
        "| TARGET_VOL | CAP | Expo. moy. | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH | Les deux |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    n_both = 0
    for target in TARGET_GRID:
        for cap in CAP_GRID:
            me, ret, pos = evaluate(vol_fcst, r_t, target, cap)
            ok_s = me["sharpe_ann"] > me_bh["sharpe_ann"]
            ok_r = ret > ret_bh
            both = ok_s and ok_r
            n_both += int(both)
            star = " **(pré-enregistré)**" if (target == TARGET_VOL_ANNUAL_PCT and cap == CAP) else ""
            lines.append(
                f"| {target:.0f} %{star} | {cap}x | {pos.mean():.2f}x | {me['sharpe_ann']:+.2f} | "
                f"{100 * ret:+.1f}% | {me['max_drawdown_pct']:.1f}% | {'OUI' if ok_s else 'non'} | "
                f"{'OUI' if ok_r else 'non'} | {'OUI' if both else 'non'} |"
            )
    n_cells = len(TARGET_GRID) * len(CAP_GRID)
    lines += [
        "",
        f"**{n_both}/{n_cells} combinaisons de la grille battent Buy & Hold sur les DEUX jambes.**",
        "",
        "Lecture : un plateau (toutes ou presque toutes les cellules) indique un mécanisme "
        "peu sensible au calibrage ; quelques cellules isolées indiqueraient au contraire "
        "que le point pré-enregistré doit sa réussite à une coïncidence de paramétrage. "
        "Cette grille ne modifie en aucun cas le verdict du cycle.",
    ]

    out = ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

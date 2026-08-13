"""Backtest — Overlay vol-targeting gaté par un régime de volatilité
réalisée FAIBLE (spécification pré-enregistrée dans
PREREG_lowvol_regime_vol_targeting_overlay.md, committée avant ce
script). Troisième type de porte hiérarchique (tendance #47, calendrier
#54, breadth #57), ici auto-référentielle (dérivée de la vol elle-même).
n_trials=1, aucune dépendance ML. Règle de succès renforcée.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
MEDIAN_WINDOW = 252
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def combined_position(r: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (longueur T-1). Renvoie la position
    pour chaque rendement de r : clip(vol_cible/vol_lagged(t), 1.0, CAP)
    si vol_lagged(t) < mediane glissante de vol_lagged (regime de vol
    faible), 1.0 sinon."""
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan

    # mediane glissante calculee UNIQUEMENT sur des valeurs de vol_lagged
    # (deja causales : vol_lagged[t] ne depend que de r[..t-2]) -> aucune
    # fuite supplementaire possible par construction.
    median_vol = pd.Series(vol_lagged).rolling(MEDIAN_WINDOW).median().values
    gate = vol_lagged < median_vol

    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    pos = np.where(gate, vt_exposure, 1.0)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    lines = [
        "# Résultat — Overlay vol-targeting gaté par un régime de volatilité réalisée faible (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si vol_réalisée(t-1) < médiane glissante {MEDIAN_WINDOW}j de vol_réalisée, sinon 1.0x.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])

        pos_full = combined_position(bh_full)
        start = VOL_WINDOW + MEDIAN_WINDOW
        bh_t = bh_full[start:]
        pos = pos_full[start:]

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        # Sauvegarde INCONDITIONNELLE du P&L (cycle #424, lot 3). Ce script
        # boucle sur cinq marches ; on sauvegarde le NDX, marche de reference
        # du backlog -- convention tranchee au #416 pour `santa`. Aucune ligne
        # de calcul n'est modifiee par cet ajout.
        if fname == "nasdaq100_daily.txt":
            np.savez(ROOT / "results" / "nonml_lowvol_regime_vol_targeting_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t,
                     dates=pd.to_datetime(df["date"]).values[1:][start:],
                     cost_bps=COST_BPS)

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        gate_active = (pos > 1.0)
        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{100*gate_active.mean():.1f}% | {pos.mean():.2f}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_lowvol_regime_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

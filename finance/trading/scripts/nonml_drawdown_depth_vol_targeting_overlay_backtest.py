"""Backtest — Overlay vol-targeting gaté par la profondeur de drawdown
glissante (spécification pré-enregistrée dans
PREREG_drawdown_depth_vol_targeting_overlay.md, committée avant ce
script). Réutilise `drawdown_60` (Étape B) comme porte RELATIVE
(comparaison à sa propre médiane glissante), explicitement distincte du
#38 (seuil fixe 95%, remplacement direct de l'exposition, cause connue
de son échec de crise, #163). Mécanisme #46 INCHANGÉ. n_trials=1, aucune
dépendance ML. Règle de succès renforcée.
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
DD_WINDOW = 60
MEDIAN_WINDOW = 252
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def drawdown_60_lagged(close: np.ndarray) -> np.ndarray:
    """drawdown_60(t) = close(t)/rolling_max_60j(close)(t) - 1, decale
    d'un jour (t-1), aligne sur r = log(close[1:]/close[:-1]) (longueur T-1)."""
    roll_max = pd.Series(close).rolling(DD_WINDOW, min_periods=1).max().values
    dd = close / roll_max - 1.0
    lagged = np.roll(dd, 1)
    lagged[0] = np.nan
    return lagged[1:]


def healthy_dd_mask(close: np.ndarray) -> np.ndarray:
    """Porte = drawdown_60 (t-1) >= sa mediane glissante MEDIAN_WINDOW
    jours (drawdown moins profond que la norme recente = sain = amplifier)."""
    dd = drawdown_60_lagged(close)
    med = pd.Series(dd).rolling(MEDIAN_WINDOW).median().values
    gate = dd >= med
    return np.nan_to_num(gate, nan=0.0).astype(bool)


def combined_position(r: np.ndarray, gate: np.ndarray) -> np.ndarray:
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    pos = np.where(gate, vt_exposure, 1.0)
    return np.nan_to_num(pos, nan=1.0)


def main():
    lines = [
        "# Résultat — Overlay vol-targeting gaté par la profondeur de drawdown glissante "
        "(pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si le drawdown_{DD_WINDOW}j(t-1) est ≥ sa médiane glissante {MEDIAN_WINDOW}j (drawdown moins "
        f"profond que la norme récente), sinon 1.0x. Échantillon testable à partir de la "
        f"{DD_WINDOW + MEDIAN_WINDOW}e séance.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0
    start = DD_WINDOW + MEDIAN_WINDOW

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])
        if len(bh_full) <= start:
            continue

        gate = healthy_dd_mask(close)
        pos_full = combined_position(bh_full, gate)
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
            np.savez(ROOT / "results" / "nonml_drawdown_depth_vol_targeting_overlay_pnl.npz",
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

    out = ROOT / "results" / "nonml_drawdown_depth_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

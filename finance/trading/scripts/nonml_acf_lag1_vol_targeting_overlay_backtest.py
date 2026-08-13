"""Backtest — Overlay vol-targeting gaté par l'autocorrélation à un seul
retard (ACF lag-1) glissante (spécification pré-enregistrée dans
PREREG_acf_lag1_vol_targeting_overlay.md, committée avant ce script,
incluant la vérification préalable de redondance avec le VR(5) du #217,
ρ=0,87). n_trials=1, aucune dépendance ML. Règle de succès renforcée.
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
ACF_WINDOW = 252
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


def rolling_acf1_series(r: np.ndarray) -> np.ndarray:
    """ACF(1)(t) calculee sur r[t-ACF_WINDOW:t] (EXCLUANT r[t], fenetre
    strictement anterieure a t, donc causale)."""
    n = len(r)
    acf1 = np.full(n, np.nan)
    for k in range(ACF_WINDOW, n):
        window = r[k - ACF_WINDOW:k]
        dm = window - window.mean()
        den = np.sum(dm ** 2)
        if den <= 0:
            continue
        acf1[k] = np.sum(dm[1:] * dm[:-1]) / den
    return acf1


def trending_acf1_mask(r: np.ndarray) -> np.ndarray:
    """Porte = ACF(1) glissante >= sa mediane glissante MEDIAN_WINDOW
    jours (persistance immediate plus forte que la norme recente =
    regime tendanciel = amplifier). Deja causale par construction."""
    acf1 = rolling_acf1_series(r)
    med = pd.Series(acf1).rolling(MEDIAN_WINDOW).median().values
    gate = acf1 >= med
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
        "# Résultat — Overlay vol-targeting gaté par l'autocorrélation à un seul retard "
        "(ACF lag-1) glissante (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si l'ACF(1) glissante {ACF_WINDOW}j est ≥ sa médiane glissante {MEDIAN_WINDOW}j, "
        f"sinon 1.0x. Échantillon testable à partir de la {ACF_WINDOW + MEDIAN_WINDOW}e séance.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0
    start = ACF_WINDOW + MEDIAN_WINDOW

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

        gate = trending_acf1_mask(bh_full)
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
            np.savez(ROOT / "results" / "nonml_acf_lag1_vol_targeting_overlay_pnl.npz",
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

    out = ROOT / "results" / "nonml_acf_lag1_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

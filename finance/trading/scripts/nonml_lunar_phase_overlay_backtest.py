"""Backtest — Effet lunaire (Dichev & Janes 2003 ; Yuan, Zheng & Zhu
2006), overlay levé (spécification pré-enregistrée dans
PREREG_lunar_phase_overlay.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Règle de succès renforcée sur 5 marchés (≥4/5).

Phase lunaire calculée par formule astronomique standard (aucune
donnée externe, aucun fetch) : mois synodique ≈29,530588853 jours
depuis une nouvelle lune de référence connue et publique
(2000-01-06 18:14 UTC).
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
SYNODIC_MONTH = 29.530588853
NEW_MOON_REF = pd.Timestamp("2000-01-06 18:14:00")
WINDOW_DAYS = 7  # +/- jours calendaires autour de la nouvelle lune, repris de Yuan-Zheng-Zhu 2006

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def new_moon_window_mask(dates: pd.DatetimeIndex) -> np.ndarray:
    """True si la date est a <= WINDOW_DAYS jours calendaires de la
    nouvelle lune la plus proche (formule astronomique standard, pas
    de donnee externe)."""
    days_since_ref = (dates - NEW_MOON_REF).total_seconds().values / 86400.0
    phase_days = np.mod(days_since_ref, SYNODIC_MONTH)  # 0 = nouvelle lune exacte
    dist_to_new_moon = np.minimum(phase_days, SYNODIC_MONTH - phase_days)
    return dist_to_new_moon <= WINDOW_DAYS


def main():
    lines = [
        "# Résultat — Effet lunaire (nouvelle lune), overlay levé (pré-enregistré)",
        "",
        f"`position(t) = {CAP}x` si la date est dans une fenêtre de ±{WINDOW_DAYS} jours "
        f"calendaires autour de la nouvelle lune, `1.0x` sinon. Coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | % temps levé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
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
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        mask_full = new_moon_window_mask(dates)
        mask = mask_full[:-1]  # decision au jour t (deja connue avant l'ouverture, pas besoin de decalage : le calendrier est connu a l'avance)
        assert len(mask) == len(bh_full)

        pos = np.where(mask, CAP, 1.0)
        frac_lev = float(mask.mean())

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {len(bh_full)} | {100*frac_lev:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:]
            np.savez(ROOT / "results" / "nonml_lunar_phase_overlay_pnl.npz",
                     pos=pos, r_asset=bh_full, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_lunar_phase_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()

"""Backtest — Intersection Halloween ET année pré-électorale, overlay levé
(spécification pré-enregistrée dans
PREREG_halloween_preelection_and_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée sur 5 marchés
(≥4/5).

Réutilise `preelection_mask` du #30 (import direct, Règle 7) et la
formule Halloween du #17 (reproduite à l'identique, pas de fonction
séparée dans le script d'origine).
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
from prediction import trading_metrics  # noqa: E402
from nonml_presidential_cycle_overlay_backtest import preelection_mask  # noqa: E402

COST_BPS = 5.0
CAP = 2.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def main():
    lines = [
        "# Résultat — Intersection Halloween ET année pré-électorale, overlay levé (pré-enregistré)",
        "",
        f"Position 1.0x en permanence, CAP={CAP}x quand nov-avril (#17) ET année "
        f"pré-électorale (#30) coïncident. Coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | % temps actif | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.to_datetime(df["date"])
        bh_full = np.log(close[1:] / close[:-1])

        month = dates.dt.month.values[1:]
        is_winter = (month >= 11) | (month <= 4)
        pre_mask = preelection_mask(df["date"])[1:]
        mask = is_winter & pre_mask
        frac = float(mask.mean())

        pos = np.where(mask, CAP, 1.0)
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {100*frac:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:]
            np.savez(ROOT / "results" / "nonml_halloween_preelection_and_overlay_pnl.npz",
                     pos=pos, r_asset=bh_full, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_halloween_preelection_and_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()

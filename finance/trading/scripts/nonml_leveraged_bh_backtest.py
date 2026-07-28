"""Backtest — Buy & Hold levé en continu (spécification pré-enregistrée
dans PREREG_leveraged_bh.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Règle de succès renforcée.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

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
        "# Résultat — Buy & Hold levé en continu (pré-enregistré, règle renforcée)",
        "",
        f"Position = CAP={CAP}x constante, rebalancement quotidien implicite.",
        "",
        "| Marché | BH 1x Sharpe | BH 1x Rdt total | BH 1x MDD | Levé x2 Sharpe | Levé x2 Rdt total | Levé x2 MDD | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])

        pnl_bh = r.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        pnl_lev = CAP * r
        pnl_lev[0] -= CAP * (COST_BPS / 1e4)

        me_bh = trading_metrics(pnl_bh)
        me_lev = trading_metrics(pnl_lev)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

        sharpe_ok = me_lev["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_lev > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_lev['sharpe_ann']:+.2f} | {100*ret_lev:+.1f}% | {me_lev['max_drawdown_pct']:.1f}% | "
            f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où le levé x{CAP} bat Buy&Hold 1x en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")
    lines.append("")
    lines.append(
        "**Lecture honnête** : cohérent avec la discussion déjà eue avec l'utilisateur "
        "(décroissance par la volatilité) — un levier constant sans dimensionnement "
        "adaptatif dépend entièrement du ratio μ/σ² propre à chaque marché, pas d'un edge "
        "de timing."
    )

    out = ROOT / "results" / "nonml_leveraged_bh_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

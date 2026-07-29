"""Backtest — Stratégie "nuit seulement" (spécification pré-enregistrée
dans PREREG_overnight_vs_intraday.md, committée avant ce script).
Décomposition exacte du rendement quotidien en composante nuit
(clôture(t)→ouverture(t+1)) et jour (ouverture(t+1)→clôture(t+1)).
n_trials=1, aucune dépendance ML. Règle de succès renforcée.
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

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def decompose_returns(open_: np.ndarray, close: np.ndarray):
    """Renvoie (r_nuit, r_jour, r_bh), chacun de longueur T-1, avec
    r_nuit[t] = log(open[t+1]/close[t]), r_jour[t] = log(close[t+1]/open[t+1]),
    r_bh[t] = log(close[t+1]/close[t]) = r_nuit[t] + r_jour[t] (identite exacte)."""
    r_nuit = np.log(open_[1:] / close[:-1])
    r_jour = np.log(close[1:] / open_[1:])
    r_bh = np.log(close[1:] / close[:-1])
    return r_nuit, r_jour, r_bh


def main():
    lines = [
        "# Résultat — Stratégie nuit seulement vs Buy&Hold (pré-enregistré, règle renforcée)",
        "",
        "Position = 1.0x de la clôture(t) à l'ouverture(t+1), 0.0x pendant la séance "
        "(2 transactions/jour, 5 bps chacune). r_nuit(t)+r_jour(t)=r_BH(t) par construction.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Nuit Sharpe | Nuit Rdt total | Nuit MDD | "
        "Part nuit du rdt brut | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        open_ = df["open"].values
        close = df["close"].values

        r_nuit, r_jour, r_bh = decompose_returns(open_, close)

        # identite exacte : verification defensive (pas d'aggregation d'erreur)
        assert np.allclose(r_nuit + r_jour, r_bh, atol=1e-10), "decomposition nuit+jour != BH"

        pnl_night = r_nuit.copy()
        pnl_night -= 2 * (COST_BPS / 1e4)  # 2 transactions/jour, tous les jours
        pnl_bh = r_bh.copy()
        pnl_bh[0] -= COST_BPS / 1e4  # cout d'entree unique pour BH

        me_bh = trading_metrics(pnl_bh)
        me_night = trading_metrics(pnl_night)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_night = np.cumprod(1.0 + pnl_night)[-1] - 1.0

        r_nuit_sum = r_nuit.sum()
        r_bh_sum = r_bh.sum()
        part_nuit = 100 * r_nuit_sum / r_bh_sum if r_bh_sum != 0 else float("nan")

        sharpe_ok = me_night["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_night > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_night['sharpe_ann']:+.2f} | {100*ret_night:+.1f}% | {me_night['max_drawdown_pct']:.1f}% | "
            f"{part_nuit:.0f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où la stratégie nuit bat Buy&Hold en Sharpe ET "
                 f"rendement (critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_overnight_vs_intraday_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

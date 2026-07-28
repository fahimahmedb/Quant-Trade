"""Backtest — Overnight vs Intraday (spécification pré-enregistrée dans
PREREG_overnight_intraday.md, committée avant ce script). n_trials=1,
aucune dépendance ML.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]        # finance/trading
FINANCE_ROOT = ROOT.parent                          # finance
REPO_ROOT = FINANCE_ROOT.parent                     # Quant-Trade
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


def compute_returns(df):
    open_ = df["open"].values
    close = df["close"].values
    overnight = np.log(open_[1:] / close[:-1])   # close_{t-1} -> open_t
    intraday = np.log(close[1:] / open_[1:])     # open_t -> close_t
    bh = np.log(close[1:] / close[:-1])           # rendement close-to-close (Buy&Hold)
    return overnight, intraday, bh


def pnl_daily_transaction(returns: np.ndarray, cost_bps: float) -> np.ndarray:
    """Une transaction complete (ouverture+fermeture de position) CHAQUE
    jour -> cout = cost_bps a chaque jour (turnover=1 systematique)."""
    return returns - cost_bps / 1e4


def main():
    lines = [
        "# Résultat — Overnight vs Intraday (pré-enregistré, exécuté une fois)",
        "",
        "| Marché | BH Sharpe | Overnight Sharpe | Intraday Sharpe | Overnight bat BH ? | Intraday bat BH ? |",
        "|---|---|---|---|---|---|",
    ]
    n_markets = 0
    n_success = 0
    details = []

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        overnight, intraday, bh = compute_returns(df)

        pnl_bh = bh.copy()
        pnl_bh[0] -= COST_BPS / 1e4  # 1 seul cout d'entree sur toute la periode (Buy&Hold ne retourne jamais)
        pnl_on = pnl_daily_transaction(overnight, COST_BPS)
        pnl_id = pnl_daily_transaction(intraday, COST_BPS)

        me_bh = trading_metrics(pnl_bh)
        me_on = trading_metrics(pnl_on)
        me_id = trading_metrics(pnl_id)

        on_beats = me_on["sharpe_ann"] > me_bh["sharpe_ann"]
        id_beats = me_id["sharpe_ann"] > me_bh["sharpe_ann"]
        n_markets += 1
        if on_beats or id_beats:
            n_success += 1

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {me_on['sharpe_ann']:+.2f} | "
            f"{me_id['sharpe_ann']:+.2f} | {'OUI' if on_beats else 'non'} | "
            f"{'OUI' if id_beats else 'non'} |"
        )
        details.append({
            "market": name, "bh": me_bh["sharpe_ann"], "on": me_on["sharpe_ann"],
            "id": me_id["sharpe_ann"], "on_raw_mean": overnight.mean(), "id_raw_mean": intraday.mean(),
        })

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où Overnight-only OU Intraday-only bat Buy&Hold "
                 f"net de coûts (critère pré-enregistré : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")
    lines.append("")

    lines.append("## Décomposition brute (rendement moyen quotidien, avant coûts)")
    lines.append("")
    lines.append("| Marché | Rendement overnight moy./j (brut) | Rendement intraday moy./j (brut) |")
    lines.append("|---|---|---|")
    for d in details:
        lines.append(f"| {d['market']} | {100*d['on_raw_mean']:+.4f}% | {100*d['id_raw_mean']:+.4f}% |")

    lines.append("")
    lines.append(
        "**Lecture honnête** : Overnight-only et Intraday-only impliquent une transaction "
        "PAR JOUR (turnover maximal), contre 1 seule transaction pour Buy & Hold sur toute "
        "la période — un coût de 5bps/jour peut à lui seul dominer un rendement moyen "
        "quotidien qui est typiquement de l'ordre de quelques points de base. Si le critère "
        "échoue, ce n'est pas nécessairement parce que l'anomalie overnight n'existe pas "
        "(la décomposition brute ci-dessus le dit), mais parce qu'elle n'est pas monétisable "
        "à ce niveau de coûts de transaction avec un rebalancement quotidien — distinction "
        "importante, pas masquée."
    )

    out = ROOT / "results" / "nonml_overnight_intraday_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

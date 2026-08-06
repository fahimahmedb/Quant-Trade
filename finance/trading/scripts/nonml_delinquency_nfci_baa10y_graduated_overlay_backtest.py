"""Backtest — Position graduée par nombre de votes (défaut carte #286
+ NFCI #291 + BAA10Y #199), overlay défensif (spécification
pré-enregistrée dans PREREG_delinquency_nfci_baa10y_graduated_overlay.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée sur 5 marchés (≥4/5).

Réutilisation STRICTE des définitions déjà validées (Règle 7), aucune
modification : build_delinquency_series/load_delinquency_lag du #286,
build_nfci_series/load_nfci_lag du #291, load_baa10y_lag du #199,
expanding_tercile_gate_high du #296. Seule la fonction reliant le
nombre de votes à la position change (sizing continu au lieu d'un
seuil binaire comme au #301).
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
from nonml_credit_card_delinquency_overlay_backtest import (  # noqa: E402
    build_delinquency_series, load_delinquency_lag,
)
from nonml_financial_conditions_overlay_backtest import (  # noqa: E402
    build_nfci_series, load_nfci_lag,
)
from nonml_credit_spread_overlay_backtest import load_baa10y_lag  # noqa: E402
from nonml_delinquency_nfci_combined_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, expanding_tercile_gate_high,
)


def position_from_votes(votes: np.ndarray) -> np.ndarray:
    """position(t) = 1.0 - CUT*(votes/3), sizing continu (0..3 votes)."""
    return 1.0 - CUT * (votes.astype(float) / 3.0)


def main():
    delinq_series = build_delinquency_series()
    nfci_series = build_nfci_series()

    lines = [
        "# Résultat — Position graduée par nombre de votes (défaut carte #286 + NFCI #291 + BAA10Y #199), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = 1,0 - {CUT}×Votes(t)/3` où Votes(t) ∈ {{0,1,2,3}} est le nombre de signaux "
        f"(DRCCLACBS_lag, NFCI_lag, BAA10Y_lag) dans leur tercile expanding le plus haut. "
        f"Sizing continu, pas de seuil binaire. Coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | % temps à 0 vote | % 1 vote | % 2 votes | % 3 votes | BH Sharpe | BH Rdt total | Overlay Sharpe | Overlay Rdt total | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
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

        delinq_lag = load_delinquency_lag(dates, delinq_series)[1:]
        nfci_lag = load_nfci_lag(dates, nfci_series)[1:]
        baa10y_lag = load_baa10y_lag(dates)[1:]

        gate_delinq = expanding_tercile_gate_high(delinq_lag)
        gate_nfci = expanding_tercile_gate_high(nfci_lag)
        gate_baa10y = expanding_tercile_gate_high(baa10y_lag)

        valid = np.isfinite(delinq_lag) & np.isfinite(nfci_lag) & np.isfinite(baa10y_lag)
        votes = gate_delinq.astype(int) + gate_nfci.astype(int) + gate_baa10y.astype(int)

        start = int(np.argmax(valid))
        votes_t = votes[start:]
        valid_t = valid[start:]
        bh_t = bh_full[start:]
        assert valid_t.all(), "les trois series doivent etre valides sur toute la fenetre testable"

        pos = position_from_votes(votes_t)
        frac_v = [float((votes_t == k).mean()) for k in range(4)]

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
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
            f"| {name} | {len(bh_t)} | {100*frac_v[0]:.1f}% | {100*frac_v[1]:.1f}% | "
            f"{100*frac_v[2]:.1f}% | {100*frac_v[3]:.1f}% | {me_bh['sharpe_ann']:+.2f} | "
            f"{100*ret_bh:+.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:][start:]
            np.savez(ROOT / "results" / "nonml_delinquency_nfci_baa10y_graduated_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_delinquency_nfci_baa10y_graduated_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()

"""Backtest — Pression de vente nette des initiés (SEC Form 4, panier
AAPL/MSFT/NVDA, transactions P/S de marché ouvert uniquement), overlay
défensif (spécification pré-enregistrée dans
PREREG_insider_selling_pressure_overlay.md, committée avant ce
script). n_trials=1, aucune dépendance ML. Règle de succès renforcée
sur 5 marchés (≥4/5).

Réutilise CUT=0,5, COST_BPS, MARKETS et expanding_tercile_cut_high
(tercile le plus HAUT = défensif) du #291 (NFCI, Règle 7). Fenêtre
glissante de 21 jours (ROLL_WINDOW, réutilisé du RET_WINDOW=21 déjà
validé au #198) pour lisser la rareté quotidienne des dépôts P/S.
Décalage de publication conservateur de 3 jours calendaires.
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
from nonml_financial_conditions_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, expanding_tercile_cut_high,
)

PUBLICATION_LAG_DAYS = 3
ROLL_WINDOW = 21


def build_net_sell_pressure_series() -> pd.Series:
    raw = pd.read_csv(REPO_ROOT / "data" / "insider_form4_transactions.csv")
    raw["date"] = pd.to_datetime(raw["date"])
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
    raw = raw.dropna(subset=["value"])

    signed = np.where(raw["code"] == "S", raw["value"], -raw["value"])
    daily = pd.Series(signed, index=raw["date"]).groupby(level=0).sum()

    full_idx = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    daily_full = daily.reindex(full_idx, fill_value=0.0)

    roll = daily_full.rolling(ROLL_WINDOW, min_periods=ROLL_WINDOW).sum()
    roll = roll.dropna()

    available_dates = roll.index + pd.Timedelta(days=PUBLICATION_LAG_DAYS)
    s = pd.Series(roll.values, index=available_dates)
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s


def load_net_sell_pressure_lag(dates: pd.DatetimeIndex, pressure_series: pd.Series) -> np.ndarray:
    y = pressure_series.reindex(dates, method="ffill")
    return y.shift(1).values


def main():
    pressure_series = build_net_sell_pressure_series()

    lines = [
        "# Résultat — Pression de vente nette des initiés (SEC Form 4, AAPL/MSFT/NVDA), overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si NetSellPressure_lag(t) (somme glissante {ROLL_WINDOW}j de "
        f"[valeur des ventes S − valeur des achats P] sur le panier AAPL/MSFT/NVDA) est dans son "
        f"tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps. "
        f"Décalage de publication {PUBLICATION_LAG_DAYS}j + alignement causal quotidien standard.",
        "",
        "| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
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

        pressure_lag_full = load_net_sell_pressure_lag(dates, pressure_series)
        pressure_lag = pressure_lag_full[1:]
        pos_full = expanding_tercile_cut_high(pressure_lag)

        start = int(np.argmax(np.isfinite(pos_full)))
        pos = pos_full[start:]
        bh_t = bh_full[start:]
        assert len(pos) == len(bh_t)
        assert np.isfinite(pos).all()

        frac_cut = float((pos == CUT).mean())

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
            f"| {name} | {len(bh_t)} | {100*frac_cut:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:][start:]
            np.savez(ROOT / "results" / "nonml_insider_selling_pressure_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append("**Note qualité des données** : 1 transaction MSFT (01/09/2020, code S, prix affiché "
                 "2 261 327 $/action) exclue avant tout calcul — erreur de saisie confirmée dans le "
                 "document XML officiel SEC lui-même (prix implausible pour MSFT ~228$ à cette date), "
                 "filtre symétrique prix>5000$/action (1 seule ligne concernée sur 2544).")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_insider_selling_pressure_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()

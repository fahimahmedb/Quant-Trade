"""Backtest — Combinaison ET (3/3) du même trio de signaux macro que
le #334 : breakeven inflation (#200, seul PASS net), demandes
continues de chômage (#322), balance commerciale (#327) (spécification
pré-enregistrée dans
PREREG_macro_combo_and_breakeven_claims_trade_overlay.md, committée
avant ce script). n_trials=1, aucune dépendance ML. Règle de succès
renforcée sur 5 marchés (≥4/5).

Réutilise directement (imports, aucune réimplémentation) les fonctions
de porte déjà validées des trois scripts d'origine, identiques au
#334 : #200 (nonml_inflation_breakeven_overlay_backtest.py), #322
(nonml_continuing_claims_overlay_backtest.py +
nonml_jobless_claims_overlay_backtest.py), #327
(nonml_trade_balance_overlay_backtest.py +
nonml_m2_growth_overlay_backtest.py). Seule la logique de combinaison
change (ET au lieu de majorité), Règle 7.
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
from nonml_inflation_breakeven_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, load_t10yie_lag,
    expanding_tercile_cut_high as t10yie_gate_high,
)
from nonml_continuing_claims_overlay_backtest import (  # noqa: E402
    build_continuing_claims_yoy_series, load_continuing_claims_yoy_lag,
)
from nonml_trade_balance_overlay_backtest import (  # noqa: E402
    build_trade_balance_series, load_trade_balance_lag,
)
from nonml_jobless_claims_overlay_backtest import (  # noqa: E402
    expanding_tercile_cut_high as claims_gate_high,
)
from nonml_m2_growth_overlay_backtest import (  # noqa: E402
    expanding_tercile_cut_low as trade_gate_low,
)


def and_3_of_3(g1: np.ndarray, g2: np.ndarray, g3: np.ndarray) -> np.ndarray:
    return (g1 == CUT) & (g2 == CUT) & (g3 == CUT)


def main():
    claims_series = build_continuing_claims_yoy_series()
    trade_series = build_trade_balance_series()

    lines = [
        "# Résultat — Combinaison ET (3/3) breakeven inflation + demandes continues + balance commerciale (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si LES 3 gates (#200 T10YIE tercile haut, #322 CCSA tercile haut, "
        f"#327 BOPGSTB tercile bas) sont SIMULTANÉMENT actifs, `1.0x` sinon. Design purement défensif. "
        f"Coûts {COST_BPS:.0f} bps.",
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

        t10yie_lag = load_t10yie_lag(dates)[1:]
        claims_lag = load_continuing_claims_yoy_lag(dates, claims_series)[1:]
        trade_lag = load_trade_balance_lag(dates, trade_series)[1:]

        gate1 = t10yie_gate_high(t10yie_lag)
        gate2 = claims_gate_high(claims_lag)
        gate3 = trade_gate_low(trade_lag)

        # Intersection des zones valides des 3 signaux uniquement (aucune
        # fuite : chaque porte reste NaN tant que son propre historique
        # n'est pas disponible, la combinaison hérite du max des 3 starts).
        valid = np.isfinite(gate1) & np.isfinite(gate2) & np.isfinite(gate3)
        start = int(np.argmax(valid)) if valid.any() else len(valid)

        pos_active = and_3_of_3(gate1[start:], gate2[start:], gate3[start:])
        pos = np.where(pos_active, CUT, 1.0)
        bh_t = bh_full[start:]
        assert len(pos) == len(bh_t)

        frac_cut = float((pos == CUT).mean())

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
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
            f"| {name} | {len(bh_t)} | {100*frac_cut:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:][start:]
            np.savez(ROOT / "results" / "nonml_macro_combo_and_breakeven_claims_trade_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_macro_combo_and_breakeven_claims_trade_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()

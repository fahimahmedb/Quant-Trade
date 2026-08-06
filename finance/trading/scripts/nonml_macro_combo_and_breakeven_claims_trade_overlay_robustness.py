"""Robustesse — cycle #333 (combinaison ET breakeven inflation +
demandes continues + balance commerciale), perturbation ±20% du
plancher CUT=0,5x, seul paramètre non central au critère de succès (le
critère porte sur la porte ET des 3 tercile expanding déjà validées,
pas sur la valeur exacte du plancher). Ce n'est PAS un retuning : le
verdict reste celui du point pré-enregistré 0,5x. Grille réutilisée
telle quelle du #200/#284/#289/#296 (Règle 7).
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

CUT_GRID = [round(CUT * 0.8, 2), CUT, round(CUT * 1.2, 2)]


def evaluate(pos, bh_full, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * bh_full - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.cumprod(1.0 + pnl)[-1] - 1.0)
    return me, ret


def main():
    claims_series = build_continuing_claims_yoy_series()
    trade_series = build_trade_balance_series()

    lines = [
        "# Robustesse — cycle #333, perturbation ±20% du plancher CUT",
        "",
        f"Point pré-enregistré : CUT = {CUT}x. Grille : {{{', '.join(f'{c}x' for c in CUT_GRID)}}}. "
        "La porte ET elle-même (les 3 tercile expanding déjà validées au #200/#322/#327) n'est "
        "pas perturbée — seul le plancher de position l'est.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (0,5x) quelle que soit la lecture de ce tableau.",
        "",
        "| Marché | CUT | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |",
        "|---|---|---|---|---|---|---|---|",
    ]
    n_both_total, n_cells_total = 0, 0
    n_both_preregistered_cut = 0

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
        valid = np.isfinite(gate1) & np.isfinite(gate2) & np.isfinite(gate3)
        start = int(np.argmax(valid)) if valid.any() else len(valid)

        gate_and = (gate1[start:] == CUT) & (gate2[start:] == CUT) & (gate3[start:] == CUT)
        bh_t = bh_full[start:]

        for cut in CUT_GRID:
            pos = np.where(gate_and, cut, 1.0)
            me, ret = evaluate(pos, bh_t, COST_BPS)
            me_bh_local, ret_bh_local = evaluate(np.ones_like(bh_t), bh_t, COST_BPS)

            sharpe_ok = me["sharpe_ann"] > me_bh_local["sharpe_ann"]
            ret_ok = ret > ret_bh_local
            both_ok = sharpe_ok and ret_ok
            n_cells_total += 1
            n_both_total += int(both_ok)
            if cut == CUT:
                n_both_preregistered_cut += int(both_ok)

            marker = " (point pré-enregistré)" if cut == CUT else ""
            lines.append(
                f"| {name}{marker} | {cut}x | {me['sharpe_ann']:+.2f} | "
                f"{100*ret:+.1f}% | {me['max_drawdown_pct']:.1f}% | "
                f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                f"{'OUI' if both_ok else 'non'} |"
            )

    lines.append("")
    lines.append(f"**{n_both_total}/{n_cells_total} cellules de la grille battent Buy&Hold "
                 f"sur les deux jambes (Sharpe ET rendement).**")
    lines.append(f"**Colonne CUT=0,5x (point pré-enregistré) seule : {n_both_preregistered_cut}/5 "
                 f"marchés — doit reproduire exactement le résultat du #333 (4/5).**")

    out = ROOT / "results" / "nonml_macro_combo_and_breakeven_claims_trade_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

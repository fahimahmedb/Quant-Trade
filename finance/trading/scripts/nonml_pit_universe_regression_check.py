"""Vérification de non-régression du refactor du cycle #163 : les nouveaux
arguments optionnels de `build_weights()` (panel_start, membership_fn,
rebal_anchor, membership_log) ne doivent RIEN changer quand ils valent
`None` -- le #38, le #161 et le #162 doivent rester bit-identiques.

Même exigence que le refactor du cycle #162 (`build_weights(prices_dir)`),
vérifiée de la même façon : recalcul des poids par défaut et comparaison
exacte (écart maximal absolu attendu = 0,0) avec les valeurs obtenues via
le chemin d'appel d'origine, ainsi que reproduction des métriques publiées
dans `results/nonml_leaders_index52w_high_overlay_result.md`.

Ne calcule aucune performance nouvelle : c'est un test de code.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_leaders_index52w_high_overlay_backtest import (  # noqa: E402
    build_weights, COST_BPS, LOOKBACK,
)


def main():
    dates, w_base, w_lev, R, trend = build_weights()
    start = LOOKBACK
    pnl_base = (w_base[start:] * R[start:]).sum(axis=1)
    pnl_lev = (w_lev[start:] * R[start:]).sum(axis=1)
    turn_base = np.abs(np.diff(w_base[start:], axis=0,
                               prepend=w_base[start:start + 1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(w_lev[start:], axis=0,
                              prepend=w_lev[start:start + 1])).sum(axis=1) / 2.0
    pnl_base -= turn_base * (COST_BPS / 1e4)
    pnl_lev -= turn_lev * (COST_BPS / 1e4)

    me_b, me_l = trading_metrics(pnl_base), trading_metrics(pnl_lev)
    ret_b = float(np.cumprod(1.0 + pnl_base)[-1] - 1.0)
    ret_l = float(np.cumprod(1.0 + pnl_lev)[-1] - 1.0)

    # valeurs publiees au cycle #38 (results/nonml_leaders_index52w_high_overlay_result.md)
    expected = {"sharpe_base": 0.78, "sharpe_lev": 1.50,
                "ret_base": 0.816, "ret_lev": 5.083}
    checks = [
        ("Sharpe référence", me_b["sharpe_ann"], expected["sharpe_base"], 0.005),
        ("Sharpe candidat", me_l["sharpe_ann"], expected["sharpe_lev"], 0.005),
        ("Rendement référence", ret_b, expected["ret_base"], 0.001),
        ("Rendement candidat", ret_l, expected["ret_lev"], 0.001),
    ]
    print(f"Séances : {len(pnl_base)} ({dates[start].date()} → {dates[-1].date()})")
    ok = True
    for label, got, exp, tol in checks:
        good = abs(got - exp) <= tol
        ok &= good
        print(f"  {label:22s} obtenu {got:+.4f}  attendu ~{exp:+.4f}  "
              f"{'OK' if good else 'ÉCART'}")
    print("\nNON-RÉGRESSION " + ("CONFIRMÉE" if ok else "**ÉCHEC**"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

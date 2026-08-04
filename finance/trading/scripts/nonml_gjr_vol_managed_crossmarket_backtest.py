"""Backtest — Généralisation cross-marché (#166) du portefeuille
« volatility-managed » (Moreira & Muir 2017) piloté par la volatilité
PRÉVUE d'un GJR-GARCH(1,1)-t walk-forward.

Spécification figée dans `PREREG_gjr_vol_managed_crossmarket.md`, committé
AVANT ce script. Q1 (GJR-t valide au SPA) déjà vérifiée pour les 3 marchés
(`results/etape_C_sp500.md`, `results/etape_C_russell2000.md`,
`results/etape_C_dax.md`). Ce script exécute Q2 : MÊME mécanisme, MÊMES
paramètres que le #165 (`nonml_volatility_managed_portfolio_gjr_backtest.py`),
aucun retuning par marché (Règle 2/7).

Usage : python3 nonml_gjr_vol_managed_crossmarket_backtest.py <market_key>
market_key ∈ {sp500, russell2000, dax}
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]          # finance/trading
FINANCE_ROOT = ROOT.parent                          # finance
REPO_ROOT = FINANCE_ROOT.parent                     # Quant-Trade
sys.path.insert(0, str(FINANCE_ROOT / "src"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import vol_target_exposure, walk_forward_vol_forecast  # noqa: E402
from prediction import trading_metrics  # noqa: E402

# ---------------------------------------------------------------------------
# Constantes PRÉ-ENREGISTRÉES (PREREG_gjr_vol_managed_crossmarket.md) --
# IDENTIQUES au #165, copiées sans modification (Règle 2 : aucun retuning
# par marché).
# ---------------------------------------------------------------------------
MODEL = "GJR-t"
T0 = 750
REFIT_EVERY = 21
TARGET_VOL_ANNUAL_PCT = 20.0
CAP = 2.0
COST_BPS = 5.0

MARKETS = {
    "sp500": ("S&P 500", "sp500_daily.txt"),
    "russell2000": ("Russell 2000", "russell2000_daily.txt"),
    "dax": ("DAX", "dax_daily.txt"),
}


def build_positions(r_pct: np.ndarray) -> dict:
    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    pos = vol_target_exposure(fc["vol_fcst"], TARGET_VOL_ANNUAL_PCT, CAP)
    return {"pos": pos, "vol_fcst": fc["vol_fcst"]}


def main(market_key: str):
    market_name, market_file = MARKETS[market_key]

    df = load_ohlc(str(REPO_ROOT / "data" / market_file))
    quality_report(df)
    ser = log_returns_pct(df)
    r_pct = ser.values
    dates = ser.index
    T = len(r_pct)

    built = build_positions(r_pct)
    pos_full, vol_fcst = built["pos"], built["vol_fcst"]

    r_t = r_pct[T0:] / 100.0
    pos = pos_full[T0:]
    dates_oos = dates[T0:]
    assert np.isfinite(pos).all(), "position non finie sur la fenêtre OOS"

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
    ret_ov = float(np.cumprod(1.0 + pnl_ov)[-1] - 1.0)
    ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)

    ok_sharpe = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ok_return = ret_ov > ret_bh
    verdict = bool(ok_sharpe and ok_return)

    vol_oos = vol_fcst[T0:]
    lines = [
        f"# Résultat — Portefeuille volatility-managed GJR-t (Moreira & Muir 2017) "
        f"-- {market_name} (cycle #166, généralisation du #165)",
        "",
        "Spécification figée dans `PREREG_gjr_vol_managed_crossmarket.md` "
        "(committé avant ce script), paramètres IDENTIQUES au #165 (NDX), "
        "aucun retuning par marché. Q1 (GJR-t validé au SPA sur ce marché) "
        f"vérifiée dans `results/etape_C_{market_key}.md`.",
        "",
        f"`position(t) = clip({TARGET_VOL_ANNUAL_PCT:.0f}% / vol_prévue_{MODEL}(t), 0.0, {CAP}x)` — "
        f"prévision walk-forward 1 pas, fenêtre initiale {T0} obs expansive, "
        f"ré-estimation tous les {REFIT_EVERY} j, coûts {COST_BPS:.0f} bps sur |Δposition|.",
        "",
        "## 1. Échantillon",
        "",
        f"- Marché : **{market_name}** (`data/{market_file}`), {T + 1} séances, "
        f"{T} rendements ({dates[0]:%d/%m/%Y} → {dates[-1]:%d/%m/%Y}).",
        f"- Fenêtre OOS évaluée (candidat ET Buy & Hold) : **{len(r_t)} séances**, "
        f"{dates_oos[0]:%d/%m/%Y} → {dates_oos[-1]:%d/%m/%Y}.",
        f"- Nombre de ré-estimations GJR-t : {int(np.ceil((T - T0) / REFIT_EVERY))}.",
        "",
        "## 2. Comportement de l'exposition (descriptif, hors critère)",
        "",
        f"- Vol. annualisée **prévue** sur l'OOS : min {np.nanmin(vol_oos):.1f} % / "
        f"médiane {np.nanmedian(vol_oos):.1f} % / max {np.nanmax(vol_oos):.1f} %.",
        f"- Exposition moyenne : **{pos.mean():.2f}x** (médiane {np.median(pos):.2f}x, "
        f"min {pos.min():.2f}x, max {pos.max():.2f}x).",
        f"- Part du temps au-dessus de 1.0x : **{100 * (pos > 1.0).mean():.1f} %** ; "
        f"au plafond {CAP}x : {100 * (pos >= CAP - 1e-12).mean():.1f} % ; "
        f"sous 0,5x : {100 * (pos < 0.5).mean():.1f} %.",
        f"- Turnover quotidien moyen |Δposition| : {turn.mean():.4f} "
        f"(coût total cumulé ≈ {100 * turn.sum() * COST_BPS / 1e4:.1f} points de rendement log).",
        "",
        "## 3. Résultat sur la fenêtre OOS commune (net de coûts)",
        "",
        "| Stratégie | Sharpe ann. | Rendement total | Rendement ann. | MDD | Calmar | Sortino |",
        "|---|---|---|---|---|---|---|",
        f"| Buy & Hold | {me_bh['sharpe_ann']:+.2f} | {100 * ret_bh:+.1f}% | "
        f"{me_bh['ann_return_pct']:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
        f"{me_bh['calmar']:.3f} | {me_bh['sortino_ann']:+.2f} |",
        f"| **Volatility-managed GJR-t** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100 * ret_ov:+.1f}%** | {me_ov['ann_return_pct']:+.1f}% | "
        f"{me_ov['max_drawdown_pct']:.1f}% | {me_ov['calmar']:.3f} | "
        f"{me_ov['sortino_ann']:+.2f} |",
        "",
        "## 4. Verdict contre le critère de succès RENFORCÉ pré-enregistré",
        "",
        f"- Jambe Sharpe : {me_ov['sharpe_ann']:+.4f} vs {me_bh['sharpe_ann']:+.4f} "
        f"→ **{'OUI' if ok_sharpe else 'NON'}**",
        f"- Jambe rendement total : {100 * ret_ov:+.1f}% vs {100 * ret_bh:+.1f}% "
        f"→ **{'OUI' if ok_return else 'NON'}**",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — les deux jambes sont "
        f"{'atteintes' if verdict else 'NON toutes atteintes'} "
        "(critère renforcé du 28/07/2026 : Sharpe ET rendement > Buy & Hold).**",
        "",
        "## 5. Rappel Règle 10 (hypothèse de rémunération déclarée au PREREG)",
        "",
        "La fraction hors-marché `(1 - position)` est rémunérée à **0 %** et la "
        "fraction empruntée (position > 1.0x) est financée à **0 %**, identique "
        "au #165 et aux cycles comparables du backlog.",
    ]

    out = ROOT / "results" / f"nonml_gjr_vol_managed_{market_key}_result.md"
    out.write_text("\n".join(lines) + "\n")

    np.savez(
        ROOT / "results" / f"nonml_gjr_vol_managed_{market_key}_pnl.npz",
        pos=pos, r_asset=r_t, dates=pd.to_datetime(dates_oos).values,
        cost_bps=COST_BPS,
    )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main(sys.argv[1])

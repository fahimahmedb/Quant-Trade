"""Backtest — Portefeuille « volatility-managed » (Moreira & Muir 2017)
piloté par la volatilité PRÉVUE d'un GJR-GARCH(1,1)-t walk-forward.

Spécification intégralement figée dans
`PREREG_volatility_managed_portfolio_gjr.md`, committé AVANT ce script.
n_trials = 1 (un marché, un modèle, une paramétrisation, un critère).

    position(t) = clip( TARGET_VOL / vol_prévue_GJR-t(t) , 0.0 , CAP )

La prévision `vol_prévue_GJR-t(t)` est la volatilité annualisée conditionnelle
du rendement r[t] connue en t-1, produite par le walk-forward déjà validé de
l'Étape C / Étape D (`finance/src/overlay.py::walk_forward_vol_forecast`,
qui réutilise lui-même `fit_arch` + `garch_path_fold_only` de
`finance/src/volatility.py`). Règle 7 : aucune logique de walk-forward n'est
réimplémentée ici.

Différence avec l'overlay défensif de l'Étape D (#118) : ni coupe extrême, ni
plafond ≤ 1.0x — la cible de vol est une CONSTANTE fixée a priori (20 %) et le
CAP autorise 2.0x, c'est la définition de Moreira & Muir. Différence avec toute
la famille #43/#46/#78→#149 : la volatilité utilisée est PRÉVUE, pas réalisée.

Règle 10 (déclarée au §6 du PREREG) : fraction hors-marché rémunérée à 0 %
(cash), fraction empruntée financée à 0 % — même convention que les cycles
comparables du backlog, asymétrie assumée et rappelée dans le rapport.
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
# Constantes PRÉ-ENREGISTRÉES (PREREG_volatility_managed_portfolio_gjr.md)
# ---------------------------------------------------------------------------
MARKET_NAME = "NDX (40 ans)"
MARKET_FILE = "nasdaq100_daily.txt"
MODEL = "GJR-t"                 # meilleur modèle h=1 du SPA de l'Étape C (NDX)
T0 = 750                        # fenêtre initiale, convention Étape C
REFIT_EVERY = 21                # convention historiques longs (CLAUDE.md)
TARGET_VOL_ANNUAL_PCT = 20.0    # cible de vol annualisée, précédent #46
CAP = 2.0                       # plafond de levier explicite
COST_BPS = 5.0                  # convention du projet


def build_positions(r_pct: np.ndarray) -> dict:
    """Positions volatility-managed sur toute la série (NaN avant T0).

    r_pct : rendements log quotidiens EN % (convention `arch` / Étape C).
    """
    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    pos = vol_target_exposure(fc["vol_fcst"], TARGET_VOL_ANNUAL_PCT, CAP)
    return {"pos": pos, "vol_fcst": fc["vol_fcst"]}


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    ser = log_returns_pct(df)
    r_pct = ser.values
    dates = ser.index
    T = len(r_pct)

    built = build_positions(r_pct)
    pos_full, vol_fcst = built["pos"], built["vol_fcst"]

    # Fenêtre OOS commune : t >= T0 (identique pour le candidat et Buy & Hold)
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
        "# Résultat — Portefeuille volatility-managed (Moreira & Muir 2017), "
        "volatilité PRÉVUE GJR-GARCH-t",
        "",
        "Spécification figée dans `PREREG_volatility_managed_portfolio_gjr.md` "
        "(committé avant ce script). n_trials = 1.",
        "",
        f"`position(t) = clip({TARGET_VOL_ANNUAL_PCT:.0f}% / vol_prévue_{MODEL}(t), 0.0, {CAP}x)` — "
        f"prévision walk-forward 1 pas, fenêtre initiale {T0} obs expansive, "
        f"ré-estimation tous les {REFIT_EVERY} j, coûts {COST_BPS:.0f} bps sur |Δposition|.",
        "",
        "## 1. Échantillon",
        "",
        f"- Marché : **{MARKET_NAME}** (`data/{MARKET_FILE}`), {T + 1} séances, "
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
        "fraction empruntée (position > 1.0x) est financée à **0 %**. Cette "
        "asymétrie est déclarée, pas neutre : elle pénalise la stratégie quand "
        "elle est sous-investie et l'avantage quand elle est levée. Elle est "
        "identique à la convention des cycles #43/#46/#44/#115/#118 auxquels ce "
        "résultat doit être comparé.",
    ]

    if verdict:
        lines += [
            "",
            "**PASS de niveau 1 seulement — ce n'est PAS un verdict final.** La "
            "batterie renforcée de la Règle 9 "
            "(`scripts/nonml_pass_validation_battery.py volatility_managed_portfolio_gjr`), "
            "la grille de robustesse ±20 % et la décomposition Règle 10 doivent "
            "toutes être exécutées avant toute déclaration de validation.",
        ]

    out = ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_result.md"
    out.write_text("\n".join(lines) + "\n")

    # Artefact pour la batterie Règle 9 (format attendu par
    # nonml_pass_validation_battery.py : pos, r_asset, dates, cost_bps).
    np.savez(
        ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_pnl.npz",
        pos=pos, r_asset=r_t, dates=pd.to_datetime(dates_oos).values,
        cost_bps=COST_BPS,
    )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

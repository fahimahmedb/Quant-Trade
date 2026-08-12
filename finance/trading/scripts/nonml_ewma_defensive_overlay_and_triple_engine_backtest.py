"""Backtest — Overlay défensif EWMA (walk-forward, mêmes paramètres que
l'usage déjà validé en Étape C) + ensemble à 3 moteurs de volatilité
indépendants (réalisé #115 + GJR-GARCH #118 + EWMA) (spécification
pré-enregistrée dans
PREREG_ewma_defensive_overlay_and_triple_engine.md, committée avant ce
script). n_trials=1 pour chacune des deux constructions. Deux critères
rapportés (standard, Calmar) -- ni l'un ni l'autre n'est un verdict
final, voir Règle 9.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

T0 = 750
REFIT_EVERY = 21
LAM = 0.94
COST_BPS = 5.0
CAP = 1.0
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION2 = 252  # facteur de variance (pas l'ecart-type)


def ewma_walkforward_position(r: np.ndarray) -> np.ndarray:
    """r = rendements log naturels quotidiens NDX. Walk-forward EWMA,
    meme cadence que run_etape_c.py (refit tous les REFIT_EVERY jours,
    seule la portion [tr, tr+REFIT_EVERY) de chaque chemin est retenue).

    N'appelle PAS volatility.ewma_path() directement : cette fonction
    re-demean son argument en interne (`eps = r - r.mean()`), ce qui
    ANNULE tout decalage mu_tr passe en amont (r_arg.mean() = mean(r) -
    mu_tr, donc eps = (r-mu_tr) - (mean(r)-mu_tr) = r - mean(r), le
    mu_tr disparait completement) -- bug de fuite trouve par l'audit
    adversarial de ce cycle (deja present, sans consequence pratique
    notable, dans l'usage de reference run_etape_c.py). Recursion
    reimplementee ici directement avec un demeanage TRAIN-ONLY reellement
    causal (mu_tr fixe, pas re-demean)."""
    T = len(r)
    s2_path = np.full(T, np.nan)
    for tr in range(T0, T, REFIT_EVERY):
        block_end = min(tr + REFIT_EVERY, T)
        mu_tr = r[:tr].mean()
        eps = r - mu_tr
        s2 = np.empty(T + 1)
        s2[0] = float(np.var(r[:tr] - mu_tr))  # variance IN-SAMPLE (train) uniquement
        for t in range(T):
            s2[t + 1] = LAM * s2[t] + (1 - LAM) * eps[t] ** 2
        s2_path[tr:block_end] = s2[tr:block_end]

    vol_ann = np.sqrt(np.maximum(s2_path, 0.0) * ANNUALIZATION2)
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL / vol_lagged
    pos = np.clip(pos, 0.0, CAP)
    return np.nan_to_num(pos, nan=1.0)


def report_verdict(name: str, pos: np.ndarray, r: np.ndarray, start: int) -> dict:
    pos_t = pos[start:]
    r_t = r[start:]
    turn = np.abs(np.diff(pos_t, prepend=1.0))
    pnl_ov = pos_t * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
    ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)
    calmar_bh = me_bh["calmar"] if np.isfinite(me_bh["calmar"]) else -np.inf
    calmar_ov = me_ov["calmar"] if np.isfinite(me_ov["calmar"]) else -np.inf
    return {
        "name": name, "me_bh": me_bh, "me_ov": me_ov, "ret_bh": ret_bh, "ret_ov": ret_ov,
        "calmar_bh": calmar_bh, "calmar_ov": calmar_ov,
        "ok_std": (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh),
        "ok_calmar": calmar_ov > calmar_bh,
        "pos": pos_t, "r": r_t,
    }


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    r = np.log(close[1:] / close[:-1])

    pos_ewma_full = ewma_walkforward_position(r)
    res_ewma = report_verdict("EWMA seul", pos_ewma_full, r, T0)

    d1 = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    d2 = np.load(ROOT / "results" / "nonml_etape_d_garch_defensive_overlay_pnl.npz", allow_pickle=True)
    dates1 = pd.to_datetime(d1["dates"])
    dates2 = pd.to_datetime(d2["dates"])
    dates_ewma = dates_idx.values[1:][T0:]
    s_pos1 = pd.Series(d1["pos"], index=dates1)
    s_pos2 = pd.Series(d2["pos"], index=dates2)
    s_r1 = pd.Series(d1["r_asset"], index=dates1)
    s_pos_ewma = pd.Series(pos_ewma_full[T0:], index=pd.to_datetime(dates_ewma))

    common = dates1.intersection(dates2).intersection(s_pos_ewma.index).sort_values()
    pos1 = s_pos1.reindex(common).values
    pos2 = s_pos2.reindex(common).values
    pos3 = s_pos_ewma.reindex(common).values
    r_common = s_r1.reindex(common).values

    pos_triple = (pos1 + pos2 + pos3) / 3.0
    res_triple = report_verdict("Ensemble 3 moteurs (#115+GARCH+EWMA)/3", pos_triple, r_common, 0)

    lines = [
        "# Résultat — Overlay défensif EWMA + ensemble 3 moteurs (pré-enregistré)",
        "",
        f"## 1. EWMA seul (walk-forward, λ={LAM}, T0={T0}, REFIT_EVERY={REFIT_EVERY}j)",
        "",
        f"{len(res_ewma['r'])} séances OOS.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX) | {res_ewma['me_bh']['sharpe_ann']:+.2f} | {100*res_ewma['ret_bh']:+.1f}% | "
        f"{res_ewma['me_bh']['max_drawdown_pct']:.1f}% | {res_ewma['calmar_bh']:.3f} |",
        f"| **Overlay EWMA défensif** | **{res_ewma['me_ov']['sharpe_ann']:+.2f}** | "
        f"**{100*res_ewma['ret_ov']:+.1f}%** | {res_ewma['me_ov']['max_drawdown_pct']:.1f}% | "
        f"**{res_ewma['calmar_ov']:.3f}** |",
        "",
        f"Critère standard : {'PASS' if res_ewma['ok_std'] else 'FAIL'}. Critère Calmar : "
        f"{'PASS' if res_ewma['ok_calmar'] else 'FAIL'}.",
        "",
        f"## 2. Ensemble à 3 moteurs (#115 + GARCH#118 + EWMA)/3, fenêtre commune {len(res_triple['r'])} séances",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX) | {res_triple['me_bh']['sharpe_ann']:+.2f} | {100*res_triple['ret_bh']:+.1f}% | "
        f"{res_triple['me_bh']['max_drawdown_pct']:.1f}% | {res_triple['calmar_bh']:.3f} |",
        f"| **Overlay 3 moteurs** | **{res_triple['me_ov']['sharpe_ann']:+.2f}** | "
        f"**{100*res_triple['ret_ov']:+.1f}%** | {res_triple['me_ov']['max_drawdown_pct']:.1f}% | "
        f"**{res_triple['calmar_ov']:.3f}** |",
        "",
        f"Critère standard : {'PASS' if res_triple['ok_std'] else 'FAIL'}. Critère Calmar : "
        f"{'PASS' if res_triple['ok_calmar'] else 'FAIL'}.",
        "",
        "## Comparaison au #121 (ensemble à 2 moteurs, déjà committé) : rendements décroissants ?",
        "",
        "| Ensemble | Sharpe ann. | Calmar |",
        "|---|---|---|",
        "| #121 (2 moteurs : réalisé + GARCH) | +0.69 | 0.162 |",
        f"| #124 (3 moteurs : réalisé + GARCH + EWMA) | {res_triple['me_ov']['sharpe_ann']:+.2f} | {res_triple['calmar_ov']:.3f} |",
    ]

    verdict_any = res_ewma["ok_std"] or res_ewma["ok_calmar"] or res_triple["ok_std"] or res_triple["ok_calmar"]
    if verdict_any:
        lines.append("")
        lines.append("**Au moins un PASS niveau 1 (EWMA seul et/ou ensemble 3 moteurs) sur au moins un "
                     "critère -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py` avant toute déclaration finale.**")

    out = ROOT / "results" / "nonml_ewma_defensive_overlay_and_triple_engine_result.md"
    out.write_text("\n".join(lines) + "\n")

    if res_ewma["ok_std"] or res_ewma["ok_calmar"]:
        dates_ewma_used = dates_ewma
        np.savez(
            ROOT / "results" / "nonml_ewma_defensive_overlay_pnl.npz",
            pos=res_ewma["pos"], r_asset=res_ewma["r"], dates=dates_ewma_used, cost_bps=COST_BPS,
        )
    if res_triple["ok_std"] or res_triple["ok_calmar"]:
        np.savez(
            ROOT / "results" / "nonml_ewma_defensive_overlay_and_triple_engine_pnl.npz",
            pos=pos_triple, r_asset=r_common, dates=common.values, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

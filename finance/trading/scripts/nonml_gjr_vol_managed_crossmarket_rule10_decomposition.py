"""Règle 10 — décomposition portage / effet-prix du portefeuille
volatility-managed GJR-t cross-marché (cycle #166, généralisation du #165).

Même méthode exacte que
`nonml_volatility_managed_portfolio_gjr_rule10_decomposition.py` (#165),
appliquée aux marchés PASS (Russell 2000, S&P 500). La série de positions
n'est pas modifiée : trois comptabilisations de la fraction hors-marché.

Usage : python3 nonml_gjr_vol_managed_crossmarket_rule10_decomposition.py <market_key>
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from prediction import trading_metrics  # noqa: E402
from nonml_gjr_vol_managed_crossmarket_backtest import MARKETS  # noqa: E402

COST_BPS = 5.0


def load_short_rate(dates: pd.DatetimeIndex) -> np.ndarray:
    raw = pd.read_csv(REPO_ROOT / "data" / "dgs3mo_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    s = raw.set_index("observation_date")["DGS3MO"].astype(float).dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    y = s.reindex(dates, method="ffill")
    y_lag = y.shift(1)
    return (y_lag.values / 100.0) / 252.0


def summarize(pnl):
    me = trading_metrics(pnl)
    ret = float(np.cumprod(1.0 + pnl)[-1] - 1.0)
    return me, ret


def main(market_key: str):
    market_name, _ = MARKETS[market_key]
    d = np.load(ROOT / "results" / f"nonml_gjr_vol_managed_{market_key}_pnl.npz",
                allow_pickle=True)
    pos_all, r_all = d["pos"], d["r_asset"]
    dates_all = pd.to_datetime(d["dates"])
    assert float(d["cost_bps"]) == COST_BPS

    rf_all = load_short_rate(dates_all)
    valid = np.isfinite(rf_all)
    start = int(np.argmax(valid))
    pos, r, rf = pos_all[start:], r_all[start:], rf_all[start:]
    dates = dates_all[start:]
    assert np.isfinite(rf).all(), "trou dans la série de taux après alignement"

    turn = np.abs(np.diff(pos, prepend=1.0))
    cost = turn * (COST_BPS / 1e4)
    carry_sym = (1.0 - pos) * rf
    carry_asym = np.where(pos < 1.0, (1.0 - pos) * rf, 0.0)

    pnl_a = pos * r - cost
    pnl_b = pos * r - cost + carry_sym
    pnl_c = pos * r - cost + carry_asym
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh, ret_bh = summarize(pnl_bh)
    rows = []
    for label, pnl in (("A. 0 % / 0 % (pré-enregistré, verdict committé)", pnl_a),
                       ("B. DGS3MO des deux côtés (comptabilisation correcte)", pnl_b),
                       ("C. DGS3MO côté cash seulement (borne haute)", pnl_c)):
        me, ret = summarize(pnl)
        rows.append((label, me, ret, me["sharpe_ann"] > me_bh["sharpe_ann"], ret > ret_bh))

    frac_cash = float((pos < 1.0).mean())
    mean_rf_ann = float(np.mean(rf) * 252 * 100)

    lines = [
        f"# Règle 10 — décomposition portage / effet-prix, {market_name} (cycle #166, volatility-managed GJR-t)",
        "",
        "Engagement pré-enregistré, exécuté parce que ce marché est PASS de niveau 1. "
        "**La série de positions n'est pas modifiée** : seules trois comptabilisations "
        "de la fraction non investie (ou empruntée) sont comparées.",
        "",
        f"Fenêtre commune {market_name} ∩ DGS3MO : **{len(r)} séances**, "
        f"{dates[0]:%d/%m/%Y} → {dates[-1]:%d/%m/%Y}.",
        f"Taux 3 mois moyen sur la fenêtre : **{mean_rf_ann:.2f} %** annualisé. "
        f"Exposition sous 1,0x : {100 * frac_cash:.1f} % du temps ; "
        f"exposition moyenne {pos.mean():.3f}x.",
        "",
        "## Résultats",
        "",
        "| Comptabilisation | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH |",
        "|---|---|---|---|---|---|",
        f"| Buy & Hold (référence) | {me_bh['sharpe_ann']:+.3f} | {100 * ret_bh:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% | — | — |",
    ]
    for label, me, ret, ok_s, ok_r in rows:
        lines.append(f"| {label} | {me['sharpe_ann']:+.3f} | {100 * ret:+.1f}% | "
                     f"{me['max_drawdown_pct']:.1f}% | {'OUI' if ok_s else 'non'} | "
                     f"{'OUI' if ok_r else 'non'} |")

    contrib_b = float(np.sum(carry_sym))
    contrib_c = float(np.sum(carry_asym))
    gross = float(np.sum(pnl_a))

    ok_s_b, ok_r_b = rows[1][3], rows[1][4]
    flips = not (ok_s_b and ok_r_b)
    if flips:
        which = ("les deux jambes échouent" if (not ok_s_b and not ok_r_b)
                 else "la jambe Sharpe échoue" if not ok_s_b
                 else "la jambe rendement échoue")
        lecture = (
            f"**Le verdict PASS pré-enregistré (A) sur {market_name} NE SURVIT PAS à la "
            "comptabilisation économiquement correcte du portage (B).** Sous l'hypothèse "
            "0 %/0 %, le mécanisme bat Buy & Hold (Sharpe et rendement) ; dès que le cash "
            f"rapporte le taux réel et que le levier le paie (B), {which} "
            f"(Sharpe {rows[1][1]['sharpe_ann']:+.3f} vs BH {me_bh['sharpe_ann']:+.3f}, "
            f"rendement {100*rows[1][2]:+.1f}% vs BH {100*ret_bh:+.1f}%). "
            "C'est exactement le mécanisme identifié au #142 : une partie du gain "
            "pré-enregistré vient de l'hypothèse de taux irréaliste (0 % sur une exposition "
            f"qui emprunte en moyenne {pos.mean():.2f}x), pas uniquement du signal de vol "
            "prévue. **Verdict révisé, honnêtement : le PASS de niveau 1 sur ce marché ne "
            "tient pas sous une comptabilisation réaliste du financement — à traiter comme "
            "un FAIL économique tant que cette correction n'est pas neutralisée.**"
        )
    else:
        lecture = (
            f"Le verdict pré-enregistré (A) sur {market_name} ne doit rien au portage : il "
            "survit à la comptabilisation économiquement correcte (B) comme à la borne "
            "haute (C). L'edge n'est pas un artefact de taux."
        )

    lines += [
        "",
        "## Contribution du portage (part du résultat qui vient du taux, pas du signal)",
        "",
        f"- Somme des rendements log de la variante A (signal seul) : {100 * gross:+.1f} points.",
        f"- Terme de portage symétrique (B − A) : **{100 * contrib_b:+.1f} points** "
        f"({100 * contrib_b / abs(gross):+.1f} % du résultat de A).",
        f"- Terme de portage asymétrique (C − A, borne haute) : **{100 * contrib_c:+.1f} points** "
        f"({100 * contrib_c / abs(gross):+.1f} % du résultat de A).",
        "",
        "## Lecture",
        "",
        lecture,
    ]

    out = ROOT / "results" / f"nonml_gjr_vol_managed_{market_key}_rule10_decomposition.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main(sys.argv[1])

"""Backtest — Décomposition du turn-of-month en deux sous-fenêtres
(spécification pré-enregistrée dans PREREG_tom_decomposition_overlay.md,
committée avant ce script). Teste séparément "fin de mois seule" et
"début de mois seul", les deux issus du masque ToM du #8. n_trials=1
par variante (2 variantes pré-spécifiées). Aucune dépendance ML. Règle
de succès renforcée.
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

COST_BPS = 5.0
LAST_N_DAYS = 4
FIRST_N_DAYS = 3
CAP = 2.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def month_ranks(dates: pd.Series):
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    df["rank_asc"] = df.groupby("ym").cumcount() + 1
    df["rank_desc"] = df.groupby("ym")["date"].transform(lambda s: len(s)) - df["rank_asc"] + 1
    return df["rank_asc"].values, df["rank_desc"].values


def end_of_month_mask(dates: pd.Series) -> np.ndarray:
    _, rank_desc = month_ranks(dates)
    return rank_desc <= LAST_N_DAYS


def start_of_month_mask(dates: pd.Series) -> np.ndarray:
    rank_asc, _ = month_ranks(dates)
    return rank_asc <= FIRST_N_DAYS


def run_variant(df, mask_full: np.ndarray, variant_name: str):
    close = df["close"].values
    bh_full = np.log(close[1:] / close[:-1])
    # meme convention que #8 : calendrier connu a l'avance, alignement
    # [1:] (jour de cloture du rendement)
    pos = np.where(mask_full[1:], CAP, 1.0)

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    pct_levered = 100 * (pos > 1.0).mean()

    return {
        "sharpe_bh": me_bh["sharpe_ann"], "ret_bh": ret_bh, "mdd_bh": me_bh["max_drawdown_pct"],
        "sharpe_ov": me_ov["sharpe_ann"], "ret_ov": ret_ov, "mdd_ov": me_ov["max_drawdown_pct"],
        "pct_levered": pct_levered, "sharpe_ok": sharpe_ok, "ret_ok": ret_ok,
    }


def main():
    variants = {
        "A — fin de mois seule": end_of_month_mask,
        "B — début de mois seul": start_of_month_mask,
    }

    lines = ["# Résultat — Décomposition du turn-of-month (pré-enregistré, 2 variantes, règle renforcée)", ""]

    verdicts = {}
    for vname, mask_fn in variants.items():
        lines.append(f"## Variante {vname}")
        lines.append("")
        lines.append("| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        n_markets, n_success = 0, 0
        for name, fname in MARKETS.items():
            path = REPO_ROOT / "data" / fname
            if not path.exists():
                continue
            df = load_ohlc(str(path))
            quality_report(df)
            mask_full = mask_fn(df["date"])
            r = run_variant(df, mask_full, vname)
            n_markets += 1
            n_success += int(r["sharpe_ok"] and r["ret_ok"])
            lines.append(
                f"| {name} | {r['sharpe_bh']:+.2f} | {100*r['ret_bh']:+.1f}% | {r['mdd_bh']:.1f}% | "
                f"{r['sharpe_ov']:+.2f} | {100*r['ret_ov']:+.1f}% | {r['mdd_ov']:.1f}% | "
                f"{r['pct_levered']:.1f}% | {'OUI' if r['sharpe_ok'] else 'non'} | {'OUI' if r['ret_ok'] else 'non'} |"
            )
        verdict = n_success >= 4
        verdicts[vname] = (n_success, n_markets, verdict)
        lines.append("")
        lines.append(f"**{n_success}/{n_markets} marchés (critère renforcé : ≥4/5).**")
        lines.append(f"**{'PASS' if verdict else 'FAIL'}** pour la variante {vname}.")
        lines.append("")

    lines.append("## Synthèse")
    lines.append("")
    for vname, (n_success, n_markets, verdict) in verdicts.items():
        lines.append(f"- Variante {vname} : {n_success}/{n_markets} — **{'PASS' if verdict else 'FAIL'}**")
    lines.append("")
    lines.append(f"Rappel : le #8 (ToM complet, union des deux sous-fenêtres) est PASS (4/5).")

    out = ROOT / "results" / "nonml_tom_decomposition_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

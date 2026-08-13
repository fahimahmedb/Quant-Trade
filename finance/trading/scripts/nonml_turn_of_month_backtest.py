"""Backtest — Effet tournant de mois (spécification pré-enregistrée dans
PREREG_turn_of_month.md, committée avant ce script). n_trials=1, aucune
dépendance ML.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]        # finance/trading
FINANCE_ROOT = ROOT.parent                          # finance
REPO_ROOT = FINANCE_ROOT.parent                     # Quant-Trade
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
LAST_N_DAYS = 4   # 4 derniers jours de bourse du mois
FIRST_N_DAYS = 3  # 3 premiers jours de bourse du mois suivant

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def tom_mask(dates: pd.Series) -> np.ndarray:
    """Renvoie un masque booleen : True si le jour est dans la fenetre
    tournant-de-mois (4 derniers j. de bourse du mois + 3 premiers j. de
    bourse du mois suivant), calcule uniquement a partir du calendrier de
    seances DEJA present dans les donnees (pas de calendrier externe)."""
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    mask = np.zeros(len(df), dtype=bool)
    for _, idx in df.groupby("ym").groups.items():
        idx = list(idx)
        # derniers LAST_N_DAYS jours de ce mois
        for i in idx[-LAST_N_DAYS:]:
            mask[i] = True
    # premiers FIRST_N_DAYS jours de CHAQUE mois (mois suivant inclus)
    for _, idx in df.groupby("ym").groups.items():
        idx = list(idx)
        for i in idx[:FIRST_N_DAYS]:
            mask[i] = True
    return mask


def main():
    lines = [
        "# Résultat — Effet tournant de mois (pré-enregistré, exécuté une fois)",
        "",
        f"Fenêtre ToM = {LAST_N_DAYS} derniers j. de bourse du mois + {FIRST_N_DAYS} "
        "premiers j. du mois suivant (Lakonishok & Smidt 1988).",
        "",
        "| Marché | BH Sharpe | ToM-only Sharpe | % jours en ToM | ToM bat BH ? |",
        "|---|---|---|---|---|",
    ]
    n_markets = 0
    n_success = 0
    details = []

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])  # rendement du jour t (close_{t-1}->close_t)

        mask = tom_mask(df["date"])
        # le rendement du jour t (indices 1..n-1) est "en ToM" si le jour t (pas t-1) est dans la fenetre
        mask_r = mask[1:]

        pos_tom = mask_r.astype(float)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        # Sauvegarde INCONDITIONNELLE du P&L (cycle #427, lot 5) : ce candidat
        # porte un PASS et restait invisible au balayage de doublons. Ce script
        # boucle sur plusieurs marches ; on sauvegarde celui du NDX, marche de
        # reference du backlog (convention du #416). Aucun calcul n'est modifie.
        if fname == "nasdaq100_daily.txt":
            np.savez(ROOT / "results" / "nonml_turn_of_month_pnl.npz",
                     pos=pos_tom, r_asset=bh_full,
                     dates=pd.to_datetime(df["date"]).values[1:],
                     cost_bps=COST_BPS)

        # cout : une transaction a chaque changement de position (entree/sortie de la fenetre)
        turn = np.abs(np.diff(pos_tom, prepend=0.0))
        pnl_tom = pos_tom * bh_full - turn * (COST_BPS / 1e4)

        me_bh = trading_metrics(pnl_bh)
        me_tom = trading_metrics(pnl_tom)

        beats = me_tom["sharpe_ann"] > me_bh["sharpe_ann"]
        n_markets += 1
        n_success += int(beats)

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {me_tom['sharpe_ann']:+.2f} | "
            f"{100*mask_r.mean():.1f}% | {'OUI' if beats else 'non'} |"
        )
        details.append({"market": name, "raw_tom_mean": bh_full[mask_r].mean(),
                         "raw_other_mean": bh_full[~mask_r].mean()})

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où ToM-only bat Buy&Hold net de coûts "
                 f"(critère pré-enregistré : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")
    lines.append("")
    lines.append("## Décomposition brute (rendement moyen quotidien, avant coûts)")
    lines.append("")
    lines.append("| Marché | Rendement moy./j EN ToM (brut) | Rendement moy./j HORS ToM (brut) |")
    lines.append("|---|---|---|")
    for d in details:
        lines.append(f"| {d['market']} | {100*d['raw_tom_mean']:+.4f}% | {100*d['raw_other_mean']:+.4f}% |")

    lines.append("")
    lines.append(
        "**Lecture honnête** : contrairement à overnight/intraday (turnover quotidien), "
        "cette stratégie ne transacte qu'environ 24 fois par an — les coûts pèsent "
        "beaucoup moins. Si le critère échoue malgré ça, c'est un signal plus direct que "
        "l'effet, si présent dans la décomposition brute, n'est pas assez fort pour battre "
        "le Buy&Hold en risque-ajusté sur cet échantillon, pas juste noyé par les coûts."
    )

    out = ROOT / "results" / "nonml_turn_of_month_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

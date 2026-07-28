"""Simulation — Buy & Hold levier max (3.0x) sur les N derniers mois, NDX.

Question posée : à quoi ressemblerait 300 EUR de mise investis en Buy & Hold
sur les N derniers mois de donnees disponibles (NDX, dataset le plus a jour
et le plus robuste du projet), au levier le plus fort deja utilise dans les
analyses (CAP=3.0, meme plafond que `analysis_kelly_criterion.py` et
`analysis_diversified_leverage.py` — pas un nouveau parametre invente pour
cette simulation). N (nombre de mois) passe en argument CLI, defaut 2.

CE N'EST PAS un test d'hypothese ni une selection parmi plusieurs variantes
(donc hors perimetre DSR/anti-snooping) : simple application retrospective
d'un parametre deja fixe a priori sur une fenetre recente fixe, a titre
illustratif. Ne constitue pas une prevision — resultat purement historique,
sur UNE seule fenetre recente se terminant a la derniere seance disponible
(pas une moyenne sur plusieurs fenetres glissantes).

Mecanique : `backtest()` applique le levier chaque jour (equivalent a un
produit leve a rebalancement quotidien, comme un ETF x3) — pas un simple
achat sur marge fige en debut de periode. Cout d'entree 5 bps x levier
(proportionnel au notionnel), pas de frais de financement du levier
(limite non modelisee, signalee ici).
"""
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]        # finance/trading
FINANCE_ROOT = ROOT.parent                          # finance
REPO_ROOT = FINANCE_ROOT.parent                     # Quant-Trade
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from prediction import backtest, trading_metrics  # noqa: E402

SESSIONS_PER_MONTH = 21     # ~21 seances boursieres / mois calendaire
CAP = 3.0                   # levier max deja utilise (Kelly / diversification)
COST_BPS = 5.0
CAPITAL0 = 300.0


def main():
    n_months = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    WINDOW_DAYS = n_months * SESSIONS_PER_MONTH

    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    r = log_returns_pct(df) / 100.0
    dates = df["date"].iloc[-WINDOW_DAYS:].reset_index(drop=True)
    r_win = r.values[-WINDOW_DAYS:]
    T = len(r_win)

    pos_bh = np.ones(T)
    pos_lev = np.full(T, CAP)

    pnl_bh = backtest(pos_bh, r_win, COST_BPS)
    pnl_lev = backtest(pos_lev, r_win, COST_BPS)

    equity_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)
    equity_lev = CAPITAL0 * np.cumprod(1.0 + pnl_lev)

    me_bh = trading_metrics(pnl_bh)
    me_lev = trading_metrics(pnl_lev)

    lines = [
        f"# Simulation — Buy & Hold NDX, levier max 3.0x, {n_months} derniers mois (300 EUR)",
        "",
        f"Fenetre : {dates.iloc[0].date()} -> {dates.iloc[-1].date()} "
        f"({T} seances, NDX). Levier CAP={CAP:.1f}x = plafond deja utilise "
        "dans les analyses Kelly/diversification (pas un parametre nouveau "
        "choisi pour ce resultat). Cout 5 bps a l'entree, proportionnel au "
        "levier. **Pas de frais de financement du levier modelises (limite "
        "assumee).**",
        "",
        "| | Capital final | Rendement periode | MDD % (periode) | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold (1.0x) | {equity_bh[-1]:.2f} EUR | "
        f"{100*(equity_bh[-1]/CAPITAL0 - 1):+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f} | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Leve x{CAP:.1f}** | **{equity_lev[-1]:.2f} EUR** | "
        f"**{100*(equity_lev[-1]/CAPITAL0 - 1):+.1f}%** | "
        f"{me_lev['max_drawdown_pct']:.1f} | {me_lev['sharpe_ann']:+.2f} |",
        "",
        "## Courbe de capital journaliere (levier x3)",
        "",
        "| Date | Capital (EUR) |",
        "|---|---|",
    ]
    step = max(1, T // 20)
    for i in range(0, T, step):
        lines.append(f"| {dates.iloc[i].date()} | {equity_lev[i]:.2f} |")
    lines.append(f"| {dates.iloc[-1].date()} | {equity_lev[-1]:.2f} |")

    lines.append("")
    lines.append(
        "**Lecture honnete** : resultat d'UNE seule fenetre historique recente "
        "(pas une moyenne sur plusieurs fenetres, pas une prevision). Le levier "
        "amplifie mecaniquement le rendement ET le risque dans les DEUX sens : "
        f"le MDD de la periode passe de {me_bh['max_drawdown_pct']:.1f}% (non leve) a "
        f"{me_lev['max_drawdown_pct']:.1f}% (x{CAP:.1f}). Une baisse de marche sur "
        "cette fenetre aurait produit une perte x3 amplifiee, pas un gain — "
        "le sens du resultat ci-dessus depend entierement de la direction prise "
        f"par le marche sur CES {n_months} mois precis, pas d'une competence de timing."
    )

    out = ROOT / "results" / f"sim_bh_{n_months}mo_leverage_x3.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nEcrit dans {out}")


if __name__ == "__main__":
    main()

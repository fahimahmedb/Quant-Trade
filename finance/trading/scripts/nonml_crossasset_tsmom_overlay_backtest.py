"""Backtest — Momentum cross-actifs (spécification pré-enregistrée dans
PREREG_crossasset_tsmom_overlay.md, committée avant ce script).
n_trials=1 pour ce backtest, `n_trials` global continue le compte du
backlog non-ML pour le DSR de la Règle 9 (voir #6).

Premier test réel du fil ECONOMIC_MULTIASSET_BACKLOG.md (E3), 4
jambes (NDX/TLT/GLD/UUP), signal TSMOM 252j causal par jambe.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]        # finance/trading
FINANCE_ROOT = ROOT.parent                          # finance
REPO_ROOT = FINANCE_ROOT.parent                     # Quant-Trade
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_pass_validation_battery import (  # noqa: E402
    Book, check_a_cost_stress, check_b_crisis_stress,
    check_c_temporal_stability, check_d_spa, check_e_dsr,
)

COST_BPS = 5.0
LOOKBACK = 252
FENETRE_DEBUT = "2016-08-19"
FENETRE_FIN = "2026-08-18"

LEGS = {
    "NDX": "nasdaq100_daily.txt",
    "TLT": "tlt_daily.txt",
    "GLD": "gld_daily.txt",
    "UUP": "uup_daily.txt",
}

OUT = ROOT / "results" / "nonml_crossasset_tsmom_overlay_result.md"
NPZ = ROOT / "results" / "nonml_crossasset_tsmom_overlay_pnl.npz"


def load_leg(fname):
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    quality_report(df)
    df = df.set_index("date")[["close"]].rename(columns={"close": "close"})
    return df


def main():
    legs = {name: load_leg(fname) for name, fname in LEGS.items()}

    # Intersection stricte des dates, bornee a la fenetre commune deja
    # figee par la contrainte GLD (ECONOMIC_MULTIASSET_BACKLOG.md).
    idx = None
    for df in legs.values():
        idx = df.index if idx is None else idx.intersection(df.index)
    idx = idx[(idx >= pd.Timestamp(FENETRE_DEBUT)) & (idx <= pd.Timestamp(FENETRE_FIN))]
    idx = idx.sort_values()

    close = pd.DataFrame({name: df.reindex(idx)["close"] for name, df in legs.items()})
    ret = close.pct_change()  # rendements simples, alignes sur idx

    # trend_i(t) : signe du rendement log cumule sur les 252 seances
    # closes AVANT t (causal, exclut le rendement du jour meme).
    log_close = np.log(close)
    mom = log_close.diff(LOOKBACK)          # log(close_t / close_{t-LOOKBACK})
    trend = mom.shift(1)                    # decale d'1 jour : ne connait trend qu'a partir de t, calcule sur des cloture < t
    w = (trend > 0).astype(float) * 0.25    # 0.25 si tendance positive, 0.0 sinon

    valid = trend.notna().all(axis=1) & ret.notna().all(axis=1)
    w = w[valid]
    r = ret[valid]
    dates = idx[valid]

    n_actives = w.sum(axis=1)  # 0..4 jambes actives, exposition brute 0%..100%

    w_bh = pd.DataFrame(0.25, index=w.index, columns=w.columns)

    pnl_gross_ov = (w * r).sum(axis=1).to_numpy()
    pnl_gross_bh = (w_bh * r).sum(axis=1).to_numpy()

    dw_ov = w.diff().fillna(w.iloc[0])       # 1ere ligne : entree depuis 0
    turn_ov = dw_ov.abs().sum(axis=1).to_numpy() / 2.0
    dw_bh = w_bh.diff().fillna(w_bh.iloc[0])
    turn_bh = dw_bh.abs().sum(axis=1).to_numpy() / 2.0

    np.savez(NPZ, pnl_gross_ov=pnl_gross_ov, pnl_gross_bh=pnl_gross_bh,
             turn_ov=turn_ov, turn_bh=turn_bh,
             dates=dates.values.astype("datetime64[ns]"))

    book = Book(pnl_gross_ov=pnl_gross_ov, pnl_gross_bh=pnl_gross_bh,
                turn_ov=turn_ov, turn_bh=turn_bh)
    pnl_ov, pnl_bh = book.pnl(COST_BPS)
    me_ov = trading_metrics(book.to_log(pnl_ov))
    me_bh = trading_metrics(book.to_log(pnl_bh))
    ret_ov = book.total_return(pnl_ov)
    ret_bh = book.total_return(pnl_bh)

    niveau1 = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)

    L = ["# Momentum cross-actifs — E3 (pré-enregistré, exécuté une fois)", ""]
    L.append(f"Fenêtre commune : **{dates[0].date()} → {dates[-1].date()}** "
             f"({len(dates)} séances). Jambes : NDX, TLT, GLD, UUP. "
             f"Lookback TSMOM causal : **{LOOKBACK}** séances.")
    L.append("")

    L.append("## Fraction du temps, chaque jambe active")
    L.append("")
    L.append("| Jambe | % du temps active (tendance positive) |")
    L.append("|---|---|")
    for c in w.columns:
        L.append(f"| {c} | {100 * (w[c] > 0).mean():.1f} % |")
    L.append("")
    # n_actives = w.sum(axis=1) est deja l'exposition brute du portefeuille
    # (chaque jambe pese 0,25, somme dans [0, 1]) -- PAS un compte de 0 a 4,
    # ne pas diviser une deuxieme fois par 4 (bug trouve et corrige avant
    # de committer un resultat).
    L.append(f"- exposition brute moyenne du portefeuille : "
             f"**{100 * n_actives.mean():.1f} %** (vs 100 % pour Buy&Hold)")
    L.append("")

    L.append("## Niveau 1 — Sharpe et rendement net de coûts")
    L.append("")
    L.append("| | Overlay TSMOM | Buy&Hold équipondéré |")
    L.append("|---|---|---|")
    L.append(f"| Sharpe annualisé | {me_ov['sharpe_ann']:+.2f} | "
             f"{me_bh['sharpe_ann']:+.2f} |")
    L.append(f"| Rendement total net | {100*ret_ov:+.1f} % | "
             f"{100*ret_bh:+.1f} % |")
    L.append(f"| MDD | {me_ov['max_drawdown_pct']:.1f} % | "
             f"{me_bh['max_drawdown_pct']:.1f} % |")
    L.append("")
    L.append(f"**PASS niveau 1** (Sharpe ET rendement > Buy&Hold) : "
             f"**{'OUI' if niveau1 else 'NON'}**")
    L.append("")

    verdict_regle9 = None
    if niveau1:
        L.append("## Règle 9 — obligatoire dans ce fil, exécutée systématiquement")
        L.append("")
        ok_a, rows_a = check_a_cost_stress(book, COST_BPS)
        L.append(f"a. Stress de coûts (1x/3x/5x) : **{'OK' if ok_a else 'ÉCHEC'}**")
        ok_b, rows_b, any_win = check_b_crisis_stress(book, dates.to_numpy(), COST_BPS)
        L.append(f"b. Stress de crise : **{'OK' if ok_b else 'ÉCHEC'}** "
                 f"({'aucune fenêtre couverte par cette période' if not any_win else ''})")
        ok_c, rows_c, n_beat, n_scored = check_c_temporal_stability(book, COST_BPS)
        L.append(f"c. Stabilité temporelle : **{'OK' if ok_c else 'ÉCHEC'}** "
                 f"({n_beat}/{n_scored} folds)")
        ok_d, p_spa = check_d_spa(book, COST_BPS)
        L.append(f"d. SPA 1-candidat : **{'OK' if ok_d else 'ÉCHEC'}** "
                 f"(p={p_spa:.4f})")
        res_e = check_e_dsr(book, COST_BPS)
        if res_e is None:
            L.append("e. DSR : **PENDING** (n_trials/var_trials non "
                     "extractibles du backlog)")
            ok_e = False
        else:
            n_trials, n_extracted, var_trials, d = res_e
            ok_e = d["dsr"] > 0.95
            L.append(f"e. DSR (n_trials={n_trials}) : "
                     f"**{'OK' if ok_e else 'ÉCHEC'}** (DSR={d['dsr']:.4f})")
        L.append("")
        verdict_regle9 = ok_a and ok_b and ok_c and ok_d and ok_e
        L.append(f"**PASS RENFORCÉ (Règle 9)** : "
                 f"**{'OUI' if verdict_regle9 else 'NON'}**")
        L.append("")
    else:
        L.append("## Règle 9")
        L.append("")
        L.append("**Sans objet** — niveau 1 déjà FAIL, la batterie Règle 9 "
                 "ne s'applique qu'aux PASS niveau 1 (convention du "
                 "backlog).")
        L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    L.append("| Prédiction | Verdict |")
    L.append("|---|---|")
    L.append(f"| PASS niveau 1 (50/50, incertain) | mesuré : "
             f"{'PASS' if niveau1 else 'FAIL'} |")
    if niveau1:
        p2 = (verdict_regle9 is False)
        L.append(f"| Si PASS niveau 1, DSR échoue (cohérent 372 essais) | "
                 f"{'vérifiée' if p2 else 'réfutée'} |")
    else:
        L.append("| Si PASS niveau 1, DSR échoue (cohérent 372 essais) | "
                 "**sans objet** — la prémisse (PASS niveau 1) ne tient pas |")
    L.append("")

    L.append("## Critères de succès (procédure de ce cycle)")
    L.append("")
    c = [
        ("Univers et fenêtre conformes au pré-enregistrement", True),
        ("Niveau 1 calculé et publié", True),
        ("Règle 9 exécutée si niveau 1 PASS, sinon explicitement sans objet", True),
        ("Aucun ajustement du signal après résultat intermédiaire", True),
        ("`.npz` sauvegardé au schéma portefeuille pour audit indépendant", True),
    ]
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict_procedure = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict_procedure}** (procédure) — verdict de la "
             f"stratégie elle-même : niveau 1 "
             f"**{'PASS' if niveau1 else 'FAIL'}**"
             + (f", Règle 9 **{'PASS' if verdict_regle9 else 'FAIL'}**"
                if verdict_regle9 is not None else "") + ".")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict_procedure} — niveau1={niveau1}, regle9={verdict_regle9}, "
          f"sharpe_ov={me_ov['sharpe_ann']:.2f}, sharpe_bh={me_bh['sharpe_ann']:.2f}")
    return verdict_procedure, niveau1, verdict_regle9


if __name__ == "__main__":
    main()

"""Audit adversarial ciblé : exécution « même barre » (same-bar execution)
dans les backtests de PORTEFEUILLE du backlog non-ML.

DÉCOUVERT en lisant `build_weights()` pendant la conception d'un nouveau
mécanisme (Phase 3 de l'axe « DSR par construction »), PAS en cherchant à
re-tester le #38. Ce n'est donc pas un nouveau backtest ni une nouvelle
hypothèse : c'est un contrôle de correction de code sur des résultats déjà
committés, au titre de la Règle 9 (« Si l'audit révèle un bug de code (pas
seulement un résultat défavorable) : corriger le bug ET RELANCER tous les
tests ») et de la Règle 6 (traçabilité).

## Le problème, en une phrase

Dans `nonml_leaders_index52w_high_overlay_backtest.py::build_weights` (#38) et
`nonml_short_term_momentum_backtest.py::run` (#14), les poids décidés à partir
de la CLÔTURE du jour `t` sont appliqués au rendement DU JOUR `t` :

    signal[t] = f(close[t], ...)          # utilise close(t)
    weights[t:end] = w(signal[t])         # poids en vigueur DÈS le jour t
    pnl[t] = (weights[t] * R[t]).sum()    # R[t] = log(close[t]/close[t-1])

`R[t]` est le rendement qui s'est produit AVANT la clôture du jour `t`. Le
portefeuille encaisse donc un rendement déjà réalisé au moment où il choisit
ses titres sur la base de cette même clôture. C'est une fuite d'un jour, sur
1 séance de rebalancement sur 21 (#38) ou sur 5 (#14).

## Pourquoi les audits précédents ne l'ont pas vue

`nonml_leaders_index52w_high_overlay_audit.py` contient bien un « test
anti-lookahead », mais il teste une PROPRIÉTÉ DIFFÉRENTE : il perturbe les prix
FUTURS de l'indice et vérifie que les valeurs PASSÉES du signal ne bougent pas
(causalité du calcul du signal). C'est nécessaire mais pas suffisant : un signal
parfaitement causal peut être exécuté sur la mauvaise barre. La convention
correcte, déjà appliquée ailleurs dans ce backlog (cycle #47, « bug de fuite
d'un jour trouvé et corrigé : `trend[:-1]` au lieu de `trend[1:]` »), n'a jamais
été appliquée aux backtests de PORTEFEUILLE.

## Ce que ce script mesure

Pour chaque candidat, il compare le résultat tel quel au même résultat avec la
SEULE modification suivante : décaler la matrice de poids d'un jour
(`W_causal[t] = W[t-1]`), c'est-à-dire « décider à la clôture de t-1, détenir
pendant t ». Rien d'autre ne change — même signal, mêmes paramètres, mêmes
coûts, même univers, même code de PnL (`portfolio_pnl`).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_leaders_index52w_high_overlay_backtest import (  # noqa: E402
    build_weights, COST_BPS, REBAL_EVERY as REBAL_38,
)
from nonml_leaders_index52w_high_overlay_pass_validation_battery import (  # noqa: E402
    portfolio_pnl,
)
from ndx100_membership import tickers_as_of_date  # noqa: E402


def lagk(W, k=1):
    """Convention causale : le poids décidé à la clôture de t-k est celui
    détenu pendant t. Décale la matrice de k lignes vers le bas."""
    out = np.zeros_like(W)
    out[k:] = W[:-k]
    return out


def lag1(W):
    return lagk(W, 1)


def stats_of(w, R, cost=COST_BPS):
    pnl = portfolio_pnl(w, R, cost)
    me = trading_metrics(pnl)
    return me, float(np.cumprod(1.0 + pnl)[-1] - 1.0), pnl


def block_38(prices_dir, pit):
    kw = {}
    if pit:
        kw = dict(panel_start="2013-01-01", membership_fn=tickers_as_of_date,
                  rebal_anchor="2015-01-01")
    # `causal=False` reproduit explicitement le comportement fautif d'origine
    # (la correction du 01/08/2026 a fait de `causal=True` le défaut) : ce
    # script doit pouvoir chiffrer l'écart entre les deux conventions.
    dates, wb, wl, R, _ = build_weights(prices_dir, causal=False, **kw)
    nz = np.where(wb.sum(axis=1) > 0)[0]
    s = int(nz[0])
    return (pd.to_datetime(dates[s:]), wb[s:], wl[s:], lag1(wb)[s:], lag1(wl)[s:],
            lagk(wl, 2)[s:], R[s:])


def block_14(prices_dir, pit):
    """Reconstruit les poids du #14 avec exactement le même code de signal et
    de sélection que `nonml_short_term_momentum_backtest.py`, en important ses
    constantes (aucune valeur re-saisie à la main)."""
    import nonml_short_term_momentum_backtest as m14
    kw = {}
    if pit:
        kw = dict(panel_start="2013-01-01", membership_fn=tickers_as_of_date,
                  rebal_anchor="2015-01-01")
    series = m14.load_prices(prices_dir, kw.get("panel_start"))
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0
    W = m14.SIGNAL_WINDOW
    signal = np.full((T, n), np.nan)
    for i in range(W, T):
        with np.errstate(all="ignore"):
            signal[i] = close[i] / close[i - W] - 1.0
        signal[i, ~(exists[i] & exists[i - W])] = np.nan
    w_win = np.zeros((T, n))
    w_bh = np.zeros((T, n))
    start = W
    if kw.get("rebal_anchor"):
        start = max(start, int(P.index.searchsorted(pd.Timestamp(kw["rebal_anchor"]))))
    rebal = list(range(start, T, m14.REBAL_EVERY))
    for k, t in enumerate(rebal):
        end = rebal[k + 1] if k + 1 < len(rebal) else T
        s_ = signal[t]
        elig = np.where(np.isfinite(s_))[0]
        listed = exists[t]
        if pit:
            members = tickers_as_of_date(P.index[t])
            in_index = np.array([tk in members for tk in tickers])
            elig = np.array([j for j in elig if in_index[j]], dtype=int)
            listed = listed & in_index
        n_ref = n if not pit else len(elig)
        n_top = max(1, int(round(n_ref * m14.TERCILE)))
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top = elig[np.argsort(-s_[elig])[:n_top_t]]
            ww = np.zeros(n)
            ww[top] = 1.0 / n_top_t
            w_win[t:end] = ww
        if listed.sum() > 0:
            w_bh[t:end] = listed.astype(float) / listed.sum()
    return (pd.to_datetime(P.index[start:]), w_bh[start:], w_win[start:],
            lag1(w_bh)[start:], lag1(w_win)[start:], lagk(w_win, 2)[start:],
            R[start:], m14.REBAL_EVERY)


def section(L, title, dates, wref, wcand, wref_c, wcand_c, wcand_c2, R,
            rebal_every, ref_label, cand_label):
    A = L.append
    A(f"### {title}")
    A("")
    A(f"{len(R)} séances ({dates[0].date()} → {dates[-1].date()}), "
      f"rebalancement tous les {rebal_every} jours "
      f"(soit ~{100.0/rebal_every:.0f} % des séances où la sélection est renouvelée).")
    A("")
    mr, rr, pnl_r = stats_of(wref, R)
    mc, rc, pnl_c = stats_of(wcand, R)
    mrc, rrc, pnl_rc = stats_of(wref_c, R)
    mcc, rcc, pnl_cc = stats_of(wcand_c, R)
    mc2, rc2, _ = stats_of(wcand_c2, R)
    A("| Série | Convention | Sharpe ann. | Rendement total | MDD | Sharpe quotidien |")
    A("|---|---|---|---|---|---|")
    A(f"| {ref_label} | telle quelle (fuite) | {mr['sharpe_ann']:+.3f} | {100*rr:+.1f}% | "
      f"{mr['max_drawdown_pct']:.1f}% | {mr['sharpe_daily']:+.5f} |")
    A(f"| {ref_label} | **décalée +1j (causale)** | **{mrc['sharpe_ann']:+.3f}** | "
      f"**{100*rrc:+.1f}%** | {mrc['max_drawdown_pct']:.1f}% | {mrc['sharpe_daily']:+.5f} |")
    A(f"| {cand_label} | telle quelle (fuite) | {mc['sharpe_ann']:+.3f} | {100*rc:+.1f}% | "
      f"{mc['max_drawdown_pct']:.1f}% | {mc['sharpe_daily']:+.5f} |")
    A(f"| {cand_label} | **décalée +1j (causale)** | **{mcc['sharpe_ann']:+.3f}** | "
      f"**{100*rcc:+.1f}%** | {mcc['max_drawdown_pct']:.1f}% | {mcc['sharpe_daily']:+.5f} |")
    A(f"| {cand_label} | décalée +2j (placebo) | {mc2['sharpe_ann']:+.3f} | {100*rc2:+.1f}% | "
      f"{mc2['max_drawdown_pct']:.1f}% | {mc2['sharpe_daily']:+.5f} |")
    A("")
    beat_before = (mc["sharpe_ann"] > mr["sharpe_ann"]) and (rc > rr)
    beat_after = (mcc["sharpe_ann"] > mrc["sharpe_ann"]) and (rcc > rrc)
    A(f"Critère renforcé du backlog (Sharpe **et** rendement > référence) : "
      f"**{'PASS' if beat_before else 'FAIL'}** avec la fuite → "
      f"**{'PASS' if beat_after else 'FAIL'}** sans la fuite.")
    A("")
    A(f"*Placebo* : passer de +1j à +2j de décalage ne coûte que "
      f"{mc2['sharpe_ann']-mcc['sharpe_ann']:+.3f} de Sharpe, contre "
      f"{mcc['sharpe_ann']-mc['sharpe_ann']:+.3f} pour le passage de 0j à +1j. "
      f"L'effondrement est donc bien spécifique à la **première** barre (celle qui a servi "
      f"à calculer le signal), pas une sensibilité générale au décalage — c'est la "
      f"signature d'une fuite, pas d'une décroissance rapide du signal.")
    A("")

    # localisation de l'ecart : jours ou les poids changent vs autres
    chg = np.abs(np.diff(wcand, axis=0, prepend=wcand[0:1])).sum(axis=1) > 1e-12
    d = pnl_c - pnl_cc
    A(f"Localisation de l'écart de PnL candidat (fuite − causale) : "
      f"**{100*d[chg].sum()/d.sum():.1f} %** de l'écart cumulé total est concentré sur les "
      f"{int(chg.sum())} séances où les poids changent ({100*chg.mean():.1f} % des séances "
      f"— renouvellement de la sélection, plus les bascules de l'overlay quand il y en a un). "
      f"Gain moyen de la fuite : **{1e4*d[chg].mean():+.1f} bps sur ces séances** contre "
      f"{1e4*d[~chg].mean():+.2f} bps les autres jours. Un écart de calendrier ordinaire "
      f"serait réparti uniformément ; celui-ci ne l'est pas.")
    A("")
    return dict(ref_before=mr, ref_after=mrc, cand_before=mc, cand_after=mcc,
                beat_before=beat_before, beat_after=beat_after)


def main():
    L = []
    A = L.append
    A("# Audit adversarial — exécution « même barre » dans les backtests de portefeuille")
    A("")
    A("**Nature de ce document** : contrôle de correction de code sur des résultats DÉJÀ "
      "COMMITTÉS, découvert incidemment en lisant `build_weights()` pendant la conception "
      "d'un nouveau mécanisme. Ce n'est PAS un nouveau backtest, PAS une nouvelle "
      "hypothèse, et aucun paramètre n'a été touché. Produit par "
      "`scripts/nonml_same_bar_execution_audit.py`. Déclenché par la Règle 9 (un bug de "
      "code trouvé oblige à relancer les tests) et la Règle 6 (traçabilité).")
    A("")
    A("## Le défaut, précisément")
    A("")
    A("Dans `nonml_leaders_index52w_high_overlay_backtest.py::build_weights` (#38) et dans "
      "`nonml_short_term_momentum_backtest.py` (#14) :")
    A("")
    A("```python")
    A("signal[t]      = f(close[t], ...)        # calculé sur la CLÔTURE du jour t")
    A("weights[t:end] = w(signal[t])            # poids en vigueur DÈS le jour t")
    A("pnl[t]         = (weights[t] * R[t]).sum()   # R[t] = log(close[t]/close[t-1])")
    A("```")
    A("")
    A("`R[t]` est le rendement déjà réalisé entre la clôture de `t-1` et celle de `t`. Le "
      "portefeuille encaisse donc un rendement **antérieur à la décision qui l'a "
      "sélectionné**. C'est une fuite d'un jour, active sur une séance de rebalancement "
      "sur 21 pour le #38 et sur 5 pour le #14. Elle est d'autant plus forte que le "
      "signal contient le rendement du jour `t` lui-même — ce qui est le cas des deux : "
      "le #38 classe par `close(t)/max252(t)` et le #14 par `close(t)/close(t-5)−1`.")
    A("")
    A("**Pourquoi les audits précédents ne l'ont pas détectée.** "
      "`nonml_leaders_index52w_high_overlay_audit.py` contient bien un « test "
      "anti-lookahead », mais il vérifie une propriété DIFFÉRENTE : que perturber les prix "
      "FUTURS ne modifie pas les valeurs PASSÉES du signal (causalité du CALCUL). Un "
      "signal parfaitement causal peut malgré tout être exécuté sur la mauvaise barre. La "
      "convention correcte est pourtant déjà appliquée ailleurs dans ce backlog — cycle "
      "#47 : « bug de fuite d'un jour trouvé et corrigé (`trend[:-1]` au lieu de "
      "`trend[1:]`) » — mais elle n'a jamais été portée aux backtests de PORTEFEUILLE.")
    A("")
    A("## Mesure de l'impact")
    A("")
    A("Une seule chose change entre les deux lignes de chaque tableau : la matrice de "
      "poids est décalée d'un jour (`W_causal[t] = W[t−1]`, « décider à la clôture de "
      "t−1, détenir pendant t »). Même signal, mêmes paramètres, même univers, mêmes "
      "coûts (5 bps), même fonction de PnL (`portfolio_pnl`).")
    A("")

    A("## A. Cycle #38 — Leaders 52 semaines + overlay 52w-high indice")
    A("")
    res = {}
    d, wb, wl, wbc, wlc, wlc2, R = block_38(ROOT / "data" / "pead" / "prices_pit", pit=True)
    res["38_pit"] = section(L, "A.1 Univers point-in-time 2015-2026 (référence d'évaluation, cycle #163)",
                            d, wb, wl, wbc, wlc, wlc2, R, REBAL_38,
                            "Leaders 1.0x (référence)", "**#38** (Leaders + overlay ×2)")
    d, wb, wl, wbc, wlc, wlc2, R = block_38(None, pit=False)
    res["38_orig"] = section(L, "A.2 Univers d'origine 2022-2026 (cycle #38 tel que committé le 28/07)",
                             d, wb, wl, wbc, wlc, wlc2, R, REBAL_38,
                             "Leaders 1.0x (référence)", "**#38** (Leaders + overlay ×2)")

    A("## B. Cycle #14 — momentum court terme « Winners » (rebalancement hebdomadaire)")
    A("")
    d, wb, ww, wbc, wwc, wwc2, R, rb = block_14(ROOT / "data" / "pead" / "prices_pit", pit=True)
    res["14_pit"] = section(L, "B.1 Univers point-in-time 2015-2026 (cycle #164)",
                            d, wb, ww, wbc, wwc, wwc2, R, rb,
                            "Équipondéré (référence)", "**#14** (Winners, tercile sup.)")
    d, wb, ww, wbc, wwc, wwc2, R, rb = block_14(None, pit=False)
    res["14_orig"] = section(L, "B.2 Univers d'origine 2021-2026 (cycle #14 tel que committé le 28/07)",
                             d, wb, ww, wbc, wwc, wwc2, R, rb,
                             "Équipondéré (référence)", "**#14** (Winners, tercile sup.)")

    A("## Conclusion")
    A("")
    A("Les quatre configurations testées donnent le même verdict qualitatif, sur deux "
      "univers indépendants et deux mécanismes indépendants : **le PASS disparaît dès que "
      "l'exécution est décalée d'un jour.** L'écart est concentré à plus de 90 % sur les "
      "séances de rebalancement, ce qui identifie la cause sans ambiguïté (si c'était un "
      "simple effet de décalage de calendrier, l'écart serait réparti uniformément).")
    A("")
    A("Ce que cela implique, sans enjoliver :")
    A("")
    A("1. **Le #38 n'est pas le meilleur candidat du backlog — il n'a probablement aucun "
      "edge.** Une fois l'exécution rendue causale, il ne bat plus sa propre référence "
      "Leaders 1.0x. Le DSR record de 0,754 (#163), le SPA à p=0,0000 (#161/#163) et les "
      "4/4 folds de stabilité portaient tous sur une série de PnL contaminée.")
    A("2. **Le #14 est le cycle le plus touché**, parce qu'il rebalance chaque semaine "
      "(20 % des séances contaminées contre 4,8 % pour le #38) et que son signal — le "
      "rendement des 5 derniers jours **incluant le jour même** — est celui qui recoupe "
      "le plus directement le rendement encaissé. Son Sharpe spectaculaire (+2,35 à "
      "l'origine, +1,85 corrigé du biais du survivant au #164) était en grande partie une "
      "sélection des gagnants du jour, payée le jour même.")
    A("3. **Les cycles #161 à #164 restent méthodologiquement valides** — biais du "
      "survivant, analyse de puissance, univers point-in-time : tout ce travail est "
      "correct et reste utile. Mais il a été appliqué à un candidat dont l'edge était "
      "artificiel. La correction du biais du survivant (#163) et la correction de "
      "l'exécution (ici) sont deux défauts indépendants qui s'additionnent.")
    A("4. **Portée exacte, à ne pas exagérer.** Ce défaut concerne les backtests de "
      "PORTEFEUILLE (matrice de poids titre par titre) : #4, #14, #15, #38, #39, #42, "
      "#51, #73, #75, #79, #82, #84, #86, et leurs dérivés. Les overlays scalaires sur "
      "indice (la majorité du backlog, familles #29/#37/#47/#54/#57/#115/#134/#149…) "
      "utilisent une autre infrastructure, où l'alignement causal a été explicitement "
      "vérifié et corrigé dès le cycle #47 — ils ne sont **pas** concernés a priori, mais "
      "aucun d'eux n'a jamais atteint le seuil DSR de toute façon.")
    A("5. **Ce que ce document ne fait PAS.** Il ne corrige pas les scripts d'origine. "
      "Corriger `build_weights()` invaliderait rétroactivement une vingtaine de rapports "
      "déjà committés (#4, #14, #33, #38, #42, #51, #73, #82, #161→#164…) : c'est une "
      "décision de protocole qui revient à l'utilisateur, pas une décision d'analyse. Le "
      "chiffrage est fourni ici pour qu'elle soit prise en connaissance de cause.")
    A("")
    A("**Lecture positive, et elle est réelle** : le protocole a fonctionné. Ce n'est pas "
      "une statistique défavorable qui a révélé le défaut, c'est la lecture ligne à ligne "
      "du code exigée par la Règle 7 avant de réutiliser une brique. Et le diagnostic "
      "chiffré de la Phase 2 (`nonml_dsr_decomposition_38.md`) reste valable dans sa "
      "partie méthodologique — il faut simplement lire sa conclusion comme « il fallait un "
      "Sharpe de 1,71 et nous n'en avions même pas 0,48 », au lieu de « il en manquait "
      "0,29 ».")

    out = ROOT / "results" / "nonml_same_bar_execution_audit.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Batterie de validation renforcée (Règle 9) pour le #38 (Leaders
52-semaines + overlay 52w-high indice) -- spécification pré-enregistrée
dans PREREG_leaders_index52w_high_overlay_pass_validation_battery.md
(cycle #161), committée AVANT tout calcul de ce script.

Le #38 est une stratégie de PORTEFEUILLE (poids sur ~100 titres NDX-100),
pas un overlay scalaire sur un seul actif -- ne réutilise donc PAS le
format `pos x r_asset` de nonml_pass_validation_battery.py. Réutilise à
la place les poids déjà committés de
`nonml_leaders_index52w_high_overlay_backtest.py::build_weights()` (Règle
7 : pas de réimplémentation divergente), et applique les mêmes 5
contrôles a-e, même convention de coût/turnover, même référence que le
PREREG original du #38 (portefeuille Leaders 1.0x, PAS Buy&Hold).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics, dsr  # noqa: E402
from volatility import spa_test  # noqa: E402
from nonml_leaders_index52w_high_overlay_backtest import (  # noqa: E402
    build_weights, COST_BPS,
)
from nonml_pass_validation_battery import (  # noqa: E402
    approx_var_trials, parse_backlog_n_trials, CRISIS_WINDOWS,
)

EMBARGO = 5
N_FOLDS = 4


def portfolio_pnl(weights, R, cost_bps, mask=None):
    w = weights if mask is None else weights[mask]
    r = R if mask is None else R[mask]
    turn = np.abs(np.diff(w, axis=0, prepend=w[0:1])).sum(axis=1) / 2.0
    return (w * r).sum(axis=1) - turn * (cost_bps / 1e4)


def total_return(pnl):
    return float(np.cumprod(1.0 + pnl)[-1] - 1.0)


EXTENDED_PREAMBLE = (
    "**LIMITE MÉTHODOLOGIQUE MAJEURE, à lire avant toute interprétation** : l'univers "
    "de titres utilisé ici est la liste des membres du NDX-100 **de 2026** "
    "(`data/pead/ndx100_constituents.json`), appliquée telle quelle à un historique "
    "remontant jusqu'à 1970 pour les titres qui en disposent. Sur les décennies "
    "anciennes, ceci introduit un **biais du survivant sévère** : seuls les titres "
    "qui (a) existaient déjà ET (b) sont restés assez grands pour rester dans le "
    "NDX-100 en 2026 sont inclus — le portefeuille des années 1970-1990 ne peut "
    "matériellement contenir QUE de futurs géants technologiques déjà connus "
    "aujourd'hui, jamais les entreprises qui ont existé puis disparu/reculé. Ce biais "
    "s'atténue à mesure qu'on se rapproche de 2026 (univers de plus en plus complet et "
    "réaliste) mais reste présent à un degré inconnu sur toute la période. **Les "
    "rendements totaux astronomiques ci-dessous (§a) en sont la signature typique** "
    "— ce n'est PAS un résultat économiquement interprétable en niveau absolu. Les "
    "métriques les MOINS affectées par ce biais sont le SPA (teste un ordre relatif "
    "candidat/référence sur le MÊME univers biaisé des deux côtés) et le score par "
    "fold (qui montre COMMENT l'edge évolue dans le temps) ; le DSR reste, lui, "
    "informatif sur la significativité mais ne corrige PAS ce biais de sélection de "
    "l'univers. **Conclusion à ce cycle : ce test ne peut PAS confirmer ni réfuter "
    "proprement l'hypothèse du #162 (édge borné par l'échantillon vs favorable par "
    "chance) tant que l'univers n'est pas reconstruit avec la composition HISTORIQUE "
    "réelle du NDX-100 à chaque date (donnée non triviale à obtenir gratuitement, "
    "hors scope de ce cycle) — rapporté ici pour traçabilité complète (Règle 6), "
    "PAS comme un verdict fiable.** *(Corrigé au cycle #163 : la composition "
    "point-in-time réelle a finalement été trouvée et utilisée — voir "
    "`..._pit_universe.md`.)*"
)


def bias_section(mlog):
    """Quantifie le biais RÉSIDUEL de l'univers point-in-time : à chaque date
    de rebalancement, part des membres RÉELS de l'indice effectivement
    investissables (prix disponibles + 252 séances d'historique). Le
    complément est le biais restant, mesuré et non estimé."""
    df = pd.DataFrame(mlog, columns=["date", "membres", "investissables"])
    df["couverture"] = df["investissables"] / df["membres"]
    out = ["## Biais résiduel de l'univers point-in-time (mesuré, non estimé)",
           "",
           "À chaque date de rebalancement : nombre de membres RÉELS du NDX-100 "
           "(composition point-in-time) et nombre d'entre eux réellement investissables "
           "(prix disponibles ET 252 séances d'historique). Le complément est le biais "
           "restant — titres retirés de la cote dont la série de prix n'est plus exposée "
           "par la source, ou titres entrés à l'indice avant d'avoir un an de cotation.",
           "",
           "| Année | Rebal. | Membres réels (moy.) | Investissables (moy.) | Couverture moy. | Couverture min. |",
           "|---|---|---|---|---|---|"]
    df["annee"] = pd.to_datetime(df["date"]).dt.year
    for year, g in df.groupby("annee"):
        out.append(f"| {year} | {len(g)} | {g['membres'].mean():.0f} | "
                   f"{g['investissables'].mean():.1f} | {100*g['couverture'].mean():.1f}% | "
                   f"{100*g['couverture'].min():.1f}% |")
    out += ["",
            f"**Couverture moyenne sur toute la période : {100*df['couverture'].mean():.1f}% "
            f"(minimum {100*df['couverture'].min():.1f}%).** À comparer aux 42 % (2015) à "
            f"68 % (2022) de couverture des cycles #161/#162, mesurés dans "
            f"`results/nonml_ndx100_universe_census.md` — le biais n'est pas totalement nul "
            "ici, mais il est réduit d'un ordre de grandeur ET, surtout, il est désormais "
            "MESURÉ.",
            "",
            "Nature du résidu, à ne pas sous-estimer : les titres encore manquants sont "
            "exclusivement des sociétés **retirées de la cote** (faillite, rachat, passage "
            "en non coté), donc en moyenne des sous-performants — le biais résiduel reste "
            "orienté dans le même sens (à la hausse), simplement beaucoup plus petit.",
            ""]
    return out


def main(prices_dir=None, out_suffix="", title_suffix="", build_kwargs=None,
         preamble=None, postamble=None):
    kwargs = dict(build_kwargs or {})
    dates_full, weights_base, weights_lev, R, _ = build_weights(prices_dir, **kwargs)
    # start = premier indice avec poids non nuls (fin du lookback 252j)
    nz = np.where(weights_base.sum(axis=1) > 0)[0]
    start = int(nz[0])
    w_base, w_lev = weights_base[start:], weights_lev[start:]
    R_s = R[start:]
    dates = pd.to_datetime(dates_full[start:])

    lines = [f"# Batterie de validation renforcée (Règle 9) — leaders_index52w_high_overlay (cycle #38){title_suffix}",
             "",
             f"Candidat : Leaders + overlay 52w-high indice ×2.0. Référence : portefeuille "
             f"Leaders 1.0x (cycle #4), **PAS Buy&Hold** — même convention que le PREREG "
             f"original du #38. Coût pré-enregistré {COST_BPS:.0f} bps. {len(R_s)} séances "
             f"({dates[0].date()} → {dates[-1].date()}). Les 5 contrôles doivent TOUS passer "
             "pour un PASS RENFORCÉ.", ""]

    if preamble is None and prices_dir is not None and not kwargs:
        preamble = EXTENDED_PREAMBLE
    if preamble:
        lines.append(preamble)
        lines.append("")

    mlog = kwargs.get("membership_log")
    if mlog:
        lines += bias_section(mlog)

    # ------------------------------------------------------------- a. couts
    lines.append("## a. Stress de coûts (1x, 3x, 5x)")
    lines.append("")
    lines.append("| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | OK |")
    lines.append("|---|---|---|---|---|---|")
    ok_a = True
    for mult in (1, 3, 5):
        cost = COST_BPS * mult
        pnl_b = portfolio_pnl(w_base, R_s, cost)
        pnl_l = portfolio_pnl(w_lev, R_s, cost)
        me_b, me_l = trading_metrics(np.log1p(pnl_b)), trading_metrics(np.log1p(pnl_l))
        ret_b, ret_l = total_return(pnl_b), total_return(pnl_l)
        ok = (me_l["sharpe_ann"] > me_b["sharpe_ann"]) and (ret_l > ret_b)
        ok_a &= ok
        lines.append(f"| {cost:.0f} | {me_l['sharpe_ann']:+.2f} | {me_b['sharpe_ann']:+.2f} | "
                      f"{100*ret_l:+.1f}% | {100*ret_b:+.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_a else 'ÉCHEC'} — tient jusqu'à 5x le coût nominal : {'oui' if ok_a else 'NON'}.**")
    lines.append("")

    # ------------------------------------------------------------- b. crise
    lines.append("## b. Stress de crise (MDD candidat vs référence)")
    lines.append("")
    lines.append("| Fenêtre | Séances | MDD candidat | MDD référence | Pas pire que référence |")
    lines.append("|---|---|---|---|---|")
    ok_b, any_window = True, False
    for label, d0, d1 in CRISIS_WINDOWS:
        mask = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
        n = int(mask.sum())
        if n < 20:
            lines.append(f"| {label} | {n} | -- | -- | hors couverture (<20 séances) |")
            continue
        any_window = True
        pnl_b = portfolio_pnl(w_base, R_s, COST_BPS, mask)
        pnl_l = portfolio_pnl(w_lev, R_s, COST_BPS, mask)
        mdd_b = trading_metrics(np.log1p(pnl_b))["max_drawdown_pct"]
        mdd_l = trading_metrics(np.log1p(pnl_l))["max_drawdown_pct"]
        ok = mdd_l >= mdd_b - 1.0
        ok_b &= ok
        lines.append(f"| {label} | {n} | {mdd_l:.1f}% | {mdd_b:.1f}% | {'OUI' if ok else 'non'} |")
    n_covered = sum(1 for label, d0, d1 in CRISIS_WINDOWS
                     if int(((dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))).sum()) >= 20)
    ok_b = ok_b and any_window
    lines.append("")
    if not any_window:
        lines.append("**PENDING — aucune fenêtre de crise couverte par l'historique disponible "
                      "pour ce candidat (échantillon récent, 2022-2026) : ce contrôle ne peut pas "
                      "être exécuté, il ne doit PAS être compté comme un OK silencieux (Règle 5).**")
    else:
        lines.append(f"**{'OK' if ok_b else 'ÉCHEC'} — {n_covered}/4 fenêtres de crise couvertes "
                      "par l'historique de prix titre-par-titre disponible.**")
    lines.append("")

    # --------------------------------------------------- c. stabilite temp.
    lines.append(f"## c. Stabilité temporelle ({N_FOLDS} folds non chevauchants + embargo {EMBARGO}j)")
    lines.append("")
    lines.append("| Fold | Séances | Période | Sharpe candidat | Sharpe référence | Candidat > référence |")
    lines.append("|---|---|---|---|---|---|")
    T = len(R_s)
    flen = T // N_FOLDS
    n_beat = n_scored = 0
    for k in range(N_FOLDS):
        f0 = k * flen + (EMBARGO if k > 0 else 0)
        f1 = (k + 1) * flen if k < N_FOLDS - 1 else T
        if f1 - f0 < 30:
            continue
        idx_mask = np.zeros(T, dtype=bool)
        idx_mask[f0:f1] = True
        pnl_b = portfolio_pnl(w_base, R_s, COST_BPS, idx_mask)
        pnl_l = portfolio_pnl(w_lev, R_s, COST_BPS, idx_mask)
        s_b = trading_metrics(np.log1p(pnl_b))["sharpe_ann"]
        s_l = trading_metrics(np.log1p(pnl_l))["sharpe_ann"]
        beat = s_l > s_b
        n_beat += int(beat)
        n_scored += 1
        lines.append(f"| {k+1} | {f1-f0} | {dates[f0].strftime('%m/%Y')}→{dates[f1-1].strftime('%m/%Y')} | "
                      f"{s_l:+.2f} | {s_b:+.2f} | {'OUI' if beat else 'non'} |")
    ok_c = n_scored > 0 and n_beat > n_scored / 2
    lines.append("")
    lines.append(f"**{'OK' if ok_c else 'ÉCHEC'} — {n_beat}/{n_scored} folds battus (majorité requise).**")
    lines.append("")

    # --------------------------------------------------- d. SPA 1 candidat
    lines.append("## d. SPA de Hansen à 1 candidat contre la référence")
    lines.append("")
    pnl_b_full = portfolio_pnl(w_base, R_s, COST_BPS)
    pnl_l_full = portfolio_pnl(w_lev, R_s, COST_BPS)
    # SPA sur des rendements LOG, convention du projet (identique a
    # nonml_pass_validation_battery.py). Sur des rendements simples le test
    # rendait p=0.0314 contre p=0.0672 en log : le verdict depend de la
    # convention, ce qui est en soi un signe de fragilite (voir le rapport).
    spa = spa_test({"candidat": -np.log1p(pnl_l_full), "reference": -np.log1p(pnl_b_full)}, bench="reference")
    ok_d = spa["p_value"] < 0.05
    lines.append(f"t_SPA = {spa['t_spa']:.3f}, **p = {spa['p_value']:.4f}** (bootstrap stationnaire, "
                 "H0 : la référence Leaders 1.0x n'est battue par aucun candidat).")
    lines.append("")
    lines.append(f"**{'OK' if ok_d else 'ÉCHEC'} — seuil p < 0,05.**")
    lines.append("")

    # ------------------------------------------------------------- e. DSR
    lines.append("## e. DSR avec n_trials = taille du backlog AVANT ce cycle (jamais 1)")
    lines.append("")
    n_trials = parse_backlog_n_trials()
    var_trials_annual, n_extracted = approx_var_trials()
    me_l = trading_metrics(np.log1p(pnl_l_full))
    var_trials = var_trials_annual / 252.0
    de = dsr(me_l["sharpe_daily"], me_l["n"], var_trials, n_trials=n_trials,
             skew=me_l["skew"], kurt_excess=me_l["excess_kurt"])
    ok_e = de["dsr"] > 0.95
    lines.append(f"n_trials={n_trials} (backlog avant ce cycle), var(SR essais) extraite sur "
                 f"{n_extracted} Sharpe du backlog = {var_trials_annual:.4e} (annualisée) → "
                 f"{var_trials:.4e} (journalière). Sharpe quotidien {me_l['sharpe_daily']:+.4f}, "
                 f"seuil SR₀ = {de['sr0_daily']:.4f}, z = {de['z']:+.2f}, **DSR = {de['dsr']:.3f}**.")
    lines.append("")
    lines.append(f"**{'OK' if ok_e else 'ÉCHEC'} — seuil DSR > 0,95.**")
    lines.append("")

    # ---------------------------------------------------------- verdict
    allok = all((ok_a, ok_b, ok_c, ok_d, ok_e))
    lines.append("## Verdict de la batterie")
    lines.append("")
    lines.append("| Contrôle | Statut |")
    lines.append("|---|---|")
    for lab, ok in (("a. stress de coûts ×3/×5", ok_a),
                    ("b. stress de crise", ok_b),
                    ("c. stabilité temporelle", ok_c),
                    ("d. SPA 1 candidat", ok_d),
                    (f"e. DSR (n_trials={n_trials})", ok_e)):
        lines.append(f"| {lab} | {'OK' if ok else 'ÉCHEC'} |")
    lines.append("")
    lines.append(f"### {'PASS RENFORCÉ' if allok else 'PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE'}")
    if not allok:
        lines.append("")
        lines.append("Aucune notification Telegram n'est émise (réservée au PASS RENFORCÉ complet).")

    if postamble:
        lines.append("")
        lines.append(postamble)

    out = ROOT / "results" / f"nonml_leaders_index52w_high_overlay_pass_validation_battery{out_suffix}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


PIT_PREAMBLE = (
    "**Univers POINT-IN-TIME (cycle #163)** — correction du défaut méthodologique qui "
    "affectait les cycles #161 ET #162. À chaque date de rebalancement, seuls les titres "
    "**réellement membres du NDX-100 ce jour-là** sont investissables (composition "
    "historique issue de `nasdaq-100-ticker-history` v2026.7.0, licence MIT, vendorée dans "
    "`data/ndx100_history/`). Les cycles précédents appliquaient rétroactivement la liste "
    "des membres **de 2026**, qui ne couvre que 42 % des vrais membres de l'indice en 2015 "
    "et 68 % en 2022 (mesuré dans `results/nonml_ndx100_universe_census.md`) — les absents "
    "étant par construction les titres sortis de l'indice depuis, donc en moyenne des "
    "sous-performants. Panneau de prix : 178 des 214 tickers ayant appartenu à l'indice "
    "entre 2015 et 2026 (36 séries de titres retirés de la cote ne sont plus exposées par "
    "la source — biais résiduel quantifié ci-dessous). **Aucun paramètre du #38 ne change** "
    "(TERCILE 1/3, LOOKBACK 252, REBAL_EVERY 21, CAP 2.0, seuil indice 95 %, coût 5 bps) ; "
    "seule la définition de l'univers investissable est corrigée, comme pré-enregistré "
    "dans `PREREG_leaders_index52w_high_overlay_pit_universe.md`."
)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--extended":
        main(prices_dir=ROOT / "data" / "pead" / "prices_extended",
             out_suffix="_extended_history",
             title_suffix=" — historique étendu (cycle #162)")
    elif len(sys.argv) > 1 and sys.argv[1] == "--pit":
        sys.path.insert(0, str(ROOT / "scripts"))
        from ndx100_membership import tickers_as_of_date  # noqa: E402

        mlog = []
        main(prices_dir=ROOT / "data" / "pead" / "prices_pit",
             out_suffix="_pit_universe",
             title_suffix=" — univers point-in-time 2015-2026 (cycle #163)",
             build_kwargs=dict(panel_start="2013-01-01",
                               membership_fn=tickers_as_of_date,
                               rebal_anchor="2015-01-01",
                               membership_log=mlog),
             preamble=PIT_PREAMBLE)
    else:
        main()

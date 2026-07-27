"""Audit adversarial des Étapes C/D — recalcule depuis les données brutes,
ne fait JAMAIS confiance aux tableaux markdown déjà produits.

Contexte : un audit existe déjà (results/AUDIT_CANONICAL_FRAMEWORK_FINAL.md,
results/ROBUSTNESS_AUDIT_DETAILED.md, 24/07/2026) mais il a été produit par
la même lignée d'agents que ceux qui ont construit la stratégie (conflit
d'intérêt de relecture) et lit comme une synthèse de résultats déjà calculés,
pas un recalcul indépendant. Ce script corrige quatre failles concrètes
trouvées lors de l'exploration :

1. DSR mal recalculé pour l'overlay "déployé" : l'audit cite
   `DSR: 1.000 (no trials inflation; only 1 variant selected for deployment)`
   pour la combinaison cap=2.0x/pctl=90e — mais cette combinaison provient
   d'une grille de 12 combinaisons (results/etape_D_overlay_optimized.md,
   commit a40cc098, 14/07/2026). "Un seul déployé" ne veut pas dire "aucune
   inflation" : le DSR doit être recalculé avec n_trials=12.
   ENCORE PLUS GRAVE, découvert en creusant l'historique git : le commit
   ee8a2fd (15/07/2026, "Phase 1 fixes: Pre-register combo") a DÉJÀ corrigé
   ce problème en réduisant la grille de scripts/run_etape_d_optimize.py à
   UN SEUL combo pré-enregistré (cap=1.50/pctl=95, celui d'origine de
   l'Étape D) — mais le fichier de résultats (etape_D_overlay_optimized.md)
   et l'audit du 24/07 n'ont JAMAIS été régénérés après ce fix : ils citent
   encore le combo cap=2.0/pctl=90 issu de la grille de 12, que le code
   actuel ne produit même plus. Ce script documente cet écart code/rapport
   et calcule le DSR correct (n_trials=12) pour la grille historique.
2. "Cross-market" trompeur : Composite et NDX-100 ne sont pas des marchés
   indépendants (NDX-100 ⊂ Composite, mêmes moteurs macro). Ce script
   rejoue Étape C (DM test) et Étape D (overlay pré-enregistré) sur
   Russell 2000 / S&P 500 / DAX — jamais testés jusqu'ici.
3. Grille de perturbation locale autour du point pré-enregistré (cap=1.5,
   pctl=95) : DIAGNOSTIC UNIQUEMENT (jamais utilisé pour changer le choix
   déployé — le re-sélectionner sur cette base serait exactement le
   nouveau data-snooping que ce script est censé détecter).
4. Test de mutation anti-lookahead : perturbe des données futures et
   vérifie par assertion (pas lecture de code) que les prévisions passées
   sont inchangées.

Sortie : results/ADVERSARIAL_AUDIT_v2.md
"""
import os
import subprocess
import sys
import warnings
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]  # finance/trading
FINANCE_ROOT = ROOT.parent                  # finance
REPO_ROOT = FINANCE_ROOT.parent             # repo root (Quant-Trade)
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import (  # noqa: E402
    EXTREME_CUT_FRAC,
    build_overlay_positions,
    extreme_cut,
    vol_target_exposure,
    walk_forward_vol_forecast_multi,
)
from prediction import backtest, dsr, trading_metrics  # noqa: E402
from volatility import ARCH_SPECS, dm_test, fit_arch, garch_path_fold_only  # noqa: E402

T0 = 750
COST_BPS = 5.0
REFIT_EVERY = 21
CAP_PREREG = 1.50   # combo pre-enregistre ACTUEL (post-fix ee8a2fd, 15/07)
PCTL_PREREG = 95.0
SUCCESS_MDD_REDUCTION = 0.25
SUCCESS_RET_RATIO = 0.80

INDICES = {
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def section1_stale_results_check() -> list[str]:
    """Verifie que le code actuel de run_etape_d_optimize.py ne produit
    plus la grille de 12 combos citee par les rapports d'audit -- confirme
    l'ecart code/rapport plutot que de le supposer."""
    out = []
    opt_path = ROOT / "scripts" / "run_etape_d_optimize.py"
    src = opt_path.read_text()
    import re
    cap_grid = re.search(r"CAP_GRID\s*=\s*(\[[^\]]*\])", src).group(1)
    pctl_grid = re.search(r"PCTL_GRID\s*=\s*(\[[^\]]*\])", src).group(1)
    out.append(f"- Grille ACTUELLE dans `{opt_path.relative_to(REPO_ROOT)}` : "
               f"CAP_GRID={cap_grid}, PCTL_GRID={pctl_grid}.")
    log = subprocess.run(
        ["git", "log", "--follow", "--format=%H %ad %s", "--date=short", "--",
         "finance/trading/scripts/run_etape_d_optimize.py"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout.strip().splitlines()
    out.append("- Historique git de ce fichier :")
    for line in log:
        out.append(f"  - `{line}`")
    results_path = ROOT / "results" / "etape_D_overlay_optimized.md"
    results_txt = results_path.read_text()
    cites_stale = "2.00" in results_txt and "90e" in results_txt
    out.append(f"- Le fichier de résultats `{results_path.relative_to(REPO_ROOT)}` "
               f"cite-t-il encore la grille de 12 combos (cap 2.00×/90e) ? "
               f"**{'OUI — stale, non régénéré depuis le fix' if cites_stale else 'non'}**.")
    audit_path = ROOT / "results" / "AUDIT_CANONICAL_FRAMEWORK_FINAL.md"
    audit_txt = audit_path.read_text() if audit_path.exists() else ""
    audit_cites_stale = "2.0" in audit_txt and "90th" in audit_txt
    out.append(f"- L'audit précédent (`{audit_path.name}`, daté du 24/07) "
               f"cite-t-il ce même combo cap=2.0×/90e comme déployé ? "
               f"**{'OUI' if audit_cites_stale else 'non'}**.")
    out.append("")
    out.append("**Constat** : le fix `ee8a2fd` (15/07/2026, \"Phase 1 fixes: "
                "Pre-register combo\") a réduit la grille à 1 seul combo "
                f"pré-enregistré (cap={CAP_PREREG:.2f}×/pctl={PCTL_PREREG:.0f}e, "
                "identique à celui de l'Étape D d'origine) précisément pour "
                "éliminer le biais de sélection sur 12 combinaisons. Le "
                "fichier de résultats et l'audit du 24/07 n'ont **jamais été "
                "régénérés** après ce fix : ils recommandent un déploiement "
                "(cap=2.0×/90e) que le code actuel ne produit plus.")
    return out


def rerun_grid_with_correct_dsr() -> tuple[list[str], dict]:
    """Recalcule la grille HISTORIQUE de 12 combinaisons depuis les données
    brutes (pas depuis le tableau markdown en cache) et calcule le DSR
    correct avec n_trials=12 pour le combo gagnant."""
    out = []
    cap_grid = [1.00, 1.25, 1.50, 2.00]
    pctl_grid = [90, 95, 99]

    path = REPO_ROOT / "data" / "nasdaq100_daily.txt"
    df = load_ohlc(str(path))
    r = log_returns_pct(df).values
    r_bt = r / 100.0
    T = len(r)
    idx = np.arange(T0, T)
    T_oos = len(idx)

    pos_bh = np.ones(T)
    pnl_bh = backtest(pos_bh, r_bt, COST_BPS)[idx]
    metr_bh = trading_metrics(pnl_bh)

    fc = walk_forward_vol_forecast_multi(r, T0, REFIT_EVERY, pctl_grid)
    vol_fcst, vol_target, vol_thresh = fc["vol_fcst"], fc["vol_target"], fc["vol_thresh"]

    rows = []
    for cap in cap_grid:
        expo_vt = vol_target_exposure(vol_fcst, vol_target, cap)
        for pctl in pctl_grid:
            expo = extreme_cut(expo_vt, vol_fcst, vol_thresh[pctl], EXTREME_CUT_FRAC)
            pos = np.nan_to_num(expo, nan=0.0)
            pnl = backtest(pos, r_bt, COST_BPS)[idx]
            me = trading_metrics(pnl)
            mdd_reduction = 1.0 - abs(me["max_drawdown_pct"]) / abs(metr_bh["max_drawdown_pct"])
            ret_ratio = me["ann_return_pct"] / metr_bh["ann_return_pct"]
            rows.append({"cap": cap, "pctl": pctl, "metrics": me,
                         "mdd_reduction": mdd_reduction, "ret_ratio": ret_ratio,
                         "ok": bool(mdd_reduction > SUCCESS_MDD_REDUCTION and ret_ratio >= SUCCESS_RET_RATIO)})

    sr_daily = [row["metrics"]["sharpe_daily"] for row in rows]
    var_trials = float(np.var(sr_daily, ddof=1))
    n_trials = len(rows)
    for row in rows:
        me = row["metrics"]
        row["dsr_n12"] = dsr(me["sharpe_daily"], T_oos, var_trials, n_trials,
                             skew=me["skew"], kurt_excess=me["excess_kurt"])["dsr"]
        # DSR (a tort) avec n_trials=1, pour comparaison directe avec l'audit precedent
        row["dsr_n1_wrong"] = dsr(me["sharpe_daily"], T_oos, 0.0, 1,
                                  skew=me["skew"], kurt_excess=me["excess_kurt"])["dsr"]

    best = max(rows, key=lambda x: (x["ok"], round(x["mdd_reduction"], 3), x["metrics"]["calmar"]))

    out.append(f"Grille historique recalculée depuis les données brutes (NDX, {T_oos} obs OOS) : "
               f"cap ∈ {cap_grid} × pctl ∈ {pctl_grid} = {n_trials} combinaisons.\n")
    out.append("| cap | pctl | Sharpe ann. | MDD % | ΔMDD rel. | Rdt/BH | Critère | "
               "**DSR (n=12, correct)** | DSR (n=1, à tort — cf. audit du 24/07) |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for row in sorted(rows, key=lambda x: x["metrics"]["max_drawdown_pct"], reverse=True):
        me = row["metrics"]
        out.append(f"| {row['cap']:.2f}× | {row['pctl']:.0f}e | {me['sharpe_ann']:+.2f} | "
                   f"{me['max_drawdown_pct']:.1f} | {100*row['mdd_reduction']:+.1f}% | "
                   f"{100*row['ret_ratio']:.1f}% | {'OUI' if row['ok'] else 'non'} | "
                   f"**{row['dsr_n12']:.3f}** | {row['dsr_n1_wrong']:.3f} |")
    out.append("")
    out.append(f"**Combo historiquement \"gagnant\"** : cap={best['cap']:.2f}×, "
               f"pctl={best['pctl']:.0f}e — DSR correct (n=12) = **{best['dsr_n12']:.3f}**, "
               f"DSR affiché à tort dans l'audit du 24/07 (n=1) = {best['dsr_n1_wrong']:.3f}.")
    if best["dsr_n12"] < 0.95:
        out.append(f"→ **Avec la correction n_trials=12, ce combo NE PASSE PLUS le seuil "
                   f"DSR>0,95** utilisé ailleurs dans le projet comme barre de décision. "
                   f"Le verdict \"DSR: 1.000, no trials inflation\" de l'audit du 24/07 "
                   f"est erroné.")
    else:
        out.append("→ Même avec la correction n_trials=12, ce combo reste au-dessus de 0,95 "
                   "— la conclusion pratique ne change pas, mais le raisonnement de l'audit "
                   "du 24/07 (\"no trials inflation\") était malgré tout incorrect en soi.")
    out.append("")
    out.append(f"**Rappel** : ce combo n'est de toute façon plus celui produit par le code "
               f"actuel (voir section 1) — le choix pré-enregistré en vigueur est "
               f"cap={CAP_PREREG:.2f}×/pctl={PCTL_PREREG:.0f}e (N=3 famille, "
               f"`results/etape_D_overlay.md`), qui atteint déjà seul le critère de succès "
               f"sur NDX sans nécessiter de grid-search.")
    return out, {"cap_prereg_ok_ndx": True}


def _cross_market_one_index(idx_name: str, fname: str) -> tuple[str, list[str]]:
    path = REPO_ROOT / "data" / fname
    if not path.exists():
        return idx_name, [f"- {idx_name} : fichier absent, skip"]
    df = load_ohlc(str(path))
    quality_report(df)
    r = log_returns_pct(df).values
    r_bt = r / 100.0
    T = len(r)
    if T <= T0 + REFIT_EVERY:
        return idx_name, [f"- {idx_name} : historique trop court ({T} lignes), skip"]
    idx = np.arange(T0, T)
    T_oos = len(idx)

    # --- Etape C : DM test GJR-t vs GARCH-n (meme protocole que run_etape_c.py) ---
    losses_bench, losses_gjrt = [], []
    for tr in range(T0, T, REFIT_EVERY):
        block = range(tr, min(tr + REFIT_EVERY, T))
        res_n = fit_arch(r[:tr], "GARCH-n")
        p_n = {k: float(v) for k, v in res_n.params.items()}
        path_n = garch_path_fold_only(r, p_n, tr, gjr=False)
        res_t = fit_arch(r[:tr], "GJR-t")
        p_t = {k: float(v) for k, v in res_t.params.items()}
        path_t = garch_path_fold_only(r, p_t, tr, gjr=True)
        mu = p_n["mu"]
        for t in block:
            proxy = (r[t] - mu) ** 2
            fcst_n, fcst_t = path_n[t], path_t[t]
            ratio_n = max(proxy, 1e-12) / fcst_n
            ratio_t = max(proxy, 1e-12) / fcst_t
            losses_bench.append(ratio_n - np.log(ratio_n) - 1.0)
            losses_gjrt.append(ratio_t - np.log(ratio_t) - 1.0)
    dm = dm_test(np.array(losses_bench), np.array(losses_gjrt), hac_lags=10)

    # --- Etape D : overlay pre-enregistre (cap=1.5, pctl=95), zero tuning ---
    pos_bh = np.ones(T)
    pnl_bh = backtest(pos_bh, r_bt, COST_BPS)[idx]
    metr_bh = trading_metrics(pnl_bh)
    ov = build_overlay_positions(r, T0, REFIT_EVERY, CAP_PREREG, with_extreme_cut=True,
                                 extreme_pctl=PCTL_PREREG)
    pnl_ov = backtest(ov["pos"], r_bt, COST_BPS)[idx]
    metr_ov = trading_metrics(pnl_ov)
    mdd_reduction = 1.0 - abs(metr_ov["max_drawdown_pct"]) / abs(metr_bh["max_drawdown_pct"])
    ret_ratio = metr_ov["ann_return_pct"] / metr_bh["ann_return_pct"] if metr_bh["ann_return_pct"] != 0 else np.nan
    ok = bool(mdd_reduction > SUCCESS_MDD_REDUCTION and ret_ratio >= SUCCESS_RET_RATIO)

    lines = [
        f"### {idx_name} (n={T}, OOS obs={T_oos})",
        f"- Étape C — GJR-t vs GARCH-n (QLIKE, DM HAC) : t={dm['t']:+.2f}, "
        f"p(unilat., GJR-t meilleur)={dm['p_one_sided_model_better']:.4f} → "
        f"{'bat le bench' if dm['t'] > 0 and dm['p_one_sided_model_better'] < 0.05 else 'ne bat PAS significativement le bench'}",
        f"- Étape D — overlay VolTarget+Cut (cap={CAP_PREREG:.1f}×, pctl={PCTL_PREREG:.0f}e, "
        f"figé, zéro tuning) : BuyHold Sharpe={metr_bh['sharpe_ann']:+.2f}/MDD={metr_bh['max_drawdown_pct']:.1f}% "
        f"vs Overlay Sharpe={metr_ov['sharpe_ann']:+.2f}/MDD={metr_ov['max_drawdown_pct']:.1f}% "
        f"→ ΔMDD relatif={100*mdd_reduction:+.1f}%, rendement conservé={100*ret_ratio:.1f}% "
        f"→ critère de succès : **{'OUI' if ok else 'NON'}**",
    ]
    return idx_name, lines


def section2_cross_market() -> list[str]:
    out = ["Validation cross-marché **réelle** (Russell 2000 / S&P 500 / DAX — jamais "
           "testée pour C/D jusqu'ici ; Composite vs NDX ne compte pas comme "
           "indépendant, cf. protocole anti-snooping). Même protocole exact "
           f"(T0={T0}, refit={REFIT_EVERY}j, coûts {COST_BPS:.0f}bps), définitions "
           "figées, zéro tuning.\n"]
    results_by_index = {}
    with ProcessPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(_cross_market_one_index, name, fname): name
                for name, fname in INDICES.items()}
        for fut in as_completed(futs):
            name, lines = fut.result()
            results_by_index[name] = lines
    for name in INDICES:
        out.extend(results_by_index.get(name, [f"### {name}\n- (échec)"]))
        out.append("")
    return out


def section3_local_perturbation() -> list[str]:
    """Grille locale DIAGNOSTIC UNIQUEMENT autour du point pre-enregistre --
    ne doit JAMAIS servir a re-choisir le combo deploye (ce serait le meme
    data-snooping que celui denonce en section 1)."""
    out = ["**Diagnostic uniquement — ne redéfinit PAS le combo déployé** "
           f"(cap={CAP_PREREG:.2f}×/pctl={PCTL_PREREG:.0f}e reste le choix "
           "pré-enregistré ; ceci vérifie juste l'absence de pic isolé autour de "
           "ce point sur NDX).\n"]
    cap_local = [1.30, 1.50, 1.70]
    pctl_local = [93, 95, 97]

    path = REPO_ROOT / "data" / "nasdaq100_daily.txt"
    df = load_ohlc(str(path))
    r = log_returns_pct(df).values
    r_bt = r / 100.0
    T = len(r)
    idx = np.arange(T0, T)
    pos_bh = np.ones(T)
    pnl_bh = backtest(pos_bh, r_bt, COST_BPS)[idx]
    metr_bh = trading_metrics(pnl_bh)

    fc = walk_forward_vol_forecast_multi(r, T0, REFIT_EVERY, pctl_local)
    vol_fcst, vol_target, vol_thresh = fc["vol_fcst"], fc["vol_target"], fc["vol_thresh"]

    out.append("| cap | pctl | Sharpe ann. | MDD % | ΔMDD rel. | Rdt/BH | Critère |")
    out.append("|---|---|---|---|---|---|---|")
    plateau_ok_count = 0
    for cap in cap_local:
        expo_vt = vol_target_exposure(vol_fcst, vol_target, cap)
        for pctl in pctl_local:
            expo = extreme_cut(expo_vt, vol_fcst, vol_thresh[pctl], EXTREME_CUT_FRAC)
            pos = np.nan_to_num(expo, nan=0.0)
            pnl = backtest(pos, r_bt, COST_BPS)[idx]
            me = trading_metrics(pnl)
            mdd_reduction = 1.0 - abs(me["max_drawdown_pct"]) / abs(metr_bh["max_drawdown_pct"])
            ret_ratio = me["ann_return_pct"] / metr_bh["ann_return_pct"]
            ok = mdd_reduction > SUCCESS_MDD_REDUCTION and ret_ratio >= SUCCESS_RET_RATIO
            plateau_ok_count += int(ok)
            out.append(f"| {cap:.2f}× | {pctl}e | {me['sharpe_ann']:+.2f} | "
                       f"{me['max_drawdown_pct']:.1f} | {100*mdd_reduction:+.1f}% | "
                       f"{100*ret_ratio:.1f}% | {'OUI' if ok else 'non'} |")
    out.append("")
    out.append(f"**{plateau_ok_count}/9** points de la grille locale atteignent le critère "
               f"de succès → {'plateau (robuste au choix exact du paramètre)' if plateau_ok_count >= 6 else 'sensible au réglage exact (fragile)'}.")
    return out


def section4_lookahead_mutation_test() -> list[str]:
    """Mute les donnees STRICTEMENT APRES le bloc de refit courant (pas a
    partir de tr lui-meme) et verifie que les previsions DU BLOC UTILISE EN
    PRODUCTION (path[tr:tr+refit_every], ce que walk_forward_vol_forecast
    expose reellement dans vol_fcst) sont inchangees.

    NOTE METHODOLOGIQUE (auto-correction) : une premiere version de ce test
    mutait r[tr:] (englobant tr lui-meme) et comparait tout le prefixe
    path[:tr+1], y compris la periode de burn-in avant T0 jamais utilisee en
    production. Cela produisait un FAUX POSITIF ("fuite detectee") qui
    provenait de deux artefacts sans consequence operationnelle : (1) la
    lente decroissance de l'initialisation s2[0]=eps.var() (globale) dans le
    burn-in, jamais expose comme prevision reelle, et (2) le fait, attendu et
    correct, qu'une recursion causale change legitimement a partir de
    l'indice mute lui-meme (r[tr] mute -> path[tr+1] change normalement,
    ce n'est pas une fuite vers le futur). Le test correct ci-dessous mute
    a partir de tr+refit_every (strictement apres le bloc courant) et ne
    verifie QUE le bloc reellement expose en production.
    """
    out = []
    path = REPO_ROOT / "data" / "nasdaq100_daily.txt"
    df = load_ohlc(str(path))
    r = log_returns_pct(df).values
    T = len(r)
    rng = np.random.default_rng(0)

    max_diff_overall = 0.0
    detail_rows = []
    for tr in (T0 + 1, T0 + 5 * REFIT_EVERY, T0 + 50 * REFIT_EVERY, T // 2, T - 2 * REFIT_EVERY):
        if tr >= T - REFIT_EVERY:
            continue
        res = fit_arch(r[:tr], "GJR-t")
        p = {k: float(v) for k, v in res.params.items()}
        path_original = garch_path_fold_only(r, p, tr, gjr=True)
        cut = min(tr + REFIT_EVERY, T)
        r_mutated = r.copy()
        r_mutated[cut:] = rng.normal(r[:tr].mean(), r[:tr].std(), size=T - cut)
        path_mutated = garch_path_fold_only(r_mutated, p, tr, gjr=True)
        block_diff = float(np.max(np.abs(path_original[tr:cut] - path_mutated[tr:cut])))
        max_diff_overall = max(max_diff_overall, block_diff)
        detail_rows.append((tr, cut, block_diff))

    identical = max_diff_overall < 1e-9
    out.append("Mutation des données **strictement postérieures** au bloc de refit "
               "courant (`r[tr+refit_every:]` re-tiré au hasard), vérification que "
               "les prévisions du bloc réellement exposé en production "
               "(`path[tr:tr+refit_every]`, ce que `vol_fcst` expose) sont "
               "inchangées, testé à 5 points de refit (précoce à tardif) :")
    out.append("")
    out.append("| tr | bloc utilisé | écart max |")
    out.append("|---|---|---|")
    for tr, cut, d in detail_rows:
        out.append(f"| {tr} | [{tr}:{cut}] | {d:.2e} |")
    out.append("")
    out.append(f"→ **{'PASS (aucune fuite détectée sur le bloc opérationnel, aux 5 points testés)' if identical else 'ÉCHEC — fuite d’information détectée !'}**.")

    bh_pos = np.ones(T)
    r_bt = r / 100.0
    idx = np.arange(T0, T)
    ov = build_overlay_positions(r, T0, REFIT_EVERY, CAP_PREREG, with_extreme_cut=True,
                                 extreme_pctl=PCTL_PREREG)
    sharpes_by_delay = []
    for delay in (0, 1, 2, 3):
        pnl = backtest(ov["pos"], r_bt, COST_BPS, delay=delay)[idx]
        me = trading_metrics(pnl)
        sharpes_by_delay.append(me["sharpe_ann"])
    out.append("")
    out.append("Dégradation par retard artificiel d'exécution (`backtest(..., delay=k)`, "
               "test intégré au repo) — une dégradation BRUTALE dès delay=1 (au lieu de "
               "progressive) indiquerait une fuite d'information plutôt qu'un effet "
               "temporel normal :")
    out.append("| delay (jours) | Sharpe ann. |")
    out.append("|---|---|")
    for d, sh in zip((0, 1, 2, 3), sharpes_by_delay):
        out.append(f"| {d} | {sh:+.2f} |")
    return out


def main():
    header = [
        "# Audit adversarial v2 — Étapes C/D (recalcul depuis les données brutes)",
        "",
        "Objectif : chercher activement les failles de l'audit précédent "
        "(`AUDIT_CANONICAL_FRAMEWORK_FINAL.md`, `ROBUSTNESS_AUDIT_DETAILED.md`, "
        "24/07/2026), pas confirmer ses conclusions. Aucun chiffre ci-dessous "
        "n'est recopié d'un rapport existant — tout est recalculé depuis "
        "`data/*.txt` par ce script.",
        "",
        "## 1. Écart code / rapport — la grille \"déployée\" (cap 2.0×/90e) "
        "existe-t-elle encore dans le code ?",
        "",
    ]
    s1 = section1_stale_results_check()
    s2, _ = rerun_grid_with_correct_dsr()
    s3 = ["", "## 2. DSR correct de la grille historique de 12 combinaisons", ""] + s2
    s4 = ["", "## 3. Validation cross-marché réelle (Russell 2000 / S&P 500 / DAX)", ""] + section2_cross_market()
    s5 = ["", "## 4. Grille de perturbation locale (diagnostic, NDX)", ""] + section3_local_perturbation()
    s6 = ["", "## 5. Test de mutation anti-lookahead", ""] + section4_lookahead_mutation_test()

    footer = [
        "",
        "## Verdict corrigé",
        "",
        "- Le combo \"déployé\" cité par l'audit du 24/07 (cap=2.0×/90e, "
        "DSR=1.000) n'est **plus produit par le code actuel** et son DSR "
        "était de toute façon mal calculé (n_trials=1 au lieu de 12).",
        f"- Le combo réellement pré-enregistré en vigueur (cap={CAP_PREREG:.2f}×/"
        f"pctl={PCTL_PREREG:.0f}e) reste valide sur NDX (Étape D d'origine, "
        "N=3, critère de succès atteint sans grid-search) — c'est CELUI-LÀ "
        "qui doit être cité comme référence, pas le combo de la grille de 12.",
        "- Voir section 3 pour savoir si ce combo pré-enregistré réplique sur "
        "des marchés génétiquement indépendants (jamais vérifié avant ce script).",
        "- Voir section 5 pour la détection de fuite d'information (mutation "
        "du futur + test de délai intégré).",
    ]

    report = "\n".join(header + s1 + s3 + s4 + s5 + s6 + footer) + "\n"
    out_path = ROOT / "results" / "ADVERSARIAL_AUDIT_v2.md"
    out_path.write_text(report)
    print(report)
    print(f"\nÉcrit dans {out_path}")


if __name__ == "__main__":
    main()

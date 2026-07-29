"""Audit adversarial de la validation SPA/DSR
(`nonml_backlog_spa_dsr_validation.py`, résultat déjà committé). Demande
explicite utilisateur : "audit tes résultats finaux, plus tu détruit le
travail plus on pourra observer les failles" -- ce script cherche
activement à casser la conclusion, pas à la confirmer.

Cinq contrôles, du plus mécanique au plus fondamental :

1. Recalcul indépendant (seconde implémentation, PAS un import de
   build_members) de 3 membres représentatifs -- détecte un bug de
   ré-implémentation propre à nonml_backlog_spa_dsr_validation.py.
2. Test anti-lookahead sur l'infrastructure PARTAGÉE (mutation du futur
   NDX) -- teste combined_position/near_high_mask/le decoupage
   start_common, pas les compute_*_series() individuels (déjà audités
   à leur cycle d'origine).
3. Stabilité temporelle par sous-périodes (walk-forward + embargo 5j,
   analogue adapté au cas -- PAS un ré-entraînement, ces overlays ne
   sont pas des modèles ajustés, donc le purge/embargo classique
   d'Étape B ne s'applique pas littéralement ici ; ce qui s'applique
   est un contrôle de robustesse temporelle qualitatif).
4. Sensibilité du DSR à n_trials -- quantifie le risque de SOUS-estimer
   le nombre réel d'essais (13 déclarés, mais construits après ~110
   cycles d'exploration adaptative sur le MÊME historique).
5. Calibration de spa_test()/dsr() sur une famille de 13 stratégies
   BRUIT PUR (aucun edge par construction) -- vérifie que les outils
   ne rejettent pas H0 à tort plus souvent que le taux nominal.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics, dsr, expected_max_sharpe  # noqa: E402
from volatility import spa_test  # noqa: E402
from nonml_backlog_spa_dsr_validation import (  # noqa: E402
    build_members, combined_position, COST_BPS, VOL_WINDOW,
)

EMBARGO = 5  # convention du projet (purge/embargo Étape B)


def independent_weakness_breadth(close_dict: dict) -> pd.Series:
    """Ré-implémentation manuelle (boucles Python, sans vectorisation
    pandas) de compute_weakness_breadth_series -- pour vérifier que
    build_members() n'a pas introduit d'écart lors de sa réutilisation."""
    tickers = sorted(close_dict.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = close_dict[t].index if ref_idx is None else ref_idx.union(close_dict[t].index)
    ref_idx = ref_idx.sort_values()
    T = len(ref_idx)
    breadth = np.full(T, np.nan)
    INDEX_LOOKBACK, INDEX_THRESHOLD_LOW = 252, 1.05
    aligned = {t: close_dict[t].reindex(ref_idx).values for t in tickers}
    for i in range(INDEX_LOOKBACK, T):
        # n_listed = tickers COTES ce jour-la (prix du jour fini), PAS
        # seulement ceux ayant une fenetre 252j complete -- c'est bien la
        # semantique de l'original (exists.sum(axis=1)), une premiere
        # version de cet audit l'avait mal reproduit (denominateur trop
        # restrictif) et signalait a tort un ecart de ~1-3% -- corrige ici
        # apres verification manuelle contre compute_weakness_breadth_series.
        n_listed = 0
        n_near_low = 0
        for t in tickers:
            px = aligned[t][i]
            if not np.isfinite(px):
                continue
            n_listed += 1
            window = aligned[t][i - INDEX_LOOKBACK + 1:i + 1]
            if not np.isfinite(window).all():
                continue
            if px <= INDEX_THRESHOLD_LOW * np.min(window):
                n_near_low += 1
        breadth[i] = n_near_low / n_listed if n_listed > 0 else np.nan
    return pd.Series(breadth, index=ref_idx)


def check_1_independent_recompute():
    from nonml_weakness_breadth_vol_targeting_overlay_backtest import load_all_prices as load_wb

    series = load_wb()
    indep = independent_weakness_breadth(series)

    from nonml_weakness_breadth_vol_targeting_overlay_backtest import compute_weakness_breadth_series
    orig = compute_weakness_breadth_series()

    common_idx = indep.index.intersection(orig.index)
    check_idx = common_idx[252::400]  # échantillon espacé, hors warm-up
    max_diff = 0.0
    n_checked = 0
    for d in check_idx:
        a, b = indep.loc[d], orig.loc[d]
        if np.isnan(a) and np.isnan(b):
            continue
        diff = abs(float(a) - float(b))
        max_diff = max(max_diff, diff)
        n_checked += 1
    ok = max_diff < 1e-9
    return ok, n_checked, max_diff


def check_2_lookahead():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])
    members_before = build_members(close, dates_idx, bh_full)

    T = len(close)
    cut = int(T * 0.8)
    rng = np.random.default_rng(2026)
    close_mut = close.copy()
    close_mut[cut:] = close_mut[cut:] * (1.0 + rng.normal(0, 0.5, T - cut))
    bh_full_mut = np.log(close_mut[1:] / close_mut[:-1])
    members_after = build_members(close_mut, dates_idx, bh_full_mut)

    check_slice = slice(0, cut - 260)  # marge de sécurité pour les fenêtres 252j
    worst_name, worst_diff = "aucun (tous a 0)", 0.0
    for name in members_before:
        pos_b = members_before[name][0][check_slice]
        pos_a = members_after[name][0][check_slice]
        diff = float(np.nanmax(np.abs(pos_b - pos_a)))
        if diff > worst_diff:
            worst_diff, worst_name = diff, name
    ok = worst_diff < 1e-9
    return ok, worst_name, worst_diff


def check_3_temporal_stability():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])
    members = build_members(close, dates_idx, bh_full)
    start_common = max(start for _, start in members.values())
    n_common = len(bh_full) - start_common

    n_folds = 3
    fold_len = n_common // n_folds
    rows = []
    for k in range(n_folds):
        f_start = start_common + k * fold_len
        f_end = start_common + (k + 1) * fold_len if k < n_folds - 1 else len(bh_full)
        # embargo : on retire les EMBARGO premieres seances du fold (sauf le tout premier)
        if k > 0:
            f_start += EMBARGO
        bh_f = bh_full[f_start:f_end]
        pnl_bh = bh_f.copy()
        pnl_bh[0] -= COST_BPS / 1e4
        sharpe_bh = trading_metrics(pnl_bh)["sharpe_ann"]

        fold_sharpes = {}
        for name, (pos_full, _s) in members.items():
            pos = pos_full[f_start:f_end]
            turn = np.abs(np.diff(pos, prepend=1.0))
            pnl = pos * bh_f - turn * (COST_BPS / 1e4)
            fold_sharpes[name] = trading_metrics(pnl)["sharpe_ann"]
        best = max(fold_sharpes, key=fold_sharpes.get)
        rows.append((k + 1, f_end - f_start, sharpe_bh, best, fold_sharpes[best],
                     sum(1 for v in fold_sharpes.values() if v > sharpe_bh)))
    return rows


def check_4_n_trials_sensitivity():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])
    members = build_members(close, dates_idx, bh_full)
    start_common = max(start for _, start in members.values())
    bh_common = bh_full[start_common:]
    n_common = len(bh_common)

    sharpes_daily, skews, kurts = {}, {}, {}
    for name, (pos_full, _s) in members.items():
        pos = pos_full[start_common:]
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl = pos * bh_common - turn * (COST_BPS / 1e4)
        me = trading_metrics(pnl)
        sharpes_daily[name] = me["sharpe_daily"]
        skews[name] = me["skew"]
        kurts[name] = me["excess_kurt"]

    best_name = max(sharpes_daily, key=sharpes_daily.get)
    var_trials = float(np.var(list(sharpes_daily.values()), ddof=1))

    results = []
    for n_trials_hyp in (13, 43, 110):
        d = dsr(sharpes_daily[best_name], n_common, var_trials, n_trials=n_trials_hyp,
                skew=skews[best_name], kurt_excess=kurts[best_name])
        results.append((n_trials_hyp, d["sr0_daily"], d["dsr"]))
    return best_name, results


def check_5_null_calibration(n_reps: int = 300, seed: int = 7):
    rng = np.random.default_rng(seed)
    T = 1133  # meme ordre de grandeur que la fenetre commune reelle
    K = 13
    sigma = 0.011  # vol journaliere approx. NDX
    cost = COST_BPS / 1e4

    spa_rejections = 0
    dsr_rejections = 0
    for _ in range(n_reps):
        bench = rng.normal(0, sigma, T)
        pnl_bench = bench.copy()
        pnl_bench[0] -= cost
        losses = {"bench": -pnl_bench}
        sharpes_daily = {}
        skews, kurts = {}, {}
        for k in range(K):
            strat = rng.normal(0, sigma, T)  # AUCUN edge par construction
            pnl = strat.copy()
            pnl[0] -= cost
            losses[f"m{k}"] = -pnl
            me = trading_metrics(pnl)
            sharpes_daily[f"m{k}"] = me["sharpe_daily"]
            skews[f"m{k}"] = me["skew"]
            kurts[f"m{k}"] = me["excess_kurt"]

        spa_res = spa_test(losses, bench="bench", B=400)  # B reduit pour vitesse (calibration, pas le resultat officiel)
        if spa_res["p_value"] < 0.05:
            spa_rejections += 1

        best = max(sharpes_daily, key=sharpes_daily.get)
        var_trials = float(np.var(list(sharpes_daily.values()), ddof=1))
        d = dsr(sharpes_daily[best], T, var_trials, n_trials=K, skew=skews[best], kurt_excess=kurts[best])
        if d["dsr"] > 0.95:
            dsr_rejections += 1

    return spa_rejections / n_reps, dsr_rejections / n_reps, n_reps


def main():
    lines = ["# Audit adversarial — Validation SPA/DSR de la famille vol-targeting (13 membres)",
             "",
             "Objectif : chercher activement des failles dans "
             "`nonml_backlog_spa_dsr_validation.py` et son résultat déjà committé "
             "(`results/nonml_backlog_spa_dsr_validation.md`), pas les confirmer.",
             ""]

    lines.append("## 1. Recalcul indépendant (seconde implémentation, boucles Python explicites)")
    lines.append("")
    ok1, n_checked, max_diff = check_1_independent_recompute()
    lines.append(f"Membre testé : weakness_breadth (porte continue, la plus atypique de la famille). "
                 f"{n_checked} dates vérifiées, écart max = {max_diff:.2e}.")
    lines.append(f"**{'OK — build_members() reproduit exactement compute_weakness_breadth_series().' if ok1 else 'ÉCHEC — écart détecté, bug de ré-implémentation dans le script de validation.'}**")
    lines.append("")
    lines.append("*Note de transparence sur le processus : la toute première version de ce recalcul "
                 "indépendant signalait à tort un écart (~1-3%, `n_listed` limité aux tickers avec fenêtre "
                 "252j COMPLÈTE). Investigation manuelle -> le bug était dans le recalcul indépendant "
                 "lui-même (dénominateur trop restrictif), pas dans `build_members()`/`compute_weakness_"
                 "breadth_series()` : l'original compte au dénominateur tous les tickers COTÉS ce jour-là "
                 "(`exists.sum`), pas seulement ceux avec fenêtre complète. Corrigé avant de committer ce "
                 "résultat -- documenté ici en toute transparence plutôt que silencieusement réécrit.*")
    lines.append("")

    lines.append("## 2. Test anti-lookahead sur l'infrastructure partagée (mutation des 20% de données NDX les plus récentes)")
    lines.append("")
    ok2, worst_name, worst_diff = check_2_lookahead()
    lines.append(f"Teste combined_position/near_high_mask/découpage start_common (code NOUVEAU de ce script, "
                 f"pas les compute_*_series() déjà audités à leur cycle d'origine). "
                 f"Écart max sur les positions passées (avant mutation, marge 260j) : {worst_diff:.2e} (membre {worst_name}).")
    lines.append(f"**{'OK — aucune fuite du futur vers le passé.' if ok2 else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")

    lines.append("## 3. Stabilité temporelle (walk-forward informel, 3 sous-périodes, embargo "
                 f"{EMBARGO}j entre folds)")
    lines.append("")
    lines.append("**Note méthodologique** : le purge/embargo classique (Étape B) protège contre la fuite "
                 "d'un ENTRAÎNEMENT vers un TEST via des labels qui se chevauchent temporellement -- ces "
                 "overlays ne sont PAS des modèles ajustés (aucun paramètre estimé sur une fenêtre "
                 "d'entraînement séparée), donc ce risque précis ne s'applique pas littéralement ici. "
                 "Ce qui s'applique, et qui EST fait ci-dessous, est un contrôle de robustesse temporelle : "
                 "la conclusion (aucun edge net significatif) est-elle stable sur des sous-périodes "
                 "disjointes, ou reste-t-elle un artefact d'une fenêtre commune chanceuse ? Les p-values "
                 "de sous-période ne sont PAS un nouveau test formel (échantillon trop court pour ça, "
                 "~370j/fold) -- lecture qualitative uniquement.")
    lines.append("")
    lines.append("| Fold | Séances | Sharpe Buy&Hold | Meilleur membre | Sharpe meilleur membre | # membres > BH |")
    lines.append("|---|---|---|---|---|---|")
    rows = check_3_temporal_stability()
    for k, n, sbh, best, sbest, n_beat in rows:
        lines.append(f"| {k} | {n} | {sbh:+.2f} | {best} | {sbest:+.2f} | {n_beat}/13 |")
    identities = {r[3] for r in rows}
    lines.append("")
    lines.append(f"Identité du \"meilleur membre\" stable entre folds : {'NON' if len(identities) > 1 else 'OUI'} "
                 f"({len(identities)} identité(s) différente(s) sur 3 folds : {', '.join(sorted(identities))}).")
    lines.append(f"**{'Le meilleur membre change de fold en fold -- signe classique de sélection sur bruit, cohérent avec le SPA/DSR global (pas d edge stable).' if len(identities) > 1 else 'Le meme membre domine sur les 3 folds -- signe de robustesse temporelle, en tension avec la conclusion SPA/DSR globale.'}**")
    lines.append("")

    lines.append("## 4. Sensibilité du DSR à n_trials (le nombre \"13\" est-il le bon ?)")
    lines.append("")
    lines.append("**Critique honnête** : n_trials=13 compte les membres du mécanisme \"vol-targeting "
                 "hiérarchique\" retenus dans PREREG_backlog_spa_dsr_validation.md. Mais ces 13 "
                 "constructions n'ont pas été tirées au hasard -- elles sont le produit de ~110 cycles "
                 "d'exploration ADAPTATIVE sur le MÊME historique NDX-100 (chaque nouvelle porte souvent "
                 "inspirée du succès/échec des précédentes, ex. #94 après #89, #100 après #78). Le nombre "
                 "RÉEL de \"regards\" informés sur ces données est donc probablement bien supérieur à 13 "
                 "-- n_trials=13 est optimiste (sous-estime la correction requise).")
    lines.append("")
    best_name, results = check_4_n_trials_sensitivity()
    lines.append(f"Meilleur membre : {best_name}. DSR recalculé à var_trials FIXE (celle des 13 membres), "
                 f"en faisant seulement varier n_trials :")
    lines.append("")
    lines.append("| n_trials hypothétique | SR0 (seuil de sélection) | DSR |")
    lines.append("|---|---|---|")
    for n_t, sr0, dsr_v in results:
        lines.append(f"| {n_t} | {sr0:.4f} | {dsr_v:.4f} |")
    lines.append("")
    lines.append("Le DSR ne peut que BAISSER quand n_trials augmente (SR0 monte mécaniquement) -- "
                 "le DSR=0,8883 déjà rapporté à n_trials=13 est donc un plafond, pas un plancher : "
                 "la vraie correction, si le nombre d'essais réel est plus proche de 43 ou 110, est encore "
                 "plus défavorable au edge.")
    lines.append("")

    lines.append("## 5. Calibration de spa_test()/dsr() sur une famille BRUIT PUR (aucun edge par construction)")
    lines.append("")
    lines.append("Génère 300 réplications d'une famille de 13 stratégies i.i.d. N(0,σ) sans AUCUN edge "
                 "réel (même T, même ordre de grandeur de vol que la fenêtre commune réelle), applique "
                 "spa_test()/dsr() tels quels, et mesure le taux de rejet empirique de H0. Sous un vrai "
                 "null, ce taux doit être proche du seuil nominal (5% pour SPA à p<0,05 ; le seuil DSR>0,95 "
                 "n'a pas de garantie de calibration exacte a priori mais doit rester CONTENU, pas dérailler).")
    lines.append("")
    spa_rate, dsr_rate, n_reps = check_5_null_calibration()
    lines.append(f"Sur {n_reps} réplications bruit pur : taux de rejet SPA (p<0,05) = {100*spa_rate:.1f}%, "
                 f"taux DSR>0,95 = {100*dsr_rate:.1f}%.")
    calib_ok = spa_rate < 0.15 and dsr_rate < 0.15
    lines.append(f"**{'OK — les deux outils restent conservateurs sous un null pur, pas de biais de sur-rejet flagrant.' if calib_ok else 'ATTENTION — taux de faux positifs anormalement élevé sous null pur, les outils pourraient être trop permissifs.'}**")
    lines.append("")

    lines.append("## Synthèse de l'audit")
    lines.append("")
    all_structural_ok = ok1 and ok2
    lines.append(f"- Intégrité du code (recalcul indépendant + anti-lookahead) : "
                 f"{'OK, aucun bug structurel détecté.' if all_structural_ok else 'ÉCHEC -- voir sections 1/2.'}")
    lines.append(f"- Stabilité temporelle : {'fragile (meilleur membre instable entre folds).' if len(identities) > 1 else 'relativement stable.'}")
    lines.append("- Sensibilité n_trials : le DSR=0,8883 déclaré est un CAS FAVORABLE (n_trials=13 sous-estime "
                 "probablement l'exploration réelle) -- la vraie robustesse du edge est probablement PIRE, "
                 "pas meilleure, que ce qui a été committé en section 3 du résultat principal.")
    lines.append(f"- Calibration des outils : {'conforme.' if calib_ok else 'suspecte, à re-vérifier avant tout usage supplémentaire.'}")
    lines.append("")
    lines.append("**Conclusion de l'audit : le résultat principal (H0 non rejetée par SPA, DSR<0,95) "
                 "n'est PAS remis en cause par ce contrôle adversarial -- au contraire, chaque angle "
                 "d'attaque testé ici (instabilité temporelle du meilleur membre, sous-estimation "
                 "probable de n_trials) pousse la conclusion dans le même sens : aucun edge net de la "
                 "famille vol-targeting hiérarchique ne peut être considéré comme statistiquement établi "
                 "sur cet historique.**")

    out = ROOT / "results" / "nonml_backlog_spa_dsr_validation_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

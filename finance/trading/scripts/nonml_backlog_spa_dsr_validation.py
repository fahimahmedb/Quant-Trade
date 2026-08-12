"""Validation SPA + DSR de la famille des 13 overlays vol-targeting
hiérarchiques du backlog non-ML (spécification pré-enregistrée dans
PREREG_backlog_spa_dsr_validation.md, committée avant ce script).

Réimporte les fonctions compute_*_series() et constantes déjà
committées de chacun des 13 scripts de backtest individuels — aucune
réimplémentation divergente. Duplique fidèlement la construction de
porte de chaque main() déjà committé, pour en extraire le pnl quotidien
sur une fenêtre commune, au lieu de l'écrire sur disque comme le fait
chaque script individuel.
"""
import re
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

COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    """Formule identique et partagée par les 13 scripts individuels."""
    gate_r = gate_aligned[:-1]
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    pos = np.where(gate_r, vt_exposure, 1.0)
    return np.nan_to_num(pos, nan=1.0)


def build_members(close, dates_idx, bh_full):
    """Reconstruit (pos_full, start) pour chacun des 13 membres figés,
    en dupliquant fidèlement la logique de porte du main() déjà
    committé de chaque script individuel."""
    members = {}

    # 1. dispersion cross-sectionnelle (#78)
    from nonml_dispersion_vol_targeting_overlay_backtest import (
        compute_dispersion_series, MEDIAN_WINDOW as MW1,
    )
    s = compute_dispersion_series()
    med = s.rolling(MW1).median()
    gate_series = (s >= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    pos_full = combined_position(bh_full, gate_aligned)
    valid = gate_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)
    members["dispersion"] = (pos_full, max(first_valid, VOL_WINDOW))

    # 2. weakness breadth (#89) -- porte CONTINUE (fraction), pas seuillee,
    # reproduite telle quelle (np.where sur un float : True ssi != 0)
    from nonml_weakness_breadth_vol_targeting_overlay_backtest import (
        compute_weakness_breadth_series, INDEX_LOOKBACK as IL2,
    )
    b = compute_weakness_breadth_series()
    b_raw = b.reindex(dates_idx.values, method="ffill").values
    b_aligned = np.nan_to_num(b_raw, nan=0.0)
    pos_full = combined_position(bh_full, b_aligned)
    first_valid = int(np.argmax(~np.isnan(b_raw)))
    members["weakness_breadth"] = (pos_full, max(first_valid, IL2, VOL_WINDOW))

    # 3. régime de corrélation (#90)
    from nonml_correlation_regime_vol_targeting_overlay_backtest import (
        compute_avg_correlation_series, MEDIAN_WINDOW as MW3,
    )
    s = compute_avg_correlation_series()
    med = s.rolling(MW3).median()
    gate_series = (s <= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    pos_full = combined_position(bh_full, gate_aligned)
    valid = gate_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)
    members["correlation_regime"] = (pos_full, max(first_valid, VOL_WINDOW))

    # 4. breadth momentum 12-1 mois (#94)
    from nonml_momentum_breadth_vol_targeting_overlay_backtest import (
        compute_momentum_breadth_series, LOOKBACK as LB4, BREADTH_THRESHOLD as BT4,
    )
    b = compute_momentum_breadth_series()
    b_raw = b.reindex(dates_idx.values, method="ffill").values
    b_aligned = np.nan_to_num(b_raw, nan=0.0)
    gate_aligned = b_aligned >= BT4
    pos_full = combined_position(bh_full, gate_aligned)
    first_valid = int(np.argmax(~np.isnan(b_raw)))
    members["momentum_breadth"] = (pos_full, max(first_valid, LB4, VOL_WINDOW))

    # 5. breadth SMA200 (#96)
    from nonml_sma200_breadth_vol_targeting_overlay_backtest import (
        compute_sma200_breadth_series, SMA_WINDOW as SW5, BREADTH_THRESHOLD as BT5,
    )
    b = compute_sma200_breadth_series()
    b_raw = b.reindex(dates_idx.values, method="ffill").values
    b_aligned = np.nan_to_num(b_raw, nan=0.0)
    gate_aligned = b_aligned >= BT5
    pos_full = combined_position(bh_full, gate_aligned)
    first_valid = int(np.argmax(~np.isnan(b_raw)))
    members["sma200_breadth"] = (pos_full, max(first_valid, SW5, VOL_WINDOW))

    # 6. breadth nette avance/déclin (#97)
    from nonml_net_breadth_vol_targeting_overlay_backtest import (
        compute_net_breadth_series, INDEX_LOOKBACK as IL6,
    )
    b = compute_net_breadth_series()
    b_raw = b.reindex(dates_idx.values, method="ffill").values
    gate_aligned = np.where(np.isnan(b_raw), False, b_raw > 0.0)
    pos_full = combined_position(bh_full, gate_aligned)
    first_valid = int(np.argmax(~np.isnan(b_raw)))
    members["net_breadth"] = (pos_full, max(first_valid, IL6, VOL_WINDOW))

    # 7. AND : SMA200 breadth ET momentum breadth (#98)
    from nonml_sma200_breadth_vol_targeting_overlay_backtest import (
        compute_sma200_breadth_series as csma7, SMA_WINDOW as SW7, BREADTH_THRESHOLD as SBT7,
    )
    from nonml_momentum_breadth_vol_targeting_overlay_backtest import (
        compute_momentum_breadth_series as cmom7, LOOKBACK as LB7, BREADTH_THRESHOLD as MBT7,
    )
    sma_raw = csma7().reindex(dates_idx.values, method="ffill").values
    mom_raw = cmom7().reindex(dates_idx.values, method="ffill").values
    sma_gate = np.nan_to_num(sma_raw, nan=0.0) >= SBT7
    mom_gate = np.nan_to_num(mom_raw, nan=0.0) >= MBT7
    gate_aligned = sma_gate & mom_gate
    pos_full = combined_position(bh_full, gate_aligned)
    fv_sma = int(np.argmax(~np.isnan(sma_raw)))
    fv_mom = int(np.argmax(~np.isnan(mom_raw)))
    members["sma200_momentum_and"] = (pos_full, max(fv_sma, fv_mom, SW7, LB7, VOL_WINDOW))

    # 8. concentration cross-sectionnelle (#99)
    from nonml_market_concentration_vol_targeting_overlay_backtest import (
        compute_concentration_series, MEDIAN_WINDOW as MW8,
    )
    s = compute_concentration_series()
    med = s.rolling(MW8).median()
    gate_series = (s <= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    pos_full = combined_position(bh_full, gate_aligned)
    valid = gate_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)
    members["concentration"] = (pos_full, max(first_valid, VOL_WINDOW))

    # 9. dispersion des scores de momentum (#100)
    from nonml_momentum_dispersion_vol_targeting_overlay_backtest import (
        compute_momentum_dispersion_series, MEDIAN_WINDOW as MW9,
    )
    s = compute_momentum_dispersion_series()
    med = s.rolling(MW9).median()
    gate_series = (s >= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    pos_full = combined_position(bh_full, gate_aligned)
    valid = gate_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)
    members["momentum_dispersion"] = (pos_full, max(first_valid, VOL_WINDOW))

    # 10. position continue dans le range 252j (#104)
    from nonml_range_position_vol_targeting_overlay_backtest import (
        compute_range_position_series, MEDIAN_WINDOW as MW10,
    )
    s = compute_range_position_series()
    med = s.rolling(MW10).median()
    gate_series = (s >= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    pos_full = combined_position(bh_full, gate_aligned)
    valid = gate_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)
    members["range_position"] = (pos_full, max(first_valid, VOL_WINDOW))

    # 11. AND : dispersion momentum ET tendance 52w-high (#106)
    from nonml_momentum_dispersion_vol_targeting_overlay_backtest import (
        compute_momentum_dispersion_series as cdisp11, MEDIAN_WINDOW as MW11,
    )
    from nonml_trend_vol_targeting_overlay_backtest import near_high_mask, INDEX_LOOKBACK as IL11
    trend_gate = near_high_mask(close)
    disp = cdisp11()
    med = disp.rolling(MW11).median()
    disp_gate_series = (disp >= med)
    disp_gate_raw = disp_gate_series.reindex(dates_idx.values, method="ffill")
    disp_gate_aligned = disp_gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    gate_combined = trend_gate & disp_gate_aligned
    pos_full = combined_position(bh_full, gate_combined)
    valid = disp_gate_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)
    members["momentum_dispersion_trend_and"] = (pos_full, max(first_valid, IL11, VOL_WINDOW))

    # 12. dispersion des betas individuels (#109)
    from nonml_beta_dispersion_vol_targeting_overlay_backtest import (
        compute_beta_dispersion_series, MEDIAN_WINDOW as MW12,
    )
    s = compute_beta_dispersion_series()
    med = s.rolling(MW12).median()
    gate_series = (s >= med)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    pos_full = combined_position(bh_full, gate_aligned)
    valid = gate_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)
    members["beta_dispersion"] = (pos_full, max(first_valid, VOL_WINDOW))

    # 13. breadth interne générale
    from nonml_internal_breadth_vol_targeting_overlay_backtest import (
        compute_breadth_series, INDEX_LOOKBACK as IL13,
    )
    b = compute_breadth_series()
    b_raw = b.reindex(dates_idx.values, method="ffill").values
    b_aligned = np.nan_to_num(b_raw, nan=0.0)
    pos_full = combined_position(bh_full, b_aligned)
    first_valid = int(np.argmax(~np.isnan(b_raw)))
    members["internal_breadth"] = (pos_full, max(first_valid, IL13, VOL_WINDOW))

    return members


def approx_dsr_full_backlog():
    """DSR secondaire, approximatif et explicitement caveaté, sur les
    43/110 entrées du backlog dont le Sharpe est extractible par regex.
    Univers hétérogène (mécanismes différents) -- indicatif seulement."""
    backlog = (ROOT / "NONML_STRATEGY_BACKLOG.md").read_text()
    pairs = re.findall(r"Sharpe\s+([+-][0-9.,]+)\s*→\s*([+-][0-9.,]+)", backlog)
    sharpes_after = []
    for _, after in pairs:
        try:
            sharpes_after.append(float(after.rstrip(",").replace(",", ".")))
        except ValueError:
            continue
    if len(sharpes_after) < 2:
        return None
    sharpes_after = np.array(sharpes_after)
    best_sr = float(sharpes_after.max())
    var_trials = float(np.var(sharpes_after, ddof=1))
    n_trials = len(sharpes_after)
    return best_sr, var_trials, n_trials


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    members = build_members(close, dates_idx, bh_full)
    start_common = max(start for _, start in members.values())

    bh_common = bh_full[start_common:]
    pnl_bh = bh_common.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh = trading_metrics(pnl_bh)
    ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)

    losses = {}
    sharpes = {}
    sharpes_daily = {}
    skews = {}
    kurts = {}
    rets = {}
    mdds = {}
    n_common = len(bh_common)
    for name, (pos_full, _start) in members.items():
        pos = pos_full[start_common:]
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl = pos * bh_common - turn * (COST_BPS / 1e4)
        me = trading_metrics(pnl)
        sharpes[name] = me["sharpe_ann"]
        sharpes_daily[name] = me["sharpe_daily"]
        skews[name] = me["skew"]
        kurts[name] = me["excess_kurt"]
        rets[name] = float(np.exp(pnl.sum()) - 1.0)
        mdds[name] = me["max_drawdown_pct"]
        losses[name] = -pnl

    losses["BuyHold"] = -pnl_bh
    sharpes["BuyHold"] = me_bh["sharpe_ann"]
    rets["BuyHold"] = ret_bh
    mdds["BuyHold"] = me_bh["max_drawdown_pct"]

    spa_result = spa_test(losses, bench="BuyHold")

    best_name = max((n for n in members), key=lambda n: sharpes[n])
    best_sr = sharpes[best_name]
    # var_trials sur l'echelle JOURNALIERE (non annualisee), convention
    # identique a run_etape_b.py (Etape B, DSR de l'univers N=4)
    family_sharpes_daily = np.array([sharpes_daily[n] for n in members])
    var_trials = float(np.var(family_sharpes_daily, ddof=1))
    n_trials = len(members)
    emax = expected_max_sharpe(var_trials, n_trials)
    dsr_out = dsr(
        sharpes_daily[best_name], n_common, var_trials, n_trials=n_trials,
        skew=skews[best_name], kurt_excess=kurts[best_name],
    )
    dsr_val = dsr_out["dsr"]

    approx = approx_dsr_full_backlog()

    lines = [
        "# Validation SPA + DSR — famille des 13 overlays vol-targeting hiérarchiques (backlog non-ML)",
        "",
        f"Fenêtre commune : {n_common} séances (intersection des périodes testables des 13 membres, "
        f"à partir de l'indice {start_common} de `nasdaq100_daily.txt`).",
        "",
        "## 1. Résultats individuels sur la fenêtre COMMUNE (peuvent différer légèrement des résultats "
        "originaux, calculés chacun sur sa propre fenêtre, plus longue)",
        "",
        "| Membre | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
    ]
    for name in members:
        lines.append(f"| {name} | {sharpes[name]:+.2f} | {100*rets[name]:+.1f}% | {mdds[name]:.1f}% |")

    lines += [
        "",
        "## 2. Test SPA (Hansen 2005, bootstrap stationnaire, `src/volatility.py::spa_test`, "
        "mêmes paramètres qu'à l'Étape C, aucun retuning)",
        "",
        f"Perte = -pnl net de coûts. Benchmark = Buy&Hold NDX. H0 : aucun des 13 membres ne bat "
        f"significativement le benchmark une fois corrigé pour les essais multiples.",
        "",
        f"p-value SPA : {spa_result['p_value']:.4f}",
        f"Meilleur membre (statistique de test) : {spa_result.get('best_model', best_name)}",
        "",
        f"**{'H0 REJETÉE — au moins un membre de la famille bat significativement Buy&Hold, corrigé pour 13 essais.' if spa_result['p_value'] < 0.05 else 'H0 NON REJETÉE — la famille entière, corrigée pour 13 essais, ne bat PAS significativement Buy&Hold au seuil 5%.'}**",
        "",
        "## 3. DSR (Bailey & López de Prado 2014, `src/prediction.py::dsr`, même méthode qu'à l'Étape B) "
        f"— meilleur membre = **{best_name}** (Sharpe ann. {best_sr:+.2f} sur fenêtre commune)",
        "",
        f"n_trials = {n_trials} (famille figée), var_trials (variance des {n_trials} Sharpe journaliers) = {var_trials:.6f}",
        f"Sharpe max ATTENDU sous H0 (essais multiples, expected_max_sharpe, échelle journalière) : {emax:.4f}",
        f"Sharpe journalier du meilleur membre : {sharpes_daily[best_name]:.4f} (seuil de sélection SR0={dsr_out['sr0_daily']:.4f}, z={dsr_out['z']:+.2f})",
        f"**DSR = {dsr_val:.4f}**",
        "",
        f"{'DSR > 0.95 : le Sharpe du meilleur membre reste statistiquement significatif après correction pour 13 essais.' if dsr_val > 0.95 else 'DSR ≤ 0.95 : le Sharpe du meilleur membre NE reste PAS statistiquement distinguable du hasard une fois corrigé pour 13 essais (cohérent avec la conclusion Étape B : aucun signal ne bat Buy&Hold à DSR>0.95 sur le Composite).'}",
        "",
        "## 4. DSR secondaire APPROXIMATIF sur le backlog complet (N=110, INDICATIF SEULEMENT)",
        "",
        "Univers hétérogène (mécanismes très différents, pas seulement vol-targeting) — ne respecte "
        "pas strictement l'hypothèse DSR de tests répétés de la MÊME métrique candidate. Reporté "
        "uniquement à titre de borne indicative, PAS comme résultat principal.",
        "",
    ]
    if approx is not None:
        best_sr_full, var_trials_full, n_trials_full = approx
        lines.append(
            f"n_trials≈{n_trials_full} (Sharpe extractibles par regex sur {n_trials_full}/110 entrées du "
            f"backlog), var_trials≈{var_trials_full:.4f}, meilleur Sharpe extrait≈{best_sr_full:+.2f}. "
            f"Sharpe max attendu sous H0 (essais multiples) ≈ {expected_max_sharpe(var_trials_full, n_trials_full):.4f} "
            f"(échelle Sharpe annualisé, pas directement comparable au DSR journalier de la section 3 -- "
            f"reporté ici uniquement pour illustrer l'ordre de grandeur de l'inflation du seuil de significativité "
            f"quand n_trials passe de 13 à ~110)."
        )
    else:
        lines.append("Extraction regex insuffisante (<2 valeurs) — non calculé.")

    out = ROOT / "results" / "nonml_backlog_spa_dsr_validation.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

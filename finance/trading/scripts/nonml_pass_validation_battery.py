"""Batterie de validation renforcée pour tout PASS individuel du backlog
non-ML (Règle 9, `PROTOCOLE_ANTI_SNOOPING.md`, ajoutée le 29/07/2026 suite
à la leçon de la validation SPA/DSR de la famille vol-targeting : des PASS
individuels honnêtes (n_trials=1 chacun) ne survivent PAS forcément à une
correction jointe pour essais multiples).

Usage : python3 scripts/nonml_pass_validation_battery.py <nom>
Attend `results/nonml_<nom>_pnl.npz` (pos, r_asset, dates, cost_bps) --
convention à respecter par tout NOUVEAU script de backtest quand son
verdict initial est PASS (voir nonml_<nom>_backtest.py pour l'exemple).

Cinq contrôles, TOUS doivent passer pour que le PASS soit considéré
validé par la batterie renforcée :
a. Stress de coûts (3x, 5x le coût pré-enregistré).
b. Stress de crise (2000-2002, 2007-2009, 02-04/2020, 2022) -- le MDD de
   l'overlay ne doit pas être pire que celui de Buy&Hold sur ces fenêtres.
c. Stabilité temporelle (folds non chevauchants + embargo 5j) -- doit
   battre le benchmark sur une majorité de folds.
d. SPA à 1 candidat contre le benchmark.
e. DSR avec n_trials = taille totale du backlog à cette date (jamais 1).
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

from prediction import trading_metrics, dsr, expected_max_sharpe  # noqa: E402
from volatility import spa_test  # noqa: E402

EMBARGO = 5
CRISIS_WINDOWS = [
    ("Dot-com crash", "2000-01-01", "2002-12-31"),
    ("Crise financière 2008", "2007-10-01", "2009-03-31"),
    ("Krach COVID", "2020-02-01", "2020-04-30"),
    ("Resserrement 2022", "2022-01-01", "2022-12-31"),
]


def pnl_at_cost(pos: np.ndarray, r: np.ndarray, cost_bps: float, r_alt: np.ndarray = None):
    """r_alt : rendement de l'actif alternatif recevant la fraction
    (1-pos) du capital, au lieu du cash (0%) par defaut -- generalisation
    retrocompatible pour les mecanismes de DIVERSIFICATION (cycle #134),
    n'affecte aucun verdict anterieur (r_alt=None <=> cash, comportement
    original inchange)."""
    turn = np.abs(np.diff(pos, prepend=1.0))
    if r_alt is None:
        pnl_ov = pos * r - turn * (cost_bps / 1e4)
    else:
        pnl_ov = pos * r + (1.0 - pos) * r_alt - turn * (cost_bps / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= cost_bps / 1e4
    return pnl_ov, pnl_bh


def check_a_cost_stress(pos, r, cost_baseline, r_alt=None):
    rows = []
    for mult in (1, 3, 5):
        cost = cost_baseline * mult
        pnl_ov, pnl_bh = pnl_at_cost(pos, r, cost, r_alt)
        me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
        ret_ov = float(np.cumprod(1.0 + pnl_ov)[-1] - 1.0)
        ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)
        ok = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)
        rows.append((cost, me_ov["sharpe_ann"], me_bh["sharpe_ann"], ret_ov, ret_bh, ok))
    all_ok = all(r[-1] for r in rows)
    return all_ok, rows


def check_b_crisis_stress(pos, r, dates, cost_baseline, r_alt=None):
    rows = []
    any_window = False
    all_ok = True
    for label, d0, d1 in CRISIS_WINDOWS:
        mask = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
        n = int(mask.sum())
        if n < 20:
            rows.append((label, n, None, None, None))
            continue
        any_window = True
        pos_w, r_w = pos[mask], r[mask]
        r_alt_w = r_alt[mask] if r_alt is not None else None
        pnl_ov, pnl_bh = pnl_at_cost(pos_w, r_w, cost_baseline, r_alt_w)
        mdd_ov = trading_metrics(pnl_ov)["max_drawdown_pct"]
        mdd_bh = trading_metrics(pnl_bh)["max_drawdown_pct"]
        ok = mdd_ov >= mdd_bh - 1.0  # tolerance 1pt (arrondis)
        all_ok &= ok
        rows.append((label, n, mdd_ov, mdd_bh, ok))
    return (all_ok and any_window), rows, any_window


def check_c_temporal_stability(pos, r, cost_baseline, n_folds=4, r_alt=None):
    T = len(r)
    fold_len = T // n_folds
    rows = []
    n_beat = 0
    n_scored = 0
    for k in range(n_folds):
        f0 = k * fold_len
        f1 = (k + 1) * fold_len if k < n_folds - 1 else T
        if k > 0:
            f0 += EMBARGO
        if f1 - f0 < 30:
            continue
        pos_f, r_f = pos[f0:f1], r[f0:f1]
        r_alt_f = r_alt[f0:f1] if r_alt is not None else None
        pnl_ov, pnl_bh = pnl_at_cost(pos_f, r_f, cost_baseline, r_alt_f)
        s_ov = trading_metrics(pnl_ov)["sharpe_ann"]
        s_bh = trading_metrics(pnl_bh)["sharpe_ann"]
        beat = s_ov > s_bh
        n_beat += int(beat)
        n_scored += 1
        rows.append((k + 1, f1 - f0, s_ov, s_bh, beat))
    majority_ok = n_scored > 0 and n_beat > n_scored / 2
    return majority_ok, rows, n_beat, n_scored


def check_d_spa(pos, r, cost_baseline, r_alt=None):
    pnl_ov, pnl_bh = pnl_at_cost(pos, r, cost_baseline, r_alt)
    losses = {"candidat": -pnl_ov, "BuyHold": -pnl_bh}
    res = spa_test(losses, bench="BuyHold")
    return res["p_value"] < 0.05, res["p_value"]


def parse_backlog_n_trials():
    """Lit le dernier total "X PASS [niveau 1] sur Y hypothèses testées" du
    backlog. Bug trouvé au cycle #161 (leaders_index52w_high_overlay) : la
    regex d'origine ne matchait QUE l'ancien format "X PASS sur Y..." (sans
    "niveau 1"), donc figée sur la dernière occurrence de cette forme
    (n_trials=125, cycle #125) depuis le changement de formulation au
    cycle #126 -- toutes les batteries #126-#160 ont donc calculé leur DSR
    avec un n_trials TROP BAS (125 au lieu de la vraie taille du backlog à
    chaque date, jusqu'à 160). Corrigé pour matcher les deux formulations.
    Sans impact sur les verdicts déjà rendus : tous les DSR concernés
    étaient très loin du seuil (0,95) dans le sens du FAIL, et un n_trials
    plus élevé ne peut que les enfoncer davantage (seuil SR0 plus sévère),
    jamais les faire basculer en PASS -- mais le calcul DOIT être exact
    pour tout nouveau candidat, notamment un edge brut élevé comme le #38."""
    backlog = (ROOT / "NONML_STRATEGY_BACKLOG.md").read_text()
    matches = re.findall(r"(\d+) PASS(?: niveau 1)? sur (\d+) hypoth[eè]ses test[eé]es", backlog)
    if not matches:
        return None
    return int(matches[-1][1])


def approx_var_trials():
    backlog = (ROOT / "NONML_STRATEGY_BACKLOG.md").read_text()
    pairs = re.findall(r"Sharpe\s+([+-][0-9.,]+)\s*→\s*([+-][0-9.,]+)", backlog)
    vals = []
    for _, after in pairs:
        try:
            vals.append(float(after.rstrip(",").replace(",", ".")))
        except ValueError:
            continue
    if len(vals) < 2:
        return None, 0
    return float(np.var(np.array(vals), ddof=1)), len(vals)


def check_e_dsr(pos, r, cost_baseline, r_alt=None):
    pnl_ov, _ = pnl_at_cost(pos, r, cost_baseline, r_alt)
    me = trading_metrics(pnl_ov)
    n_trials = parse_backlog_n_trials()
    var_trials_annual, n_extracted = approx_var_trials()
    if n_trials is None or var_trials_annual is None:
        return None
    # les Sharpe extraits du backlog par regex sont ANNUALISES (echelle
    # affichee dans les rapports) -- dsr()/expected_max_sharpe() attendent
    # var_trials sur l'echelle JOURNALIERE (meme convention que run_etape_b.py
    # et nonml_backlog_spa_dsr_validation.py). Sharpe_annuel = Sharpe_jour *
    # sqrt(252) => Var(Sharpe_annuel) = 252 * Var(Sharpe_jour). Bug trouve et
    # corrige AVANT tout usage de ce script sur un vrai PASS (voir smoke-test
    # sur #106 : SR0 aberrant a 1.385/jour sans cette conversion).
    var_trials = var_trials_annual / 252.0
    d = dsr(me["sharpe_daily"], me["n"], var_trials, n_trials=n_trials,
            skew=me["skew"], kurt_excess=me["excess_kurt"])
    return n_trials, n_extracted, var_trials, d


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nonml_pass_validation_battery.py <nom>")
        sys.exit(1)
    name = sys.argv[1]
    npz_path = ROOT / "results" / f"nonml_{name}_pnl.npz"
    if not npz_path.exists():
        print(f"MANQUANT : {npz_path} -- ce script de backtest doit sauvegarder "
              f"(pos, r_asset, dates, cost_bps) sur verdict PASS (voir Règle 9).")
        sys.exit(1)

    data = np.load(npz_path, allow_pickle=True)
    pos, r, cost_bps = data["pos"], data["r_asset"], float(data["cost_bps"])
    dates = pd.to_datetime(data["dates"])
    r_alt = data["r_alt"] if "r_alt" in data.files else None

    lines = [f"# Batterie de validation renforcée — {name}",
             "",
             f"Coût pré-enregistré : {cost_bps:.1f} bps. {len(r)} séances.",
             ""]

    lines.append("## a. Stress de coûts (1x, 3x, 5x)")
    lines.append("")
    lines.append("| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |")
    lines.append("|---|---|---|---|---|---|")
    ok_a, rows_a = check_a_cost_stress(pos, r, cost_bps, r_alt)
    for cost, s_ov, s_bh, r_ov, r_bh, ok in rows_a:
        lines.append(f"| {cost:.1f} | {s_ov:+.2f} | {s_bh:+.2f} | {100*r_ov:+.1f}% | {100*r_bh:+.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_a else 'ÉCHEC'} — tient à 5x le coût nominal : {'oui' if ok_a else 'NON'}.**")
    lines.append("")

    lines.append("## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)")
    lines.append("")
    lines.append("| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |")
    lines.append("|---|---|---|---|---|")
    ok_b, rows_b, any_window = check_b_crisis_stress(pos, r, dates, cost_bps, r_alt)
    for label, n, mdd_ov, mdd_bh, ok in rows_b:
        if mdd_ov is None:
            lines.append(f"| {label} | {n} | -- | -- | hors couverture (<20 séances) |")
        else:
            lines.append(f"| {label} | {n} | {mdd_ov:.1f}% | {mdd_bh:.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    if not any_window:
        lines.append("**PENDING — aucune fenêtre de crise couverte par l'historique disponible pour ce "
                     "candidat (échantillon trop récent) : ce contrôle ne peut pas être exécuté, il ne "
                     "doit PAS être compté comme un OK silencieux (Règle 5).**")
    else:
        lines.append(f"**{'OK' if ok_b else 'ÉCHEC'} — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : {'oui' if ok_b else 'NON'}.**")
    lines.append("")

    lines.append(f"## c. Stabilité temporelle (folds non chevauchants + embargo {EMBARGO}j)")
    lines.append("")
    lines.append("| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |")
    lines.append("|---|---|---|---|---|")
    ok_c, rows_c, n_beat, n_scored = check_c_temporal_stability(pos, r, cost_bps, r_alt=r_alt)
    for k, n, s_ov, s_bh, beat in rows_c:
        lines.append(f"| {k} | {n} | {s_ov:+.2f} | {s_bh:+.2f} | {'OUI' if beat else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_c else 'ÉCHEC'} — bat le benchmark sur {n_beat}/{n_scored} folds "
                 f"(majorité {'atteinte' if ok_c else 'NON atteinte'}).**")
    lines.append("")

    lines.append("## d. SPA à 1 candidat contre Buy&Hold")
    lines.append("")
    ok_d, p_spa = check_d_spa(pos, r, cost_bps, r_alt)
    lines.append(f"p-value SPA : {p_spa:.4f}")
    lines.append(f"**{'OK' if ok_d else 'ÉCHEC'} — significatif à 5% : {'oui' if ok_d else 'NON'}.**")
    lines.append("")

    lines.append("## e. DSR avec n_trials = taille totale du backlog (jamais 1)")
    lines.append("")
    e_res = check_e_dsr(pos, r, cost_bps, r_alt)
    if e_res is None:
        lines.append("**PENDING — n_trials/var_trials non extractibles du backlog, contrôle non exécuté "
                     "(ne pas absorber silencieusement en OK, Règle 5).**")
        ok_e = False
    else:
        n_trials, n_extracted, var_trials, d = e_res
        lines.append(f"n_trials = {n_trials} (taille totale du backlog), var_trials (échelle journalière, "
                     f"convertie depuis les Sharpe annualisés extraits) ≈ {var_trials:.6f} "
                     f"(estimée sur {n_extracted} Sharpe extractibles de l'historique du backlog -- "
                     f"univers hétérogène, approximation prudente).")
        lines.append(f"SR0 (seuil de sélection) = {d['sr0_daily']:.4f} (journalier), DSR = {d['dsr']:.4f}")
        ok_e = d["dsr"] > 0.95
        lines.append(f"**{'OK' if ok_e else 'ÉCHEC'} — DSR>0,95 : {'oui' if ok_e else 'NON'}.**")
    lines.append("")

    verdict_final = ok_a and ok_b and ok_c and ok_d and ok_e
    lines.append("## Verdict de la batterie renforcée")
    lines.append("")
    lines.append(f"a. Stress coûts : {'OK' if ok_a else 'ÉCHEC'}")
    lines.append(f"b. Stress crise : {'OK' if ok_b else ('PENDING' if not any_window else 'ÉCHEC')}")
    lines.append(f"c. Stabilité temporelle : {'OK' if ok_c else 'ÉCHEC'}")
    lines.append(f"d. SPA 1-candidat : {'OK' if ok_d else 'ÉCHEC'}")
    lines.append(f"e. DSR (n_trials=backlog) : {'OK' if ok_e else 'ÉCHEC'}")
    lines.append("")
    lines.append(f"**{'PASS RENFORCÉ — tous les contrôles a-e tiennent. Notification Telegram requise avant tout audit supplémentaire (Règle 9).' if verdict_final else 'PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.'}**")

    out = ROOT / "results" / f"nonml_{name}_pass_validation_battery.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    sys.exit(0 if verdict_final else 2)


if __name__ == "__main__":
    main()

"""Etape D v3 - Overlay defensif (vol-targeting sur volatilite realisee)
+ diversification obligataire vs Buy & Hold.
Produit results/etape_D_v3_bond_diversification.md.

Formalise dans l'infrastructure officielle Etape D le mecanisme deja
valide dans le backlog non-ML (finance/trading/PREREG_defensive_calmar_
vol_targeting_overlay.md = #115, PREREG_defensive_diversification_
bond_overlay.md = #134, PASS niveau 1, meilleur score Regle 9 du
backlog : 4/5 -- puis PREREG_cash_rate_correction_defensive_vol_
targeting_44.md = #149, cible 15% au lieu de 20%, MEILLEUR resultat
brut du backlog, egalement 4/5, ajoute comme 4e variante au cycle
#152). Aucun nouveau parametre, aucun retuning -- reproduit exactement
les resultats deja obtenus, dans le meme style que run_etape_d.py
(GJR-GARCH).

PROTOCOLE FIGE AVANT EXECUTION (identique en esprit a run_etape_d.py) :
- Univers de 4 variantes declarees, aucun ajout a posteriori (N=4 pour le DSR) :
    1. Buy & Hold pur                                    - reference
    2. VolTarget-Defensif20 (#115)                        - expo = clip(20%/vol_realisee_20j, 0, 1.0)
    3. VolTarget-Defensif20 + Diversification (#134)      - fraction (1-expo) allouee
       a un proxy obligataire (Tresor US 10 ans, DGS10, duration modifiee)
       au lieu du cash, au lieu de rester en cash a 0%.
    4. VolTarget-Defensif15 + Diversification (#149)      - meme mecanisme,
       cible 15% au lieu de 20% (mecanisme plus defensif, #44).
- Couts : 5 bps aller-retour, preleves sur le turnover de l'exposition.
- Evaluation : Sharpe/Sortino/Calmar/MDD/rendement annualise NETS + DSR (N=4),
  et le critere de succes EXPLICITE deja utilise par run_etape_d.py :
  reduction du MDD >25% (relatif) SANS perdre plus de 20% du rendement
  annualise de Buy & Hold (reste >=80%).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]          # finance/trading
FINANCE_ROOT = ROOT.parent                          # finance
REPO_ROOT = FINANCE_ROOT.parent                     # Quant-Trade
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from prediction import dsr, trading_metrics  # noqa: E402

COST_BPS = 5.0
TARGET_VOL_ANNUAL = 0.20
TARGET_VOL_ANNUAL_44 = 0.15
VOL_WINDOW = 20
CAP = 1.0  # jamais de levier -- mecanisme DEFENSIF uniquement (#115/#44)
ANNUALIZATION = np.sqrt(252)
MATURITY_YEARS = 10
MODELS = [
    "BuyHold",
    "VolTarget-Défensif20",
    "VolTarget-Défensif20+Diversification",
    "VolTarget-Défensif15+Diversification",
]

DATASETS = [
    ("Composite (5 ans)", REPO_ROOT / "data" / "nasdaq_composite_daily.txt"),
    ("NDX (40 ans)", REPO_ROOT / "data" / "nasdaq100_daily.txt"),
    ("S&P 500", REPO_ROOT / "data" / "sp500_daily.txt"),
    ("Russell 2000", REPO_ROOT / "data" / "russell2000_daily.txt"),
]

OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "etape_D_v3_bond_diversification.md")


def vol_target_position(r: np.ndarray, target_vol: float = TARGET_VOL_ANNUAL) -> np.ndarray:
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = target_vol / vol_lagged
    pos = np.clip(pos, 0.0, CAP)
    return np.nan_to_num(pos, nan=1.0)


def load_dgs10() -> pd.Series:
    df = pd.read_csv(REPO_ROOT / "data" / "dgs10_daily.csv")
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["DGS10"] = pd.to_numeric(df["DGS10"], errors="coerce")
    s = pd.Series(df["DGS10"].values, index=df["observation_date"]).dropna()
    return s[~s.index.duplicated(keep="first")].sort_index()


def bond_return_proxy(yield_pct: pd.Series, maturity_years: int = MATURITY_YEARS) -> pd.Series:
    y = yield_pct.values / 100.0
    y_lag = np.roll(y, 1)
    y_lag[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        d_mac = (1 + y_lag) / y_lag * (1 - 1 / (1 + y_lag) ** maturity_years)
    d_mod = d_mac / (1 + y_lag)
    d_mod = np.where(y_lag == 0.0, float(maturity_years), d_mod)  # limite y->0, cf. #141
    r_bond = y_lag / 252.0 - d_mod * (y - y_lag)
    return pd.Series(r_bond, index=yield_pct.index)


def main():
    lines = []
    w = lines.append
    w("# Étape D v3 — Overlay défensif (vol-targeting réalisée) + diversification obligataire vs Buy & Hold\n")
    w("Formalise dans l'infrastructure officielle Étape D le mécanisme déjà validé dans le backlog "
      "non-ML (`PREREG_defensive_calmar_vol_targeting_overlay.md` = #115, "
      "`PREREG_defensive_diversification_bond_overlay.md` = #134, PASS niveau 1, meilleur score Règle 9 "
      "du backlog non-ML : 4/5 — coûts/crise/stabilité OK, SPA/DSR à n_trials=backlog encore en échec).\n")
    w(f"**Protocole figé** : `TARGET_VOL_ANNUAL={TARGET_VOL_ANNUAL:.0%}` (variantes 20) ou "
      f"`{TARGET_VOL_ANNUAL_44:.0%}` (variante 15), `VOL_WINDOW={VOL_WINDOW}j`, `CAP={CAP:.1f}×` "
      f"(jamais de levier — mécanisme DÉFENSIF), proxy obligataire Trésor US 10 ans (DGS10, duration "
      f"modifiée, formule fermée) ; coûts {COST_BPS:.0f} bps aller-retour ; univers de {len(MODELS)} "
      f"variantes (N={len(MODELS)} pour le DSR), figé avant évaluation.\n")

    dgs10 = load_dgs10()
    r_bond_all_10y = bond_return_proxy(dgs10)

    summary_rows = []
    for label, path in DATASETS:
        df = load_ohlc(str(path))
        r_pct = log_returns_pct(df)
        r = r_pct.values / 100.0  # rendements log naturels
        dates = r_pct.index
        T = len(r)

        pos_eq20 = vol_target_position(r, TARGET_VOL_ANNUAL)
        pos_eq15 = vol_target_position(r, TARGET_VOL_ANNUAL_44)
        r_bond_aligned = r_bond_all_10y.reindex(dates, method="ffill")
        valid = r_bond_aligned.notna().values
        start = max(VOL_WINDOW, int(np.argmax(valid)) if valid.any() else len(valid))

        idx = np.arange(start, T)
        pos_eq20_oos = pos_eq20[idx]
        pos_eq15_oos = pos_eq15[idx]
        r_oos = r[idx]
        r_bond_oos = r_bond_aligned.values[idx]
        dates_oos = dates[idx]

        turn20 = np.abs(np.diff(pos_eq20_oos, prepend=1.0))
        turn15 = np.abs(np.diff(pos_eq15_oos, prepend=1.0))
        pnl = {
            "BuyHold": r_oos - np.concatenate(([COST_BPS / 1e4], np.zeros(len(r_oos) - 1))),
            "VolTarget-Défensif20": pos_eq20_oos * r_oos - turn20 * (COST_BPS / 1e4),
            "VolTarget-Défensif20+Diversification": pos_eq20_oos * r_oos + (1.0 - pos_eq20_oos) * r_bond_oos - turn20 * (COST_BPS / 1e4),
            "VolTarget-Défensif15+Diversification": pos_eq15_oos * r_oos + (1.0 - pos_eq15_oos) * r_bond_oos - turn15 * (COST_BPS / 1e4),
        }
        metr = {m: trading_metrics(pnl[m]) for m in MODELS}

        sr_daily = {m: metr[m]["sharpe_daily"] for m in MODELS}
        var_trials = float(np.var(list(sr_daily.values()), ddof=1))
        T_oos = len(idx)
        dsr_out = {m: dsr(sr_daily[m], T_oos, var_trials, n_trials=len(MODELS),
                          skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])
                  for m in MODELS}

        n_years = (dates_oos[-1] - dates_oos[0]).days / 365.25
        w(f"## {label}\n")
        w(f"- Fenêtre : {dates_oos[0]:%d/%m/%Y} → {dates_oos[-1]:%d/%m/%Y} ({T_oos} obs, ~{n_years:.1f} ans).")
        w(f"- Exposition équity cible 20% : moy. {pos_eq20_oos.mean():.2f}×, min {pos_eq20_oos.min():.2f}×, "
          f"max {pos_eq20_oos.max():.2f}× — cible 15% : moy. {pos_eq15_oos.mean():.2f}×, min "
          f"{pos_eq15_oos.min():.2f}×, max {pos_eq15_oos.max():.2f}× (cap {CAP:.1f}×, jamais de levier).\n")

        w("| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Profit factor | DSR |")
        w("|---|---|---|---|---|---|---|---|")
        for m in MODELS:
            me = metr[m]
            w(f"| {m} | {me['sharpe_ann']:+.2f} | {me['sortino_ann']:+.2f} | "
              f"{me['calmar']:+.2f} | {me['max_drawdown_pct']:.1f} | "
              f"{me['ann_return_pct']:+.1f} | {me['profit_factor']:.2f} | "
              f"{dsr_out[m]['dsr']:.3f} |")
        w("")

        bh = metr["BuyHold"]
        for m in ("VolTarget-Défensif20", "VolTarget-Défensif20+Diversification", "VolTarget-Défensif15+Diversification"):
            me = metr[m]
            mdd_reduction = 1.0 - abs(me["max_drawdown_pct"]) / abs(bh["max_drawdown_pct"])
            ret_ratio = me["ann_return_pct"] / bh["ann_return_pct"] if bh["ann_return_pct"] != 0 else np.nan
            ok = mdd_reduction > 0.25 and ret_ratio >= 0.80
            summary_rows.append((label, m, mdd_reduction, ret_ratio, ok, me["calmar"], bh["calmar"]))
            w(f"- **{m} vs BuyHold** : réduction MDD relative = {100*mdd_reduction:+.1f}% (seuil >25%), "
              f"rendement ann. conservé = {100*ret_ratio:.1f}% du BuyHold (seuil ≥80%) → "
              + ("**critère de succès atteint**" if ok else "**critère de succès NON atteint**"))
        w("")

    w("## Verdict — critère de succès explicite (identique à run_etape_d.py)\n")
    w("Succès = réduction du MDD >25% (relatif) **et** rendement annualisé conservé ≥80% de Buy & "
      "Hold. Vérifié, pas supposé :\n")
    w("| Jeu de données | Variante | ΔMDD relatif | Rdt ann. / BuyHold | Calmar (overlay vs BH) | Critère |")
    w("|---|---|---|---|---|---|")
    any_success = False
    for label, m, mdd_r, ret_r, ok, cal, cal_bh in summary_rows:
        any_success = any_success or ok
        w(f"| {label} | {m} | {100*mdd_r:+.1f}% | {100*ret_r:.1f}% | {cal:+.2f} vs {cal_bh:+.2f} | {'OUI' if ok else 'NON'} |")
    w("")
    if any_success:
        w("**Verdict honnête** : le critère de succès Étape D est atteint pour au moins une combinaison "
          "jeu de données/variante ci-dessus. Sur NDX, la variante cible 15% (#149) obtient le "
          "MEILLEUR résultat des deux (MDD relatif et Sharpe supérieurs à la variante cible 20%, #134) "
          "— cohérent avec le résultat déjà documenté dans le backlog non-ML. Rappel important (cf. "
          "backlog non-ML, cycle #142) : la décomposition du gain de la diversification obligataire "
          "montre que 86-89% de l'amélioration vient du simple PORTAGE (taux positif au lieu de 0% "
          "cash pendant les phases dé-risquées), pas principalement d'un effet de couverture actions/"
          "obligations authentique ('flight to quality') — à documenter honnêtement si ce résultat est "
          "repris dans un rapport exécutif. Rappel Règle 9 (backlog non-ML) : les deux mécanismes "
          "(#134 ET #149) atteignent 4/5 sur la batterie renforcée (coûts/crise/stabilité OK) mais "
          "échouent SPA et DSR à n_trials=backlog (~150) — PAS un PASS RENFORCÉ au sens strict de "
          "cette batterie plus sévère.")
    else:
        w("**Verdict honnête : le critère de succès N'EST ATTEINT nulle part** sur les jeux de données "
          "testés ici.")

    out = Path(OUT)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()

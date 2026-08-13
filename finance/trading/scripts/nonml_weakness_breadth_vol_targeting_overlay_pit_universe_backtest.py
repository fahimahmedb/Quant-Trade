"""Backtest — Overlay vol-targeting gaté par la breadth de FAIBLESSE,
univers de titres POINT-IN-TIME (spécification pré-enregistrée dans
`PREREG_weakness_breadth_vol_targeting_overlay_pit_universe.md`, committée avant ce
script).

Réutilisation stricte (Règle 7) du cycle d'origine (#89) : **aucun paramètre
modifié**, seuil de porte compris (0,0). Seul l'univers change — à chaque date,
seuls les titres réellement membres du NDX-100 entrent dans les comptages.

Le P&L n'est **pas** un panier : les deux jambes sont l'indice NDX-100 lui-même.
Conventions de P&L rétablies au #404.

Particularité de ce candidat : **le PASS d'origine est déjà déclaré non
informatif par son propre rapport** — la porte (breadth de faiblesse ≥ 50 %) ne
s'ouvrait que 5 jours sur 1385. Le script compte donc explicitement les
activations et applique le critère d'informativité **fixé au pré-enregistrement**
(porte brute active sur ≥ 2 % des séances), qui étiquette le verdict sans le
modifier.
"""
import json
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
from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
COMPOSITION_START = pd.Timestamp("2015-01-01")

# --- Parametres REPRIS A L'IDENTIQUE du cycle d'origine (Regle 7) ---
INDEX_LOOKBACK = 252
INDEX_THRESHOLD_LOW = 1.05
BREADTH_THRESHOLD = 0.50
INFORMATIVE_MIN_ACTIVE = 0.02  # fixe au PREREG, convention de lisibilite
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def load_all_prices_pit():
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > INDEX_LOOKBACK + 21:
            series[path.stem] = close
    return series


def compute_weakness_breadth_series_pit():
    """Breadth de faiblesse(t) = n_proche_bas / n_cotes, calculee sur les seuls
    MEMBRES du NDX-100 a la date t.

    NaN avant le 01/01/2015 (aucune appartenance connue) — c'est cette valeur
    NaN, et non un `False`, qui delimite la fenetre testable en aval.
    """
    series = load_all_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = P.shape
    tickers = list(P.columns)
    exists = np.isfinite(close)

    rolling_min = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(INDEX_LOOKBACK, T):
        window = close[i - INDEX_LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_min[i] = np.nanmin(window, axis=0)

    near_low = np.where(has_full, close <= INDEX_THRESHOLD_LOW * rolling_min, False)

    breadth = np.full(T, np.nan)
    coverage = []
    for i in range(T):
        if P.index[i] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[i])
        if not members:
            continue
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        listed = exists[i] & member_cols
        n_listed = int(listed.sum())
        if n_listed == 0:
            continue
        n_low = int((near_low[i] & listed).sum())
        breadth[i] = n_low / n_listed
        coverage.append(n_listed / max(1, len(members)))

    cov = float(np.mean(coverage)) if coverage else float("nan")
    return pd.Series(breadth, index=P.index), cov


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    """INCHANGE par rapport au cycle d'origine."""
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


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    breadth_net, cov = compute_weakness_breadth_series_pit()
    # La serie BRUTE conserve les NaN ; la PORTE est booleenne. C'est la
    # separation des deux qui delimite correctement la fenetre testable
    # (piege du #396).
    breadth_raw = breadth_net.reindex(dates_idx.values, method="ffill").values
    gate_aligned = np.where(np.isnan(breadth_raw), False, breadth_raw >= BREADTH_THRESHOLD)

    pos_full = combined_position(bh_full, gate_aligned)

    first_valid = int(np.argmax(~np.isnan(breadth_raw)))
    start = max(first_valid, INDEX_LOOKBACK, VOL_WINDOW)
    bh_t = bh_full[start:]
    pos = pos_full[start:]

    # Controle pre-enregistre : la fenetre doit demarrer en 2015-2016, pas 1985.
    start_date = dates_idx.iloc[1:].iloc[start]
    if start_date < pd.Timestamp("2015-01-01"):
        raise SystemExit(
            f"PIEGE DU #396 : la fenetre testable demarre le {start_date.date()}, "
            "anterieurement a la composition point-in-time. Resultat invalide, "
            "a corriger avant tout commit."
        )

    # Comptage des activations : la porte BRUTE (breadth >= seuil) et la porte
    # EFFECTIVE (position finale > 1x, apres clip du vol-targeting) ne coincident
    # pas. Le critere d'informativite du PREREG porte sur la porte brute.
    gate_raw_window = gate_aligned[:-1][start:]
    n_raw_active = int(gate_raw_window.sum())
    frac_raw_active = n_raw_active / max(1, len(gate_raw_window))
    informative = frac_raw_active >= INFORMATIVE_MIN_ACTIVE

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok
    gate_active = (pos > 1.0)

    lines = [
        "# Résultat — breadth de faiblesse, univers POINT-IN-TIME (pré-enregistré)",
        "",
        "Réutilisation stricte (Règle 7) du cycle d'origine (#89) : **aucun paramètre "
        "modifié**, seuil de porte compris (50 %). Seul l'univers change — à chaque date, "
        "seuls les titres réellement membres du NDX-100 entrent dans les comptages.",
        "",
        "**Le P&L n'est pas un panier** : les deux jambes sont l'indice NDX-100 lui-même. "
        "L'univers titres n'alimente que la porte.",
        "",
        f"Couverture moyenne (titres cotés éligibles / membres réels) : {100*cov:.1f}%. "
        f"{len(bh_t)} séances testables ({start_date.date()} → {dates_idx.iloc[-1].date()}).",
        "",
        "## Activation de la porte — mesure décisive pour ce candidat",
        "",
        f"- porte **brute** (breadth ≥ {100*BREADTH_THRESHOLD:.0f} %) active : "
        f"**{n_raw_active} séance(s) sur {len(gate_raw_window)}** "
        f"({100*frac_raw_active:.2f} %)",
        f"- porte **effective** (exposition > 1,0×, après clip du vol-targeting) active : "
        f"{100*float((pos > 1.0).mean()):.2f} % des séances",
        f"- breadth de faiblesse observée : moyenne {100*np.nanmean(breadth_net.values):.1f} %, "
        f"maximum {100*np.nanmax(breadth_net.values):.1f} %",
        f"- exposition moyenne : {pos.mean():.2f}×",
        "",
        f"Critère d'informativité **fixé au pré-enregistrement** : porte brute active sur "
        f"≥ {100*INFORMATIVE_MIN_ACTIVE:.0f} % des séances.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay gaté breadth de faiblesse (PIT)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'} sur univers point-in-time.**",
        "",
    ]
    if informative:
        lines.append(f"**Verdict INFORMATIF** — la porte brute s'active sur "
                     f"{100*frac_raw_active:.2f} % des séances, au-dessus du seuil de "
                     f"{100*INFORMATIVE_MIN_ACTIVE:.0f} % fixé avant calcul. Le résultat "
                     f"reflète un comportement de la stratégie, pas son inactivité.")
    else:
        lines.append(f"**⚠️ VERDICT NON INFORMATIF** — la porte brute ne s'active que sur "
                     f"{100*frac_raw_active:.2f} % des séances, sous le seuil de "
                     f"{100*INFORMATIVE_MIN_ACTIVE:.0f} % fixé **avant** calcul. La stratégie "
                     f"est donc quasi identique à Buy & Hold sur cette période, et le verdict "
                     f"ci-dessus mesure cette inactivité, **pas un edge**. Même conclusion "
                     f"qu'au cycle d'origine, dont le rapport portait déjà cet avertissement.")
    lines.append("")
    lines.append("Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. "
                 "Leur comparaison mesure l'effet du biais du survivant sur ce candidat.")
    lines.append("")

    out = ROOT / "results" / "nonml_weakness_breadth_vol_targeting_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    np.savez(
        ROOT / "results" / "nonml_weakness_breadth_vol_targeting_overlay_pit_universe_pnl.npz",
        pos=pos, r_asset=bh_t, dates=dates_idx.values[1:][start:], cost_bps=COST_BPS,
    )

    print("\n".join(lines))
    print(f"Écrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()

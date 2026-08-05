"""Backtest — Overlay vol-targeting gaté par le ratio de variance de
Lo-MacKinlay glissant (spécification pré-enregistrée dans
PREREG_variance_ratio_vol_targeting_overlay.md, committée avant ce
script). Réutilise diagnostics.py::lo_mackinlay_vr (Étape A) en fenêtre
glissante comme porte du mécanisme #46/#47. n_trials=1, aucune
dépendance ML. Règle de succès renforcée.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from diagnostics import lo_mackinlay_vr  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CAP = 2.0
Q = 5
VR_WINDOW = 252
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def momentum_regime_mask(r: np.ndarray) -> np.ndarray:
    """Renvoie un masque booleen (longueur T-1, alignee sur r) : True au
    jour k quand VR(q) calcule sur la fenetre r[k-VR_WINDOW:k] (EXCLUANT
    r[k] lui-meme, connu seulement a la cloture du jour k+1) est >= 1.0
    (regime de persistance/momentum local), False sinon (retour a la
    moyenne local, ou fenetre degeneree -> porte inactive par defaut)."""
    n = len(r)
    gate = np.zeros(n, dtype=bool)
    for k in range(VR_WINDOW, n):
        window = r[k - VR_WINDOW:k]
        try:
            vr = lo_mackinlay_vr(window, Q)["VR"]
        except AssertionError:
            continue  # fenetre degeneree -> porte inactive par defaut (declare au PREREG)
        gate[k] = vr >= 1.0
    return gate


def combined_position(r: np.ndarray, gate: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (longueur T-1). gate = porte de
    regime alignee directement sur r (deja causale par construction,
    contrairement aux autres portes de cette famille qui necessitent un
    decalage [:-1] -- ici gate[k] exclut deja r[k] de son propre calcul,
    voir momentum_regime_mask)."""
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    pos = np.where(gate, vt_exposure, 1.0)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    lines = [
        "# Résultat — Overlay vol-targeting gaté par le ratio de variance de Lo-MacKinlay glissant (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si VR({Q}) calculé sur les {VR_WINDOW} rendements précédents est ≥1,0 (régime de persistance "
        f"locale), sinon 1.0x. Échantillon testable = à partir de la {VR_WINDOW+2}e séance.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])

        gate = momentum_regime_mask(bh_full)
        pos_full = combined_position(bh_full, gate)
        start = VR_WINDOW
        bh_t = bh_full[start:]
        pos = pos_full[start:]

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        gate_active = (pos > 1.0)
        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{100*gate_active.mean():.1f}% | {pos.mean():.2f}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_variance_ratio_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

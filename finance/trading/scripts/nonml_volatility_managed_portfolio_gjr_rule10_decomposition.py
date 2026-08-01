"""Règle 10 — décomposition portage / effet-prix du portefeuille
volatility-managed GJR-t (cycle #165).

Engagement pris au §6 du PREREG **avant tout calcul** : le mécanisme fait
descendre l'exposition sous 1,0x une partie du temps (et monter au-dessus le
reste du temps), donc l'hypothèse de rémunération de la fraction hors-marché
devait être déclarée (elle l'a été : 0 % des deux côtés) ET, en cas de PASS,
décomposée avant toute communication du résultat comme un edge authentique.

Le mécanisme du #165 n'a **aucun effet-prix** à décomposer (l'actif alternatif
est du cash, pas une obligation à duration comme au #134) : la totalité de
l'effet d'une hypothèse de taux réaliste passe par le **portage**, qui est
donc isolé directement — c'est la version dégénérée, et exacte, de la méthode
du #142.

Trois comptabilisations de la MÊME série de positions (aucune n'est une
nouvelle hypothèse ni un nouvel essai — la position n'est pas touchée) :

  A. 0 % / 0 %      — hypothèse pré-enregistrée, celle du verdict committé.
  B. taux réel des DEUX côtés — le cash rapporte DGS3MO, le levier le paie.
     C'est la comptabilisation économiquement correcte.
  C. taux réel côté cash SEULEMENT — borne haute, volontairement trop
     favorable, publiée pour encadrer l'incertitude.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0


def load_short_rate(dates: pd.DatetimeIndex) -> np.ndarray:
    """Taux 3 mois quotidien, aligné causalement (valeur de la VEILLE).

    Portage seul : `y(t-1)/252`, sans terme d'effet-prix — le cash n'a pas de
    duration (méthode du #142 réduite à son terme de portage)."""
    raw = pd.read_csv(REPO_ROOT / "data" / "dgs3mo_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    s = raw.set_index("observation_date")["DGS3MO"].astype(float).dropna()
    s = s[~s.index.duplicated(keep="first")].sort_index()
    y = s.reindex(dates, method="ffill")
    y_lag = y.shift(1)
    return (y_lag.values / 100.0) / 252.0


def summarize(pnl):
    me = trading_metrics(pnl)
    ret = float(np.cumprod(1.0 + pnl)[-1] - 1.0)
    return me, ret


def main():
    d = np.load(ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_pnl.npz",
                allow_pickle=True)
    pos_all, r_all = d["pos"], d["r_asset"]
    dates_all = pd.to_datetime(d["dates"])
    assert float(d["cost_bps"]) == COST_BPS

    rf_all = load_short_rate(dates_all)
    valid = np.isfinite(rf_all)
    start = int(np.argmax(valid))
    pos, r, rf = pos_all[start:], r_all[start:], rf_all[start:]
    dates = dates_all[start:]
    assert np.isfinite(rf).all(), "trou dans la série de taux après alignement"

    turn = np.abs(np.diff(pos, prepend=1.0))
    cost = turn * (COST_BPS / 1e4)
    carry_sym = (1.0 - pos) * rf                       # <0 quand pos>1 (financement)
    carry_asym = np.where(pos < 1.0, (1.0 - pos) * rf, 0.0)

    pnl_a = pos * r - cost
    pnl_b = pos * r - cost + carry_sym
    pnl_c = pos * r - cost + carry_asym
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh, ret_bh = summarize(pnl_bh)
    rows = []
    for label, pnl in (("A. 0 % / 0 % (pré-enregistré, verdict committé)", pnl_a),
                       ("B. DGS3MO des deux côtés (comptabilisation correcte)", pnl_b),
                       ("C. DGS3MO côté cash seulement (borne haute)", pnl_c)):
        me, ret = summarize(pnl)
        rows.append((label, me, ret, me["sharpe_ann"] > me_bh["sharpe_ann"], ret > ret_bh))

    frac_cash = float((pos < 1.0).mean())
    mean_rf_ann = float(np.mean(rf) * 252 * 100)

    lines = [
        "# Règle 10 — décomposition portage / effet-prix (cycle #165, volatility-managed GJR-t)",
        "",
        "Engagement pré-enregistré (§6 du PREREG), exécuté parce que le cycle est PASS de "
        "niveau 1. **La série de positions n'est pas modifiée** : seules trois "
        "comptabilisations de la fraction non investie (ou empruntée) sont comparées. Ce "
        "n'est ni un nouvel essai, ni une nouvelle hypothèse.",
        "",
        f"Fenêtre commune NDX ∩ DGS3MO : **{len(r)} séances**, "
        f"{dates[0]:%d/%m/%Y} → {dates[-1]:%d/%m/%Y} "
        f"(la série DGS3MO commence en 1981, elle couvre donc toute la fenêtre OOS).",
        f"Taux 3 mois moyen sur la fenêtre : **{mean_rf_ann:.2f} %** annualisé. "
        f"Exposition sous 1,0x : {100 * frac_cash:.1f} % du temps ; "
        f"exposition moyenne {pos.mean():.3f}x (donc la stratégie **emprunte** en moyenne, "
        f"légèrement).",
        "",
        "## Résultats",
        "",
        "| Comptabilisation | Sharpe | Rendement total | MDD | Sharpe > BH | Rdt > BH |",
        "|---|---|---|---|---|---|",
        f"| Buy & Hold (référence) | {me_bh['sharpe_ann']:+.3f} | {100 * ret_bh:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% | — | — |",
    ]
    for label, me, ret, ok_s, ok_r in rows:
        lines.append(f"| {label} | {me['sharpe_ann']:+.3f} | {100 * ret:+.1f}% | "
                     f"{me['max_drawdown_pct']:.1f}% | {'OUI' if ok_s else 'non'} | "
                     f"{'OUI' if ok_r else 'non'} |")

    contrib_b = float(np.sum(carry_sym))
    contrib_c = float(np.sum(carry_asym))
    gross = float(np.sum(pnl_a))
    lines += [
        "",
        "## Contribution du portage (part du résultat qui vient du taux, pas du signal)",
        "",
        f"- Somme des rendements log de la variante A (signal seul) : {100 * gross:+.1f} points.",
        f"- Terme de portage symétrique (B − A) : **{100 * contrib_b:+.1f} points** "
        f"({100 * contrib_b / abs(gross):+.1f} % du résultat de A).",
        f"- Terme de portage asymétrique (C − A, borne haute) : **{100 * contrib_c:+.1f} points** "
        f"({100 * contrib_c / abs(gross):+.1f} % du résultat de A).",
        "",
        "## Lecture",
        "",
        "Le point à trancher, posé par le #142 : le résultat est-il un edge du mécanisme, "
        "ou l'artefact d'une hypothèse de taux irréaliste ? Ici la réponse est directement "
        "lisible — **le verdict pré-enregistré (A) ne doit rien au portage**, puisqu'il est "
        "rendu sous l'hypothèse 0 %. La comptabilisation correcte (B) est même **légèrement "
        "défavorable** au candidat (exposition moyenne > 1x ⇒ il paie plus de financement "
        "qu'il ne touche d'intérêts), ce qui est l'inverse exact de la situation du #134, "
        "où 86-89 % du gain venait du portage. La borne haute (C) montre l'ampleur maximale "
        "que pourrait prendre l'effet si l'on n'imputait aucun coût de financement — elle "
        "est publiée pour encadrer l'incertitude, pas pour être retenue.",
    ]

    out = ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_rule10_decomposition.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

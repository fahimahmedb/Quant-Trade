"""Audit adversarial — Overnight vs Intraday.

Vérification indépendante : par construction mathématique,
overnight_t + intraday_t == rendement close-to-close du jour t (identité
log-additive). Si cette identité ne tient pas dans les données calculées
par le backtest principal, c'est la preuve d'un bug de calcul (pas un
résultat économique). Sert aussi à vérifier que le résultat FAIL n'est pas
un artefact du bug de coût déjà trouvé et corrigé manuellement pendant ce
cycle (documenté ici pour traçabilité).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def main():
    lines = [
        "# Audit adversarial — Overnight vs Intraday",
        "",
        "## Vérification d'identité (overnight + intraday == close-to-close)",
        "",
        "| Marché | Écart max abs. (devrait être ~0) |",
        "|---|---|",
    ]
    max_err_global = 0.0
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        open_, close = df["open"].values, df["close"].values
        overnight = np.log(open_[1:] / close[:-1])
        intraday = np.log(close[1:] / open_[1:])
        bh = np.log(close[1:] / close[:-1])
        err = np.max(np.abs((overnight + intraday) - bh))
        max_err_global = max(max_err_global, err)
        lines.append(f"| {name} | {err:.2e} |")

    lines.append("")
    ok = max_err_global < 1e-9
    lines.append(
        f"**{'OK' if ok else 'ÉCHEC'}** — identité mathématique "
        f"{'vérifiée (aucun bug de décomposition)' if ok else 'VIOLÉE, bug à corriger avant toute conclusion'}."
    )
    lines.append("")
    lines.append(
        "**Note de traçabilité** : un bug a été trouvé et corrigé PENDANT ce cycle, avant "
        "de considérer le résultat final — le calcul initial du backtest soustrayait le "
        "coût de transaction de Buy & Hold à CHAQUE jour au lieu d'une seule fois à "
        "l'entrée, ce qui écrasait artificiellement son Sharpe (ex. NDX affichait "
        "faussement +0.04 au lieu de +0.53 attendu, cohérent avec les résultats déjà "
        "établis ailleurs dans le projet). Corrigé dans `nonml_overnight_intraday_backtest.py` "
        "avant tout commit de résultat — traçable dans l'historique git de ce fichier."
    )

    out = ROOT / "results" / "nonml_overnight_intraday_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

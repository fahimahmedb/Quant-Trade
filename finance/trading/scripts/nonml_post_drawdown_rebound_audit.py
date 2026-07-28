"""Audit adversarial — Overlay levé post-drawdown extrême.

Vérifie la logique de détection de choc et de fenêtre de levier sur un
exemple synthétique construit à la main (pas de biais de sélection sur
les vraies données), où le résultat attendu est connu par construction.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_post_drawdown_rebound_backtest import rebound_exposure, DD_WINDOW, DD_THRESHOLD, REBOUND_LEN, CAP  # noqa: E402


def main():
    lines = ["# Audit adversarial — Overlay levé post-drawdown extrême", "",
             "## Test sur série synthétique (résultat attendu connu par construction)", ""]

    # Serie synthetique : plat a 100 pendant 30j, puis chute a 85 (-15%, > seuil -10%)
    # en 1 jour, puis plat a 85 indefiniment.
    #
    # ATTENTION (nuance trouvee en construisant ce test) : la pre-registration dit
    # explicitement "...ou nouveau choc qui prolonge/relance la fenetre". Avec un
    # drawdown mesure sur un MAX ROULANT de 20j, le niveau pre-choc (100) reste dans
    # la fenetre roulante pendant 20 jours apres la chute -> le drawdown reste <= -10%
    # chaque jour de t=30 a t=49, redeclenchant le choc CHAQUE jour durant cette
    # periode (comportement conforme au texte pre-enregistre, pas un bug de calcul).
    # Le dernier redeclenchement (t=49) etend donc le levier jusqu'a 49+20-1=68.
    close = np.concatenate([np.full(30, 100.0), np.full(1, 85.0), np.full(60, 85.0)])
    pos = rebound_exposure(close)

    shock_day = 30
    last_retrigger_day = shock_day + DD_WINDOW - 1  # dernier jour ou le rolling max contient encore 100
    expected_lev_days = set(range(shock_day, last_retrigger_day + REBOUND_LEN))
    actual_lev_days = set(np.where(pos > 1.0)[0])

    ok = expected_lev_days == actual_lev_days
    lines.append(f"Jours de levier attendus (choc initial jour {shock_day}, re-déclenché "
                 f"jusqu'au jour {last_retrigger_day} tant que le max roulant contient le "
                 f"niveau pré-choc, dernière extension +{REBOUND_LEN}j) : "
                 f"{sorted(expected_lev_days)[:3]}...{sorted(expected_lev_days)[-3:]}")
    lines.append(f"Jours de levier observés : {sorted(actual_lev_days)[:3]}...{sorted(actual_lev_days)[-3:] if actual_lev_days else []}")
    lines.append(f"**{'OK — logique de détection/fenêtre conforme à la pré-registration (le re-déclenchement prolongé est un comportement PRÉVU du design, pas un bug).' if ok else 'ÉCHEC — divergence, bug à corriger.'}**")
    lines.append("")
    lines.append(
        "**Interprétation du FAIL du backtest principal** : sur les 5 marchés réels, "
        "lever l'exposition juste après un choc amplifie le risque de POURSUITE de la "
        "baisse (les chocs de marché ne sont pas suivis d'un rebond systématique à court "
        "terme — mécanisme similaire au reversal titre du cycle #5, également en échec "
        "net). Ce n'est pas un artefact de mesure : les MDD de l'overlay sont "
        "systématiquement pires que Buy&Hold sur les 5 marchés."
    )

    out = ROOT / "results" / "nonml_post_drawdown_rebound_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

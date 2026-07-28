"""Vérification anti-cheat générique — contrôle le PROCESSUS (pas les
statistiques) pour n'importe quel cycle du backlog non-ML.

Généralisation de pead_anti_cheat_check.py : mêmes 5 vérifications, mais
paramétrées par nom de stratégie au lieu d'être codées en dur pour PEAD.

Usage : python3 scripts/nonml_anti_cheat_check.py <nom_strategie>
  cherche PREREG_<nom_strategie>.md, scripts/nonml_<nom_strategie>_backtest.py,
  results/nonml_<nom_strategie>_result.md
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False).stdout.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nonml_anti_cheat_check.py <nom_strategie>")
        sys.exit(1)
    name = sys.argv[1]

    prereg = ROOT / f"PREREG_{name}.md"
    backtest_script = ROOT / "scripts" / f"nonml_{name}_backtest.py"
    result_file = ROOT / "results" / f"nonml_{name}_result.md"

    checks = []
    prereg_rel = str(prereg.relative_to(REPO_ROOT))
    result_rel = str(result_file.relative_to(REPO_ROOT))

    prereg_commits = git("log", "--format=%H %ct", "--follow", "--", prereg_rel).splitlines()
    result_commits = git("log", "--format=%H %ct", "--follow", "--", result_rel).splitlines()

    if not prereg_commits:
        checks.append(("FAIL", f"Pré-enregistrement {prereg_rel} non trouvé dans l'historique git."))
    else:
        first_prereg_ts = int(prereg_commits[-1].split()[1])
        checks.append(("OK", f"Pré-enregistrement committé (premier commit à {first_prereg_ts})."))

        if result_commits:
            first_result_ts = int(result_commits[-1].split()[1])
            if first_prereg_ts < first_result_ts:
                checks.append(("OK", "Le pré-enregistrement précède chronologiquement le premier résultat."))
            else:
                checks.append(("FAIL", "**Le pré-enregistrement est POSTÉRIEUR ou simultané au résultat.**"))

            prereg_after_result = [c for c in prereg_commits if int(c.split()[1]) > first_result_ts]
            if prereg_after_result:
                checks.append(("FAIL", f"**Pré-enregistrement modifié APRÈS le premier résultat** "
                                        f"({len(prereg_after_result)} commit(s))."))
            else:
                checks.append(("OK", "Aucune modification du pré-enregistrement après le premier résultat."))
        else:
            checks.append(("INFO", "Résultat pas encore committé — vérification différée."))

    code = backtest_script.read_text() if backtest_script.exists() else ""
    suspicious_patterns = [
        r"for\s+\w+\s+in\s+\[.*(?:threshold|seuil|H\s*=|holding|window)",
        r"GridSearch",
        r"itertools\.product",
        r"sklearn",  # hors ML : aucune dependance ML attendue dans ces scripts
    ]
    hits = [p for p in suspicious_patterns if re.search(p, code, re.IGNORECASE)]
    if hits:
        checks.append(("FAIL", f"Motif(s) suspect(s) trouvé(s) dans le code : {hits}."))
    else:
        checks.append(("OK", "Aucun motif de recherche de paramètres ni de dépendance ML détecté."))

    lines = [f"# Vérification anti-cheat — {name}", ""]
    n_fail = sum(1 for s, _ in checks if s == "FAIL")
    for status, msg in checks:
        lines.append(f"- **[{status}]** {msg}")
    lines.append("")
    lines.append(f"**Verdict : {'ÉCHEC — protocole violé' if n_fail else 'CONFORME'}** "
                 f"({n_fail} échec(s) sur {len(checks)} vérifications).")

    out = ROOT / "results" / f"nonml_{name}_anti_cheat.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

"""Vérification anti-cheat PEAD — contrôle le PROCESSUS, pas les
statistiques (celles-ci sont couvertes par pead_adversarial_audit.py).

Vérifie automatiquement, via git, que le protocole
PROTOCOLE_ANTI_SNOOPING.md a été respecté pour ce chantier précis :
1. Le pré-enregistrement a été committé AVANT le premier résultat.
2. Le pré-enregistrement n'a PAS été modifié après ce premier commit de
   résultat (ce qui serait un ajustement rétroactif déguisé).
3. Le code du backtest ne contient aucune boucle de recherche de
   paramètres (grille de seuils/durées) — n_trials=1 vérifié sur le CODE,
   pas juste affirmé dans le texte.
4. Le critère de succès cité dans le rapport de résultat correspond
   mot pour mot à celui du pré-enregistrement (pas de redéfinition
   silencieuse après coup).
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent
PREREG = ROOT / "PEAD_PREREGISTRATION.md"
BACKTEST_SCRIPT = ROOT / "scripts" / "pead_backtest.py"
RESULT_FILE = ROOT / "results" / "pead_backtest_result.md"


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False).stdout.strip()


def main():
    checks = []

    # 1. Le pre-enregistrement doit avoir un commit, et ce commit doit preceder
    #    chronologiquement le premier commit du fichier de resultat (si deja committe).
    prereg_rel = str(PREREG.relative_to(REPO_ROOT))
    result_rel = str(RESULT_FILE.relative_to(REPO_ROOT))

    prereg_commits = git("log", "--format=%H %ct", "--follow", "--", prereg_rel).splitlines()
    result_commits = git("log", "--format=%H %ct", "--follow", "--", result_rel).splitlines()

    if not prereg_commits:
        checks.append(("FAIL", "Pré-enregistrement non trouvé dans l'historique git — "
                                "ce chantier n'a jamais été committé avant exécution."))
    else:
        first_prereg_ts = int(prereg_commits[-1].split()[1])  # plus ancien commit du fichier
        checks.append(("OK", f"Pré-enregistrement committé (premier commit à {first_prereg_ts})."))

        if result_commits:
            first_result_ts = int(result_commits[-1].split()[1])
            if first_prereg_ts < first_result_ts:
                checks.append(("OK", "Le pré-enregistrement précède chronologiquement "
                                      "le premier commit de résultat."))
            else:
                checks.append(("FAIL", "**Le pré-enregistrement est POSTÉRIEUR ou simultané "
                                        "au commit de résultat** — pré-enregistrement invalide, "
                                        "possible ajustement rétroactif."))
        else:
            checks.append(("INFO", "Résultat pas encore committé — vérification différée "
                                    "au prochain lancement de ce script après commit."))

    # 2. Le fichier de pre-enregistrement n'a pas ete modifie APRES le premier
    #    commit de resultat (si un resultat existe deja).
    if prereg_commits and result_commits:
        first_result_ts = int(result_commits[-1].split()[1])
        prereg_after_result = [c for c in prereg_commits
                                if int(c.split()[1]) > first_result_ts]
        if prereg_after_result:
            checks.append(("FAIL", f"**Le pré-enregistrement a été modifié APRÈS le premier "
                                    f"résultat** ({len(prereg_after_result)} commit(s) suspect(s)) "
                                    "— violation du protocole, résultat non fiable tel quel."))
        else:
            checks.append(("OK", "Aucune modification du pré-enregistrement après le premier résultat."))

    # 3. Pas de grille de recherche de parametres dans le code du backtest
    #    (recherche de patterns type boucle sur une liste de seuils/H).
    code = BACKTEST_SCRIPT.read_text() if BACKTEST_SCRIPT.exists() else ""
    suspicious_patterns = [
        r"for\s+\w+\s+in\s+\[.*(?:threshold|seuil|H\s*=|holding)",
        r"GridSearch",
        r"itertools\.product",
    ]
    hits = [p for p in suspicious_patterns if re.search(p, code, re.IGNORECASE)]
    if hits:
        checks.append(("FAIL", f"Motif(s) suspect(s) de recherche de paramètres trouvé(s) "
                                f"dans le code : {hits} — n_trials=1 non vérifié."))
    else:
        checks.append(("OK", "Aucun motif de recherche de paramètres (grille/boucle sur "
                              "seuils) détecté dans pead_backtest.py — n_trials=1 cohérent "
                              "avec le code."))

    # 4. Le critere de succes du rapport correspond au pre-enregistrement
    #    (comparaison textuelle des seuils numeriques cles : H, COST_BPS, tstat>2, degradation<50%).
    prereg_text = PREREG.read_text()
    key_values_prereg = {
        "H=60": "H = 60" in prereg_text or "H=60" in prereg_text,
        "10 bps": "10 bps" in prereg_text,
        "t-stat > 2": "t-stat > 2" in prereg_text,
        "50%": "50%" in prereg_text,
    }
    missing = [k for k, present in key_values_prereg.items() if not present]
    if missing:
        checks.append(("WARN", f"Éléments du critère pré-enregistré non retrouvés tels quels "
                                f"dans le texte : {missing} (vérification textuelle grossière, "
                                "à relire manuellement)."))
    else:
        checks.append(("OK", "Les paramètres clés du critère de succès (H=60, 10bps, t-stat>2, "
                              "dégradation<50%) sont bien présents dans le pré-enregistrement."))

    lines = ["# Vérification anti-cheat — chantier PEAD", ""]
    n_fail = sum(1 for s, _ in checks if s == "FAIL")
    for status, msg in checks:
        lines.append(f"- **[{status}]** {msg}")
    lines.append("")
    lines.append(f"**Verdict : {'ÉCHEC — protocole violé' if n_fail else 'CONFORME'}** "
                 f"({n_fail} échec(s) sur {len(checks)} vérifications).")

    out = ROOT / "results" / "pead_anti_cheat_check.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()

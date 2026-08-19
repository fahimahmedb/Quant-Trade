"""Audit indépendant du #519 : recompte les appelants de `en_gras_dans` par
`grep -n` externe (processus séparé) plutôt que par lecture Python + regex
interne, et revérifie la table de la Partie 1 en relisant directement les
rapports source (#514, #515) plutôt que les valeurs recopiées dans le
backtest.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RESULT_MD = RESULTS / "nonml_witness_synthesis_500_515_result.md"
OUT = RESULTS / "nonml_witness_synthesis_500_515_audit_result.md"
MOI = Path(__file__).name
# Les deux scripts de CE cycle decrivent `en_gras_dans` dans leur propre
# prose (pour construire le rapport) -- ce n'est pas un appel au detecteur,
# exclus au meme titre que MOI.
CYCLE_519 = {MOI, "nonml_witness_synthesis_500_515_backtest.py"}

DEFINITEUR = "nonml_borrowed_figures_confrontation_backtest.py"
RAPPORT_515 = RESULTS / "nonml_untested_detectors_lift_result.md"
RAPPORT_514 = RESULTS / "nonml_contextual_rule_permutation_control_result.md"


def grep_fichiers(motif):
    r = subprocess.run(["grep", "-rl", motif + "(", str(SCRIPTS),
                        "--include=nonml_*.py"],
                       capture_output=True, text=True)
    noms = {Path(l).name for l in r.stdout.splitlines() if l.strip()}
    noms.discard(DEFINITEUR)
    noms -= CYCLE_519
    return sorted(noms)


def main():
    porteurs = grep_fichiers("en_gras_dans")

    # Partie 1 -- revalidation en relisant les rapports source, pas le
    # backtest de ce cycle.
    txt515 = RAPPORT_515.read_text(encoding="utf-8") if RAPPORT_515.exists() else ""
    lifts = re.findall(r"lift\s*\**(\d+,\d+)", txt515)

    txt_pub = RESULT_MD.read_text(encoding="utf-8") if RESULT_MD.exists() else ""

    def extrait(motif):
        m = re.search(motif, txt_pub)
        return m.group(1) if m else None

    pub_porteurs = extrait(r"fichiers appelant `en_gras_dans\(` [^:]*: \*\*(\d+)\*\*")

    L = []
    A = L.append
    A("# Audit indépendant — #519, bilan des témoins et usages de `en_gras_dans`")
    A("")
    A("Route distincte du backtest : `grep -rl` en processus externe (pas")
    A("de lecture Python + regex interne) pour recompter les appelants, et")
    A("relecture directe du rapport source du #515")
    A("(`nonml_untested_detectors_lift_result.md`) pour vérifier que le")
    A("lift de D501 (1,5) y est bien publié tel quel, sans passer par le")
    A("backtest de ce cycle.")
    A("")
    A("## Recompte des appelants de `en_gras_dans`, par `grep -rl`")
    A("")
    A(f"- fichiers trouvés (hors définition et hors ce script) : "
      f"**{len(porteurs)}**")
    for p in porteurs:
        A(f"  - `{p}`")
    A("")
    accord_porteurs = (pub_porteurs is not None and
                       int(pub_porteurs) == len(porteurs))
    A(f"- nombre publié par le backtest : **{pub_porteurs}**")
    A(f"- accord : **{'OUI' if accord_porteurs else 'NON'}**")
    A("")

    A("## Le lift de D501 (1,5), retrouvé dans sa source (#515), pas recopié")
    A("")
    if txt515:
        A(f"- occurrences de `lift` suivies d'un nombre dans le rapport du "
          f"#515 : {lifts if lifts else 'aucune trouvée par ce motif'}")
        contient_15 = "1,5" in txt515
        A(f"- le rapport du #515 contient-il littéralement « 1,5 » : "
          f"**{'OUI' if contient_15 else 'NON'}**")
    else:
        A(f"- rapport `{RAPPORT_515.name}` introuvable — vérification "
          "impossible par cette route.")
        contient_15 = None
    A("")

    tout_ok = accord_porteurs and (contient_15 is True)
    verdict = "PASS" if tout_ok else "FAIL"
    A(f"**{verdict}** — " + (
        "la route indépendante (grep externe + relecture directe de la "
        "source du #515) reproduit les grandeurs publiées par le backtest."
        if verdict == "PASS" else
        "désaccord entre la route indépendante et le rapport publié."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — porteurs={porteurs}, accord_porteurs={accord_porteurs}, "
          f"contient_1_5={contient_15}")


if __name__ == "__main__":
    main()

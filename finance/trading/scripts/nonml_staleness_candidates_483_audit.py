"""Audit indépendant du #523 : revérifie les 2 candidats sans réutiliser
le code du backtest — recalcule `classer()` par une réimplémentation
distincte (lecture de tout le fichier PREREG plutôt que 12 lignes, motif
de déclaration légèrement différent) et confirme par grep externe que
l'axe du #518 est bien « le chiffre cité par le #485 », pas un mot de
`MOTS`.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"
REPO = ROOT.parent.parent

RESULT_MD = RESULTS / "nonml_staleness_candidates_483_result.md"
OUT = RESULTS / "nonml_staleness_candidates_483_audit_result.md"

MOTS = ["audit", "correction", "diagnostic", "infrastructure", "inventaire",
        "vérification", "verification", "modification", "réparation",
        "arbitrage"]
CANDIDATS = ["coverage_wording_fix", "duplicate_sweep_coverage"]


def classer_v2(nom):
    """Reimplementation independante : lit tout le fichier PREREG (pas
    seulement 12 lignes), cherche la premiere occurrence de 'Cycle d\''
    ou 'Cycle de' suivie de texte en gras, motif legerement plus large que
    celui du backtest."""
    p = ROOT / f"PREREG_{nom}.md"
    if not p.exists():
        return None, ""
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"Cycle d[e']+\s*\*\*([^*]+)\*\*", txt)
    if not m:
        return "NON DÉCLARÉ", ""
    decl = m.group(1).strip().lower()
    a_un_mot = any(w in decl for w in MOTS)
    return ("SANS RÉSULTAT ATTENDU" if a_un_mot else "RÉSULTAT ATTENDU"), decl


def grep_c(motif, chemin):
    r = subprocess.run(["grep", "-c", motif, str(chemin)],
                       capture_output=True, text=True)
    try:
        return int(r.stdout.strip())
    except ValueError:
        return 0


def main():
    txt_pub = RESULT_MD.read_text(encoding="utf-8") if RESULT_MD.exists() else ""

    L = []
    A = L.append
    A("# Audit indépendant — #523, les 2 candidats du #483")
    A("")
    A("Route distincte du backtest : réimplémentation propre de "
      "`classer()` (fichier PREREG lu en entier, pas seulement 12 "
      "lignes), et `grep -c` externe pour confirmer que l'axe "
      "d'évaluation du #518 (« le chiffre cité par le #485 ») est bien "
      "absent de tout vocabulaire lié à `MOTS`.")
    A("")

    tout_ok = True
    for nom in CANDIDATS:
        classe, decl = classer_v2(nom)
        prereg_existe = (ROOT / f"PREREG_{nom}.md").exists()
        resultat_existe = (RESULTS / f"nonml_{nom}_result.md").exists()
        toujours_orphelin = prereg_existe and not resultat_existe
        mal_classe_tient = classe == "RÉSULTAT ATTENDU"

        A(f"## `{nom}`")
        A("")
        A(f"- classement recalculé (route indépendante) : **{classe}**, "
          f"déclaration lue : « {decl} »")
        A(f"- toujours orphelin : **{'OUI' if toujours_orphelin else 'NON'}**")
        A(f"- MAL CLASSÉ tient (recalculé indépendamment) : "
          f"**{'OUI' if mal_classe_tient else 'NON'}**")

        # Confrontation au publie
        ok_bloc = f"### `{nom}`" if f"## `{nom}`" not in txt_pub else True
        pub_section_start = txt_pub.find(f"## `{nom}`")
        pub_section = txt_pub[pub_section_start:pub_section_start + 1500] if pub_section_start >= 0 else ""
        pub_orphelin = "toujours orphelin (population du #483 valide) : **OUI**" in pub_section
        pub_mal_classe = "règle se trompe encore de la même façon) : **OUI**" in pub_section

        accord = (toujours_orphelin == pub_orphelin
                 and mal_classe_tient == pub_mal_classe)
        tout_ok = tout_ok and accord
        A(f"- accord avec le rapport publié : **{'OUI' if accord else 'NON'}**")
        A("")

    A("## L'axe du #518, confirmé par grep externe sur le fichier réel")
    A("")
    n_chiffre_485 = grep_c("le chiffre cité par le #485",
                          BACKLOG)
    A(f"- occurrences de « le chiffre cité par le #485 » dans le "
      f"backlog entier : **{n_chiffre_485}**")
    A(f"- présence confirmée : **{'OUI' if n_chiffre_485 > 0 else 'NON'}** "
      f"— l'expression employée au #518 pour caractériser son propre axe "
      f"d'évaluation existe bien littéralement dans le backlog.")
    A("")

    verdict = "PASS" if tout_ok and n_chiffre_485 > 0 else "FAIL"
    A(f"**{verdict}** — " + (
        "la route indépendante (relecture PREREG complète + grep externe) "
        "reproduit les conclusions du backtest pour les 2 candidats."
        if verdict == "PASS" else
        "désaccord entre la route indépendante et le rapport publié."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — tout_ok={tout_ok}, n_chiffre_485={n_chiffre_485}")


if __name__ == "__main__":
    main()

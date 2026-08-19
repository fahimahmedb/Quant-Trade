"""Audit indépendant du #521 : recalcule le pourcentage et les deux
comptes cités dans le rapport régénéré du #485, à partir du dictionnaire
`V` reparsé par une route distincte de celle du backtest (import direct
du module cible plutôt que regex/grep), et confirme qu'aucun seuil de
prédiction figé n'a bougé en relisant `HEAD~1` du script.
"""
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAPPORT = RESULTS / "nonml_irreparable_figures_census_result.md"
OUT = RESULTS / "nonml_census_485_stale_literals_audit_result.md"
COMMIT_REPARATION = "5915dbb"


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location(nom[:-3], p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    c485 = module("nonml_irreparable_figures_census_backtest.py")
    n_irrep = sum(1 for v in c485.V.values() if v[0] == "IRRÉPARABLE")
    n_rep = sum(1 for v in c485.V.values() if v[0] == "RÉPARABLE")
    pct = 100 * n_rep / len(c485.V)

    txt = RAPPORT.read_text(encoding="utf-8")
    m_pct = re.search(r"actionnable à (\d+,\d+) %", txt)
    pub_pct = m_pct.group(1) if m_pct else None
    m_cinq = re.search(r"une des (\d+) renvoie", txt)
    pub_irrep = int(m_cinq.group(1)) if m_cinq else None
    m_douze = re.search(r"chacun des (\d+) demande", txt)
    pub_rep = int(m_douze.group(1)) if m_douze else None

    accord_pct = pub_pct is not None and abs(float(pub_pct.replace(",", ".")) - pct) < 0.05
    accord_irrep = pub_irrep == n_irrep
    accord_rep = pub_rep == n_rep

    # Seuils figes : relire HEAD~1 (avant reparation) et HEAD, confirmer
    # que les deux lignes de seuil sont identiques.
    def extrait_seuils(rev):
        s = git("show", f"{rev}:finance/trading/scripts/"
                "nonml_irreparable_figures_census_backtest.py")
        return re.findall(r"len\(irrep\) >= \d+|len\(rep\) >= \d+", s)

    seuils_avant = extrait_seuils(f"{COMMIT_REPARATION}~1")
    seuils_apres = extrait_seuils(COMMIT_REPARATION)
    seuils_inchanges = seuils_avant == seuils_apres and len(seuils_avant) == 2

    L = []
    A = L.append
    A("# Audit indépendant — #521, littéraux périmés du script du #485")
    A("")
    A("Route distincte du backtest : import direct du module cible (pas")
    A("de regex sur texte source) pour recalculer `n_irrep`, `n_rep` et le")
    A("pourcentage depuis son dictionnaire `V` ; comparaison de `HEAD~1` à")
    A("`HEAD` via `git show` pour les seuils de prédiction figés.")
    A("")
    A("## Recalcul depuis le module importé, vs publié dans le rapport")
    A("")
    A("| Grandeur | Recalculée | Publiée | Accord |")
    A("|---|---|---|---|")
    A(f"| irréparables | {n_irrep} | {pub_irrep} | "
      f"**{'OUI' if accord_irrep else 'NON'}** |")
    A(f"| réparables | {n_rep} | {pub_rep} | "
      f"**{'OUI' if accord_rep else 'NON'}** |")
    A(f"| % réparables (dette actionnable) | {pct:.1f} % | {pub_pct} % | "
      f"**{'OUI' if accord_pct else 'NON'}** |")
    A("")

    A("## Les seuils de prédiction figés — inchangés par le commit de réparation")
    A("")
    A(f"- seuils avant (`{COMMIT_REPARATION}~1`) : {seuils_avant}")
    A(f"- seuils après (`{COMMIT_REPARATION}`) : {seuils_apres}")
    A(f"- identiques : **{'OUI' if seuils_inchanges else 'NON'}**")
    A("")

    verdict = "PASS" if (accord_irrep and accord_rep and accord_pct
                         and seuils_inchanges) else "FAIL"
    A(f"**{verdict}** — " + (
        "la route indépendante (import direct du module) reproduit les "
        "3 grandeurs publiées, et les seuils de prédiction figés du #485 "
        "sont confirmés intacts par comparaison git directe."
        if verdict == "PASS" else
        "désaccord entre la route indépendante et le rapport publié."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — irrep={n_irrep}/{pub_irrep} rep={n_rep}/{pub_rep} "
          f"pct={pct:.1f}/{pub_pct} seuils_ok={seuils_inchanges}")


if __name__ == "__main__":
    main()

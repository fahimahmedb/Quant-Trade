"""Audit indépendant — #534, correction du statut stale d'E3.

Route distincte du backtest : recalcule les comptes de séances par
lecture de fichier BRUTE (comptage de lignes, sans passer par
`data_loader.load_ohlc`) plutôt que de faire confiance au chargeur du
backtest ; vérifie le commit de correction par `git show` externe.

Lecture du disque et de l'historique git, aucune modification, aucun
script de marché exécuté.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent
RESULTS = ROOT / "results"
ECON = ROOT / "ECONOMIC_MULTIASSET_BACKLOG.md"

OUT = RESULTS / "nonml_economic_backlog_e3_fetch_status_correction_audit_result.md"

FICHIERS = {
    "TLT": ("tlt_daily.txt", 6051),
    "GLD": ("gld_daily.txt", 2512),
    "UUP": ("uup_daily.txt", 4898),
}
COMMIT_CORRECTION = "6cd3ff5"


def compte_lignes_donnees(path):
    """Compte les lignes de donnees BRUTES (tout sauf l'en-tete), sans
    passer par le parseur du backtest -- route independante."""
    with open(path, encoding="utf-8") as f:
        lignes = f.readlines()
    return len(lignes) - 1  # 1 ligne d'en-tete


def main():
    L = ["# Audit indépendant — #534, correction du statut stale d'E3", ""]

    L.append("## Recompte brut des lignes de données (sans `data_loader`)")
    L.append("")
    L.append("| Fichier | Lignes de données (comptage brut) | Attendu "
             "(backtest) | Accord |")
    L.append("|---|---|---|---|")
    tout_accord = True
    for nom, (fichier, attendu) in FICHIERS.items():
        path = REPO_ROOT / "data" / fichier
        n = compte_lignes_donnees(path)
        accord = (n == attendu)
        tout_accord = tout_accord and accord
        L.append(f"| {nom} | {n} | {attendu} | "
                 f"{'OUI' if accord else 'NON'} |")
    L.append("")
    L.append(f"- accord sur les 3 fichiers, route de comptage indépendante : "
             f"**{'OUI' if tout_accord else 'NON'}**")
    L.append("")

    L.append("## Commit de correction vérifié par `git show`")
    L.append("")
    show = subprocess.run(
        ["git", "show", "--name-only", "--format=", COMMIT_CORRECTION],
        capture_output=True, text=True, cwd=REPO_ROOT)
    fichiers_touches = sorted(l for l in show.stdout.splitlines() if l.strip())
    attendus = sorted([
        "finance/trading/ECONOMIC_MULTIASSET_BACKLOG.md",
        "finance/trading/results/nonml_economic_backlog_e3_fetch_status_correction_result.md",
        "finance/trading/scripts/nonml_economic_backlog_e3_fetch_status_correction_backtest.py",
    ])
    L.append(f"- fichiers touchés par {COMMIT_CORRECTION} : "
             f"**{len(fichiers_touches)}**")
    for f in fichiers_touches:
        L.append(f"  - `{f}`")
    diff_attendu = (fichiers_touches == attendus)
    L.append(f"- exactement les 3 fichiers attendus (backtest, résultat, "
             f"backlog corrigé) : **{'OUI' if diff_attendu else 'NON'}**")
    L.append("")

    diff_econ = subprocess.run(
        ["git", "show", "--format=", COMMIT_CORRECTION, "--",
         "finance/trading/ECONOMIC_MULTIASSET_BACKLOG.md"],
        capture_output=True, text=True, cwd=REPO_ROOT)
    lignes_plus = [l for l in diff_econ.stdout.splitlines()
                   if l.startswith("+") and not l.startswith("+++")]
    lignes_moins = [l for l in diff_econ.stdout.splitlines()
                    if l.startswith("-") and not l.startswith("---")]
    diff_econ_borne = (len(lignes_plus) == 1 and len(lignes_moins) == 1)
    L.append(f"- diff du backlog économique lui-même : **{len(lignes_moins)}** "
             f"ligne(s) retirée(s), **{len(lignes_plus)}** ligne(s) ajoutée(s) "
             f"— borné à 1/1 : **{'OUI' if diff_econ_borne else 'NON'}**")
    L.append("")

    contient_e3_stale = "fetch en cours" in ECON.read_text(encoding="utf-8")
    L.append(f"- l'ancien texte (« fetch en cours ») encore présent dans le "
             f"fichier actuel : **{'OUI (problème)' if contient_e3_stale else 'NON'}**")
    L.append("")

    verdict = ("PASS" if (tout_accord and diff_attendu and diff_econ_borne
                          and not contient_e3_stale) else "FAIL")
    L.append(f"**{verdict}** — la route indépendante (comptage brut de "
             f"lignes, `git show` externe) confirme les comptes du "
             f"backtest, le périmètre exact du commit de correction, et "
             f"le diff du backlog économique borné à une seule ligne "
             f"remplacée.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — tout_accord={tout_accord}, diff_attendu={diff_attendu}, "
          f"diff_econ_borne={diff_econ_borne}")
    return verdict


if __name__ == "__main__":
    main()

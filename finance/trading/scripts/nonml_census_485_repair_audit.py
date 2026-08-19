"""Audit indépendant du #520 : réparation du dictionnaire V du #485.

Ne réutilise pas le module `nonml_irreparable_figures_census_backtest`
(pas d'import) -- reparse son code source par une route texte/AST
indépendante, et compare au commit précédent (`git show HEAD~1`) plutôt
qu'à une copie locale, pour vérifier le diff annoncé au pré-enregistrement.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

CIBLE = SCRIPTS / "nonml_irreparable_figures_census_backtest.py"
RAPPORT = RESULTS / "nonml_irreparable_figures_census_result.md"
OUT = RESULTS / "nonml_census_485_repair_audit_result.md"

ATTENDU = {
    "nonml_reproducibility_campaign_v3_lot2_audit.py": "RÉPARABLE",
    "nonml_battery_backfill_lot_audit.py": "IRRÉPARABLE",
    "nonml_coverage_wording_fix_audit.py": "IRRÉPARABLE",
    "nonml_report_idempotence_backtest.py": "IRRÉPARABLE",
    "nonml_reproducibility_campaign_v2_audit.py": "IRRÉPARABLE",
}


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def extraire_V(src):
    """Reparse le dictionnaire V par une regex sur le texte brut -- route
    differente de l'AST utilise par le backtest lui-meme pour construire
    sa population."""
    out = {}
    for m in re.finditer(
            r'"(nonml_[a-z0-9_]+\.py)":\s*\("(RÉPARABLE|IRRÉPARABLE)"',
            src):
        out[m.group(1)] = m.group(2)
    return out


def main():
    src_actuel = CIBLE.read_text(encoding="utf-8")
    V_actuel = extraire_V(src_actuel)

    src_avant = git("show", f"HEAD~1:finance/trading/scripts/{CIBLE.name}")
    V_avant = extraire_V(src_avant) if src_avant else {}

    L = []
    A = L.append
    A("# Audit indépendant — #520, réparation du dictionnaire V du #485")
    A("")
    A("Route indépendante : reparse `V` par regex sur le texte brut (pas")
    A("l'AST du backtest, pas d'import du module), et compare au commit")
    A("précédent via `git show HEAD~1` plutôt qu'à une copie locale.")
    A("")
    A("## Les 5 verdicts corrigés, vérifiés un par un")
    A("")
    A("| Script | Avant (HEAD~1) | Après | Attendu | Accord |")
    A("|---|---|---|---|---|")
    tout_ok = True
    for nom, attendu in ATTENDU.items():
        avant = V_avant.get(nom, "absent")
        apres = V_actuel.get(nom, "absent")
        ok = apres == attendu
        tout_ok = tout_ok and ok
        A(f"| `{nom}` | {avant} | {apres} | {attendu} | "
          f"**{'OUI' if ok else 'NON'}** |")
    A("")

    # Les 12 autres entrees ne doivent PAS avoir change.
    autres_avant = {k: v for k, v in V_avant.items() if k not in ATTENDU}
    autres_apres = {k: V_actuel.get(k) for k in autres_avant}
    inchangees = autres_avant == autres_apres
    A(f"- les **{len(autres_avant)}** autres entrées de `V` sont-elles "
      f"identiques avant/après : **{'OUI' if inchangees else 'NON'}**")
    if not inchangees:
        for k in autres_avant:
            if autres_avant[k] != autres_apres.get(k):
                A(f"  - `{k}` : {autres_avant[k]} → {autres_apres.get(k)}")
    A("")

    A("## Le compte du rapport, recalculé indépendamment depuis `V`")
    A("")
    n_irrep = sum(1 for v in V_actuel.values() if v == "IRRÉPARABLE")
    n_rep = sum(1 for v in V_actuel.values() if v == "RÉPARABLE")
    txt_rap = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""
    m = re.search(r"IRRÉPARABLES\*\* : \*\*(\d+) / (\d+)\*\*", txt_rap)
    pub_irrep = int(m.group(1)) if m else None
    pub_total = int(m.group(2)) if m else None
    m2 = re.search(r"réparables\*\* : \*\*(\d+)\*\*", txt_rap)
    pub_rep = int(m2.group(1)) if m2 else None
    A(f"- recalculé depuis `V` (regex indépendante) : "
      f"**{n_irrep}** irréparables, **{n_rep}** réparables "
      f"({len(V_actuel)} entrées au total)")
    A(f"- publié dans le rapport : **{pub_irrep} / {pub_total}** "
      f"irréparables, **{pub_rep}** réparables")
    accord_compte = (n_irrep == pub_irrep and n_rep == pub_rep
                     and len(V_actuel) == pub_total)
    A(f"- accord : **{'OUI' if accord_compte else 'NON'}**")
    A("")

    A("## Dette connue, non corrigée dans ce cycle")
    A("")
    litteral_12 = "chacun des 12" in src_actuel
    A(f"- le littéral en dur « chacun des 12 » (l.288, devrait valoir "
      f"**{n_rep}**) est-il toujours présent : "
      f"**{'OUI — dette non résolue' if litteral_12 else 'NON, déjà corrigé'}**")
    A("")
    if litteral_12:
        A("> Ce littéral décrivait une coïncidence numérique exacte avant")
        A("> ce cycle (12 réparables = « 12 » écrit en dur). La réparation")
        A("> du #520 change le compte sans le mettre à jour — **hors du")
        A("> périmètre déclaré au pré-enregistrement** (5 lignes de `V`")
        A("> uniquement). **Nouvelle dette, signalée, pas corrigée ici.**")
    A("")

    verdict = "PASS" if (tout_ok and inchangees and accord_compte) else "FAIL"
    A(f"**{verdict}** — " + (
        "les 5 corrections sont vérifiées sur pièce, les 12 autres "
        "entrées sont intactes, et le compte publié se recalcule "
        "identiquement par une route indépendante."
        if verdict == "PASS" else
        "au moins un désaccord entre la route indépendante et l'annoncé."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — 5/5 verdicts corrects={tout_ok}, "
          f"12 autres inchangées={inchangees}, compte OK={accord_compte}, "
          f"littéral_12_toujours_présent={litteral_12}")


if __name__ == "__main__":
    main()

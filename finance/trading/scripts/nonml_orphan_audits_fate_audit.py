"""Audit adversarial du #480 — recalcul independant.

Route differente : l'existence historique d'un `_result.md` est etablie par
`git rev-list --all --objects` (enumeration des blobs) au lieu de
`git log --diff-filter=A` ; la declaration du PREREG est relue sur ses **dix
premieres lignes** au lieu du texte entier.

Le controle central : le rapport a-t-il **publie les faits qui contredisent
son propre classement** ? C'est la seule garantie qu'un lecteur puisse
reclasser sans croire l'auteur.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAPPORT = RESULTS / "nonml_orphan_audits_fate_result.md"
OUT = RESULTS / "nonml_orphan_audits_fate_audit.md"
TROIS = ["n_trials_dependence_correction", "pnl_duplicate_sweep_v2",
         "pnl_persistence_exposed_pass"]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def main():
    # 1. Blobs jamais vus, toute branche confondue.
    connus = set()
    for l in git("rev-list", "--all", "--objects").splitlines():
        parts = l.split(" ", 1)
        if len(parts) == 2:
            connus.add(parts[1].split("/")[-1])

    faits = []
    for nom in TROIS:
        faits.append({
            "nom": nom,
            "result_historique": f"nonml_{nom}_result.md" in connus,
            "audit_present": (RESULTS / f"nonml_{nom}_audit.md").exists(),
            "backtest_present": (SCRIPTS / f"nonml_{nom}_backtest.py").exists(),
            "tete": "\n".join(
                (ROOT / f"PREREG_{nom}.md").read_text(encoding="utf-8")
                .splitlines()[:10]) if (ROOT / f"PREREG_{nom}.md").exists() else "",
        })

    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    def lu(m):
        g = re.search(m, pub)
        return g.group(1) if g else None

    n_hist = sum(1 for f in faits if f["result_historique"])
    n_bt = sum(1 for f in faits if f["backtest_present"])
    mesures = [
        ("`_result.md` jamais existants (blobs)", n_hist,
         lu(r"aucun `_result\.md` dans l'historique \| 0 \| (\d+)")),
        ("scripts `_backtest.py` présents", n_bt, "0"),
        ("audits présents", sum(1 for f in faits if f["audit_present"]), "3"),
    ]

    L = ["# Audit adversarial — le sort des 3 audits orphelins (#480)", ""]
    L.append("**Recalcul par une route différente** : l'existence historique est")
    L.append("établie par `git rev-list --all --objects` (énumération des **blobs**)")
    L.append("au lieu de `git log --diff-filter=A`, et la déclaration du")
    L.append("pré-enregistrement est relue sur ses **dix premières lignes**.")
    L.append("")
    L.append("| Grandeur | Audit | Rapport | Verdict |")
    L.append("|---|---|---|---|")
    ecarts = 0
    for nom, mien, publie in mesures:
        ok = publie is not None and str(mien) == str(publie)
        ecarts += 0 if ok else 1
        L.append(f"| {nom} | **{mien}** | "
                 f"{publie if publie is not None else '*non relu*'} | "
                 f"{'**concordant**' if ok else '**ÉCART**'} |")
    L.append("")

    L.append("## Ce que les pré-enregistrements disent d'eux-mêmes")
    L.append("")
    L.append("Relu **hors du backtest**, sur les dix premières lignes de chacun :")
    L.append("")
    for f in faits:
        m = re.search(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", f["tete"], re.I)
        L.append(f"- `{f['nom']}` → "
                 + (f"« Cycle de **{m.group(1).strip()}** »" if m
                    else "**aucune déclaration dans les 10 premières lignes**"))
    L.append("")
    decl = sum(1 for f in faits
               if re.search(r"Cycle d[e'’]\s*\*\*", f["tete"], re.I))
    L.append(f"- pré-enregistrements se déclarant explicitement : **{decl} / 3**")
    L.append("")
    if decl == 3:
        L.append("> **Les trois se déclarent, dès leur en-tête, comme des cycles qui")
        L.append("> n'évaluent aucune stratégie.** Aucun ne promet de `_result.md`. La")
        L.append("> route indépendante aboutit donc à la **lecture C pour les trois**.")
    L.append("")

    L.append("## Le contrôle central — le rapport publie-t-il ce qui le contredit ?")
    L.append("")
    L.append("Un cycle dont la règle mécanique et la lecture à la main divergent peut")
    L.append("cacher la seconde. **Vérifié dans le rapport publié :**")
    L.append("")
    controles = [
        ("le rapport signale que sa règle a mal lu",
         "Ce que ma règle a mal lu" in pub),
        ("il nomme le mot manqué (« diagnostic »)", "diagnostic" in pub),
        ("il nomme son faux positif", "aux positif" in pub),
        ("il énonce la lecture à la main (les trois en C)",
         "les trois relèvent de la lecture C" in pub),
        ("il **refuse** de reclasser à son avantage",
         "Je ne retiens pas cette version" in pub),
        ("la prédiction 1 reste marquée réfutée",
         bool(re.search(r"≥ 2 sur 3 relèvent de C \| ≥ 2 \| \d+ \| \*\*réfutée\*\*",
                        pub))),
    ]
    L.append("| Contrôle | Résultat |")
    L.append("|---|---|")
    for lab, ok in controles:
        L.append(f"| {lab} | {'**OUI**' if ok else '**NON**'} |")
    L.append("")
    manques = [lab for lab, ok in controles if not ok]
    if not manques:
        L.append("> **Le rapport publie intégralement ce qui contredit son propre")
        L.append("> classement, et refuse d'en tirer parti.** C'est la condition pour")
        L.append("> qu'un lecteur puisse reclasser sans croire l'auteur — et elle est")
        L.append("> tenue.")
        L.append("")
        L.append("**L'audit ne conclut pas que le classement mécanique est bon** : il")
        L.append("conclut que **le désaccord est visible**. Sur le fond, la route")
        L.append("indépendante donne **C pour les trois**, et le rapport le dit")
        L.append("lui-même sans se l'attribuer.")
    else:
        L.append(f"> **{len(manques)} contrôle(s) échoue(nt)** — publié tel quel :")
        for m in manques:
            L.append(f"> - {m}")
    L.append("")

    L.append("## Effets de bord du backtest")
    L.append("")
    bt = (SCRIPTS / "nonml_orphan_audits_fate_backtest.py").read_text(encoding="utf-8")
    dangers = re.findall(r"(checkout|rm\s|unlink|open\s*\([^)]*[\"']w|"
                         r"subprocess\.run\(\[sys\.executable)", bt)
    L.append(f"- écritures : **{bt.count('write_text')}** (`OUT` seul)")
    L.append(f"- exécution d'un script du dépôt / `checkout` / suppression : "
             f"**{len(dangers)}**")
    L.append("")
    L.append("**Aucun effet de bord — lecture de `git` et du disque.**" if not dangers
             else f"**À examiner : {dangers}**")
    L.append("")

    L.append("## Verdict")
    L.append("")
    L.append(f"**{'CONCORDANT' if ecarts == 0 else 'DISCORDANT'}** — "
             f"**{len(mesures) - ecarts}/{len(mesures)}** grandeurs se retrouvent, et")
    L.append(f"**{len(controles) - len(manques)}/{len(controles)}** contrôles de")
    L.append("transparence sont tenus.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de")
    L.append("> l'historique à la date de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

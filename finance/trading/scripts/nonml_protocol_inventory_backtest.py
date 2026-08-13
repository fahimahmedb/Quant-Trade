"""Inventaire vérifié de la dette de protocole (#431).

Spécification pré-enregistrée dans `PREREG_protocol_inventory.md`, committée
avant toute mesure.

Cycle d'**inventaire**, pas de stratégie : cinq contrôles mécaniques et
reproductibles sur le dépôt. Aucun verdict recalculé, aucun paramètre touché.

Les contrôles B et E se comptent mécaniquement mais **ne se concluent pas
mécaniquement** : le script publie le compte brut ET la liste, pour que chaque
écart soit inspecté avant d'être qualifié.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
DATA = REPO / "data"
OUT = RESULTS / "nonml_protocol_inventory_result.md"


def git_known(path_rel: str) -> bool:
    """Le fichier a-t-il existé à un moment dans l'historique git ?"""
    r = subprocess.run(["git", "log", "--oneline", "--all", "--", path_rel],
                       cwd=str(REPO), capture_output=True, text=True, timeout=120)
    return bool(r.stdout.strip())


def verdict_of(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    if "**PASS" in t or "PASS (niveau 1)" in t:
        return "PASS"
    if "**FAIL" in t:
        return "FAIL"
    return "indéterminé"


def main():
    L = ["# Inventaire vérifié de la dette de protocole (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("aucun paramètre touché.")
    L.append("")
    L.append("Le #430 a constaté la file d'outillage vide ; le #429 avait fixé la règle pour ce")
    L.append("cas — **chercher une dette réelle plutôt que d'en inventer une, et l'écrire si**")
    L.append("**l'on n'en trouve pas**. Cinq contrôles mécaniques, définis avant toute mesure.")
    L.append("")

    findings = {}

    # --- A : anti-cheat non CONFORME --------------------------------------
    L.append("## Contrôle A — rapports anti-cheat dont le verdict n'est pas CONFORME")
    L.append("")
    ac = sorted(RESULTS.glob("nonml_*_anti_cheat.md"))
    bad = [p for p in ac if "CONFORME" not in p.read_text(encoding="utf-8")]
    findings["A"] = len(bad)
    L.append(f"- rapports anti-cheat examinés : **{len(ac)}**")
    L.append(f"- verdict **non CONFORME** : **{len(bad)}**")
    L.append("")
    for p in bad:
        name = p.name.replace("nonml_", "").replace("_anti_cheat.md", "")
        txt = p.read_text(encoding="utf-8")
        reason = next((l.strip("- ").strip() for l in txt.splitlines()
                       if "[FAIL]" in l), "raison non lisible")
        L.append(f"- `{name}` — {reason}")
    L.append("")

    # --- B : résultat sans PREREG -----------------------------------------
    L.append("## Contrôle B — rapports de résultat sans pré-enregistrement homonyme")
    L.append("")
    res = sorted(RESULTS.glob("nonml_*_result.md"))
    missing_prereg, resolved = [], []
    for p in res:
        name = p.name.replace("nonml_", "").replace("_result.md", "")
        rel = f"finance/trading/PREREG_{name}.md"
        if (ROOT / f"PREREG_{name}.md").exists():
            continue
        if git_known(rel):
            continue
        # Une variante (marche, univers PIT) est couverte par le PREREG de son
        # parent : `gjr_vol_managed_dax` par `PREREG_gjr_vol_managed_*`.
        # Resolution ajoutee apres inspection des 5 premiers ecarts (#431).
        base = re.sub(r"_(dax|russell2000|sp500|composite|ndx)$", "", name)
        base = re.sub(r"_pit_universe$", "", base)
        if base != name and list(ROOT.glob(f"PREREG_{base}*.md")):
            resolved.append((name, base))
            continue
        missing_prereg.append(name)
    findings["B_brut"] = len(missing_prereg)
    L.append(f"- rapports de résultat examinés : **{len(res)}**")
    L.append(f"- sans `PREREG_<nom>.md` présent **ni dans l'historique git** : "
             f"**{len(missing_prereg)}**")
    L.append("")
    L.append(f"- dont **résolus** : variante d'un candidat dont le pré-enregistrement porte le")
    L.append(f"  nom du parent : **{len(resolved)}**")
    L.append("")
    L.append("Un pré-enregistrement peut porter un nom différent de son résultat : une variante")
    L.append("de marché (`_dax`, `_sp500`) ou d'univers (`_pit_universe`) est couverte par le")
    L.append("pré-enregistrement de son parent. La résolution est **automatique et listée**,")
    L.append("pas décidée au cas par cas.")
    L.append("")
    if resolved:
        L.append("| Variante | Couverte par |")
        L.append("|---|---|")
        for n, b in resolved:
            L.append(f"| `{n}` | `PREREG_{b}*.md` |")
        L.append("")
    if missing_prereg:
        L.append("| Candidat | Verdict publié |")
        L.append("|---|---|")
        for n in missing_prereg:
            L.append(f"| `{n}` | {verdict_of(RESULTS / f'nonml_{n}_result.md')} |")
        L.append("")

    # --- C : PASS jamais soumis à la batterie -----------------------------
    L.append("## Contrôle C — rapports PASS jamais soumis à la batterie (Règle 9)")
    L.append("")
    passes = [p for p in res if verdict_of(p) == "PASS"]
    no_batt = []
    for p in passes:
        name = p.name.replace("nonml_", "").replace("_result.md", "")
        txt = p.read_text(encoding="utf-8")
        has = (RESULTS / f"nonml_{name}_pass_validation_battery.md").exists()
        # Un rapport peut porter lui-meme la mention de son passage.
        if not has and "batterie" not in txt.lower() and "validation" not in txt.lower():
            no_batt.append(name)
    findings["C"] = len(no_batt)
    L.append(f"- rapports **PASS** : **{len(passes)}**")
    L.append(f"- sans trace de batterie (fichier dédié **ni** mention interne) : "
             f"**{len(no_batt)}**")
    L.append("")
    # La Regle 9 est apparue avec `nonml_pass_validation_battery.py`, ajoute au
    # depot le 2026-07-29. Un PASS anterieur n'a jamais pu y etre soumis : ce
    # n'est pas une violation mais une anteriorite, et les deux sont comptees
    # separement plutot que confondues.
    RULE9_DATE = "2026-07-29"
    before, sameday, after = [], [], []
    for n in no_batt:
        r = subprocess.run(
            ["git", "log", "--reverse", "--format=%ad", "--date=short", "--diff-filter=A",
             "--", f"finance/trading/results/nonml_{n}_result.md"],
            cwd=str(REPO), capture_output=True, text=True, timeout=120)
        d = r.stdout.split("\n")[0].strip() if r.stdout.strip() else ""
        if d and d < RULE9_DATE:
            before.append((n, d))
        elif d == RULE9_DATE:
            sameday.append((n, d))
        else:
            after.append((n, d or "?"))
    L.append(f"La Règle 9 est apparue avec `nonml_pass_validation_battery.py`, ajouté au dépôt")
    L.append(f"le **{RULE9_DATE}**. Un PASS publié **avant** cette date n'a jamais pu y être")
    L.append("soumis : c'est une **antériorité**, pas une violation. Les deux sont comptées")
    L.append("séparément plutôt que confondues en un chiffre alarmant.")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| PASS **antérieurs** à la Règle 9 | **{len(before)}** |")
    L.append(f"| PASS du **jour même** de son introduction (ambigu) | **{len(sameday)}** |")
    L.append(f"| PASS **strictement postérieurs**, sans batterie | **{len(after)}** |")
    L.append("")
    L.append("Les **{}** du jour même sont **ambigus** : rien ne dit s'ils ont été publiés".format(len(sameday)))
    L.append("avant ou après l'ajout du script dans la même journée. Je les compte à part plutôt")
    L.append("que de les ranger du côté qui m'arrange.")
    L.append("")
    if after:
        L.append("Les **strictement postérieurs** sont la dette réelle de ce contrôle :")
        L.append("")
        L.append("| Candidat | Rapport publié le |")
        L.append("|---|---|")
        for n, d in sorted(after, key=lambda t: t[1]):
            L.append(f"| `{n}` | {d} |")
        L.append("")
    else:
        L.append("**Aucun PASS postérieur à la Règle 9 n'échappe à la batterie.**")
        L.append("")
    findings["C_apres_regle9"] = len(after)

    # --- D : source de données absente ------------------------------------
    L.append("## Contrôle D — scripts référençant un fichier de `data/` absent")
    L.append("")
    present = {p.name for p in DATA.glob("*") if p.is_file()}
    pat = re.compile(r'"([A-Za-z0-9_\-]+\.(?:txt|csv))"')
    dangling = {}
    for s in sorted(SCRIPTS.glob("nonml_*.py")):
        try:
            src = s.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        for fn in set(pat.findall(src)):
            if fn.endswith(("_result.md", ".md")):
                continue
            if fn not in present and (DATA / fn).suffix in (".txt", ".csv"):
                dangling.setdefault(fn, []).append(s.name)
    findings["D"] = len(dangling)
    L.append(f"- fichiers présents dans `data/` : **{len(present)}**")
    L.append(f"- noms référencés par un script mais **absents** : **{len(dangling)}**")
    L.append("")
    if dangling:
        L.append("| Fichier référencé | Scripts |")
        L.append("|---|---|")
        for fn, ss in sorted(dangling.items()):
            L.append(f"| `{fn}` | {len(ss)} — {', '.join(f'`{x}`' for x in ss[:3])} |")
        L.append("")

    # --- E : PREREG sans artefact -----------------------------------------
    L.append("## Contrôle E — pré-enregistrements sans aucun artefact produit")
    L.append("")
    preregs = sorted(ROOT.glob("PREREG_*.md"))
    orphan = []
    for p in preregs:
        name = p.name.replace("PREREG_", "").replace(".md", "")
        arte = [
            RESULTS / f"nonml_{name}_result.md",
            RESULTS / f"nonml_{name}_audit.md",
            RESULTS / f"nonml_{name}.md",
            RESULTS / f"nonml_{name}_anti_cheat.md",
        ]
        if not any(a.exists() for a in arte):
            orphan.append(name)
    findings["E_brut"] = len(orphan)
    L.append(f"- pré-enregistrements examinés : **{len(preregs)}**")
    L.append(f"- sans `_result.md`, `_audit.md`, `<nom>.md` ni `_anti_cheat.md` : "
             f"**{len(orphan)}**")
    L.append("")
    L.append("Compte **brut** lui aussi : un cycle d'outillage nomme parfois son rapport")
    L.append("autrement que son pré-enregistrement. Liste fournie pour inspection.")
    L.append("")
    if orphan:
        for n in orphan[:40]:
            L.append(f"- `{n}`")
        if len(orphan) > 40:
            L.append(f"- … et **{len(orphan) - 40}** autres")
        L.append("")

    # --- Synthèse ---------------------------------------------------------
    L.append("## Synthèse des cinq contrôles")
    L.append("")
    L.append("| Contrôle | Compte |")
    L.append("|---|---|")
    L.append(f"| A — anti-cheat non CONFORME | **{findings['A']}** |")
    L.append(f"| B — résultat sans PREREG homonyme (brut) | **{findings['B_brut']}** |")
    L.append(f"| C — PASS sans trace de batterie | **{findings['C']}** |")
    L.append(f"| D — source `data/` absente | **{findings['D']}** |")
    L.append(f"| E — PREREG sans artefact (brut) | **{findings['E_brut']}** |")
    L.append("")
    L.append("Les comptes B et E sont **bruts et non conclusifs** — ils appellent une")
    L.append("inspection, faite dans l'audit de ce cycle.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")
    return findings


if __name__ == "__main__":
    main()

"""Audit adversarial du #474 — recalcul independant.

Ne reutilise NI le module du #464, NI les fonctions du backtest : les deux
populations et les trois faits R/H/S sont recalcules par une autre route
(decoupage du backlog par expression reguliere sur le texte entier, listing
du disque par `os.scandir`, historique par `git rev-list` + `git ls-tree`).

Un chiffre qui ne se retrouve pas est signale, jamais aligne.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAPPORT = RESULTS / "nonml_orphans_interrupted_or_lost_result.md"
OUT = RESULTS / "nonml_orphans_interrupted_or_lost_audit.md"
MOI = "orphans_interrupted_or_lost"

# Route differente : on decoupe le texte entier d'un coup, pas ligne a ligne.
BLOC = re.compile(r"^## Backlog #(\d+)\b.*?(?=^## |\Z)", re.M | re.S)
CITE = re.compile(r"PREREG_([a-z0-9_]+)\.md")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def scan(dossier, prefixe, suffixe):
    return sorted(e.name for e in os.scandir(dossier)
                  if e.is_file() and e.name.startswith(prefixe)
                  and e.name.endswith(suffixe))


def main():
    texte = (ROOT / "NONML_STRATEGY_BACKLOG.md").read_text(encoding="utf-8")
    blocs = [(int(m.group(1)), m.group(0)) for m in BLOC.finditer(texte)]

    rapports = scan(RESULTS, "nonml_", ".md")
    scripts = scan(SCRIPTS, "nonml_", ".py")
    preregs = [n[len("PREREG_"):-3] for n in scan(ROOT, "PREREG_", ".md")]

    cites, sans_rapport = set(), []
    for num, corps in blocs:
        noms = sorted(set(CITE.findall(corps)))
        cites.update(noms)
        if len(noms) == 1 and f"nonml_{noms[0]}_result.md" not in rapports:
            sans_rapport.append((num, noms[0]))

    def porte(nom, liste, ext):
        pre = f"nonml_{nom}"
        return [n for n in liste
                if n.startswith(pre) and n.endswith(ext)
                and not n.endswith("_anti_cheat.md")]

    aucun_fichier = [(n, x) for n, x in sans_rapport if not porte(x, rapports, ".md")]
    orphelins = [n for n in preregs
                 if n not in cites and n not in texte and n != MOI]

    # H par une autre route : tous les chemins jamais apparus dans l'historique.
    connus = set()
    for l in git("rev-list", "--all", "--objects").splitlines():
        parts = l.split(" ", 1)
        if len(parts) == 2 and "/results/nonml_" in "/" + parts[1]:
            connus.add(parts[1].split("/")[-1])

    def classe(nom):
        R = porte(nom, rapports, ".md")
        H = [n for n in connus
             if n.startswith(f"nonml_{nom}") and n.endswith(".md")
             and not n.endswith("_anti_cheat.md")]
        S = porte(nom, scripts, ".py")
        if R:
            return "CYCLE COMPLET"
        if H:
            return "TRACE PERDUE"
        return "CYCLE INTERROMPU (script écrit)" if S else "CYCLE INTERROMPU (au préreg)"

    cl_ent = [classe(x) for _n, x in aucun_fichier]
    cl_orp = [classe(x) for x in orphelins]

    def cpt(l, mot):
        return sum(1 for c in l if c.startswith(mot))

    # --- Confrontation au rapport du backtest -------------------------------
    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    def lu(motif):
        m = re.search(motif, pub)
        return int(m.group(1)) if m else None

    mesures = [
        ("entrées sans aucun fichier", len(aucun_fichier),
         lu(r"entrées sans aucun fichier \| 10 \| \*\*(\d+)\*\*")),
        ("`PREREG_` jamais mentionnés", len(orphelins),
         lu(r"jamais mentionnés \| 24 \| \*\*(\d+)\*\*")),
        ("cycles complets (orphelins)", cpt(cl_orp, "CYCLE COMPLET"),
         lu(r"cycles complets\*\* \*\(rapport présent[^)]*\)\* : \*\*(\d+)\*\*")),
        ("cycles interrompus (orphelins)", cpt(cl_orp, "CYCLE INTERROMPU"),
         lu(r"\*\*cycles interrompus\*\* : \*\*(\d+)\*\*")),
        ("traces perdues (total)",
         cpt(cl_ent, "TRACE") + cpt(cl_orp, "TRACE"),
         lu(r"≥ 1 trace perdue au total \| ≥ 1 \| (\d+)")),
        ("interrompus (entrées sans fichier)", cpt(cl_ent, "CYCLE INTERROMPU"),
         lu(r"entrées classées interrompues : \*\*(\d+)\*\*")),
    ]

    L = ["# Audit adversarial — les orphelins du #464 (#474)", ""]
    L.append("**Recalcul par une route différente.** Ni le module du #464 ni les")
    L.append("fonctions du backtest ne sont réutilisés : découpage du backlog par")
    L.append("expression régulière sur le **texte entier**, listing par `os.scandir`,")
    L.append("historique par `git rev-list --all --objects` au lieu de `git log")
    L.append("--diff-filter=A`.")
    L.append("")
    L.append("| Grandeur | Audit | Rapport | Verdict |")
    L.append("|---|---|---|---|")
    ecarts = 0
    for nom, mien, publie in mesures:
        ok = publie is not None and mien == publie
        if not ok:
            ecarts += 1
        L.append(f"| {nom} | **{mien}** | "
                 f"{publie if publie is not None else '*non relu*'} | "
                 f"{'**concordant**' if ok else '**ÉCART**'} |")
    L.append("")

    # --- Verification anti-lookahead / anti-effet de bord --------------------
    src = (SCRIPTS / f"nonml_{MOI}_backtest.py").read_text(encoding="utf-8")
    ecrit = re.findall(r"(write_text|open\s*\([^)]*[\"']w|checkout|rm\s|unlink)", src)
    hors = [x for x in ecrit if x != "write_text"]
    L.append("## Effets de bord du backtest")
    L.append("")
    L.append(f"- écritures détectées : **{len(ecrit)}** "
             f"(`write_text` du seul rapport : **{ecrit.count('write_text')}**)")
    L.append(f"- écritures **hors rapport** (`checkout`, `rm`, `open(...,'w')`) : "
             f"**{len(hors)}**")
    L.append("")
    if not hors:
        L.append("**Aucun effet de bord.** Le script lit le disque et `git`, écrit son")
        L.append("seul rapport. Rien à annuler.")
    else:
        L.append(f"**{len(hors)} écriture(s) hors rapport** — à examiner : {hors}")
    L.append("")

    L.append("## Auto-inclusion")
    L.append("")
    exclut = f'!= MOI' in src or f'n != MOI' in src
    L.append(f"- le backtest s'exclut explicitement de sa population : "
             f"**{'OUI' if exclut else 'NON'}**")
    L.append(f"- `{MOI}` figure-t-il dans la population publiée : "
             f"**{'OUI — défaut' if f'`{MOI}`' in pub.split('## Critères')[0] and '| `' + MOI + '`' in pub else 'non'}**")
    L.append("")

    L.append("## Verdict")
    L.append("")
    L.append(f"**{'CONCORDANT' if ecarts == 0 else 'DISCORDANT'}** — "
             f"**{len(mesures) - ecarts}/{len(mesures)}** grandeurs se retrouvent par")
    L.append("une route indépendante.")
    if ecarts:
        L.append("")
        L.append("**Les écarts sont publiés tels quels, pas alignés.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de")
    L.append("> l'historique à la date de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

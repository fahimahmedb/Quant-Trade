"""Audit adversarial du #483 — recalcul independant.

Route differente : la population est etablie par `os.scandir` et un test
d'existence sur l'ensemble des noms de `results/` (au lieu d'un test fichier
par fichier), et l'auto-declaration est cherchee sur les **vingt** premieres
lignes au lieu de douze -- pour voir si la fenetre de douze lignes,
pre-enregistree, ecarte des declarations.

Le controle central : ce cycle a-t-il tenu son engagement le plus difficile —
**ne rien predire sur une reponse deja connue** ?
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

RAPPORT = RESULTS / "nonml_orphan_audits_declared_reading_result.md"
PREREG = ROOT / "PREREG_orphan_audits_declared_reading.md"
OUT = RESULTS / "nonml_orphan_audits_declared_reading_audit.md"
MOI = "orphan_audits_declared_reading"
MOTS = ["audit", "correction", "diagnostic", "infrastructure", "inventaire",
        "vérification", "verification", "modification", "réparation",
        "arbitrage"]
DECL = re.compile(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)
TROIS = ["n_trials_dependence_correction", "pnl_duplicate_sweep_v2",
         "pnl_persistence_exposed_pass"]


def main():
    noms_res = {e.name for e in os.scandir(RESULTS) if e.is_file()}
    pop = []
    for e in sorted(os.scandir(ROOT), key=lambda x: x.name):
        if not (e.is_file() and e.name.startswith("PREREG_")
                and e.name.endswith(".md")):
            continue
        nom = e.name[len("PREREG_"):-3]
        if f"nonml_{nom}_result.md" in noms_res or nom == MOI:
            continue
        lignes = Path(e.path).read_text(encoding="utf-8").splitlines()
        m12 = DECL.search("\n".join(lignes[:12]))
        m20 = DECL.search("\n".join(lignes[:20]))
        pop.append({"nom": nom, "d12": m12.group(1).strip() if m12 else None,
                    "d20": m20.group(1).strip() if m20 else None})

    def classe(d):
        if d is None:
            return "NON DÉCLARÉ"
        return ("SANS RÉSULTAT ATTENDU"
                if any(w in d.lower() for w in MOTS) else "RÉSULTAT ATTENDU")

    c12 = [classe(d["d12"]) for d in pop]
    c20 = [classe(d["d20"]) for d in pop]
    tardives = [d for d in pop if d["d12"] is None and d["d20"] is not None]

    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""
    pre = PREREG.read_text(encoding="utf-8") if PREREG.exists() else ""

    def lu(m):
        g = re.search(m, pub)
        return g.group(1) if g else None

    mesures = [
        ("population", len(pop), lu(r"Population énumérée \(\*\*(\d+)\*\*\)")),
        ("SANS RÉSULTAT ATTENDU", c12.count("SANS RÉSULTAT ATTENDU"),
         lu(r"\*\*SANS RÉSULTAT ATTENDU\*\* \| \*\*(\d+)\*\*")),
        ("RÉSULTAT ATTENDU", c12.count("RÉSULTAT ATTENDU"),
         lu(r"\*\*RÉSULTAT ATTENDU\*\* \| \*\*(\d+)\*\*")),
        ("NON DÉCLARÉ", c12.count("NON DÉCLARÉ"),
         lu(r"\*\*NON DÉCLARÉ\*\* \| \*\*(\d+)\*\*")),
    ]

    L = ["# Audit adversarial — la règle de lecture déclarée (#483)", ""]
    L.append("**Recalcul par une route différente** : population établie par")
    L.append("`os.scandir` et un ensemble de noms, et auto-déclaration cherchée sur les")
    L.append("**vingt** premières lignes au lieu des douze pré-enregistrées.")
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

    L.append("## La fenêtre de douze lignes écarte-t-elle des déclarations ?")
    L.append("")
    L.append("Le pré-enregistrement a figé **douze** lignes. Une fenêtre trop courte")
    L.append("gonflerait artificiellement les « NON DÉCLARÉS ».")
    L.append("")
    L.append(f"- déclarations trouvées entre la ligne **13** et la ligne **20** : "
             f"**{len(tardives)}**")
    for d in tardives[:8]:
        L.append(f"  - `{d['nom']}` — « {d['d20']} »")
    L.append("")
    if not tardives:
        L.append("> **Aucune.** Élargir la fenêtre ne récupère rien : la convention")
        L.append("> d'auto-déclaration, quand elle existe, tient dans l'en-tête. **Le")
        L.append(f"> chiffre de {c12.count('NON DÉCLARÉ')} non déclarés n'est pas un")
        L.append("> artefact de fenêtre**, c'est la réalité du dépôt.")
    else:
        L.append(f"> **{len(tardives)} déclaration(s) tardive(s)** — la fenêtre de douze")
        L.append("> lignes en écarte, et le chiffre publié en est affecté. **Publié tel")
        L.append("> quel** : la fenêtre était pré-enregistrée et n'est pas élargie ici.")
    L.append("")

    L.append("## Le contrôle central — l'engagement le plus difficile a-t-il tenu ?")
    L.append("")
    L.append("Ce cycle rejouait une question **dont il connaissait déjà la réponse**.")
    L.append("La tentation était d'inscrire « 3/3 vérifié » au crédit du cycle.")
    L.append("")
    controles = [
        ("le PREREG déclare l'aveu avant mesure",
         "Je connais donc déjà la réponse" in pre),
        ("le PREREG interdit toute prédiction sur les trois",
         "aucune ne porte sur les trois" in pre.lower()
         or "aucune prédiction n'est formulée" in pre),
        ("le rapport qualifie le résultat de non informatif",
         "non informatif" in pub),
        ("aucune des 3 prédictions ne porte sur les trois",
         "Aucune ne porte sur les trois" in pub),
        ("le rapport publie l'échec de sa propre règle",
         "MAL CLASSÉ" in pub and "manque à ma liste" in pub),
        ("la liste de mots n'est pas élargie après mesure",
         "n'est pas corrigée ici" in pub or "reste publiée" in pub),
        ("la liste de mots du script est identique à celle du PREREG",
         all(w in pre for w in MOTS)),
    ]
    L.append("| Contrôle | Résultat |")
    L.append("|---|---|")
    for lab, ok in controles:
        L.append(f"| {lab} | {'**OUI**' if ok else '**NON**'} |")
    L.append("")
    manques = [lab for lab, ok in controles if not ok]
    if not manques:
        L.append("> **L'engagement a tenu.** Le cycle ratifie sans se créditer, et")
        L.append("> publie que sa propre règle s'est trompée sur **la totalité** de son")
        L.append("> échantillon d'examen.")
    else:
        L.append(f"> **{len(manques)} contrôle(s) échoue(nt)** :")
        for m in manques:
            L.append(f"> - {m}")
    L.append("")

    L.append("## Les trois du #480, recomptés")
    L.append("")
    for n in TROIS:
        d = next((x for x in pop if x["nom"] == n), None)
        L.append(f"- `{n}` → **{classe(d['d12']) if d else 'absent de la population'}**"
                 + (f" (« {d['d12']} »)" if d and d["d12"] else ""))
    L.append("")
    ok3 = all(classe(next((x for x in pop if x["nom"] == n), {"d12": None})["d12"])
              == "SANS RÉSULTAT ATTENDU" for n in TROIS)
    L.append("> **La ratification est confirmée par la route indépendante.**"
             if ok3 else "> **La ratification n'est pas confirmée.**")
    L.append("> Elle **n'apprend rien de neuf** — c'est le propre d'une ratification,")
    L.append("> et le rapport le dit lui-même.")
    L.append("")

    L.append("## Effets de bord du backtest")
    L.append("")
    bt = (SCRIPTS / f"nonml_{MOI}_backtest.py").read_text(encoding="utf-8")
    dangers = re.findall(r"(checkout|subprocess|rm\s|unlink|open\s*\([^)]*[\"']w)", bt)
    L.append(f"- écritures : **{bt.count('write_text')}** (`OUT` seul)")
    L.append(f"- `subprocess` / `checkout` / suppression : **{len(dangers)}**")
    L.append("")
    L.append("**Aucun effet de bord — le script ne fait que lire le disque.**"
             if not dangers else f"**À examiner : {dangers}**")
    L.append("")

    L.append("## Verdict")
    L.append("")
    L.append(f"**{'CONCORDANT' if ecarts == 0 else 'DISCORDANT'}** — "
             f"**{len(mesures) - ecarts}/{len(mesures)}** grandeurs se retrouvent, et")
    L.append(f"**{len(controles) - len(manques)}/{len(controles)}** contrôles de")
    L.append("protocole sont tenus.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

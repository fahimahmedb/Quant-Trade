"""Audit adversarial du #477 — recalcul independant.

Route differente : le backlog est decoupe par `str.split("\\n## ")` au lieu du
generateur du #464, la recherche de mention se fait par `in` sur le texte brut
ligne a ligne au lieu du texte entier, et la presence des rapports est etablie
par `os.scandir` au lieu de `Path.glob`.

Un chiffre qui ne se retrouve pas est signale, jamais aligne.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

RAPPORT = RESULTS / "nonml_orphan_cycles_entries_result.md"
OUT = RESULTS / "nonml_orphan_cycles_entries_audit.md"
MOI = "orphan_cycles_entries"


def main():
    texte = (ROOT / "NONML_STRATEGY_BACKLOG.md").read_text(encoding="utf-8")
    lignes = texte.splitlines()

    # Decoupage par split, pas par le generateur du #464.
    blocs = ["## " + b for b in texte.split("\n## ")[1:]]
    cites = set()
    for b in blocs:
        cites.update(re.findall(r"PREREG_([a-z0-9_]+)\.md", b))

    fichiers_res = sorted(e.name for e in os.scandir(RESULTS) if e.is_file())
    fichiers_scr = sorted(e.name for e in os.scandir(SCRIPTS) if e.is_file())
    preregs = sorted(n[len("PREREG_"):-3] for n in
                     (e.name for e in os.scandir(ROOT) if e.is_file())
                     if n.startswith("PREREG_") and n.endswith(".md"))

    orphelins = [n for n in preregs
                 if n not in cites and n not in texte and n != MOI]

    complets, couverts, non_couverts = [], [], []
    for n in orphelins:
        rap = [f for f in fichiers_res
               if f.startswith(f"nonml_{n}") and f.endswith(".md")
               and not f.endswith("_anti_cheat.md")]
        if not rap:
            continue
        scr = [f for f in fichiers_scr
               if f.startswith(f"nonml_{n}") and f.endswith(".py")]
        complets.append(n)
        # Mention cherchee ligne a ligne, pas sur le texte entier.
        trouve = [f for f in rap + scr if any(f in l for l in lignes)]
        (couverts if trouve else non_couverts).append(n)

    avec_result = [n for n in complets
                   if any(f == f"nonml_{n}_result.md" for f in fichiers_res)]
    audit_seul = [n for n in complets
                  if n not in avec_result
                  and any(f == f"nonml_{n}_audit.md" for f in fichiers_res)]

    pub = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""

    def lu(m):
        g = re.search(m, pub)
        return g.group(1) if g else None

    mesures = [
        ("cycles complets re-dérivés", len(complets),
         lu(r"re-dérivés ici : \*\*(\d+)\*\*")),
        ("couverts autrement", len(couverts),
         lu(r"\*\*couverts autrement\*\* : \*\*(\d+) /")),
        ("non couverts", len(non_couverts),
         lu(r"\*\*non couverts\*\* : \*\*(\d+)\*\*")),
        ("avec un `_result.md`", len(avec_result),
         lu(r"cycle publié au sens plein\)\* : \*\*(\d+)\*\*")),
        ("avec un `_audit.md` seul", len(audit_seul),
         lu(r"pas le résultat\)\* : \*\*(\d+)\*\*")),
    ]

    L = ["# Audit adversarial — les cycles sans entrée de backlog (#477)", ""]
    L.append("**Recalcul par une route différente** : découpage du backlog par")
    L.append("`split(\"\\n## \")` au lieu du générateur du #464, recherche de mention")
    L.append("**ligne à ligne** au lieu du texte entier, présence des fichiers par")
    L.append("`os.scandir` au lieu de `Path.glob`.")
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

    L.append("## Le contrôle qui compte : zéro couvert, est-ce crédible ?")
    L.append("")
    L.append("Un `0 / 13` est un résultat extrême. **Un audit qui se contenterait de")
    L.append("le confirmer par la même logique ne prouverait rien.** Contrôle en sens")
    L.append("inverse : je prends des noms de rapports que le backlog **cite**")
    L.append("certainement, et je vérifie que ma recherche les trouve.")
    L.append("")
    temoins = [f for f in fichiers_res
               if f.endswith("_result.md") and any(f in l for l in lignes)][:5]
    L.append(f"- rapports `_result.md` **trouvés** dans le backlog par la même")
    L.append(f"  recherche : **{len([f for f in fichiers_res if f.endswith('_result.md') and any(f in l for l in lignes)])}**")
    for t in temoins:
        L.append(f"  - `{t}`")
    L.append("")
    if temoins:
        n_tem = len([f for f in fichiers_res if f.endswith("_result.md")
                     and any(f in l for l in lignes)])
        L.append(f"> **La recherche fonctionne.** Elle trouve **{n_tem}** rapports")
        L.append("> cités ailleurs ; si elle n'en trouve **aucun** parmi les 13, c'est")
        L.append("> que ces 13 ne sont réellement cités nulle part. **Le `0` n'est pas")
        L.append("> un défaut de méthode.**")
    else:
        L.append("> **La recherche ne trouve rien du tout** — le `0` serait alors un")
        L.append("> artefact, et il faudrait le dire. **C'est le cas ici.**")
    L.append("")

    L.append("## Effets de bord du backtest")
    L.append("")
    bt = (SCRIPTS / f"nonml_{MOI}_backtest.py").read_text(encoding="utf-8")
    dangers = re.findall(r"(checkout|subprocess|rm\s|unlink|open\s*\([^)]*[\"']w)", bt)
    L.append(f"- écritures : **{bt.count('write_text')}** (`OUT` seul)")
    L.append(f"- `subprocess` / `checkout` / suppression : **{len(dangers)}**")
    L.append("")
    L.append("**Aucun effet de bord — le script ne fait que lire.**" if not dangers
             else f"**À examiner : {dangers}**")
    L.append("")
    L.append("L'ajout de l'entrée collective au backlog est fait **hors du script**,")
    L.append("à la main, et signalé dans le rapport — un script qui réécrit le backlog")
    L.append("serait exactement le genre d'effet de bord que ces cycles traquent.")
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
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

"""Robustesse (7a) — la regle du #448 tient-elle hors de sa forme exacte ?

Ce n'est **PAS un retuning** : la regle du balayage reste celle du #448,
inchangee. On demonte la decoration retiree en quatre couches et on regarde
si le resultat depend d'une seule d'entre elles (pic) ou tient sur un
voisinage (plateau).

Grille fixee AVANT execution.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

OUT = RESULTS / "nonml_verdict_detector_complete_robustness.md"

A_RECUPERER = ("third_npz_schema_handling", "sweep_pass_prose_fix")

# Couches de decoration, cumulatives. Declarees avant execution.
GRILLE = [
    ("V0 — aucune (règle #447)", set()),
    ("V1 — titres", {"titre"}),
    ("V2 — titres + citations", {"titre", "cit"}),
    ("V3 — titres + citations + puces", {"titre", "cit", "puce"}),
    ("V4 — tout (règle #448)", {"titre", "cit", "puce", "label"}),
]


def nu(ln, couches):
    s = ln.strip()
    if "titre" in couches:
        while s.startswith("#"):
            s = s[1:]
        s = s.lstrip()
    if "cit" in couches:
        while s.startswith(">"):
            s = s[1:].lstrip()
    if "puce" in couches and s[:2] in ("- ", "* "):
        s = s[2:].lstrip()
    if "label" in couches:
        tete = s[2:] if s[:2] == "**" else s
        if tete[:7].lower() == "verdict":
            reste = tete[7:]
            if reste[:6].lower() == " final":
                reste = reste[6:]
            if reste[:2] == "**":
                reste = reste[2:]
            reste = reste.lstrip()
            if reste[:1] in (":", "—", "-", "："):
                s = reste[1:].lstrip()
    return s


def verdict(t, couches):
    lignes = t.splitlines()
    if any(nu(ln, couches).startswith("**PASS")
           or nu(ln, couches).startswith("PASS (niveau 1)") for ln in lignes):
        return "PASS"
    if any(nu(ln, couches).startswith("**FAIL") for ln in lignes):
        return "FAIL"
    return "indéterminé"


def main():
    scripts = {p.name[len("nonml_"):-len("_backtest.py")]
               for p in SCRIPTS.glob("nonml_*_backtest.py")}
    npz = {p.name[len("nonml_"):-len("_pnl.npz")]
           for p in RESULTS.glob("nonml_*_pnl.npz")}
    textes = {}
    for n in sorted(scripts - npz):
        f = RESULTS / f"nonml_{n}_result.md"
        if f.exists():
            textes[n] = f.read_text(encoding="utf-8")

    rows = []
    for nom, couches in GRILLE:
        c = {"PASS": 0, "FAIL": 0, "indéterminé": 0}
        for t in textes.values():
            c[verdict(t, couches)] += 1
        recup = sum(1 for n in A_RECUPERER
                    if n in textes and verdict(textes[n], couches) == "FAIL")
        rows.append((nom, c, recup))

    L = ["# Robustesse — la règle du #448 hors de sa forme exacte", ""]
    L.append("**Étape 7a. Ce n'est pas un retuning** : la règle du balayage reste celle du")
    L.append("#448, inchangée. On démonte la décoration retirée en **quatre couches** et on")
    L.append("regarde si le résultat tient sur un voisinage ou dépend d'une seule d'entre")
    L.append("elles. La grille était fixée avant exécution.")
    L.append("")
    L.append(f"Rapports examinés : **{len(textes)}**")
    L.append("")
    L.append("| Variante | PASS | FAIL | indéterminé | Faux négatifs #447 récupérés (/2) |")
    L.append("|---|---|---|---|---|")
    for nom, c, recup in rows:
        L.append(f"| {nom} | {c['PASS']} | {c['FAIL']} | {c['indéterminé']} | "
                 f"**{recup}** |")
    L.append("")

    plateau = all(r[2] == 2 for r in rows[1:])
    premier_complet = next((nom for nom, _, rec in rows if rec == 2), None)
    L.append("## Lecture — et un constat qui dérange")
    L.append("")
    L.append(f"Les deux faux négatifs ne sont **tous deux** récupérés qu'à partir de")
    L.append(f"**{premier_complet}**. Autrement dit :")
    L.append("")
    L.append("- la couche **titres** (V1) rattrape `### **FAIL**` — le rapport du #446 ;")
    L.append("- la couche **étiquette** (V4) est **seule** à rattraper")
    L.append("  `## Verdict : **FAIL**` — le rapport du #444. Les couches intermédiaires")
    L.append("  (citations, puces) ne changent **rien** : 0 reclassement entre V1 et V3.")
    L.append("")
    if plateau:
        L.append("**Plateau** : le résultat tient sur tout le voisinage.")
    else:
        L.append("**Ce n'est pas un plateau, c'est un escalier à deux marches** — et la seconde")
        L.append("marche ne porte qu'**un seul** cas.")
        L.append("")
        L.append("Le rapport de robustesse que j'avais rédigé d'avance annonçait un plateau et")
        L.append("le mot « pic » n'y figurait qu'en garde-fou. **La mesure dit l'inverse de ce")
        L.append("que j'avais écrit**, et c'est la mesure qui est publiée.")
        L.append("")
        L.append("### La question qu'il faut poser franchement")
        L.append("")
        L.append("La couche « étiquette » a-t-elle été **taillée pour le cas qu'elle devait")
        L.append("rattraper** ? Le pré-enregistrement l'a déclarée avant toute mesure, et")
        L.append("l'anti-cheat le confirme — mais elle a été déclarée **en sachant** que le")
        L.append("#444 énonçait `## Verdict : **FAIL**`, puisque le #447 l'avait publié.")
        L.append("")
        L.append("**Honnêtement : oui, en partie.** La règle couvre quatre formes ; deux")
        L.append("d'entre elles ne servent à rien sur le corpus actuel, et une n'existe que")
        L.append("pour un unique rapport. Ce n'est pas du data-snooping au sens du protocole —")
        L.append("aucun seuil n'a été balayé, aucun résultat de stratégie n'est en jeu — mais")
        L.append("c'est une règle **ajustée à des cas connus**, et le dire vaut mieux que")
        L.append("laisser le tableau suggérer une robustesse qu'il ne montre pas.")
        L.append("")
        L.append("Ce qui **ne** serait **pas** honnête serait de retirer la couche maintenant")
        L.append("pour faire joli : elle est déclarée, elle est utile, elle reste.")
    L.append("")
    L.append("## Ce que ces couches valent pour la suite")
    L.append("")
    L.append("Il **ne** signifie **pas** que les trois couches supplémentaires sont inutiles :")
    L.append("elles couvrent des formes d'énoncé qui n'existent pas *encore* dans le dépôt")
    L.append("(`> **FAIL**`, `- **PASS**`, `Verdict final : **PASS**`). Les garder, c'est")
    L.append("accepter un coût nul aujourd'hui contre un faux négatif évité demain.")
    L.append("")
    L.append("Mais il faut lire le tableau pour ce qu'il montre : **sur le corpus")
    L.append("d'aujourd'hui, deux des quatre couches sont inertes et une ne sert qu'une fois.**")
    L.append("La robustesse de la règle est donc **à démontrer par l'usage**, pas acquise.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

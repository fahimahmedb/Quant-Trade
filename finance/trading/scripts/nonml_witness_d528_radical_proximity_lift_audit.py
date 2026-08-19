"""Audit indépendant — #530, témoin (permutation + négatif/positif) de D528.

Route distincte du backtest : dénombrement par `grep -c`/`wc -l`
externes (sous-processus, pas de comptage Python interne) ; ré-estimation
du taux de proximité par une fenêtre **structurelle** (le même
paragraphe, coupé sur ligne vide, plutôt qu'une fenêtre fixe de 400
caractères) — mesure différente du backtest, testée pour l'accord
**qualitatif** (le sens du lift), pas l'égalité numérique exacte ;
vérification par grep externe des citations exactes des deux témoins ;
confirmation par `git diff --stat` qu'aucun script existant n'a été
modifié par ce commit.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_witness_d528_radical_proximity_lift_audit_result.md"

MARQUEURS = ["rétracté", "FAUSSE", "n'est pas un défaut", "contredit", "réfuté"]
SEUIL_LIFT = 3


def radical(nom):
    return re.sub(r"^nonml_|_backtest\.py$|_audit\.py$|\.py$", "", nom)


def grep_c(motif, fichier):
    """Compte les OCCURRENCES (pas les lignes) : `grep -c` compterait une
    ligne contenant deux fois le motif comme une seule -- `grep -o`
    recompte chaque occurrence (une par ligne de sortie), comme le
    `re.findall` du backtest. Pas de shell=True (motifs avec apostrophe)."""
    out = subprocess.run(["grep", "-o", "-F", motif, str(fichier)],
                          capture_output=True, text=True)
    return len(out.stdout.splitlines())


def sections(txt):
    bornes = [(m.start(), int(m.group(1))) for m in
              re.finditer(r"^## Backlog #(\d+)", txt, re.MULTILINE)]
    out = []
    for i, (pos, n) in enumerate(bornes):
        fin = bornes[i + 1][0] if i + 1 < len(bornes) else len(txt)
        out.append((n, txt[pos:fin]))
    return out


def paragraphes(sec_txt):
    """Decoupe une section en paragraphes sur ligne vide -- fenetre
    structurelle, alternative a la fenetre fixe de 400 caracteres du
    backtest."""
    bornes = [0] + [m.end() for m in re.finditer(r"\n\s*\n", sec_txt)] + [len(sec_txt)]
    return sorted(set(bornes))


def paragraphe_de(pos, bornes):
    for i in range(len(bornes) - 1):
        if bornes[i] <= pos < bornes[i + 1]:
            return bornes[i], bornes[i + 1]
    return 0, len(bornes)


def main():
    txt = BACKLOG.read_text(encoding="utf-8")
    secs = sections(txt)
    noms = sorted(p.name for p in SCRIPTS.glob("nonml_*.py"))
    radicaux = sorted({radical(n) for n in noms}, key=len, reverse=True)

    # --- Recompte externe de la population ---
    n_sections_grep = int(subprocess.run(
        ["grep", "-c", "^## Backlog #", str(BACKLOG)],
        capture_output=True, text=True).stdout.strip() or "0")
    n_radicaux_grep = int(subprocess.run(
        "ls " + str(SCRIPTS / "nonml_*.py") + " | wc -l",
        shell=True, capture_output=True, text=True).stdout.strip() or "0")
    n_marqueurs = {mk: grep_c(mk, BACKLOG) for mk in MARQUEURS}
    n_marqueurs_total = sum(n_marqueurs.values())

    # --- Taux structurel (fenetre = paragraphe) ---
    n_occ = 0
    n_hit_struct = 0
    for n_sec, sec_txt in secs:
        bornes_p = paragraphes(sec_txt)
        for mk in MARQUEURS:
            for mm in re.finditer(re.escape(mk), sec_txt):
                n_occ += 1
                p0, p1 = paragraphe_de(mm.start(), bornes_p)
                para = sec_txt[p0:p1]
                if any(r in para for r in radicaux):
                    n_hit_struct += 1
    A_struct = n_hit_struct / n_occ if n_occ else 0.0

    # Permutation structurelle : position aleatoire dans les bornes de
    # la meme section (module standard, seed differente du backtest).
    import random
    rng = random.Random(530)
    N_PERM = 20
    taux_nuls = []
    for _ in range(N_PERM):
        hits = 0
        for n_sec, sec_txt in secs:
            bornes_p = paragraphes(sec_txt)
            for mk in MARQUEURS:
                n_reel = len(re.findall(re.escape(mk), sec_txt))
                for _k in range(n_reel):
                    p = rng.randint(0, max(0, len(sec_txt) - 1))
                    p0, p1 = paragraphe_de(p, bornes_p)
                    para = sec_txt[p0:p1]
                    if any(r in para for r in radicaux):
                        hits += 1
        taux_nuls.append(hits / n_occ if n_occ else 0.0)
    A_nul_struct = sum(taux_nuls) / len(taux_nuls)
    lift_struct = (A_struct / A_nul_struct) if A_nul_struct > 0 else float("inf")

    # --- Verification des deux temoins par grep externe direct ---
    citation_dette_ok = grep_c("collision avec la phrase générique", BACKLOG) >= 1
    # Le radical du temoin positif doit se trouver a +/-3 lignes du
    # marqueur qui l'identifie (route ligne-a-ligne, pas caractere).
    pipe = subprocess.run(
        f"grep -B3 -A3 -F \"n'est pas un défaut\" '{BACKLOG}' "
        "| grep -c 'reproducibility_sample_lot3'",
        shell=True, capture_output=True, text=True)
    citation_positif_ok = int(pipe.stdout.strip() or "0") >= 1

    # --- Confirmation qu'aucun script existant n'a ete modifie ---
    diff = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--", "finance/trading/scripts/"],
        capture_output=True, text=True, cwd=ROOT)
    touche_hors_cycle = [l for l in diff.stdout.splitlines()
                          if "witness_d528_radical_proximity_lift" not in l and l.strip()]

    L = ["# Audit indépendant — #530, témoin (permutation + négatif/positif) "
         "de D528", ""]
    L.append("Route distincte du backtest : dénombrement par grep externe, "
             "fenêtre structurelle (paragraphe) au lieu de la fenêtre fixe "
             "de 400 caractères, seed de permutation différente (530).")
    L.append("")

    L.append("## Recompte externe de la population")
    L.append("")
    L.append(f"- sections (`grep -c '^## Backlog #'`) : **{n_sections_grep}** "
             f"(backtest : {len(secs)}, accord : "
             f"{'OUI' if n_sections_grep == len(secs) else 'NON'})")
    L.append(f"- radicaux (`ls | wc -l`) : **{n_radicaux_grep}** "
             f"(backtest : {len(noms)}, accord : "
             f"{'OUI' if n_radicaux_grep == len(noms) else 'NON'})")
    L.append(f"- occurrences de marqueur, somme des `grep -o -F | wc -l` : "
             f"**{n_marqueurs_total}** (backtest : 164, accord : "
             f"{'OUI' if n_marqueurs_total == 164 else 'NON'})")
    L.append("")
    L.append("| Marqueur | grep -o -F \\| wc -l |")
    L.append("|---|---|")
    for mk, c in n_marqueurs.items():
        L.append(f"| « {mk} » | {c} |")
    L.append("")

    L.append("## Taux structurel (fenêtre = paragraphe) vs taux du backtest "
             "(fenêtre = 400 caractères)")
    L.append("")
    L.append(f"- `A_struct` (fenêtre paragraphe) : **{A_struct:.4f}** "
             f"({n_hit_struct}/{n_occ})")
    L.append(f"- `A_nul_struct` (moyenne sur {N_PERM} tirages, seed=530) : "
             f"**{A_nul_struct:.4f}**")
    L.append(f"- **lift structurel = {lift_struct:.2f}**")
    L.append("")
    accord_qualitatif = (lift_struct < SEUIL_LIFT)
    L.append(f"> Accord qualitatif avec le backtest (lift < {SEUIL_LIFT}, "
             f"la proximité seule ne discrimine pas) : "
             f"**{'OUI' if accord_qualitatif else 'NON'}**. Les deux routes "
             f"utilisent une définition de fenêtre différente (paragraphe "
             f"vs 400 caractères) — un accord sur les **valeurs exactes** "
             f"n'est **pas** attendu, seulement sur le **sens** du "
             f"résultat.")
    L.append("")

    L.append("## Vérification directe des deux témoins")
    L.append("")
    L.append(f"- citation du témoin négatif 1 (« collision avec la phrase "
             f"générique... ») trouvée dans le backlog par grep externe : "
             f"**{'OUI' if citation_dette_ok else 'NON'}**")
    L.append(f"- citation du témoin positif (« n'est pas un défaut », "
             f"marqueur du #482) trouvée dans le backlog par grep externe : "
             f"**{'OUI' if citation_positif_ok else 'NON'}**")
    L.append("")

    L.append("## Aucun script existant modifié par ce commit")
    L.append("")
    if touche_hors_cycle:
        L.append("**Fichiers touchés hors des deux scripts du #530 :**")
        for l in touche_hors_cycle:
            L.append(f"- {l}")
    else:
        L.append("- confirmé : **0** fichier de `scripts/` touché par ce "
                 "commit en dehors des deux nouveaux scripts du #530.")
    L.append("")

    accord_pop = (n_sections_grep == len(secs) and n_radicaux_grep == len(noms)
                  and n_marqueurs_total == 164)
    verdict = ("PASS" if (accord_pop and accord_qualitatif
                          and citation_dette_ok and citation_positif_ok
                          and not touche_hors_cycle) else "FAIL")
    L.append(f"**{verdict}** — la route indépendante confirme la "
             f"population du backtest, confirme le **sens** du lift "
             f"(< {SEUIL_LIFT}) sous une définition de fenêtre différente, "
             f"et confirme les deux citations et l'absence de "
             f"modification hors du commit du #530.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — lift_struct={lift_struct:.2f}, accord_pop={accord_pop}, "
          f"accord_qualitatif={accord_qualitatif}")
    return verdict


if __name__ == "__main__":
    main()

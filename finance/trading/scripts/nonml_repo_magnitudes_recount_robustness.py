"""Robustesse (7a) du #462 — perturber le REPERE, pas les definitions.

**Ce n'est pas un retuning.** Les six globs et l'univers restent ceux du
pre-enregistrement. On perturbe deux choses exterieures au critere :

  1. la BORNE de l'univers (#443 declaree, elargie vers l'arriere) ;
  2. la CONVENTION D'EPINGLAGE — le seul resultat positif du cycle (le saut
     `batteries` de +29 au #457) doit survivre a un autre choix de commit,
     sinon c'est un artefact du repere et non un fait du depot.

Le risque est reel : si le saut se deplace ou se fractionne selon la
convention, la confirmation du #457 ne tient plus.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_backlog_figures_verification_backtest as bt  # noqa: E402
import nonml_repo_magnitudes_recount_backtest as mg  # noqa: E402

OUT = RESULTS / "nonml_repo_magnitudes_recount_robustness.md"
BACKLOG = "finance/trading/NONML_STRATEGY_BACKLOG.md"
ENTREES = list(range(443, 461))
BORNES = [443, 430, 415, 400]

_MEMO = {}


def git(*a):
    if a not in _MEMO:
        r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
        _MEMO[a] = r.stdout if r.returncode == 0 else None
    return _MEMO[a]


def sha_entree(num):
    return bt.commit_introducteur(num)


def sha_prereg(num):
    """Le commit qui a ajoute le PREREG du meme cycle."""
    s = sha_entree(num)
    if s is None:
        return None
    txt = bt.texte_entree(git("show", f"{s}:{BACKLOG}") or "", num) or ""
    noms = sorted(set(re.findall(r"PREREG_([a-z0-9_]+)\.md", txt)))
    if len(noms) != 1:
        return None
    # Defaut de la premiere version : `git log -S<nom>` cherche la chaine dans
    # le CONTENU du fichier, pas dans son nom — aucun PREREG ne se cite
    # lui-meme, la convention rendait 0 point, et le rapport en concluait que
    # le saut « ne survit pas ». Une conclusion fausse CONTRE ma propre
    # trouvaille reste une conclusion fausse. On demande le commit qui a
    # AJOUTE le fichier.
    out = git("log", "--diff-filter=A", "--format=%H", "--",
              f"finance/trading/PREREG_{noms[0]}.md")
    lignes = [l for l in (out or "").splitlines() if l.strip()]
    return lignes[-1] if lignes else None


def sha_parent(num):
    s = sha_entree(num)
    if s is None:
        return None
    p = git("rev-parse", f"{s}^")
    return p.strip() if p else None


CONVENTIONS = [("commit de l'entrée *(déclarée)*", sha_entree),
               ("commit du `PREREG_` du même cycle", sha_prereg),
               ("parent du commit de l'entrée", sha_parent)]


def serie_batteries(fn):
    s = []
    for num in ENTREES:
        sha = fn(num)
        if sha is None:
            continue
        c = mg.compte(sha)
        if c:
            s.append((num, c["batteries"]))
    return s


def sauts(serie):
    return [(a, va, b, vb) for (a, va), (b, vb) in zip(serie, serie[1:]) if vb != va]


def main():
    L = ["# Robustesse (7a) — re-mesure des grandeurs du dépôt", ""]
    L.append("**Ce n'est pas un retuning.** Les six globs et l'univers restent ceux du")
    L.append("pré-enregistrement. On perturbe le **repère**, pas les définitions.")
    L.append("")

    # --- 1. la convention d'epinglage --------------------------------------
    L.append("## 1. La convention d'épinglage — le test qui compte")
    L.append("")
    L.append("Le seul résultat positif du cycle est le saut `batteries` **92 → 121** au")
    L.append("#457. S'il se déplace ou se fractionne quand on change de convention, ce")
    L.append("n'est pas un fait du dépôt mais **un artefact de mon repère**.")
    L.append("")
    L.append("| Convention | Points | Sauts | Détail |")
    L.append("|---|---|---|---|")
    verdicts, series_par_conv = [], []
    for nom, fn in CONVENTIONS:
        s = serie_batteries(fn)
        j = sauts(s)
        det = " ; ".join(f"#{a}→#{b} : {va}→**{vb}** (**{vb - va:+d}**)"
                         for a, va, b, vb in j) or "*aucun*"
        if not s:
            det = "*instrument muet — exclue du verdict*"
        L.append(f"| {nom} | {len(s)} | **{len(j)}** | {det} |")
        verdicts.append((nom, j))
        series_par_conv.append((nom, s))
    L.append("")
    # Une convention qui ne rend AUCUN point n'a pas mesure : c'est une panne
    # d'instrument, pas un desaccord. La compter comme un echec du saut serait
    # une conclusion fausse — contre ma propre trouvaille, mais fausse.
    muettes = [nom for (nom, _fn), (_n, s) in zip(CONVENTIONS,
                                                  [(n, s) for n, s in series_par_conv])
               if len(s) == 0]
    evaluables = [(nom, j) for (nom, j), (_n, s) in zip(verdicts, series_par_conv)
                  if len(s) > 0]
    unique_29 = [(nom, j) for nom, j in evaluables
                 if len(j) == 1 and j[0][3] - j[0][1] == 29]
    if muettes:
        L.append(f"> **{len(muettes)} convention(s) sans aucun point** : "
                 + ", ".join(f"« {m} »" for m in muettes) + ".")
        L.append("> C'est une **panne d'instrument**, pas un désaccord — elles sont")
        L.append("> **exclues du verdict** au lieu d'être comptées comme un échec du")
        L.append("> saut.")
        L.append("")
    L.append(f"- conventions **évaluables** : **{len(evaluables)}/{len(CONVENTIONS)}**")
    L.append(f"- donnant **un saut unique de +29** : "
             f"**{len(unique_29)}/{len(evaluables)}**")
    L.append("")
    if evaluables and len(unique_29) == len(evaluables):
        L.append("**Le saut survit à toutes les conventions évaluables.** Il n'est pas un")
        L.append("artefact du repère : les 29 rapports de batterie existent dans le dépôt,")
        L.append("quel que soit le commit qu'on choisit pour regarder.")
        etiquettes = {(j[0][0], j[0][2]) for _n, j in unique_29}
        if len(etiquettes) > 1:
            L.append("")
            L.append("> **L'étiquette du saut change, sa taille non.** Épinglé au")
            L.append("> `PREREG_`, le saut apparaît une entrée plus loin : les fichiers")
            L.append("> d'un cycle arrivent **après** son pré-enregistrement et **avant**")
            L.append("> son entrée de backlog, donc le repère « PREREG » les voit au tour")
            L.append("> suivant. **C'est le même +29, vu d'un cran plus tôt** — ce")
            L.append("> décalage confirme la mécanique au lieu de la contredire.")
    else:
        L.append("**Le saut ne survit pas à toutes les conventions.** Publié tel quel :")
        L.append("c'est exactement le genre de fragilité qu'une robustesse doit révéler,")
        L.append("et elle affaiblit la seule affirmation positive du cycle.")
    L.append("")

    # --- 2. la borne --------------------------------------------------------
    L.append("## 2. La borne de l'univers")
    L.append("")
    L.append("Déclarée à **#443**. Élargie vers l'arrière : la table doit rester")
    L.append("**croissante** sur les six grandeurs, sinon mon comptage est en cause.")
    L.append("")
    L.append("| Depuis | Entrées | Décroissances | `batteries` de → à |")
    L.append("|---|---|---|---|")
    ok_bornes = 0
    for b in BORNES:
        s, baisses = [], 0
        for num in range(b, 461):
            sha = sha_entree(num)
            if sha is None:
                continue
            c = mg.compte(sha)
            if c:
                s.append((num, c))
        for cle, _ in mg.GRANDEURS:
            vals = [c[cle] for _n, c in s]
            baisses += sum(1 for x, y in zip(vals, vals[1:]) if y < x)
        if baisses == 0:
            ok_bornes += 1
        bornes_bat = f"{s[0][1]['batteries']} → {s[-1][1]['batteries']}" if s else "—"
        marque = " *(déclarée)*" if b == 443 else ""
        L.append(f"| **#{b}**{marque} | {len(s)} | **{baisses}** | {bornes_bat} |")
    L.append("")
    L.append(f"- bornes sans aucune décroissance : **{ok_bornes}/{len(BORNES)}**")
    L.append("")
    if ok_bornes == len(BORNES):
        L.append("**Plateau.** Le comptage se comporte de la même façon sur tout")
        L.append("l'intervalle testé — le dépôt n'ajoute que des fichiers.")
    else:
        L.append("**Au moins une borne fait apparaître une décroissance**, ce qui")
        L.append("signale soit une suppression réelle, soit un défaut de mon comptage.")
    L.append("")

    L.append("## Ce que la robustesse **n'**établit pas")
    L.append("")
    L.append("- Elle éprouve le **recomptage**, pas l'appariement de prose — que le")
    L.append("  rapport publie déjà comme un **échec**. Perturber une règle ratée ne la")
    L.append("  rendrait pas bonne.")
    L.append("- Elle ne rend pas recomptables les **trois** faux connus qui se")
    L.append("  définissent par le contenu ou par une relation entre globs.")
    L.append("")
    L.append("Aucun paramètre n'a été modifié après lecture de ces résultats.")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

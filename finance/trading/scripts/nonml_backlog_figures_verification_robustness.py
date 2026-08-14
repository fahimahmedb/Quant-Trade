"""Robustesse (7a) du #461 — perturbation de l'univers et des lectures.

**Ce n'est pas un retuning.** La regle d'extraction, les exclusions et le
critere restent CEUX DU PRE-ENREGISTREMENT. On perturbe deux choses qui ne sont
pas au coeur du critere :

  1. la BORNE de l'univers — declaree a #443, elargie vers l'arriere ;
  2. les LECTURES d'explication — en retirant celle des fichiers freres, puis
     celle des sections de citation, pour voir de combien le residu depend
     d'ajouts que j'ai faits apres avoir vu le resultat.

Le risque est reel et assume : un residu qui explose sur les entrees anterieures
refuterait la conclusion « aucune erreur de chiffre ».
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import nonml_backlog_figures_verification_backtest as bt  # noqa: E402

OUT = RESULTS / "nonml_backlog_figures_verification_robustness.md"

BORNES = [443, 430, 415, 400]            # #443 = borne pre-enregistree
LECTURES = [("déclarée + freres + citation", True, True),
            ("sans les fichiers frères", False, True),
            ("sans les sections de citation", True, False),
            ("règle stricte seule", False, False)]


# `git log -S` fait une recherche pickaxe sur TOUTE l'histoire du backlog :
# la refaire pour chaque cellule de la grille, c'est 480 recherches la ou 60
# suffisent. Memoisation pure — aucun effet sur les chiffres.
_MEMO_SHA, _MEMO_BLOB = {}, {}


def sha_de(num):
    if num not in _MEMO_SHA:
        _MEMO_SHA[num] = bt.commit_introducteur(num)
    return _MEMO_SHA[num]


def blob_de(ref):
    if ref not in _MEMO_BLOB:
        _MEMO_BLOB[ref] = bt.git("show", ref)
    return _MEMO_BLOB[ref]


def mesure(debut, freres_on, citation_on):
    n_tok = n_typo = n_fre = n_cit = n_dur = 0
    entrees = 0
    for num in range(debut, 461):
        sha = sha_de(num)
        if sha is None:
            continue
        blob = blob_de(f"{sha}:{bt.BACKLOG}")
        if blob is None:
            continue
        txt = bt.texte_entree(blob, num)
        if txt is None:
            continue
        noms = sorted(set(bt.re.findall(r"PREREG_([a-z0-9_]+)\.md", txt)))
        if len(noms) != 1:
            continue
        nom = noms[0]
        rap = blob_de(f"{sha}:finance/trading/results/nonml_{nom}_result.md")
        if rap is None:
            continue
        entrees += 1
        rap_n = bt.normalise(rap)
        freres = {}
        if freres_on:
            for suff in ("audit", "robustness"):
                f = blob_de(f"{sha}:finance/trading/results/nonml_{nom}_{suff}.md")
                if f is not None:
                    freres[suff] = bt.normalise(f)
        for seg, _sec, cite in bt.segments_gras(txt):
            for j in bt.jetons_du_segment(seg):
                n_tok += 1
                if j in rap_n:
                    continue
                if any(v in rap_n for v in bt.variantes_typographiques(j)):
                    n_typo += 1
                    continue
                if any(j in c or any(v in c for v in bt.variantes_typographiques(j))
                       for c in freres.values()):
                    n_fre += 1
                    continue
                if citation_on and cite:
                    n_cit += 1
                    continue
                n_dur += 1
    return entrees, n_tok, n_typo, n_fre, n_cit, n_dur


def main():
    L = ["# Robustesse (7a) — vérification des chiffres du backlog", ""]
    L.append("**Ce n'est pas un retuning.** La règle d'extraction, les exclusions et le")
    L.append("critère restent ceux du pré-enregistrement. On perturbe la **borne** de")
    L.append("l'univers et les **lectures d'explication**.")
    L.append("")

    L.append("## 1. La borne de l'univers")
    L.append("")
    L.append("Déclarée à **#443**. Élargie vers l'arrière, sur des entrées que le")
    L.append("pré-enregistrement ne couvrait pas — **avec le risque réel que la")
    L.append("conclusion n'y survive pas.**")
    L.append("")
    L.append("| Depuis | Entrées | Jetons | Typo | Frères | Citation | **Résidu** | Résidu / jeton |")
    L.append("|---|---|---|---|---|---|---|---|")
    taux = []
    for b in BORNES:
        e, t, ty, fr, ci, du = mesure(b, True, True)
        tx = 100 * du / max(t, 1)
        taux.append(tx)
        part = f"{tx:.2f} %".replace(".", ",")
        marque = " *(pré-enregistrée)*" if b == 443 else ""
        L.append(f"| **#{b}**{marque} | {e} | {t} | {ty} | {fr} | {ci} | **{du}** | {part} |")
    L.append("")
    etendue = max(taux) - min(taux)
    plateau = etendue <= 2.0          # seuil de lecture, fixe ici avant mesure
    L.append(f"Taux de résidu : de **{min(taux):.2f} %** à **{max(taux):.2f} %**, "
             f"étendue **{etendue:.2f} point(s)**.".replace(".", ","))
    L.append("")
    if plateau:
        L.append("C'est un **plateau** : la conclusion ne tient pas au choix de la borne.")
    else:
        L.append("**Ce n'est pas un plateau.** Le taux de résidu **dépend de la borne**,")
        L.append("donc la fenêtre pré-enregistrée n'est pas représentative des entrées")
        L.append("antérieures. **Rapporté tel quel** — c'est le genre de résultat qu'un")
        L.append("cycle de vérification doit publier contre lui-même.")
    L.append("")
    L.append("> **Réserve, dite tout de suite :** les résidus des entrées antérieures à")
    L.append("> #443 **n'ont pas été vérifiés à la main**, contrairement aux quatre de")
    L.append("> l'univers déclaré. Ce tableau montre que leur *nombre* ne dérape pas ; il")
    L.append("> ne dit **pas** qu'aucun n'est une erreur.")
    L.append("")

    L.append("## 2. Les lectures d'explication")
    L.append("")
    L.append("Deux des quatre classifications ont été ajoutées **après** avoir vu le")
    L.append("résultat. Il faut donc montrer **de combien** le résidu en dépend, sur")
    L.append("l'univers pré-enregistré.")
    L.append("")
    L.append("| Lecture | Jetons | **Résidu** |")
    L.append("|---|---|---|")
    res = {}
    for nom, fo, co in LECTURES:
        _e, t, _ty, _fr, _ci, du = mesure(443, fo, co)
        res[nom] = du
        L.append(f"| {nom} | {t} | **{du}** |")
    L.append("")
    base = res["déclarée + freres + citation"]
    strict = res["règle stricte seule"]
    L.append(f"Le résidu passe de **{base}** (toutes lectures) à **{strict}** (règle")
    L.append(f"stricte seule), soit **×{strict/max(base,1):.0f}**.".replace(".0**", "**"))
    L.append("")
    L.append("**C'est le chiffre le plus inconfortable de ce cycle, et il est publié.**")
    L.append("")
    L.append("Ce que cela veut dire — et ne veut pas dire : les jetons que ces lectures")
    L.append("expliquent **ont bien été retrouvés**, dans un fichier frère du même cycle")
    L.append("ou dans une section qui cite un autre cycle. Ce ne sont pas des erreurs.")
    L.append("Mais **c'est moi qui ai décidé, après coup, que ces endroits comptaient** —")
    L.append("et un lecteur en droit d'être méfiant doit voir les deux colonnes.")
    L.append("")

    L.append("## Ce que la robustesse établit")
    L.append("")
    L.append(f"- **Borne de l'univers** : {'plateau' if plateau else '**pas** un plateau'}")
    L.append(f"  (étendue {etendue:.2f} point(s) de taux de résidu).".replace(".", ","))
    L.append(f"- **Lectures d'explication** : le résidu passe de **{base}** à")
    L.append(f"  **{strict}** quand on les retire — la conclusion **dépend** de")
    L.append("  classifications posées après mesure. Publié, pas masqué.")
    L.append("")
    L.append("Aucun paramètre n'a été modifié après lecture de ces résultats.")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

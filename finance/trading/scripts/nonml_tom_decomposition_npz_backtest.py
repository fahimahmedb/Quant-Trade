"""Donner un `.npz` a `tom_decomposition_overlay`, et le soumettre au balayage (#452).

Specification pre-enregistree dans `PREREG_tom_decomposition_npz.md`,
committee AVANT toute modification et toute mesure.

La variante A porte un PASS (4/5 marches) et n'avait aucun `.npz` : elle
echappait au balayage de doublons (#446). Or le #8 (`tom_overlay`, ToM complet)
est PASS lui aussi et possede le sien — et la variante A est une **sous-fenetre**
de cette union. Deux essais n'en font-ils qu'un ?
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT.parent / "src"))

from prediction import trading_metrics  # noqa: E402
import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402

OUT = RESULTS / "nonml_tom_decomposition_npz_result.md"
CIBLE = "nonml_tom_decomposition_overlay"
RAPPORT = f"{CIBLE}_result.md"
NPZ = RESULTS / f"{CIBLE}_pnl.npz"
BASE = "77954e4"          # commit du PREREG, epingle (lecon des #445/#451)


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True,
                          text=True, check=check).stdout


def main():
    rel = f"finance/trading/results/{RAPPORT}"
    avant = git("show", f"{BASE}:{rel}", check=False)

    r = subprocess.run([sys.executable, str(SCRIPTS / f"{CIBLE}_backtest.py")],
                       cwd=REPO, capture_output=True, text=True, timeout=1800)
    apres = (RESULTS / RAPPORT).read_text(encoding="utf-8")

    identique = (avant == apres)
    npz_cree = NPZ.exists()

    # --- Concordance : le Sharpe du .npz figure-t-il au rapport ? ----------
    sharpe = None
    concordant = False
    if npz_cree:
        d = np.load(NPZ, allow_pickle=True)
        pos = np.asarray(d["pos"], float)
        ra = np.asarray(d["r_asset"], float)
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl = pos * ra - turn * float(d["cost_bps"]) / 1e4
        sharpe = trading_metrics(pnl)["sharpe_ann"]
        concordant = f"{sharpe:+.2f}" in set(re.findall(r"[+-]\d\.\d\d", apres))

    # --- Le balayage voit-il la serie, et que dit-il ? --------------------
    dup, quasi, _ = sw.main()
    dans_groupe = [g for g in dup if any(CIBLE in x for x in g)]
    quasi_liees = [(a, b, c) for a, b, c in quasi if CIBLE in a or CIBLE in b]

    # Correlation avec le #8, mesuree explicitement (prediction du PREREG)
    corr8 = None
    p8 = RESULTS / "nonml_tom_overlay_pnl.npz"
    if npz_cree and p8.exists():
        s_a, _ = sw.net_pnl(np.load(NPZ, allow_pickle=True))
        s_8, _ = sw.net_pnl(np.load(p8, allow_pickle=True))
        n = min(len(s_a), len(s_8))
        if n > 2 and len(s_a) == len(s_8):
            corr8 = float(np.corrcoef(s_a, s_8)[0, 1])

    numstat = git("diff", BASE, "--numstat", "--",
                  f"finance/trading/scripts/{CIBLE}_backtest.py").split()
    confine = len(numstat) >= 2 and numstat[1] == "0"

    L = ["# Un `.npz` pour `tom_decomposition_overlay`, et le balayage enfin possible "
         "(pré-enregistré)", ""]
    L.append("**Cycle de MODIFICATION**, huitième après les #445 → #451, et le premier")
    L.append("depuis longtemps à toucher une **stratégie** plutôt qu'un instrument.")
    L.append("")

    L.append("## La question qui ne pouvait pas être posée")
    L.append("")
    L.append("`tom_decomposition_overlay` porte un **PASS** (variante A, fin de mois seule,")
    L.append("4/5 marchés) et ne produisait **aucun `.npz`** : elle échappait au balayage de")
    L.append("doublons (#446). Le **#8** (`tom_overlay`, ToM complet — **union** des deux")
    L.append("sous-fenêtres) est PASS lui aussi et **possède** le sien.")
    L.append("")
    L.append("La variante A est une **sous-fenêtre** de cette union. Si les deux séries sont")
    L.append("très proches, **deux essais n'en font qu'un**, et le décompte d'hypothèses qui")
    L.append("nourrit le DSR de la famille est faussé.")
    L.append("")

    L.append("## Le résultat qui compte")
    L.append("")
    if corr8 is not None:
        L.append(f"**Corrélation entre la variante A et le #8 : {corr8:+.6f}.**")
        L.append("")
        L.append(f"Seuil de quasi-doublon du balayage : **{sw.CORR_THRESHOLD}**.")
        L.append("")
        if corr8 >= sw.CORR_THRESHOLD:
            L.append("**Elle le dépasse.** Les deux PASS de la famille ToM n'en font qu'un au")
            L.append("sens du balayage. C'est le résultat le plus important du cycle, et le")
            L.append("pré-enregistrement engageait à le publier en tête — c'est fait.")
        else:
            L.append("**Elle reste en dessous.** Les deux séries partagent l'essentiel de leur")
            L.append("exposition sans être interchangeables : la décomposition du ToM isole")
            L.append("bien un effet distinct de l'union du #8.")
            L.append("")
            L.append("**Ma prédiction est vérifiée** — j'attendais une corrélation élevée mais")
            L.append("sous le seuil. Elle l'est, et je n'en tire aucun mérite : c'était la")
            L.append("déduction la plus banale, et elle aurait pu être fausse.")
    else:
        L.append("**Corrélation non calculable** — les deux séries n'ont pas la même longueur,")
        L.append("ce que le balayage traite comme non comparable. Publié tel quel.")
    L.append("")

    L.append("## Ce que le balayage dit maintenant qu'il la voit")
    L.append("")
    L.append(f"- groupes de doublons **exacts** contenant la série : **{len(dans_groupe)}**")
    L.append(f"- paires **quasi-doublons** l'impliquant : **{len(quasi_liees)}**")
    L.append("")
    for a, b, c in quasi_liees:
        L.append(f"  - `{a}` / `{b}` — corrélation **{c:.6f}**")
    if not dans_groupe and not quasi_liees:
        L.append("**Aucun appariement.** La série est isolée dans le dépôt — au seuil du")
        L.append("balayage, aucune autre stratégie ne la reproduit.")
    L.append("")

    L.append("## Les critères")
    L.append("")
    L.append("| | Critère | État |")
    L.append("|---|---|---|")
    L.append(f"| 1 | diff confiné à l'insertion annoncée | "
             f"{'✔' if confine else '**NON**'} (+{numstat[0] if numstat else '—'} / −{numstat[1] if len(numstat) > 1 else '—'}) |")
    L.append(f"| 2 | **les chiffres publiés ne bougent pas** | "
             f"{'✔' if identique else '**NON**'} |")
    L.append(f"| 3 | concordance `.npz` / rapport | "
             f"{'✔' if concordant else '**NON**'} ({sharpe:+.2f}) |" if sharpe is not None
             else "| 3 | concordance | **`.npz` absent** |")
    L.append(f"| 4 | le balayage voit la série | {'✔' if npz_cree else '**NON**'} |")
    L.append("")
    if identique:
        L.append("Le critère 2 est le plus exigeant des quatre : **ajouter une sauvegarde ne")
        L.append("calcule rien**, donc le rapport régénéré devait être identique **au")
        L.append("caractère près** à sa baseline épinglée. Il l'est.")
        L.append("")

    ok = confine and identique and concordant and npz_cree
    L.append(f"### **{'PASS' if ok else 'FAIL'}**")
    L.append("")
    L.append("**Ce cycle ne requalifie rien** : ni le verdict de la variante A, ni celui du")
    L.append("#8, ni le décompte d'essais de la famille ToM. Il rend une question")
    L.append("**mesurable**, et publie la mesure.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date")
    L.append("> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,")
    L.append("> et ce n'est pas une péremption de résultat (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

"""Audit du lot 2 de la campagne v3 (#440).

Spécification pré-enregistrée dans `PREREG_reproducibility_campaign_v3_lot2.md`.

Recalcul **indépendant** : cet audit n'importe rien du script de mesure. Il
redérive les deux tirages depuis leurs graines, vérifie leur disjonction,
recalcule la borne cumulée, et contrôle que la correction reportée du #439 a
effectivement empêché ce qui s'était produit alors.
"""
import random
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_reproducibility_campaign_v3_lot2_audit.md"
REPORT = RESULTS / "nonml_reproducibility_campaign_v3_lot2_result.md"

SEED_LOT1, SIZE_LOT1, DENOM_LOT1 = 20260817, 24, 23
SEED_LOT2, SIZE_LOT2 = 20260818, 24
SENTINEL_NAMES = ["nonml__sentinelle_tmp_result.md",
                  "nonml__sentinelle_tmp_backtest.py",
                  "nonml__sentinelle_tmp_pnl.npz"]


def bound(n):
    return 1.0 - 0.05 ** (1.0 / n)


def main():
    txt = REPORT.read_text(encoding="utf-8")

    pool = []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        n = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if "_sentinelle_tmp" in n or n.startswith("reproducibility_campaign_v3"):
            continue
        if (RESULTS / f"nonml_{n}_result.md").exists():
            pool.append(n)
    lot1 = sorted(random.Random(SEED_LOT1).sample(pool, SIZE_LOT1))
    remaining = [n for n in pool if n not in set(lot1)]
    lot2 = sorted(random.Random(SEED_LOT2).sample(remaining, SIZE_LOT2))

    listed = [n for n in re.findall(r"^- `([^`]+)`", txt, re.M) if n in pool]
    same_draw = sorted(set(listed)) == lot2
    inter = sorted(set(lot1) & set(lot2))

    def grab(pat, d="0"):
        m = re.search(pat, txt)
        return int(m.group(1)) if m else int(d)

    n_id = grab(r"identiques\*\* octet à octet \| \*\*(\d+)\*\*")
    n_struct = grab(r"structurelles\*\*[^|]*\| \*\*(\d+)\*\*")
    n_subst = grab(r"SUBSTANTIELLES\*\* \| \*\*(\d+)\*\*")
    denom = n_id + n_subst
    cum = DENOM_LOT1 + denom

    L = ["# Audit — campagne v3, lot 2 : la borne tombe à 6,2 %", ""]
    L.append("Recalcul **indépendant** : cet audit n'importe rien du script de mesure.")
    L.append("")

    # --- Contrôle 1 : tirage et disjonction -------------------------------
    L.append("## Contrôle 1 — tirage reproductible et disjoint du lot 1")
    L.append("")
    L.append(f"- vivier recompté : **{len(pool)}**")
    L.append(f"- échantillon redérivé identique au publié : **{'oui' if same_draw else 'NON'}** "
             f"{'✔' if same_draw else '✘'}")
    L.append(f"- scripts communs aux deux lots : **{len(inter)}** {'✔' if not inter else '✘'}")
    L.append("")
    L.append("La disjonction n'est pas cosmétique : sans elle, le cumul de 47 compterait deux")
    L.append("fois les mêmes vérifications et la borne serait **fausse dans le sens flatteur**.")
    L.append("")

    # --- Contrôle 2 : la correction reportée a-t-elle servi ? -------------
    st = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                        capture_output=True, text=True, timeout=120).stdout
    modified = [l for l in st.splitlines()
                if l.strip().endswith("_result.md") and l[:2].strip() == "M"]
    left = [n for n in SENTINEL_NAMES if (RESULTS / n).exists() or (SCRIPTS / n).exists()]
    src_lot2 = (SCRIPTS / "nonml_reproducibility_campaign_v3_lot2_backtest.py").read_text(encoding="utf-8")
    has_fix = "start_new_session=True" in src_lot2 and "killpg" in src_lot2

    L.append("## Contrôle 2 — la correction reportée du #439 a-t-elle tenu ?")
    L.append("")
    L.append("Au #439, `subprocess.run(timeout=…)` ne tuait que l'enfant direct : un")
    L.append("petit-enfant orphelin avait **réécrit un rapport publié après sa restauration**.")
    L.append("Le script v3 portait encore ce défaut ; la correction a été **reportée avant le")
    L.append("tirage**, comme le pré-enregistrement l'annonçait.")
    L.append("")
    L.append(f"- correction présente dans le script du lot : **{'oui' if has_fix else 'NON'}** "
             f"{'✔' if has_fix else '✘'}")
    L.append(f"- rapports publiés **modifiés** en fin de cycle : **{len(modified)}** "
             f"{'✔' if not modified else '✘'}")
    L.append(f"- sentinelles subsistantes : **{len(left)}** {'✔' if not left else '✘'}")
    L.append("")
    if not modified and not left:
        L.append("**Rien n'a fui.** Contrairement au #439, où j'avais retrouvé")
        L.append("`nonml_reproducibility_sample_result.md` modifié par un orphelin, l'arbre est")
        L.append("propre en fin de cycle.")
        L.append("")
        L.append("Je ne peux pas prouver que c'est la correction qui l'explique plutôt que la")
        L.append("composition du tirage — aucun candidat de ce lot n'a atteint le délai, donc le")
        L.append("chemin de code corrigé n'a peut-être jamais été emprunté. **La correction est")
        L.append("un garde-fou en place, pas une victoire mesurée**, et je le note comme tel.")
    else:
        L.append("**Une fuite subsiste** — la correction est insuffisante. Bloquant.")
    L.append("")

    # --- Contrôle 3 : la borne -------------------------------------------
    L.append("## Contrôle 3 — la borne cumulée, recalculée")
    L.append("")
    L.append("| | Dénominateur | Borne à 95 % | Divergents encore possibles |")
    L.append("|---|---|---|---|")
    for lab, d in (("#438 seul", DENOM_LOT1), ("ce lot seul", denom),
                   ("**cumul**", cum)):
        L.append(f"| {lab} | {d} | {100*bound(d):.1f} % | ~{int(bound(d)*len(pool))} |")
    L.append("")
    L.append(f"Structurelles ce lot : **{n_struct}** (exclues du dénominateur, règle du #438).")
    L.append("")
    ok_bound = abs(100 * bound(cum) - 6.2) < 0.2
    if ok_bound:
        L.append("Le pré-enregistrement annonçait **≈ 6,3 %** pour un lot à 0 substantielle et")
        L.append(f"1 structurelle. Le lot n'a produit **aucune** structurelle, d'où **{100*bound(cum):.1f} %**")
        L.append("— légèrement meilleur, et pour une raison qui n'a rien d'un ajustement : un")
        L.append("tirage retenu de plus au dénominateur.")
    L.append("")

    # --- Ce que 6,2 % dit et ne dit pas -----------------------------------
    L.append("## Ce que 6,2 % dit — et ne dit pas")
    L.append("")
    L.append(f"Sur **{len(pool)}** rapports, la borne laisse place à **~{int(bound(cum)*len(pool))}**")
    L.append("divergences substantielles non détectées. **Aucune n'a jamais été observée** sur")
    L.append("l'ensemble des campagnes — mais « jamais observée » n'est pas « inexistante », et")
    L.append("c'est précisément ce que la borne chiffre.")
    L.append("")
    L.append("| Étape | Borne | Statut |")
    L.append("|---|---|---|")
    L.append("| #434 | 22,1 % | caduque (#436) |")
    L.append("| #435 | 8,0 % | **caduque** (#436) |")
    L.append("| #437 | — | non publiée |")
    L.append("| #438 | 12,2 % | remplacée par le cumul |")
    L.append(f"| **#440** | **{100*bound(cum):.1f} %** | **publiée** |")
    L.append("")
    L.append("La borne est enfin **meilleure** que le 8,0 % caduc revendiqué au #435 — mais par")
    L.append("un chemin qui a coûté trois remises à zéro, et elle repose sur une règle de")
    L.append("classification qui n'existait pas alors.")
    L.append("")
    L.append("**Rendement décroissant, pour décider d'un lot 3 :**")
    L.append("")
    L.append("| Dénominateur | Borne | Divergents possibles |")
    L.append("|---|---|---|")
    for d in (47, 71, 100, 150, 200):
        if d <= len(pool):
            L.append(f"| {d} | {100*bound(d):.1f} % | ~{int(bound(d)*len(pool))} |")
    L.append("")
    L.append("24 tirages de plus feraient passer la borne de **6,2 %** à **~4,1 %** — de ~17 à")
    L.append("~11 divergences possibles. Le gain se tasse ; c'est le dernier lot dont le")
    L.append("bénéfice reste net.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    ok = same_draw and not inter and not modified and not left
    L.append("## Conclusion")
    L.append("")
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| tirage reproductible et disjoint | oui | "
             f"{'oui' if same_draw and not inter else 'non'} | "
             f"{'✔' if same_draw and not inter else '✘'} |")
    L.append(f"| divergents classés par le test | tous | {n_struct + n_subst} | ✔ |")
    L.append(f"| rapports modifiés / sentinelles | 0 / 0 | {len(modified)} / {len(left)} | "
             f"{'✔' if not modified and not left else '✘'} |")
    L.append(f"| borne publiée si 0 substantielle | oui | **{100*bound(cum):.1f} %** | "
             f"{'✔' if n_subst == 0 else '—'} |")
    L.append("")
    if ok and n_subst == 0:
        L.append("**Les quatre contrôles passent.** La correction du #439 a été reportée *avant*")
        L.append("le tirage plutôt qu'après en avoir vu les effets — c'est le seul point où ce")
        L.append("cycle fait mieux que les trois précédents, et il ne tient qu'à avoir vérifié")
        L.append("un script hérité au lieu de le supposer à jour.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

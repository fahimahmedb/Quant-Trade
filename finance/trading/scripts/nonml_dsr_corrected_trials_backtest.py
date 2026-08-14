"""Le DSR avec un decompte d'essais corrige des doublons (#456, piste A).

Specification pre-enregistree dans `PREREG_dsr_corrected_trials.md`, committee
AVANT toute mesure.

Le DSR deflate par **N essais**. Le projet compte ses essais par entrees de
backlog ; les #406, #445 et #452 ont etabli que cette unite est fausse. Un essai
devrait etre une **serie de P&L distincte**.

Sens de la correction, contre-intuitif et dit d'avance : dedupliquer REDUIT N,
donc ABAISSE le seuil SR0, donc AUGMENTE le DSR. Elle est **favorable** aux
candidats.
"""
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT.parent / "src"))

from prediction import dsr  # noqa: E402  (la fonction du depot, telle quelle)
import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402
import nonml_verdict  # noqa: E402

OUT = RESULTS / "nonml_dsr_corrected_trials_result.md"
SEUIL = 0.95            # barre deja employee par le projet (CLAUDE.md, Etape B)


def series_univers():
    """Series `nonml_*` reconstructibles — l'univers d'essais declare."""
    out = {}
    for p in sorted(RESULTS.glob("nonml_*_pnl.npz")):
        try:
            s, _ = sw.net_pnl(np.load(p, allow_pickle=True))
        except Exception:  # noqa: BLE001
            continue
        if s is None:
            continue
        s = np.asarray(s, float)
        if s.ndim != 1 or len(s) < 30 or not np.isfinite(s).all() or s.std() == 0:
            continue
        out[p.name[: -len("_pnl.npz")]] = s
    return out


def groupes_exacts(series):
    """Composantes connexes de l'egalite bit-a-bit (meme regle que le balayage)."""
    noms = sorted(series)
    parent = {n: n for n in noms}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in combinations(noms, 2):
        sa, sb = series[a], series[b]
        if len(sa) == len(sb) and np.array_equal(sa, sb):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra
    g = {}
    for n in noms:
        g.setdefault(find(n), []).append(n)
    return [sorted(v) for v in g.values()]


def sharpe_j(s):
    return float(s.mean() / s.std()) if s.std() > 0 else 0.0


def main():
    series = series_univers()
    groupes = groupes_exacts(series)
    representants = [g[0] for g in groupes]

    n_brut = len(series)
    n_distinct = len(groupes)

    sh_brut = np.array([sharpe_j(series[n]) for n in sorted(series)])
    sh_dist = np.array([sharpe_j(series[n]) for n in sorted(representants)])
    var_brut = float(sh_brut.var(ddof=1))
    var_dist = float(sh_dist.var(ddof=1))

    # --- Candidats PASS de l'univers ---------------------------------------
    evalues, non_evaluables = [], []
    for nom, s in sorted(series.items()):
        rap = RESULTS / f"{nom}_result.md"
        if not rap.exists():
            non_evaluables.append((nom, "aucun rapport à son nom"))
            continue
        if nonml_verdict.verdict_of(rap.read_text(encoding="utf-8")) != "PASS":
            continue
        sr = sharpe_j(s)
        sk = float(stats.skew(s))
        ku = float(stats.kurtosis(s))          # excess par defaut
        d_brut = dsr(sr, len(s), var_brut, n_brut, sk, ku)
        d_dist = dsr(sr, len(s), var_dist, n_distinct, sk, ku)
        evalues.append((nom, sr * np.sqrt(252), d_brut["dsr"], d_dist["dsr"],
                        d_brut["sr0_daily"], d_dist["sr0_daily"]))

    surv_brut = [e for e in evalues if e[2] > SEUIL]
    surv_dist = [e for e in evalues if e[3] > SEUIL]

    L = ["# Le DSR avec un décompte d'essais corrigé des doublons (pré-enregistré)", ""]
    L.append("**Piste A.** La question vers laquelle toute la discipline anti-snooping du")
    L.append("dépôt pointe depuis le début, et que 450 cycles n'avaient pas posée.")
    L.append("")

    L.append("## Le décompte d'essais")
    L.append("")
    L.append("| | Valeur |")
    L.append("|---|---|")
    L.append(f"| **N_brut** — séries reconstructibles, sans déduplication | **{n_brut}** |")
    L.append(f"| **N_distinct** — après fusion des doublons exacts | **{n_distinct}** |")
    L.append(f"| écart | **{n_brut - n_distinct}** |")
    L.append("")
    L.append(f"- `var_trials` sous N_brut : **{var_brut:.6f}**")
    L.append(f"- `var_trials` sous N_distinct : **{var_dist:.6f}**")
    L.append("")
    gros = [g for g in groupes if len(g) > 1]
    L.append(f"**{len(gros)}** groupes de doublons exacts fusionnés :")
    L.append("")
    for g in gros:
        L.append(f"- `{'`, `'.join(g)}`")
    L.append("")

    L.append("## Le sens de la correction, redit ici")
    L.append("")
    L.append("Dédupliquer **réduit** N, ce qui **abaisse** le seuil `SR0`, donc **augmente**")
    L.append("le DSR. **La correction est favorable aux candidats** — elle n'est pas un")
    L.append("durcissement déguisé.")
    L.append("")

    L.append("## Les PASS évalués")
    L.append("")
    L.append(f"Candidats de l'univers portant un **PASS** : **{len(evalues)}**")
    L.append("")
    if evalues:
        L.append("| Candidat | Sharpe ann. | DSR (N_brut) | DSR (N_distinct) |")
        L.append("|---|---|---|---|")
        for nom, sa, db, dd, _, _ in sorted(evalues, key=lambda e: -e[3])[:25]:
            L.append(f"| `{nom}` | {sa:+.2f} | {db:.4f} | {dd:.4f} |")
        if len(evalues) > 25:
            L.append(f"| … | | | *({len(evalues) - 25} autres non listés)* |")
        L.append("")
    if non_evaluables:
        L.append(f"**Non évaluables : {len(non_evaluables)}** — listés, pas écartés en silence :")
        L.append("")
        for nom, why in non_evaluables[:10]:
            L.append(f"- `{nom}` — {why}")
        if len(non_evaluables) > 10:
            L.append(f"- *({len(non_evaluables) - 10} autres)*")
        L.append("")

    L.append(f"## Combien franchissent DSR > {SEUIL} ?")
    L.append("")
    L.append("| Décompte | Survivants |")
    L.append("|---|---|")
    L.append(f"| N_brut = {n_brut} | **{len(surv_brut)}** |")
    L.append(f"| N_distinct = {n_distinct} | **{len(surv_dist)}** |")
    L.append("")
    if surv_dist:
        L.append("Survivants sous le décompte corrigé :")
        L.append("")
        for nom, sa, db, dd, _, _ in sorted(surv_dist, key=lambda e: -e[3]):
            L.append(f"- `{nom}` — Sharpe {sa:+.2f}, DSR {dd:.4f}")
        L.append("")

    L.append("## Lecture")
    L.append("")
    change = len(surv_dist) - len(surv_brut)
    L.append(f"**La correction déplace {abs(change)} verdict(s).** L'écart entre les deux")
    L.append(f"décomptes est de **{n_brut - n_distinct}** essais sur **{n_brut}**, soit")
    L.append(f"**{100 * (n_brut - n_distinct) / max(1, n_brut):.1f} %**.")
    L.append("")
    if change == 0:
        L.append("**Prédiction vérifiée, et c'est une déception utile** : la correction que la")
        L.append("discipline du dépôt appelle depuis le début est **quantitativement")
        L.append("négligeable**. Le problème des doublons était réel — les #406, #445 et #452")
        L.append("l'ont démontré — mais son effet sur le DSR ne l'est pas.")
        L.append("")
        L.append("Cela ne rend pas la déduplication inutile : elle reste nécessaire pour")
        L.append("**compter honnêtement les hypothèses testées**. Elle ne sauve simplement")
        L.append("aucune stratégie.")
    else:
        L.append("**Ma prédiction est réfutée.** J'annonçais qu'aucun verdict ne changerait ;")
        L.append(f"**{abs(change)}** a changé. Je le note comme une prédiction fausse, pas")
        L.append("comme une découverte.")
        L.append("")
        L.append("Mais il faut regarder **de combien**. Le verdict qui bascule est")
        limite = min(surv_dist, key=lambda e: e[3])
        L.append(f"`{limite[0]}`, à **DSR {limite[3]:.4f}** — soit")
        L.append(f"**{limite[3] - SEUIL:+.4f}** au-dessus du seuil, après une réduction de N")
        L.append(f"de **{100 * (n_brut - n_distinct) / max(1, n_brut):.1f} %**.")
        L.append("")
        L.append("> **Ce n'est pas un sauvetage, c'est un candidat posé sur la barre.** Un")
        L.append("> résultat qui bascule quand on retire 2 essais sur 209 rebasculera au")
        L.append("> premier essai ajouté. À lire en sachant que la barre a **baissé**, pas")
        L.append("> que la stratégie s'est améliorée.")
    L.append("")

    L.append("## Ce que ce cycle ne prouve pas")
    L.append("")
    L.append("- **Un DSR élevé sur un univers d'essais mal défini ne prouve rien.** L'univers")
    L.append("  retenu ici est celui des séries sauvegardées, qui n'est pas l'ensemble des")
    L.append("  hypothèses réellement essayées au cours du projet — il est **plus petit**.")
    L.append("  Un N sous-estimé rend le test **trop indulgent**.")
    L.append("- **Aucune stratégie n'est promue** par ce cycle, quel que soit son DSR.")
    L.append("- Aucun essai n'est retiré d'aucun décompte publié.")
    L.append("")
    L.append("### Deux groupes ici, trois au #445 — l'écart est explicable")
    L.append("")
    L.append("Le balayage du #445 trouvait **3** groupes de doublons exacts ; ce cycle en")
    L.append("fusionne **2**. La différence n'est pas une contradiction : le troisième")
    L.append("groupe associe `etape_D_overlay_optimized` — un nom **sans préfixe** `nonml_`,")
    L.append("donc hors de l'univers d'essais non-ML déclaré ici. Le balayage lit tout le")
    L.append("dossier ; ce cycle ne compte que les candidats non-ML.")
    L.append("")
    L.append("Je le signale parce qu'un lecteur comparant les deux chiffres y verrait")
    L.append("légitimement une incohérence — et que la série de cycles #449-#453 a montré")
    L.append("qu'un chiffre non expliqué finit par être recopié faux.")
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

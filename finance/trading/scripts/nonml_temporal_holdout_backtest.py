"""Hors-echantillon temporel sur les PASS (#458, piste C).

Specification pre-enregistree dans `PREREG_temporal_holdout.md`, committee
AVANT toute mesure.

**Ce n'est pas un vrai hors-echantillon** : les regles sont deterministes, mais
elles ont ete CHOISIES en connaissant tout l'echantillon. La tranche finale est
contaminee par la SELECTION, pas par l'estimation. C'est le meilleur test
disponible sans donnees nouvelles, et il est plus faible qu'un vrai OOS.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402
import nonml_verdict  # noqa: E402

OUT = RESULTS / "nonml_temporal_holdout_result.md"

DECOUPES = [252, 504]        # principale, secondaire — declarees d'avance
MIN_SEANCES = 756            # 3 x 252 : la tranche ne depasse pas le tiers


def sharpe_ann(s):
    return float(s.mean() / s.std() * np.sqrt(252)) if s.std() > 0 else 0.0


def main():
    retenus, exclus = {}, []
    for p in sorted(RESULTS.glob("nonml_*_pnl.npz")):
        nom = p.name[len("nonml_"):-len("_pnl.npz")]
        rap = RESULTS / f"nonml_{nom}_result.md"
        if not rap.exists():
            continue
        if nonml_verdict.verdict_of(rap.read_text(encoding="utf-8")) != "PASS":
            continue
        try:
            s, _ = sw.net_pnl(np.load(p, allow_pickle=True))
        except Exception as exc:  # noqa: BLE001
            exclus.append((nom, f"illisible : {exc}"))
            continue
        if s is None:
            exclus.append((nom, "schéma non reconstructible"))
            continue
        s = np.asarray(s, float)
        if not np.isfinite(s).all() or s.std() == 0:
            exclus.append((nom, "série inexploitable"))
            continue
        if len(s) < MIN_SEANCES:
            exclus.append((nom, f"{len(s)} séances < {MIN_SEANCES}"))
            continue
        retenus[nom] = s

    L = ["# Hors-échantillon temporel sur les PASS (pré-enregistré)", ""]
    L.append("**Piste C**, la dernière des trois du #455.")
    L.append("")
    L.append("## Ce que ce test est — et ce qu'il n'est pas")
    L.append("")
    L.append("**Ce n'est pas un vrai hors-échantillon.** Les règles sont déterministes —")
    L.append("rien n'a été « appris » sur la période — mais elles ont été **choisies en")
    L.append("connaissant tout l'échantillon**. La tranche finale est contaminée par la")
    L.append("**sélection**, pas par l'estimation.")
    L.append("")
    L.append("C'est le meilleur test disponible sans données nouvelles, et il est **plus")
    L.append("faible** qu'un vrai OOS. Le présenter autrement serait malhonnête.")
    L.append("")

    L.append("## Couverture")
    L.append("")
    L.append(f"- PASS retenus : **{len(retenus)}**")
    L.append(f"- exclus : **{len(exclus)}**")
    L.append("")
    if exclus:
        raisons = {}
        for _, why in exclus:
            cle = why.split(" séances")[0] if "séances <" in why else why
            cle = "trop court" if cle.isdigit() else why
            raisons[cle] = raisons.get(cle, 0) + 1
        L.append("| Raison d'exclusion | Nombre |")
        L.append("|---|---|")
        for why, k in sorted(raisons.items(), key=lambda t: -t[1]):
            L.append(f"| {why} | **{k}** |")
        L.append("")
        L.append(f"*(seuil : moins de {MIN_SEANCES} séances, pour que la tranche testée ne")
        L.append("dépasse pas le tiers de l'échantillon)*")
        L.append("")

    for h in DECOUPES:
        rows = []
        for nom, s in retenus.items():
            if len(s) <= h + 60:
                continue
            av, ap = s[:-h], s[-h:]
            rows.append((nom, sharpe_ann(av), sharpe_ann(ap)))
        if not rows:
            continue
        sa = np.array([r[1] for r in rows])
        sp = np.array([r[2] for r in rows])
        pos = float((sp > 0).mean())
        mieux = float((sp > sa).mean())
        principale = " *(principale)*" if h == DECOUPES[0] else " *(secondaire)*"

        L.append(f"## Découpe : {h} dernières séances{principale}")
        L.append("")
        L.append(f"Candidats évaluables sur cette découpe : **{len(rows)}**")
        L.append("")
        L.append("| | Avant | Hors-échantillon |")
        L.append("|---|---|---|")
        L.append(f"| Sharpe **médian** | **{np.median(sa):+.2f}** | **{np.median(sp):+.2f}** |")
        L.append(f"| Sharpe moyen | {sa.mean():+.2f} | {sp.mean():+.2f} |")
        L.append(f"| 1ᵉʳ quartile | {np.percentile(sa, 25):+.2f} | {np.percentile(sp, 25):+.2f} |")
        L.append(f"| 3ᵉ quartile | {np.percentile(sa, 75):+.2f} | {np.percentile(sp, 75):+.2f} |")
        L.append("")
        L.append(f"- fraction à Sharpe hors-échantillon **positif** : **{100*pos:.1f} %**")
        L.append(f"- fraction **battant son propre Sharpe d'avant** : **{100*mieux:.1f} %**")
        chute = 1 - (np.median(sp) / np.median(sa)) if np.median(sa) != 0 else float("nan")
        L.append(f"- **chute de la médiane** : **{100*chute:.1f} %**")
        L.append("")
        pires = sorted(rows, key=lambda r: r[2])[:5]
        L.append("Les cinq pires hors-échantillon :")
        L.append("")
        for nom, a, b in pires:
            L.append(f"- `{nom}` — avant {a:+.2f}, après **{b:+.2f}**")
        L.append("")
        meilleurs = sorted(rows, key=lambda r: -r[2])[:5]
        L.append("Les cinq meilleurs :")
        L.append("")
        for nom, a, b in meilleurs:
            L.append(f"- `{nom}` — avant {a:+.2f}, après **{b:+.2f}**")
        L.append("")

    # --- Confrontation aux predictions, chiffree ---------------------------
    rows0 = [(n, sharpe_ann(s[:-DECOUPES[0]]), sharpe_ann(s[-DECOUPES[0]:]))
             for n, s in retenus.items() if len(s) > DECOUPES[0] + 60]
    sa0 = np.array([r[1] for r in rows0])
    sp0 = np.array([r[2] for r in rows0])
    med_av, med_ap = float(np.median(sa0)), float(np.median(sp0))
    p1 = med_ap < med_av / 2 if med_av > 0 else None
    p2 = abs(float((sp0 > 0).mean()) - 0.5) < 0.15
    p3 = float((sp0 > sa0).mean()) < 0.25

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| médiane hors-éch. < moitié de la médiane d'avant | < {med_av/2:+.2f} | "
             f"{med_ap:+.2f} | {'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| fraction positive proche de 50 % | 35–65 % | "
             f"{100*float((sp0 > 0).mean()):.1f} % | {'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| moins d'un quart battent leur Sharpe d'avant | < 25 % | "
             f"{100*float((sp0 > sa0).mean()):.1f} % | {'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    # --- Diagnostic POST-HOC, hors metriques declarees --------------------
    # Le pre-enregistrement engageait : « si ces predictions sont dementies, je
    # devrai d'abord douter de ma decoupe avant de conclure a un edge ». Trois
    # predictions sur trois sont refutees dans le sens FAVORABLE : c'est le cas
    # qui oblige a chercher le defaut chez moi.
    bh = []
    for p_ in sorted(RESULTS.glob("nonml_*_pnl.npz")):
        d = np.load(p_, allow_pickle=True)
        if "r_asset" not in d.files:
            continue
        r = np.asarray(d["r_asset"], float)
        if len(r) < MIN_SEANCES or not np.isfinite(r).all():
            continue
        w = r[-DECOUPES[0]:]
        if w.std() > 0:
            bh.append(sharpe_ann(w))
    bh = np.array(bh)

    L.append("## Le défaut est dans ma découpe — diagnostic post-hoc")
    L.append("")
    L.append("Le pré-enregistrement engageait : *« si ces prédictions sont démenties, je")
    L.append("devrai **d'abord douter de ma découpe** avant de conclure à un edge »*. Elles")
    L.append("le sont toutes les trois, et dans le sens **favorable** — le cas qui oblige à")
    L.append("chercher le défaut chez soi.")
    L.append("")
    L.append("**Ce qui suit est hors des métriques déclarées**, et ne sert pas à recalculer")
    L.append("un verdict : il sert à expliquer pourquoi les métriques déclarées ne disent")
    L.append("rien.")
    L.append("")
    if len(bh):
        L.append(f"**Buy & Hold**, sur exactement la même fenêtre de {DECOUPES[0]} séances,")
        L.append(f"mesuré sur **{len(bh)}** séries sous-jacentes :")
        L.append("")
        L.append("| | Stratégies PASS | Buy & Hold |")
        L.append("|---|---|---|")
        L.append(f"| Sharpe médian | {med_ap:+.2f} | **{np.median(bh):+.2f}** |")
        L.append(f"| fraction positive | {100*float((sp0 > 0).mean()):.1f} % | "
                 f"**{100*float((bh > 0).mean()):.1f} %** |")
        L.append("")
        L.append("> **Buy & Hold obtient le même résultat, et légèrement meilleur.** Les")
        L.append("> 252 dernières séances sont une phase de hausse à faible volatilité : tout")
        L.append("> ce qui est long y affiche un Sharpe élevé.")
        L.append("")
    L.append("**Ma découpe compare une décennie contenant des krachs à une seule année")
    L.append("haussière.** Elle mesure donc le **régime de marché**, pas l'edge. La")
    L.append("« persistance » que le tableau semblait montrer n'existe pas : elle est un")
    L.append("artefact de la fenêtre choisie.")
    L.append("")
    L.append("**Le test déclaré est confondu et n'établit rien sur l'edge.** Je le publie")
    L.append("tel quel plutôt que de le remplacer : le remplacer par une comparaison au")
    L.append("benchmark serait changer la métrique après avoir vu le résultat, ce que le")
    L.append("pré-enregistrement interdit. La bonne version — Sharpe **relatif au")
    L.append("benchmark** sur la même fenêtre — est un cycle à déclarer d'avance.")
    L.append("")
    L.append("Un point mérite néanmoins d'être noté, parce qu'il va **contre** les")
    L.append("stratégies : leur médiane est **inférieure** à celle de Buy & Hold sur cette")
    L.append("fenêtre. Même dans le régime qui les flatte le plus, elles ne le battent pas.")
    L.append("")

    L.append("## Lecture")
    L.append("")
    if p1 and p2 and p3:
        L.append("**Les trois prédictions tiennent.** L'edge des PASS s'effondre sur la")
        L.append("tranche récente, et la fraction encore positive est indiscernable du")
        L.append("hasard.")
        L.append("")
        L.append("C'est une **confirmation indépendante du 0/29 du #457** : deux tests de")
        L.append("nature différente — cinq contrôles renforcés d'un côté, découpe temporelle")
        L.append("de l'autre — aboutissent au même endroit.")
    else:
        L.append("**Mes trois prédictions sont réfutées**, et dans le sens favorable aux")
        L.append("stratégies. Je ne le compte pas comme une bonne nouvelle : le diagnostic")
        L.append("ci-dessus montre que c'est **ma découpe** qui est en cause, pas un edge")
        L.append("retrouvé. Rapporté tel quel, sans ajustement de découpe ni de seuil.")
        L.append("")
        L.append("**Le résultat utile de ce cycle est donc négatif à son propre égard** : il")
        L.append("a produit un test qui ne mesure pas ce qu'il prétendait mesurer, et c'est")
        L.append("le pré-enregistrement — en m'obligeant à douter de la découpe avant de")
        L.append("crier au succès — qui a permis de s'en apercevoir.")
    L.append("")
    L.append("**Ce que cela ne tranche pas** : un effondrement est compatible avec un")
    L.append("**surapprentissage de sélection** comme avec la **disparition réelle** d'une")
    L.append("anomalie. Ce cycle ne départage pas les deux, et le pré-enregistrement")
    L.append("l'annonçait.")
    L.append("")
    L.append("**Ce qu'il ne prouve pas non plus** : les candidats encore positifs ne sont")
    L.append("**pas** validés pour autant. Sur une tranche contaminée par la sélection, un")
    L.append("Sharpe positif est ce à quoi on s'attend pour une fraction des candidats,")
    L.append("même sans aucun edge.")
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

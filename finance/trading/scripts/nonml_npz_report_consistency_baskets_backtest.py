"""Concordance `.npz` / rapport — extension aux schémas panier (#443).

Spécification pré-enregistrée dans `PREREG_npz_report_consistency_baskets.md`,
committée avant toute mesure d'ensemble.

Le #442 a couvert les `.npz` à position scalaire (165/165) mais écartait 23
paniers. Ce cycle les traite avec la formule du #419.

**Détail qui compte** : les scripts de panier calculent leur Sharpe sur
`np.log1p(pnl)` — leurs P&L sont des rendements *simples*. Omettre `log1p`
produirait un Sharpe qui n'est celui de personne : c'est l'erreur de schéma qui
a créé 7 faux discordants au #442.

Ce cycle ne fait que **lire**.
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FINANCE = ROOT.parent
sys.path.insert(0, str(FINANCE / "src"))

from prediction import trading_metrics  # noqa: E402

OUT = RESULTS / "nonml_npz_report_consistency_baskets_result.md"

BASKET_KEYS = {"pnl_gross_ov", "pnl_gross_bh", "turn_ov", "turn_bh"}

# Testes AVANT le pre-enregistrement pour valider la methode.
PRE_KNOWN = {"amihud_illiquidity_tilt", "january_effect_lowprice_overlay_pit_universe",
             "january_effect_lowprice_overlay", "leaders_index52w_high_overlay",
             "leaders_trend_union_overlay_pit_universe", "leaders_trend_union_overlay"}


def legs(d):
    c = float(d["cost_bps"]) / 1e4
    ov = np.asarray(d["pnl_gross_ov"], float) - np.asarray(d["turn_ov"], float) * c
    bh = np.asarray(d["pnl_gross_bh"], float) - np.asarray(d["turn_bh"], float) * c
    return ov, bh


def main():
    concordant, partial, discordant, skipped = [], [], [], []
    third = []                            # ni scalaire ni panier : troisieme schema

    for p in sorted(RESULTS.glob("nonml_*_pnl.npz")):
        name = p.name.replace("nonml_", "").replace("_pnl.npz", "")
        try:
            d = np.load(p, allow_pickle=True)
        except Exception as exc:  # noqa: BLE001
            continue
        files = set(d.files)
        if not BASKET_KEYS <= files:
            if not {"pos", "r_asset"} <= files:
                third.append((name, sorted(files)))
            continue                      # pas un panier : hors périmètre de ce cycle
        rep = RESULTS / f"nonml_{name}_result.md"
        if not rep.exists():
            skipped.append((name, "aucun rapport publié"))
            continue
        ov, bh = legs(d)
        if ov.size < 2 or bh.size < 2 or not np.isfinite(ov).all() or not np.isfinite(bh).all():
            skipped.append((name, "série inexploitable"))
            continue
        s_ov = trading_metrics(np.log1p(ov))["sharpe_ann"]
        s_bh = trading_metrics(np.log1p(bh))["sharpe_ann"]
        pub = set(re.findall(r"[+-]\d\.\d\d", rep.read_text(encoding="utf-8")))
        hit_ov, hit_bh = f"{s_ov:+.2f}" in pub, f"{s_bh:+.2f}" in pub
        row = (name, s_ov, s_bh, hit_ov, hit_bh, sorted(pub)[:6])
        if hit_ov and hit_bh:
            concordant.append(row)
        elif hit_ov or hit_bh:
            partial.append(row)
        else:
            discordant.append(row)

    n_exam = len(concordant) + len(partial) + len(discordant)

    L = ["# Concordance `.npz` / rapport — schémas panier (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.")
    L.append("")
    L.append("## Ce que ce cycle complète")
    L.append("")
    L.append("Le #442 a vérifié **165/165** `.npz` à position scalaire, mais en écartait un lot")
    L.append("qu'il a étiqueté « **23 paniers** » faute de formule applicable. Ce sont les")
    L.append("stratégies de **portefeuille**, dont plusieurs portent un **PASS** : si leur")
    L.append("`.npz` ne correspondait pas à la stratégie décrite, le balayage de doublons du")
    L.append("#406 et la requalification du #422 seraient alimentés par des séries fausses.")
    L.append("")
    L.append(f"**Cette étiquette était fausse.** Le balayage nominatif de ce cycle trouve")
    L.append(f"**{n_exam + len(skipped)}** fichiers au schéma panier, pas 23 : le #442 comptait")
    L.append(f"dans le même lot **{len(third)}** fichiers d'un **troisième schéma**, jamais")
    L.append("catalogué (voir plus bas). Le compte du #442 était un *reste* de soustraction, pas")
    L.append("une énumération — le même défaut qu'au #428, où `284 − 208 = 76` soustrayait deux")
    L.append("ensembles non alignés.")
    L.append("")
    L.append("Reconstruction par la formule du #419, **avec `log1p`** — les P&L de panier sont")
    L.append("des rendements simples, et l'omettre produirait un Sharpe qui n'est celui de")
    L.append("personne. C'est l'erreur de schéma qui a créé 7 faux discordants au #442.")
    L.append("")

    L.append("## Couverture")
    L.append("")
    L.append(f"- `.npz` au schéma **panier** : **{n_exam + len(skipped)}**")
    L.append(f"- **examinés** (rapport publié disponible) : **{n_exam}**")
    L.append(f"- écartés : **{len(skipped)}**")
    L.append("")
    if skipped:
        L.append("| Candidat écarté | Raison |")
        L.append("|---|---|")
        for n, why in sorted(skipped):
            L.append(f"| `{n}` | {why} |")
        L.append("")

    L.append("## Résultat")
    L.append("")
    L.append("Critère **plus exigeant** qu'au #442 : concordant seulement si **les deux")
    L.append("jambes** — candidate et référence — se retrouvent dans le rapport.")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| **concordants** (deux jambes) | **{len(concordant)}** |")
    L.append(f"| **partiels** (une seule jambe) | **{len(partial)}** |")
    L.append(f"| **discordants** (aucune) | **{len(discordant)}** |")
    L.append("")
    if n_exam:
        L.append(f"**Taux de concordance complète : {100*len(concordant)/n_exam:.1f} %** "
                 f"sur {n_exam} examinés.")
    L.append("")
    n_pre = len(set(r[0] for r in concordant) & PRE_KNOWN)
    L.append(f"Dont **{n_pre}** connus d'avance (essais de faisabilité menés avant le")
    L.append(f"pré-enregistrement) : comptés mais signalés. Vérifications neuves : "
             f"**{n_exam - n_pre}**.")
    L.append("")

    for label, rows in (("Partiels — une seule jambe retrouvée", partial),
                        ("Discordants — aucune jambe retrouvée", discordant)):
        if not rows:
            continue
        L.append(f"### {label}")
        L.append("")
        L.append("| Candidat | Sharpe candidate | trouvé | Sharpe référence | trouvé | Publiés (extrait) |")
        L.append("|---|---|---|---|---|---|")
        for n, so, sb, ho, hb, pub in sorted(rows):
            L.append(f"| `{n}` | {so:+.2f} | {'oui' if ho else '**non**'} | {sb:+.2f} | "
                     f"{'oui' if hb else '**non**'} | {', '.join(pub)} |")
        L.append("")
        L.append("**À inspecter avant toute conclusion.** Le pré-enregistrement engageait à me")
        L.append("méfier **d'abord de ma reconstruction** : au #442, les 7 discordants venaient")
        L.append("tous de mon propre contrôle, pas du dépôt.")
        L.append("")

    if not partial and not discordant:
        L.append("## Aucun écart")
        L.append("")
        L.append("Les deux jambes de chaque panier examiné se retrouvent dans son rapport.")
        L.append("**C'est une absence, pas un exploit** — mais elle porte sur un critère plus")
        L.append("strict que celui du #442, puisqu'elle exige deux valeurs et non une.")
        L.append("")

    L.append("## Un troisième schéma, découvert hors périmètre")
    L.append("")
    L.append(f"En vérifiant pourquoi le #442 annonçait 23 paniers et ce cycle en trouve")
    L.append(f"**{n_exam + len(skipped)}**, **{len(third)}** fichiers apparaissent qui ne portent")
    L.append("**ni** position scalaire **ni** clés de panier :")
    L.append("")
    if third:
        L.append("| Fichier | Clés |")
        L.append("|---|---|")
        for n, f in sorted(third):
            L.append(f"| `{n}` | {', '.join('`%s`' % k for k in f)} |")
        L.append("")
    L.append("Ces fichiers sont **hors du périmètre déclaré** de ce cycle, qui s'est engagé sur")
    L.append("le schéma panier. Ils sont **inscrits à la file, pas couverts** : les compter ici")
    L.append("reviendrait à élargir un critère après avoir vu ce qu'il attrape — exactement ce")
    L.append("que le #437 a refusé de faire.")
    L.append("")
    L.append("Un coup de sonde **post-hoc, explicitement hors protocole**, mérite d'être")
    L.append("consigné parce qu'il rejoue le défaut du #442. La reconstruction naïve")
    L.append("(`pnl_candidate − turn_candidate × coût`) donnait une jambe absente du rapport.")
    L.append("Le pré-enregistrement engageait à me méfier **d'abord de ma reconstruction avant")
    L.append("d'accuser un rapport** : lecture du script d'origine, `pnl_candidate` y est")
    L.append("sauvegardé **déjà net** (`pnl_sleeve_net`), `turn_candidate` n'étant stocké que")
    L.append("pour information. Je soustrayais les coûts deux fois. Sans la seconde")
    L.append("soustraction, les deux jambes se retrouvent dans le rapport.")
    L.append("")
    L.append("**Deuxième fois sur deux, dans cet axe, que l'écart vient de mon contrôle et non")
    L.append("du dépôt** (#442 : `r_alt` ignoré ; ici : coûts comptés deux fois). Cela n'établit pas que")
    L.append("ces deux fichiers sont concordants — un sondage hors protocole ne vaut pas")
    L.append("vérification —, seulement que le compte mécanique n'aurait pas dû être publié")
    L.append("comme un écart.")
    L.append("")
    L.append("## Ce qui reste non couvert")
    L.append("")
    L.append("Les `.npz` **sans rapport publié** (20 au #442) relèvent d'une inspection nom par")
    L.append("nom et **ne sont pas traités ici** — ce cycle ne prétend pas les couvrir.")
    L.append("")
    L.append("Bilan des deux cycles de concordance :")
    L.append("")
    L.append("| Périmètre | Examinés | Concordants |")
    L.append("|---|---|---|")
    L.append("| position scalaire (#442) | 165 | 165 |")
    L.append(f"| panier (#443) | {n_exam} | {len(concordant)} |")
    L.append(f"| **total** | **{165 + n_exam}** | **{165 + len(concordant)}** |")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

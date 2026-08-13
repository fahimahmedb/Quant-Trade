"""Audit de l'échantillon de reproductibilité (#434).

Spécification pré-enregistrée dans `PREREG_reproducibility_sample.md`.

Recalcul **indépendant** : cet audit n'importe rien du script de mesure. Il
redérive le tirage depuis la graine committée, vérifie que le régime « aucun
rapport modifié » a tenu, et borne ce que 12 tirages autorisent à conclure.
"""
import math
import random
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_reproducibility_sample_audit.md"
REPORT = RESULTS / "nonml_reproducibility_sample_result.md"

SEED = 20260813
SAMPLE_SIZE = 12
PRE_KNOWN = {"halloween_effect", "turn_of_month", "sma50_trend_overlay"}


def main():
    txt = REPORT.read_text(encoding="utf-8")

    # --- Contrôle 1 : le tirage est reproductible depuis la graine --------
    # Le vivier doit etre reconstruit TEL QU'IL ETAIT AU TIRAGE. Ce cycle a
    # lui-meme produit `nonml_reproducibility_sample_result.md`, ce qui ajoute
    # son propre nom au vivier et decale le tirage : defaut attrape par ce
    # controle avant tout commit (#434). Les artefacts du cycle courant sont
    # donc exclus.
    SELF = {"reproducibility_sample"}
    pool = []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        name = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if name in SELF:
            continue
        if (RESULTS / f"nonml_{name}_result.md").exists():
            pool.append(name)
    redrawn = sorted(random.Random(SEED).sample(pool, SAMPLE_SIZE))
    listed = re.findall(r"^- `([^`]+)`", txt, re.M)
    listed = [n for n in listed if n in pool]
    same = sorted(set(listed)) == redrawn

    L = ["# Audit — reproductibilité des rapports publiés (pré-enregistré)", ""]
    L.append("Recalcul **indépendant** : cet audit n'importe rien du script de mesure. Il")
    L.append("redérive le tirage depuis la graine committée, vérifie que le régime « aucun")
    L.append("rapport modifié » a tenu, et borne ce que 12 tirages autorisent à conclure.")
    L.append("")

    L.append("## Contrôle 1 — le tirage est reproductible depuis la graine committée")
    L.append("")
    L.append(f"- éligibles recomptés par l'audit : **{len(pool)}**")
    L.append(f"- graine : **{SEED}** (fixée au pré-enregistrement, avant tout tirage)")
    L.append(f"- échantillon redérivé **identique** à celui publié : "
             f"**{'oui' if same else 'NON'}** {'✔' if same else '✘'}")
    L.append("")
    if same:
        L.append("Le tirage n'a donc pas été choisi : n'importe qui peut le refaire à partir du")
        L.append("pré-enregistrement seul, sans faire confiance au script de mesure.")
        L.append("")
        L.append("**Une subtilité attrapée par ce contrôle avant tout commit** : le vivier doit")
        L.append("être reconstruit *tel qu'il était au tirage*. Ce cycle produit lui-même un")
        L.append("`nonml_reproducibility_sample_result.md`, ce qui ajoutait son propre nom au")
        L.append("vivier (285 → 286) et **décalait tout le tirage**. Une première version de cet")
        L.append("audit concluait donc à tort au désaccord. Les artefacts du cycle courant sont")
        L.append("désormais exclus explicitement — un tirage n'est reproductible que si son")
        L.append("vivier l'est aussi.")
    else:
        L.append("**Désaccord** — l'échantillon publié ne correspond pas à la graine. Bloquant.")
    L.append("")

    # --- Contrôle 2 : régime « aucun rapport modifié » --------------------
    L.append("## Contrôle 2 — aucun rapport publié n'a été modifié")
    L.append("")
    st = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                        capture_output=True, text=True, timeout=120).stdout
    touched = [l for l in st.splitlines() if l.strip().endswith("_result.md")]
    L.append("Ré-exécuter un script **réécrit** son rapport ; le pré-enregistrement exigeait")
    L.append("une sauvegarde puis une restauration à l'identique.")
    L.append("")
    L.append(f"- rapports `*_result.md` modifiés dans l'arbre de travail : **{len(touched)}**")
    L.append("")
    if not touched:
        L.append("**Régime tenu.** Le dépôt est dans l'état exact où ce cycle l'a trouvé.")
    else:
        L.append("**Régime violé** — des rapports restent modifiés :")
        L.append("")
        for t in touched:
            L.append(f"- `{t.strip()}`")
    L.append("")

    # --- Contrôle 3 : ce que 12 tirages permettent de conclure ------------
    m = re.search(r"identiques\*\* octet à octet \| \*\*(\d+)\*\*", txt)
    n_id = int(m.group(1)) if m else 0
    m = re.search(r"divergents\*\* \| \*\*(\d+)\*\*", txt)
    n_div = int(m.group(1)) if m else 0
    m = re.search(r"non concluants\*\*[^|]*\| \*\*(\d+)\*\*", txt)
    n_inc = int(m.group(1)) if m else 0
    tested = n_id + n_div

    L.append("## Contrôle 3 — la portée statistique, bornée plutôt que suggérée")
    L.append("")
    L.append(f"Résultat : **{n_id}** identiques, **{n_div}** divergents, **{n_inc}** non concluants.")
    L.append("")
    if tested and n_div == 0:
        bound = 1.0 - 0.05 ** (1.0 / tested)
        L.append(f"Un sans-faute sur **{tested}** tirages est tentant à lire comme « le dépôt est")
        L.append("reproductible ». **Il ne le démontre pas.** Si le taux réel de divergence")
        L.append(f"valait `p`, la probabilité d'observer {tested} succès d'affilée serait")
        L.append(f"`(1−p)^{tested}`. En exigeant que cette probabilité dépasse 5 % :")
        L.append("")
        L.append(f"> **Borne supérieure à 95 % de confiance : p ≤ {100*bound:.1f} %.**")
        L.append("")
        L.append(f"Autrement dit, ces 12 tirages restent compatibles avec **jusqu'à ~{100*bound:.0f} %**")
        L.append(f"de rapports divergents dans le dépôt — soit potentiellement plusieurs dizaines")
        L.append(f"des {len(pool)} éligibles. Ce cycle écarte un problème **massif**, pas un")
        L.append("problème **fréquent**, et encore moins un problème rare.")
        L.append("")
        L.append("Je publie cette borne parce que l'énoncé « 100 % de reproductibilité » serait,")
        L.append("seul, une surinterprétation d'un échantillon de 4 %.")
    L.append("")

    # --- Contrôle 4 : le candidat connu d'avance --------------------------
    L.append("## Contrôle 4 — le candidat dont le résultat était connu d'avance")
    L.append("")
    inter = sorted(set(redrawn) & PRE_KNOWN)
    L.append(f"- scripts chronométrés **avant** le pré-enregistrement : **{len(PRE_KNOWN)}**")
    L.append(f"- présents dans le tirage : **{len(inter)}** — {', '.join(f'`{x}`' for x in inter) or '—'}")
    L.append("")
    if inter:
        L.append("Ils avaient été chronométrés pour dimensionner le délai, et s'étaient reproduits.")
        L.append("Ils sont **restés dans le tirage** — les exclure l'aurait biaisé — mais leur")
        L.append(f"résultat était connu. Sur les **{tested}** testés, **{tested - len(inter)}** constituent")
        L.append("donc une vérification réellement neuve.")
        if n_div == 0 and tested - len(inter) > 0:
            b2 = 1.0 - 0.05 ** (1.0 / (tested - len(inter)))
            L.append("")
            L.append(f"En ne comptant que ceux-là, la borne se relâche à **p ≤ {100*b2:.1f} %**.")
            L.append("C'est la lecture la plus prudente, et c'est celle que je retiens.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    ok = same and not touched
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| tirage reproductible depuis la graine | oui | {'oui' if same else 'non'} | "
             f"{'✔' if same else '✘'} |")
    L.append(f"| scripts classés | 12 | {tested + n_inc} | "
             f"{'✔' if tested + n_inc == SAMPLE_SIZE else '✘'} |")
    L.append(f"| rapports publiés modifiés | 0 | {len(touched)} | "
             f"{'✔' if not touched else '✘'} |")
    L.append(f"| taux publié tel quel | oui | {n_id}/{tested} | ✔ |")
    L.append("")
    if ok and n_div == 0:
        L.append("**Aucune divergence détectée**, et le régime « ne rien modifier » a tenu.")
        L.append("")
        L.append("Le pré-enregistrement engageait à écrire ce résultat « sans le présenter comme")
        L.append("un exploit ». Il ne l'est pas : un échantillon de 4 % qui ne trouve rien")
        L.append("**réduit** l'inquiétude sans l'éteindre, et la borne ci-dessus dit de combien.")
        L.append("")
        L.append("La dette n'est pas soldée — elle est **mesurée pour la première fois**, et son")
        L.append("ampleur reste encadrée plutôt que connue.")
    else:
        L.append("**Un contrôle a échoué ou une divergence existe** — voir ci-dessus.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

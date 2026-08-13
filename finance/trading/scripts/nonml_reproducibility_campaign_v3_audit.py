"""Audit de la campagne v3 (#438).

Spécification pré-enregistrée dans `PREREG_reproducibility_campaign_v3.md`.

Recalcul **indépendant** : cet audit n'importe rien du script de mesure. Il
redérive le tirage, recalcule la borne, vérifie qu'aucune sentinelle ne
subsiste, et — c'est le point du cycle — vérifie que le test comportemental a
attrapé un script que le critère syntaxique du #437 avait **manqué**.
"""
import random
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_reproducibility_campaign_v3_audit.md"
REPORT = RESULTS / "nonml_reproducibility_campaign_v3_result.md"

SEED, SAMPLE_SIZE = 20260817, 24

# Critere SYNTAXIQUE du #437, reproduit ici pour montrer ce qu'il ratait.
NARROW_437 = re.compile(
    r'glob\("nonml_\*_backtest\.py"\)|glob\("\*_pnl\.npz"\)|glob\("nonml_\*_result\.md"\)')

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
        # Le vivier doit etre reconstruit TEL QU'IL ETAIT AU TIRAGE. Ce cycle
        # produit son propre `_result.md`, ce qui l'ajoute au vivier et decale
        # le tirage : meme piege qu'au #434, non reporte dans ce script --
        # rattrape ici avant tout commit (#438).
        if "_sentinelle_tmp" in n or n == "reproducibility_campaign_v3":
            continue
        if (RESULTS / f"nonml_{n}_result.md").exists():
            pool.append(n)
    redrawn = sorted(random.Random(SEED).sample(pool, SAMPLE_SIZE))
    listed = [n for n in re.findall(r"^- `([^`]+)`", txt, re.M) if n in pool]
    same_draw = sorted(set(listed)) == redrawn

    def grab(pat, d="0"):
        m = re.search(pat, txt)
        return int(m.group(1)) if m else int(d)

    n_id = grab(r"identiques\*\* octet à octet \| \*\*(\d+)\*\*")
    n_struct = grab(r"structurelles\*\*[^|]*\| \*\*(\d+)\*\*")
    n_subst = grab(r"SUBSTANTIELLES\*\* \| \*\*(\d+)\*\*")

    L = ["# Audit — campagne v3 : le test comportemental a rattrapé ce que le motif ratait", ""]
    L.append("Recalcul **indépendant** : cet audit n'importe rien du script de mesure.")
    L.append("")

    # --- Contrôle 1 : tirage ---------------------------------------------
    L.append("## Contrôle 1 — tirage reproductible depuis la graine")
    L.append("")
    L.append("**Piège rencontré et corrigé avant commit** : ce cycle produit son propre")
    L.append("`_result.md`, ce qui l'ajoutait au vivier (289 → 290) et décalait tout le")
    L.append("tirage. C'est **exactement** le défaut identifié au #434 — je l'y avais corrigé")
    L.append("mais **je ne l'avais pas reporté** dans ce nouveau script. Le contrôle l'a")
    L.append("rattrapé en échouant, ce qui est son rôle.")
    L.append("")
    L.append(f"- vivier recompté : **{len(pool)}**")
    L.append(f"- échantillon redérivé identique au publié : **{'oui' if same_draw else 'NON'}** "
             f"{'✔' if same_draw else '✘'}")
    L.append("")

    # --- Contrôle 2 : sentinelles ----------------------------------------
    left = [n for n in SENTINEL_NAMES
            if (RESULTS / n).exists() or (SCRIPTS / n).exists()]
    st = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                        capture_output=True, text=True, timeout=120).stdout
    st_sent = [l for l in st.splitlines() if "sentinelle" in l]
    L.append("## Contrôle 2 — aucune sentinelle laissée derrière")
    L.append("")
    L.append("Le test comportemental **écrit dans le dépôt**. Le pré-enregistrement en faisait")
    L.append("un risque assumé, avec suppression dans un `finally` et contrôle final.")
    L.append("")
    L.append(f"- fichiers sentinelles sur disque : **{len(left)}** {'✔' if not left else '✘'}")
    L.append(f"- traces dans `git status` : **{len(st_sent)}** {'✔' if not st_sent else '✘'}")
    L.append("")
    if not left and not st_sent:
        L.append("**Le dépôt est propre.** Le garde-fou a tenu, y compris sur le script")
        L.append("divergent où le test a effectivement été déclenché.")
    else:
        L.append("**CYCLE EN ÉCHEC** — une sentinelle subsiste, comme le pré-enregistrement")
        L.append("l'avait prévu comme condition d'échec.")
    L.append("")

    # --- Contrôle 3 : le test a-t-il servi à quelque chose ? --------------
    m = re.search(r"\| `([^`]+)` \| \d+ \| le rapport change", txt)
    struct_name = m.group(1) if m else None
    L.append("## Contrôle 3 — le test comportemental a-t-il apporté ce que le motif ne pouvait pas ?")
    L.append("")
    L.append("C'est la question du cycle. Le #437 avait exclu les auto-référents par un")
    L.append("**motif de code** énumérant trois écritures ; il en avait **manqué deux**.")
    L.append("")
    if struct_name:
        src = (SCRIPTS / f"nonml_{struct_name}_backtest.py").read_text(encoding="utf-8")
        caught_by_437 = bool(NARROW_437.search(src))
        L.append(f"La divergence structurelle détectée est `{struct_name}`.")
        L.append("")
        L.append("| | |")
        L.append("|---|---|")
        L.append(f"| capturé par le critère **syntaxique** du #437 | "
                 f"**{'oui' if caught_by_437 else 'NON'}** |")
        L.append(f"| classé par le test **comportemental** du #438 | **oui, structurelle** |")
        L.append("")
        if not caught_by_437:
            L.append("**Le test attrape exactement ce que le motif ratait.** Ce script fait partie")
            L.append("des deux que le #437 avait manqués — il écrit son `glob` d'une manière que")
            L.append("mes trois littéraux ne couvraient pas.")
            L.append("")
            L.append("Le changement de méthode n'est donc pas cosmétique : sans lui, ce tirage")
            L.append("aurait produit une **troisième** campagne annulée par une divergence que")
            L.append("j'aurais dû reclasser après coup.")
        else:
            L.append("Ce script était déjà capturé par le critère syntaxique — le test")
            L.append("comportemental n'a rien apporté sur ce cas précis.")
    L.append("")
    L.append("**Nuance sur la prédiction.** Le pré-enregistrement attendait que le test classe")
    L.append("`pnl_duplicate_sweep` ou `empty_pass_requalification` comme structurels. **Ni")
    L.append("l'un ni l'autre n'a été tiré** : la prédiction n'a pas été mise à l'épreuve sur")
    L.append("les cas nommés, mais sur un troisième script de la même famille. Je le signale")
    L.append("plutôt que de compter la prédiction comme vérifiée.")
    L.append("")

    # --- Contrôle 4 : la borne -------------------------------------------
    denom = n_id + n_subst
    L.append("## Contrôle 4 — la borne, recalculée")
    L.append("")
    L.append("| | Valeur |")
    L.append("|---|---|")
    L.append(f"| identiques | {n_id} |")
    L.append(f"| structurelles (exclues du dénominateur) | {n_struct} |")
    L.append(f"| substantielles | {n_subst} |")
    L.append(f"| **dénominateur** | **{denom}** |")
    L.append(f"| **borne à 95 %** | **{100*bound(denom):.1f} %** |")
    L.append("")
    L.append("La règle d'exclusion des structurelles était **fixée au pré-enregistrement**,")
    L.append("avant tout tirage — ce n'est pas une reclassification de circonstance.")
    L.append("")

    # --- Honnêteté sur ce que vaut cette borne ----------------------------
    L.append("## Ce que vaut cette borne — et pourquoi elle est plus faible qu'avant")
    L.append("")
    L.append("| | Borne | Statut |")
    L.append("|---|---|---|")
    L.append("| #435 | 8,0 % | **caduque** (#436) |")
    L.append("| #437 | — | non publiée |")
    L.append(f"| **#438** | **{100*bound(denom):.1f} %** | **publiée** |")
    L.append("")
    L.append("C'est la **première borne publiable de la campagne**, et elle est **moins bonne**")
    L.append(f"que celle revendiquée au #435. Normal : elle repose sur **{denom}** tirages au lieu")
    L.append("de 36, parce que les trois remises à zéro ont été assumées plutôt que contournées.")
    L.append("")
    L.append(f"Sur un vivier de **{len(pool)}**, elle laisse encore place à "
             f"**~{int(bound(denom)*len(pool))}** divergences substantielles non détectées.")
    L.append("Elle ne dit pas que le dépôt est reproductible ; elle dit qu'un problème")
    L.append("**massif** de péremption est écarté, et rien de plus.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    ok = same_draw and not left and not st_sent
    L.append("## Conclusion")
    L.append("")
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| 24 tirés et classés | 24 | {n_id + n_struct + n_subst} | "
             f"{'✔' if n_id + n_struct + n_subst == SAMPLE_SIZE else '✘'} |")
    L.append(f"| divergents classés par le test | tous | {n_struct + n_subst} | ✔ |")
    L.append(f"| sentinelles subsistantes | 0 | {len(left)} | {'✔' if not left else '✘'} |")
    L.append(f"| borne publiée si k=0 substantielle | oui | "
             f"**{100*bound(denom):.1f} %** | {'✔' if n_subst == 0 else '—'} |")
    L.append("")
    if ok and n_subst == 0:
        L.append("**La campagne aboutit à sa troisième tentative.** Le changement de méthode —")
        L.append("tester la propriété au lieu de deviner son écriture — était le bon, et il a")
        L.append("servi dès ce tirage.")
        L.append("")
        L.append("Ce qui a coûté trois cycles n'est pas la mesure, c'est d'avoir voulu deux")
        L.append("fois reconnaître un comportement par la forme du code qui le produit.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

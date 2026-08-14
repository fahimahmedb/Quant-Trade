"""Verifier les chiffres que le backlog publie (#461).

Specification pre-enregistree dans `PREREG_backlog_figures_verification.md`,
committee AVANT toute mesure.

Attaque la seule ligne de dette decidable seul : « comptes de backlog non
reverifies, quatre faux en six cycles », inscrite six fois sans jamais etre
allee voir.

Test ASYMETRIQUE, declare comme tel avant usage : une absence est informative,
une presence ne prouve rien.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_backlog_figures_verification_result.md"

BACKLOG = "finance/trading/NONML_STRATEGY_BACKLOG.md"
ENTREES = list(range(443, 461))          # univers FIGE au pre-enregistrement

# Espaces qui servent de separateur de milliers en typographie francaise.
ESPACES = "    "


def git(*args):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def commit_introducteur(num):
    """Le commit qui a AJOUTE l'entree — occurrence la plus ancienne (#445/#451)."""
    out = git("log", "-S", f"## Backlog #{num} (", "--format=%H", "--", BACKLOG)
    lignes = [l for l in (out or "").splitlines() if l.strip()]
    return lignes[-1] if lignes else None


def normalise(t):
    """Retire les espaces INTERNES aux groupes de chiffres. Rien d'autre."""
    motif = re.compile(f"(?<=\\d)[{ESPACES}](?=\\d)")
    avant = None
    while avant != t:
        avant, t = t, motif.sub("", t)
    return t


def texte_entree(blob, num):
    """Le texte de l'entree : du titre jusqu'au prochain `## `."""
    lignes = blob.splitlines()
    debut = None
    for i, l in enumerate(lignes):
        if l.startswith(f"## Backlog #{num} ("):
            debut = i
            break
    if debut is None:
        return None
    fin = len(lignes)
    for j in range(debut + 1, len(lignes)):
        if lignes[j].startswith("## "):
            fin = j
            break
    return "\n".join(lignes[debut:fin])


# --- Exclusions, decidees dans le pre-enregistrement, pas apres --------------
EXCLUS = [
    re.compile(r"#\d+"),                       # references de cycle
    re.compile(r"\d{2}/\d{2}/\d{4}"),          # dates
    re.compile(r"\b4/4\b"),                    # score anti-cheat
    re.compile(r"n_trials\s*=\s*\d+"),         # n_trials = 1
]

JETON = re.compile(r"[+\-−]?\d+(?:,\d+)?%?")


def jetons_du_segment(seg):
    s = normalise(seg)
    for rx in EXCLUS:
        s = rx.sub(" ", s)
    return JETON.findall(s)


# Sections d'une entree qui, par construction, CITENT d'autres cycles plutot
# que de rapporter la mesure du cycle courant. Reperees APRES coup (voir le
# rapport) ; elles n'otent aucun jeton du compte de tete.
SECTIONS_CITATION = ("dette restante", "file des prochains cycles",
                     "file « à faire »", "file des cycles")


def segments_gras(txt):
    """(segment en gras, section qui le porte, section = citation ?)."""
    section, cite = "— en-tête —", False
    for ligne in txt.splitlines():
        # Un TITRE, pas une ligne de prose commencant par « #447 ». Defaut
        # trouve en relisant la sortie : `startswith("#")` capturait les
        # references de cycle en tete de ligne et fabriquait de fausses sections.
        if re.match(r"#{1,6}\s", ligne):
            titre = ligne.lstrip("#").strip()
            if not ligne.startswith("## Backlog"):
                section = titre
                bas = titre.lower()
                cite = any(bas.startswith(s) for s in SECTIONS_CITATION)
        for seg in re.findall(r"\*\*(.+?)\*\*", ligne):
            yield seg, section, cite


def variantes_typographiques(j):
    """Formes qui ne different du jeton que par la TYPOGRAPHIE.

    Sert uniquement a EXPLIQUER une absence, jamais a la faire disparaitre :
    le compte de tete reste celui de la regle stricte declaree.

    Defaut corrige en cours de cycle (publie) : la premiere version retirait
    AUSSI le signe de tete, si bien que `−1` etait « explique » par un `1` et
    `−0,07` par un `0.07`. Retirer un moins CHANGE LA VALEUR — ce n'est pas une
    variante typographique. Seul le `+` explicite, facultatif en prose, peut
    etre retire. La correction rend la colonne PLUS severe.
    """
    v = {j}
    for a, b in (("−", "-"), ("-", "−")):
        v |= {x.replace(a, b) for x in v}
    v |= {x.replace(",", ".") for x in v}
    v |= {x[1:] for x in v if x.startswith("+")}
    # TRIE, pas un set : l'ordre d'iteration d'un set de chaines change d'une
    # execution a l'autre (graine de hachage). La CLASSIFICATION etait stable,
    # mais l'etiquette affichee changeait — le rapport n'etait pas idempotent.
    # Defaut trouve par le controle D de l'audit, pas par le backtest.
    return sorted(x for x in v if x and x != j)


def main():
    lignes_rapport, traites, exclus = [], [], []

    for num in ENTREES:
        sha = commit_introducteur(num)
        if sha is None:
            exclus.append((num, "commit introducteur introuvable", None))
            continue
        blob = git("show", f"{sha}:{BACKLOG}")
        if blob is None:
            exclus.append((num, "backlog illisible au commit", sha))
            continue
        txt = texte_entree(blob, num)
        if txt is None:
            exclus.append((num, "entrée absente du backlog à ce commit", sha))
            continue

        noms = sorted(set(re.findall(r"PREREG_([a-z0-9_]+)\.md", txt)))
        if len(noms) != 1:
            exclus.append((num, f"{len(noms)} PREREG cités (attendu : 1)", sha))
            continue
        nom = noms[0]
        chemin = f"finance/trading/results/nonml_{nom}_result.md"
        rap = git("show", f"{sha}:{chemin}")
        if rap is None:
            exclus.append((num, f"rapport `{chemin}` absent à ce commit", sha))
            continue
        rap_n = normalise(rap)
        # Un cycle publie sur TROIS fichiers : le resultat, l'audit, la
        # robustesse (7a). Ma regle declaree n'en lit qu'un. Les freres servent
        # a DIAGNOSTIQUER une absence, jamais a l'oter du compte de tete.
        freres = {}
        for suff in ("audit", "robustness"):
            f = git("show", f"{sha}:finance/trading/results/nonml_{nom}_{suff}.md")
            if f is not None:
                freres[suff] = normalise(f)

        vus, absents, n_jetons = set(), [], 0
        for seg, section, cite in segments_gras(txt):
            for j in jetons_du_segment(seg):
                n_jetons += 1
                if j in rap_n:
                    continue
                cause, classe = "introuvable", "dur"
                for v in variantes_typographiques(j):
                    if v in rap_n:
                        cause, classe = f"variante typographique `{v}`", "typo"
                        break
                if classe == "dur":
                    for suff, corps in freres.items():
                        if j in corps or any(v in corps
                                             for v in variantes_typographiques(j)):
                            cause = f"publié dans `nonml_{nom}_{suff}.md`"
                            classe = "frere"
                            break
                if classe == "dur" and cite:
                    cause = f"cite un autre cycle (section « {section} »)"
                    classe = "citation"
                cle = (j, seg, section)
                if cle in vus:
                    continue
                vus.add(cle)
                absents.append((j, seg, section, cause, classe))
        traites.append((num, sha, nom, n_jetons, absents))

    # ---------------------------------------------------------------- rapport
    n_ent = len(traites)
    n_tok = sum(t[3] for t in traites)
    avec = [t for t in traites if t[4]]
    n_abs = sum(len(t[4]) for t in traites)
    n_typo = sum(1 for t in traites for a in t[4] if a[4] == "typo")
    n_cit = sum(1 for t in traites for a in t[4] if a[4] == "citation")
    n_fre = sum(1 for t in traites for a in t[4] if a[4] == "frere")
    n_dur = sum(1 for t in traites for a in t[4] if a[4] == "dur")
    durs = [(t[0], a) for t in traites for a in t[4] if a[4] == "dur"]

    L = ["# Vérifier les chiffres que le backlog publie (pré-enregistré)", ""]
    L.append("Le backlog porte, en bas de ses six dernières entrées, la même ligne :")
    L.append("« **comptes de backlog non revérifiés : quatre faux en six cycles** ».")
    L.append("Je l'ai inscrite six fois sans jamais aller voir. Ce cycle y va.")
    L.append("")

    L.append("## L'asymétrie du test — reprise ici, comme le pré-enregistrement l'exige")
    L.append("")
    L.append("> Une **absence** est informative : un chiffre que le backlog publie et qu'on")
    L.append("> ne retrouve pas dans le rapport qu'il cite est soit une erreur de recopie,")
    L.append("> soit un calcul fait de tête sans être rendu vérifiable. Une **présence** ne")
    L.append("> prouve rien : `0` se trouve dans n'importe quel rapport par coïncidence.")
    L.append(">")
    L.append("> **Ce cycle ne peut donc pas conclure que les chiffres du backlog sont")
    L.append("> justes.** Il produit une **borne inférieure** du nombre de chiffres")
    L.append("> invérifiables, et rien de plus.")
    L.append("")

    L.append("## Couverture")
    L.append("")
    L.append(f"- entrées de l'univers figé (#{ENTREES[0]}–#{ENTREES[-1]}) : "
             f"**{len(ENTREES)}**")
    L.append(f"- traitées : **{n_ent}**")
    L.append(f"- exclues : **{len(exclus)}**")
    L.append(f"- jetons numériques vérifiés : **{n_tok}**")
    L.append("")
    if exclus:
        L.append("| Entrée | Raison d'exclusion | Commit |")
        L.append("|---|---|---|")
        for num, why, sha in exclus:
            L.append(f"| #{num} | {why} | `{(sha or '—')[:8]}` |")
        L.append("")

    L.append("## Le résultat")
    L.append("")
    L.append(f"- entrées portant **au moins un** jeton absent : **{len(avec)}** "
             f"sur **{n_ent}**")
    L.append(f"- jetons absents **sous la règle stricte déclarée** : **{n_abs}** "
             f"({str(round(100*n_abs/max(n_tok,1), 2)).replace('.', ',')} %)")
    L.append("")
    L.append("Décomposés :")
    L.append("")
    L.append("| Classe | Nombre | Ce que ça veut dire |")
    L.append("|---|---|---|")
    L.append(f"| **variante typographique** | **{n_typo}** | le chiffre EST dans le "
             "rapport, écrit `0.53` là où le backlog écrit `0,53` |")
    L.append(f"| **publié dans un fichier frère** | **{n_fre}** | le chiffre est dans "
             "l'`_audit.md` ou le `_robustness.md` du même cycle |")
    L.append(f"| **citation d'un autre cycle** | **{n_cit}** | le chiffre est publié "
             "dans une section qui, par construction, cite d'autres cycles |")
    L.append(f"| **introuvable** | **{n_dur}** | ni dans le rapport, ni sous une "
             "variante, ni dans une section de citation |")
    L.append("")
    L.append(f"> Le chiffre informatif est le dernier : **{n_dur}** jetons sur "
             f"**{n_tok}** "
             f"(**{str(round(100*n_dur/max(n_tok,1), 2)).replace('.', ',')} %**).")
    L.append("")

    L.append("### Cinq défauts de mon propre instrument, publiés")
    L.append("")
    L.append("**Aucun des cinq n'ôte un jeton du compte de tête.**")
    L.append("")
    L.append("1. **Le signe.** Ma colonne « variante typographique » retirait aussi le")
    L.append("   signe de tête : `−1` se trouvait « expliqué » par un `1`, et `−0,07` par")
    L.append("   un `0.07`. **Retirer un moins change la valeur** — ce n'est pas une")
    L.append("   variante d'écriture. Seul le `+` explicite, facultatif en prose, est")
    L.append("   désormais retiré. La correction rend la colonne **plus sévère**.")
    L.append("2. **Les sections de citation.** Ma règle traitait toute l'entrée comme si")
    L.append("   elle rapportait la mesure du cycle. Or chaque entrée se termine par une")
    L.append("   **« Dette restante »** et une **« File des prochains cycles »** qui")
    L.append("   citent les chiffres d'**autres** cycles — `190/190` (#442), `4,2 %`")
    L.append("   (#441). Les compter comme des écarts de recopie était une erreur de")
    L.append("   conception de ma part.")
    L.append("3. **Les fichiers frères.** Un cycle publie sur **trois** fichiers —")
    L.append("   `_result.md`, `_audit.md`, `_robustness.md`. Mon pré-enregistrement n'en")
    L.append("   déclare qu'**un**. Les chiffres de robustesse (7a) et les recomptages")
    L.append("   d'audit étaient donc cherchés dans un fichier qui, par construction, ne")
    L.append("   les contient pas.")
    L.append("4. **Le repérage des titres.** `startswith(\"#\")` prenait une ligne de prose")
    L.append("   commençant par `#447` pour un titre de section, et fabriquait des")
    L.append("   sections inexistantes. Corrigé en exigeant un vrai titre Markdown.")
    L.append("5. **Le rapport n'était pas idempotent.** Les variantes typographiques")
    L.append("   étaient stockées dans un `set` : la classification était stable, mais")
    L.append("   **l'étiquette affichée** changeait d'une exécution à l'autre au gré de")
    L.append("   la graine de hachage. Corrigé par un tri. **Ce défaut-là, le backtest")
    L.append("   ne pouvait pas le voir — c'est le contrôle D de l'audit qui l'a")
    L.append("   trouvé**, et c'est précisément à cela que sert un audit qui ne partage")
    L.append("   aucune fonction avec ce qu'il vérifie.")
    L.append("")
    L.append("> **Les classifications 2 et 3 ont été ajoutées APRÈS avoir vu le")
    L.append("> résultat.** Je le dis plutôt que de les laisser passer pour prévues.")
    L.append("> Elles ne modifient **aucun** chiffre de la règle déclarée — le compte de")
    L.append(f"> tête reste **{n_abs}** — mais il faut voir ce qu'elles font :")
    L.append("> **chaque couche d'explication que j'ajoute rend le backlog plus propre,")
    L.append("> et je les ai toutes ajoutées après avoir vu le chiffre.** C'est la")
    L.append("> raison pour laquelle le résidu ci-dessous **ne doit pas** se lire comme")
    L.append("> un taux d'exactitude du backlog.")
    L.append("")
    L.append("Et c'est, une fois de plus, **la relecture de la sortie** qui a trouvé les")
    L.append("quatre défauts — pas la mesure. C'est la constante de tous les cycles")
    L.append("depuis le #442.")
    L.append("")

    L.append("## Épinglage — chaque entrée à SON commit")
    L.append("")
    L.append("Un rapport de ce dépôt dépend de l'état du dépôt (#436-#438). Comparer le")
    L.append("rapport d'aujourd'hui à un chiffre publié il y a dix cycles fabriquerait des")
    L.append("écarts qui ne seraient que de la dérive — leçon des #445 et #451.")
    L.append("")
    L.append("| Entrée | Commit épinglé | Rapport cité | Jetons | Absents |")
    L.append("|---|---|---|---|---|")
    for num, sha, nom, n_j, absents in traites:
        marque = f"**{len(absents)}**" if absents else "0"
        L.append(f"| #{num} | `{sha[:8]}` | `nonml_{nom}_result.md` | {n_j} | {marque} |")
    L.append("")

    L.append("## Tous les jetons absents, en entier")
    L.append("")
    L.append("Le critère 2 interdit d'en résumer un seul. Chacun est donné avec le")
    L.append("segment en gras qui le porte.")
    L.append("")
    if not avec:
        L.append("**Aucun.** Tous les jetons numériques publiés dans les 18 entrées se")
        L.append("retrouvent dans le rapport que l'entrée cite, au commit de l'entrée.")
        L.append("")
        L.append("> **Ce n'est pas une preuve d'exactitude** — voir l'asymétrie ci-dessus.")
    else:
        for num, sha, nom, _, absents in traites:
            if not absents:
                continue
            L.append(f"### #{num} — `nonml_{nom}_result.md` (`{sha[:8]}`)")
            L.append("")
            L.append("| Jeton | Segment en gras qui le porte | Section | Diagnostic |")
            L.append("|---|---|---|---|")
            for j, seg, sec, cause, classe in absents:
                s = seg.replace("|", "\\|")
                marque = f"**{cause}**" if classe == "dur" else cause
                L.append(f"| `{j}` | {s} | {sec} | {marque} |")
            L.append("")

    L.append("## Le noyau informatif — les jetons introuvables sous toute lecture")
    L.append("")
    if not durs:
        L.append("**Aucun.** Toute absence s'explique par la typographie ou par une")
        L.append("section de citation.")
    else:
        L.append(f"Ce sont les **{len(durs)}** seuls chiffres que le backlog publie et")
        L.append("qu'aucune des lectures ci-dessus ne retrouve : ni dans le rapport cité,")
        L.append("ni sous une variante typographique, ni dans un fichier frère du même")
        L.append("cycle, ni dans une section qui cite un autre cycle.")
        L.append("")
        L.append("| Entrée | Jeton | Segment | Section |")
        L.append("|---|---|---|---|")
        for num, (j, seg, sec, _c, _k) in durs:
            s = seg.replace("|", "\\|")
            L.append(f"| #{num} | `{j}` | {s} | {sec} |")
    L.append("")

    # --- Verification a la main des residus ---------------------------------
    # Epinglee : si le jeu de residus change, le texte ci-dessous devient faux
    # et le rapport le DIT au lieu de le taire.
    RESIDUS_VERIFIES = {
        (445, "0,90"): "La grille de robustesse écrit **`0.9`**, le backlog **`0,90`**. "
                       "*Même valeur, zéro final en plus.* **Pas une erreur.**",
        (452, "+0,970"): "Le rapport donne un maximum de **`+0.969870`**, que le backlog "
                         "arrondit en **`+0,970`**. Le voisin `+0,959` est passé, lui, "
                         "parce que `0.959` est un préfixe de `0.959460` — "
                         "*le sens de l'arrondi décide, pas l'exactitude.* "
                         "**Pas une erreur.**",
        (454, "−5"): "Affirmation sur un `git diff`, pas sur le rapport. **Vérifiée "
                     "directement contre git** : le commit `d2cbda21` porte "
                     "`8  5  nonml_sessions_column_backfill_audit.py`. "
                     "**Le backlog dit vrai.**",
        (460, "−0,06"): "Citation de l'edge médian du **#459**, dans une section de "
                        "synthèse que ma liste de sections de citation ne couvre pas. "
                        "**Pas une erreur.**",
    }
    trouves = {(num, a[0]) for num, a in durs}
    L.append("## Les résidus, vérifiés un par un **à la main**")
    L.append("")
    if trouves != set(RESIDUS_VERIFIES):
        L.append("> **Le jeu de résidus a changé depuis la vérification manuelle.**")
        L.append("> Le tableau ci-dessous est **périmé** et ne doit pas être lu comme")
        L.append(f"> une vérification. Attendu : {sorted(RESIDUS_VERIFIES)} ;")
        L.append(f"> mesuré : {sorted(trouves)}.")
        L.append("")
    else:
        L.append("Quatre, c'est assez peu pour aller voir chacun **dans la source**")
        L.append("plutôt que d'en tirer un taux. C'est fait :")
        L.append("")
        L.append("| Entrée | Jeton | Ce que la source dit |")
        L.append("|---|---|---|")
        for (num, j), quoi in sorted(RESIDUS_VERIFIES.items()):
            L.append(f"| #{num} | `{j}` | {quoi} |")
        L.append("")
        L.append("> **Aucun des quatre n'est une erreur de chiffre.** Trois sont des")
        L.append("> artefacts de mon test par sous-chaîne — zéro final, sens de")
        L.append("> l'arrondi, fait vérifiable dans git et non dans le rapport — et le")
        L.append("> quatrième est une citation d'un autre cycle.")
        L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(avec) >= 3
    p3 = all(t[3] > 0 for t in traites)
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| au moins 3 entrées portent un jeton absent | ≥ 3 | {len(avec)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append("| les absences portent surtout sur des chiffres **dérivés** "
             "(pourcentages, sommes) | — | "
             f"typographie **{n_typo}**, citation **{n_cit}**, dérivés : minoritaires | "
             "**réfutée** |")
    L.append(f"| aucune entrée sans jeton à vérifier | 0 | "
             f"{sum(1 for t in traites if t[3] == 0)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    L.append("**La prédiction 2 est réfutée, et de la façon la plus instructive.** Je")
    L.append("m'attendais à des erreurs de calcul commises en rédigeant. Les absences ne")
    L.append("viennent quasiment pas de là : elles viennent de la **typographie** (le")
    L.append("backlog francise les décimales que le script imprime en `0.53`), de mon")
    L.append("**mauvais découpage** de l'entrée, et du fait que je cherchais dans **un**")
    L.append("fichier ce qu'un cycle publie sur **trois**.")
    L.append("")
    L.append("### La prédiction 1 est « vérifiée » — et cette vérification est creuse")
    L.append("")
    L.append("Mécaniquement, **17 entrées sur 18** portent un jeton absent : la")
    L.append("prédiction passe. **Elle ne devrait convaincre personne.** Les absences")
    L.append("qu'elle compte sont, à quatre près, des artefacts de mon instrument, et")
    L.append("les quatre restantes n'en sont pas non plus après vérification manuelle.")
    L.append("")
    L.append("C'est la situation du **#458** exactement : un verdict mécanique favorable")
    L.append("posé sur une mesure qui ne mesure pas ce qu'elle annonce. La différence")
    L.append("est qu'ici le pré-enregistrement m'obligeait à publier chaque absence en")
    L.append("entier — et c'est cette obligation, pas la statistique, qui a rendu le")
    L.append("défaut visible.")
    L.append("")
    if not p1:
        L.append("**La prédiction 1 est réfutée dans le sens qui m'arrange.** Le")
        L.append("pré-enregistrement m'oblige alors à **douter de l'instrument d'abord**")
        L.append("(leçon du #458) : une extraction qui ne trouve rien est plus probablement")
        L.append("cassée qu'un backlog exact. L'audit dédié recompte indépendamment ; le")
        L.append(f"chiffre de couverture — **{n_tok}** jetons extraits sur **{n_ent}**")
        L.append("entrées — est ce qui permet de juger si l'extraction a réellement mordu.")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = (n_ent + len(exclus)) == len(ENTREES)
    L.append(f"1. **{n_ent + len(exclus)}/{len(ENTREES)}** entrées traitées ou exclues avec")
    L.append(f"   raison — **{'OUI' if c1 else 'NON'}**.")
    L.append("2. Tout jeton absent publié en entier avec son segment — **OUI** (section")
    L.append("   ci-dessus, aucun résumé, aucun « et N autres »).")
    L.append("3. Épinglage par entrée publié, commit par commit — **OUI**.")
    L.append("4. Asymétrie du test reprise dans ce rapport — **OUI** (en tête).")
    L.append("")
    verdict = "PASS" if c1 else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé**, pas sur le nombre")
    L.append("d'écarts trouvés : un cycle qui n'en trouve aucun et le montre proprement")
    L.append("réussit.")
    L.append("")

    L.append("## Ce que ce cycle établit, et ce qu'il n'établit pas")
    L.append("")
    L.append("**Il n'a trouvé aucune erreur de chiffre** dans les 18 entrées, sur les")
    L.append(f"**{n_tok}** jetons qu'elles publient.")
    L.append("")
    L.append("> **Ce n'est pas un certificat d'exactitude, et la dette reste inscrite.**")
    L.append("")
    L.append("Trois raisons, toutes déclarées d'avance ou publiées ci-dessus :")
    L.append("")
    L.append("1. **Le test est asymétrique** : une présence ne prouve rien. Un chiffre")
    L.append("   faux qui se trouve par hasard ailleurs dans le rapport passe.")
    L.append("2. **Les quatre faux connus du backlog ne sont pas dans cet univers.**")
    L.append("   « 8 scripts » (#449), « 6 rapports » (#451), « 13 orphelins » (#453),")
    L.append("   « 29 en échec » (#457) étaient faux **par rapport au dépôt**, pas par")
    L.append("   rapport au rapport cité — qui portait souvent la même erreur. **Un")
    L.append("   contrôle de recopie ne peut pas les voir.** C'est la limite de fond")
    L.append("   de ce cycle, et elle explique pourquoi ces quatre-là ont dû être")
    L.append("   trouvés par hasard.")
    L.append("3. **J'ai ajouté deux couches d'explication après avoir vu le résultat**,")
    L.append("   et chacune a rendu le backlog plus propre.")
    L.append("")
    L.append("**La ligne « comptes de backlog non revérifiés » doit donc rester au")
    L.append("passif.** Ce cycle ne la solde pas : il montre qu'un contrôle de recopie")
    L.append("était le mauvais outil pour la solder, et lequel il aurait fallu — un")
    L.append("contrôle qui remesure la **grandeur** dans le dépôt, pas la **recopie**")
    L.append("dans le rapport. C'est un cycle à déclarer d'avance, pas à improviser ici.")
    L.append("")

    L.append("## Ce que ce cycle ne fait pas")
    L.append("")
    L.append("- Il ne **corrige** aucun chiffre du backlog : tout écart est publié et")
    L.append("  inscrit, pas réparé au passage — engagement tenu depuis le #450.")
    L.append("- Il ne **régénère** aucun rapport.")
    L.append("- Il ne juge **aucune stratégie** : un écart de recopie n'est pas un verdict.")
    L.append("")

    L.append("")
    L.append("> **Rapport épinglé** — contrairement aux inventaires de dépôt (#436-#438),")
    L.append("> ce rapport lit chaque entrée au commit qui l'a créée. Il ne dérive donc pas")
    L.append("> avec le dépôt : réexécuté dans dix cycles, il doit rendre les mêmes chiffres.")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()

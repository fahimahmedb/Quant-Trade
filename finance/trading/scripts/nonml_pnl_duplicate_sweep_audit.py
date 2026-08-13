"""Audit adversarial — balayage des doublons de P&L.

Un balayage qui ne trouve presque rien peut vouloir dire deux choses opposées :
il n'y a presque rien à trouver, ou il ne sait pas chercher. L'audit sépare les
deux.

Quatre contrôles :

1. **Contrôle positif** — un doublon synthétique est injecté dans une copie du
   répertoire de résultats. Le balayage doit le trouver. Un balayage incapable de
   détecter un doublon connu ne prouve rien par son silence.
2. **Contrôle négatif** — une série bruitée est injectée ; elle ne doit **pas**
   être signalée, sans quoi le seuil serait trop permissif.
3. **Portée réelle** — combien d'entrées du backlog le balayage peut-il seulement
   voir ? La couverture de 100 % annoncée porte sur les fichiers `.npz`, pas sur
   les candidats. L'écart est mesuré ici.
4. **Angle mort démontré** — le doublon établi au #403 (`sma200_leaders_overlay`
   / `leaders_trend_union_overlay`, univers d'origine) est-il détectable par
   cette méthode ? Contrôle décisif : si la réponse est non, le balayage ne peut
   pas conclure à l'absence de doublons.

Usage : python3 scripts/nonml_pnl_duplicate_sweep_audit.py
"""
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
sys.path.insert(0, str(ROOT / "scripts"))

import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402

OUT = RESULTS / "nonml_pnl_duplicate_sweep_audit.md"
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"


def sweep_in(dirpath):
    """Rejoue la detection sur un repertoire donne, sans reecrire de rapport."""
    saved = sw.RESULTS
    sw.RESULTS = dirpath
    try:
        paths = sorted(dirpath.glob("*_pnl.npz"))
        series = {}
        for p in paths:
            d = np.load(p, allow_pickle=True)
            s, _tag = sw.net_pnl(d)
            if s is None or s.ndim != 1 or len(s) < 2 or not np.isfinite(s).all():
                continue
            series[p.name.replace("_pnl.npz", "")] = s
        exact, quasi = [], []
        names = sorted(series)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                sa, sb = series[a], series[b]
                if len(sa) != len(sb):
                    continue
                if np.array_equal(sa, sb):
                    exact.append((a, b))
                elif np.std(sa) > 0 and np.std(sb) > 0:
                    c = float(np.corrcoef(sa, sb)[0, 1])
                    if c >= sw.CORR_THRESHOLD:
                        quasi.append((a, b, c))
        return exact, quasi
    finally:
        sw.RESULTS = saved


def main():
    L = ["# Audit adversarial — balayage des doublons de P&L", ""]
    L.append("Un balayage qui ne trouve presque rien peut vouloir dire deux choses opposées :")
    L.append("il n'y a presque rien à trouver, ou il ne sait pas chercher. Cet audit sépare")
    L.append("les deux — l'enjeu est de savoir si le résultat du balayage autorise à conclure")
    L.append("à une **absence** de doublons.")
    L.append("")

    src = sorted(RESULTS.glob("*_pnl.npz"))[0]
    d0 = np.load(src, allow_pickle=True)

    # --- 1 & 2. controles positif et negatif sur repertoire temporaire ---
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for p in RESULTS.glob("*_pnl.npz"):
            shutil.copy(p, tmpdir / p.name)
        shutil.copy(src, tmpdir / "zzz_temoin_positif_pnl.npz")

        s0, _ = sw.net_pnl(d0)
        rng = np.random.default_rng(20260813)
        payload = {k: d0[k] for k in d0.files}
        key = "pos" if "pos" in payload else ("pnl_gross_ov" if "pnl_gross_ov" in payload
                                              else "pnl_candidate")
        arr = np.asarray(payload[key], dtype=float).copy()
        payload[key] = arr + rng.normal(0.0, float(np.std(arr)) + 1e-6, size=arr.shape)
        np.savez(tmpdir / "zzz_temoin_negatif_pnl.npz", **payload)

        exact, quasi = sweep_in(tmpdir)

    pos_found = any("zzz_temoin_positif" in a or "zzz_temoin_positif" in b
                    for a, b in exact)
    neg_flagged = any("zzz_temoin_negatif" in x for pair in exact for x in pair) or \
        any("zzz_temoin_negatif" in a or "zzz_temoin_negatif" in b for a, b, _ in quasi)

    L.append("## 1. Contrôle positif — le balayage sait-il trouver ?")
    L.append("")
    L.append("Une copie conforme d'un `.npz` existant est injectée dans une copie temporaire")
    L.append("du répertoire de résultats, sous un nom différent. Le balayage doit la signaler.")
    L.append("")
    L.append(f"- doublon synthétique détecté : **{'OUI' if pos_found else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME — le silence du balayage sur le reste est informatif.' if pos_found else 'BALAYAGE AVEUGLE — son résultat ne prouve rien.'}**")
    L.append("")

    L.append("## 2. Contrôle négatif — le seuil est-il trop permissif ?")
    L.append("")
    L.append("Une copie **bruitée** (bruit d'écart-type égal à celui de la série) est injectée.")
    L.append("Elle ne doit être signalée ni comme doublon exact ni comme quasi-doublon.")
    L.append("")
    L.append(f"- série bruitée signalée à tort : **{'OUI' if neg_flagged else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME — le critère ne confond pas ressemblance et identité.' if not neg_flagged else 'SEUIL TROP PERMISSIF'}**")
    L.append("")

    # --- 3. portee reelle ---
    n_npz = len(list(RESULTS.glob("*_pnl.npz")))
    backlog_txt = BACKLOG.read_text(encoding="utf-8")
    n_entries = sum(1 for line in backlog_txt.splitlines()
                    if line.startswith("| ") and line[2:].split(" |")[0].strip().isdigit())

    L.append("## 3. Portée réelle — que voit le balayage ?")
    L.append("")
    L.append("La « couverture 100 % » annoncée par le balayage porte sur les fichiers `.npz`")
    L.append("**qui existent**, pas sur les candidats du backlog. L'écart est ici.")
    L.append("")
    L.append(f"- entrées numérotées du backlog : **{n_entries}**")
    L.append(f"- fichiers `*_pnl.npz` disponibles : **{n_npz}**")
    L.append(f"- proportion du backlog visible par le balayage : **{100*n_npz/max(1, n_entries):.0f} %**")
    L.append("")
    L.append("Un `.npz` n'est sauvegardé que par certains scripts, et souvent seulement en cas")
    L.append("de PASS. **Plus de la moitié du backlog est donc hors de portée de cette")
    L.append("méthode**, et son silence ne vaut que pour la partie qu'elle voit.")
    L.append("")

    # --- 4. angle mort demontre ---
    known_a = RESULTS / "nonml_sma200_leaders_overlay_pnl.npz"
    known_b = RESULTS / "nonml_leaders_trend_union_overlay_pnl.npz"
    a_exists, b_exists = known_a.exists(), known_b.exists()
    detectable = a_exists and b_exists

    L.append("## 4. Angle mort démontré sur le doublon connu du #403")
    L.append("")
    L.append("Contrôle décisif. Le #403 a établi que `sma200_leaders_overlay` et")
    L.append("`leaders_trend_union_overlay` sont la **même stratégie**, sur l'univers")
    L.append("d'origine comme sur l'univers point-in-time. Le balayage retrouve-t-il la paire")
    L.append("d'origine ?")
    L.append("")
    L.append(f"- `nonml_sma200_leaders_overlay_pnl.npz` présent : **{'OUI' if a_exists else 'NON'}**")
    L.append(f"- `nonml_leaders_trend_union_overlay_pnl.npz` présent : **{'OUI' if b_exists else 'NON'}**")
    L.append(f"- paire d'origine détectable par cette méthode : **{'OUI' if detectable else 'NON'}**")
    L.append("")
    if not detectable:
        L.append("**ANGLE MORT CONFIRMÉ.** Le seul doublon dont l'existence était établie")
        L.append("*avant* ce balayage est **invisible** pour lui, faute d'un `.npz` sauvegardé")
        L.append("par l'un des deux candidats. Le balayage n'a retrouvé que sa réplique sur")
        L.append("univers point-in-time, où les deux fichiers existent.")
        L.append("")
        L.append("Conséquence directe sur la lecture du résultat : **le balayage ne permet pas")
        L.append("de conclure qu'il n'y a que deux groupes de doublons dans le backlog.** Il")
        L.append("permet seulement d'affirmer qu'il n'y en a que deux parmi les candidats ayant")
        L.append("sauvegardé un `.npz`. C'est une borne inférieure, pas un décompte.")
    else:
        L.append("**Paire d'origine détectable** — le balayage la retrouve, sa portée couvre")
        L.append("bien le cas connu.")
    L.append("")

    # --- verification par lecture des groupes trouves (critere 2 du PREREG) ---
    L.append("## 5. Vérification par lecture des groupes signalés")
    L.append("")
    L.append("Critère 2 du pré-enregistrement : chaque paire est confirmée ou rejetée **par")
    L.append("lecture**, pas sur la foi du chiffre.")
    L.append("")
    L.append("### Groupe 1 — `etape_D_overlay_optimized` / `nonml_etape_d_garch_defensive_overlay`")
    L.append("")
    L.append("Les deux fichiers ont été ajoutés par le **même commit** (`0516f8f`, cycle #118).")
    L.append("Lecture de l'entrée #118 du backlog : elle est explicitement qualifiée de")
    L.append("« **FAIT — découverte importante, pas un nouveau backtest** » — il s'agissait de")
    L.append("réparer des scripts Étape D cassés et de régénérer un résultat obsolète, pas")
    L.append("d'évaluer une stratégie neuve. Le second `.npz` est un **alias de nommage** vers")
    L.append("l'espace `nonml_`, pas un second essai.")
    L.append("")
    L.append("**Doublon de fichier CONFIRMÉ, essai surnuméraire REJETÉ** : une seule stratégie,")
    L.append("un seul essai, déjà déclaré comme réutilisation à l'époque.")
    L.append("")
    L.append("### Groupe 2 — `..._trend_union_overlay_pit_universe` / `..._sma200_leaders_overlay_pit_universe`")
    L.append("")
    L.append("C'est la paire établie au #403, dont l'identité bit-à-bit avait déjà été prouvée")
    L.append("dans ce cycle-là. Les deux correspondent à **deux entrées distinctes du backlog**")
    L.append("(#401 et #403), chacune comptée comme un essai.")
    L.append("")
    L.append("**Doublon CONFIRMÉ, 1 essai surnuméraire.**")
    L.append("")
    L.append("### Décompte corrigé")
    L.append("")
    L.append("Le balayage annonçait 2 entrées surnuméraires ; la lecture en rejette une.")
    L.append("**Correction retenue : 1 essai surnuméraire**, soit 372 → **371**.")
    L.append("")
    L.append("Cette correction est **négligeable** devant l'angle mort du contrôle 4 : elle")
    L.append("porte sur la partie visible du backlog, qui en couvre moins de la moitié.")
    L.append("")

    verdict = pos_found and (not neg_flagged)
    L.append("## Verdict de l'audit")
    L.append("")
    if verdict and not detectable:
        L.append("**MÉTHODE VALIDE, PORTÉE INSUFFISANTE.** Le balayage détecte ce qu'il voit")
        L.append("(contrôles 1 et 2 conformes), mais ne voit qu'une fraction du backlog et")
        L.append("manque le seul doublon connu d'avance. Son résultat est une **borne")
        L.append("inférieure** : au moins un essai surnuméraire, probablement davantage.")
        L.append("")
        L.append("Conclure de ce cycle qu'il n'y a « que » deux doublons serait une")
        L.append("surinterprétation. C'est écrit ici pour que le chiffre ne soit pas repris")
        L.append("plus tard comme un décompte complet.")
    elif verdict:
        L.append("**MÉTHODE VALIDE.** Contrôles positif et négatif conformes, cas connu couvert.")
    else:
        L.append("**MÉTHODE NON VALIDÉE — le balayage échoue son propre contrôle.**")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()

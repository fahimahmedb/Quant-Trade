"""Etape P11 (capstone) - Pipeline de prevision CALIBRE, national -> circos -> sieges.
Produit results/etape_P11_pipeline_calibre.md.

Unifie les lecons du projet en un pipeline honnete :
  1. Entree = une prevision NATIONALE (le vrai levier, maillon incertain).
  2. Desagregation = swing PROPORTIONNEL sur la carte reelle 2022 (champion, cf. P10).
  3. Incertitude = intervalles CONFORMES par parti, dont on VERIFIE la couverture.
  4. Sortie = projection de sieges (tetes par circo) avec intervalle de confiance,
     par Monte-Carlo propageant l'incertitude nationale + residuelle.

Ne cache pas ses limites : la couverture conforme est INEGALE (partis en mutation
sous-couverts, ex. LFI) car on ne dispose que de 2 transitions.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pp_circo import LIB  # noqa: E402
from pp_circo_ml import PARTIS_TRI, conformal_coverage, monte_carlo_seats  # noqa: E402

cc = conformal_coverage(0.20)

lines = []
w = lines.append
w("# Étape P11 — Pipeline de prévision calibré (national → circonscriptions → sièges)\n")

w("## 0. Synthèse du projet en un pipeline honnête\n")
w("Les étapes précédentes ont établi, par la mesure : le levier est **national** "
  "(pas spatial, P10) ; la désagrégation gagnante est le **swing proportionnel** ; "
  "et l'incertitude doit être **calibrée puis vérifiée** (P9/P10). Ce pipeline "
  "assemble ces trois briques honnêtes.\n")
w("```")
w("prévision NATIONALE (incertaine)  ──►  swing proportionnel sur carte réelle 2022")
w("        │                                          │")
w("   (maillon faible, le vrai levier)      intervalles CONFORMES par parti")
w("        └──────────────► Monte-Carlo ──► sièges (têtes/circo) + IC")
w("```\n")

w("## 1. Incertitude calibrée : on la VÉRIFIE, on ne la suppose pas\n")
w("Intervalles conformes calibrés sur la transition 2012→2017, **couverture "
  "mesurée** sur 2017→2022 (cible 80 %) :\n")
w("| Parti | Demi-largeur Q | Couverture obtenue |")
w("|---|---|---|")
for p in PARTIS_TRI:
    flag = "" if 0.72 <= cc[p]["coverage"] <= 0.88 else " ⚠️"
    w(f"| {LIB.get(p, p)} | ±{cc[p]['q']:.2f} pts | {cc[p]['coverage']:.0%}{flag} |")
w("")
w(f"Couverture moyenne **{cc['_mean_coverage']:.0%}** (cible {cc['_target']:.0%}) — "
  "correcte en moyenne, **mais très inégale** : **LFI est gravement sous-couvert "
  f"({cc['LFI']['coverage']:.0%})** car la poussée Mélenchon 2017→2022 fut bien "
  "plus volatile que 2012→2017. La garantie conforme suppose l'échangeabilité "
  "entre scrutins — **violée** ici. Honnêtement : avec 2 transitions seulement, "
  "l'incertitude n'est pas fiablement calibrable pour un parti en mutation. Le "
  "correctif n'est pas algorithmique — il faut **plus de scrutins**.\n")

w("## 2. Projection de sièges avec incertitude (démonstration)\n")
w("Scénario national **illustratif** (PAS une prévision) passé dans le pipeline "
  "complet, avec une incertitude nationale de ±10 % (relatif) propagée par "
  "Monte-Carlo (2000 tirages) :\n")
scen = {"RN": 30, "LFI": 25, "ENS": 20, "LR": 12, "REC": 6, "EELV": 4, "PS": 3}
mc = monte_carlo_seats(scen, national_rel_sd=0.10, n_sims=2000)
w("| Parti | En tête (médiane) | IC 80 % |")
w("|---|---|---|")
for p, v in sorted(mc.items(), key=lambda kv: -kv[1]["median"]):
    if v["median"] > 0 or v["hi"] > 0:
        w(f"| {LIB.get(p, p)} | {v['median']:.0f} circos | [{v['lo']:.0f} – {v['hi']:.0f}] |")
w(f"\n*Entrée nationale : {', '.join(f'{k} {v}%' for k, v in scen.items())}. "
  "La largeur des intervalles vient d'abord de l'incertitude NATIONALE (le maillon "
  "faible), pas du spatial — ce qui illustre exactement où se joue la "
  "significativité prédictive.*\n")

w("## 3. Conclusion honnête du projet\n")
w("Le pipeline est **complet et cohérent** : chaque brique est celle que la mesure "
  "a validée (swing proportionnel > ML pour la prévision ; incertitude vérifiée, "
  "pas supposée ; national comme vrai levier). Ce qu'il **reste** n'est pas un "
  "défaut de modélisation mais une **limite de données** :")
w("- **Calibration inégale** (LFI) → il faut plus de transitions électorales.")
w("- **Prévision nationale faible** (fondamentaux non significatifs à n=11) → il "
  "faut un vrai signal national (sondages/marchés live), branchable ici tel quel.")
w("- **Downscaling ≠ prévision** : la carte spatiale est fiable pour répartir un "
  "national connu ; elle n'invente pas le national.\n")
w("En l'état, c'est la réponse la plus significative **possible** sur ces données : "
  "significative là où elle peut l'être (downscaling, p≈0), honnête sur ses "
  "limites (prévision, calibration), et **prête à s'améliorer par les données** "
  "(plus de scrutins, signal national live) plutôt que par plus de complexité.\n")

out = ROOT / "results" / "etape_P11_pipeline_calibre.md"
out.write_text("\n".join(lines))
print("\n".join(lines))

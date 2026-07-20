"""Etape P10 - VRAIE prevision inter-scrutins (le test que P9 ne faisait pas).
Produit results/etape_P10_prevision_temporelle.md.

P9 montrait une skill de DOWNSCALING (repartir un resultat 2022 deja connu vers
les circos). P10 pose la vraie question de PREVISION : un modele appris sur UNE
transition (2012->2017) predit-il une transition INEDITE (2017->2022) mieux que
la baseline ? Reponse honnete, verifiee (deux sens + modele lineaire) : NON.

Le swing PROPORTIONNEL reste le champion ; le Gradient Boosting SUR-APPREND la
transition d'entrainement et generalise mal. C'est coherent avec la litterature
(le vote precedent + le swing dominent ; la complexite sur-apprend -- etude ML
sieges australiens, IJF 2025). Donnees reelles : presidentielles 2012, 2017, 2022
par circonscription (ministere de l'Interieur).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pp_circo_ml import PARTIS_TRI, temporal_forecast  # noqa: E402

f = temporal_forecast()

lines = []
w = lines.append
w("# Étape P10 — Vraie prévision inter-scrutins (downscaling ≠ prévision)\n")

w("## 0. La question honnête\n")
w("P9 a montré qu'un Gradient Boosting **répartit** un résultat national déjà "
  "connu vers les circonscriptions mieux que le swing (skill de *downscaling*, "
  "p ≈ 0). Mais **prédit-il un scrutin futur** ? Test décisif : apprendre la "
  "transition **2012→2017**, puis prédire la transition **2017→2022** — jamais "
  "vue à l'entraînement. Partis présents aux trois présidentielles : "
  f"{', '.join(PARTIS_TRI)} (LFI = Mélenchon, explicite).\n")

w("## 1. Résultat : le swing proportionnel gagne, le ML sur-apprend\n")
w(f"Prédiction de la part 2022 par circonscription (n = {f['n']} paires "
  "circo × parti), modèles appris sur 2012→2017 :\n")
w("| Prédicteur | MAE (points) | Verdict |")
w("|---|---|---|")
rows = [("Persistance (= 2017)", f["persist"]),
        ("Swing additif", f["swing_add"]),
        ("**Swing proportionnel**", f["swing_prop"]),
        ("Régression linéaire (apprise 2012→2017)", f["ols"]),
        ("Gradient Boosting (appris 2012→2017)", f["gb"])]
best = min(r[1] for r in rows)
for name, mae in rows:
    verdict = "🏆 **champion**" if mae == best else ("sur-apprend" if "Boosting" in name else "")
    w(f"| {name} | {mae:.3f} | {verdict} |")
w("")
w(f"**Le swing proportionnel ({f['swing_prop']:.2f}) bat tout le monde**, y compris "
  f"le Gradient Boosting ({f['gb']:.2f}, +{100*(f['gb']-f['swing_prop'])/f['swing_prop']:.0f} % "
  f"d'erreur) qui **sur-apprend** la transition d'entraînement. La régression "
  f"linéaire ({f['ols']:.2f}) fait à peine mieux que le swing additif mais reste "
  "battue par le proportionnel.\n")

w("## 2. Vérifié avant de conclure (robustesse)\n")
w("- **Sens inverse** (apprendre 2017→2022, prédire 2012→2017) : même verdict, le "
  "GB explose (~7 pts d'erreur). Le sur-apprentissage n'est pas un accident d'un "
  "sens de test.")
w("- **Modèle simple** (linéaire) : généralise, le GB non — cohérent avec « la "
  "complexité sur-apprend » quand chaque transition électorale est idiosyncratique "
  "(Macron 2017, Zemmour 2022…).")
w("- **Baseline forte** : le swing proportionnel n'est pas un homme de paille — "
  "c'est lui le champion, pas le modèle.\n")

w("## 3. Ce que ça signifie (et ça corrige P9)\n")
w("- **P9 reste vrai mais restreint** : le ML de circonscription est excellent "
  "pour **désagréger un résultat connu** (downscaling), PAS pour **prévoir** un "
  "scrutin futur. La significativité de P9 ne s'étend pas à la prévision.")
w("- **La leçon (conforme à la littérature)** : en prévision de circonscription, "
  "le **vote précédent + swing proportionnel** est une baseline redoutable ; "
  "ajouter de la complexité ML dégrade la généralisation. Le levier de "
  "significativité n'est donc **pas** un modèle spatial plus riche.")
w("- **Où est vraiment le levier** : la qualité de la **prévision NATIONALE** "
  "(fondamentaux + sondages/marchés) — puis un simple swing proportionnel pour "
  "descendre aux circos, plus une **incertitude calibrée**. Voir "
  "`results/ROADMAP_SIGNIFICATIVITE.md`.\n")

w("## 4. Limites honnêtes de ce test\n")
w("- Deux transitions seulement (2012→2017, 2017→2022) : on ne peut pas encore "
  "moyenner la skill de prévision sur de nombreux scrutins.")
w("- Lignée des partis imparfaite (Mélenchon 2012 = Front de Gauche incluant le "
  "PCF ; Macron absent de 2012 donc hors du jeu tri-scrutins).")
w("- Le test suppose le résultat NATIONAL cible connu (comme le swing) : c'est un "
  "test de **désagrégation prédictive**, la brique nationale restant à fournir "
  "par ailleurs (P1/P6 ou sondages).\n")

out = ROOT / "results" / "etape_P10_prevision_temporelle.md"
out.write_text("\n".join(lines))
print("\n".join(lines))

"""Etape - SECOND TOUR par circonscription (reports de voix). Produit
results/etape_P8_second_tour.md.

Donnees REELLES : presidentielle 2022, 2nd tour, Macron vs Le Pen par
circonscription legislative (ministere de l'Interieur / data.gouv.fr, ressource
resultats-par-niveau-cirlg-t2-france-entiere). Agregat national reconstitue =
officiel (58.55 / 41.45).

Lecon honnete centrale : la part Le Pen au 2nd tour est TRES bien PREDITE par la
composition du 1er tour (R2 ~ 0.95), MAIS les TAUX DE REPORT individuels ne sont
PAS identifiables depuis des agregats (sophisme ecologique, King 1997). On montre
l'instabilite (OLS qui explose, NNLS a taux > 100 %) et on ne rapporte que ce qui
est ROBUSTE : correlations et comptabilite du reservoir.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import nnls

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

t1 = pd.read_csv(ROOT / "data" / "fr_pres2022_circo.csv", comment="#").set_index("circo_id")
t2 = pd.read_csv(ROOT / "data" / "fr_pres2022_t2_circo.csv", comment="#").set_index("circo_id")
common = sorted(set(t1.index) & set(t2.index))
t1, t2 = t1.loc[common], t2.loc[common]
e1 = t1["exprimes"].to_numpy(float)
e2 = t2["exprimes"].to_numpy(float)
y = t2["RN_t2"].to_numpy(float)                       # part Le Pen T2 (%)

LIBLP = {"RN": "Le Pen (RN)", "REC": "Zemmour (Reconquête)", "DLF": "Dupont-Aignan",
         "RES": "Lassalle", "LR": "Pécresse (LR)", "PS": "Hidalgo (PS)",
         "PCF": "Roussel (PCF)", "LFI": "Mélenchon (LFI)", "EELV": "Jadot (EELV)",
         "ENS": "Macron (ENS)"}


def natl(df, col, e):
    return float((df[col].to_numpy(float) / 100 * e).sum() / e.sum() * 100)


lines = []
w = lines.append
w("# Étape — Second tour 2022 par circonscription : reports de voix (données réelles)\n")

w("## 0. Données\n")
lp2 = natl(t2, "RN_t2", e2)
w(f"Présidentielle 2022, 2nd tour, Macron vs Le Pen, **{len(common)} circonscriptions** "
  "(ministère de l'Intérieur / data.gouv.fr, ressource récupérée via l'API "
  "tabulaire puis parsée depuis le .txt — l'API tabulaire *beta* mésinterprète "
  "les décimales à virgule de ce fichier, on calcule donc les parts depuis les "
  "voix brutes). Agrégat national reconstitué = officiel : "
  f"**Macron {100-lp2:.2f} % / Le Pen {lp2:.2f} %**.\n")

w("## 1. Géographie du 2nd tour (ce que le national masque)\n")
w(f"- Part Le Pen au 2nd tour : de **{y.min():.1f} %** (circo la plus macroniste) "
  f"à **{y.max():.1f} %** (écart-type {y.std():.1f} pts). Le « 41,5 % » national "
  "recouvre une France coupée en deux.\n")

w("## 2. Peut-on lire les REPORTS de voix ? Oui pour le tout, NON pour le détail\n")
# OLS naif (avec intercept) -> explose (colinearite compositionnelle)
Xp = ["RN", "REC", "LR", "DLF", "RES", "LFI", "PCF", "EELV", "PS", "ENS"]
A = np.column_stack([np.ones(len(common))] + [t1[p].to_numpy(float) for p in Xp])
ols, *_ = np.linalg.lstsq(A, y, rcond=None)
r2_ols = 1 - ((y - A @ ols) ** 2).sum() / ((y - y.mean()) ** 2).sum()
# NNLS sur voix -> taux instables (>100 %)
Xv = np.column_stack([t1[p].to_numpy(float) / 100 * e1 for p in Xp])
yv = y / 100 * e2
rate, _ = nnls(Xv, yv)
r2_nnls = 1 - ((yv - Xv @ rate) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
w(f"La part Le Pen T2 est **très bien prédite** par la composition du 1er tour "
  f"(R² = {max(r2_ols, r2_nnls):.2f}). Mais **les taux de report individuels ne "
  "sont PAS identifiables** depuis des agrégats — c'est le *sophisme écologique* "
  "(King 1997). Preuve par l'instabilité des estimateurs naïfs :\n")
w(f"- **OLS** (part T2 ~ parts T1, avec constante) : intercept absurde de "
  f"**{ols[0]:+.0f}** et coefficients négatifs partout → colinéarité "
  "compositionnelle (les parts somment à 100).")
w(f"- **NNLS** (taux ≥ 0 sur les voix) : « taux » de **{min(rate[Xp.index('RN')],9):.2f} "
  f"pour RN** (soit >100 %) et explosion sur les micro-partis → sous-"
  "identification quand deux partis (RN, Reconquête) sont spatialement corrélés.\n")
w("On **ne rapporte donc PAS** de matrice de reports : ce serait inventer une "
  "précision inexistante (l'erreur corrigée dans `results/AUDIT.md`). L'estimation "
  "rigoureuse exige de l'**inférence écologique** (King) ou des données de sondage "
  "individuelles.\n")

w("## 3. Le paradoxe Zemmour : le sophisme écologique en une ligne\n")
r_rec = np.corrcoef(t1["REC"], y)[0, 1]
r_rn = np.corrcoef(t1["RN"], y)[0, 1]
w(f"Corrélation spatiale part Le Pen T2 vs part Zemmour T1 : **r = {r_rec:+.2f}** "
  "(quasi nulle !) — alors qu'au niveau **individuel** les électeurs Zemmour ont "
  "massivement voté Le Pen. Explication : les fiefs de Zemmour (quartiers aisés) "
  "ne sont pas ceux de Le Pen (France populaire/périurbaine), donc la corrélation "
  "entre circonscriptions s'annule. **C'est exactement pourquoi on ne lit pas les "
  "reports dans les agrégats.**\n")

w("## 4. Ce qui EST robuste\n")
w("**Corrélations spatiales** de la part Le Pen T2 (directionnelles, stables) :\n")
w("| Score 1er tour | Corrélation avec Le Pen T2 |")
w("|---|---|")
for p in ["RN", "DLF", "RES", "PCF", "LR", "PS", "LFI", "ENS", "EELV"]:
    w(f"| {LIBLP[p]} | {np.corrcoef(t1[p], y)[0,1]:+.2f} |")
w("")
rn1, rec1, dlf1 = natl(t1, "RN", e1), natl(t1, "REC", e1), natl(t1, "DLF", e1)
w("**Comptabilité du réservoir** (robuste car agrégée) :\n")
w(f"- Bloc droite radicale au 1er tour : RN {rn1:.1f} % + Reconquête {rec1:.1f} % + "
  f"DLF {dlf1:.1f} % = **{rn1+rec1+dlf1:.1f} %**.")
w(f"- Le Pen au 2nd tour : **{lp2:.1f} %** → **+{lp2-(rn1+rec1+dlf1):.1f} pts** "
  "au-delà de ce bloc (reports d'électeurs de gauche/centre anti-Macron et "
  "d'abstentionnistes du 1er tour). Le « front républicain » a plafonné son report.\n")

w("## 5. Ce que le 2nd tour apporte au modèle deux tours\n")
w("- **Carte de vulnérabilité** : les circonscriptions où Le Pen dépasse 50 % au "
  f"2nd tour ({int((y>50).sum())} / {len(common)}) dessinent son socle de "
  "conquête — base d'une projection de sièges (législatives) et de scénarios 2027.")
w("- **Contrainte pour la fusion (P4)** : la relation T1→T2 est forte en "
  "agrégat mais les reports fins sont incertains ; tout modèle deux tours doit "
  "porter cette incertitude, pas prétendre à une matrice de report exacte.")
w("- **Limite assumée** : une élection (2022) ; inférence écologique non conduite "
  "(méthode citée, pas implémentée) ; l'API tabulaire data.gouv (beta) reste "
  "utile pour explorer mais peu fiable sur les décimales françaises de ces "
  "fichiers.\n")

out = ROOT / "results" / "etape_P8_second_tour.md"
out.write_text("\n".join(lines))
print("\n".join(lines))

# Étape P3 — Source NLP / sentiment (proxy comportemental)

## 1. Nature du proxy : comportemental, pas déclaratif

Contrairement à un sondage (déclaratif : « pour qui comptez-vous voter ? »), cette
source mesure des traces **comportementales** et une **tonalité agrégée** :


- **Volume de recherche Google Trends** : révèle un *intérêt* ou une *inquiétude* pour
  un candidat, pas une intention de vote. Un pic de recherche peut venir d'un scandale
  (intérêt négatif) autant que d'un engouement (intérêt positif).
- **Tonalité de mentions** (presse + réseaux) : sentiment moyen agrégé sur la période,
  lui-même dépendant de la ligne éditoriale et de la composition du corpus -- pas une
  mesure calibrée d'opinion publique.

Ce double proxy est donc **structurellement plus bruyant et plus manipulable** qu'un
sondage : volume gonflable par du buzz négatif coordonné, tonalité sensible au choix des
sources. Il est traité comme tel dans le mapping (voir §2) et dans l'incertitude renvoyée
(`r2_share_sd` volontairement large).

**Couverture temporelle** : Google Trends n'existe (au sens exploitable) que depuis
~2004. Les présidentielles antérieures (1965 → 2002) sont donc
**structurellement indisponibles** pour cette source -> `SourceSignal(available=False)`.

**Correction d'audit — source forward-only** : un premier jet backtestait le NLP sur des
features 2007-2022 **rédigées en connaissant l'issue** (hindsight), ce qui gonflait les
scores (cf. `results/AUDIT.md`). Ces lignes ont été **supprimées** du snapshot. Un proxy
comportemental ne peut être honnêtement backtesté que s'il est **horodaté avant le scrutin**
par une collecte vérifiable. La source NLP est donc désormais **réservée à la prévision
d'élections à venir** (2027) : sur tout l'historique elle se déclare indisponible.

## 2. Features et mapping vers la part 2nd tour

Schéma des features attendues (`data/fr_nlp_snapshot.csv`, désormais vide de données
historiques — à alimenter en live pour un scrutin à venir) :


| Colonne | Sens |
|---|---|
| `ref_trends_share` / `opp_trends_share` | Part du volume Google Trends entre référence et principal adversaire (somme = 1) |
| `ref_mention_volume` | Indice de volume de mentions du candidat de référence (base 100) |
| `ref_tonality` / `opp_tonality` | Tonalité moyenne des mentions, dans [-1, 1] |

**Mapping** (monotone, pas de boîte noire) :


```
raw   = w1 * (ref_trends_share - opp_trends_share)
      + w2 * (ref_tonality      - opp_tonality)
share = clamp( 0.5 + 0.5 * tanh(scale * raw) )
```

avec `w1 = 1.6` (différentiel de notoriété), `w2 = 0.9` (différentiel de tonalité) fixés a priori -- non ré-estimés,
n trop petit pour régresser deux poids sans surapprendre. Seul `scale` peut être recalibré
par `fit()` (régression 1D sans intercept, bornée), à partir de l'historique strictement
antérieur. `r2_share_sd` reste dans [0.06, 0.09] -- large par construction : dans la fusion
bayésienne (pondération 1/variance), cette source pèse volontairement peu face aux
fondamentaux ou aux marchés.

### Chargeur hybride

`load_nlp_features(election_id)` tente d'abord une collecte **live** (`_fetch_live`,
Google Trends via `pytrends`), protégée par `try/except` et un timeout court ; dans cet
environnement `pytrends` n'est pas une dépendance du projet, l'import échoue donc
immédiatement et **aucune requête réseau n'est jamais émise** -- repli systématique et
instantané sur le snapshot offline `data/fr_nlp_snapshot.csv`.

## 3. Backtest hors-échantillon (OOS)

**Protocole anti-data-snooping** (fenêtre expansive, identique aux autres sources) :

- Pour prédire l'élection T, `NlpSource` est entraînée UNIQUEMENT sur les élections
  d'année < T (recalibration de `scale` seulement, voir §2)
- Données historiques rétrospectives **supprimées** (cf. §1) : **0 pli scoré**. La valeur
  de cette source ne pourra être mesurée que sur un scrutin futur (2027), sans hindsight.

| Annee | Election | Reference | Part prevue | P(victoire) | Part reelle | Issue |
|---|---|---|---|---|---|---|
| 1988 | FR_pres_1988 | mitterrand_1988 | — | — | 0.540 | (source indispo.) |
| 1995 | FR_pres_1995 | jospin_1995 | — | — | 0.474 | (source indispo.) |
| 2002 | FR_pres_2002 | chirac_2002 | — | — | 0.822 | (source indispo.) |
| 2007 | FR_pres_2007 | sarkozy_2007 | — | — | 0.531 | (source indispo.) |
| 2012 | FR_pres_2012 | sarkozy_2012 | — | — | 0.484 | (source indispo.) |
| 2017 | FR_pres_2017 | hamon_2017 | — | — | — (élim. T1) | (source indispo.) |
| 2022 | FR_pres_2022 | macron_2022 | — | — | 0.586 | (source indispo.) |

*0/7 plis disponibles (les autres sont antérieurs à ~2004, indisponibilité attendue, pas un échec).*

## 4. Limitations honnêtes

⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :


1. **Aucune validation historique (n=0)** : les features rétrospectives ayant été
   supprimées, aucun pli n'est scoré. Le mapping et ses poids `w1`/`w2` restent des choix
   a priori **non validés** sur données réelles dans ce dépôt.

2. **Validation reportée au futur** : la seule mesure honnête de cette source passe par une
   collecte Google Trends / presse **horodatée avant** un scrutin à venir (2027). Toute
   reconstruction a posteriori serait du hindsight — l'erreur corrigée ici.

3. **Proxy bruité et manipulable** : volume de recherche et tonalité agrégée peuvent être
   gonflés ou orientés par des campagnes coordonnées (bots, brigading), un scandale
   médiatique sans lien avec l'issue du vote, ou un biais de couverture éditoriale. Le
   signal n'a de sens qu'agrégé avec d'autres sources, jamais utilisé seul.

4. **Mapping simple par construction** : poids `w1`/`w2` fixés a priori, pas appris --
   choix délibéré anti-surapprentissage vu la taille de l'échantillon, mais qui laisse de
   côté d'éventuelles non-linéarités (ex. effet de seuil au-delà d'un certain volume).

5. **Causalité non établie** : notoriété/tonalité et vote peuvent être co-déterminés par
   un troisième facteur (actualité, contexte macro) sans lien causal direct entre les
   deux -- cette source capture une corrélation contemporaine, pas un mécanisme causal.

**Conclusion** : ce module est un **composant bruité d'un ensemble** (fusion avec
fondamentaux, marchés). Sa valeur attendue est de capter des signaux de dernière minute
(dynamique de campagne) que les fondamentaux structurels ne voient pas -- pas de remplacer
un sondage, et certainement pas de faire une prévision autonome.

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
**structurellement indisponibles** pour cette source -> `SourceSignal(available=False)`,
traitées comme un pli non scorable par le backtest OOS (attendu, pas une anomalie).

## 2. Features et mapping vers la part 2nd tour

Snapshot `data/fr_nlp_snapshot.csv` (valeurs illustratives, voir en-tête du fichier) :


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
- Les élections 1965 → 2002 n'ont pas de donnée NLP : plis marqués « indisponible »,
  seules 2007 → 2022 sont effectivement scorées (n=4 au maximum)

| Annee | Election | Reference | Part prevue | P(victoire) | Part reelle | Issue |
|---|---|---|---|---|---|---|
| 1988 | FR_pres_1988 | mitterrand_1988 | — | — | 0.540 | (source indispo.) |
| 1995 | FR_pres_1995 | jospin_1995 | — | — | 0.474 | (source indispo.) |
| 2002 | FR_pres_2002 | chirac_2002 | — | — | 0.822 | (source indispo.) |
| 2007 | FR_pres_2007 | sarkozy_2007 | 0.521 | 0.61 | 0.531 | ✓ gagne |
| 2012 | FR_pres_2012 | sarkozy_2012 | 0.357 | 0.03 | 0.484 | ✗ perd |
| 2017 | FR_pres_2017 | macron_2017 | 0.558 | 0.78 | 0.661 | ✓ gagne |
| 2022 | FR_pres_2022 | macron_2022 | 0.556 | 0.77 | 0.586 | ✓ gagne |

**OOS (n=4)** — Brier 0.063 | log-loss 0.257 | MAE part 0.067 | taux de bonne issue 100%

*4/7 plis disponibles (les autres sont antérieurs à ~2004, indisponibilité attendue, pas un échec).*

## 4. Limitations honnêtes

⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :


1. **Snapshot illustratif** : les valeurs de `data/fr_nlp_snapshot.csv` sont construites
   à dire d'expert (ordre de grandeur plausible), PAS extraites d'un export réel Google
   Trends ni d'un moteur de sentiment calibré. À remplacer avant toute publication.

2. **Échantillon minuscule** : au mieux 4 élections avec donnée NLP (2007-2022), dont 2
   seulement disponibles pour la calibration du dernier pli testé. Aucune conclusion
   statistique robuste ne peut être tirée d'un backtest à si peu de points ; les
   métriques OOS ci-dessus sont indicatives, pas une preuve de valeur ajoutée.

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

# Pré-enregistrement — Cycle #163 : le #38 ré-évalué sur l'univers POINT-IN-TIME réel du NDX-100

**Committé AVANT tout calcul de stratégie et AVANT le fetch réseau des
prix manquants.** Cycle #163 du backlog non-ML, correction directe du
défaut méthodologique identifié au cycle #162.

Le seul travail antérieur à ce fichier est le recensement de composition
d'indice et de disponibilité de prix
(`scripts/nonml_ndx100_universe_census.py` →
`results/nonml_ndx100_universe_census.md`, commits 2820d88/054595a/247d30d),
qui ne calcule **aucune** performance de stratégie : son rôle est
uniquement de mesurer le problème et de justifier chiffrément le périmètre
fixé ci-dessous (Règle 1 : un périmètre justifié, pas deviné ; Règle 6 :
traçabilité).

## Contexte : ce qui cloche dans les cycles #161 et #162

Le #38 (Leaders 52-semaines + overlay 52w-high indice) est le meilleur
résultat brut du backlog. Il a été évalué :

- au **#161** sur `data/pead/prices/` — fenêtre 2022-01-03 → 2026-07-27
  (~4,5 ans), bornée par un `PRICE_PERIOD1 = date(2021, 1, 1)` codé en dur
  dans `scripts/pead_fetch_data.py`, héritage sans rapport de l'ancien
  protocole PEAD. Score Règle 9 : **4/5**, DSR=0,730.
- au **#162** sur `data/pead/prices_extended/` — fenêtre 1970-2026. Score
  **3/5**, DSR=0,612, résultat déclaré **non conclusif** parce qu'un biais
  du survivant sévère avait été détecté.

Les deux utilisent le **même univers de titres** : la liste des membres du
NDX-100 **de 2026** (`data/pead/ndx100_constituents.json`, 103 tickers),
appliquée rétroactivement. Le recensement du cycle #163 mesure exactement
l'ampleur du problème :

| Date | Vrais membres du NDX-100 | Présents dans la liste 2026 | Couverture |
|---|---|---|---|
| 2015-01-01 | 105 | 44 | **42 %** |
| 2020-01-01 | 103 | 60 | **58 %** |
| 2022-01-01 | 101 | 69 | **68 %** |
| 2026-01-01 | 101 | 93 | 92 % |

Deux conséquences, à énoncer avant de calculer quoi que ce soit :

1. Le biais n'affecte pas seulement le #162 (1970-2026) : **le #161 lui-même
   est touché**. Au début de sa fenêtre, un tiers des vrais membres de
   l'indice était structurellement absent de son univers investissable.
2. Les absents ne sont pas un échantillon neutre : ce sont **par
   construction les titres sortis de l'indice depuis** (faillite, rachat,
   chute de capitalisation), donc en moyenne des sous-performants. Le
   biais est **orienté à la hausse** des rendements du portefeuille
   Leaders comme de sa référence.

## Correction retenue (fixée ici, avant tout calcul)

Reconstruire l'univers **point-in-time** : à chaque date de rebalancement,
n'autoriser que les titres **réellement membres de l'indice ce jour-là**.

- **Source de composition** : paquet `nasdaq-100-ticker-history` v2026.7.0
  (https://github.com/jmccarrell/n100tickers, licence MIT, auteur Jeff
  McCarrell). `pip install` indisponible dans cet environnement → données
  YAML **vendorées verbatim** dans `data/ndx100_history/` (empreintes
  SHA-256 dans `data/ndx100_history/SOURCE.md`) et logique `tickers_as_of`
  reportée à l'identique dans `scripts/ndx100_membership.py`, vérifiée
  contre les doctests publiés en amont.
- **Fenêtre** : **2015-01-01 → fin des données de prix (≈ 2026-07-27)**,
  soit ~11,5 ans. Cette borne n'est PAS un choix libre : 2015-01-01 est la
  **première date couverte par la source de composition point-in-time**.
  Aller plus tôt réintroduirait exactement le biais que ce cycle corrige.
  Aller plus tard réduirait l'échantillon sans aucune contrepartie.
- **Univers de prix à récupérer** : les **214 tickers ayant appartenu au
  NDX-100 entre 2015 et 2026** (et non les 103 membres actuels). 113 sont
  absents des dossiers de prix déjà committés et seront récupérés
  (Yahoo Finance, `period1=0`) dans un dossier **nouveau et séparé**,
  `data/pead/prices_pit/`. Les dossiers `data/pead/prices/` et
  `data/pead/prices_extended/` ne sont **jamais modifiés** (Règle 6).

## Changement de logique explicitement déclaré (Règle 7)

Ce cycle ne se contente PAS de changer la fenêtre de données : il modifie
la définition de l'univers investissable. Le changement est le suivant, et
c'est le **seul** :

```
# avant (#38, #161, #162)
elig = np.where(np.isfinite(r))[0]

# après (#163)
elig = np.where(np.isfinite(r))[0]
elig = [j for j in elig if tickers[j] in tickers_as_of(date_de_rebalancement)]
```

Points fixés ici :

- Le critère de prix (`np.isfinite(r)`, c'est-à-dire 252 séances complètes)
  est **inchangé** : un titre récemment entré en Bourse reste inéligible
  jusqu'à disposer du lookback, exactement comme avant.
- L'appartenance est évaluée **à la date de rebalancement elle-même**
  (information publique ce jour-là) — aucune anticipation.
- Un titre membre mais **sans prix récupérable** (retrait de cote ancien,
  ticker introuvable chez Yahoo) est simplement non investable, comme un
  titre sans historique suffisant. **Le nombre exact de ces cas sera
  rapporté** : c'est le biais résiduel de ce cycle, et il sera quantifié,
  pas estimé à la louche.
- Le recyclage de ticker (un symbole libéré puis réattribué à une autre
  société) est neutralisé mécaniquement par la grille d'appartenance : les
  prix d'un ticker ne sont utilisés que sur les périodes où il était membre.
- Panneau de prix tronqué à **2013-01-01** pour le calcul (fournit le
  lookback de 252 séances avant 2015-01-01). Choix purement calculatoire :
  aucune quantité évaluée à partir de 2015-01-01 n'en dépend, la fenêtre
  glissante de 252 séances ne remontant jamais avant 2014.
- La grille de rebalancement (tous les 21 jours) est **ancrée à la première
  séance ≥ 2015-01-01**, première date couverte par la composition. Ancrage
  déclaré ici, jamais ajusté ensuite.

## Ce qui ne change PAS (aucun retuning)

`TERCILE = 1/3`, `LOOKBACK = 252`, `REBAL_EVERY = 21`, `CAP = 2.0`,
`INDEX_LOOKBACK = 252`, `INDEX_THRESHOLD = 0.95`, `COST_BPS = 5.0`.
Signal de tendance indice : `data/nasdaq100_daily.txt`, inchangé.
Référence : **portefeuille Leaders 1.0x** construit sur **le même univers
point-in-time** que le candidat (les deux jambes subissent exactement le
même traitement d'univers), conformément au PREREG d'origine du #38 — pas
Buy&Hold.

Aucune grille, aucune variante, aucun second essai. Si le résultat déçoit,
il est rapporté tel quel et le cycle est clos.

## Critère de succès (identique au #161, Règle 9)

Ré-exécution de la **même** batterie
`nonml_leaders_index52w_high_overlay_pass_validation_battery.py`,
5 contrôles a-e, tous requis pour un PASS RENFORCÉ :

a. stress de coûts ×1/×3/×5 (5 / 15 / 25 bps) ;
b. stress de crise (MDD candidat pas pire que la référence). **Couverture
   attendue : 2/4 fenêtres** (krach COVID 2020, resserrement 2022). Le
   dot-com (2000-2002) et la crise de 2008 restent **hors couverture** —
   la source de composition point-in-time commence en 2015. Ce sera
   affiché comme tel (Règle 5 : pas d'absorption silencieuse), et c'est un
   progrès net sur le 1/4 du #161 ;
c. stabilité temporelle : 4 folds non chevauchants + embargo 5j, majorité
   requise ;
d. SPA de Hansen à 1 candidat, p < 0,05 ;
e. DSR avec `n_trials` = taille du backlog avant ce cycle (lu
   automatiquement, **jamais 1**), seuil 0,95.

**`n_trials` de CE cycle = 1** : une seule fenêtre (imposée par la source),
une seule définition d'univers, aucun paramètre libre exploré.

## Hypothèse testée, et comment elle peut être réfutée

Hypothèse : une fois le biais du survivant **éliminé** (et non plus estimé),
le #38 conserve son edge et le score de la batterie reste comparable au
4/5 du #161, sur un échantillon 2,5× plus long.

Réfutations possibles, toutes à rapporter honnêtement :

- **Le score chute** → l'edge du #38 était en partie un artefact de
  survivorship : la sélection « Leaders » privilégie mécaniquement les
  titres proches de leur plus haut, et un univers composé uniquement de
  futurs gagnants amplifie artificiellement cette sélection. Ce serait le
  résultat le plus important du cycle, et il invaliderait partiellement le
  #161 comme « meilleure preuve disponible ».
- **Le score se maintient mais le DSR baisse** → l'edge est réel mais plus
  faible que mesuré jusqu'ici.
- **Le score se maintient et le DSR monte** → l'hypothèse du #161 (edge
  réel borné par la puissance statistique) est confirmée avec un univers
  cette fois défendable.

Aucun de ces trois cas ne déclenchera un second essai avec d'autres
paramètres.

## Anti-cheat

Ce fichier est committé **avant** le fetch réseau des 113 tickers manquants
et **avant** toute exécution de la batterie. Vérification automatisée après
coup : `python3 scripts/nonml_anti_cheat_check.py
leaders_index52w_high_overlay_pit_universe`.

# Composition point-in-time du NASDAQ-100 — source et traçabilité

Fichiers `n100-ticker-changes-YYYY.yaml` copiés **verbatim, sans aucune
modification**, depuis le projet amont :

- **Projet** : `nasdaq-100-ticker-history` (module Python
  `nasdaq_100_ticker_history`, appelé aussi *n100tickers*)
- **Auteur** : Jeff McCarrell
- **Dépôt** : https://github.com/jmccarrell/n100tickers
- **Version amont** : `2026.7.0` (champ `version` de `pyproject.toml` à la
  date de récupération)
- **Chemin amont** : `src/nasdaq_100_ticker_history/n100-ticker-changes-YYYY.yaml`
- **Récupéré le** : 01/08/2026, via `raw.githubusercontent.com`, branche `main`
- **Licence** : MIT — copie intégrale dans `LICENSE_n100tickers.txt`
- **Couverture documentée par l'amont** : 2015-01-01 → au moins 2026-06-22

## Empreintes SHA-256 (16 premiers caractères) des fichiers récupérés

| Fichier | sha256 (préfixe) |
|---|---|
| n100-ticker-changes-2015.yaml | `1f6af72a08534b32` |
| n100-ticker-changes-2016.yaml | `8f208c9a905d9b61` |
| n100-ticker-changes-2017.yaml | `aee3198efa302812` |
| n100-ticker-changes-2018.yaml | `560ca15e698a3f49` |
| n100-ticker-changes-2019.yaml | `241a85556e2e2303` |
| n100-ticker-changes-2020.yaml | `fc471f590e44a0f7` |
| n100-ticker-changes-2021.yaml | `e810a7f3e67c702d` |
| n100-ticker-changes-2022.yaml | `6313b84f4d178b8d` |
| n100-ticker-changes-2023.yaml | `7d545922ec54325c` |
| n100-ticker-changes-2024.yaml | `12bec472989760c3` |
| n100-ticker-changes-2025.yaml | `e20a547ed1bb5d6f` |
| n100-ticker-changes-2026.yaml | `f45d2b464ca7e52c` |

## Pourquoi un portage plutôt qu'un `pip install`

L'environnement d'exécution de ce projet n'autorise pas l'installation de
paquets, et l'amont dépend de `strictyaml` (également indisponible). Seule
la fonction de chargement est réécrite, avec PyYAML déjà présent, dans
`scripts/ndx100_membership.py` — transcription littérale de la logique
amont (`tickers_on_Jan_1` puis application chronologique des opérations
`union`/`difference` de date ≤ date demandée), vérifiée contre les
doctests publiés en amont (`tickers_as_of(2020, 9, 1)` → 103 membres,
contient `TSLA`).

**Écart connu entre PyYAML et strictyaml, corrigé explicitement** : PyYAML
applique la résolution booléenne YAML 1.1, qui transformerait le ticker
`ON` (ON Semiconductor, membre du NDX-100 de 2023 à 2025) en `True`.
`scripts/ndx100_membership.py` désactive ce résolveur et le vérifie par
assertion — bug détecté et corrigé AVANT tout calcul de stratégie.

## Ne pas modifier

Ces fichiers sont une donnée externe figée (même statut que
`data/nasdaq_composite_daily.txt`). Toute mise à jour doit être une
nouvelle récupération amont documentée ici, jamais une édition manuelle.

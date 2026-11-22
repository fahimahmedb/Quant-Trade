# Contrôle EU ETS EEA — sidérurgie française (code 24) 2021–2025

**Fichier fourni par l'utilisateur** : `eea_t_eu-emission-trading-scheme_p_2005-2025_v03_r00.zip`. Archive ZIP vérifiée avec `testzip() == None` (aucune entrée défectueuse), 9 objets, 6,084,504 octets. SHA-256 ZIP : `3fb6126d4ded99cb69e4c1814a91a42892b38ec5c6a443f12beee12c7e4720be`.

**Origine indiquée dans le fichier** : European Environment Agency (EEA), données EU ETS du registre de l'Union, cube **version 83**, classeur `CITL_cube_final_version83_2026-10-15_14-48.xlsx`; notice : `https://doi.org/10.2909/9eee3fc9-3060-4e3f-bc8d-e22e7c3f6bda`. La documentation d'octobre 2026 précise que les données sont **agrégées par pays, activité et année**, et qu'une partie des codes d'activité anciens a été reclassée.

**Contrôles exécutés** : structure XML du tableur lue en flux sans modification ; 92 241 lignes de données sur neuf colonnes ; 37 codes de pays/entités (certains sont des fonds institutionnels et pas des pays), 31 codes d'activité, 19 libellés de mesure. Filtres stricts : `country_code=FR`, `main_activity_code=24`, `active_installation=all entities`, `size=All sizes`, années 2021–2025, métriques `1.1`, `2.1`, `4.1`. Une seule observation attendue par métrique et année : **15/15 contrôles d'unicité réussis**. La source comporte également des catégories récapitulatives (`20-99`), qu'il serait erroné d'additionner aux codes élémentaires.

## Résultat descriptif par année

| Année | Allocations gratuites (quotas) | Émissions vérifiées (tCO₂-eq.) | Écart arithmétique allocations − émissions | Quotas restitués |
|---|---:|---:|---:|---:|
| 2021 | 16 635 109 | 15 481 146 | +1 153 963 | 15 481 146 |
| 2022 | 15 514 280 | 14 056 865 | +1 457 415 | 13 982 273 |
| 2023 | 15 706 373 | 11 508 929 | +4 197 444 | 11 583 519 |
| 2024 | 12 145 121 | 10 573 841 | +1 571 280 | 10 573 841 |
| 2025 | 10 954 227 | 9 905 438 | +1 048 789 | 9 886 851 |
| **TOTAL** | **70 955 110** | **61 526 219** | **+9 428 891** | **61 507 630** |

**Interprétation bornée :** sur le **secteur agrégé code 24, en France seulement**, les quotas gratuits du cube excèdent les émissions vérifiées de **9,428,891** unités sur 2021–2025. **Ce n'est ni un solde de trésorerie, ni un nombre de quotas réellement vendus, ni la situation d'ArcelorMittal.** Le fichier ne donne **aucun identifiant d'installation, d'exploitant ou d'entreprise** et ne distingue pas les transferts de quotas liés aux accords de gaz résiduels. Il ne peut donc pas confirmer ou réfuter le déficit de 29 323 123 quotas présenté dans l'autre dossier pour **l'ensemble des installations européennes d'ArcelorMittal**, après transferts. Périmètres et comptabilités différents.

**Réserve temporelle :** le fichier est un instantané publié en 2026 et ne prouve pas les valeurs effectivement connues en 2021, 2022, etc. L'analyse de marché point-in-time requiert des archives par date de publication. Les colonnes années incluent quelques valeurs d'allocation planifiées jusqu'à 2030 : ne jamais les lire comme des émissions futures réalisées.

**Pièce décisive à rechercher :** sur le site officiel du **registre de l'Union**, rubrique `Data Download`, récupérer les fichiers **`Operators Daily`** et **`Operators Yearly Activity Daily`** afin de rapprocher les identifiants des installations, leurs exploitants, allocations et émissions annuelles : `https://union-registry-data.ec.europa.eu/report/eu-registry-data-download`. Les transferts spécifiques entre sociétés, les achats nets et les contrats d'énergie ne seront pas nécessairement publics même après cette étape.

**Fichier de travail généré :** `eea_fr_steel_24_2021_2025_summary.csv`, SHA-256 `1f7e88ec8c902b2da4a2cb86fe033c2460b3aed1ab5be2d218a7e712ac3fa8fe`. Extraction descriptive, aucune donnée de prix boursier consultée ni backtest exécuté. L'archive ZIP d'origine demeure inchangée.
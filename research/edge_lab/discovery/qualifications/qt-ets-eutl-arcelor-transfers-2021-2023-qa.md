# Quant-Trade — registre EU ETS : transactions et rapprochement ArcelorMittal

**Date : 22 novembre 2026.** Analyse des cinq fichiers nouvellement transmis ; aucune opération, changement de méthode IA ou test de rendement.

## 1. Preuves d’acquisition et intégrité

| Fichier | Taille, nature | SHA-256 | Disposition |
|---|---|---|---|
| `transactions_eutl_2026.zip` | ZIP 41,53 Mo, 3 entrées, CRC PASS; deux CSV internes (ESD et non-ESD) | `b19060b8df7c7053b4e8486f98e8fe47f67d4fc11bbb878ce145c4c4d273dcb2` | QA CSV complet, source transactionnelle utile |
| `operators_daily 2.csv.gz` | 1,95 Mo, copie parfaite des opérateurs existants | `79eac53e3066f6c8eb9233cce2b74dc6624e21fccf657df617ae4e0dad5f3cd5` | NO_CHANGE_REQUIRED — doublon |
| `registry_holdings_daily.csv.gz` | 232 octets, 6 catégories agrégées | `29117517fe116a77ecdbdafb5f61040d0beb0e1cb5558a3799a74eeb5639cd09` | PARK — pas d’avoirs par société |
| `verified_emissions_2025_en.xlsx` | 8,23 Mo, 18 993 lignes de données dans onglet principal | `8f4e628d9d8d7decb0a9bae4cde067442dec9a25c12ec2a561f52687cfb6b99a` | Contre-épreuve des chiffres par installation |
| `compliance_2025_code_en.xlsx` | 1,42 Mo, 15 305 lignes de données dans onglet principal | `2ab43fc5d8675d0c22c4f9688a6f8a246a11d30bc5ee058e7fb0bc79b2b1d2ed` | Contre-épreuve par phase/installation |

L’archive inclut un CSV **ESD (Effort Sharing Decision)** à ne pas confondre avec les échanges EU ETS. Le CSV **non-ESD** a été entièrement lu avec `csv.reader` : **2 210 346 enregistrements, aucune anomalie de longueur de ligne**, extraction du 6 octobre 2026. Les transactions vont de **2005 à 2023**, sans transactions **2024–2025**.

## 2. Flux candidats vers des acteurs de l’énergie (2021–2023)

Sélection déterministe exploratoire : `TRANSACTION_STATUS=Completed`, `TRANSACTION_TYPE=10-0` (transfert interne au registre), `UNIT_TYPE_DESCRIPTION=Non-Kyoto Unit`, compte émetteur explicitement nommé **ArcelorMittal ou Industeel**, compte destinataire portant l’un des sept noms ci-dessous. Le type « Non-Kyoto Unit » n’est pas une preuve du sous-type exact d’allocation. L’appartenance de la contrepartie au secteur énergie est un filtre métier, non la preuve de la convention sidérurgique.

| Compte destinataire | 2021 | 2022 | 2023 | Total |
|---|---:|---:|---:|---:|
| Electrabel | 4 028 778 | 4 604 190 | 4 108 771 | **12 741 739** |
| ENGIE | 3 003 880 | 3 773 529 | 3 094 027 | **9 871 436** |
| TAMEH Polska Sp. z o. o. | 1 519 319 | 3 994 541 | 3 229 900 | **8 743 760** |
| Aboño Generaciones Eléctricas, S.L.U. | 1 689 237 | 2 750 665 | 2 010 341 | **6 450 243** |
| Vulkan Energiewirtschaft Oderbrücke GmbH | 1 764 789 | 1 737 043 | 1 785 331 | **5 287 163** |
| Cogeneración Siderúrgica Asturiana, S.A. | 194 498 | 69 818 | 0 | **264 316** |
| DALKIA | 44 065 | 47 748 | 44 698 | **136 511** |
| **Total exploratoire** | **12 244 566** | **16 977 534** | **14 273 068** | **43 495 168** |

**73 identifiants de transaction distincts, 74 lignes de détail**. Un transfert ENGIE (`EU716396`) est détaillé en deux lignes de 1 020 000 et 2 753 529 unités : additionner les quantités des lignes distinctes sans compter deux fois le nombre de transactions. Les 43 495 168 unités sont un flux **brut dirigé** vers ces contreparties, pas un résultat comptable net, une dépense financière ou une confirmation des 72 056 762 quotas déclarés.

**Référence ArcelorMittal :** allocations gratuites européennes 2021–2025 **212 809 169** ; émissions vérifiées **170 075 530** ; transferts déclarés aux producteurs d’électricité associés à l’utilisation des gaz sidérurgiques **72 056 762** ; solde déclaré après transferts **−29 323 123**. Source : https://corporate.arcelormittal.com/sustainability/climate/climate-faq .

**Limites de comparabilité déterminantes :** (1) 2024–2025 absents des transactions accessibles ; (2) correspondance juridique des titulaires des comptes et périmètre consolidé incomplète ; (3) une transaction à un producteur d’électricité peut relever d’un achat/vente ou d’une autre convention que le transfert de gaz sidérurgiques ; (4) montants par sous-type de quota et statut économique du paiement non identifiés ; (5) les données transactionnelles sont rendues publiques avec un délai réglementaire de trois ans (art. annex XIII 2019/1122 modifié). Règlement : https://eur-lex.europa.eu/eli/reg_del/2019/1122/2025-01-01/eng .

## 3. Recoupement avec les deux classeurs 2025

**Émissions 2025 (classeur daté 1er avril 2026)** : 18 993 lignes générales ; **76** correspondances installation `(REGISTRY_CODE, INSTALLATION_IDENTIFIER)` avec les **87** sites de la précédente extraction large par noms. Sur ces 76 correspondances, les émissions xlsx correspondent exactement aux séries quotidiennes pour 2021, 2022 et 2023 (**63/63 valeurs disponibles**), 2024 (**62/62**), et 2025 (**48/48**). Pour 2025, **28 lignes xlsx sont « n/a »**, ce qui ne signifie pas zéro émission.

**Allocations :** en 2021–2024, chaque année donne 61 correspondances strictes et une divergence de 10 147 quotas pour FR-206303 ; 14 valeurs xlsx `n/a` (ne pas forcer à zéro). En 2025 : 58 égalités, 4 divergences et 14 `n/a`; ne pas masquer les divergences de millésimes ou de périmètre.

**Conformité (63 sites recoupés) :** la colonne `TOTAL_VERIFIED_EMISSIONS` porte un **total pluriannuel (2021–2025)** ; comparer au seul chiffre 2025 aurait été **faux**. Rapprochement au cumul réel : **61 égalités exactes** pour émissions, deux sites dont le cumul complet ne peut être reconstitué ; **57 égalités exactes** pour quotas restitués, six dossiers incomplets. Les 63 lignes recoupées portent le code de conformité `A` (la signification réglementaire du code reste à qualifier, pas une preuve de coût nul).

## 4. Holdings et doublon

- `operators_daily 2.csv.gz` : SHA-256 **identique** au fichier précédent `operators_daily.csv.gz`, donc `NO_CHANGE_REQUIRED`; ne pas créer de nouvelles installations en le réimportant.
- `registry_holdings_daily.csv.gz` : six catégories de détention globale au 22 novembre 2026 (EUA, EUAA, CHU, CHUA, CER, ERU). **Aucun compte ou site individuel** : ce document ne permet pas de déterminer le portefeuille de quotas d’ArcelorMittal.

## 5. Verdict et prochaine pièce économiquement décisive

- **`TRANSACTION_EVIDENCE_PARTIAL_PASS`** : archives détaillées de transferts, 43,495 millions d’unités sortantes vers sept contreparties énergétiques candidates (2021–2023) ; calcul exact selon le filtre annoncé, mais **non attribuable contractuellement sans autre preuve**.
- **`COMPANY_RECONCILIATION_UNKNOWN`** : les **72,056762 millions sur 2021–2025** restent non rapprochés intégralement, notamment faute de transactions 2024–2025 et faute de convention de gaz résiduels ou de confirmation par partenaire.
- **`PARK_2024_2025_TRANSACTIONS_PUBLICATION_LAG`** : aucune reconstitution d’années non publiées. Les données 2024 et 2025 de conformité/émission ne sont **pas** des transactions de transfert.
- **`NO_ECONOMIC_BACKTEST`** : pas de valeur actualisée ni d’alpha actionnarial ; coûts des EUA, couverture, flux de trésorerie, benchmark et prix d’action PIT restent inconnus.

Prochaine preuve utile : table de périmètre et conventions signées (ArcelorMittal × producteurs électriques), distinction des quotas remis contractuellement et des achats/cessions de marché, publication future des transferts 2024–2025. Les événements d’allocation et de conformité restent exploitables dès maintenant pour l’étude documentaire, sans simuler un gain boursier.

## 6. Pièces de contrôle

- `qt_ets_arcelor_energy_counterparties_2021_2023.csv` : série agrégée reproductible par contrepartie et année.
- `qt_ets_arcelor_eutl_2026_receipt.json` : SHA des cinq fichiers, filtres, contrôles et écarts.
- Originaux binaires conservés localement ; **non versés dans le dépôt** (volume, droits, source brute).
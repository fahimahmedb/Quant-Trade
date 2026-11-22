# Quant-Trade — H-INDUSTRY / EU ETS : comptes et millésimes de conformité (22 novembre 2026)

**Périmètre :** prolongement du rapprochement ArcelorMittal/Industeel à partir des sept nouveaux fichiers transmis, en réutilisant `transactions_eutl_2026.zip`, les exports `operators_daily` et `operators_yearly_activity_daily`, et les 86 installations déjà qualifiées. Aucun ordre, nouvel essai de cours, modification du comportement IA ou calcul d'alpha.

## 1. Fichiers inspectés et intégrité

| Source | SHA-256 |
|---|---|
| `accounts_daily.csv.gz` | `fa0a8a99350adde4030e7b6726cccf90758709958511170d2c735396680f8c3e` |
| `verified_emissions_2023_en_1.xlsx` | `1e9d43a0a820594514b8921b147c4509435ff1856b5ee7abbac2123d198ab19b` |
| `verified_emissions_2024_en.xlsx` | `716e113b16227bb494b82516b607d1f62f25eefd0cfeb57a504422f05b17873f` |
| `compliance_2021_code_en.xlsx` | `26969b3486bf478574d1caefdd1e736f592e28a3fd83175b2063e9fe27c1f1e5` |
| `compliance_2022_code_en.xlsx` | `d472efb7fc4fa4dfdb61b7a7526a7940979400aacf82c579bf5bf246984d30ab` |
| `compliance_2023_code_en.xlsx` | `b81e1c4e17b1d682b25d22699d2fb5d19ff10f0` |
| `compliance_2024_code_en.xlsx` | `a8b2191b56fa576b7d9e0ae000ddab24b5aa90e8511e4287203461ca4684dd7a` |

Contrôle gzip, en-tête CSV et identifiant de compte ; extraction ciblée OOXML des feuilles Excel sans réécriture des originaux. Contrôles exécutés : unicité des **50 598** paires `(REGISTRY_CODE, ACCOUNT_IDENTIFIER)` ; toutes les transactions EUTL non-ESD relues, **2 210 346** lignes au bon schéma ; égalité exacte du total précédemment isolé. Les identifiants de compte isolés sont uniques dans la population des comptes observés en 2026.

## 2. Transactions candidates vers producteurs d'énergie, 2021–2023

Filtre **inchangé** de l'exploration précédente : `TRANSACTION_STATUS=Completed`, `TRANSACTION_TYPE=10-0`, `UNIT_TYPE_DESCRIPTION=Non-Kyoto Unit`, source ArcelorMittal ou Industeel explicitement identifiable dans les informations EUTL, destinataire correspondant à l'une des sept contreparties énergétiques candidates. La nomenclature est un filtre, **pas une preuve de convention de gaz sidérurgiques**.

| Année de transaction | Compte `Operator Holding Account` dans le snapshot 2026 | Compte `Trading Account` dans le snapshot 2026 | Total |
|---|---:|---:|---:|
| 2021 | 9 196 621 | 3 047 945 | 12 244 566 |
| 2022 | 13 156 257 | 3 821 277 | 16 977 534 |
| 2023 | 11 134 343 | 3 138 725 | 14 273 068 |
| **Total** | **33 487 221** | **10 007 947** | **43 495 168** |

**74 lignes de détail / 73 IDs de transactions** ; les **74 comptes source sont rapprochés par identifiant unique**, sans besoin d'alignement approximatif de noms ; **0 flux supplémentaire** découvert par l'enrichissement du snapshot des comptes. Les sept lignes de comptes Trading proviennent d'**ArcelorMittal Treasury**, à destination d'ENGIE ou de DALKIA dans les observations retenues. **Un compte `Trading` ne démontre pas une vente ni un prix payé.** La qualification de l'instrument transféré reste bornée par les libellés EUTL.

**Contradiction à préserver :** les **43,495 M** couvrent seulement 2021–2023 et sept destinataires présélectionnés ; ArcelorMittal annonce **72 056 762** unités transférées à des producteurs d'électricité sur **2021–2025**. Une simple différence de 28,56 M ne mesure **pas** automatiquement les transactions manquantes : périmètre et cause contractuelle n'ont pas été réconciliés. Les transactions publiques 2024–2025 sont absentes du ZIP fourni. Déclaration source : https://corporate.arcelormittal.com/sustainability/climate/climate-faq .

## 3. Révisions entre les publications Verified Emissions 2023 et 2024

En-têtes originaux inspectés : publication/extraction du **1er avril 2024** pour le fichier 2023 et du **1er avril 2025** pour le fichier 2024. Jointure stricte `(REGISTRY_CODE, INSTALLATION_IDENTIFIER)` avec les **86** installations du périmètre de travail conservé ; **77/86** sont présents dans chacune des deux feuilles. La qualification 86 sites repose sur les noms des détenteurs au 22 novembre 2026, **pas sur un arbre historique certifié du groupe**.

Sur les années **2021–2023**, comparaison des cellules chiffrées des deux millésimes : **12 valeurs modifiées**, dont **9 allocations et 3 émissions vérifiées**. Le détail cellule par cellule est dans `qt_ets_verified_revision_2023_2024.csv` :

- DE-67, ArcelorMittal Hamburg, allocation 2021 **−7 719** et 2022 **−6 422** ; allocation 2023 **−5 356**.
- DE-60, Bremen, allocation 2023 **−1 640**.
- LU-13, Belval/Differdange, émission 2023 **+1 152**.
- BE-108, ArcelorMittal Belgium, émission 2022 **+305**.

Le reste des 12 corrections est documenté dans le CSV. Une case vide ou `n/a` **n'est jamais assimilée à zéro**. Ces différences montrent qu'un niveau 2021–2023 consulté en 2026 n'était pas nécessairement connu en 2024 ; il n'y a **aucune mesure de rendement, surprise ou signal PIT** construite à partir de ces révisions.

## 4. Les quatre millésimes Compliance 2021–2024

Pour les sites retenus, **65/86 installations** apparaissent dans chacun des quatre classeurs de conformité. Leur code :

| Fichier | `A` | `B` | Autres codes dans les sites rapprochés |
|---|---:|---:|---:|
| 2021 | 65 | 0 | 0 |
| 2022 | 64 | 1 | 0 |
| 2023 | 64 | 1 | 0 |
| 2024 | 65 | 0 | 0 |

L'unique `B` de 2022 et 2023 concerne **BE-115, Galva prépeint – Flémalle** (titulaire dans le snapshot 2026 : ArcelorMittal Belgium). Les règlements officiels du registre associent le symbole **B** à une insuffisance de quotas restitués par rapport aux émissions vérifiées à la date réglementaire applicable ; le code **A** indique un niveau de restitution suffisant. **Ce statut historique ne suffit pas à prouver sanction, perte, montant de pénalité ou impact financier net**, et la conformité future ne modifie pas automatiquement le code attribué à un état historique. Référence primaire : https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R1122-20230910 .

Les lignes `TOTAL_VERIFIED_EMISSIONS` et `TOTAL_SURRENDERED_ALLOWANCES` sont **cumulatives par période** et ne doivent pas être assimilées aux seuls flux de l'année du fichier ; un même instant de clôture de tableau ne constitue pas une chronologie transactionnelle.

## 5. Conclusion et prochaine preuve discriminante

**PASS :** intégrité de sept fichiers et lecture correcte de leurs structures ; compte source EUTL identifié pour 74/74 lignes candidates ; 43,495 M recomptés ; 12 révisions de chiffres quantifiées ; code B isolé et compris selon règle primaire.

**UNKNOWN :** groupe légal consolidé par année, nature commerciale ou contractuelle des transferts ArcelorMittal↔producteurs, prix EUA et flux nets, publication des transferts 2024–2025, équivalence du périmètre de 43,495 M avec les 72,057 M annoncés, effet valorisation/actions, vrai avantage patrimonial.

**PARK** : télécharger de nouveau les mêmes classeurs, rechercher encore les historiques pré-2021 sans nouvelle hypothèse matérielle, ou rouvrir les essais ETF négatifs. **Prochaine preuve :** conventions gaz sidérurgiques/liens compte→centrale datés et/ou détails des achats ou transferts contractualisés, puis données publiques 2024–2025 lorsqu'elles seront libérées. L'analyse du seul compte `Trading` ne suffit pas.

### Artefacts

- `qt_ets_accounts_arcelor_energy_candidates_2021_2023.csv` — 74 lignes EUTL candidates enrichies des identifiants et types de comptes 2026.
- `qt_ets_verified_revision_2023_2024.csv` — les 12 valeurs révisées par pays, installation, mesure et année.
- `qt_ets_accounts_reconciliation_qa_2026-11-22.json` et `qt_ets_verified_revision_qa_2026-11-22.json` — contrôles et SHA.
- `qt_ets_accounts_reconcile_2026.py` et `qt_ets_vintages_stream.py` — scripts de lecture reproductible, ne contiennent ni données privées ni API de trading.
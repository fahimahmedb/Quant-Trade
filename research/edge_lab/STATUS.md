# Quant — labo de recherche

**État : IDLE**

Un état IDLE/BLOCKED est normal lorsqu'aucun travail économique n'est admissible.

Dernier cycle attesté : `2026-10-11T00:23:03.103495+00:00` ; acteur `github-actions-metadata`.
Rappels désactivés (confirmation outil) : `2026-10-11T00:11:00Z`.
L'activité d'un worker économique est attestée par une réservation et un reçu d'exécution, pas un commit récent.

[Pause/reprise persistante : modifier `paused` dans CONTROL.json](https://github.com/fahimahmedb/Quant-Trade/edit/research/edge-lab-continuous/research/edge_lab/CONTROL.json)
La pause empêche tout nouveau travail. Le contrôle et l'état du scheduler sont distincts ; désactiver les rappels arrête ses réveils.

## Prochaine décision utile

Aucune question ouverte ; attendre une preuve ou un accès nouveau.

## Programme et preuves

| Voie | État | Preuve figée | Prochain travail |
|---|---|---|---|
| Treasury/ZF — pression d'adjudication | `BLOCKED_DATA_ACCESS` | [5bb78345](https://github.com/fahimahmedb/Quant-Trade/tree/5bb78345e0cc9d02ac38c13d2c0981cb380021be) | Qualifier droits, BBO, rolls PIT et prix du paquet complet ; aucun achat. |
| EUR/USD — grille technique sur proxy | `FROZEN_NOT_EXECUTED` | [e42d4924](https://github.com/fahimahmedb/Quant-Trade/tree/e42d4924a33efa78bab97939d654424cc1501fb8) | Réutiliser le gel/harnais ; qualifier proxy, droits et historique d'expositions. |
| Hyperliquid — flux forcés | `BLOCKED_HOST` | [a6961e5f](https://github.com/fahimahmedb/Quant-Trade/tree/a6961e5fc02785c7c2d797f0e1fca94425150705) | Vérifier un hôte qualifié et les global fills ; ne pas substituer trades WS. |
| F2 — accès prediction | `BLOCKED_PERMISSION` | [e7344cfd](https://github.com/fahimahmedb/Quant-Trade/tree/e7344cfda865b987e57c0d0ad8eb37f4f164cf9e) | Attendre une permission explicite ; ce blocage n'est pas un rejet économique. |
| Form 4/F3 et 13D distinct | `BLOCKED_DATA_CHAIN` | [afd69b74](https://github.com/fahimahmedb/Quant-Trade/tree/afd69b74c12d02cb9b8f731137ba5c357819ab24) | Réutiliser census ; qualifier CIK/security PIT et delist prices. |
| Volatility insurance risk transfer in CFE VX futures: test whether hedging demand compensates sellers after executable costs, jump/tail/margin risk and an appropriate risk-premium benchmark; no promised alpha. | `HYPOTHESIS` | Hypothèse, aucun edge établi | Choisir un test discriminant accessible. |
| B2/B4 ETF daily | `REJECTED_CLOSED` | [1e88c6b8](https://github.com/fahimahmedb/Quant-Trade/tree/1e88c6b82d682ae6d6d71b0732cb1bdb232cea3a) | Conserver rejets, 40 essais déclarés et shadow non lu. |
| F1 carry crypto | `REJECTED_CLOSED` | [ea9d2d0e](https://github.com/fahimahmedb/Quant-Trade/tree/ea9d2d0e0e057199bb168249c963acbc88e89de5) | Conserver la disposition publique ; aucune ouverture des outcomes A/B. |
| Prediction negative-risk | `REJECTED_CLOSED` | [2b66b193](https://github.com/fahimahmedb/Quant-Trade/tree/2b66b1937257651b3a941bba6d7a1e5e45c01137) | Conserver KILL du rerun valide, séparé du premier résultat invalidé. |

## N, essais et fenêtres

Nouveaux looks réservés/consommés par le labo : **0**.
Les jours/instruments/routes corrélés ne sont pas convertis en observations indépendantes.
M effectif et expositions privées : UNKNOWN. Aucun seuil historique ni Sharpe cible modifié.

| Jeu de données | Essais historiques déclarés | Nouveaux chemins chargés | Historique complet ? |
|---|---:|---:|---|
| crypto-carry-f1 | UNKNOWN | 0 | UNKNOWN |
| daily-etf-panel | 40 | 0 | UNKNOWN |
| eurusd-histdata | UNKNOWN | 0 | UNKNOWN |
| prediction-flb | UNKNOWN | 0 | UNKNOWN |
| treasury-zf-bbo | UNKNOWN | 0 | UNKNOWN |

40 = B2 36 + B4 4 pour le même panel, sans double addition. Les fenêtres protégées et réservations F1 restent fermées.

## Coût et limites

| Mesure | Valeur |
|---|---|
| Dépenses autorisées/engagées USD | 0 |
| Tokens | NON MESURÉ |
| CPU mesuré des opérations locales | 0.0463 |
| Durée mesurée des opérations locales | 14.112 |
| Octets de payload de métadonnées | 10416 |
| Trafic réseau total | NON MESURÉ |
| Temps humain | NON MESURÉ |

Pas de budget Owner total chiffré. 120 s/2 MiB sont des bornes techniques par opération, pas une allocation économique. Tokens NON MESURÉS. Aucun quota d'expériences ni Sharpe cible.

Aucun achat, capital réel ou trading live autorisé. Coût du polling du modèle et facture totale NON MESURÉS.
Claude : pas de revue simulée ; contradiction ciblée après disponibilité, sans seconde boucle.

## Exécutions et apprentissages

Aucun worker économique exécuté. La qualification et la veille ne sont pas un backtest.
- `build:eurusd-technical-grid:exact-legacy-adapter` : **WAIT** — Implement saved exact adapter plan and receipt reconciliation with synthetic fixtures; no new source review/outcome. ; preuves lab-exact-legacy-metadata-plan-20261011T0004Z.
- `build:eurusd-technical-grid:implement-saved-adapter` : **QUALIFIED** — Software complete on synthetic proof. Publish and verify exact-head CI. Market admissions remain blocked, reminders off, no repeated source review. ; preuves lab-complete-loop-synthetic-20261011T0013Z, owner-reminders-off-20261011T0011Z.
- `build:eurusd-technical-grid:lab-workflow-completion` : **WAIT** — Core workflow software implemented and validated with synthetic receipts. Completion still requires the distinct exact legacy bridge and final real temporary-Git proof; preserve partial receipt, all history and disabled reminders. No actual market launch. ; preuves lab-workflow-core-synthetic-20261010T2355Z.
- `build:eurusd-technical-grid:legacy-authority-bridge` : **WAIT** — Read-only exact preflight built/reviewed/tested; full launch remains WAIT. Preserve original refs/gates and all spent history. Next distinct construction question measures synthetic CPU/storage/runtime bounds, without price data, old runtime boot, ref creation or economic launch. ; preuves eurusd-legacy-exact-readonly-preflight-20261010T2001Z, fx-legacy-control-resource-bridge-gap-20261010.
- `build:eurusd-technical-grid:synthetic-reader-boundary` : **WAIT** — Exact parser duplicate-group and CRC fixture completed and preserved. Resource/source/original-launch admission remains WAIT; no new OPEN question justified by cached information. Next: bounded metadata tick, wake only on distinct permitted full-input/group bounds or original reservation/launcher authority evidence. Never repeat the same probe, change frozen parameters/code/window, or auto-launch market. ; preuves eurusd-synthetic-reader-group-crc-20261010T2136Z.
- `build:eurusd-technical-grid:synthetic-resource-envelope` : **WAIT** — Synthetic full-calendar engine probe implemented and completed; complete market resource envelope remains WAIT. Next distinct construction question challenges same-timestamp/duplicate group memory and parser/CRC on synthetic ZIPs, with no real archives or result access; no changed freeze or automatic market launch. ; preuves eurusd-full-calendar-synthetic-capacity-20261010T2012Z.
- `qualify:cfe-vix-term-premium` : **WAIT** — No economic launch or hourly repeat qualification. Wake only on a distinct exact zero-paid package/rights/clock/PIT/cost/resource fact or a genuinely new implementation admission question. Otherwise cheap allowlisted metadata tick then IDLE/BLOCKED; preserve all spent history. ; preuves cfe-vx-accessible-catalogue-only-20261010, cfe-vx-rights-and-execution-qualification-open-20261010, cfe-vx-tas-timing-not-a-fill-cached-20261010, cfe-vx-current-fees-no-existing-entitlement-20261010T1731Z, cfe-vx-public-settlement-package-insufficient-for-admission-20261010T1734Z.
- `qualify:eurusd-technical-grid` : **WAIT** — WAIT scoped to full admission: preserve the original proxy freeze and all history; no price access. Next distinct implementation work must review an exact lab-control/original-reservation adapter and measure complete capture/storage/full-window execution bounds without market outcomes. Do not reopen this qualification hourly, reduce windows, change limits or substitute the generic runner. Process the still-OPEN Hyperliquid host/global-fills question next; ZF stays WAIT without new entitlement evidence. ; preuves histdata-personal-proxy-qualified-cached-20261010, fx-current-host-and-look-preflight-20261010T1657Z, fx-legacy-control-resource-bridge-gap-20261010, fx-runtime-qualification-construction-20261010.
- `qualify:hyperliquid-forced-flow` : **WAIT** — WAIT for a verifiably pre-existing compliant node/global-fill/local-clock/BBO host with documented zero-paid authorized access, durable resources and original protocol gates. No node installation, paid host, requester-pays archive or trades-only substitute. Current docs/host question is closed until a distinct host/access fact; inspect one different mechanism with genuinely accessible primary data instead, preserving all old exposures and multiplicity. ; preuves hl-global-fills-host-primary-cached-20261010, hl-selected-host-capacity-20261010T1705Z, hl-stale-readiness-marker-contradiction-20261010.
- `qualify:treasury-auction-zf` : **WAIT** — Qualifier un devis/entitlement du paquet complet sans achat ; examiner la réserve EURUSD et une alternative accessible si ce verrou persiste. ; preuves audit-R18-databento-access-20261010.

Les verdicts économiques importés conservent leur portée. Source inaccessible, manque de puissance et défaut logiciel restent distincts.

[Audit et méthodes externes](https://github.com/fahimahmedb/Quant-Trade/blob/fae3be50549d8b023c3e9a42eb14a51613bcb8c4/research/mission_audit_2026-10-10/REPORT.md) · [Fonctionnement et reprise](README.md)

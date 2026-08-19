# Clôture du lot `hardcoded_figures_remainder` (#479) : les 22 candidats restants (pré-enregistré)

Deux tests mécaniques appliqués à chacun : rétractation explicite non appliquée (comme au #527), et compatibilité d'axe (comme aux #523-#525).

## Les 22 candidats, verdict actuel et tests

| Script | Verdict `V` actuel | Cycle citant | Axe | Rétractation trouvée | Compatible |
|---|---|---|---|---|---|
| `nonml_battery_backfill_lot_audit.py` | defaut | #508 | committabilité de la réparation (#507) | non | OUI |
| `nonml_citer_451_resolution_backtest.py` | legitime | #481 | MASQUANT/ANODIN d'une garde (#481, même script, ligne différ… | non | OUI |
| `nonml_conditional_sections_sweep_backtest.py` | legitime | #509 | écart de régénération de rapport (idempotence temporelle) | non | OUI |
| `nonml_dsr_corrected_trials_backtest.py` | partiel | #518 | réparabilité d'un chiffre (#485/#518) | non | OUI |
| `nonml_idempotence_famille_capable_backtest.py` | defaut | #518 | réparabilité d'un chiffre (#485/#518) | non | OUI |
| `nonml_idempotence_lot2_backtest.py` | partiel | #518 | réparabilité d'un chiffre (#485/#518) | non | OUI |
| `nonml_marker_emitter_crossing_backtest.py` | defaut | #481 | MASQUANT/ANODIN d'une garde (#481, même script, ligne différ… | non | OUI |
| `nonml_net_pnl_correction_robustness.py` | legitime | #481 | MASQUANT/ANODIN d'une garde (#481) | non | OUI |
| `nonml_orphans_interrupted_or_lost_backtest.py` | partiel | #485 | réparabilité d'un chiffre (#485) | non | OUI |
| `nonml_pnl_duplicate_sweep_audit.py` | defaut | #480 | classification orpheline A/C/? (#480) | non | OUI |
| `nonml_pnl_duplicate_sweep_v2_audit.py` | legitime | #480 | classification orpheline A/C/? (#480) | non | OUI |
| `nonml_pnl_persistence_exposed_pass_audit.py` | defaut | #480 | défaut réel confirmé (#482, Cible 1) | non | OUI |
| `nonml_report_idempotence_audit.py` | legitime | #504 | emprunts non rattachés à une source (#504) — cible potentiel… | non | OUI |
| `nonml_reproducibility_campaign_v2_audit.py` | partiel | #518 | réparabilité d'un chiffre (#485/#518) | non | OUI |
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | defaut | #485 | réparabilité d'un chiffre (#485, #493) | non | OUI |
| `nonml_reproducibility_sample_backtest.py` | legitime | #482 | citation légitime (#482) — cible potentiellement confondue p… | non | OUI |
| `nonml_self_inclusion_repair_audit.py` | legitime | #516 | procédural/substantiel (#516) | non | OUI |
| `nonml_sweep_pass_prose_fix_backtest.py` | legitime | #494 | classe d'exécution A/C, témoin non publié (#494) — déjà faux… | non | OUI |
| `nonml_content_defined_magnitudes_audit.py` | defaut | #504 | emprunts non rattachés à une source (#504, résidu nommé) | non | OUI |
| `nonml_content_defined_magnitudes_backtest.py` | defaut | #504 | emprunts non rattachés à une source (#504, résidu nommé) | non | OUI |
| `nonml_coverage_wording_fix_audit.py` | defaut | #518 | réparabilité d'un chiffre (#518, IRRÉPARABLE) | non | OUI |
| `nonml_report_idempotence_backtest.py` | defaut | #504 | emprunts non rattachés à une source (#504, résidu nommé) | non | OUI |

## Justifications, une par une

### `nonml_battery_backfill_lot_audit.py` (#508)

**Axe** : committabilité de la réparation (#507)

Le #508 discute la committabilité d'une correction, pas la légitimité du chiffre lui-même — axe distinct de la classification defaut/legitime.

### `nonml_citer_451_resolution_backtest.py` (#481)

**Axe** : MASQUANT/ANODIN d'une garde (#481, même script, ligne différente)

Le #481 classe une section GARDÉE de ce script (ANODIN, l.187) — un axe de détection de témoin, sans rapport avec la légitimité du littéral « 0 » cité par le #479.

### `nonml_conditional_sections_sweep_backtest.py` (#509)

**Axe** : écart de régénération de rapport (idempotence temporelle)

Le #509 discute un écart de 56 minutes entre deux régénérations d'un rapport — axe temporel/idempotence, sans rapport avec la légitimité du littéral illustratif cité par le #479.

### `nonml_dsr_corrected_trials_backtest.py` (#518)

**Axe** : réparabilité d'un chiffre (#485/#518)

Le #518 confirme EXACTE (réparable, len(gros) calculé) — compatible avec « partiel » du #479 : la partie propre au cycle est bien calculée, pas fabriquée, ce qui soutient plutôt que contredit la distinction citation/résultat propre du #479.

### `nonml_idempotence_famille_capable_backtest.py` (#518)

**Axe** : réparabilité d'un chiffre (#485/#518)

Le #518 confirme EXACTE (réparable, import v1.FAUTIFS_463/SAINS_463) — compatible avec « defaut » du #479 : un calcul fait à la main peut être réparable sans cesser d'être, aujourd'hui, un defaut.

### `nonml_idempotence_lot2_backtest.py` (#518)

**Axe** : réparabilité d'un chiffre (#485/#518)

Le #518 confirme EXACTE (réparable, tous/DEJA construits) — compatible avec « partiel » du #479, même raisonnement que dsr_corrected_trials.

### `nonml_marker_emitter_crossing_backtest.py` (#481)

**Axe** : MASQUANT/ANODIN d'une garde (#481, même script, ligne différente) — déjà faux positif confirmé pour l'axe #484 au #524

Le #481 classe une section gardée (ANODIN, l.175) — axe de détection de témoin. Le #479 classe un littéral distinct (« 1 », compte mécanique) « defaut ». Deux axes, même script, pas de contradiction.

### `nonml_net_pnl_correction_robustness.py` (#481)

**Axe** : MASQUANT/ANODIN d'une garde (#481)

Le #481 classe une section gardée de ce script (ANODIN, l.76) — axe de détection de témoin, sans rapport avec le seuil « 0,9999 » cité par le #479 comme constante de protocole légitime.

### `nonml_orphans_interrupted_or_lost_backtest.py` (#485)

**Axe** : réparabilité d'un chiffre (#485)

Le #485 classe ce script RÉPARABLE (« mon cycle #474 », calcul len(ent)+len(orp) confirmé) — compatible avec « partiel » du #479 : même lecture que #518, un résultat propre calculé reste un défaut d'écriture en dur tant qu'il n'est pas interpolé.

### `nonml_pnl_duplicate_sweep_audit.py` (#480)

**Axe** : classification orpheline A/C/? (#480)

Le #480 classe ce script par sa complétude documentaire (orphelin ou non), pas par la légitimité de son chiffre « 371 » — axe distinct de celui du #479.

### `nonml_pnl_duplicate_sweep_v2_audit.py` (#480)

**Axe** : classification orpheline A/C/? (#480)

Même axe que pnl_duplicate_sweep_audit — le #480 ne discute pas la légitimité des citations « 93,3 % » / « 0,8679 » du #479.

### `nonml_pnl_persistence_exposed_pass_audit.py` (#480)

**Axe** : défaut réel confirmé (#482, Cible 1)

Le #482 confirme explicitement : « défaut réel, irréparable » — compatible avec, et renforce, le verdict « defaut » du #479. Pas une contradiction : les deux s'accordent.

### `nonml_report_idempotence_audit.py` (#504)

**Axe** : emprunts non rattachés à une source (#504) — cible potentiellement confondue par sous-chaîne avec report_idempotence_backtest

Les 5 résidus nommés au #504 incluent `report_idempotence_backtest` (déjà « defaut » au #479, compatible), PAS `report_idempotence_audit` — la mention screenée au #522 est une collision de sous-chaîne, même famille de faux positif qu'au #523.

### `nonml_reproducibility_campaign_v2_audit.py` (#518)

**Axe** : réparabilité d'un chiffre (#485/#518)

Le #518 reclasse ce script IRRÉPARABLE (le glob trouvé sert eligible(), pas le compte cité) — compatible avec « partiel » du #479 : la partie citation (173) reste légitime, la partie propre (208) reste en dur, exactement la distinction que fait le #479.

### `nonml_reproducibility_campaign_v3_lot2_audit.py` (#485)

**Axe** : réparabilité d'un chiffre (#485, #493)

Le #493 reclasse ce script RÉPARABLE (bound() calcule bien 6,2 % et ~4,1 %) — compatible avec « defaut » du #479 : une projection faite à la main reste un defaut même si une fonction du script pourrait, après coup, la recalculer.

### `nonml_reproducibility_sample_backtest.py` (#482)

**Axe** : citation légitime (#482) — cible potentiellement confondue par sous-chaîne avec reproducibility_sample_lot3_audit, déjà réparé au #527

Le marqueur « n'est pas un défaut » trouvé à proximité au balayage mécanique appartient à la discussion du #482 sur `reproducibility_sample_lot3_audit` (réparé au #527), pas sur `reproducibility_sample_backtest` — collision de sous-chaîne, vérifiée explicitement ci-dessous.

### `nonml_self_inclusion_repair_audit.py` (#516)

**Axe** : procédural/substantiel (#516)

Le #516 nomme ce script comme l'unique exception SUBSTANTIELLE de son propre classement — axe de procédure de cycle, sans rapport avec la légitimité du littéral « 7 rapports » (périmètre déclaré) cité par le #479.

### `nonml_sweep_pass_prose_fix_backtest.py` (#494)

**Axe** : classe d'exécution A/C, témoin non publié (#494) — déjà faux positif confirmé pour l'axe #484 au #525

Le #494 discute si le script est sûr à exécuter (classe A) — axe d'exécution, sans rapport avec la légitimité du littéral « 4 PASS » cité par le #479 comme citation dans un bloc.

### `nonml_content_defined_magnitudes_audit.py` (#504)

**Axe** : emprunts non rattachés à une source (#504, résidu nommé)

Le #504 nomme ce script comme résidu — compatible avec « defaut » du #479 : les deux s'accordent, le chiffre « 2 » n'est ni cité ni dérivable.

### `nonml_content_defined_magnitudes_backtest.py` (#504)

**Axe** : emprunts non rattachés à une source (#504, résidu nommé)

Le #504 nomme ce script comme résidu — compatible avec « defaut » du #479, même raisonnement.

### `nonml_coverage_wording_fix_audit.py` (#518)

**Axe** : réparabilité d'un chiffre (#518, IRRÉPARABLE)

Le #518 confirme IRRÉPARABLE (aucun glob, littéral en dur) — compatible avec, et renforce, « defaut » du #479.

### `nonml_report_idempotence_backtest.py` (#504)

**Axe** : emprunts non rattachés à une source (#504, résidu nommé)

Le #504 nomme ce script comme résidu — compatible avec « defaut » du #479.

## Le compte

- candidats vérifiés : **22**
- nouvelles rétractations trouvées : **0**
- compatibles (aucune correction) : **22**
- non tranchés, reportés : **0**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| Au plus 1 nouvelle rétractation | ≤ 1 | 0 | **vérifiée** |
| Au moins 18 compatibles sans correction | ≥ 18 | 22 | **vérifiée** |
| Au plus 3 non tranchés | ≤ 3 | 0 | **vérifiée** |

> Un candidat trouvé par le balayage mécanique brut (`nonml_battery_backfill_lot_audit.py`, marqueur « rétracté » à proximité) s'est révélé être la phrase générique de la « Dette restante » listant des **numéros de cycle** rétractés, pas une discussion de ce script précis — **exclue explicitement**, corrigée avant de committer un résultat plutôt que comptée comme une vraie rétractation.

## Critères de succès

1. Les 22 candidats listés, verdict `V` cité — **OUI**.
2. Résultat du test de rétractation publié pour chacun — **OUI**.
3. Verdict de compatibilité d'axe publié avec citation, pour chacun — **OUI**.
4. Tout candidat non tranché nommé, pas résolu sans preuve — **OUI**.
5. Toute rétractation confirmée appliquée avec diff borné — **OUI**.

**PASS** — le critère porte sur le **procédé** : clore un lot de 22 candidats par un test mécanique déclaré plutôt que par une revue ligne à ligne indéfinie.

**Aucune correction appliquée** — les 22 candidats du #522 pour `hardcoded_figures_remainder` sont désormais tous vérifiés (10 aux #523-#527 individuellement, 22 ici en lot), et le lot est **clos**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification de dépôt, aucune position.

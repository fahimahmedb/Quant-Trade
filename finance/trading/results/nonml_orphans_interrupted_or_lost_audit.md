# Audit adversarial — les orphelins du #464 (#474)

**Recalcul par une route différente.** Ni le module du #464 ni les
fonctions du backtest ne sont réutilisés : découpage du backlog par
expression régulière sur le **texte entier**, listing par `os.scandir`,
historique par `git rev-list --all --objects` au lieu de `git log
--diff-filter=A`.

| Grandeur | Audit | Rapport | Verdict |
|---|---|---|---|
| entrées sans aucun fichier | **10** | 10 | **concordant** |
| `PREREG_` jamais mentionnés | **23** | 23 | **concordant** |
| cycles complets (orphelins) | **13** | 13 | **concordant** |
| cycles interrompus (orphelins) | **10** | 10 | **concordant** |
| traces perdues (total) | **0** | 0 | **concordant** |
| interrompus (entrées sans fichier) | **10** | 10 | **concordant** |

## Effets de bord du backtest

- écritures détectées : **1** (`write_text` du seul rapport : **1**)
- écritures **hors rapport** (`checkout`, `rm`, `open(...,'w')`) : **0**

**Aucun effet de bord.** Le script lit le disque et `git`, écrit son
seul rapport. Rien à annuler.

## Auto-inclusion

- le backtest s'exclut explicitement de sa population : **OUI**
- `orphans_interrupted_or_lost` figure-t-il dans la population publiée : **non**

## Verdict

**CONCORDANT** — **6/6** grandeurs se retrouvent par
une route indépendante.


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution (cycles #436-#438).
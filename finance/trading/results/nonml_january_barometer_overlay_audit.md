# Audit adversarial — Overlay levé January Barometer

## 1. Recalcul indépendant (datetime standard, regroupement par balayage séquentiel)

| Marché | Écart position (nb j.) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — position confirmée par recalcul indépendant.**

## 2. Détail par année (NDX, marché le plus long) — vérifie l'absence de biais évident

| Année | Rdt janvier | Signal (levé fev-déc) |
|---|---|---|
| 1986 | +0.5% | CAP |
| 1987 | +17.9% | CAP |
| 1988 | +1.8% | CAP |
| 1989 | +5.1% | CAP |
| 1990 | -9.8% | 1.0x |
| 1991 | +15.9% | CAP |
| 1992 | +2.3% | CAP |
| 1993 | +2.9% | CAP |
| 1994 | +3.9% | CAP |
| 1995 | +0.3% | CAP |
| 1996 | +2.7% | CAP |
| 1997 | +12.2% | CAP |
| 1998 | +8.1% | CAP |
| 1999 | +15.9% | CAP |
| 2000 | -3.7% | 1.0x |
| 2001 | +10.7% | CAP |
| 2002 | -1.7% | 1.0x |
| 2003 | -0.1% | 1.0x |
| 2004 | +1.7% | CAP |
| 2005 | -6.3% | 1.0x |
| 2006 | +4.0% | CAP |
| 2007 | +2.0% | CAP |
| 2008 | -11.7% | 1.0x |
| 2009 | -2.6% | 1.0x |
| 2010 | -6.4% | 1.0x |
| 2011 | +2.9% | CAP |
| 2012 | +8.3% | CAP |
| 2013 | +2.7% | CAP |
| 2014 | -1.9% | 1.0x |
| 2015 | -2.1% | 1.0x |
| 2016 | -6.8% | 1.0x |
| 2017 | +5.2% | CAP |
| 2018 | +8.7% | CAP |
| 2019 | +9.1% | CAP |
| 2020 | +3.0% | CAP |
| 2021 | +0.3% | CAP |
| 2022 | -8.5% | 1.0x |
| 2023 | +10.6% | CAP |
| 2024 | +1.9% | CAP |
| 2025 | +2.2% | CAP |
| 2026 | +1.2% | CAP |

**29/41 années avec janvier positif sur NDX (71%).**

## 3. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures (aucune année N+1 n'affecte la décision de l'année N).**

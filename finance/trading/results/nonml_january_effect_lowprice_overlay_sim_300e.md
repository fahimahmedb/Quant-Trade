# Simulation — 300 EUR, "January effect" (proxy prix bas) en overlay (~3 derniers mois)

Période : 2026-04-27 → 2026-07-27 (63 séances). Référence = tercile prix bas 1.0x (pas Buy&Hold classique).

**Attention — fenêtre non informative** : les ~3 derniers mois disponibles (2026-04-27 → 2026-07-27) ne contiennent AUCUN jour de janvier. L'overlay est donc rigoureusement IDENTIQUE à la référence 1.0x sur cette fenêtre précise (0 jour de levier) — signalé honnêtement plutôt que de présenter un résultat trompeur. Le verdict statistique réel reste celui du backtest complet (2021-2026, PASS, voir robustesse plateau 4/4).

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Tercile prix bas 1.0x (référence) | 308.41 EUR | +2.8% | -5.5% | +0.93 |
| **+ overlay janvier x2.0** | **308.41 EUR** | **+2.8%** | -5.5% | +0.93 |

Jours de janvier dans cette fenêtre : 0/63.

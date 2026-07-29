# Audit adversarial — Overlay de confirmation multi-marché NDX+Russell2000

Recalcul indépendant du signal NDX (boucle explicite) : 0 écarts. **OK.**

Test anti-lookahead signal NDX : OK — aucune fuite.
Test anti-lookahead signal Russell 2000 : OK — aucune fuite.

Delta de Sharpe non arrondi (overlay − BH) : 0.009229
**OK — le PASS tient sur la valeur exacte, pas un artefact arrondi.**

**Lecture honnête** : la marge de Sharpe est très fine (+0,01) et le MDD se dégrade légèrement (-82,9%→-83,8%), contrairement aux autres overlays de tendance du backlog qui préservaient bien mieux le MDD (#37/#38). Le gain de rendement (+5429,9%→+10207,8%) provient surtout de l'effet multiplicatif du levier sur un actif à drift positif sur 40 ans (mécanique déjà identifiée au #10), pas d'un edge de timing nouveau et marqué. PASS techniquement valide mais À NUANCER : la confirmation croisée n'apporte pas un edge clairement supérieur au signal NDX seul (#37, Sharpe +0,51→+0,59 sur NDX).

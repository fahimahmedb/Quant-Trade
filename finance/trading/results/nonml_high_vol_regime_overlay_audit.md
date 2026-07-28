# Audit adversarial — Overlay levé sur régime de vol élevée

## Test anti-lookahead (mutation des 20% de rendements les plus récents)

Écart de classification de régime sur 7935 jours antérieurs à la mutation (NDX) : 0 jours différents.
**OK — aucune fuite, le passé est bien inchangé.**

**Lecture économique du FAIL** : la vol élevée persiste bien statistiquement (clustering ARCH, cf. Étape A), mais elle coïncide en pratique surtout avec des PHASES DE BAISSE ou de krach (asymétrie de la vol, effet levier documenté en finance empirique -- la vol monte quand les prix chutent), donc lever l'exposition en régime de vol élevée revient largement à lever sur les mêmes périodes que les chocs de prix déjà testés et FAIL aux cycles #13/#22/#24, pas sur une prime de risque isolée et exploitable.
